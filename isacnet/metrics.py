"""BER/SER and range/velocity NMSE (eq. 43)."""
from itertools import permutations
import numpy as np

from .modulation import BITS


def ber_ser(idx_hat, idx_true, data_mask):
    a, b = idx_hat[data_mask], idx_true[data_mask]
    ser = np.mean(a != b)
    ber = np.mean(BITS[a] != BITS[b])
    return float(ber), float(ser)


def match_targets(r_hat, v_hat, r_true, v_true):
    """Assign estimates to true targets minimising the summed NMSE.

    A missing estimate counts as (0, 0), i.e. NMSE 1 for that target.
    """
    L = len(r_true)
    r_hat = list(r_hat) + [0.0] * max(0, L - len(r_hat))
    v_hat = list(v_hat) + [0.0] * max(0, L - len(v_hat))
    best, best_cost = None, np.inf
    for perm in permutations(range(len(r_hat)), L):
        cost = sum(((r_hat[p] - r_true[l]) / r_true[l]) ** 2 + ((v_hat[p] - v_true[l]) / v_true[l]) ** 2
                   for l, p in enumerate(perm))
        if cost < best_cost:
            best, best_cost = perm, cost
    return np.array([r_hat[p] for p in best]), np.array([v_hat[p] for p in best])


def nmse(r_hat, v_hat, r_true, v_true):
    r_true, v_true = np.asarray(r_true, float), np.asarray(v_true, float)
    rm, vm = match_targets(r_hat, v_hat, r_true, v_true)
    return float(np.mean(((rm - r_true) / r_true) ** 2)), float(np.mean(((vm - v_true) / v_true) ** 2))
