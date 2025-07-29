import torch
import pytest
from voidwalker import Voidwalker, run_voidwalker


def make_points(n=50, d=2, seed=42):
    torch.manual_seed(seed)
    return torch.rand(n, d)


def test_initialisation_and_run():
    points = make_points()
    bounds = torch.tensor([[0.0, 1.0], [0.0, 1.0]])
    vw = Voidwalker(points, n_samples=1000, n_voids=5, bounds=bounds, margin=1e-3,
                    outer_ring_width=0.05, alpha=0.05)
    voids, radii = vw.run()

    assert voids.shape == (5, 3)
    assert radii.shape == (5,)
    assert torch.all(voids[:, 2] > 0)
    assert torch.all(voids[:, 2] == radii)


def test_functional_interface():
    points = make_points()
    bounds = torch.tensor([[0.0, 1.0], [0.0, 1.0]])
    voids, radii, frames = run_voidwalker(points, n_samples=1000, n_voids=5, bounds=bounds,
                                          margin=1e-3, outer_ring_width=0.05, alpha=0.05,
                                          record_frames=True)

    assert isinstance(voids, torch.Tensor)
    assert isinstance(radii, torch.Tensor)
    assert isinstance(frames, list)
    assert voids.shape[1] == 3
    assert radii.shape == (5,)
    assert torch.all(voids[:, 2] == radii)


def test_voids_respect_bounds():
    points = make_points()
    bounds = torch.tensor([[0.0, 1.0], [0.0, 1.0]])
    voids, _, _ = run_voidwalker(points, n_samples=1000, n_voids=5, bounds=bounds,
                                 margin=1e-3, outer_ring_width=0.05, alpha=0.05)

    centres = voids[:, :2]
    assert torch.all(centres >= 0.0)
    assert torch.all(centres <= 1.0)


def test_voids_approximately_repel_points():
    points = make_points()
    bounds = torch.tensor([[0.0, 1.0], [0.0, 1.0]])
    voids, radii, _ = run_voidwalker(points, n_samples=1000, n_voids=5, bounds=bounds,
                                     margin=1e-3, outer_ring_width=0.05, alpha=0.05)

    centres = voids[:, :2]
    dists = torch.cdist(centres, points)
    min_dists = dists.min(dim=1).values

    num_violations = (min_dists <= radii + 1e-3).sum().item()
    assert num_violations <= 1


def test_voids_approximately_repel_each_other():
    points = make_points()
    bounds = torch.tensor([[0.0, 1.0], [0.0, 1.0]])
    voids, radii, _ = run_voidwalker(points, n_samples=1000, n_voids=6, bounds=bounds,
                                     margin=1e-3, outer_ring_width=0.05, alpha=0.05)

    centres = voids[:, :2]
    dists = torch.cdist(centres, centres)
    rr_sum = radii.unsqueeze(1) + radii.unsqueeze(0) + 1e-3
    eye = torch.eye(len(centres), dtype=torch.bool)
    close_pairs = (dists < rr_sum) & (~eye)
    too_close = close_pairs.any(dim=1)
    assert too_close.sum().item() <= 1


def test_high_margin_blocks_growth():
    points = make_points()
    bounds = torch.tensor([[0.0, 1.0], [0.0, 1.0]])
    with pytest.raises(RuntimeError, match="Not enough valid initial voids after filtering."):
        run_voidwalker(points, n_samples=1000, n_voids=3, bounds=bounds,
                       margin=0.5, outer_ring_width=0.05, alpha=0.05)


def test_failure_when_no_valid_seeds():
    points = make_points(n=1000)
    bounds = torch.tensor([[0.0, 1.0], [0.0, 1.0]])
    with pytest.raises(RuntimeError, match="Not enough valid initial voids after filtering."):
        run_voidwalker(points, n_samples=1000, n_voids=10, bounds=bounds,
                       margin=0.1, outer_ring_width=0.05, alpha=0.05)


def test_does_not_mutate_input_points():
    points = make_points()
    points_clone = points.clone()
    bounds = torch.tensor([[0.0, 1.0], [0.0, 1.0]])
    _, _, _ = run_voidwalker(points, n_samples=1000, n_voids=5, bounds=bounds,
                             margin=1e-3, outer_ring_width=0.05, alpha=0.05)
    assert torch.equal(points, points_clone)


def test_voids_terminate_by_csr_test():
    points = make_points(n=500)
    bounds = torch.tensor([[0.0, 1.0], [0.0, 1.0]])
    alpha = 0.05
    vw = Voidwalker(points, n_samples=1000, n_voids=5, bounds=bounds, margin=1e-3,
                    outer_ring_width=0.1, alpha=alpha)
    vw.run()
    memberships = vw.get_outer_ring_membership()
    member_counts = torch.tensor([len(m) for m in memberships], dtype=torch.float32)

    radii = vw.voids[:, 2]
    expected_counts = vw.global_density * torch.pi * (
        (radii + vw.outer_ring_width) ** 2 - radii ** 2
    )

    k = member_counts.floor()
    lam = expected_counts.clamp(min=1e-8)
    cdf = torch.special.gammainc(k + 1, lam)
    p_values = 1.0 - cdf

    terminated = (p_values <= alpha)
    assert torch.all(~vw.active[terminated])
