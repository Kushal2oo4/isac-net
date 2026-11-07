#!/usr/bin/env bash
# One ISAC-NET for all conditions: a single eta trained on frames whose SNR (uniform 0-25 dB) and
# clutter (N_c in 0..20, alpha_c log-uniform 0.01-1, sigma_f,c uniform 0-30 Hz) are drawn at random
# per frame, in the spirit of Sagduyu et al. (arXiv 2610.40586, Sec. VI). Then evaluate it against
# the clutter-free-trained eta (results/eta_paper_lr.json) on clean and cluttered test frames.
#
#   DEVICE=cpu THREADS=8 bash scripts/run_clutter_train.sh      # Apple silicon (MPS lacks complex solve)
set -euo pipefail
cd "$(dirname "$0")/.."
DEVICE=${DEVICE:-cpu}
THREADS=${THREADS:-8}
STEPS=${STEPS:-150}
BATCH=${BATCH:-8}
TRIALS=${TRIALS:-50}
WORKERS=${WORKERS:-$(python -c "import os; print(os.cpu_count())")}
paper="--grid full --snr-def combined --ls first --inner 1 --layers 5"

echo "== train: one eta, random SNR + clutter =="
python scripts/train_isacnet.py $paper --device "$DEVICE" --workers 1 --threads "$THREADS" \
  --joint --snr 0 25 --snr-uniform --random-clutter --clutter 20 --clutter-strength 1 --clutter-doppler 30 \
  --lr 0.002 --steps "$STEPS" --batch "$BATCH" --val-frames 48 --val-every 15 \
  --out results/eta_clutter_rand.json
for cond in "0 1" "5 1" "20 0.1" "20 1"; do
  set -- $cond
  for eta in eta_paper_lr eta_clutter_rand; do
    echo "== eval $eta, N_c=$1 alpha_c=$2 =="
    python scripts/eval_isacnet.py $paper --trials "$TRIALS" --snr 0 5 10 15 20 25 --workers "$WORKERS" \
      --eta "results/$eta.json" --clutter "$1" --clutter-strength "$2" --clutter-doppler 30 \
      --out "results/clutter_eval_${eta}_nc$1_a$2"
  done
done
echo done
