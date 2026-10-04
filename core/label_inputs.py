from dataclasses import dataclass

import adsk.core

from .app import FusionPartsError

ENABLE_ID = "label_enable"
POSITION_ID = "label_position"
OFFSET_ID = "label_offset"
DEPTH_ID = "label_depth"
HEIGHT_ID = "label_height"

TOP = "Top"
BOTTOM = "Bottom"

@dataclass(frozen=True)
class LabelSpec:
    """Engraved label settings. Lengths are in Fusion units (cm)."""

    enabled: bool
    on_top: bool
    offset: float
    depth: float
    height: float

def add_label_inputs(inputs):
    """Add the engrave checkbox, position, offset, depth and text height fields."""
    inputs.addBoolValueInput(ENABLE_ID, "Engrave tooth count", True, "", True)

    position = inputs.addDropDownCommandInput(
        POSITION_ID, "Label position", adsk.core.DropDownStyles.TextListDropDownStyle
    )
    position.listItems.add(TOP, True)
    position.listItems.add(BOTTOM, False)

    offset = inputs.addValueInput(
        OFFSET_ID, "Label offset", "mm", adsk.core.ValueInput.createByString("0 mm")
    )
    offset.tooltip = "0 centres the text in the space around the bore. Positive moves it away from the centre, negative toward it."

    inputs.addValueInput(
        DEPTH_ID, "Engraving depth", "mm", adsk.core.ValueInput.createByString("0.25 mm")
    )
    inputs.addValueInput(
        HEIGHT_ID, "Text height", "mm", adsk.core.ValueInput.createByString("3 mm")
    )

def read_label(inputs):
    """Read the label fields into a LabelSpec, checking they make sense."""
    enabled = inputs.itemById(ENABLE_ID).value
    on_top = inputs.itemById(POSITION_ID).selectedItem.name == TOP
    offset = inputs.itemById(OFFSET_ID).value
    depth = inputs.itemById(DEPTH_ID).value
    height = inputs.itemById(HEIGHT_ID).value
    if enabled and depth <= 0:
        raise FusionPartsError("Engraving depth must be greater than zero.")
    if enabled and height <= 0:
        raise FusionPartsError("Text height must be greater than zero.")
    return LabelSpec(
        enabled=enabled, on_top=on_top, offset=offset, depth=depth, height=height
    )
