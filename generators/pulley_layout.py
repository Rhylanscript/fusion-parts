import math
from dataclasses import dataclass

from ..core.units import mm

CHAR_WIDTH = 0.7
LABEL_MARGIN_MM = 0.5
MIN_LABEL_HEIGHT_MM = 1.0
LABEL_STEP_MM = 0.25


def cap_points(tip_radius, flange_radius, thickness, cone_length, teeth_edge, outward):
    """Corner points (radius, height) of one end cap of the pulley.

    A cap is a flange plus an optional cone that eases the belt onto the
    teeth. Its half-profile is revolved around the pulley's axis.

    teeth_edge: height of the end face of the toothed section.
    outward:    -1 for the bottom cap (grows downward), +1 for the top cap.
    """
    far_edge = teeth_edge + outward * (cone_length + thickness)
    points = [(0.0, teeth_edge)]
    if cone_length > 0:
        points.append((tip_radius, teeth_edge))
        points.append((flange_radius, teeth_edge + outward * cone_length))
    else:
        points.append((flange_radius, teeth_edge))
    points.append((flange_radius, far_edge))
    points.append((0.0, far_edge))
    return points

@dataclass(frozen=True)
class LabelPlan:
    """Where an engraved label goes. Lengths are Fusion units."""

    height: float
    centre: tuple


def label_fit(label_length, inner_radius, outer_radius, max_height, on_top, offset):
    """Find where, and how big, an engraved label can go.

    The label is straight text, centred above the bore (or below it) in the
    ring between `inner_radius` (0 for no bore) and `outer_radius`. It starts
    in the middle of that ring; `offset` then moves it away from the pulley's
    centre (positive) or toward it (negative). The text shrinks from
    `max_height` until it fits. Returns a LabelPlan, or None if it can't fit.
    """
    margin = mm(LABEL_MARGIN_MM)
    limit = outer_radius - margin
    direction = 1 if on_top else -1
    height = max_height
    while height >= mm(MIN_LABEL_HEIGHT_MM) - 1e-9:
        half_width = label_length * CHAR_WIDTH * height / 2
        half_height = height / 2
        if half_width < limit:
            far = math.sqrt(limit**2 - half_width**2) - half_height
            near = inner_radius + margin + half_height if inner_radius > 0 else -far
            distance = (near + far) / 2 + offset
            if near <= distance <= far:
                return LabelPlan(height, (0.0, direction * distance))
        height -= mm(LABEL_STEP_MM)
    return None
