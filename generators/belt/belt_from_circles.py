import math

import adsk.core

from ...core.fusion.app import FusionPartsError
from ...core.fusion.command import DialogCommand
from ...core.fusion.features import extrude_profile
from ...core.fusion.output import add_output_dropdown, resolve_target
from ...core.fusion.orientation import offset_ground_plane, up_vector
from ...core.fusion.sketches import draw_segments, model_to_sketch, new_sketch, ring_profile
from ...core.inputs.belt_inputs import add_belt_input, read_belt
from ...core.inputs.circle_inputs import add_circle_picker, read_circle
from ...core.shapes.geometry import are_parallel, dot, in_plane_distance, place_segments
from ...core.shapes.units import mm, to_mm

from .belt_path import loops_from_radii

PULLEY_A_ID = "bfc_pulley_a"
PULLEY_B_ID = "bfc_pulley_b"
WIDTH_ID = "bfc_width"
FLIP_ID = "bfc_flip"
INFO_ID = "bfc_info"


class BeltFromCirclesCommand(DialogCommand):
    cmd_id = "fp_belt_from_circles_cmd"
    cmd_name = "Belt From Circles"
    cmd_tooltip = "Generate a belt around two selected circles."

    def build_inputs(self, inputs):
        add_circle_picker(inputs, PULLEY_A_ID, "Pulley 1")
        add_circle_picker(inputs, PULLEY_B_ID, "Pulley 2")
        add_belt_input(inputs)
        inputs.addValueInput(
            WIDTH_ID, "Belt width", "mm", adsk.core.ValueInput.createByString("6 mm")
        )
        flip = inputs.addBoolValueInput(FLIP_ID, "Flip direction", True, "", False)
        flip.tooltip = "By default the belt grows upward from the picked circle. Tick this to grow it downward instead."
        inputs.addTextBoxCommandInput(INFO_ID, "Selection", "Nothing selected yet.", 5, True)
        add_output_dropdown(inputs)

    def on_inputs_changed(self, inputs, changed_input):
        inputs.itemById(INFO_ID).formattedText = self._describe(inputs)

    def on_execute(self, inputs):
        belt = read_belt(inputs)
        width = inputs.itemById(WIDTH_ID).value
        if width <= 0:
            raise FusionPartsError("Belt width must be greater than zero.")
        circle_a, circle_b = self._read_pair(inputs)

        up = up_vector()
        flat_distance = in_plane_distance(circle_a.centre, circle_b.centre, up)
        outer, inner = self._build_loops(circle_a, circle_b, belt, flat_distance)

        height = dot(circle_a.centre, up)
        if inputs.itemById(FLIP_ID).value: height -= width

        target = resolve_target(inputs, "%s Belt" % belt.name)
        plane = offset_ground_plane(target, height)
        sketch = new_sketch(target, plane=plane, name="Belt outline")

        start = model_to_sketch(sketch, *circle_a.centre)
        end = model_to_sketch(sketch, *circle_b.centre)
        angle = math.atan2(end[1] - start[1], end[0] - start[0])

        draw_segments(sketch, place_segments(outer, start, angle))
        draw_segments(sketch, place_segments(inner, start, angle))

        profile = ring_profile(sketch)
        if profile is None:
            raise FusionPartsError("Couldn't build the belt outline.")
        extrude_profile(target, profile, width)

    def _read_pair(self, inputs):
        """Return both circles, checking they can share a belt"""
        circle_a = read_circle(inputs, PULLEY_A_ID)
        circle_b = read_circle(inputs, PULLEY_B_ID)
        if circle_a is None or circle_b is None:
            raise FusionPartsError("Pick a circle in both boxes.")
        up = up_vector()
        if not (are_parallel(circle_a.normal, up) and are_parallel(circle_b.normal, up)):
            raise FusionPartsError(
                "Both circles must lie flat on the ground plane (facing straight up or down)."
            )
        return circle_a, circle_b

    def _build_loops(self, circle_a, circle_b, belt, distance):
        """work out belt outline"""
        try:
            return loops_from_radii(
                circle_a.radius, circle_b.radius, mm(belt.thickness), distance
            )
        except ValueError as error:
            raise FusionPartsError(str(error))

    def _describe(self, inputs):
        """text for the info box"""
        lines = [
            _describe_circle("Pulley 1", inputs, PULLEY_A_ID),
            _describe_circle("Pulley 2", inputs, PULLEY_B_ID),
        ]
        try:
            circle_a, circle_b = self._read_pair(inputs)
        except FusionPartsError as error:
            lines.append(str(error))
        else:
            distance = in_plane_distance(circle_a.centre, circle_b.centre, up_vector())
            lines.append("Centre distance: %.2f mm" % to_mm(distance))
        return "<br />".join(lines)


def _describe_circle(label, inputs, input_id):
    """one line of text about the circle picked in `input_id`"""
    try:
        circle = read_circle(inputs, input_id)
    except FusionPartsError as error:
        return "%s: %s" % (label, error)
    if circle is None:
        return "%s: nothing selected" % label

    x, y, z = (to_mm(value) for value in circle.centre)
    return "%s: radius %.3f mm, centre (%.2f, %.2f, %.2f) mm" % (
        label, to_mm(circle.radius), x, y, z,
    )
