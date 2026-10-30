# ISAC-NET run status (paper setup retrain: lower lr, 5 layers, 0-25 dB)

**Updated:** 2026-10-30 11:20 PM IST

_If this time stops moving, the Mac run has stopped (or the Mac is offline/asleep)._

**State:** RUNNING (pid 53318, elapsed 01:12:00)

**Current step:** `scripts/eval_isacnet.py`

## Stages started
```
== stage A: test lr 0.002 ==
== stage B: train lr 0.002 ==
== stage C: evaluate literal, with window ==
```

## Errors
```
(none)
```

## Last log lines
```
[snr joint] step 60/200 train 0.8839 val 0.9651 (best 0.9651, Alg. 3 1.9665) (1250s)
[snr joint] step 80/200 train 0.8974 val 0.8499 (best 0.8499, Alg. 3 1.9665) (1676s)
[snr joint] step 100/200 train 0.9670 val 0.8419 (best 0.8419, Alg. 3 1.9665) (2091s)
[snr joint] step 120/200 train 0.9397 val 0.9756 (best 0.8419, Alg. 3 1.9665) (2485s)
[snr joint] step 140/200 train 1.0230 val 0.9541 (best 0.8419, Alg. 3 1.9665) (2872s)
[snr joint] step 160/200 train 0.9709 val 0.9498 (best 0.8419, Alg. 3 1.9665) (3287s)
[snr joint] step 180/200 train 0.8704 val 0.9052 (best 0.8419, Alg. 3 1.9665) (3717s)
[snr joint] step 200/200 train 0.7717 val 1.0270 (best 0.8419, Alg. 3 1.9665) (4143s)
SNR 0: [[1.0, 0.0, 9.89, 0.0, 0.127], [1.0, -0.1, 9.918, 0.0, 0.002], [0.896, -0.107, 9.945, 0.0, 0.089], [0.893, 0.112, 9.967, 0.017, 0.0], [0.894, 0.0, 10.0, 0.134, 0.0]]
SNR 5: [[1.0, 0.0, 9.89, 0.0, 0.127], [1.0, -0.1, 9.918, 0.0, 0.002], [0.896, -0.107, 9.945, 0.0, 0.089], [0.893, 0.112, 9.967, 0.017, 0.0], [0.894, 0.0, 10.0, 0.134, 0.0]]
SNR 10: [[1.0, 0.0, 9.89, 0.0, 0.127], [1.0, -0.1, 9.918, 0.0, 0.002], [0.896, -0.107, 9.945, 0.0, 0.089], [0.893, 0.112, 9.967, 0.017, 0.0], [0.894, 0.0, 10.0, 0.134, 0.0]]
SNR 15: [[1.0, 0.0, 9.89, 0.0, 0.127], [1.0, -0.1, 9.918, 0.0, 0.002], [0.896, -0.107, 9.945, 0.0, 0.089], [0.893, 0.112, 9.967, 0.017, 0.0], [0.894, 0.0, 10.0, 0.134, 0.0]]
SNR 20: [[1.0, 0.0, 9.89, 0.0, 0.127], [1.0, -0.1, 9.918, 0.0, 0.002], [0.896, -0.107, 9.945, 0.0, 0.089], [0.893, 0.112, 9.967, 0.017, 0.0], [0.894, 0.0, 10.0, 0.134, 0.0]]
SNR 25: [[1.0, 0.0, 9.89, 0.0, 0.127], [1.0, -0.1, 9.918, 0.0, 0.002], [0.896, -0.107, 9.945, 0.0, 0.089], [0.893, 0.112, 9.967, 0.017, 0.0], [0.894, 0.0, 10.0, 0.134, 0.0]]
== stage C: evaluate literal, with window ==
```

## Result files
```
Oct 30 23:19 results/eta_paper_lr.json
Oct 30 22:08 results/eta_paper_lr_test.json
```
