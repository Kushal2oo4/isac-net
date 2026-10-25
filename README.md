# ISAC-NET run status

**Updated:** 2026-10-25 11:16 PM IST

_If this time stops moving, the Mac run has stopped (or the Mac is offline/asleep)._

**State:** RUNNING (pid 45960, elapsed 02:49:06)

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
[snr 15] step 20/300 train 0.9754 val 0.4671 (best 0.4671, Alg. 3 1.2249) (369s)
[snr 20] step 20/300 train 0.3872 val 0.5313 (best 0.4002, Alg. 3 0.4002) (369s)
[snr 5] step 20/300 train 0.8364 val 0.0718 (best 0.0718, Alg. 3 0.6157) (369s)
[snr 10] step 40/300 train 2.8896 val 1.7830 (best 0.7679, Alg. 3 1.2953) (737s)
[snr 0] step 40/300 train 8.2441 val 0.8037 (best 0.8037, Alg. 3 1.2844) (737s)
[snr 25] step 40/300 train 0.0875 val 0.0180 (best 0.0180, Alg. 3 0.2924) (737s)
[snr 20] step 40/300 train 2.8127 val 3.0344 (best 0.4002, Alg. 3 0.4002) (737s)
[snr 5] step 40/300 train 1.5540 val 0.1115 (best 0.0718, Alg. 3 0.6157) (737s)
[snr 15] step 40/300 train 0.5370 val 0.1720 (best 0.1720, Alg. 3 1.2249) (737s)
[snr 0] step 60/300 train 1.5014 val 0.9021 (best 0.8037, Alg. 3 1.2844) (1108s)
[snr 10] step 60/300 train 2.2755 val 2.1093 (best 0.7679, Alg. 3 1.2953) (1109s)
[snr 20] step 60/300 train 0.8073 val 0.6115 (best 0.4002, Alg. 3 0.4002) (1109s)
[snr 25] step 60/300 train 0.0958 val 0.0250 (best 0.0180, Alg. 3 0.2924) (1109s)
[snr 15] step 60/300 train 1.1978 val 0.6277 (best 0.1720, Alg. 3 1.2249) (1109s)
[snr 5] step 60/300 train 2.8971 val 0.0936 (best 0.0718, Alg. 3 0.6157) (1110s)
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
