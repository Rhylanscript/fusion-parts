import math

def polar(radius, angle):
    """Convert (distance from centre, angle in radians) to an (x, y) point."""
    return (radius * math.cos(angle), radius * math.sin(angle))

def arc_through(centre, start, end):
    """Return ("arc", start, middle, end) for the short arc around `centre`"""
    radius = math.hypot(start[0] - centre[0], start[1] - centre[1])
    first = math.atan2(start[1] - centre[1], start[0] - centre[0])
    last = math.atan2(end[1] - centre[1], end[0] - centre[0])
    difference = (last - first + math.pi) % (2 * math.pi) - math.pi
    middle = (
        centre[0] + radius * math.cos(first + difference / 2),
        centre[1] + radius * math.sin(first + difference / 2),
    )
    return ("arc", start, middle, end)

def dot(a, b):
    """dot product of two vectors given as tuples"""
    return sum(x * y for x, y in zip(a, b))


def are_parallel(normal_a, normal_b, tolerance=1e-6):
    """True if two unit vectors point along the same line (either way round)"""
    return math.isclose(abs(dot(normal_a, normal_b)), 1.0, abs_tol=tolerance)


def in_plane_distance(point_a, point_b, normal):
    """Distance between two 3D points once any height along `normal` is ignored

    `normal` must be a unit vector. Two pulleys at different heights along
    their shared axis still count as being as far apart as their centres are
    when viewed from above.
    """
    along = tuple(b - a for a, b in zip(point_a, point_b))
    lift = dot(along, normal)
    flat = [component - lift * n for component, n in zip(along, normal)]
    return math.sqrt(dot(flat, flat))


def _place_point(point, origin, angle):
    """Rotate an (x, y) point by `angle` around (0, 0), then move it by `origin`."""
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    x, y = point
    return (origin[0] + x * cos_a - y * sin_a, origin[1] + x * sin_a + y * cos_a)


def place_segments(segments, origin, angle):
    """Rotate then move every point of a list of line/arc/spline pieces.

    Same piece format as draw_segments(). Lets us build a shape in a simple
    spot (pulley 1 at the origin, pulley 2 along X) and then slide it onto
    wherever the pulleys really are.
    """
    placed = []
    for segment in segments:
        if segment[0] == "spline":
            points = [_place_point(point, origin, angle) for point in segment[1]]
            placed.append(("spline", points))
        else:
            points = tuple(_place_point(point, origin, angle) for point in segment[1:])
            placed.append((segment[0],) + points)
    return placed
