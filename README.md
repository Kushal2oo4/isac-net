# ISAC-NET run status

Updated **2026-10-25 14:49 UTC** by the cloud machine, every 10 minutes.
If this time stops moving, the cloud machine has stopped.

**Cloud runs: finished or stopped.**

## Plan (cloud, 4 CPU cores)
1. ISAC-NET on the converging Alg. 3 (4 D-AMP updates per layer): train 150 steps per SNR (0–25 dB), then evaluate 100 trials per SNR.
2. The same for the literal Alg. 3 (1 update per layer).

## Stage log
### Stages
```
== train inner4 Sun Oct 25 14:36:33 UTC 2026
```

## Live output
Training prints a line every 15 steps per SNR: `train` = training loss, `val` = loss on fixed held-out frames, `Alg. 3` = held-out loss of the hand-set values (lower is better).

### 1 · train (converging Alg. 3)
_not started yet_

### 1 · evaluate (converging Alg. 3)
_not started yet_

### 2 · train (literal Alg. 3)
_not started yet_

### 2 · evaluate (literal Alg. 3)
_not started yet_

## Figures
_appear here when each evaluation finishes_

The Mac run writes to `~/isac-net/run_gpu.log` on your Mac: `tail -f ~/isac-net/run_gpu.log`.
