import math

import pytest

from FusionParts.core.shapes.belts import BELTS
from FusionParts.generators.gear.gear_profile import GearSpec
from FusionParts.generators.gear.gear_profile import outline_segments as gear_outline
from FusionParts.generators.pulley.pulley_profile import outline_segments as pulley_outline


def _start(segment):
    return segment[1][0] if segment[0] == "spline" else segment[1]


def _end(segment):
    return segment[1][-1] if segment[0] == "spline" else segment[-1]


def _gaps(segments):
    """Largest distance between the end of one piece and the start of the next."""
    return max(
        math.dist(_end(segment), _start(segments[(index + 1) % len(segments)]))
        for index, segment in enumerate(segments)
    )


@pytest.mark.parametrize("teeth", [20, 60, 100])
def test_gear_outline_is_closed(teeth):
    spec = GearSpec(teeth=teeth, module=0.1, pressure_angle=math.radians(20))
    assert _gaps(gear_outline(spec)) < 1e-9

@pytest.mark.parametrize("belt", BELTS, ids=lambda belt: belt.name)
def test_pulley_outline_is_closed_for_every_allowed_tooth_count(belt):
    for teeth in range(10, 201):
        assert _gaps(pulley_outline(belt, teeth)) < 1e-9, teeth
