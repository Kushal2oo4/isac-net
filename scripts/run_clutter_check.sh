#!/usr/bin/env bash
# Quick check: how much does distributed clutter (Sagduyu et al., arXiv 2610.40586) hurt
# Alg. 3 and the trained ISAC-NET (eta_paper_lr.json, one eta for 0-25 dB, trained without clutter)?
# Paper setup, literal Alg. 3 (1 update/layer), 5 layers, search window on.
#   TRIALS=16 bash scripts/run_clutter_check.sh
set -euo pipefail
cd "$(dirname "$0")/.."
TRIALS=${TRIALS:-16}
WORKERS=${WORKERS:-$(python -c "import os; print(os.cpu_count())")}
SNR=${SNR:-"10 20"}
paper="--grid full --snr-def combined --ls first --inner 1 --layers 5"
for nc in 0 5 20; do
  for a in 0.1 1; do
    [ "$nc" = 0 ] && [ "$a" = 0.1 ] && continue
    echo "== N_c=$nc alpha_c=$a =="
    python scripts/eval_isacnet.py $paper --trials "$TRIALS" --snr $SNR --workers "$WORKERS" \
      --eta results/eta_paper_lr.json --clutter "$nc" --clutter-strength "$a" --clutter-doppler 30 \
      --out "results/clutter_nc${nc}_a${a}"
  done
done
