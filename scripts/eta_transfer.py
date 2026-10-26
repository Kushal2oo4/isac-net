"""Per-frame BER of Alg. 3, ISAC-NET with its own SNR's eta, and ISAC-NET with
the eta trained at another SNR. Shows whether a poor mean BER comes from a few
failed frames.

    python scripts/eta_transfer.py --eta results/eta_gpu_literal.json --inner 1 --snr 15 20 --from-snr 25
"""
import argparse
import json
import os
import sys
from multiprocessing import Pool

import numpy as np
import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from isacnet import SimConfig  # noqa: E402
from isacnet.isac_net import ISACNet  # noqa: E402
from isacnet.metrics import ber_ser  # noqa: E402
from isacnet.modulation import hard_decision  # noqa: E402
from isacnet.simulator import make_frame  # noqa: E402


def one_trial(job):
    args, table, snr, trial = job
    torch.set_num_threads(1)
    cfg = SimConfig()
    frame = make_frame(cfg, snr, np.random.default_rng([args.seed + 99, int(snr * 10) + 1000, trial]))
    etas = {"alg3": None, "own": table[str(float(snr))], f"eta{args.from_snr:g}": table[str(float(args.from_snr))]}
    out = {}
    for name, eta in etas.items():
        net = ISACNet(cfg, n_layers=5, n_inner=args.inner)
        with torch.no_grad():
            if eta is not None:
                net.eta.copy_(torch.tensor(eta))
            x = net(frame)["x"].numpy()
        idx = np.full(frame.idx.shape, -1)
        idx[frame.data_mask] = hard_decision(x)
        out[name] = ber_ser(idx, frame.idx, frame.data_mask)[0]
    return snr, out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--eta", required=True, help="JSON written by train_isacnet.py")
    p.add_argument("--inner", type=int, default=1)
    p.add_argument("--snr", type=float, nargs="+", default=[15, 20])
    p.add_argument("--from-snr", type=float, default=25)
    p.add_argument("--trials", type=int, default=24)
    p.add_argument("--workers", type=int, default=os.cpu_count())
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args()

    table = json.load(open(args.eta))["eta"]
    jobs = [(args, table, s, t) for s in args.snr for t in range(args.trials)]
    with Pool(args.workers) as pool:
        res = pool.map(one_trial, jobs)
    for s in args.snr:
        for name in res[0][1]:
            b = np.array([r[name] for ss, r in res if ss == s])
            print(f"SNR {s:g} {name:8s} mean BER {b.mean():.2e} median {np.median(b):.2e} "
                  f"frames with BER > 1e-2: {(b > 1e-2).sum()}/{len(b)}")


if __name__ == "__main__":
    main()
