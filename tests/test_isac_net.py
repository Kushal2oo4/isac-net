import numpy as np
import pytest

torch = pytest.importorskip("torch")

from isacnet import small_config  # noqa: E402
from isacnet.isac_net import ISACNet, isac_loss  # noqa: E402
from isacnet.metrics import ber_ser, nmse  # noqa: E402
from isacnet.modulation import hard_decision  # noqa: E402
from isacnet.simulator import make_frame  # noqa: E402


def test_alg3_high_snr_recovers_symbols_and_targets():
    cfg = small_config(path_loss="equal")
    fr = make_frame(cfg, 25.0, np.random.default_rng(0))
    with torch.no_grad():
        out = ISACNet(cfg, n_layers=3)(fr)
    idx = np.full(fr.idx.shape, -1)
    idx[fr.data_mask] = hard_decision(out["x"].numpy())
    assert ber_ser(idx, fr.idx, fr.data_mask)[0] < 1e-3
    nr, nv = nmse(out["r"].numpy(), out["v"].numpy(), cfg.ranges, cfg.velocities)
    assert nr < 1e-2 and nv < 5e-2


def test_gradients_reach_hyperparameters():
    cfg = small_config(path_loss="equal")
    fr = make_frame(cfg, 10.0, np.random.default_rng(1))
    net = ISACNet(cfg, n_layers=2, tau_db=20.0)  # wide gate so eta3 gets a gradient
    loss, _ = isac_loss(net(fr), fr, cfg)
    loss.backward()
    g = net.eta.grad.abs().sum(0)
    assert torch.all(g[[0, 1, 2, 4]] > 0)


def test_torch_sensor_matches_numpy():
    from isacnet.sensing import RangeDopplerSensor, division_matrix
    from isacnet.torch_ops import TorchSensor

    cfg = small_config(path_loss="equal")
    fr = make_frame(cfg, 15.0, np.random.default_rng(6))
    rows = np.arange(cfg.M)
    S = division_matrix(fr.Y, fr.X, rows)
    ref = RangeDopplerSensor(cfg, rows).clean(S, 3, threshold=0.0)
    got = TorchSensor(cfg, rows, torch.device("cpu")).clean(torch.as_tensor(S, dtype=torch.complex64), 3)
    order = np.argsort(ref.ranges)
    gorder = np.argsort(got.ranges)
    assert np.allclose(ref.ranges[order], got.ranges[gorder], atol=1e-3)
    assert np.allclose(ref.velocities[order], got.velocities[gorder], atol=1e-3)
