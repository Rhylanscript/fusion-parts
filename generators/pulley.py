import adsk.core

from ..core.app import FusionPartsError
from ..core.belt_inputs import add_belt_input, read_belt
from ..core.belts import outside_diameter, root_radius
from ..core.bore_inputs import add_bore_inputs, check_bore_fits, read_bore
from ..core.command import DialogCommand
from ..core.features import JOIN, extrude_profile
from ..core.flange_inputs import add_flange_inputs, read_flanges
from ..core.output import add_output_dropdown, resolve_target
from ..core.sketches import (
    add_circle,
    draw_bore,
    draw_segments,
    largest_profile,
    new_sketch,
)
from .pulley_profile import outline_segments

TEETH_ID = "teeth"
WIDTH_ID = "belt_width"
CLEARANCE_ID = "belt_clearance"

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
        bore_choice = read_bore(inputs)
        check_bore_fits(bore_choice, root_radius(belt, teeth), "Use more teeth.")
        outline = self._build_outline(belt, teeth)

        name = "%s Pulley %dT" % (belt.name, teeth)
        target = resolve_target(inputs, name)

        toothed_length = belt_width + 2 * clearance
        toothed_start = flanges.thickness if flanges.bottom else 0.0
        self._add_teeth(target, outline, bore_choice, toothed_length, toothed_start)

        flange_radius = outside_diameter(belt, teeth) / 2 + flanges.overhang
        if flanges.bottom:
            self._add_flange(target, flange_radius, bore_choice, flanges.thickness, 0.0)
        if flanges.top:
            top_start = toothed_start + toothed_length
            self._add_flange(target, flange_radius, bore_choice, flanges.thickness, top_start)

    def _build_outline(self, belt, teeth):
        """Work out the toothed outline, turning math errors into friendly ones."""
        try:
            return outline_segments(belt, teeth)
        except ValueError as error:
            raise FusionPartsError(str(error))

    def _add_teeth(self, target, outline, bore_choice, length, start):
        """Make the toothed section as the pulley's first (new) body."""
        sketch = new_sketch(target, name="Pulley outline")
        draw_segments(sketch, outline)
        draw_bore(sketch, bore_choice)
        extrude_profile(target, largest_profile(sketch), length, start_offset=start)

    def _add_flange(self, target, radius, bore_choice, thickness, start):
        """Make one flange disc and join it to the pulley body."""
        sketch = new_sketch(target, name="Pulley flange")
        add_circle(sketch, radius)
        draw_bore(sketch, bore_choice)
        extrude_profile(
            target, largest_profile(sketch), thickness, JOIN, start_offset=start
        )
