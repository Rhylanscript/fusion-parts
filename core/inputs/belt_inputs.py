import adsk.core

from ..shapes.belts import BELTS, find_belt

BELT_ID = "belt"

def add_belt_input(inputs):
    """Add the Belt profile dropdown to a dialog."""
    dropdown = inputs.addDropDownCommandInput(
        BELT_ID, "Belt profile", adsk.core.DropDownStyles.TextListDropDownStyle
    )
    for index, belt in enumerate(BELTS):
        dropdown.listItems.add(belt.name, index == 0)

def read_belt(inputs):
    """Return the BeltProfile the user picked."""
    return find_belt(inputs.itemById(BELT_ID).selectedItem.name)
