# ISAC-NET run status (paper setup retrain: lower lr, 5 layers, 0-25 dB)

**Updated:** 2026-10-31 02:42 PM IST

_If this time stops moving, the Mac run has stopped (or the Mac is offline/asleep)._

**State:** FINISHED

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
2090/2200
2200/2200
alg3     SNR -20.0 BER 5.15e-01 SER 9.46e-01 NMSE r 5.2e-01 (med 3.0e-01) v 3.4e+00 (med 2.4e+00)
alg3     SNR -10.0 BER 4.36e-01 SER 8.95e-01 NMSE r 4.7e-01 (med 2.5e-01) v 2.9e+00 (med 2.4e+00)
alg3     SNR  -5.0 BER 3.79e-01 SER 8.51e-01 NMSE r 3.1e-01 (med 1.4e-01) v 2.2e+00 (med 1.0e+00)
alg3     SNR   0.0 BER 2.84e-01 SER 7.54e-01 NMSE r 1.8e-01 (med 2.1e-02) v 1.3e+00 (med 3.1e-01)
alg3     SNR   5.0 BER 1.68e-01 SER 5.49e-01 NMSE r 9.4e-02 (med 2.5e-06) v 7.8e-01 (med 1.6e-02)
alg3     SNR  10.0 BER 6.14e-02 SER 2.30e-01 NMSE r 6.2e-02 (med 8.1e-08) v 6.0e-01 (med 1.6e-02)
alg3     SNR  15.0 BER 5.99e-03 SER 2.36e-02 NMSE r 2.1e-02 (med 8.1e-08) v 2.3e-01 (med 1.2e-02)
alg3     SNR  20.0 BER 5.46e-05 SER 2.16e-04 NMSE r 2.2e-02 (med 8.1e-08) v 3.0e-01 (med 1.2e-02)
alg3     SNR  25.0 BER 4.02e-07 SER 1.61e-06 NMSE r 8.6e-03 (med 8.1e-08) v 1.4e-01 (med 1.2e-02)
alg3     SNR  30.0 BER 2.06e-08 SER 8.24e-08 NMSE r 6.1e-03 (med 8.1e-08) v 4.8e-02 (med 1.2e-02)
alg3     SNR  40.0 BER 0.00e+00 SER 0.00e+00 NMSE r 9.5e-03 (med 8.1e-08) v 3.1e-02 (med 1.2e-02)
wrote results/paper_lr_fig{8,9,10}.png
done: results/paper_lr_fig{8,9,10}.png
```

## Result files
```
Oct 31 14:36 results/paper_lr_fig8.png
Oct 31 14:36 results/paper_lr_fig10.png
Oct 31 14:36 results/paper_lr_fig9.png
Oct 31 13:58 results/isacnet_paper_lr.json
Oct 31 02:52 results/isacnet_paper_lr_window.json
Oct 30 23:19 results/eta_paper_lr.json
Oct 30 22:08 results/eta_paper_lr_test.json
```

### paper_lr_fig10.png
![paper_lr_fig10.png](paper_lr_fig10.png)

### paper_lr_fig8.png
![paper_lr_fig8.png](paper_lr_fig8.png)

### paper_lr_fig9.png
![paper_lr_fig9.png](paper_lr_fig9.png)
