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
from isacnet import SimConfig, add_cfg_args, apply_cfg_args, small_config  # noqa: E402
from isacnet.torch_ops import pick_device  # noqa: E402
from isacnet.isac_net import ISACNet, isac_loss  # noqa: E402
from isacnet.simulator import make_frame  # noqa: E402


def make_cfg(args):
    cfg = SimConfig() if args.grid == "full" else small_config()
    cfg.path_loss = args.path_loss
    return apply_cfg_args(cfg, args)


# Box that keeps the learned D-AMP / blending weights in a stable range.
ETA_LO = [0.0, -1.0, 0.0, 0.0, 0.0]
ETA_HI = [1.5, 1.0, 30.0, 1.0, 1.0]


@torch.no_grad()
def validate(net, frames, cfg, lam):
    return float(np.mean([isac_loss(net(f), f, cfg, lam=lam)[0].item() for f in frames]))


def train_one(job):
    """Adam on eta with gradient clipping, a cosine learning-rate schedule and
    an eta box; keeps the eta with the lowest loss on a fixed validation set,
    starting from the hand-set Alg. 3 values, so training can never end up
    worse than Alg. 3 on that set.

    snr is one SNR, or a list of SNRs (--joint): then every frame, training and
    validation, draws its SNR uniformly from the list and one eta is learned."""
    args, snr = job
    torch.set_num_threads(max(1, args.threads))
    cfg = make_cfg(args)
    torch.manual_seed(args.seed)
    snrs = list(snr) if isinstance(snr, (list, tuple)) else [snr]
    key = 0 if len(snrs) > 1 else int(snrs[0] * 10) + 1000
    rng = np.random.default_rng([args.seed, 7, key])
    val_rng = np.random.default_rng([args.seed, 8, key])

    def draw(r):
        return make_frame(cfg, float(r.choice(snrs)), r)

    val = [draw(val_rng) for _ in range(args.val_frames)]
    snr = "joint" if len(snrs) > 1 else snrs[0]
    dev = pick_device(args.device)
    net = ISACNet(cfg, n_layers=args.layers, report=args.report, n_inner=args.inner, device=dev)
    lo = torch.tensor(ETA_LO, device=dev)
    hi = torch.tensor(ETA_HI, device=dev)
    opt = torch.optim.Adam(net.parameters(), lr=args.lr)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(1, args.steps))
    best_val = validate(net, val, cfg, args.lam)
    best_eta = net.eta.detach().cpu().numpy().tolist()
    log, vlog = [], [(0, best_val)]
    t0 = time.time()
    for it in range(args.steps):
        opt.zero_grad()
        tot, com = 0.0, 0.0
        for _ in range(args.batch):
            frame = draw(rng)
            loss, comm = isac_loss(net(frame), frame, cfg, lam=args.lam)
            (loss / args.batch).backward()
            tot += loss.item() / args.batch
            com += comm.item() / args.batch
        torch.nn.utils.clip_grad_norm_(net.parameters(), args.clip)
        opt.step()
        sched.step()
        with torch.no_grad():
            net.eta.copy_(torch.maximum(torch.minimum(net.eta, hi), lo))
        log.append((tot, com))
        if (it + 1) % args.val_every == 0 or it + 1 == args.steps:
            v = validate(net, val, cfg, args.lam)
            vlog.append((it + 1, v))
            if v < best_val:
                best_val, best_eta = v, net.eta.detach().cpu().numpy().tolist()
            print(f"[snr {snr}] step {it + 1}/{args.steps} train {np.mean([l[0] for l in log[-args.val_every:]]):.4f} "
                  f"val {v:.4f} (best {best_val:.4f}, Alg. 3 {vlog[0][1]:.4f}) ({time.time() - t0:.0f}s)", flush=True)
    return snr, best_eta, dict(train=log, val=vlog, last_eta=net.eta.detach().cpu().numpy().tolist())


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--grid", choices=["small", "full"], default="small")
    p.add_argument("--path-loss", choices=["physical", "equal"], default="physical")
    add_cfg_args(p)
    p.add_argument("--snr", type=float, nargs="+", default=[0, 5, 10, 15, 20])
    p.add_argument("--layers", type=int, default=5)
    p.add_argument("--inner", type=int, default=4, help="D-AMP updates per layer (1 = literal Alg. 3)")
    p.add_argument("--device", default="cpu", help="cpu, cuda, mps or auto; use --workers 1 on a GPU")
    p.add_argument("--steps", type=int, default=60)
    p.add_argument("--batch", type=int, default=2)
    p.add_argument("--lr", type=float, default=0.01)
    p.add_argument("--clip", type=float, default=1.0, help="gradient-norm clip")
    p.add_argument("--val-frames", type=int, default=4, help="fixed validation frames per SNR")
    p.add_argument("--val-every", type=int, default=10, help="validate every N steps")
    p.add_argument("--lam", type=float, default=1.0, help="weight of the sensing NMSE in the loss")
    p.add_argument("--report", choices=["grid", "fine"], default="grid")
    p.add_argument("--workers", type=int, default=min(os.cpu_count(), 5))
    p.add_argument("--threads", type=int, default=1, help="torch threads per worker")
    p.add_argument("--joint", action="store_true",
                   help="learn one eta over all --snr values (frames draw a random SNR) instead of one per SNR")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out", default="results/eta.json")
    args = p.parse_args()

    jobs = [(args, args.snr)] if args.joint else [(args, s) for s in args.snr]
    if args.workers > 1 and len(jobs) > 1:
        with Pool(args.workers) as pool:
            res = pool.map(train_one, jobs)
    else:  # GPUs: train the SNRs one after another in this process
        res = [train_one(j) for j in jobs]
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    if args.joint:  # same eta at every SNR, so eval_isacnet.py reads it unchanged
        _, eta, log = res[0]
        res = [(s, eta, log) for s in args.snr]
    with open(args.out, "w") as f:
        json.dump({"args": vars(args),
                   "eta": {str(s): eta for s, eta, _ in res},
                   "loss": {str(s): log for s, _, log in res}}, f, indent=1)
    for s, eta, _ in res:
        print(f"SNR {s:g}:", np.round(eta, 3).tolist())


if __name__ == "__main__":
    main()
