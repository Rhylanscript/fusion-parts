import adsk.core

from ..core.command import DialogCommand
from ..core.features import extrude_profile
from ..core.output import add_output_dropdown, resolve_target
from ..core.sketches import add_circle, new_sketch

TEETH_ID = "teeth"
MODULE_ID = "module"
THICKNESS_ID = "thickness"

class SpurGearCommand(DialogCommand):
    cmd_id = "fp_spur_gear_cmd"
    cmd_name = "Spur Gear"
    cmd_tooltip = "Generate a spur gear."

    def build_inputs(self, inputs):
        inputs.addIntegerSpinnerCommandInput(TEETH_ID, "Teeth", 6, 200, 1, 20)
        inputs.addValueInput(
            MODULE_ID, "Module", "mm", adsk.core.ValueInput.createByString("1 mm")
        )
        inputs.addValueInput(
            THICKNESS_ID, "Thickness", "mm", adsk.core.ValueInput.createByString("5 mm")
        )
        add_output_dropdown(inputs)

    def on_execute(self, inputs):
        teeth = inputs.itemById(TEETH_ID).value
        module = inputs.itemById(MODULE_ID).value
        thickness = inputs.itemById(THICKNESS_ID).value

        outer_radius = module * (teeth + 2) / 2

        target = resolve_target(inputs, "Spur Gear")
        sketch = new_sketch(target, name="Gear outline")
        add_circle(sketch, radius=outer_radius)
        extrude_profile(target, sketch.profiles.item(0), thickness)
