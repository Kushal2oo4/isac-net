"""Monte Carlo sweep of the baseline receivers: BER/SER and range/velocity NMSE vs SNR.

    python scripts/sweep_baselines.py --grid full --trials 50 --out results/baselines_full
"""
import argparse
import json
import os
import sys
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from isacnet import C, SimConfig, add_cfg_args, apply_cfg_args, small_config  # noqa: E402
from isacnet.baselines import run_baselines  # noqa: E402
from isacnet.metrics import ber_ser, nmse  # noqa: E402
from isacnet.simulator import make_frame  # noqa: E402

COMM = ["perfect_csi", "map_ls", "damp_ls", "map_recon"]
SENSE = ["dft2d", "dft2d_clean", "sense_pilot", "sense_perfect"]


def make_cfg(args):
    cfg = SimConfig() if args.grid == "full" else small_config()
    cfg.path_loss = args.path_loss
    return apply_cfg_args(cfg, args)


def one_trial(job):
    args, snr, trial = job
    cfg = make_cfg(args)
    rng = np.random.default_rng([args.seed, int(snr * 10) + 1000, trial])
    fr = make_frame(cfg, snr, rng)
    out = run_baselines(cfg, fr, len(cfg.ranges))
    res = {}
    for k in COMM:
        res[k] = ber_ser(out[k]["idx"], fr.idx, fr.data_mask)
    for k in SENSE:
        res[k] = nmse(out[k]["r"], out[k]["v"], cfg.ranges, cfg.velocities)
    return snr, res


def crb_nmse(cfg, snr_db):
    """Paper's theoretical line: std = resolution / sqrt(2 SNR), as NMSE over targets."""
    snr = 10 ** (np.asarray(snr_db) / 10)
    dR = C / (2 * cfg.B)
    dV = C / (2 * cfg.T * cfg.M * cfg.fc)
    r, v = np.asarray(cfg.ranges), np.asarray(cfg.velocities)
    nr = np.mean((dR / np.sqrt(2 * snr[:, None]) / r) ** 2, axis=1)
    nv = np.mean((dV / np.sqrt(2 * snr[:, None]) / v) ** 2, axis=1)
    return nr, nv


def plot(path, snrs, agg, cfg):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(1, 3, figsize=(15, 4.2))
    for k in COMM:
        ax[0].semilogy(snrs, [max(agg[k][s][0], 1e-7) for s in snrs], "o-", label=k)
    ax[0].set(xlabel="SNR [dB]", ylabel="BER", title="Communication (cf. Fig. 9)")
    nr_crb, nv_crb = crb_nmse(cfg, snrs)
    for j, name in enumerate(["range", "velocity"]):
        a = ax[1 + j]
        for k in SENSE:
            a.semilogy(snrs, [agg[k][s][j] for s in snrs], "o-", label=k)
        a.semilogy(snrs, nr_crb if j == 0 else nv_crb, "k--", label="CRB (paper)")
        a.set(xlabel="SNR [dB]", ylabel=f"NMSE {name}", title=f"Sensing: {name} (cf. Fig. 10)")
    for a in ax:
        a.grid(True, which="both", alpha=0.3)
        a.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=130)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--grid", choices=["small", "full"], default="small")
    p.add_argument("--path-loss", choices=["physical", "equal"], default="physical")
    add_cfg_args(p)
    p.add_argument("--snr", type=float, nargs="+", default=[-10, -5, 0, 5, 10, 15, 20, 25, 30])
    p.add_argument("--trials", type=int, default=50)
    p.add_argument("--workers", type=int, default=os.cpu_count())
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out", default="results/baselines")
    args = p.parse_args()

    jobs = [(args, s, t) for s in args.snr for t in range(args.trials)]
    acc = {k: {s: [] for s in args.snr} for k in COMM + SENSE}
    with Pool(args.workers) as pool:
        for i, (snr, res) in enumerate(pool.imap_unordered(one_trial, jobs, chunksize=2)):
            for k, v in res.items():
                acc[k][snr].append(v)
            if (i + 1) % max(1, len(jobs) // 20) == 0:
                print(f"{i + 1}/{len(jobs)}", flush=True)

    agg = {k: {s: np.mean(acc[k][s], axis=0).tolist() for s in args.snr} for k in acc}
    # Mean NMSE is dominated by the occasional missed target (e.g. one sitting in
    # the transmit array's null), so the median is stored alongside it.
    med = {k: {s: np.median(acc[k][s], axis=0).tolist() for s in args.snr} for k in SENSE}
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out + ".json", "w") as f:
        json.dump({"args": vars(args),
                   "results": {k: {str(s): v for s, v in d.items()} for k, d in agg.items()},
                   "median_nmse": {k: {str(s): v for s, v in d.items()} for k, d in med.items()}},
                  f, indent=1)
    plot(args.out + ".png", args.snr, agg, make_cfg(args))
    for s in args.snr:
        print(f"SNR {s:5.1f} | " + " ".join(f"{k}={agg[k][s][0]:.2e}" for k in COMM)
              + " | " + " ".join(f"{k}=({agg[k][s][0]:.1e},{agg[k][s][1]:.1e})" for k in SENSE))


if __name__ == "__main__":
    main()
