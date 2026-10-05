import adsk.core

from ...core.fusion.orientation import side_plane, up_axis, up_point
from ...core.fusion.app import FusionPartsError
from ...core.fusion.output import add_output_dropdown, resolve_target
from ...core.fusion.command import DialogCommand
from ...core.fusion.engrave import engrave_text
from ...core.fusion.features import CUT, JOIN, extrude_profile, revolve_profile
from ...core.fusion.sketches import (
    draw_bore,
    draw_segments,
    largest_profile,
    model_to_sketch,
    new_sketch,
    polygon_segments,
)
from ...core.inputs.belt_inputs import add_belt_input, read_belt
from ...core.inputs.bore_inputs import add_bore_inputs, check_bore_fits, read_bore
from ...core.inputs.flange_inputs import add_flange_inputs, read_flanges
from ...core.inputs.label_inputs import add_label_inputs, read_label
from ...core.shapes.bores import bore_reach
from ...core.shapes.units import mm
from ...core.shapes.belts import outside_diameter, root_radius

from .pulley_layout import cap_points, label_fit
from .pulley_profile import outline_segments


TEETH_ID = "teeth"
WIDTH_ID = "belt_width"
CLEARANCE_ID = "belt_clearance"

BORE_OVERSHOOT = mm(1.0)

class PulleyCommand(DialogCommand):
    cmd_id = "fp_pulley_cmd"
    cmd_name = "Timing Pulley"
    cmd_tooltip = "Generate a timing belt pulley."

    def build_inputs(self, inputs):
        add_belt_input(inputs)
        inputs.addIntegerSpinnerCommandInput(TEETH_ID, "Teeth", 10, 200, 1, 20)
        inputs.addValueInput(
            WIDTH_ID, "Belt width", "mm", adsk.core.ValueInput.createByString("9 mm")
        )
        inputs.addValueInput(
            CLEARANCE_ID, "Belt clearance", "mm",
            adsk.core.ValueInput.createByString("0.25 mm"),
        )
        add_flange_inputs(inputs)
        add_label_inputs(inputs)
        add_bore_inputs(inputs)
        add_output_dropdown(inputs)

    def on_execute(self, inputs):
        belt = read_belt(inputs)
        teeth = inputs.itemById(TEETH_ID).value
        belt_width = inputs.itemById(WIDTH_ID).value
        clearance = inputs.itemById(CLEARANCE_ID).value
        if belt_width <= 0:
            raise FusionPartsError("Belt width must be greater than zero.")
        if clearance < 0:
            raise FusionPartsError("Belt clearance can't be negative.")

        flanges = read_flanges(inputs)
        label = read_label(inputs)
        bore_choice = read_bore(inputs)

        floor_radius = root_radius(belt, teeth)
        check_bore_fits(bore_choice, floor_radius, "Use more teeth.")
        outline = self._build_outline(belt, teeth)
        label_plan = self._plan_label(label, teeth, bore_choice, floor_radius)

        name = "%s Timing Pulley %dT" % (belt.name, teeth)
        target = resolve_target(inputs, name)

        tip_radius = outside_diameter(belt, teeth) / 2
        flange_radius = tip_radius + flanges.overhang
        cap_length = flanges.thickness + flanges.cone_length
        teeth_start = cap_length if flanges.bottom else 0.0
        teeth_end = teeth_start + belt_width + 2 * clearance
        height = teeth_end + (cap_length if flanges.top else 0.0)

        body = self._add_teeth(target, outline, teeth_end - teeth_start, teeth_start)
        if flanges.bottom:
            body = self._add_cap(target, tip_radius, flange_radius, flanges, teeth_start, -1)
        if flanges.top:
            body = self._add_cap(target, tip_radius, flange_radius, flanges, teeth_end, +1)
        if bore_choice is not None:
            self._cut_bore(target, bore_choice, height, body)
        if label_plan is not None:
            engrave_text(
                target, str(teeth), label_plan.height, label_plan.centre,
                label.depth, height, [body],
            )

    def _build_outline(self, belt, teeth):
        """Work out the toothed outline, turning math errors into friendly ones."""
        try:
            return outline_segments(belt, teeth)
        except ValueError as error:
            raise FusionPartsError(str(error))

    def _plan_label(self, label, teeth, bore_choice, floor_radius):
        """Find room for the engraved tooth count, or None if it's switched off."""
        if not label.enabled:
            return None
        inner_radius = 0.0
        if bore_choice is not None:
            inner_radius = bore_reach(bore_choice)
        plan = label_fit(
            len(str(teeth)), inner_radius, floor_radius,
            label.height, label.on_top, label.offset,
        )
        if plan is None:
            raise FusionPartsError(
                "There isn't room to engrave the tooth count there. Try a smaller "
                "label offset, fewer digits (more teeth), a smaller bore, or untick "
                "'Engrave tooth count'."
               )
        return plan

    def _add_teeth(self, target, outline, length, start):
        """Make the toothed section as the pulley's first body. Returns the body."""
        sketch = new_sketch(target, name="Pulley outline")
        draw_segments(sketch, outline)
        feature = extrude_profile(
            target, largest_profile(sketch), length, start_offset=start
        )
        return feature.bodies.item(0)

    def _add_cap(self, target, tip_radius, flange_radius, flanges, teeth_edge, outward):
        """Revolve one flange-and-cone cap and join it to the pulley. Returns the body."""
        points = cap_points(
            tip_radius, flange_radius, flanges.thickness,
            flanges.cone_length, teeth_edge, outward,
        )
        sketch = new_sketch(target, plane=side_plane(target), name="Pulley flange")
        corners = [
            model_to_sketch(sketch, *up_point(radius, height))
            for radius, height in points
        ]
        draw_segments(sketch, polygon_segments(corners))
        feature = revolve_profile(
            target, largest_profile(sketch), up_axis(target), JOIN
        )
        return feature.bodies.item(0)

    def _cut_bore(self, target, bore_choice, height, body):
        """Cut the shaft bore through the whole pulley, touching only `body`."""
        sketch = new_sketch(target, name="Pulley bore")
        draw_bore(sketch, bore_choice)
        extrude_profile(
            target, largest_profile(sketch), height + 2 * BORE_OVERSHOOT, CUT,
            start_offset=-BORE_OVERSHOOT, participants=[body],
        )
