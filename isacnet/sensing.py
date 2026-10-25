"""2D-DFT passive sensing (Sec. III-B) and channel reconstruction (Alg. 2).

The paper evaluates the range/Doppler spectrum on a 10x zero-padded grid
(MI = 2560, NI = 10240). Building that full map for 8 antennas costs
gigabytes, so we search a 2x padded map first and then evaluate the exact
10x grid only in a +-1 coarse-bin window around each peak. Near the peak
the values are identical to the full padded DFT.
"""
from dataclasses import dataclass
import numpy as np

from .config import C, SimConfig
from .channel import effective_channel, phase_grid


@dataclass
class SensingResult:
    ranges: np.ndarray
    velocities: np.ndarray
    peak_snr: np.ndarray   # peak power over noise floor, per detection


def _row_spacing(rows):
    rows = np.asarray(rows)
    if len(rows) == 1:
        return 1
    d = np.diff(rows)
    if not np.all(d == d[0]):
        raise ValueError("sensing rows must be uniformly spaced")
    return int(d[0])


class RangeDopplerSensor:
    """Range/velocity estimation from S = Y / X on a set of OFDM symbols."""

    def __init__(self, cfg: SimConfig, rows, coarse_pad: int = 2):
        self.cfg = cfg
        self.rows = np.asarray(rows)
        self.Teff = _row_spacing(rows) * cfg.T
        self.Mr = len(self.rows)
        self.n = np.arange(cfg.N)
        self.m = self.rows - self.rows[0]  # time origin at first row (phase folds into gain)
        # coarse grids
        self.Kv = coarse_pad * self.Mr
        self.Kr = coarse_pad * cfg.N
        self.dv_coarse = C / (self.Teff * self.Kv * cfg.fc)
        self.dr_coarse = C / (self.Kr * cfg.df)
        # fine grid steps follow the paper's zero padding (Table III)
        self.dr_fine = C / (cfg.NI * cfg.df)
        self.dv_fine = C / (self.Teff * self.Mr * (cfg.MI / cfg.M) * cfg.fc)

    # ---- spectra -------------------------------------------------------
    def coarse_map(self, S):
        """Non-coherent sum over antennas of |2D DFT|^2, shape [Kv, Kr]."""
        # range: IDFT over subcarriers; velocity: DFT over symbols
        A = np.fft.ifft(S, n=self.Kr, axis=2) * self.Kr
        A = np.fft.fft(A, n=self.Kv, axis=1)
        return np.sum(np.abs(A) ** 2, axis=0)

    def search_mask(self):
        """Coarse bins inside the (max_range, max_speed) search window."""
        iv = np.arange(self.Kv)
        v = np.where(iv < self.Kv // 2, iv, iv - self.Kv) * self.dv_coarse
        r = np.arange(self.Kr) * self.dr_coarse
        return (np.abs(v)[:, None] <= self.cfg.max_speed) & (r[None, :] <= self.cfg.max_range)

    def coarse_to_rv(self, iv, ir):
        v_idx = iv if iv < self.Kv // 2 else iv - self.Kv
        return ir * self.dr_coarse, v_idx * self.dv_coarse

    def _bases(self, r, v):
        ar = np.exp(-2j * np.pi * np.outer(self.n, np.atleast_1d(r)) * self.cfg.df / C)        # [N, R]
        av = np.exp(2j * np.pi * np.outer(self.m, np.atleast_1d(v)) * self.cfg.fc / C * self.cfg.T)  # [Mr, V]
        return ar, av

    def correlate(self, S, r, v):
        """sum_mn S_k(m,n) conj(a_v(m) a_r(n)) for all (v, r) pairs, shape [Nr, V, R]."""
        ar, av = self._bases(r, v)
        tmp = S @ np.conj(ar)                                  # [Nr, Mr, R]
        return np.einsum("mv,kmr->kvr", np.conj(av), tmp)

    def _grid_peak(self, S, r, v):
        P = np.sum(np.abs(self.correlate(S, r, v)) ** 2, axis=0)
        iv, ir = np.unravel_index(np.argmax(P), P.shape)
        return r[ir], v[iv], P[iv, ir]

    def refine(self, S, r0, v0):
        """Peak on the paper's zero-padded grid, searched +-1 coarse bin around (r0, v0)."""
        r = r0 + np.arange(-self.dr_coarse, self.dr_coarse + 1e-12, self.dr_fine)
        v = v0 + np.arange(-self.dv_coarse, self.dv_coarse + 1e-12, self.dv_fine)
        return self._grid_peak(S, r, v)

    def zoom(self, S, r0, v0, rounds=3):
        """Off-grid refinement: repeatedly search +-1 step at 10x finer spacing."""
        dr, dv = self.dr_fine, self.dv_fine
        r, v = r0, v0
        for _ in range(rounds):
            r, v, peak = self._grid_peak(S, r + np.linspace(-dr, dr, 21), v + np.linspace(-dv, dv, 21))
            dr, dv = dr / 10, dv / 10
        return r, v, peak

    def atom(self, r, v):
        ar, av = self._bases(r, v)
        return av[:, 0][:, None] * ar[:, 0][None, :]          # [Mr, N]

    def residual(self, S, ranges, velocities):
        """S minus the joint least-squares fit of all atoms (per antenna)."""
        A = np.stack([self.atom(r, v).ravel() for r, v in zip(ranges, velocities)])  # [L, MrN]
        Sf = S.reshape(S.shape[0], -1)
        G = np.linalg.solve(np.conj(A) @ A.T, np.conj(A) @ Sf.T)                       # [L, Nr]
        return (Sf - G.T @ A).reshape(S.shape)

    # ---- detectors -----------------------------------------------------
    def clean(self, S, max_targets, threshold=10.0, report="grid"):
        """Cyclic peak extraction (Alg. 3 step 4): find peak, remove, repeat.

        Each detection is zoomed off-grid before removal and all gains are
        re-fitted jointly (OMP-style), so a strong target's leftovers do not
        mask weak ones; the paper does not say how its subtraction is done.
        Stops when the peak falls below `threshold` x noise floor (eta_3) or
        after `max_targets` detections. report="grid" returns the estimates
        on the paper's 10x DFT grid, report="fine" the zoomed values.
        """
        R = S
        floor = None
        rs, vs, rf, vf, snrs = [], [], [], [], []
        for _ in range(max_targets):
            P = self.coarse_map(R)
            if floor is None:
                floor = np.median(P)
                mask = self.search_mask()
            iv, ir = np.unravel_index(np.argmax(np.where(mask, P, -1.0)), P.shape)
            r, v, peak = self.refine(R, *self.coarse_to_rv(iv, ir))
            if peak < threshold * floor:
                break
            r2, v2, _ = self.zoom(R, r, v)
            rs.append(r); vs.append(v); rf.append(r2); vf.append(v2); snrs.append(peak / floor)
            R = self.residual(S, rf, vf)
        if report == "fine":
            rs, vs = rf, vf
        return SensingResult(np.array(rs), np.array(vs), np.array(snrs))

    def top_peaks(self, S, n_targets):
        """Conventional 2D-DFT [5]: the n largest local maxima of one map, no subtraction."""
        P = self.coarse_map(S)
        pad = np.pad(P, 1, mode="wrap")
        neigh = np.stack([pad[1 + dy:1 + dy + P.shape[0], 1 + dx:1 + dx + P.shape[1]]
                          for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx])
        is_max = (P >= neigh.max(axis=0)) & self.search_mask()
        cand = np.flatnonzero(is_max)
        cand = cand[np.argsort(P.flat[cand])[::-1][:n_targets]]
        floor = np.median(P)
        rs, vs, snrs = [], [], []
        for c in cand:
            iv, ir = np.unravel_index(c, P.shape)
            r, v, peak = self.refine(S, *self.coarse_to_rv(iv, ir))
            rs.append(r); vs.append(v); snrs.append(peak / floor)
        return SensingResult(np.array(rs), np.array(vs), np.array(snrs))


def division_matrix(Y, X, rows):
    """S_g = Y / X on the chosen symbols, eq. (27). Shape [Nr, len(rows), N]."""
    return Y[:, rows] / X[rows][None]


def reconstruct_channel(cfg: SimConfig, ranges, velocities, Y, X, rows):
    """ISAC channel reconstruction CHA([r, v]) (Alg. 2).

    The paper rebuilds H_a^l from estimated AoD/AoA and path loss. Here the
    per-antenna complex gains g_l = H_a^l 1_Nt are fitted by least squares on
    `rows` (known pilots, or pilots + detected data), which absorbs AoA, AoD,
    fading and path loss in one step. Returns (H_hat [Nr, M, N], gains [L, Nr]).
    """
    L = len(ranges)
    if L == 0:
        return np.zeros((cfg.Nr, cfg.M, cfg.N), complex), np.zeros((0, cfg.Nr), complex)
    phis = np.stack([phase_grid(cfg, r, v)[rows] * X[rows] for r, v in zip(ranges, velocities)])  # [L, Mr, N]
    Phi = phis.reshape(L, -1)
    gram = np.conj(Phi) @ Phi.T                       # [L, L]
    rhs = np.conj(Phi) @ Y[:, rows].reshape(Y.shape[0], -1).T  # [L, Nr]
    gains = np.linalg.solve(gram + 1e-9 * np.eye(L), rhs)
    return effective_channel(cfg, gains, ranges, velocities), gains
