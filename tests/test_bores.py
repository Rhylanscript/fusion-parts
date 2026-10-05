import math

import pytest

from FusionParts.core.shapes.bores import (
    BORES, BoreChoice, bore_outer_radius, bore_reach, bore_segments, ears_fit,
)
from FusionParts.core.shapes.units import mm

CLEARANCE = mm(0.1)


def _gaps(segments):
    """Largest distance between the end of one piece and the start of the next."""
    return max(
        math.dist(segment[-1], segments[(index + 1) % len(segments)][1])
        for index, segment in enumerate(segments)
    )


def _points(segments):
    return [point for segment in segments for point in segment[1:]]


@pytest.mark.parametrize("bore", BORES, ids=lambda bore: bore.name)
def test_plain_bore_is_closed_and_has_no_ears(bore):
    choice = BoreChoice(bore, CLEARANCE)
    segments = bore_segments(choice)
    assert len(segments) == 12
    assert _gaps(segments) < 1e-12
    assert bore_reach(choice) == bore_outer_radius(bore, CLEARANCE)


@pytest.mark.parametrize("bore", BORES, ids=lambda bore: bore.name)
@pytest.mark.parametrize("diameter", [0.2, 0.5, 1.0, 2.0])
def test_eared_bore_is_closed_and_reaches_the_ear_tips(bore, diameter):
    choice = BoreChoice(bore, CLEARANCE, ear_radius=mm(diameter / 2))
    segments = bore_segments(choice)
    assert len(segments) == 24
    assert _gaps(segments) < 1e-12

    furthest = max(math.hypot(x, y) for x, y in _points(segments))
    assert math.isclose(furthest, bore_reach(choice))


def test_ears_that_are_too_big_are_rejected():
    choice = BoreChoice(BORES[0], CLEARANCE, ear_radius=mm(2.0))
    assert not ears_fit(choice)
    with pytest.raises(ValueError):
        bore_segments(choice)
