# ISAC-NET run status (paper setup: combined SNR, -20..40 dB, 10 layers)

**Updated:** 2026-10-28 09:37 PM IST

_If this time stops moving, the Mac run has stopped (or the Mac is offline/asleep)._

**State:** RUNNING (pid 32587, elapsed 05:22:31)

**Current step:** `scripts/eval_isacnet.py`

## Stages started
```
== baselines ==
== train ISAC-NET (literal, one eta for all SNRs, 10 layers) ==
== evaluate literal ==
== evaluate Alg. 3 with 4 updates per layer ==
== evaluate with the search window ==
```

## Errors
```
(none)
```

## Last log lines
```
alg3     SNR  20.0 BER 5.47e-05 SER 2.17e-04 NMSE r 9.5e+00 (med 8.1e-08) v 9.3e+02 (med 1.2e-02)
alg3     SNR  25.0 BER 4.12e-07 SER 1.65e-06 NMSE r 5.9e+00 (med 8.1e-08) v 5.7e+02 (med 1.2e-02)
alg3     SNR  30.0 BER 2.06e-08 SER 8.24e-08 NMSE r 1.9e+00 (med 8.1e-08) v 1.5e+02 (med 1.2e-02)
alg3     SNR  40.0 BER 0.00e+00 SER 0.00e+00 NMSE r 9.5e-03 (med 8.1e-08) v 3.1e-02 (med 1.2e-02)
wrote results/paper_fig{8,9,10}.png
== evaluate with the search window ==
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
Oct 28 20:55 results/paper_fig8.png
Oct 28 20:55 results/paper_fig10.png
Oct 28 20:55 results/paper_fig9.png
Oct 28 20:55 results/isacnet_paper_inner4.json
Oct 28 20:12 results/isacnet_paper_literal.json
Oct 28 18:47 results/eta_paper_literal.json
Oct 28 16:30 results/baselines_paper.png
Oct 28 16:30 results/baselines_paper.json
```

### paper_fig10.png
![paper_fig10.png](paper_fig10.png)

### paper_fig8.png
![paper_fig8.png](paper_fig8.png)

### paper_fig9.png
![paper_fig9.png](paper_fig9.png)
