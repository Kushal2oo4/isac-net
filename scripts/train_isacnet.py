"""Train ISAC-NET's per-layer hyper-parameters, one set per SNR (Sec. IV-B).

    python scripts/train_isacnet.py --grid full --snr 0 5 10 15 20 --steps 60 --out results/eta_full.json

Frames are generated on the fly. The paper splits a MATLAB data set 95/5 %
into train/test; with fresh random frames at every step, training and
evaluation data never overlap.
"""
import argparse
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np
import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from isacnet import SimConfig, small_config  # noqa: E402
from isacnet.isac_net import ISACNet, isac_loss  # noqa: E402
from isacnet.simulator import make_frame  # noqa: E402


def make_cfg(args):
    cfg = SimConfig() if args.grid == "full" else small_config()
    cfg.path_loss = args.path_loss
    return cfg


def train_one(job):
    args, snr = job
    torch.set_num_threads(max(1, args.threads))
    cfg = make_cfg(args)
    torch.manual_seed(args.seed)
    rng = np.random.default_rng([args.seed, 7, int(snr * 10) + 1000])
    net = ISACNet(cfg, n_layers=args.layers, report=args.report)
    opt = torch.optim.Adam(net.parameters(), lr=args.lr)
    log = []
    t0 = time.time()
    for it in range(args.steps):
        opt.zero_grad()
        tot, com = 0.0, 0.0
        for _ in range(args.batch):
            frame = make_frame(cfg, snr, rng)
            loss, comm = isac_loss(net(frame), frame, cfg, lam=args.lam)
            (loss / args.batch).backward()
            tot += loss.item() / args.batch
            com += comm.item() / args.batch
        opt.step()
        with torch.no_grad():  # keep the blending weights in [0, 1]
            net.eta[:, 3:].clamp_(0.0, 1.0)
        log.append((tot, com))
        if (it + 1) % max(1, args.steps // 10) == 0:
            print(f"[snr {snr:g}] step {it + 1}/{args.steps} loss {np.mean([l[0] for l in log[-5:]]):.4f} "
                  f"comm-mse {np.mean([l[1] for l in log[-5:]]):.4f} ({time.time() - t0:.0f}s)", flush=True)
    return snr, net.eta.detach().numpy().tolist(), log


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--grid", choices=["small", "full"], default="small")
    p.add_argument("--path-loss", choices=["physical", "equal"], default="physical")
    p.add_argument("--snr", type=float, nargs="+", default=[0, 5, 10, 15, 20])
    p.add_argument("--layers", type=int, default=5)
    p.add_argument("--steps", type=int, default=60)
    p.add_argument("--batch", type=int, default=2)
    p.add_argument("--lr", type=float, default=0.02)
    p.add_argument("--lam", type=float, default=1.0, help="weight of the sensing NMSE in the loss")
    p.add_argument("--report", choices=["grid", "fine"], default="grid")
    p.add_argument("--workers", type=int, default=min(os.cpu_count(), 5))
    p.add_argument("--threads", type=int, default=1, help="torch threads per worker")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out", default="results/eta.json")
    args = p.parse_args()

    with Pool(args.workers) as pool:
        res = pool.map(train_one, [(args, s) for s in args.snr])
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as f:
        json.dump({"args": vars(args),
                   "eta": {str(s): eta for s, eta, _ in res},
                   "loss": {str(s): log for s, _, log in res}}, f, indent=1)
    for s, eta, _ in res:
        print(f"SNR {s:g}:", np.round(eta, 3).tolist())


if __name__ == "__main__":
    main()
