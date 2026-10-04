import math

def polar(radius, angle):
    """Convert (distance from centre, angle in radians) to an (x, y) point."""
    return (radius * math.cos(angle), radius * math.sin(angle))
