import math

from ...core.shapes.belts import outside_diameter, pitch_diameter
from ...core.shapes.geometry import polar
from ...core.shapes.units import mm

def _check_tangent(radius_a, radius_b, distance):
    """Stop if no straight belt section can join two circles this far apart."""
    if distance <= abs(radius_a - radius_b):
        raise ValueError("The pulleys are too close together. Increase the centre distance.")

def _on_circle(centre_x, radius, angle):
    """Point on a circle whose centre is at (centre_x, 0)."""
    x, y = polar(radius, angle)
    return (centre_x + x, y)

def loop_segments(radius_a, radius_b, distance):
    """Closed racetrack around two circles, as line/arc pieces (Fusion units)."""
    _check_tangent(radius_a, radius_b, distance)
    angle = math.acos((radius_a - radius_b) / distance)

    top_a = _on_circle(0.0, radius_a, angle)
    bottom_a = _on_circle(0.0, radius_a, -angle)
    top_b = _on_circle(distance, radius_b, angle)
    bottom_b = _on_circle(distance, radius_b, -angle)

    return [
        ("line", bottom_a, bottom_b),
        ("arc", bottom_b, _on_circle(distance, radius_b, 0.0), top_b),
        ("line", top_b, top_a),
        ("arc", top_a, _on_circle(0.0, radius_a, math.pi), bottom_a),
    ]

def loops_from_radii(radius_a, radius_b, thickness, distance):
    """Return (outer_loop, inner_loop) for a belt hugging two circles.

    The inner loop touches both circles. All lengths are in Fusion units.
    """
    if distance <= radius_a + radius_b:
        raise ValueError(
            "The pulleys would overlap. Increase the centre distance."
        )
    inner = loop_segments(radius_a, radius_b, distance)
    outer = loop_segments(radius_a + thickness, radius_b + thickness, distance)
    return outer, inner

def belt_loops(belt, teeth_a, teeth_b, distance):
    """Return (outer_loop, inner_loop) for a belt hugging two pulleys."""
    radius_a = outside_diameter(belt, teeth_a) / 2
    radius_b = outside_diameter(belt, teeth_b) / 2
    return loops_from_radii(radius_a, radius_b, mm(belt.thickness), distance)

def pitch_length(belt, teeth_a, teeth_b, distance):
    """Length of the belt's tension cord around both pulleys (Fusion units)."""
    radius_a = pitch_diameter(belt, teeth_a) / 2
    radius_b = pitch_diameter(belt, teeth_b) / 2
    _check_tangent(radius_a, radius_b, distance)
    lean = math.asin((radius_b - radius_a) / distance)
    return (
        2 * distance * math.cos(lean)
        + radius_a * (math.pi - 2 * lean)
        + radius_b * (math.pi + 2 * lean)
    )

def belt_teeth(belt, teeth_a, teeth_b, distance):
    """How many belt teeth fit the pitch length (usually not a whole number)."""
    return pitch_length(belt, teeth_a, teeth_b, distance) / mm(belt.pitch)
