#!/usr/bin/env bash
# Full training + evaluation run for a CUDA GPU (or DEVICE=mps on Apple silicon).
#
#   bash scripts/run_gpu.sh              # everything, a few hours on one GPU
#   STEPS=50 TRIALS=20 bash scripts/run_gpu.sh   # quick check first
#
# Trains ISAC-NET twice: on our converging Alg. 3 (4 D-AMP updates per layer)
# and on the literal Alg. 3 (1 update per layer), then evaluates both and
# draws Figs. 8-10 into results/.
set -euo pipefail
cd "$(dirname "$0")/.."

DEVICE=${DEVICE:-cuda}
STEPS=${STEPS:-300}
BATCH=${BATCH:-4}
TRIALS=${TRIALS:-200}
SNR_TRAIN=${SNR_TRAIN:-"0 5 10 15 20 25"}
SNR_EVAL=${SNR_EVAL:-"-5 0 5 10 15 20 25"}
BASE_TRIALS=${BASE_TRIALS:-200}
CPU_WORKERS=${CPU_WORKERS:-$(python -c "import os; print(os.cpu_count())")}

common="--grid full --device $DEVICE --workers 1"

if [ ! -f results/baselines_full_gpu.json ]; then
  echo "== baselines (NumPy, on $CPU_WORKERS CPU cores) =="
  python scripts/sweep_baselines.py --grid full --trials "$BASE_TRIALS" --workers "$CPU_WORKERS" \
    --snr $SNR_EVAL --out results/baselines_full_gpu
fi

for inner in 4 1; do
  tag=$([ "$inner" = 1 ] && echo literal || echo inner4)
  echo "== train ISAC-NET ($tag) =="
  python scripts/train_isacnet.py $common --inner "$inner" --steps "$STEPS" --batch "$BATCH" \
    --val-frames 16 --val-every 20 --snr $SNR_TRAIN --out "results/eta_gpu_$tag.json"
  echo "== evaluate ($tag) =="
  python scripts/eval_isacnet.py $common --inner "$inner" --trials "$TRIALS" --snr $SNR_EVAL \
    --eta "results/eta_gpu_$tag.json" --out "results/isacnet_gpu_$tag"
  python scripts/plot_figures.py --baselines results/baselines_full_gpu.json \
    --isacnet "results/isacnet_gpu_$tag.json" --out "results/fig_gpu_${tag}_"
done
echo "done: results/fig_gpu_*"
