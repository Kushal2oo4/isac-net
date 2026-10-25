"""Gray-coded 16-QAM (unit average energy) and QPSK pilots."""
import numpy as np

# Gray map for one axis: 2 bits -> level
_LEVELS = np.array([-3.0, -1.0, 3.0, 1.0])  # index b0b1: 00->-3, 01->-1, 10->+3, 11->+1
_NORM = np.sqrt(10.0)
CONSTELLATION = np.array(
    [(_LEVELS[i >> 2] + 1j * _LEVELS[i & 3]) / _NORM for i in range(16)]
)  # symbol index i = b0 b1 b2 b3 (b0b1 -> I, b2b3 -> Q)
BITS = np.array([[(i >> (3 - k)) & 1 for k in range(4)] for i in range(16)], dtype=np.int8)


def random_symbols(rng, shape):
    """Return (symbol indices, complex symbols)."""
    idx = rng.integers(0, 16, size=shape)
    return idx, CONSTELLATION[idx]


def hard_decision(x):
    """Nearest-constellation-point index for each complex sample."""
    # Separable decision per axis is exact for square QAM.
    def axis(v):
        lv = np.clip(np.round((v * _NORM - 1.0) / 2.0) * 2.0 + 1.0, -3, 3)  # nearest odd level
        return np.select([lv == -3, lv == -1, lv == 3], [0, 1, 2], default=3)
    return (axis(x.real) << 2) | axis(x.imag)


def bit_errors(idx_hat, idx_true):
    return int(np.sum(BITS[idx_hat] != BITS[idx_true]))


def qpsk_pilots(shape, seed=12345):
    """Fixed unit-modulus pilot sequence (same in every frame)."""
    rng = np.random.default_rng(seed)
    ph = rng.integers(0, 4, size=shape)
    return np.exp(1j * (np.pi / 4 + np.pi / 2 * ph))
