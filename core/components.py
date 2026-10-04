import adsk.core

from .app import get_design


def new_component(name):
    """Create a new empty component in the root of the design and return it."""
    design = get_design()
    occurrence = design.rootComponent.occurrences.addNewComponent(
        adsk.core.Matrix3D.create()
    )
    component = occurrence.component
    component.name = name
    return component
