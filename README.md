# ISAC-NET run status

**Updated:** 2026-10-25 11:26 PM IST

_If this time stops moving, the Mac run has stopped (or the Mac is offline/asleep)._

**State:** RUNNING (pid 45960, elapsed 02:59:09)

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
[snr 25] step 60/300 train 0.0958 val 0.0250 (best 0.0180, Alg. 3 0.2924) (1109s)
[snr 15] step 60/300 train 1.1978 val 0.6277 (best 0.1720, Alg. 3 1.2249) (1109s)
[snr 5] step 60/300 train 2.8971 val 0.0936 (best 0.0718, Alg. 3 0.6157) (1110s)
[snr 20] step 80/300 train 2.4091 val 0.5082 (best 0.4002, Alg. 3 0.4002) (1473s)
[snr 0] step 80/300 train 0.9054 val 1.0096 (best 0.8037, Alg. 3 1.2844) (1473s)
[snr 10] step 80/300 train 1.0139 val 33.4018 (best 0.7679, Alg. 3 1.2953) (1474s)
[snr 25] step 80/300 train 0.1621 val 0.0971 (best 0.0180, Alg. 3 0.2924) (1474s)
[snr 5] step 80/300 train 4.3434 val 0.0610 (best 0.0610, Alg. 3 0.6157) (1474s)
[snr 15] step 80/300 train 0.2515 val 0.9351 (best 0.1720, Alg. 3 1.2249) (1475s)
[snr 0] step 100/300 train 0.8829 val 1.0597 (best 0.8037, Alg. 3 1.2844) (1843s)
[snr 20] step 100/300 train 1.8763 val 0.1808 (best 0.1808, Alg. 3 0.4002) (1843s)
[snr 25] step 100/300 train 3.8483 val 0.2076 (best 0.0180, Alg. 3 0.2924) (1843s)
[snr 10] step 100/300 train 4.0697 val 780.6520 (best 0.7679, Alg. 3 1.2953) (1844s)
[snr 15] step 100/300 train 11.6128 val 0.3109 (best 0.1720, Alg. 3 1.2249) (1844s)
[snr 5] step 100/300 train 2.0820 val 0.0613 (best 0.0610, Alg. 3 0.6157) (1847s)
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
