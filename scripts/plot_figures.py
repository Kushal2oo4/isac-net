"""Paper-style Figs. 8, 9, 10 from the sweep / eval JSON files.

    python scripts/plot_figures.py --baselines results/baselines_full_physical.json \
        --isacnet results/isacnet_full.json --out results/fig
"""
import argparse
import json
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from isacnet import SimConfig  # noqa: E402
from scripts.sweep_baselines import crb_nmse  # noqa: E402

LABELS = {"perfect_csi": "Perfect CSI", "map_ls": "MAP (LS CSI)", "damp_ls": "D-AMP (LS CSI)",
          "map_recon": "MAP (pilot sensing CSI)", "dft2d": "2D-DFT [5]", "dft2d_clean": "2D-DFT + extraction",
          "sense_pilot": "Pilot-only sensing", "sense_perfect": "Perfect (true X)",
          "alg3": "Alg. 3", "isacnet": "ISAC-NET"}
STYLE = {"alg3": "s-", "isacnet": "*-"}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--baselines", required=True)
    p.add_argument("--isacnet", required=True)
    p.add_argument("--stat", choices=["mean", "median"], default="median", help="NMSE statistic")
    p.add_argument("--out", default="results/fig")
    a = p.parse_args()
    def by_float(d):  # JSON keys may be "10" or "10.0"
        return {k: {float(s): v for s, v in sub.items()} for k, sub in d.items()}

    base = json.load(open(a.baselines))
    base = {"results": by_float(base["results"]), "median_nmse": by_float(base["median_nmse"])}
    net = by_float(json.load(open(a.isacnet))["results"])
    snrs = sorted(base["results"]["map_ls"])
    nsnr = sorted(next(iter(net.values())))
    key = lambda s: s  # noqa: E731

    # Fig. 9: BER and SER
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    for j, name in enumerate(["BER", "SER"]):
        for k in ["perfect_csi", "map_ls", "damp_ls", "map_recon"]:
            ax[j].semilogy(snrs, [max(base["results"][k][key(s)][j], 1e-7) for s in snrs], "o--",
                           label=LABELS[k], alpha=0.8)
        for k, d in net.items():
            ax[j].semilogy(nsnr, [max(d[key(s)]["mean"][-1][j], 1e-7) for s in nsnr], STYLE[k],
                           label=LABELS[k], lw=2)
        ax[j].set(xlabel="SNR [dB]", ylabel=name, title=f"{name} (cf. Fig. 9)")
    for x in ax:
        x.grid(True, which="both", alpha=0.3)
        x.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(a.out + "9.png", dpi=130)

    # Fig. 10: range and velocity NMSE
    cfg = SimConfig()
    crb = crb_nmse(cfg, snrs)
    src = base["median_nmse"] if a.stat == "median" else base["results"]
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    for j, name in enumerate(["range", "velocity"]):
        for k in ["dft2d", "sense_pilot", "sense_perfect"]:
            ax[j].semilogy(snrs, [src[k][key(s)][j] for s in snrs], "o--", label=LABELS[k], alpha=0.8)
        for k, d in net.items():
            ax[j].semilogy(nsnr, [d[key(s)][a.stat][-1][2 + j] for s in nsnr], STYLE[k], label=LABELS[k], lw=2)
        ax[j].semilogy(snrs, crb[j], "k:", label="CRB (paper's formula)")
        ax[j].set(xlabel="SNR [dB]", ylabel=f"NMSE ({a.stat})", title=f"{name} (cf. Fig. 10)")
    for x in ax:
        x.grid(True, which="both", alpha=0.3)
        x.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(a.out + "10.png", dpi=130)

    # Fig. 8: BER and NMSE versus layer
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    for s in [x for x in (0.0, 10.0) if x in nsnr]:
        for k, d in net.items():
            m = np.array(d[key(s)]["mean"])
            md = np.array(d[key(s)][a.stat])
            layers = np.arange(1, len(m) + 1)
            ax[0].semilogy(layers, np.maximum(m[:, 0], 1e-7), STYLE[k], label=f"{LABELS[k]}, {s:g} dB")
            ax[1].semilogy(layers, md[:, 2] + md[:, 3], STYLE[k], label=f"{LABELS[k]}, {s:g} dB")
    ax[0].set(xlabel="layer / iteration", ylabel="BER", title="BER vs layers (cf. Fig. 8a)")
    ax[1].set(xlabel="layer / iteration", ylabel=f"NMSE r + v ({a.stat})", title="NMSE vs layers (cf. Fig. 8b)")
    for x in ax:
        x.grid(True, which="both", alpha=0.3)
        x.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(a.out + "8.png", dpi=130)
    print("wrote", a.out + "{8,9,10}.png")


if __name__ == "__main__":
    main()
