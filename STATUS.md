# ISAC-NET run status (paper setup: combined SNR, -20..40 dB, 10 layers)

**Updated:** 2026-10-28 06:45 PM IST

_If this time stops moving, the Mac run has stopped (or the Mac is offline/asleep)._

**State:** RUNNING (pid 32587, elapsed 02:30:51)

**Current step:** `scripts/train_isacnet.py`

## Stages started
```
== baselines ==
== train ISAC-NET (literal, one eta for all SNRs, 10 layers) ==
```

## Errors
```
(none)
```

## Last log lines
```
SNR  15.0 | perfect_csi=4.79e-03 map_ls=2.41e-01 damp_ls=2.44e-01 map_recon=5.25e-03 | dft2d=(4.4e-01,1.5e+00) dft2d_clean=(2.3e+00,1.4e+04) sense_pilot=(4.0e+01,2.2e+01) sense_perfect=(2.7e+01,2.0e+03)
SNR  20.0 | perfect_csi=2.30e-05 map_ls=2.19e-01 damp_ls=2.20e-01 map_recon=2.95e-05 | dft2d=(4.1e-01,1.5e+00) dft2d_clean=(1.3e+00,1.4e+04) sense_pilot=(2.6e+01,1.4e+01) sense_perfect=(1.7e+01,1.8e+03)
SNR  25.0 | perfect_csi=3.09e-08 map_ls=2.17e-01 damp_ls=2.17e-01 map_recon=2.16e-07 | dft2d=(4.4e-01,3.3e+00) dft2d_clean=(2.1e+00,8.0e+03) sense_pilot=(1.8e+01,1.1e+01) sense_perfect=(4.9e+00,6.1e+02)
SNR  30.0 | perfect_csi=4.42e-06 map_ls=2.18e-01 damp_ls=2.18e-01 map_recon=6.17e-06 | dft2d=(4.6e-01,4.5e+00) dft2d_clean=(4.1e+00,9.4e+02) sense_pilot=(1.0e+01,4.1e+00) sense_perfect=(4.0e+00,4.1e+02)
SNR  40.0 | perfect_csi=0.00e+00 map_ls=2.23e-01 damp_ls=2.23e-01 map_recon=3.09e-08 | dft2d=(4.7e-01,4.4e+00) dft2d_clean=(1.3e+00,1.4e+02) sense_pilot=(4.8e+00,2.3e+00) sense_perfect=(1.3e+00,1.6e+02)
== train ISAC-NET (literal, one eta for all SNRs, 10 layers) ==
[snr joint] step 20/200 train 0.6647 val 2.2488 (best 0.6664, Alg. 3 0.6664) (776s)
[snr joint] step 40/200 train 1.5817 val 1.8075 (best 0.6664, Alg. 3 0.6664) (1585s)
[snr joint] step 60/200 train 2.1599 val 1.3816 (best 0.6664, Alg. 3 0.6664) (2394s)
[snr joint] step 80/200 train 1.8750 val 2.7398 (best 0.6664, Alg. 3 0.6664) (3201s)
[snr joint] step 100/200 train 2.0231 val 1.2261 (best 0.6664, Alg. 3 0.6664) (4006s)
[snr joint] step 120/200 train 2.4434 val 4.6536 (best 0.6664, Alg. 3 0.6664) (4804s)
[snr joint] step 140/200 train 3.4272 val 5.8337 (best 0.6664, Alg. 3 0.6664) (5609s)
[snr joint] step 160/200 train 6.5549 val 5.8162 (best 0.6664, Alg. 3 0.6664) (6429s)
[snr joint] step 180/200 train 6.7999 val 4.8425 (best 0.6664, Alg. 3 0.6664) (7252s)
```

## Result files
```
Oct 28 16:30 results/baselines_paper.png
Oct 28 16:30 results/baselines_paper.json
```
