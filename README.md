# ISAC-NET run status

**Updated:** 2026-10-26 12:07 AM IST

_If this time stops moving, the Mac run has stopped (or the Mac is offline/asleep)._

**State:** RUNNING (pid 45960, elapsed 03:39:20)

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
[snr 15] step 180/300 train 1.2514 val 0.2580 (best 0.1720, Alg. 3 1.2249) (3381s)
[snr 10] step 180/300 train 0.8055 val 0.3889 (best 0.3811, Alg. 3 1.2953) (3385s)
[snr 5] step 180/300 train 1.7536 val 0.0860 (best 0.0608, Alg. 3 0.6157) (3384s)
[snr 20] step 200/300 train 1.4625 val 0.1700 (best 0.1505, Alg. 3 0.4002) (3741s)
[snr 0] step 200/300 train 1.1905 val 1.9582 (best 0.8037, Alg. 3 1.2844) (3741s)
[snr 25] step 200/300 train 1.4162 val 0.1386 (best 0.0180, Alg. 3 0.2924) (3742s)
[snr 15] step 200/300 train 2.5091 val 3.4637 (best 0.1720, Alg. 3 1.2249) (3743s)
[snr 10] step 200/300 train 1.5913 val 0.5401 (best 0.3811, Alg. 3 1.2953) (3747s)
[snr 5] step 200/300 train 1.8619 val 0.0785 (best 0.0608, Alg. 3 0.6157) (3747s)
[snr 20] step 220/300 train 1.2602 val 0.8046 (best 0.1505, Alg. 3 0.4002) (4109s)
[snr 0] step 220/300 train 381.4346 val 1.8605 (best 0.8037, Alg. 3 1.2844) (4109s)
[snr 25] step 220/300 train 1.6895 val 0.1561 (best 0.0180, Alg. 3 0.2924) (4113s)
[snr 15] step 220/300 train 0.6187 val 0.2801 (best 0.1720, Alg. 3 1.2249) (4113s)
[snr 10] step 220/300 train 2.3200 val 0.5079 (best 0.3811, Alg. 3 1.2953) (4118s)
[snr 5] step 220/300 train 2.7035 val 0.0629 (best 0.0608, Alg. 3 0.6157) (4118s)
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
