import math
from dataclasses import dataclass

from ..core.belts import outside_diameter, root_radius
from ..core.geometry import polar
from ..core.units import mm

_TINY = 1e-6

@dataclass
class _Half:
    """Half a tooth gap, worked out for a tooth lying along angle 0.

    All points are (x, y) in Fusion units. The other half is a mirror image.
    """

    tip: tuple            # where the flat tooth tip ends
    fillet_centre: tuple
    join: tuple           # where the fillet meets the flank
    flank_centre: tuple
    root: tuple           # where the flank meets the gap floor
    root_angle: float     # angle of `root` from the tooth centre line
    has_floor: bool       # True when there is a floor arc between the two roots

def _acos(value):
    """acos that tolerates tiny rounding errors just outside -1..1."""
    return math.acos(max(-1.0, min(1.0, value)))

def _solve_half(belt, teeth):
    """Work out the points of one half-gap using circle-tangent geometry."""
    groove = belt.groove
    gap_angle = math.pi / teeth  # angle from a tooth centre to the middle of the next gap
    tip_radius = outside_diameter(belt, teeth) / 2
    floor_radius = root_radius(belt, teeth)

    flank_radius = mm(groove.flank_radius)
    fillet_radius = mm(groove.fillet_radius)
    centre_radius = tip_radius - mm(groove.flank_centre_depth)
    flank_angle = gap_angle + math.asin(mm(groove.flank_centre_offset) / centre_radius)
    flank_centre = polar(centre_radius, flank_angle)

    # The fillet circle touches the tip circle from inside, and touches the
    # flank circle from outside. That fixes where its centre is.
    fillet_pos = tip_radius - fillet_radius
    touch_distance = flank_radius + fillet_radius
    spread = _acos(
        (fillet_pos**2 + centre_radius**2 - touch_distance**2)
        / (2 * fillet_pos * centre_radius)
    )
    fillet_angle = flank_angle - spread
    fillet_centre = polar(fillet_pos, fillet_angle)

    # The touching point lies on the straight line between the two centres.
    share = fillet_radius / touch_distance
    join = (
        fillet_centre[0] + (flank_centre[0] - fillet_centre[0]) * share,
        fillet_centre[1] + (flank_centre[1] - fillet_centre[1]) * share,
    )

    # Where the flank circle crosses the gap floor circle.
    root_spread = _acos(
        (floor_radius**2 + centre_radius**2 - flank_radius**2)
        / (2 * floor_radius * centre_radius)
    )
    root_angle = flank_angle - root_spread
    root = polar(floor_radius, root_angle)

    join_angle = math.atan2(join[1], join[0])
    if not 0 < fillet_angle < join_angle < root_angle <= gap_angle + _TINY:
        raise ValueError(
            "The %s tooth shape doesn't fit on %d teeth. Use more teeth."
            % (belt.name, teeth)
        )
    return _Half(
        tip=polar(tip_radius, fillet_angle),
        fillet_centre=fillet_centre,
        join=join,
        flank_centre=flank_centre,
        root=root,
        root_angle=root_angle,
        has_floor=gap_angle - root_angle > _TINY,
    )

def _rotate(point, angle):
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    return (point[0] * cos_a - point[1] * sin_a, point[0] * sin_a + point[1] * cos_a)

def _mirror(point):
    return (point[0], -point[1])

def _arc_through(centre, start, end):
    """Return ("arc", start, middle, end) for the short arc around `centre`."""
    radius = math.hypot(start[0] - centre[0], start[1] - centre[1])
    first = math.atan2(start[1] - centre[1], start[0] - centre[0])
    last = math.atan2(end[1] - centre[1], end[0] - centre[0])
    difference = (last - first + math.pi) % (2 * math.pi) - math.pi
    middle = (
        centre[0] + radius * math.cos(first + difference / 2),
        centre[1] + radius * math.sin(first + difference / 2),
    )
    return ("arc", start, middle, end)

def _place(half, angle, mirrored):
    """Copy of the half-gap points, optionally mirrored, rotated to `angle`."""
    def move(point):
        if mirrored:
            point = _mirror(point)
        return _rotate(point, angle)

    return _Half(
        tip=move(half.tip),
        fillet_centre=move(half.fillet_centre),
        join=move(half.join),
        flank_centre=move(half.flank_centre),
        root=move(half.root),
        root_angle=half.root_angle,
        has_floor=half.has_floor,
    )

def outline_segments(belt, teeth):
    """Every piece of the pulley's toothed outline, in drawing order.

    Same format as the gear: ("arc", start, middle, end) tuples with (x, y)
    points in Fusion units. Raises ValueError if the tooth shape cannot fit
    this many teeth.
    """
    half = _solve_half(belt, teeth)
    step = 2 * math.pi / teeth
    tip_radius = outside_diameter(belt, teeth) / 2
    floor_radius = root_radius(belt, teeth)

    # Place both halves of every gap once, so neighbouring pieces share the
    # exact same end points.
    right_sides = [_place(half, index * step, mirrored=False) for index in range(teeth)]
    left_sides = [_place(half, index * step, mirrored=True) for index in range(teeth)]

    segments = []
    for index in range(teeth):
        right = right_sides[index]
        left_next = left_sides[(index + 1) % teeth]
        tooth_left = left_sides[index]

        segments.append(("arc", tooth_left.tip, polar(tip_radius, index * step), right.tip))
        segments.append(_arc_through(right.fillet_centre, right.tip, right.join))
        segments.append(_arc_through(right.flank_centre, right.join, right.root))
        if right.has_floor:
            floor_middle = polar(floor_radius, index * step + step / 2)
            segments.append(("arc", right.root, floor_middle, left_next.root))
            segments.append(_arc_through(left_next.flank_centre, left_next.root, left_next.join))
        else:
            segments.append(_arc_through(left_next.flank_centre, right.root, left_next.join))
        segments.append(_arc_through(left_next.fillet_centre, left_next.join, left_next.tip))
    return segments
