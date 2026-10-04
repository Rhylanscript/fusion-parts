import adsk.core

from .app import FusionPartsError
from .bores import BORES, bore_outer_radius, find_bore
from .units import mm

BORE_ID = "bore"
CLEARANCE_ID = "bore_clearance"
NO_BORE = "None"

MIN_WALL_MM = 0.5

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

def check_bore_fits(bore_choice, solid_radius, hint):
    """Stop with a clear message if the bore would leave too thin a wall.

    `solid_radius` (Fusion units) is the radius of the thinnest part of the
    solid around the bore: the root radius for a gear, the outside radius
    for a pulley. `hint` is advice for the user, such as "Use more teeth."
    """
    if bore_choice is None:
        return
    bore, clearance = bore_choice
    limit = solid_radius - mm(MIN_WALL_MM)
    if bore_outer_radius(bore, clearance) > limit:
        raise FusionPartsError("The bore is too big for this part. " + hint)
