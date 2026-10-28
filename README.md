# ISAC-NET run status (paper setup: combined SNR, -20..40 dB, 10 layers)

**Updated:** 2026-10-28 08:36 PM IST

_If this time stops moving, the Mac run has stopped (or the Mac is offline/asleep)._

**State:** RUNNING (pid 32587, elapsed 04:22:06)

**Current step:** `scripts/eval_isacnet.py`

## Stages started
```
== baselines ==
== train ISAC-NET (literal, one eta for all SNRs, 10 layers) ==
== evaluate literal ==
== evaluate Alg. 3 with 4 updates per layer ==
```

## Errors
```
(none)
```

## Last log lines
```
isacnet  SNR  25.0 BER 4.37e-01 SER 8.76e-01 NMSE r 7.6e-01 (med 4.8e-01) v 4.2e+04 (med 3.2e+04)
isacnet  SNR  30.0 BER 4.37e-01 SER 8.79e-01 NMSE r 1.1e+00 (med 4.8e-01) v 3.7e+04 (med 3.2e+04)
isacnet  SNR  40.0 BER 4.40e-01 SER 8.87e-01 NMSE r 1.1e+00 (med 4.8e-01) v 3.9e+04 (med 2.8e+04)
== evaluate Alg. 3 with 4 updates per layer ==
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
```

## Result files
```
Oct 28 20:12 results/isacnet_paper_literal.json
Oct 28 18:47 results/eta_paper_literal.json
Oct 28 16:30 results/baselines_paper.png
Oct 28 16:30 results/baselines_paper.json
```
