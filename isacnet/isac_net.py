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
with hand-set, fixed values. Everything runs in PyTorch on `device` (CPU,
CUDA or Apple MPS). Peak search (argmax) and hard symbol decisions are not
differentiable and run on detached values; gradients reach every eta through
the continuous parts above.

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
from . import torch_ops as T

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
                 report="grid", eta_init=DEFAULT_ETA, n_inner=4, device="cpu"):
        super().__init__()
        self.cfg, self.K, self.max_targets, self.n_inner = cfg, n_layers, max_targets, n_inner
        self.step, self.tau_db, self.report = step, tau_db, report
        self.device = torch.device(device)
        self.eta = torch.nn.Parameter(torch.tensor([list(eta_init)] * n_layers, dtype=torch.float32,
                                                   device=self.device))
        self.full = T.TorchSensor(cfg, np.arange(cfg.M), self.device)
        self.pilot = T.TorchSensor(cfg, cfg.pilot_idx, self.device)
        self.m = torch.arange(cfg.M, dtype=torch.float32, device=self.device)
        self.n = torch.arange(cfg.N, dtype=torch.float32, device=self.device)
        self.all_rows = torch.arange(cfg.M, device=self.device)
        self.pilot_rows = torch.as_tensor(cfg.pilot_idx, device=self.device)

    # ---- helpers -------------------------------------------------------
    def build_channel(self, r, v, w, gains):
        H = 0
        for l in range(len(gains)):
            H = H + (w[l] * gains[l])[:, None, None] * T.phase_grid(self.cfg, r[l], v[l], self.m, self.n)[None]
        return H

    def sense(self, sensor, S):
        res = sensor.clean(S, self.max_targets, threshold=0.0, report=self.report)
        return res.ranges, res.velocities, 10 * np.log10(np.maximum(res.peak_snr, 1e-12))

    def _vec(self, a):
        return torch.as_tensor(np.asarray(a), dtype=torch.float32, device=self.device)

    # ---- forward -------------------------------------------------------
    def forward(self, frame, return_history=False):
        cfg, dev = self.cfg, self.device
        d = torch.as_tensor(frame.data_mask, device=dev)
        Y = torch.as_tensor(frame.Y, dtype=T.CDT, device=dev)
        X_known = torch.as_tensor(frame.X, dtype=T.CDT, device=dev)  # only pilot rows are used
        Yd = Y[:, d]

        # Pilot block (Fig. 4): rough sensing and channel from the pilots alone.
        pr = self.pilot_rows
        r_np, v_np, _ = self.sense(self.pilot, Y[:, pr] / X_known[pr][None])
        g = T.reconstruct_gains(cfg, r_np, v_np, Y, X_known, pr, self.m, self.n)
        r, v = self._vec(r_np), self._vec(v_np)
        H = self.build_channel(r, v, torch.ones(len(r_np), device=dev), g)

        X = torch.zeros(Yd.shape[1:], dtype=T.CDT, device=dev)
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
            X_full = X_known.clone()
            X_full[d] = T.hard_decision(X.detach())
            rn, vn, pk = self.sense(self.full, Y / X_full[None])
            order = _pair(r.detach().cpu().numpy(), v.detach().cpu().numpy(), rn, vn)
            rn, vn, pk = rn[order], vn[order], pk[order]
            L_old = len(r)
            r_new, v_new = self._vec(rn), self._vec(vn)
            if L_old:
                Lb = min(L_old, len(rn))
                r = torch.cat([e4 * r[:Lb] + (1 - e4) * r_new[:Lb], r_new[Lb:]])
                v = torch.cat([e4 * v[:Lb] + (1 - e4) * v_new[:Lb], v_new[Lb:]])
            else:
                r, v = r_new, v_new
            w = torch.sigmoid((self._vec(pk) - e3) / self.tau_db)

            # Channel reconstruction (gains by LS on all symbols, detached).
            g = T.reconstruct_gains(cfg, r.detach().cpu().numpy(), v.detach().cpu().numpy(),
                                    Y, X_full, self.all_rows, self.m, self.n)
            H_new = self.build_channel(r, v, w, g)
            H = e5 * H + (1 - e5) * H_new
            if return_history:
                hist.append(dict(x=X.detach().cpu().numpy().copy(), r=r.detach().cpu().numpy().copy(),
                                 v=v.detach().cpu().numpy().copy(), w=w.detach().cpu().numpy().copy()))
        out = dict(x=X, r=r, v=v, w=w)
        if return_history:
            out["history"] = hist
        return out


def isac_loss(out, frame, cfg, lam=1.0):
    """MSE of the data symbols + lam * (range NMSE + velocity NMSE), eq. (43)."""
    x_true = torch.as_tensor(frame.X[frame.data_mask], dtype=T.CDT, device=out["x"].device)
    comm = ((out["x"] - x_true).abs() ** 2).mean()
    r_true = np.asarray(cfg.ranges, float)
    v_true = np.asarray(cfg.velocities, float)
    r, v = out["r"], out["v"]
    L = len(r_true)
    if len(r) == 0:
        return comm + lam * 2.0, comm
    # pair estimates with true targets (missing ones cost NMSE 1)
    rn, vn = r.detach().cpu().numpy(), v.detach().cpu().numpy()
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
