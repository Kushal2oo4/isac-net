"""Monte Carlo evaluation of Alg. 3 (fixed eta) and ISAC-NET (trained eta).

Records final BER/SER/NMSE (Figs. 9, 10) and per-layer values (Fig. 8).

    python scripts/eval_isacnet.py --grid full --eta results/eta_full.json --trials 40 --out results/isacnet_full
"""
import argparse
import json
import os
import sys
from multiprocessing import Pool

import numpy as np
import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from isacnet import SimConfig, small_config  # noqa: E402
from isacnet.torch_ops import pick_device  # noqa: E402
from isacnet.isac_net import ISACNet  # noqa: E402
from isacnet.metrics import ber_ser, nmse  # noqa: E402
from isacnet.modulation import hard_decision  # noqa: E402
from isacnet.simulator import make_frame  # noqa: E402


def make_cfg(args):
    cfg = SimConfig() if args.grid == "full" else small_config()
    cfg.path_loss = args.path_loss
    return cfg


def nearest_eta(table, snr):
    keys = sorted(table, key=lambda s: abs(float(s) - snr))
    return table[keys[0]]


def one_trial(job):
    args, snr, trial, eta_table = job
    torch.set_num_threads(1)
    cfg = make_cfg(args)
    rng = np.random.default_rng([args.seed + 99, int(snr * 10) + 1000, trial])
    frame = make_frame(cfg, snr, rng)
    nets = {"alg3": ISACNet(cfg, n_layers=args.layers, report=args.report, n_inner=args.inner,
                  device=pick_device(args.device))}
    if eta_table:
        net = ISACNet(cfg, n_layers=args.layers, report=args.report, n_inner=args.inner,
                  device=pick_device(args.device))
        with torch.no_grad():
            net.eta.copy_(torch.tensor(nearest_eta(eta_table, snr), device=net.eta.device))
        nets["isacnet"] = net
    res = {}
    with torch.no_grad():
        for name, net in nets.items():
            out = net(frame, return_history=True)
            layers = []
            for h in out["history"]:
                idx = np.full(frame.idx.shape, -1)
                idx[frame.data_mask] = hard_decision(h["x"])
                b, s = ber_ser(idx, frame.idx, frame.data_mask)
                layers.append((b, s) + nmse(h["r"], h["v"], cfg.ranges, cfg.velocities))
            res[name] = layers
    return snr, res


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--grid", choices=["small", "full"], default="small")
    p.add_argument("--path-loss", choices=["physical", "equal"], default="physical")
    p.add_argument("--snr", type=float, nargs="+", default=[-10, -5, 0, 5, 10, 15, 20, 25, 30])
    p.add_argument("--layers", type=int, default=5)
    p.add_argument("--inner", type=int, default=4, help="D-AMP updates per layer (1 = literal Alg. 3)")
    p.add_argument("--device", default="cpu", help="cpu, cuda, mps or auto; use --workers 1 on a GPU")
    p.add_argument("--report", choices=["grid", "fine"], default="grid")
    p.add_argument("--eta", default=None, help="JSON written by train_isacnet.py")
    p.add_argument("--trials", type=int, default=40)
    p.add_argument("--workers", type=int, default=os.cpu_count())
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out", default="results/isacnet")
    args = p.parse_args()

    eta_table = json.load(open(args.eta))["eta"] if args.eta else None
    jobs = [(args, s, t, eta_table) for s in args.snr for t in range(args.trials)]
    acc = {}
    pool = Pool(args.workers) if args.workers > 1 else None  # GPUs: run in-process
    it = pool.imap_unordered(one_trial, jobs) if pool else map(one_trial, jobs)
    for i, (snr, res) in enumerate(it):
        for name, layers in res.items():
            acc.setdefault(name, {}).setdefault(snr, []).append(layers)
        if (i + 1) % max(1, len(jobs) // 20) == 0:
            print(f"{i + 1}/{len(jobs)}", flush=True)
    if pool:
        pool.close()

    # [trial, layer, (ber, ser, nmse_r, nmse_v)]
    summary = {}
    for name, d in acc.items():
        summary[name] = {}
        for s, trials in d.items():
            a = np.array(trials)
            summary[name][str(s)] = dict(mean=a.mean(0).tolist(), median=np.median(a, 0).tolist())
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out + ".json", "w") as f:
        json.dump({"args": vars(args), "metrics": ["ber", "ser", "nmse_r", "nmse_v"], "results": summary}, f, indent=1)
    for name in summary:
        for s in args.snr:
            m = summary[name][str(s)]["mean"][-1]
            md = summary[name][str(s)]["median"][-1]
            print(f"{name:8s} SNR {s:5.1f} BER {m[0]:.2e} SER {m[1]:.2e} "
                  f"NMSE r {m[2]:.1e} (med {md[2]:.1e}) v {m[3]:.1e} (med {md[3]:.1e})")


if __name__ == "__main__":
    main()
