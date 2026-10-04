import math

import pytest

from FusionParts.core.belts import find_belt, outside_diameter
from FusionParts.core.units import mm
from FusionParts.generators.belt_path import (
    belt_loops, belt_teeth, loop_segments, pitch_length,
)

BELT = find_belt("HTD 3M")
DISTANCE = mm(225)


def _is_closed(segments):
    for index, segment in enumerate(segments):
        following = segments[(index + 1) % len(segments)]
        if not math.dist(segment[-1], following[1]) < 1e-12:
            return False
    return True

def test_demo_belt_is_180_teeth():
    """24T + 36T HTD 3M, 225 mm apart, is the 540 mm belt from the demo STEP."""
    length = pitch_length(BELT, 24, 36, DISTANCE)
    assert math.isclose(length, mm(540.146), abs_tol=mm(0.01))
    assert round(belt_teeth(BELT, 24, 36, DISTANCE)) == 180

def test_loops_are_closed():
    outer, inner = belt_loops(BELT, 24, 36, DISTANCE)
    assert _is_closed(outer)
    assert _is_closed(inner)

def test_inner_loop_touches_tooth_tips_and_outer_is_one_thickness_further():
    outer, inner = belt_loops(BELT, 24, 36, DISTANCE)
    tip = outside_diameter(BELT, 24) / 2
    assert math.isclose(inner[3][2][0], -tip)
    assert math.isclose(outer[3][2][0], -(tip + mm(BELT.thickness)))

def test_equal_pulleys_give_level_straight_sections():
    _, inner = belt_loops(BELT, 24, 24, DISTANCE)
    bottom, top = inner[0], inner[2]
    assert math.isclose(bottom[1][1], bottom[2][1])
    assert math.isclose(top[1][1], top[2][1])

def test_pulleys_too_close_are_rejected():
    with pytest.raises(ValueError):
        belt_loops(BELT, 24, 36, mm(20))
    with pytest.raises(ValueError):
        loop_segments(1.0, 3.0, 1.5)
    with pytest.raises(ValueError):
        pitch_length(BELT, 24, 36, mm(5))
