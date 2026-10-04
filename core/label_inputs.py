from dataclasses import dataclass

import adsk.core

from .app import FusionPartsError

ENABLE_ID = "label_enable"
DEPTH_ID = "label_depth"
HEIGHT_ID = "label_height"

@dataclass(frozen=True)
class LabelSpec:
    """Engraved label settings. Lengths are in Fusion units (cm)."""

    enabled: bool
    depth: float
    height: float

def add_label_inputs(inputs):
    """Add the engrave checkbox, depth and text height fields to a dialog."""
    inputs.addBoolValueInput(ENABLE_ID, "Engrave tooth count", True, "", True)
    inputs.addValueInput(
        DEPTH_ID, "Engraving depth", "mm", adsk.core.ValueInput.createByString("0.25 mm")
    )
    inputs.addValueInput(
        HEIGHT_ID, "Text height", "mm", adsk.core.ValueInput.createByString("3 mm")
    )

def read_label(inputs):
    """Read the label fields into a LabelSpec, checking they make sense"""
    enabled = inputs.itemById(ENABLE_ID).value
    depth = inputs.itemById(DEPTH_ID).value
    height = inputs.itemById(HEIGHT_ID).value
    if enabled and depth <= 0: raise FusionPartsError("Engraving depth must be greater than zero.")
    if enabled and height <= 0: raise FusionPartsError("Text height must be greater than zero.")
    return LabelSpec(enabled=enabled, depth=depth, height=height)
