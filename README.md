# ISAC-NET run status (paper setup retrain: lower lr, 5 layers, 0-25 dB)

**Updated:** 2026-10-31 10:48 AM IST

_If this time stops moving, the Mac run has stopped (or the Mac is offline/asleep)._

**State:** RUNNING (pid 53318, elapsed 12:40:06)

**Current step:** `scripts/eval_isacnet.py`

## Stages started
```
== stage A: test lr 0.002 ==
== stage B: train lr 0.002 ==
== stage C: evaluate literal, with window ==
== stage C: evaluate literal, no window ==
```

## Errors
```
(none)
```

## Last log lines
```
isacnet  SNR  30.0 BER 7.89e-04 SER 3.15e-03 NMSE r 1.8e-02 (med 8.1e-08) v 1.0e-01 (med 1.2e-02)
isacnet  SNR  40.0 BER 7.09e-04 SER 2.83e-03 NMSE r 2.3e-02 (med 8.1e-08) v 9.4e-02 (med 1.2e-02)
== stage C: evaluate literal, no window ==
110/2200
220/2200
330/2200
440/2200
550/2200
660/2200
770/2200
880/2200
990/2200
1100/2200
1210/2200
1320/2200
```

## Result files
```
Oct 31 02:52 results/isacnet_paper_lr_window.json
Oct 30 23:19 results/eta_paper_lr.json
Oct 30 22:08 results/eta_paper_lr_test.json
```
