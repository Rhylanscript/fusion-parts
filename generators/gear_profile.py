import math
from dataclasses import dataclass

# How many points we sample along each tooth flank
# note that more points = smoother curve
FLANK_POINTS = 8

@dataclass
class GearSpec:
    """The numbers that define a spur gear. Lengths are in Fusion units (cm)."""

    teeth: int
    module: float
    pressure_angle: float # rad

    @property
    def pitch_radius(self):
        return self.module * self.teeth / 2

    @property
    def base_radius(self):
        return self.pitch_radius * math.cos(self.pressure_angle)

    @property
    def tip_radius(self):
        return self.pitch_radius + self.module  # addendum = 1 module

    @property
    def root_radius(self):
        return self.pitch_radius - 1.25 * self.module  # dedendum = 1.25 modules


def _involute_function(angle):
    return math.tan(angle) - angle

def _polar(radius, angle):
    """Convert (distance from centre, angle) to an (x, y) point."""
    return (radius * math.cos(angle), radius * math.sin(angle))

def _right_flank_angle(spec, radius):
    """Angle of the tooths right flank at `radius`, measured from the tooth's centre line.

    It is negative (the right flank sits clockwise of the centre line) and
    shrinks toward zero as the tooth narrows toward the tip.
    """
    ratio = min(1.0, spec.base_radius / radius)
    roll_angle = math.acos(ratio)
    return (
        _involute_function(roll_angle)
        - _involute_function(spec.pressure_angle)
        - math.pi / (2 * spec.teeth)
    )


def _tooth_segments(spec, index):
    """Outline pieces for one tooth, going counter-clockwise, root to root."""
    offset = index * 2 * math.pi / spec.teeth
    root = spec.root_radius
    start_radius = max(root, spec.base_radius)
    root_angle = _right_flank_angle(spec, start_radius)

    radii = [
        start_radius + (spec.tip_radius - start_radius) * step / (FLANK_POINTS - 1)
        for step in range(FLANK_POINTS)
    ]
    right_flank = [_polar(r, offset + _right_flank_angle(spec, r)) for r in radii]
    left_flank = [_polar(r, offset - _right_flank_angle(spec, r)) for r in reversed(radii)]
    tip_middle = _polar(spec.tip_radius, offset)

    segments = []
    needs_radial_line = root < spec.base_radius
    if needs_radial_line:
        segments.append(("line", _polar(root, offset + root_angle), right_flank[0]))
    segments.append(("spline", right_flank))
    segments.append(("arc", right_flank[-1], tip_middle, left_flank[0]))
    segments.append(("spline", left_flank))
    if needs_radial_line:
        segments.append(("line", left_flank[-1], _polar(root, offset - root_angle)))
    return segments


def outline_segments(spec):
    """Every piece of the gear outline, in drawing order, as plain tuples.

    Each piece is one of:
    - ("line", start, end)
    - ("arc", start, middle, end)
    - ("spline", [point, point, ...])
    where a point is an (x, y) tuple.
    """
    step = 2 * math.pi / spec.teeth
    start_radius = max(spec.root_radius, spec.base_radius)
    root_angle = _right_flank_angle(spec, start_radius)

    segments = []
    for index in range(spec.teeth):
        segments.extend(_tooth_segments(spec, index))

        offset = index * step
        next_offset = ((index + 1) % spec.teeth) * step
        gap_start = _polar(spec.root_radius, offset - root_angle)
        gap_middle = _polar(spec.root_radius, offset + step / 2)
        gap_end = _polar(spec.root_radius, next_offset + root_angle)
        segments.append(("arc", gap_start, gap_middle, gap_end))
    return segments
