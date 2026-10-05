import adsk.core

from .app import FusionPartsError
from .bores import BORES, BoreChoice, bore_reach, ears_fit, find_bore
from .units import mm

BORE_ID = "bore"
CLEARANCE_ID = "bore_clearance"
EARS_ID = "bore_ears"
EAR_SIZE_ID = "bore_ear_size"
NO_BORE = "None"

MIN_WALL_MM = 0.5

def add_bore_inputs(inputs):
    """Add the shaft bore dropdown, clearance and mouse ear fields to a dialog."""
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

    inputs.addBoolValueInput(EARS_ID, "Mouse ears", True, "", False)
    ear_size = inputs.addValueInput(
        EAR_SIZE_ID,
        "Mouse ear diameter",
        "mm",
        adsk.core.ValueInput.createByString("1 mm"),
    )
    ear_size.tooltip = "Adds a small round relief in each corner of the hex hole so the corners print cleanly. The edges are rounded with a fillet the same size as the ear."

def read_bore(inputs):
    """Return a BoreChoice, or None if the user chose no bore."""
    name = inputs.itemById(BORE_ID).selectedItem.name
    if name == NO_BORE:
        return None

    clearance = inputs.itemById(CLEARANCE_ID).value
    if clearance < 0:
        raise FusionPartsError("Bore clearance can't be negative.")
    return BoreChoice(find_bore(name), clearance, _read_ear_radius(inputs))

def _read_ear_radius(inputs):
    """Radius of the mouse ears in Fusion units, or 0 when they're switched off."""
    if not inputs.itemById(EARS_ID).value:
        return 0.0
    diameter = inputs.itemById(EAR_SIZE_ID).value
    if diameter <= 0:
        raise FusionPartsError("Mouse ear diameter must be greater than zero.")
    return diameter / 2

def check_bore_fits(bore_choice, solid_radius, hint):
    """Stop with a clear message if the bore would leave too thin a wall.

    `solid_radius` (Fusion units) is the radius of the thinnest part of the
    solid around the bore: the root radius for a gear, the outside radius
    for a pulley. `hint` is advice for the user, such as "Use more teeth."
    """
    if bore_choice is None:
        return
    if bore_choice.has_ears and not ears_fit(bore_choice):
        raise FusionPartsError(
            "The mouse ears are too big for this bore. Use a smaller ear diameter."
        )
    limit = solid_radius - mm(MIN_WALL_MM)
    if bore_reach(bore_choice) > limit:
        message = "The bore is too big for this part. " + hint
        if bore_choice.has_ears:
            message += " Smaller mouse ears, or none, also help."
        raise FusionPartsError(message)
