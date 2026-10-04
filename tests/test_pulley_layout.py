from FusionParts.core.units import mm
from FusionParts.generators.pulley_layout import cap_points, label_fit


def test_cap_has_a_cone_corner_only_when_cone_length_is_positive():
    assert len(cap_points(1.0, 1.5, 0.05, 0.0, 0.0, -1)) == 4
    assert len(cap_points(1.0, 1.5, 0.05, 0.075, 0.0, -1)) == 5


def test_bottom_cap_grows_downward_and_top_cap_upward():
    bottom = cap_points(1.0, 1.5, 0.05, 0.075, 1.0, -1)
    top = cap_points(1.0, 1.5, 0.05, 0.075, 1.0, +1)
    assert min(z for _, z in bottom) < 1.0
    assert max(z for _, z in top) > 1.0


def test_label_fits_in_a_big_ring_and_not_in_a_tiny_one():
    assert label_fit(2, mm(4), mm(15), mm(3), True, 0.0) is not None
    assert label_fit(3, mm(4), mm(5), mm(3), True, 0.0) is None
