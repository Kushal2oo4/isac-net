"""Pilot channel estimation and communication signal detection."""
import numpy as np

from .config import SimConfig
from .modulation import hard_decision


def ls_channel_estimate(cfg: SimConfig, Y, X):
    """LS estimate on pilot symbols, linearly interpolated over time. [Nr, M, N]."""
    p = np.asarray(cfg.pilot_idx)
    Hp = Y[:, p] / X[p][None]                       # [Nr, P, N]
    m = np.arange(cfg.M)
    j = np.clip(np.searchsorted(p, m, side="right") - 1, 0, len(p) - 1)
    j2 = np.clip(j + 1, 0, len(p) - 1)
    span = np.where(j2 > j, p[j2] - p[j], 1)
    w = np.clip((m - p[j]) / span, 0.0, 1.0)        # hold the last pilot beyond its row
    return (1 - w)[None, :, None] * Hp[:, j] + w[None, :, None] * Hp[:, j2]


def ml_detect(Y, H):
    """ML/MAP detection with a given channel, per resource element.

    y = h x + z with a scalar 16-QAM x and an Nr-vector h, so ML reduces to
    MRC followed by the nearest constellation point. Returns (soft, indices).
    """
    num = np.sum(np.conj(H) * Y, axis=0)
    den = np.sum(np.abs(H) ** 2, axis=0) + 1e-12
    x_soft = num / den
    return x_soft, hard_decision(x_soft)


def improved_damp(Y, H, n_iter=10, eta1=1.0, eta2=0.0, step=0.5, precondition=True):
    """Improved D-AMP signal detection, Alg. 1 / eqs. (23)-(24).

        X^{k+1} = eta1 X^k + mu * sum_l (H_a^l)^H Z^k (H_phi^l)^H
        Z^{k+1} = eta2 Z^k + Y - sum_l H_a^l X^k H_phi^l

    Notes on our reading of the paper:
      * We use the Hermitian (conjugate) transpose; the plain transpose
        written in (23) does not converge for complex channels.
      * A step size mu is needed for convergence. With precondition=True,
        mu = step / ||h(m,n)||^2 per resource element; otherwise step / max ||h||^2.
      * (24) uses X^k (not X^{k+1}), kept as written. Because of that one-step
        lag, eta1 = 1, eta2 = 0 oscillates for step >= 1 (characteristic
        polynomial z^2 - z + step), hence the default step = 0.5.
    eta1 / eta2 may be scalars or length-n_iter sequences (learned in ISAC-NET).
    Returns (soft estimate, hard indices), both [M, N].
    """
    eta1 = np.broadcast_to(np.asarray(eta1, float), (n_iter,))
    eta2 = np.broadcast_to(np.asarray(eta2, float), (n_iter,))
    hn = np.sum(np.abs(H) ** 2, axis=0) + 1e-12
    mu = step / hn if precondition else step / hn.max()
    X = np.zeros(Y.shape[1:], complex)
    Z = np.zeros_like(Y)
    for k in range(n_iter):
        X_new = eta1[k] * X + mu * np.sum(np.conj(H) * Z, axis=0)
        Z = eta2[k] * Z + Y - H * X[None]
        X = X_new
    return X, hard_decision(X)
