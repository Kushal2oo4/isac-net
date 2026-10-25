# ISAC-NET run status

**Updated:** 2026-10-25 08:56 PM IST

_If this time stops moving, the Mac run has stopped (or the Mac is offline/asleep)._

**State:** RUNNING (pid 45960, elapsed 28:27)

**Current step:** `scripts/train_isacnet.py`

## Stages started
```
== baselines (NumPy, on 12 CPU cores) ==
== train ISAC-NET (inner4) ==
```

## Errors
```
(none)
```

## Last log lines
```
SNR  20.0 | perfect_csi=0.00e+00 map_ls=5.15e-09 damp_ls=1.55e-08 map_recon=0.00e+00 | dft2d=(4.2e-01,2.4e-01) dft2d_clean=(5.0e-03,7.8e-02) sense_pilot=(1.8e-02,2.3e-01) sense_perfect=(5.0e-03,7.8e-02)
SNR  25.0 | perfect_csi=0.00e+00 map_ls=0.00e+00 damp_ls=0.00e+00 map_recon=0.00e+00 | dft2d=(4.4e-01,2.4e-01) dft2d_clean=(1.9e-03,2.3e-02) sense_pilot=(6.7e-03,1.1e-01) sense_perfect=(1.9e-03,2.3e-02)
== train ISAC-NET (inner4) ==
[snr 0] step 20/300 train 0.9395 val 0.8000 (best 0.4812, Alg. 3 0.4812) (471s)
[snr 10] step 20/300 train 0.4286 val 0.3089 (best 0.3089, Alg. 3 0.3091) (471s)
[snr 25] step 20/300 train 0.0412 val 0.0139 (best 0.0138, Alg. 3 0.0138) (471s)
[snr 20] step 20/300 train 0.2480 val 0.0150 (best 0.0149, Alg. 3 0.0149) (472s)
[snr 5] step 20/300 train 0.5789 val 0.0559 (best 0.0559, Alg. 3 0.0570) (472s)
[snr 15] step 20/300 train 0.1318 val 0.0195 (best 0.0195, Alg. 3 0.0195) (472s)
[snr 15] step 40/300 train 0.1191 val 0.0194 (best 0.0194, Alg. 3 0.0195) (924s)
[snr 0] step 40/300 train 0.9945 val 0.8132 (best 0.4812, Alg. 3 0.4812) (924s)
[snr 10] step 40/300 train 0.1337 val 0.3089 (best 0.3089, Alg. 3 0.3091) (924s)
[snr 25] step 40/300 train 0.0806 val 0.0139 (best 0.0138, Alg. 3 0.0138) (924s)
[snr 5] step 40/300 train 0.4871 val 0.0556 (best 0.0556, Alg. 3 0.0570) (925s)
[snr 20] step 40/300 train 0.1658 val 0.0149 (best 0.0149, Alg. 3 0.0149) (925s)
```

## Result files
```
Oct 25 20:38 results/baselines_full_gpu.png
Oct 25 20:38 results/baselines_full_gpu.json
```
