import math

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

def label_fit(label_length, inner_radius, outer_radius, max_height):
    """Find where, and how big, an engraved label can go. Fusion units.

    The label sits on the +X side, between the bore (`inner_radius`, 0 for no
    bore) and `outer_radius`. The text shrinks from `max_height` until it
    fits. Returns (centre_x, height), or None if even the smallest size fails.
    """
    margin = mm(LABEL_MARGIN_MM)
    limit = outer_radius - margin
    height = max_height
    while height >= mm(MIN_LABEL_HEIGHT_MM) - 1e-9:
        half_width = label_length * CHAR_WIDTH * height / 2
        half_height = height / 2
        if math.hypot(half_width, half_height) <= limit:
            if inner_radius <= 0:
                return 0.0, height
            furthest = math.sqrt(limit**2 - half_height**2) - half_width
            nearest = inner_radius + margin + half_width
            if nearest <= furthest:
                return (nearest + furthest) / 2, height
        height -= mm(LABEL_STEP_MM)
    return None
