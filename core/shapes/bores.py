import math
from dataclasses import dataclass

from .geometry import arc_through, polar
from .units import mm

MIN_FLAT_MM = 0.1

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

@dataclass(frozen=True)
class BoreChoice:
    """A bore the user picked, plus the options set in the dialog.

    `clearance` and `ear_radius` are in Fusion units (cm). An `ear_radius`
    of 0 means no mouse ears.
    """

    bore: Bore
    clearance: float
    ear_radius: float = 0.0

    @property
    def has_ears(self):
        return self.ear_radius > 0


@dataclass(frozen=True)
class _Ear:
    """The points of one mouse ear, listed in counter-clockwise order.

    Each ear is a small circle centred on a hexagon corner. A fillet joins
    the circle to the flat on each side so the outline has no sharp corners.
    All points are (x, y) in Fusion units.
    """

    flat_end: tuple       # where the flat before the corner stops
    first_centre: tuple   # centre of the fillet beside that flat
    first_touch: tuple    # where that fillet meets the ear circle
    tip: tuple            # the outermost point of the ear circle
    second_touch: tuple   # where the other fillet meets the ear circle
    second_centre: tuple  # centre of the fillet beside the next flat
    flat_start: tuple     # where the flat after the corner begins


def find_bore(name):
    for bore in BORES:
        if bore.name == name:
            return bore
    raise ValueError("Unknown bore: " + name)


def bore_outer_radius(bore, clearance):
    """Radius of the bore's round part, with clearance added (Fusion units)."""
    return mm(bore.round_diameter / 2) + clearance


def _flat_distance(choice):
    """Distance from the centre to each flat, with clearance added."""
    return mm(choice.bore.across_flats / 2) + choice.clearance


def _corner_radius(choice):
    """Distance from the centre to a sharp hexagon corner.

    The bore's round part trims the corners slightly, so the plain hole stops
    just short of this. The mouse ears are centred on the sharp corner.
    """
    return _flat_distance(choice) / math.cos(math.pi / 6)


def _fillet_radius(ear_radius):
    """The fillets are the same size as the ear holes."""
    return ear_radius


def _fillet_reach(ear_radius):
    """How far from the corner a fillet touches the flat, measured along it.

    The fillet circle touches the flat, so its centre is one fillet radius
    away from the flat. It also touches the ear circle from outside, so its
    centre is (ear radius + fillet radius) from the ear centre. Pythagoras
    gives the distance along the flat.
    """
    fillet = _fillet_radius(ear_radius)
    return math.sqrt((ear_radius + fillet) ** 2 - fillet**2)


def ears_fit(choice):
    """True if the ears leave some straight flat between neighbouring ears."""
    side = 2 * _flat_distance(choice) / math.sqrt(3)
    used = 2 * _fillet_reach(choice.ear_radius)
    return side - used >= mm(MIN_FLAT_MM)


def bore_reach(choice):
    """Distance from the centre to the furthest point of the bore (Fusion units)."""
    if choice.has_ears:
        return _corner_radius(choice) + choice.ear_radius
    return bore_outer_radius(choice.bore, choice.clearance)


def _plain_segments(choice):
    """The bore outline with no ears: six flats and six rounded corners."""
    radius = bore_outer_radius(choice.bore, choice.clearance)
    flat_distance = _flat_distance(choice)

    half_angle = math.acos(flat_distance / radius)
    if half_angle > math.pi / 6:
        raise ValueError(
            "Bore '%s' doesn't make a hexagon trimmed by a circle." % choice.bore.name
        )

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


def _move(point, distance, angle):
    """The point `distance` away from `point`, heading in direction `angle`."""
    dx, dy = polar(distance, angle)
    return (point[0] + dx, point[1] + dy)


def _fillet_side(corner, ear_radius, along, out):
    """Work out the fillet between one flat and the ear circle.

    corner: the ear's centre (a hexagon corner).
    along:  direction from the corner back along the flat.
    out:    direction from the flat into the material (away from the hole).
    Returns (where the fillet leaves the flat, fillet centre, where it meets
    the ear circle).
    """
    fillet = _fillet_radius(ear_radius)
    flat_point = _move(corner, _fillet_reach(ear_radius), along)
    centre = _move(flat_point, fillet, out)

    # The two circles touch on the straight line between their centres.
    share = ear_radius / (ear_radius + fillet)
    touch = (
        corner[0] + (centre[0] - corner[0]) * share,
        corner[1] + (centre[1] - corner[1]) * share,
    )
    return flat_point, centre, touch


def _solve_ear(choice, corner):
    """Work out the ear on the corner that follows flat number `corner`."""
    flat_angle = corner * math.pi / 3
    corner_angle = flat_angle + math.pi / 6
    point = polar(_corner_radius(choice), corner_angle)

    flat_end, first_centre, first_touch = _fillet_side(
        point, choice.ear_radius, flat_angle - math.pi / 2, flat_angle
    )
    flat_start, second_centre, second_touch = _fillet_side(
        point, choice.ear_radius, flat_angle + 5 * math.pi / 6, flat_angle + math.pi / 3
    )
    return _Ear(
        flat_end=flat_end,
        first_centre=first_centre,
        first_touch=first_touch,
        tip=_move(point, choice.ear_radius, corner_angle),
        second_touch=second_touch,
        second_centre=second_centre,
        flat_start=flat_start,
    )


def _eared_segments(choice):
    """The bore outline with a mouse ear (and two fillets) on every corner."""
    if not ears_fit(choice):
        raise ValueError("The mouse ears are too big for this bore.")

    # Solve every ear once, so neighbouring pieces share exact end points.
    ears = [_solve_ear(choice, corner) for corner in range(6)]

    segments = []
    for flat in range(6):
        ear = ears[flat]
        previous = ears[flat - 1]
        segments.append(("line", previous.flat_start, ear.flat_end))
        segments.append(arc_through(ear.first_centre, ear.flat_end, ear.first_touch))
        segments.append(("arc", ear.first_touch, ear.tip, ear.second_touch))
        segments.append(arc_through(ear.second_centre, ear.second_touch, ear.flat_start))
    return segments


def bore_segments(choice):
    """Outline pieces for the bore, in the same format as outline_segments().

    `choice` is a BoreChoice. Its clearance (Fusion units) is added to both
    the round radius and the distance from the centre to each flat, so the
    hole is slightly bigger than the shaft all the way round. With mouse ears
    switched on, every corner gets a small round relief with filleted edges.
    """
    if choice.has_ears:
        return _eared_segments(choice)
    return _plain_segments(choice)
