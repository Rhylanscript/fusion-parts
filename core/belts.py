import math
from dataclasses import dataclass
from typing import Optional

from .units import mm

@dataclass(frozen=True)
class GrooveShape:
    """The shape of one tooth gap on a pulley. Sizes are in millimetres.

    Every gap is built from circular arcs. Going from the tooth tip down:
      fillet  - small rounded corner on the tooth (radius `fillet_radius`)
      flank   - big concave arc (radius `flank_radius`) forming the side of the gap
      root    - flat-ish floor of the gap, concentric with the pulley (optional)

    flank_centre_depth:  how far below the tooth tips the flank arc's centre sits.
    flank_centre_offset: how far that centre is moved sideways from the middle
                         of the gap, toward the far side (0 = centred).
    root_depth:          how far below the tooth tips the gap floor is.
                         None means the gap ends at the lowest point of the flank arc.
    """

    flank_radius: float
    flank_centre_depth: float
    flank_centre_offset: float
    fillet_radius: float
    root_depth: Optional[float] = None

    @property
    def total_depth(self):
        """Depth of the gap from tooth tip to gap floor, in mm."""
        if self.root_depth is not None:
            return self.root_depth
        return self.flank_centre_depth + self.flank_radius

@dataclass(frozen=True)
class BeltProfile:
    """A timing belt type. Sizes are in millimetres.

    pitch: distance from one tooth centre to the next.
    pitch_line_differential: how far the belt's tension cord sits above the
    pulley's tooth tips. It is why a pulley's outside diameter is smaller
    than its pitch diameter.
    groove: the tooth gap shape, measured from real example pulleys.
    """

    name: str
    pitch: float
    pitch_line_differential: float
    groove: GrooveShape

BELTS = [
    BeltProfile(
        "HTD 5M", pitch=5.0, pitch_line_differential=0.5715,
        groove=GrooveShape(
            flank_radius=1.8842, flank_centre_depth=0.1885,
            flank_centre_offset=0.1445, fillet_radius=0.43, root_depth=1.9983,
        ),
    ),
    BeltProfile(
        "HTD 3M", pitch=3.0, pitch_line_differential=0.381,  # verify
        groove=GrooveShape(
            flank_radius=0.93, flank_centre_depth=0.27,
            flank_centre_offset=0.0, fillet_radius=0.26,
        ),
    ),
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

def root_radius(belt, teeth):
    """Radius at the bottom of the tooth gaps (Fusion units)."""
    return outside_diameter(belt, teeth) / 2 - mm(belt.groove.total_depth)
