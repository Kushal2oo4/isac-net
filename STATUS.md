# ISAC-NET run status (paper setup retrain: lower lr, 5 layers, 0-25 dB)

**Updated:** 2026-10-31 02:22 PM IST

_If this time stops moving, the Mac run has stopped (or the Mac is offline/asleep)._

**State:** RUNNING (pid 53318, elapsed 16:13:42)

**Current step:** `scripts/eval_isacnet.py`

## Stages started
```
== stage A: test lr 0.002 ==
== stage B: train lr 0.002 ==
== stage C: evaluate literal, with window ==
== stage C: evaluate literal, no window ==
== stage C: evaluate 4 updates, with window ==
```

## Errors
```
(none)
```

## Last log lines
```
isacnet  SNR  15.0 BER 4.12e-01 SER 8.57e-01 NMSE r 6.9e-01 (med 4.8e-01) v 3.3e+04 (med 2.6e+04)
isacnet  SNR  20.0 BER 4.18e-01 SER 8.65e-01 NMSE r 6.6e-01 (med 4.8e-01) v 3.5e+04 (med 2.6e+04)
isacnet  SNR  25.0 BER 4.19e-01 SER 8.59e-01 NMSE r 8.5e-01 (med 4.8e-01) v 3.7e+04 (med 2.7e+04)
isacnet  SNR  30.0 BER 4.14e-01 SER 8.59e-01 NMSE r 8.0e-01 (med 4.8e-01) v 3.1e+04 (med 2.7e+04)
isacnet  SNR  40.0 BER 4.25e-01 SER 8.73e-01 NMSE r 7.2e-01 (med 4.8e-01) v 3.3e+04 (med 2.5e+04)
== stage C: evaluate 4 updates, with window ==
110/2200
220/2200
330/2200
440/2200
550/2200
660/2200
770/2200
880/2200
990/2200
```

## Result files
```
Oct 31 13:58 results/isacnet_paper_lr.json
Oct 31 02:52 results/isacnet_paper_lr_window.json
Oct 30 23:19 results/eta_paper_lr.json
Oct 30 22:08 results/eta_paper_lr_test.json
```
