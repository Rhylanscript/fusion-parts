import math
from dataclasses import dataclass

from .geometry import polar
from .units import mm

@dataclass(frozen=True)
class Bore:
    """A shaft hole: a round profile trimmed by a hexagon (like REX).
    Sizes are in millimetres.
    """

    name: str
    round_diameter: float
    across_flats: float


BORES = [
    Bore("goBILDA 8mm REX", round_diameter=8.0, across_flats=7.0),
    Bore("goBILDA 12mm REX", round_diameter=12.0, across_flats=11.0),
]


def find_bore(name):
    for bore in BORES:
        if bore.name == name:
            return bore
    raise ValueError("Unknown bore: " + name)


def bore_outer_radius(bore, clearance):
    """Radius of the bore's round part, with clearance added (Fusion units)."""
    return mm(bore.round_diameter / 2) + clearance


def bore_segments(bore, clearance):
    """Outline pieces for the bore, in the same format as outline_segments().

    `clearance` (Fusion units) is added to both the round radius and the
    distance from the centre to each flat, so the hole is slightly bigger
    than the shaft all the way round.
    """
    radius = bore_outer_radius(bore, clearance)
    flat_distance = mm(bore.across_flats / 2) + clearance

    half_angle = math.acos(flat_distance / radius)
    if half_angle > math.pi / 6:
        raise ValueError("Bore '%s' doesn't make a hexagon trimmed by a circle." % bore.name)

    starts = []
    ends = []
    for flat in range(6):
        direction = flat * math.pi / 3
        starts.append(polar(radius, direction - half_angle))
        ends.append(polar(radius, direction + half_angle))

    segments = []
    for flat in range(6):
        segments.append(("line", starts[flat], ends[flat]))
        corner_middle = polar(radius, flat * math.pi / 3 + math.pi / 6)
        segments.append(("arc", ends[flat], corner_middle, starts[(flat + 1) % 6]))
    return segments
