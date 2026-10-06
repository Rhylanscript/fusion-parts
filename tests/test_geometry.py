import math

from FusionParts.core.shapes.geometry import (
    are_parallel, in_plane_distance, place_segments,
)


def test_opposite_normals_still_count_as_parallel():
    assert are_parallel((0, 0, 1), (0, 0, -1))
    assert not are_parallel((0, 0, 1), (0, 1, 0))


def test_height_along_the_normal_is_ignored():
    assert math.isclose(in_plane_distance((0, 0, 0), (3, 4, 10), (0, 0, 1)), 5.0)


def test_place_segments_rotates_then_moves():
    placed = place_segments([("line", (1, 0), (2, 0))], (10, 0), math.pi / 2)
    _, start, end = placed[0]
    assert math.isclose(start[0], 10, abs_tol=1e-12)
    assert math.isclose(start[1], 1)
    assert math.isclose(end[1], 2)
