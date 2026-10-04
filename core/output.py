import adsk.core

from .app import ASSEMBLY, PART, get_design, get_design_intent
from .components import new_component

OUTPUT_ID = "output"
OUTPUT_COMPONENT = "New component"
OUTPUT_BODY = "New body"

def _allowed_outputs():
    """Which output choices make sense for the kind of file that's open.

    Part files can't contain components, assembly files shouldn't get loose
    bodies, and hybrid files can have either.
    """
    intent = get_design_intent()
    if intent == PART:
        return [OUTPUT_BODY]
    if intent == ASSEMBLY:
        return [OUTPUT_COMPONENT]
    return [OUTPUT_COMPONENT, OUTPUT_BODY]

def add_output_dropdown(inputs):
    """Add the Output dropdown to a dialog"""
    dropdown = inputs.addDropDownCommandInput(
        OUTPUT_ID, "Output", adsk.core.DropDownStyles.TextListDropDownStyle
    )
    for index, option in enumerate(_allowed_outputs()):
        dropdown.listItems.add(option, index == 0)
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
