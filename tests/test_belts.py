import math

from FusionParts.core.belts import (
    BELTS, find_belt, outside_diameter, pitch_diameter, root_radius,
)
from FusionParts.core.units import mm


def test_pitch_diameter_is_teeth_times_pitch_over_pi():
    belt = find_belt("HTD 3M")
    assert math.isclose(pitch_diameter(belt, 24), mm(24 * 3 / math.pi))


def test_outside_is_smaller_than_pitch_and_root_is_smaller_still():
    for belt in BELTS:
        for teeth in (10, 24, 100):
            tip = outside_diameter(belt, teeth) / 2
            assert outside_diameter(belt, teeth) < pitch_diameter(belt, teeth)
            assert root_radius(belt, teeth) < tip


def test_every_belt_has_positive_sizes():
    for belt in BELTS:
        assert belt.pitch > 0
        assert belt.thickness > 0
