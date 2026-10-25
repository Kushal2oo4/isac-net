"""Single-reflection geometric MIMO-OFDM ISAC channel, eqs. (5)-(17).

Every transmit antenna sends the same symbol x(m, n) (eq. 6b), so the
Nr x Nt matrix H_a^l only enters through g_l = H_a^l 1_Nt, an Nr-vector.
The received signal per resource element is then

    y(m, n) = sum_l g_l * phi_l(m, n) * x(m, n) + z(m, n)            (6a)
    phi_l(m, n) = exp(-j 2 pi n df tau_l) * exp(j 2 pi f_d,l m T)    (15)

with tau_l = r_l / c and f_d,l = v_l fc / c (eqs. 16, 32). The constant
carrier phase exp(-j 2 pi fc tau_l) is folded into g_l. H_phi^l is
diagonal, so it is applied element-wise instead of as an MN x MN matrix.
"""
from dataclasses import dataclass
import numpy as np

from .config import C, SimConfig


def steering(n_ant, theta):
    """Half-wavelength ULA steering vector, eq. (8)."""
    k = np.arange(n_ant)
    return np.exp(1j * np.pi * k * np.sin(theta)) / np.sqrt(n_ant)


@dataclass
class Channel:
    gains: np.ndarray       # [L, Nr] complex, g_l = H_a^l 1_Nt
    ranges: np.ndarray      # [L] path lengths r_l [m]
    velocities: np.ndarray  # [L] [m/s]
    aod: np.ndarray         # [L] [rad]
    aoa: np.ndarray         # [L] [rad]


def phase_grid(cfg: SimConfig, r, v):
    """phi(m, n) for one path, shape [M, N] (eq. 15 without the carrier term)."""
    m = np.arange(cfg.M)[:, None]
    n = np.arange(cfg.N)[None, :]
    tau = r / C
    fd = v * cfg.fc / C
    return np.exp(-2j * np.pi * n * cfg.df * tau) * np.exp(2j * np.pi * fd * m * cfg.T)


def effective_channel(cfg: SimConfig, gains, ranges, velocities):
    """H(m, n) = sum_l g_l phi_l(m, n), shape [Nr, M, N]."""
    H = np.zeros((gains.shape[1], cfg.M, cfg.N), dtype=np.complex128)
    for g, r, v in zip(gains, ranges, velocities):
        H += g[:, None, None] * phase_grid(cfg, r, v)[None]
    return H


def random_channel(cfg: SimConfig, rng, ranges=None, velocities=None):
    """Draw a channel for the given targets (default: cfg.ranges / cfg.velocities)."""
    ranges = np.asarray(cfg.ranges if ranges is None else ranges, dtype=float)
    velocities = np.asarray(cfg.velocities if velocities is None else velocities, dtype=float)
    L = len(ranges)
    aod = rng.uniform(-np.pi / 3, np.pi / 3, L)
    aoa = rng.uniform(-np.pi / 3, np.pi / 3, L)
    # Split the bistatic path length r = r1 + r2 between the two legs.
    split = rng.uniform(0.3, 0.7, L)
    r1, r2 = ranges * split, ranges * (1 - split)
    if cfg.path_loss == "physical":
        # Large-scale factor F_l ~ lambda^2 sigma / ((4 pi)^3 (r1 r2)^2) is a power;
        # use its square root as the amplitude.
        amp = np.sqrt(cfg.lam ** 2 * cfg.rcs / ((4 * np.pi) ** 3 * (r1 * r2) ** 2))
    else:
        amp = np.ones(L)
    fe = rng.weibull(cfg.weibull_shape, L)
    carrier = np.exp(-2j * np.pi * cfg.fc * ranges / C)
    gains = np.zeros((L, cfg.Nr), dtype=np.complex128)
    for l in range(L):
        array_gain = np.conj(steering(cfg.Nt, aod[l])).sum()  # d_t^H 1_Nt
        gains[l] = fe[l] * amp[l] * carrier[l] * array_gain * steering(cfg.Nr, aoa[l])
    return Channel(gains, ranges, velocities, aod, aoa)
