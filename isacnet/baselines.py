"""Baseline receivers used in Fig. 9 and Fig. 10."""
import numpy as np

from .config import SimConfig
from .detection import improved_damp, ls_channel_estimate, ml_detect
from .modulation import CONSTELLATION
from .sensing import RangeDopplerSensor, division_matrix, reconstruct_channel
from .simulator import Frame


def detected_frame(frame: Frame, idx_hat):
    """Transmit grid with known pilots and detected data symbols."""
    X = frame.X.copy()
    X[frame.data_mask] = CONSTELLATION[idx_hat[frame.data_mask]]
    return X


def run_baselines(cfg: SimConfig, frame: Frame, n_targets: int, damp_iter: int = 10):
    """Returns {name: dict(idx=..., r=..., v=...)} for each baseline."""
    out = {}
    all_rows = np.arange(cfg.M)

    # Perfect CSI detection (communication lower bound).
    _, idx = ml_detect(frame.Y, frame.H)
    out["perfect_csi"] = dict(idx=idx)

    # Conventional: LS pilot estimate + ML/MAP detection ("MAP" in Fig. 9).
    H_ls = ls_channel_estimate(cfg, frame.Y, frame.X)
    _, idx_map = ml_detect(frame.Y, H_ls)
    out["map_ls"] = dict(idx=idx_map)

    # Improved D-AMP (Alg. 1) on the LS channel.
    _, idx_damp = improved_damp(frame.Y, H_ls, n_iter=damp_iter)
    out["damp_ls"] = dict(idx=idx_damp)

    full = RangeDopplerSensor(cfg, all_rows)

    # Conventional serial 2D-DFT [5]: sense on Y / X_detected, top-L peaks, no extraction.
    S = division_matrix(frame.Y, detected_frame(frame, idx_map), all_rows)
    res = full.top_peaks(S, n_targets)
    out["dft2d"] = dict(r=res.ranges, v=res.velocities)

    # Same, with cyclic peak extraction (step 4 of Alg. 3).
    res = full.clean(S, n_targets, threshold=0.0)
    out["dft2d_clean"] = dict(r=res.ranges, v=res.velocities)

    # "Perfect" sensing: no demodulation errors (true X).
    S_true = division_matrix(frame.Y, frame.X, all_rows)
    res = full.clean(S_true, n_targets, threshold=0.0)
    out["sense_perfect"] = dict(r=res.ranges, v=res.velocities)

    # Pilot-only rough sensing (Fig. 4 pilot block), then model-based channel
    # reconstruction and detection: a single pass of the ISAC loop.
    pil = RangeDopplerSensor(cfg, cfg.pilot_idx)
    res = pil.clean(division_matrix(frame.Y, frame.X, cfg.pilot_idx), n_targets, threshold=0.0)
    out["sense_pilot"] = dict(r=res.ranges, v=res.velocities)
    H_rec, _ = reconstruct_channel(cfg, res.ranges, res.velocities, frame.Y, frame.X, cfg.pilot_idx)
    _, idx_rec = ml_detect(frame.Y, H_rec)
    out["map_recon"] = dict(idx=idx_rec)
    return out
