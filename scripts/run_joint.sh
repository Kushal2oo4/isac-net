#!/usr/bin/env bash
# Literal Alg. 3 (1 D-AMP update per layer) with one eta trained over all SNRs
# (--joint), then evaluated like run_gpu.sh. Compare with results/*_gpu_literal*.
#
#   bash scripts/run_joint.sh                       # CUDA
#   DEVICE=cpu THREADS=8 bash scripts/run_joint.sh  # Apple silicon (MPS lacks complex solve)
set -euo pipefail
cd "$(dirname "$0")/.."

DEVICE=${DEVICE:-cuda}
STEPS=${STEPS:-300}
BATCH=${BATCH:-8}
TRIALS=${TRIALS:-200}
THREADS=${THREADS:-1}
SNR_TRAIN=${SNR_TRAIN:-"0 5 10 15 20 25"}
SNR_EVAL=${SNR_EVAL:-"-5 0 5 10 15 20 25"}
CPU_WORKERS=${CPU_WORKERS:-$(python -c "import os; print(os.cpu_count())")}
EVAL_WORKERS=$([ "$DEVICE" = cpu ] && echo "$CPU_WORKERS" || echo 1)

echo "== train ISAC-NET (literal, one eta for all SNRs) =="
python scripts/train_isacnet.py --grid full --device "$DEVICE" --workers 1 --threads "$THREADS" \
  --inner 1 --joint --steps "$STEPS" --batch "$BATCH" --val-frames 48 --val-every 20 \
  --snr $SNR_TRAIN --out results/eta_joint_literal.json
echo "== evaluate =="
python scripts/eval_isacnet.py --grid full --device "$DEVICE" --workers "$EVAL_WORKERS" --inner 1 \
  --trials "$TRIALS" --snr $SNR_EVAL --eta results/eta_joint_literal.json --out results/isacnet_joint_literal
python scripts/plot_figures.py --baselines results/baselines_full_gpu.json \
  --isacnet results/isacnet_joint_literal.json --out results/fig_joint_literal_
echo "done: results/fig_joint_literal_*"
