from dataclasses import dataclass

import adsk.core
import adsk.fusion

from .app import FusionPartsError


@dataclass(frozen=True)
class CircleInfo:
    """A circle found in the design. Lengths are in Fusion units (cm).

    centre: (x, y, z) in model space.
    normal: (x, y, z) direction the circle faces (straight out of its flat side).
    """

    centre: tuple
    radius: float
    normal: tuple


def circle_from_entity(entity):
    """Turn a picked sketch circle or circular edge into a CircleInfo.

    Raises FusionPartsError if the pick isn't a circle or an arc of one.
    """
    sketch_circle = adsk.fusion.SketchCircle.cast(entity)
    if sketch_circle is not None:
        # worldGeometry is the circle placed in the model, not in the sketch.
        return _to_info(sketch_circle.worldGeometry)

    edge = adsk.fusion.BRepEdge.cast(entity)
    if edge is not None:
        geometry = edge.geometry
        circle = adsk.core.Circle3D.cast(geometry)
        if circle is None:
            circle = adsk.core.Arc3D.cast(geometry)
        if circle is not None:
            return _to_info(circle)

    raise FusionPartsError("That isn't a circle. Pick a circular edge or a sketch circle.")


def _to_info(geometry):
    """Copy the numbers out of a Circle3D or Arc3D."""
    centre = geometry.center
    normal = geometry.normal
    return CircleInfo(
        centre=(centre.x, centre.y, centre.z),
        radius=geometry.radius,
        normal=(normal.x, normal.y, normal.z),
    )
