import math
from dataclasses import dataclass

from .units import mm

@dataclass(frozen=True)
class BeltProfile:
    """A timing belt type. Sizes are in millimetres.

    pitch: distance from one tooth centre to the next.
    pitch_line_differential: how far the belt's tension cord sits above the
    pulley's tooth tips. It is why a pulley's outside diameter is smaller
    than its pitch diameter.
    """

    name: str
    pitch: float
    pitch_line_differential: float

BELTS = [
    BeltProfile("HTD 5M", pitch=5.0, pitch_line_differential=0.5715),
    BeltProfile("HTD 3M", pitch=3.0, pitch_line_differential=0.381),  # verify
    BeltProfile("GT2 2mm", pitch=2.0, pitch_line_differential=0.254),
]

def find_belt(name):
    for belt in BELTS:
        if belt.name == name:
            return belt
    raise ValueError("Unknown belt: " + name)

def pitch_diameter(belt, teeth):
    """Diameter of the circle the belt's tension cord wraps around (Fusion units)."""
    return mm(belt.pitch * teeth / math.pi)

def outside_diameter(belt, teeth):
    """Diameter across the pulley's tooth tips (Fusion units)."""
    return pitch_diameter(belt, teeth) - 2 * mm(belt.pitch_line_differential)
