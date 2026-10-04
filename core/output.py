import adsk.core

from .app import ASSEMBLY, PART, get_design, get_design_intent
from .components import new_component

OUTPUT_ID = "output"
OUTPUT_COMPONENT = "New component"
OUTPUT_BODY = "New body"

def add_output_dropdown(inputs):
    """Add the Output dropdown to a dialog. Assemblies only get 'New component'."""
    dropdown = inputs.addDropDownCommandInput(
        OUTPUT_ID, "Output", adsk.core.DropDownStyles.TextListDropDownStyle
    )
    if get_design_intent() != PART:
        dropdown.listItems.add(OUTPUT_COMPONENT, True)
    if get_design_intent() != ASSEMBLY:
        dropdown.listItems.add(OUTPUT_BODY, False)
    return dropdown

def resolve_target(inputs, component_name):
    """Return the component the generator should build into.

    - "New component": makes a fresh component called `component_name`.
    - "New body": returns the root component, so the shape becomes a loose body.
    """
    choice = inputs.itemById(OUTPUT_ID).selectedItem.name
    if choice == OUTPUT_COMPONENT:
        return new_component(component_name)
    return get_design().rootComponent
