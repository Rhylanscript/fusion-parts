from dataclasses import dataclass

import adsk.core

from .app import FusionPartsError

STYLE_ID = "flange_style"
THICKNESS_ID = "flange_thickness"
OVERHANG_ID = "flange_overhang"

BOTH = "Both"
BOTTOM_ONLY = "Bottom only"
NONE = "None"

@dataclass(frozen=True)
class FlangeSpec:
    """What flanges the user wants. Lengths are in Fusion units (cm)."""

    bottom: bool
    top: bool
    thickness: float
    overhang: float

def add_flange_inputs(inputs):
    """Add the flange style, thickness and overhang fields to a dialog."""
    dropdown = inputs.addDropDownCommandInput(
        STYLE_ID, "Flanges", adsk.core.DropDownStyles.TextListDropDownStyle
    )
    dropdown.listItems.add(BOTH, True)
    dropdown.listItems.add(BOTTOM_ONLY, False)
    dropdown.listItems.add(NONE, False)

    inputs.addValueInput(
        THICKNESS_ID, "Flange thickness", "mm",
        adsk.core.ValueInput.createByString("1 mm"),
    )
    inputs.addValueInput(
        OVERHANG_ID, "Flange overhang", "mm",
        adsk.core.ValueInput.createByString("1.5 mm"),
    )

def read_flanges(inputs):
    """Read the flange fields into a FlangeSpec, checking they make sense."""
    style = inputs.itemById(STYLE_ID).selectedItem.name
    thickness = inputs.itemById(THICKNESS_ID).value
    overhang = inputs.itemById(OVERHANG_ID).value

    wants_flanges = style != NONE
    if wants_flanges and thickness <= 0:
        raise FusionPartsError("Flange thickness must be greater than zero.")
    if wants_flanges and overhang <= 0:
        raise FusionPartsError("Flange overhang must be greater than zero.")

    return FlangeSpec(
        bottom=wants_flanges,
        top=style == BOTH,
        thickness=thickness,
        overhang=overhang,
    )
