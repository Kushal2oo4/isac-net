# ISAC-NET run status (paper setup: combined SNR, -20..40 dB, 10 layers)

**Updated:** 2026-10-28 10:37 PM IST

_If this time stops moving, the Mac run has stopped (or the Mac is offline/asleep)._

**State:** RUNNING (pid 32587, elapsed 06:22:56)

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
isacnet  SNR  10.0 BER 6.58e-02 SER 2.46e-01 NMSE r 6.6e-02 (med 8.1e-08) v 6.0e-01 (med 1.6e-02)
isacnet  SNR  15.0 BER 7.77e-03 SER 3.05e-02 NMSE r 6.3e-02 (med 8.1e-08) v 3.0e-01 (med 1.2e-02)
isacnet  SNR  20.0 BER 1.64e-04 SER 6.49e-04 NMSE r 2.3e-02 (med 8.1e-08) v 3.0e-01 (med 1.2e-02)
isacnet  SNR  25.0 BER 1.43e-04 SER 5.68e-04 NMSE r 8.6e-03 (med 8.1e-08) v 1.4e-01 (med 1.2e-02)
isacnet  SNR  30.0 BER 2.12e-05 SER 8.49e-05 NMSE r 6.1e-03 (med 8.1e-08) v 4.8e-02 (med 1.2e-02)
isacnet  SNR  40.0 BER 1.03e-08 SER 4.12e-08 NMSE r 9.5e-03 (med 8.1e-08) v 3.1e-02 (med 1.2e-02)
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
Oct 28 22:18 results/isacnet_paper_literal_window.json
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
