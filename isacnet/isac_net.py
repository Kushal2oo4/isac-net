"""Alg. 3 (iterative ISAC signal processing) and ISAC-NET (its deep unfolding).

One layer k does, as in Alg. 3 / Fig. 5:

  signal detection  X^{k+1} = eta1 X^k + mu * sum conj(H^k) Z^k               (34)
                    Z^{k+1} = eta2 Z^k + Y_d - H^k X^k                         (35)
  passive sensing   cyclic 2D-DFT peak extraction on Y / X_hat^{k+1}           (36)-(39)
                    [r, v]^{k+1} = eta4 [r, v]^k + (1 - eta4) [r, v]_new       (40)
  reconstruction    H_new = sum_l w_l g_l phi(r_l, v_l)                        (41)
                    H^{k+1} = eta5 H^k + (1 - eta5) H_new                       (42)

where w_l = sigmoid((peak_l [dB over noise floor] - eta3) / tau) is a soft
version of the paper's hard threshold "M >= eta3", so eta3 can be learned.

ISAC-NET learns Omega_k = (eta1..eta5) per layer; Alg. 3 is the same network
with hand-set, fixed values. Peak search (argmax) and hard symbol decisions
are not differentiable, so they run in NumPy on detached values; gradients
reach every eta through the continuous parts above.

Interpretation notes (see README):
  * Each layer runs `n_inner` D-AMP updates (34)-(35) with that layer's eta1,
    eta2. A single update per layer, starting from X = Z = 0, is far from
    converged after 5 layers (BER ~4e-2 at 20 dB), which contradicts Fig. 8;
    Alg. 1 is itself an iterative detector with its own iteration count.
  * (40) and (42) are written as "eta X^k + X_new". We use convex combinations
    (eta X^k + (1 - eta) X_new), which keep r, v and H unbiased for any eta.
  * Targets found in consecutive layers are paired by nearest neighbour
    before blending them with eta4.
"""
from itertools import permutations

import numpy as np
import torch

from .config import C, SimConfig
from .modulation import CONSTELLATION, hard_decision
from .sensing import RangeDopplerSensor, division_matrix, reconstruct_channel

CDT = torch.complex64
# Alg. 3 defaults: plain D-AMP step, threshold 10 dB over floor, no memory in r, v, H.
DEFAULT_ETA = (1.0, 0.0, 10.0, 0.0, 0.0)


def _pair(prev_r, prev_v, new_r, new_v):
    """Order the new detections to match the previous ones (nearest neighbour)."""
    if len(prev_r) == 0 or len(new_r) == 0:
        return list(range(len(new_r)))
    L = min(len(prev_r), len(new_r))
    best, best_cost = None, np.inf
    for perm in permutations(range(len(new_r)), L):
        cost = sum((new_r[p] - prev_r[i]) ** 2 + (new_v[p] - prev_v[i]) ** 2 for i, p in enumerate(perm))
        if cost < best_cost:
            best, best_cost = perm, cost
    return list(best) + [j for j in range(len(new_r)) if j not in best]


class ISACNet(torch.nn.Module):
    def __init__(self, cfg: SimConfig, n_layers=5, max_targets=3, step=0.5, tau_db=1.0,
                 report="grid", eta_init=DEFAULT_ETA, n_inner=4):
        super().__init__()
        self.cfg, self.K, self.max_targets, self.n_inner = cfg, n_layers, max_targets, n_inner
        self.step, self.tau_db, self.report = step, tau_db, report
        self.eta = torch.nn.Parameter(torch.tensor([list(eta_init)] * n_layers, dtype=torch.float32))
        self.full = RangeDopplerSensor(cfg, np.arange(cfg.M))
        self.pilot = RangeDopplerSensor(cfg, cfg.pilot_idx)
        m = torch.arange(cfg.M, dtype=torch.float32)
        n = torch.arange(cfg.N, dtype=torch.float32)
        self.register_buffer("m", m)
        self.register_buffer("n", n)

    # ---- helpers -------------------------------------------------------
    def phi(self, r, v):
        """phi(m, n) for torch scalars r, v (differentiable), shape [M, N]."""
        cfg = self.cfg
        ph_r = -2 * np.pi * self.n * cfg.df / C * r
        ph_v = 2 * np.pi * self.m * cfg.T * cfg.fc / C * v
        return torch.exp(1j * (ph_v[:, None] + ph_r[None, :]))

    def build_channel(self, r, v, w, gains):
        H = 0
        for l in range(len(gains)):
            H = H + (w[l] * gains[l])[:, None, None] * self.phi(r[l], v[l])[None]
        return H

    def sense(self, sensor, S):
        res = sensor.clean(S, self.max_targets, threshold=0.0, report=self.report)
        return res.ranges, res.velocities, 10 * np.log10(np.maximum(res.peak_snr, 1e-12))

    # ---- forward -------------------------------------------------------
    def forward(self, frame, return_history=False):
        cfg = self.cfg
        d = frame.data_mask
        Y_np = frame.Y
        Y = torch.from_numpy(Y_np).to(CDT)
        Yd = Y[:, d]

        # Pilot block (Fig. 4): rough sensing and channel from the pilots alone.
        r_np, v_np, _ = self.sense(self.pilot, division_matrix(Y_np, frame.X, cfg.pilot_idx))
        _, g = reconstruct_channel(cfg, r_np, v_np, Y_np, frame.X, cfg.pilot_idx)
        r = torch.tensor(r_np, dtype=torch.float32)
        v = torch.tensor(v_np, dtype=torch.float32)
        H = self.build_channel(r, v, torch.ones(len(r_np)), torch.from_numpy(g).to(CDT))

        X = torch.zeros(Yd.shape[1:], dtype=CDT)
        Z = torch.zeros_like(Yd)
        hist = []
        for k in range(self.K):
            e1, e2, e3, e4, e5 = self.eta[k]
            Hd = H[:, d]
            mu = (self.step / (Hd.abs() ** 2).sum(0).clamp_min(1e-9)).detach()
            for _ in range(self.n_inner):
                X_new = e1 * X + mu * (Hd.conj() * Z).sum(0)
                Z = e2 * Z + Yd - Hd * X[None]
                X = X_new

            # Passive sensing on Y / X_hat with known pilots + detected data.
            X_full = frame.X.copy()
            X_full[d] = CONSTELLATION[hard_decision(X.detach().numpy())]
            rn, vn, pk = self.sense(self.full, division_matrix(Y_np, X_full, np.arange(cfg.M)))
            order = _pair(r.detach().numpy(), v.detach().numpy(), rn, vn)
            rn, vn, pk = rn[order], vn[order], pk[order]
            L_old = len(r)
            r_new = torch.tensor(rn, dtype=torch.float32)
            v_new = torch.tensor(vn, dtype=torch.float32)
            if L_old:
                Lb = min(L_old, len(rn))
                r = torch.cat([e4 * r[:Lb] + (1 - e4) * r_new[:Lb], r_new[Lb:]])
                v = torch.cat([e4 * v[:Lb] + (1 - e4) * v_new[:Lb], v_new[Lb:]])
            else:
                r, v = r_new, v_new
            w = torch.sigmoid((torch.tensor(pk, dtype=torch.float32) - e3) / self.tau_db)

            # Channel reconstruction (gains by LS on all symbols, detached).
            _, g = reconstruct_channel(cfg, r.detach().numpy(), v.detach().numpy(),
                                       Y_np, X_full, np.arange(cfg.M))
            H_new = self.build_channel(r, v, w, torch.from_numpy(g).to(CDT))
            H = e5 * H + (1 - e5) * H_new
            if return_history:
                hist.append(dict(x=X.detach().numpy().copy(), r=r.detach().numpy().copy(),
                                 v=v.detach().numpy().copy(), w=w.detach().numpy().copy()))
        out = dict(x=X, r=r, v=v, w=w)
        if return_history:
            out["history"] = hist
        return out


def isac_loss(out, frame, cfg, lam=1.0):
    """MSE of the data symbols + lam * (range NMSE + velocity NMSE), eq. (43)."""
    x_true = torch.from_numpy(frame.X[frame.data_mask]).to(CDT)
    comm = ((out["x"] - x_true).abs() ** 2).mean()
    r_true = np.asarray(cfg.ranges, float)
    v_true = np.asarray(cfg.velocities, float)
    r, v = out["r"], out["v"]
    L = len(r_true)
    if len(r) == 0:
        return comm + lam * 2.0, comm
    # pair estimates with true targets (missing ones cost NMSE 1)
    rn, vn = r.detach().numpy(), v.detach().numpy()
    best, best_cost = None, np.inf
    for perm in permutations(range(len(rn)), min(L, len(rn))):
        cost = sum(((rn[p] - r_true[i]) / r_true[i]) ** 2 + ((vn[p] - v_true[i]) / v_true[i]) ** 2
                   for i, p in enumerate(perm))
        if cost < best_cost:
            best, best_cost = perm, cost
    sens = 0
    for i, p in enumerate(best):
        sens = sens + ((r[p] - r_true[i]) / r_true[i]) ** 2 + ((v[p] - v_true[i]) / v_true[i]) ** 2
    sens = (sens + 2.0 * (L - len(best))) / L
    return comm + lam * sens, comm
