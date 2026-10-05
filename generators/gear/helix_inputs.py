import math

import adsk.core

from ...core.fusion.app import FusionPartsError

HELIX_ID = "helix_angle"

MIN_HELIX_ANGLE_DEG = 1
MAX_HELIX_ANGLE_DEG = 45

def add_helix_input(inputs):
    """Add the helix angle field to a dialog."""
    helix = inputs.addValueInput(
        HELIX_ID, "Helix angle", "deg", adsk.core.ValueInput.createByString("20 deg")
    )
    helix.tooltip = "How steeply the teeth lean. Module and pressure angle are measured on the flat face of the gear."


def read_helix_angle(inputs):
    """Read the helix angle (radians), checking it makes sense."""
    angle = inputs.itemById(HELIX_ID).value
    low = math.radians(MIN_HELIX_ANGLE_DEG)
    high = math.radians(MAX_HELIX_ANGLE_DEG)
    if not low <= angle <= high:
        raise FusionPartsError(
            "Helix angle must be between %d and %d degrees."
            % (MIN_HELIX_ANGLE_DEG, MAX_HELIX_ANGLE_DEG)
        )
    return angle
