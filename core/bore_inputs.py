import adsk.core

from .app import FusionPartsError
from .bores import BORES, find_bore

BORE_ID = "bore"
CLEARANCE_ID = "bore_clearance"
NO_BORE = "None"

def add_bore_inputs(inputs):
    """Add the shaft bore dropdown and clearance field to a dialog."""
    dropdown = inputs.addDropDownCommandInput(
        BORE_ID, "Shaft bore", adsk.core.DropDownStyles.TextListDropDownStyle
    )
    for index, bore in enumerate(BORES):
        dropdown.listItems.add(bore.name, index == 0)
    dropdown.listItems.add(NO_BORE, False)

    inputs.addValueInput(
        CLEARANCE_ID,
        "Bore clearance",
        "mm",
        adsk.core.ValueInput.createByString("0.1 mm"),
    )

def read_bore(inputs):
    """Return (bore, clearance), or None if the user chose no bore."""
    name = inputs.itemById(BORE_ID).selectedItem.name
    if name == NO_BORE:
        return None

    clearance = inputs.itemById(CLEARANCE_ID).value
    if clearance < 0:
        raise FusionPartsError("Bore clearance can't be negative.")
    return find_bore(name), clearance
