import adsk.core

from ..fusion.circles import circle_from_entity


def add_circle_picker(inputs, input_id, name):
    """Add a box that accepts one circular edge or one sketch circle"""
    picker = inputs.addSelectionInput(
        input_id, name, "Select a circular edge or a sketch circle"
    )
    picker.addSelectionFilter(adsk.core.SelectionCommandInput.CircularEdges)
    picker.addSelectionFilter(adsk.core.SelectionCommandInput.SketchCircles)
    picker.setSelectionLimits(1, 1)
    return picker


def read_circle(inputs, input_id):
    """Return a CircleInfo for whats picked, or None if nothing is picked yet"""
    picker = inputs.itemById(input_id)
    if picker.selectionCount == 0:
        return None
    return circle_from_entity(picker.selection(0).entity)
