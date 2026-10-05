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
