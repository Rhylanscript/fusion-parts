import adsk.core

from ..core.app import FusionPartsError
from ..core.belt_inputs import add_belt_input, read_belt
from ..core.command import DialogCommand
from ..core.features import extrude_profile
from ..core.output import add_output_dropdown, resolve_target
from ..core.sketches import draw_segments, new_sketch, ring_profile
from .belt_path import belt_loops, belt_teeth

TEETH_A_ID = "belt_teeth_a"
TEETH_B_ID = "belt_teeth_b"
DISTANCE_ID = "belt_distance"
WIDTH_ID = "belt_width"

class BeltCommand(DialogCommand):
    cmd_id = "fp_belt_cmd"
    cmd_name = "Timing Belt"
    cmd_tooltip = "Generate a timing belt around two pulleys."

    def build_inputs(self, inputs):
        add_belt_input(inputs)
        inputs.addIntegerSpinnerCommandInput(TEETH_A_ID, "Teeth, pulley 1", 10, 200, 1, 24)
        inputs.addIntegerSpinnerCommandInput(TEETH_B_ID, "Teeth, pulley 2", 10, 200, 1, 36)
        inputs.addValueInput(
            DISTANCE_ID, "Centre distance", "mm",
            adsk.core.ValueInput.createByString("225 mm"),
        )
        inputs.addValueInput(
            WIDTH_ID, "Belt width", "mm", adsk.core.ValueInput.createByString("6 mm")
        )
        add_output_dropdown(inputs)

    def on_execute(self, inputs):
        belt = read_belt(inputs)
        teeth_a = inputs.itemById(TEETH_A_ID).value
        teeth_b = inputs.itemById(TEETH_B_ID).value
        distance = inputs.itemById(DISTANCE_ID).value
        width = inputs.itemById(WIDTH_ID).value
        if width <= 0:
            raise FusionPartsError("Belt width must be greater than zero.")

        outer, inner = self._build_loops(belt, teeth_a, teeth_b, distance)
        tooth_count = round(belt_teeth(belt, teeth_a, teeth_b, distance))

        target = resolve_target(inputs, "%s Belt %dT" % (belt.name, tooth_count))
        sketch = new_sketch(target, name="Belt outline")
        draw_segments(sketch, outer)
        draw_segments(sketch, inner)

        profile = ring_profile(sketch)
        if profile is None:
            raise FusionPartsError("Couldn't build the belt outline.")
        extrude_profile(target, profile, width)

    def _build_loops(self, belt, teeth_a, teeth_b, distance):
        """Work out the belt outline, turning math errors into friendly ones."""
        try:
            return belt_loops(belt, teeth_a, teeth_b, distance)
        except ValueError as error:
            raise FusionPartsError(str(error))
