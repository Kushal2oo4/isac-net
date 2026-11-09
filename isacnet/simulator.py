"""OFDM frame generation and received-signal simulation."""
from dataclasses import dataclass
import numpy as np

from .channel import Channel, effective_channel, random_channel, random_clutter
from .config import SimConfig
from .modulation import qpsk_pilots, random_symbols


@dataclass
class Frame:
    X: np.ndarray          # [M, N] transmitted symbols (pilots + data)
    idx: np.ndarray        # [M, N] 16-QAM indices (-1 on pilot symbols)
    data_mask: np.ndarray  # [M] True on data symbols
    Y: np.ndarray          # [Nr, M, N] received signal
    H: np.ndarray          # [Nr, M, N] true effective channel incl. clutter (normalised)
    channel: Channel       # targets only, gains normalised to the received SNR
    noise_var: float
    clutter: Channel = None  # clutter scatterers (normalised), None without clutter


def pilot_rows(cfg: SimConfig):
    return qpsk_pilots((len(cfg.pilot_idx), cfg.N))


def make_frame(cfg: SimConfig, snr_db: float, rng, channel: Channel = None, clutter="cfg") -> Frame:
    """clutter: "cfg" draws cfg.n_clutter scatterers (none when it is 0, so frames
    without clutter are bit-identical to before); a Channel uses those; None means none."""
    if channel is None:
        channel = random_channel(cfg, rng)
    data_mask = np.ones(cfg.M, dtype=bool)
    data_mask[cfg.pilot_idx] = False

    idx, X = random_symbols(rng, (cfg.M, cfg.N))
    X[~data_mask] = pilot_rows(cfg)
    idx[~data_mask] = -1

    H = effective_channel(cfg, channel.gains, channel.ranges, channel.velocities)
    if isinstance(clutter, str):
        clutter = random_clutter(cfg, rng)
    if clutter is not None:
        H += effective_channel(cfg, clutter.gains, clutter.ranges, clutter.velocities)
    # The paper's SNR is that of the received signal: normalise E|H x|^2 = 1.
    # With clutter this counts target + clutter power, as a receiver would see it.
    scale = 1.0 / np.sqrt(np.mean(np.abs(H) ** 2))
    H *= scale
    channel = Channel(channel.gains * scale, channel.ranges, channel.velocities,
                      channel.aod, channel.aoa)
    if clutter is not None:
        clutter = Channel(clutter.gains * scale, clutter.ranges, clutter.velocities, clutter.aod, clutter.aoa)

    noise_var = 10.0 ** (-snr_db / 10.0)
    if cfg.snr_def == "combined":  # SNR after combining the Nr antennas: Nr times more noise per antenna
        noise_var *= cfg.Nr
    Z = np.sqrt(noise_var / 2) * (rng.standard_normal(H.shape) + 1j * rng.standard_normal(H.shape))
    Y = H * X[None] + Z
    return Frame(X, idx, data_mask, Y, H, channel, noise_var, clutter)
