# ISAC-NET run status

**Updated:** 2026-10-25 11:47 PM IST

_If this time stops moving, the Mac run has stopped (or the Mac is offline/asleep)._

**State:** RUNNING (pid 45960, elapsed 03:19:14)

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
[snr 10] step 120/300 train 1.0435 val 0.9606 (best 0.7679, Alg. 3 1.2953) (2213s)
[snr 15] step 120/300 train 0.6655 val 0.1998 (best 0.1720, Alg. 3 1.2249) (2213s)
[snr 5] step 120/300 train 2.1495 val 0.0608 (best 0.0608, Alg. 3 0.6157) (2217s)
[snr 25] step 140/300 train 2.8283 val 0.1865 (best 0.0180, Alg. 3 0.2924) (2597s)
[snr 20] step 140/300 train 0.7861 val 0.1902 (best 0.1808, Alg. 3 0.4002) (2597s)
[snr 15] step 140/300 train 1.1674 val 0.6540 (best 0.1720, Alg. 3 1.2249) (2597s)
[snr 0] step 140/300 train 2.5948 val 1.0855 (best 0.8037, Alg. 3 1.2844) (2598s)
[snr 10] step 140/300 train 1.0843 val 0.3811 (best 0.3811, Alg. 3 1.2953) (2600s)
[snr 5] step 140/300 train 1.7183 val 0.0732 (best 0.0608, Alg. 3 0.6157) (2602s)
[snr 0] step 160/300 train 1.1634 val 1.2573 (best 0.8037, Alg. 3 1.2844) (2987s)
[snr 20] step 160/300 train 0.6185 val 0.1524 (best 0.1524, Alg. 3 0.4002) (2988s)
[snr 25] step 160/300 train 0.8517 val 0.2000 (best 0.0180, Alg. 3 0.2924) (2988s)
[snr 15] step 160/300 train 0.5340 val 0.6212 (best 0.1720, Alg. 3 1.2249) (2989s)
[snr 10] step 160/300 train 2.2608 val 0.6294 (best 0.3811, Alg. 3 1.2953) (2993s)
[snr 5] step 160/300 train 0.9896 val 0.0817 (best 0.0608, Alg. 3 0.6157) (2993s)
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
