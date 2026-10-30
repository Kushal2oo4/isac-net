# ISAC-NET run status (paper setup retrain: lower lr, 5 layers, 0-25 dB)

**Updated:** 2026-10-31 02:53 AM IST

_If this time stops moving, the Mac run has stopped (or the Mac is offline/asleep)._

**State:** RUNNING (pid 53318, elapsed 04:45:16)

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
alg3     SNR  25.0 BER 9.50e-03 SER 3.80e-02 NMSE r 1.0e-01 (med 8.1e-08) v 8.9e-01 (med 1.2e-02)
alg3     SNR  30.0 BER 5.56e-03 SER 2.22e-02 NMSE r 6.4e-02 (med 8.1e-08) v 5.9e-01 (med 1.2e-02)
alg3     SNR  40.0 BER 4.40e-03 SER 1.76e-02 NMSE r 4.8e-02 (med 8.1e-08) v 3.6e-01 (med 1.2e-02)
isacnet  SNR -20.0 BER 5.16e-01 SER 9.49e-01 NMSE r 5.2e-01 (med 3.0e-01) v 3.4e+00 (med 2.8e+00)
isacnet  SNR -10.0 BER 5.46e-01 SER 9.55e-01 NMSE r 4.8e-01 (med 2.5e-01) v 2.8e+00 (med 1.9e+00)
isacnet  SNR  -5.0 BER 3.82e-01 SER 8.60e-01 NMSE r 3.1e-01 (med 1.3e-01) v 1.8e+00 (med 9.4e-01)
isacnet  SNR   0.0 BER 2.87e-01 SER 7.60e-01 NMSE r 2.0e-01 (med 1.7e-02) v 1.1e+00 (med 2.0e-01)
isacnet  SNR   5.0 BER 1.73e-01 SER 5.62e-01 NMSE r 8.3e-02 (med 7.0e-06) v 6.0e-01 (med 2.8e-02)
isacnet  SNR  10.0 BER 7.07e-02 SER 2.60e-01 NMSE r 6.4e-02 (med 8.1e-08) v 4.9e-01 (med 1.6e-02)
isacnet  SNR  15.0 BER 1.34e-02 SER 5.30e-02 NMSE r 6.6e-02 (med 8.1e-08) v 2.5e-01 (med 1.2e-02)
isacnet  SNR  20.0 BER 2.54e-03 SER 1.01e-02 NMSE r 4.8e-02 (med 8.1e-08) v 2.0e-01 (med 1.2e-02)
isacnet  SNR  25.0 BER 8.28e-04 SER 3.31e-03 NMSE r 2.9e-02 (med 1.4e-07) v 1.3e-01 (med 1.2e-02)
isacnet  SNR  30.0 BER 7.89e-04 SER 3.15e-03 NMSE r 1.8e-02 (med 8.1e-08) v 1.0e-01 (med 1.2e-02)
isacnet  SNR  40.0 BER 7.09e-04 SER 2.83e-03 NMSE r 2.3e-02 (med 8.1e-08) v 9.4e-02 (med 1.2e-02)
== stage C: evaluate literal, no window ==
```

## Result files
```
Oct 31 02:52 results/isacnet_paper_lr_window.json
Oct 30 23:19 results/eta_paper_lr.json
Oct 30 22:08 results/eta_paper_lr_test.json
```
