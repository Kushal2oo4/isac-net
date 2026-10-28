"""Simulation parameters (Table III of Jiang et al., IEEE TCOM 2024)."""
from dataclasses import dataclass, field

C = 299_792_458.0  # speed of light [m/s]


@dataclass
class SimConfig:
    fc: float = 4e9            # carrier frequency [Hz]
    df: float = 120e3          # subcarrier spacing [Hz]
    M: int = 256               # OFDM symbols per frame
    N: int = 1024              # subcarriers
    MI: int = 2560             # DFT points (Doppler axis), 10x zero padding
    NI: int = 10240            # IDFT points (range axis), 10x zero padding
    Tc: float = 2.08e-6        # cyclic prefix [s]
    Nt: int = 8                # transmit antennas
    Nr: int = 8                # receive antennas
    rcs: float = 1.0           # radar cross section [m^2]
    pilot_period: int = 14     # one pilot symbol every 14 (w_p = 1/14)
    weibull_shape: float = 2.0 # small-scale fading f_e ~ Weibull(k); k=2 is Rayleigh-like
    path_loss: str = "physical"  # "physical" (eq. after (8)) or "equal" (all paths same power)
    seed: int = 0
    max_range: float = 200.0   # search window for sensing [m]; prior on where targets are
    max_speed: float = 50.0    # search window |v| [m/s]
    snr_def: str = "antenna"   # "antenna": SNR per receive antenna; "combined": after combining the Nr antennas
    ls_interp: str = "linear"  # LS pilot channel over time: "linear" between pilots, or "first" pilot held

    # Fixed test scenario of Fig. 9 / Fig. 10
    ranges: tuple = (10.0, 50.0, 100.0)    # path length r_l = r1 + r2 [m]
    velocities: tuple = (5.0, 10.0, 15.0)  # [m/s], f_d = v * fc / c (eq. 32)

    @property
    def Tp(self) -> float:      # useful symbol duration [s]
        return 1.0 / self.df

    @property
    def T(self) -> float:       # whole OFDM symbol period [s]
        return self.Tp + self.Tc

    @property
    def B(self) -> float:       # bandwidth [Hz]
        return self.N * self.df

    @property
    def lam(self) -> float:
        return C / self.fc

    @property
    def pilot_idx(self):
        return list(range(0, self.M, self.pilot_period))

    @property
    def range_res(self) -> float:
        """Bin width of r in eq. (31) without zero padding: c / (N df)."""
        return C / (self.N * self.df)

    @property
    def vel_res(self) -> float:
        """Bin width of v in eq. (30) without zero padding: c / (T M fc)."""
        return C / (self.T * self.M * self.fc)


def small_config(**kw) -> SimConfig:
    """Reduced grid for fast debugging (same physics, fewer resources)."""
    base = dict(M=256, N=256, MI=2560, NI=2560, Nt=4, Nr=4)
    base.update(kw)
    return SimConfig(**base)


def add_cfg_args(p):
    """Command-line options shared by the scripts that build a SimConfig."""
    p.add_argument("--snr-def", choices=["antenna", "combined"], default="antenna",
                   help="SNR per receive antenna, or after combining the Nr antennas (closer to the paper's Fig. 9)")
    p.add_argument("--ls", choices=["linear", "first"], default="linear",
                   help="LS pilot channel: interpolated between pilots, or the first pilot held for the frame")
    p.add_argument("--no-window", action="store_true", help="search all ranges and velocities, as the paper does")


def apply_cfg_args(cfg, args):
    cfg.snr_def = args.snr_def
    cfg.ls_interp = args.ls
    if args.no_window:
        cfg.max_range = cfg.max_speed = float("inf")
    return cfg
