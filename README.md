# ISAC-NET reproduction

A Python reproduction of *ISAC-NET: Model-Driven Deep Learning for Integrated
Passive Sensing and Communication* (Jiang et al., IEEE TCOM 2024).

## Status

| Step | Content | State |
|---|---|---|
| 1 | Simulator and baselines | done |
| 2 | Alg. 3 and ISAC-NET (deep unfolding, learnable η1..η5) | done (first training run) |
| 3 | Fig. 9 (BER/SER), Fig. 10 (range/velocity NMSE), Fig. 8 if time | |
| 4 | Report and list of research gaps | |

## Layout

```
isacnet/
  config.py      Table III parameters (SimConfig), small_config() for fast runs
  modulation.py  Gray 16-QAM, QPSK pilots
  channel.py     single-reflection MIMO-OFDM channel, eqs. (5)-(17)
  simulator.py   OFDM frame (pilot every 14th symbol) + received signal
  detection.py   LS pilot channel estimate, ML/MAP detection, improved D-AMP (Alg. 1)
  sensing.py     2D-DFT sensing, cyclic peak extraction, channel reconstruction (Alg. 2)
  baselines.py   all Fig. 9 / Fig. 10 baselines on one frame
  metrics.py     BER, SER, NMSE (eq. 43) with target matching
  isac_net.py    Alg. 3 / ISAC-NET (PyTorch, runs on CPU / CUDA / MPS), loss
  torch_ops.py   PyTorch versions of sensing, channel rebuild and 16-QAM decisions
scripts/sweep_baselines.py   Monte Carlo sweep of the baselines -> results/*.json + *.png
scripts/train_isacnet.py     learn eta per SNR -> results/eta_*.json
scripts/eval_isacnet.py      Alg. 3 vs ISAC-NET, final and per layer -> results/isacnet_*.json
scripts/plot_figures.py      paper-style Figs. 8, 9, 10
tests/                       pytest sanity checks
```

```
pip install numpy matplotlib pytest torch
python -m pytest -q
python scripts/sweep_baselines.py --grid small --trials 50              # minutes on a laptop
python scripts/sweep_baselines.py --grid full  --trials 500 --out results/baselines_full   # paper size
python scripts/train_isacnet.py   --grid full  --steps 30 --out results/eta_full.json
python scripts/eval_isacnet.py    --grid full  --eta results/eta_full.json --trials 40 --out results/isacnet_full
# on a GPU: one process, everything on the device
python scripts/train_isacnet.py   --grid full --device cuda --workers 1 --steps 300 --out results/eta_full_gpu.json
python scripts/eval_isacnet.py    --grid full --device cuda --workers 1 --eta results/eta_full_gpu.json --trials 200
# Apple silicon: --device mps (or --device cpu --workers 8 to use the cores)
python scripts/plot_figures.py    --baselines results/baselines_full_physical.json --isacnet results/isacnet_full.json
```

## Baselines

| Name | What it is | Paper |
|---|---|---|
| `perfect_csi` | ML detection with the true channel | "Perfect" line, Fig. 9 |
| `map_ls` | LS on pilots, linear interpolation in time, ML detection | "MAP / conventional", Fig. 9 |
| `damp_ls` | improved D-AMP (Alg. 1) on the LS channel, fixed η | Alg. 1 |
| `map_recon` | pilot-only sensing, then channel rebuilt from (r, v), then ML | one pass of the ISAC loop |
| `dft2d` | serial 2D-DFT on Y / X̂, top-L local maxima, no extraction | "2D-DFT [5]", Fig. 10 |
| `dft2d_clean` | same with cyclic peak extraction (Alg. 3 step 4) | |
| `sense_pilot` | cyclic extraction on pilot symbols only | rough estimate, Fig. 4 |
| `sense_perfect` | cyclic extraction with the true X | "Perfect" line, Fig. 10 |

## Where we had to interpret the paper

These are deliberate choices; each is a candidate discussion point in the report.

1. **Antenna model.** Eq. (6b) sends the same symbol from every transmit antenna, so
   `H_a^l` only enters as `g_l = H_a^l 1` (an Nr-vector). That makes the transmitter a
   fixed broadside beam: targets near its nulls are almost invisible.
2. **`H_φ` is diagonal** (eq. 14), so it is applied element-wise. The paper's
   O((MN)²) complexity treats it as a dense MN×MN matrix; the real cost is O(MN).
3. **D-AMP (Alg. 1).** We use the conjugate transpose instead of the plain
   transpose in (23), plus a step size μ = 0.5/‖h‖². Because (24) uses X^k (not X^{k+1}),
   η1 = 1, η2 = 0 oscillates for step ≥ 1. This sensitivity is the reason the η's need learning.
4. **Channel reconstruction (Alg. 2).** The paper estimates AoD/AoA and path loss. We
   fit the per-antenna gain of each path by least squares on the pilots, which covers all
   of them in one step.
5. **Cyclic peak extraction.** Before removing a peak we refine it off the grid and
   re-fit all gains jointly (OMP-style). Plain subtraction at the 10× grid leaves
   residues about 17 dB below the peak, and with physical path loss the 10 m target
   is about 40 dB stronger than the 100 m one, so those residues hide it.
6. **Velocity resolution.** By eq. (30) the bin is c/(T·M·fc) ≈ 28 m/s, which the 10×
   padding interpolates to 2.8 m/s. The 5/10/15 m/s targets are below resolution, so the
   reported grid estimates have an NMSE floor of about 1e-2. `report="fine"` removes
   most of that floor.
7. **Doppler sign / bistatic geometry.** We use f_d = v·fc/c and r = r1 + r2 (eqs. 16, 32).
   The paper's CRB line uses c/(2B) and c/(2TMfc), a factor 2 finer than eqs. (30)–(31) give.
8. **Search window.** Sensing only searches r ≤ 200 m and |v| ≤ 50 m/s
   (`cfg.max_range`, `cfg.max_speed`).
9. **SNR** is the received-signal SNR: each frame's channel is normalised so that E|Hx|² = 1.
10. **Alg. 3 / ISAC-NET layer.** Each layer runs 4 D-AMP updates with that layer's η1, η2.
   With a single update per layer, starting from X = Z = 0, the detector is still far from
   converged after 5 layers (BER about 4e-2 at 20 dB), which contradicts Fig. 8.
11. **η4, η5.** Eqs. (40) and (42) read "η·old + new". We use convex combinations
    (η·old + (1 − η)·new), so r, v and H stay unbiased for any η.
12. **η3** is a hard threshold in the paper. It is replaced by a sigmoid gate on the peak
    height in dB, so it can be trained (`tau_db` sets how soft the gate is). Argmax peak search and
    hard symbol decisions run outside autograd; gradients reach the η's through the
    continuous steps (D-AMP updates, blending, channel rebuild).
13. **Training.** We use Adam with lr 0.02 for 30 steps of 2 fresh frames per SNR, not the paper's
    500 epochs × batch 128 at lr 0.001. With only 25 parameters the η's settle quickly,
    but a longer run on the lab GPU is the obvious next step.
