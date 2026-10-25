"""PyTorch versions of the sensing / reconstruction / detection steps.

Same algorithms as sensing.py, detection.py and modulation.py, but on torch
tensors so ISAC-NET runs end-to-end on a GPU (CUDA) or Apple MPS. Everything
is complex64 / float32 because MPS has no float64. The NumPy versions stay
as the reference implementation for the baselines; tests check that both
agree.
"""
import numpy as np
import torch

from .config import C, SimConfig
from .modulation import CONSTELLATION
from .sensing import RangeDopplerSensor, SensingResult

CDT = torch.complex64
_NORM = float(np.sqrt(10.0))


def pick_device(name="auto"):
    if name != "auto":
        return torch.device(name)
    if torch.cuda.is_available():
        return torch.device("cuda")
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def hard_decision(x):
    """Nearest 16-QAM point (unit energy) for a complex tensor, returns complex symbols."""
    def axis(v):
        return torch.clamp(torch.round((v * _NORM - 1.0) / 2.0) * 2.0 + 1.0, -3.0, 3.0) / _NORM
    return torch.complex(axis(x.real), axis(x.imag))


def constellation(device):
    return torch.tensor(CONSTELLATION, dtype=CDT, device=device)


class TorchSensor:
    """Torch port of RangeDopplerSensor (same grids, same peak logic)."""

    def __init__(self, cfg: SimConfig, rows, device, coarse_pad: int = 2):
        ref = RangeDopplerSensor(cfg, rows, coarse_pad)
        self.cfg, self.device = cfg, device
        for k in ("Teff", "Mr", "Kv", "Kr", "dv_coarse", "dr_coarse", "dr_fine", "dv_fine"):
            setattr(self, k, getattr(ref, k))
        self.rows = torch.as_tensor(np.asarray(rows), device=device)
        self.n = torch.arange(cfg.N, dtype=torch.float32, device=device)
        self.m = torch.as_tensor(ref.m, dtype=torch.float32, device=device)
        self.mask = torch.as_tensor(ref.search_mask(), device=device)
        self.kr = 2 * np.pi * cfg.df / C          # range phase per (subcarrier * metre)
        self.kv = 2 * np.pi * cfg.fc / C * cfg.T  # Doppler phase per (symbol * m/s)

    def coarse_map(self, S):
        A = torch.fft.ifft(S, n=self.Kr, dim=2) * self.Kr
        A = torch.fft.fft(A, n=self.Kv, dim=1)
        return (A.abs() ** 2).sum(0)

    def coarse_to_rv(self, iv, ir):
        v_idx = iv if iv < self.Kv // 2 else iv - self.Kv
        return ir * self.dr_coarse, v_idx * self.dv_coarse

    def _bases(self, r, v):
        r = torch.as_tensor(r, dtype=torch.float32, device=self.device).reshape(-1)
        v = torch.as_tensor(v, dtype=torch.float32, device=self.device).reshape(-1)
        ar = torch.exp(-1j * self.kr * self.n[:, None] * r[None, :])   # [N, R]
        av = torch.exp(1j * self.kv * self.m[:, None] * v[None, :])    # [Mr, V]
        return ar, av

    def _grid_peak(self, S, r, v):
        ar, av = self._bases(r, v)
        corr = torch.einsum("mv,kmr->kvr", av.conj(), S @ ar.conj())
        P = (corr.abs() ** 2).sum(0)
        i = int(torch.argmax(P))
        iv, ir = divmod(i, P.shape[1])
        return float(r[ir]), float(v[iv]), float(P[iv, ir])

    def refine(self, S, r0, v0):
        r = r0 + np.arange(-self.dr_coarse, self.dr_coarse + 1e-12, self.dr_fine)
        v = v0 + np.arange(-self.dv_coarse, self.dv_coarse + 1e-12, self.dv_fine)
        return self._grid_peak(S, r, v)

    def zoom(self, S, r0, v0, rounds=3):
        dr, dv = self.dr_fine, self.dv_fine
        r, v = r0, v0
        for _ in range(rounds):
            r, v, peak = self._grid_peak(S, r + np.linspace(-dr, dr, 21), v + np.linspace(-dv, dv, 21))
            dr, dv = dr / 10, dv / 10
        return r, v, peak

    def atom(self, r, v):
        ar, av = self._bases(r, v)
        return av[:, 0][:, None] * ar[:, 0][None, :]

    def residual(self, S, ranges, velocities):
        A = torch.stack([self.atom(r, v).reshape(-1) for r, v in zip(ranges, velocities)])  # [L, MrN]
        Sf = S.reshape(S.shape[0], -1)
        G = torch.linalg.solve(A.conj() @ A.T, A.conj() @ Sf.T)
        return (Sf - G.T @ A).reshape(S.shape)

    def clean(self, S, max_targets, threshold=0.0, report="grid"):
        R = S
        floor = None
        rs, vs, rf, vf, snrs = [], [], [], [], []
        for _ in range(max_targets):
            P = self.coarse_map(R)
            if floor is None:
                floor = float(torch.median(P))
            i = int(torch.argmax(torch.where(self.mask, P, torch.full_like(P, -1.0))))
            iv, ir = divmod(i, P.shape[1])
            r, v, peak = self.refine(R, *self.coarse_to_rv(iv, ir))
            if peak < threshold * floor:
                break
            r2, v2, _ = self.zoom(R, r, v)
            rs.append(r); vs.append(v); rf.append(r2); vf.append(v2); snrs.append(peak / floor)
            R = self.residual(S, rf, vf)
        if report == "fine":
            rs, vs = rf, vf
        return SensingResult(np.array(rs), np.array(vs), np.array(snrs))


def phase_grid(cfg: SimConfig, r, v, m, n):
    """phi(m, n) = exp(-j kr n r) exp(j kv m v) for torch scalars r, v (differentiable)."""
    kr = 2 * np.pi * cfg.df / C
    kv = 2 * np.pi * cfg.fc / C * cfg.T
    return torch.exp(1j * (kv * m[:, None] * v - kr * n[None, :] * r))


def reconstruct_gains(cfg: SimConfig, ranges, velocities, Y, X, rows, m, n):
    """LS per-antenna path gains (Alg. 2, see sensing.reconstruct_channel). [L, Nr]."""
    L = len(ranges)
    if L == 0:
        return torch.zeros((0, Y.shape[0]), dtype=CDT, device=Y.device)
    phis = torch.stack([phase_grid(cfg, float(r), float(v), m[rows], n) * X[rows]
                        for r, v in zip(ranges, velocities)]).reshape(L, -1)
    gram = phis.conj() @ phis.T
    rhs = phis.conj() @ Y[:, rows].reshape(Y.shape[0], -1).T
    eye = torch.eye(L, dtype=CDT, device=Y.device)
    return torch.linalg.solve(gram + 1e-6 * eye, rhs)
