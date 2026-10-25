import numpy as np
import pytest

from isacnet import small_config
from isacnet.baselines import run_baselines
from isacnet.channel import random_channel
from isacnet.detection import improved_damp, ls_channel_estimate, ml_detect
from isacnet.metrics import ber_ser, nmse
from isacnet.modulation import CONSTELLATION, hard_decision
from isacnet.sensing import RangeDopplerSensor, division_matrix, reconstruct_channel
from isacnet.simulator import make_frame


@pytest.fixture
def cfg():
    return small_config(path_loss="equal")


def test_qam_roundtrip_and_unit_energy():
    assert np.allclose(np.mean(np.abs(CONSTELLATION) ** 2), 1.0)
    assert np.array_equal(hard_decision(CONSTELLATION), np.arange(16))
    assert np.array_equal(hard_decision(CONSTELLATION * 1.05 + 0.02j), np.arange(16))


def test_received_snr_normalisation(cfg):
    fr = make_frame(cfg, 10.0, np.random.default_rng(1))
    assert np.isclose(np.mean(np.abs(fr.H) ** 2), 1.0)
    assert np.isclose(fr.noise_var, 0.1)


def test_noiseless_detection(cfg):
    fr = make_frame(cfg, 200.0, np.random.default_rng(2))
    _, idx = ml_detect(fr.Y, fr.H)
    assert ber_ser(idx, fr.idx, fr.data_mask) == (0.0, 0.0)
    H_ls = ls_channel_estimate(cfg, fr.Y, fr.X)
    assert np.linalg.norm(H_ls - fr.H) / np.linalg.norm(fr.H) < 0.05
    _, idx = improved_damp(fr.Y, fr.H, n_iter=30)
    assert ber_ser(idx, fr.idx, fr.data_mask)[0] == 0.0


def test_sensing_single_target_on_paper_grid(cfg):
    rng = np.random.default_rng(3)
    ch = random_channel(cfg, rng, ranges=[42.0], velocities=[7.0])
    fr = make_frame(cfg, 30.0, rng, channel=ch)
    sensor = RangeDopplerSensor(cfg, np.arange(cfg.M))
    res = sensor.clean(division_matrix(fr.Y, fr.X, np.arange(cfg.M)), 1, threshold=0.0)
    assert abs(res.ranges[0] - 42.0) <= sensor.dr_fine
    assert abs(res.velocities[0] - 7.0) <= sensor.dv_fine
    res = sensor.clean(division_matrix(fr.Y, fr.X, np.arange(cfg.M)), 1, threshold=0.0, report="fine")
    assert abs(res.velocities[0] - 7.0) < 0.2 * sensor.dv_fine


def test_reconstruction_with_true_parameters(cfg):
    fr = make_frame(cfg, 200.0, np.random.default_rng(4))
    H_rec, _ = reconstruct_channel(cfg, cfg.ranges, cfg.velocities, fr.Y, fr.X, cfg.pilot_idx)
    assert np.linalg.norm(H_rec - fr.H) / np.linalg.norm(fr.H) < 1e-6


def test_baselines_three_targets_high_snr(cfg):
    fr = make_frame(cfg, 25.0, np.random.default_rng(5))
    out = run_baselines(cfg, fr, 3)
    nr, nv = nmse(out["dft2d_clean"]["r"], out["dft2d_clean"]["v"], cfg.ranges, cfg.velocities)
    assert nr < 1e-2 and nv < 5e-2
    assert ber_ser(out["perfect_csi"]["idx"], fr.idx, fr.data_mask)[0] < 1e-3
