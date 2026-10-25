# ISAC-NET run status

**Updated:** 2026-10-26 12:37 AM IST

_If this time stops moving, the Mac run has stopped (or the Mac is offline/asleep)._

**State:** RUNNING (pid 45960, elapsed 04:09:29)

**Current step:** `scripts/eval_isacnet.py`

## Stages started
```
== baselines (NumPy, on 12 CPU cores) ==
== train ISAC-NET (inner4) ==
== evaluate (inner4) ==
== train ISAC-NET (literal) ==
== evaluate (literal) ==
```

## Errors
```
(none)
```

## Last log lines
```
[snr 10] step 300/300 train 0.6294 val 0.5364 (best 0.3811, Alg. 3 1.2953) (5610s)
[snr 5] step 300/300 train 1.1297 val 0.0622 (best 0.0608, Alg. 3 0.6157) (5613s)
SNR 0: [[1.0, 0.0, 9.906, 0.043, 0.0], [1.0, -0.169, 9.908, 0.021, 0.095], [0.893, -0.109, 9.8, 0.008, 0.05], [0.892, 0.03, 9.965, 0.0, 0.073], [0.875, 0.0, 10.0, 0.196, 0.0]]
SNR 5: [[1.0, 0.0, 9.966, 0.059, 0.0], [1.0, -0.271, 9.758, 0.0, 0.191], [0.848, -0.116, 9.923, 0.0, 0.02], [0.892, -0.135, 10.241, 0.1, 0.166], [0.848, 0.0, 10.0, 0.229, 0.0]]
SNR 10: [[1.0, 0.0, 10.073, 0.196, 0.0], [1.0, -0.408, 10.184, 0.0, 0.213], [0.675, -0.153, 10.179, 0.0, 0.229], [0.929, -0.213, 10.085, 0.156, 0.076], [0.897, 0.0, 10.0, 0.182, 0.0]]
SNR 15: [[1.0, 0.0, 9.924, 0.088, 0.0], [1.0, -0.125, 9.901, 0.001, 0.01], [0.886, -0.1, 10.043, 0.0, 0.126], [0.903, 0.076, 10.086, 0.0, 0.0], [0.901, 0.0, 10.0, 0.041, 0.0]]
SNR 20: [[1.0, 0.0, 9.866, 0.149, 0.0], [1.0, -0.196, 9.944, 0.0, 0.102], [0.896, -0.131, 10.004, 0.001, 0.038], [0.916, -0.054, 10.239, 0.002, 0.196], [0.879, 0.0, 10.0, 0.017, 0.0]]
SNR 25: [[1.0, 0.0, 10.112, 0.0, 0.007], [1.0, -0.112, 9.957, 0.0, 0.016], [0.898, -0.081, 10.0, 0.0, 0.146], [0.925, 0.064, 10.05, 0.002, 0.013], [0.927, 0.0, 10.0, 0.011, 0.0]]
== evaluate (literal) ==
70/1400
140/1400
210/1400
280/1400
350/1400
420/1400
```

## Result files
```
Oct 26 00:29 results/eta_gpu_literal.json
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
