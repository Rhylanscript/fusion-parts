import math

import adsk.core

from ...core.fusion.app import FusionPartsError

from .gear_profile import GearSpec

TEETH_ID = "teeth"
MODULE_ID = "module"
PRESSURE_ANGLE_ID = "pressure_angle"
THICKNESS_ID = "thickness"

MIN_PRESSURE_ANGLE_DEG = 10
MAX_PRESSURE_ANGLE_DEG = 30


def add_gear_inputs(inputs):
    """add the teeth, module and pressure angle fields to a dialog"""
    inputs.addIntegerSpinnerCommandInput(TEETH_ID, "Teeth", 6, 200, 1, 20)
    inputs.addValueInput(
        MODULE_ID, "Module", "mm", adsk.core.ValueInput.createByString("1 mm")
    )
    inputs.addValueInput(
        PRESSURE_ANGLE_ID,
        "Pressure angle",
        "deg",
        adsk.core.ValueInput.createByString("20 deg"),
    )


def add_thickness_input(inputs):
    """Add the thickness field to a dialog"""
    inputs.addValueInput(
        THICKNESS_ID, "Thickness", "mm", adsk.core.ValueInput.createByString("5 mm")
    )


def read_gear_spec(inputs):
    """Read the dialog fields into a GearSpec"""
    spec = GearSpec(
        teeth=inputs.itemById(TEETH_ID).value,
        module=inputs.itemById(MODULE_ID).value,
        pressure_angle=inputs.itemById(PRESSURE_ANGLE_ID).value,    # rad
    )
    if spec.module <= 0:
        raise FusionPartsError("Module must be greater than zero")

    low = math.radians(MIN_PRESSURE_ANGLE_DEG)
    high = math.radians(MAX_PRESSURE_ANGLE_DEG)
    if not low <= spec.pressure_angle <= high:
        raise FusionPartsError(
            "Pressure angle must be between %d and %d degrees"
            % (MIN_PRESSURE_ANGLE_DEG, MAX_PRESSURE_ANGLE_DEG)
        )
    return spec


def read_thickness(inputs):
    """Read the thickness field (Fusion units)"""
    thickness = inputs.itemById(THICKNESS_ID).value
    if thickness <= 0:
        raise FusionPartsError("Thickness must be greater than zero")
    return thickness
