import adsk.core

from ..core.app import FusionPartsError
from ..core.belt_inputs import add_belt_input, read_belt
from ..core.command import DialogCommand
from ..core.features import extrude_profile
from ..core.output import add_output_dropdown, resolve_target
from ..core.sketches import draw_segments, new_sketch, ring_profile
from ..core.units import to_mm
from .belt_path import belt_loops, belt_teeth, pitch_length

TEETH_A_ID = "belt_teeth_a"
TEETH_B_ID = "belt_teeth_b"
DISTANCE_ID = "belt_distance"
WIDTH_ID = "belt_width"
INFO_ID = "belt_info"

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
        inputs.addTextBoxCommandInput(INFO_ID, "Belt size", "", 2, True)
        self._update_info(inputs)
        add_output_dropdown(inputs)

    def on_inputs_changed(self, inputs, changed_input):
        self._update_info(inputs)

    def on_execute(self, inputs):
        belt, teeth_a, teeth_b, distance = self._read_layout(inputs)
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

    def _read_layout(self, inputs):
        """Read the belt type, both tooth counts and the centre distance."""
        return (
            read_belt(inputs),
            inputs.itemById(TEETH_A_ID).value,
            inputs.itemById(TEETH_B_ID).value,
            inputs.itemById(DISTANCE_ID).value,
        )

    def _build_loops(self, belt, teeth_a, teeth_b, distance):
        """Work out the belt outline, turning math errors into friendly ones."""
        try:
            return belt_loops(belt, teeth_a, teeth_b, distance)
        except ValueError as error:
            raise FusionPartsError(str(error))

    def _update_info(self, inputs):
        """Show the belt's pitch length and tooth count in the dialog."""
        inputs.itemById(INFO_ID).formattedText = self._describe(inputs)

    def _describe(self, inputs):
        """Text for the info box. Never raises: problems become a message."""
        belt, teeth_a, teeth_b, distance = self._read_layout(inputs)
        try:
            belt_loops(belt, teeth_a, teeth_b, distance)  # checks the spacing
            length = pitch_length(belt, teeth_a, teeth_b, distance)
            teeth = belt_teeth(belt, teeth_a, teeth_b, distance)
        except ValueError as error:
            return str(error)
        return "Pitch length: %.1f mm<br />Belt teeth: %.2f" % (to_mm(length), teeth)
