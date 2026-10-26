"""Final Figs. 8, 9, 10: baselines, CRB and several ISAC-NET / Alg. 3 runs on one set of axes.

    python scripts/plot_final.py --baselines results/baselines_full_gpu.json \
        --run "Alg. 3 (literal)=results/isacnet_joint_literal.json:alg3" \
        --run "ISAC-NET, per-SNR η=results/isacnet_gpu_literal.json:isacnet" \
        --run "ISAC-NET, one η=results/isacnet_joint_literal.json:isacnet" \
        --run "Alg. 3, 4 updates/layer=results/isacnet_gpu_inner4.json:alg3" \
        --out results/final_fig

Each --run is "label=file.json:key", key being "alg3" or "isacnet" in an eval_isacnet.py file.
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
from scripts.plot_figures import LABELS  # noqa: E402
from scripts.sweep_baselines import crb_nmse  # noqa: E402

RUN_STYLE = ["s-", "*--", "o-", "^:"]
RUN_COLOR = ["0.45", "0.65", "C0", "C3"]


def nz(v):
    """Zero errors cannot be drawn on a log axis: leave the point out."""
    v = np.asarray(v, dtype=float)
    return np.where(v > 0, v, np.nan)


def by_float(d):  # JSON keys may be "10" or "10.0"
    return {k: {float(s): v for s, v in sub.items()} for k, sub in d.items()}


def load_run(spec):
    label, rest = spec.split("=", 1)
    path, key = rest.rsplit(":", 1)
    return label, by_float(json.load(open(path))["results"])[key]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--baselines", required=True)
    p.add_argument("--run", action="append", required=True, help='"label=file.json:key"')
    p.add_argument("--stat", choices=["mean", "median"], default="mean", help="NMSE statistic")
    p.add_argument("--layer-snr", type=float, nargs="+", default=[10, 20], help="SNRs for Fig. 8")
    p.add_argument("--out", default="results/final_fig")
    a = p.parse_args()

    raw = json.load(open(a.baselines))
    base = by_float(raw["results"])
    base_nmse = base if a.stat == "mean" else by_float(raw["median_nmse"])
    runs = [load_run(s) for s in a.run]
    snrs = sorted(base["map_ls"])

    def draw_runs(ax, value):
        for i, (label, d) in enumerate(runs):
            s = sorted(d)
            ax.semilogy(s, nz([value(d[x]) for x in s]), RUN_STYLE[i % 4], color=RUN_COLOR[i % 4],
                        lw=2.5 if RUN_COLOR[i % 4] == "C0" else 1.8, ms=6, label=label)

    def finish(fig, ax, name, shared_legend=False):
        for x in ax:
            x.grid(True, which="both", alpha=0.3)
            if not shared_legend:
                x.legend(fontsize=8)
        if shared_legend:
            fig.legend(*ax[0].get_legend_handles_labels(), loc="lower center", ncol=2, fontsize=8, frameon=False)
            fig.tight_layout(rect=(0, 0.2, 1, 1))
        else:
            fig.tight_layout()
        fig.savefig(a.out + name, dpi=150)

    # Fig. 9: BER and SER
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.3))
    for j, name in enumerate(["BER", "SER"]):
        for k in ["perfect_csi", "map_ls", "damp_ls", "map_recon"]:
            ax[j].semilogy(snrs, nz([base[k][s][j] for s in snrs]), "--", lw=1, alpha=0.7, label=LABELS[k])
        draw_runs(ax[j], lambda r: r["mean"][-1][j])
        ax[j].set(xlabel="SNR [dB]", ylabel=name, title=f"{name} (cf. Fig. 9, zero-error points left out)")
    finish(fig, ax, "9.png")

    # Fig. 10: range and velocity NMSE
    crb = crb_nmse(SimConfig(), snrs)
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.3))
    for j, name in enumerate(["Range", "Velocity"]):
        for k in ["dft2d_clean", "sense_pilot", "sense_perfect"]:
            ax[j].semilogy(snrs, [base_nmse[k][s][j] for s in snrs], "--", lw=1, alpha=0.7, label=LABELS[k])
        draw_runs(ax[j], lambda r: r[a.stat][-1][2 + j])
        ax[j].semilogy(snrs, crb[j], "k:", label="CRB (paper's formula)")
        ax[j].set(xlabel="SNR [dB]", ylabel=f"NMSE ({a.stat})", title=f"{name} NMSE (cf. Fig. 10)")
    finish(fig, ax, "10.png")

    # Fig. 8: BER and NMSE versus layer
    fig, ax = plt.subplots(1, 2, figsize=(11, 5.4))
    for s, ls in zip(a.layer_snr, ["-", "--"]):
        for i, (label, d) in enumerate(runs):
            if s not in d:
                continue
            m = np.array(d[s]["mean"])
            st = np.array(d[s][a.stat])
            layers = np.arange(1, len(m) + 1)
            kw = dict(ls=ls, marker=RUN_STYLE[i % 4][0], color=RUN_COLOR[i % 4], label=f"{label}, {s:g} dB")
            ax[0].semilogy(layers, nz(m[:, 0]), **kw)
            ax[1].semilogy(layers, st[:, 2] + st[:, 3], **kw)
    ax[0].set(xlabel="layer", ylabel="BER", title="BER vs layer (cf. Fig. 8a)")
    ax[1].set(xlabel="layer", ylabel=f"NMSE range + velocity ({a.stat})", title="NMSE vs layer (cf. Fig. 8b)")
    for x in ax:
        x.set_xticks(layers)
    finish(fig, ax, "8.png", shared_legend=True)
    print("wrote", a.out + "{8,9,10}.png")


if __name__ == "__main__":
    main()
