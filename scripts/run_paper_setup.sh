#!/usr/bin/env bash
# Rerun closer to the paper's figures: SNR after combining the Nr antennas, SNR from -20 to 40 dB,
# no range/velocity search window, the "conventional" LS channel held from the first pilot, and
# 10 layers (Fig. 8). Literal Alg. 3 with one eta for all SNRs, plus the 4-update Alg. 3 as reference.
#
#   bash scripts/run_paper_setup.sh                       # CUDA
#   DEVICE=cpu THREADS=8 bash scripts/run_paper_setup.sh  # Apple silicon
set -euo pipefail
cd "$(dirname "$0")/.."

DEVICE=${DEVICE:-cuda}
STEPS=${STEPS:-200}
BATCH=${BATCH:-8}
TRIALS=${TRIALS:-200}
LAYERS=${LAYERS:-10}
THREADS=${THREADS:-1}
SNR_TRAIN=${SNR_TRAIN:-"0 5 10 15 20 25 30 35 40"}
SNR_EVAL=${SNR_EVAL:-"-20 -10 -5 0 5 10 15 20 25 30 40"}
CPU_WORKERS=${CPU_WORKERS:-$(python -c "import os; print(os.cpu_count())")}
EVAL_WORKERS=$([ "$DEVICE" = cpu ] && echo "$CPU_WORKERS" || echo 1)
paper="--grid full --snr-def combined --ls first"

echo "== baselines =="
python scripts/sweep_baselines.py $paper --no-window --trials "$TRIALS" --workers "$CPU_WORKERS" \
  --snr $SNR_EVAL --out results/baselines_paper
# Training keeps the search window so that a missed target costs at most NMSE 1 in the loss.
echo "== train ISAC-NET (literal, one eta for all SNRs, $LAYERS layers) =="
python scripts/train_isacnet.py $paper --device "$DEVICE" --workers 1 --threads "$THREADS" \
  --inner 1 --layers "$LAYERS" --joint --steps "$STEPS" --batch "$BATCH" --val-frames 48 --val-every 20 \
  --snr $SNR_TRAIN --out results/eta_paper_literal.json
echo "== evaluate literal =="
python scripts/eval_isacnet.py $paper --no-window --device "$DEVICE" --workers "$EVAL_WORKERS" --inner 1 \
  --layers "$LAYERS" --trials "$TRIALS" --snr $SNR_EVAL --eta results/eta_paper_literal.json \
  --out results/isacnet_paper_literal
echo "== evaluate Alg. 3 with 4 updates per layer =="
python scripts/eval_isacnet.py $paper --no-window --device "$DEVICE" --workers "$EVAL_WORKERS" --inner 4 \
  --layers "$LAYERS" --trials "$TRIALS" --snr $SNR_EVAL --out results/isacnet_paper_inner4
python scripts/plot_final.py --baselines results/baselines_paper.json --layer-snr 0 10 \
  --run "Alg. 3 (literal)=results/isacnet_paper_literal.json:alg3" \
  --run "ISAC-NET, one η for all SNRs=results/isacnet_paper_literal.json:isacnet@2" \
  --run "Alg. 3, 4 updates/layer=results/isacnet_paper_inner4.json:alg3@3" \
  --out results/paper_fig
# The same receivers with the 200 m / 50 m/s search window, as in our earlier runs.
echo "== evaluate with the search window =="
python scripts/eval_isacnet.py $paper --device "$DEVICE" --workers "$EVAL_WORKERS" --inner 1 \
  --layers "$LAYERS" --trials "$TRIALS" --snr $SNR_EVAL --eta results/eta_paper_literal.json \
  --out results/isacnet_paper_literal_window
python scripts/eval_isacnet.py $paper --device "$DEVICE" --workers "$EVAL_WORKERS" --inner 4 \
  --layers "$LAYERS" --trials "$TRIALS" --snr $SNR_EVAL --out results/isacnet_paper_inner4_window
python scripts/plot_final.py --baselines results/baselines_paper.json --layer-snr 0 10 \
  --run "Alg. 3 (literal)=results/isacnet_paper_literal_window.json:alg3" \
  --run "ISAC-NET, one η for all SNRs=results/isacnet_paper_literal_window.json:isacnet@2" \
  --run "Alg. 3, 4 updates/layer=results/isacnet_paper_inner4_window.json:alg3@3" \
  --out results/paper_window_fig
echo "done: results/paper_fig{8,9,10}.png, results/paper_window_fig{8,9,10}.png"
