# ISAC-NET run status

**Updated:** 2026-10-25 10:56 PM IST

_If this time stops moving, the Mac run has stopped (or the Mac is offline/asleep)._

**State:** RUNNING (pid 45960, elapsed 02:28:59)

**Current step:** `scripts/train_isacnet.py`

## Stages started
```
== baselines (NumPy, on 12 CPU cores) ==
== train ISAC-NET (inner4) ==
== evaluate (inner4) ==
== train ISAC-NET (literal) ==
```

## Errors
```
(none)
```

## Last log lines
```
alg3     SNR   0.0 BER 7.98e-02 SER 2.93e-01 NMSE r 7.9e-02 (med 8.1e-08) v 7.8e-01 (med 1.6e-02)
alg3     SNR   5.0 BER 1.14e-02 SER 4.46e-02 NMSE r 5.2e-02 (med 8.1e-08) v 3.2e-01 (med 1.2e-02)
alg3     SNR  10.0 BER 1.64e-04 SER 6.45e-04 NMSE r 2.1e-02 (med 8.1e-08) v 1.8e-01 (med 1.2e-02)
alg3     SNR  15.0 BER 3.48e-05 SER 1.36e-04 NMSE r 1.1e-02 (med 8.1e-08) v 6.7e-02 (med 1.2e-02)
alg3     SNR  20.0 BER 0.00e+00 SER 0.00e+00 NMSE r 8.8e-03 (med 8.1e-08) v 1.3e-01 (med 1.2e-02)
alg3     SNR  25.0 BER 0.00e+00 SER 0.00e+00 NMSE r 1.6e-03 (med 8.1e-08) v 4.1e-02 (med 1.2e-02)
isacnet  SNR  -5.0 BER 1.90e-01 SER 5.99e-01 NMSE r 1.7e-01 (med 4.3e-05) v 1.1e+00 (med 3.9e-02)
isacnet  SNR   0.0 BER 7.98e-02 SER 2.93e-01 NMSE r 7.9e-02 (med 8.1e-08) v 7.8e-01 (med 1.6e-02)
isacnet  SNR   5.0 BER 2.71e-02 SER 8.32e-02 NMSE r 8.8e-02 (med 8.1e-08) v 2.8e-01 (med 1.2e-02)
isacnet  SNR  10.0 BER 2.78e-04 SER 1.10e-03 NMSE r 2.4e-02 (med 8.1e-08) v 1.8e-01 (med 1.2e-02)
isacnet  SNR  15.0 BER 3.47e-05 SER 1.35e-04 NMSE r 1.1e-02 (med 8.1e-08) v 6.7e-02 (med 1.2e-02)
isacnet  SNR  20.0 BER 0.00e+00 SER 0.00e+00 NMSE r 8.8e-03 (med 8.1e-08) v 1.3e-01 (med 1.2e-02)
isacnet  SNR  25.0 BER 0.00e+00 SER 0.00e+00 NMSE r 1.6e-03 (med 8.1e-08) v 4.1e-02 (med 1.2e-02)
wrote results/fig_gpu_inner4_{8,9,10}.png
== train ISAC-NET (literal) ==
```

## Result files
```
Oct 25 22:55 results/fig_gpu_inner4_8.png
Oct 25 22:55 results/fig_gpu_inner4_10.png
Oct 25 22:55 results/fig_gpu_inner4_9.png
Oct 25 22:54 results/isacnet_gpu_inner4.json
Oct 25 22:29 results/eta_gpu_inner4.json
Oct 25 20:38 results/baselines_full_gpu.png
Oct 25 20:38 results/baselines_full_gpu.json
```

### fig_gpu_inner4_10.png
![fig_gpu_inner4_10.png](fig_gpu_inner4_10.png)

### fig_gpu_inner4_8.png
![fig_gpu_inner4_8.png](fig_gpu_inner4_8.png)

### fig_gpu_inner4_9.png
![fig_gpu_inner4_9.png](fig_gpu_inner4_9.png)
