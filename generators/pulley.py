import adsk.core

from ..core.app import FusionPartsError
from ..core.belt_inputs import add_belt_input, read_belt
from ..core.belts import outside_diameter
from ..core.bore_inputs import add_bore_inputs, check_bore_fits, read_bore
from ..core.bores import bore_segments
from ..core.command import DialogCommand
from ..core.features import extrude_profile
from ..core.output import add_output_dropdown, resolve_target
from ..core.sketches import add_circle, draw_segments, largest_profile, new_sketch

TEETH_ID = "teeth"
WIDTH_ID = "belt_width"

class PulleyCommand(DialogCommand):
    cmd_id = "fp_pulley_cmd"
    cmd_name = "Pulley"
    cmd_tooltip = "Generate a pulley."

    def build_inputs(self, inputs):
        add_belt_input(inputs)
        inputs.addIntegerSpinnerCommandInput(TEETH_ID, "Teeth", 10, 200, 1, 20)
        inputs.addValueInput(
            WIDTH_ID, "Belt width", "mm", adsk.core.ValueInput.createByString("9 mm")
        )
        add_bore_inputs(inputs)
        add_output_dropdown(inputs)

    def on_execute(self, inputs):
        belt = read_belt(inputs)
        teeth = inputs.itemById(TEETH_ID).value
        width = inputs.itemById(WIDTH_ID).value
        if width <= 0:
            raise FusionPartsError("Belt width must be greater than zero.")

        bore_choice = read_bore(inputs)
        outer_radius = outside_diameter(belt, teeth) / 2
        check_bore_fits(bore_choice, outer_radius, "Use more teeth.")

        name = "%s Pulley %dT" % (belt.name, teeth)
        target = resolve_target(inputs, name)
        sketch = new_sketch(target, name="Pulley outline")
        add_circle(sketch, outer_radius)
        if bore_choice is not None:
            bore, clearance = bore_choice
            draw_segments(sketch, bore_segments(bore, clearance))
        extrude_profile(target, largest_profile(sketch), width)
