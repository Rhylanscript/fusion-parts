import math
import adsk.core

from ..core.app import FusionPartsError
from ..core.bore_inputs import add_bore_inputs, check_bore_fits, read_bore
from ..core.bores import bore_segments
from ..core.command import DialogCommand
from ..core.features import extrude_profile
from ..core.output import add_output_dropdown, resolve_target
from ..core.sketches import draw_segments, largest_profile, new_sketch
from .gear_profile import GearSpec, outline_segments

TEETH_ID = "teeth"
MODULE_ID = "module"
PRESSURE_ANGLE_ID = "pressure_angle"
THICKNESS_ID = "thickness"

MIN_PRESSURE_ANGLE_DEG = 10
MAX_PRESSURE_ANGLE_DEG = 30

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
            PRESSURE_ANGLE_ID,
            "Pressure angle",
            "deg",
            adsk.core.ValueInput.createByString("20 deg"),
        )
        inputs.addValueInput(
            THICKNESS_ID, "Thickness", "mm", adsk.core.ValueInput.createByString("5 mm")
        )
        add_bore_inputs(inputs)
        add_output_dropdown(inputs)

    def on_execute(self, inputs):
        spec = self._read_spec(inputs)
        bore_choice = read_bore(inputs)
        thickness = inputs.itemById(THICKNESS_ID).value
        if thickness <= 0:
            raise FusionPartsError("Thickness must be greater than zero.")
        check_bore_fits(bore_choice, spec.root_radius, "Use more teeth or a larger module.")

        target = resolve_target(inputs, "Spur Gear")
        sketch = new_sketch(target, name="Gear outline")
        draw_segments(sketch, outline_segments(spec))
        if bore_choice is not None:
            bore, clearance = bore_choice
            draw_segments(sketch, bore_segments(bore, clearance))
        extrude_profile(target, largest_profile(sketch), thickness)

    def _read_spec(self, inputs):
        """Read the dialog fields into a GearSpec, checking they make sense."""
        spec = GearSpec(
            teeth=inputs.itemById(TEETH_ID).value,
            module=inputs.itemById(MODULE_ID).value,
            pressure_angle=inputs.itemById(PRESSURE_ANGLE_ID).value,  # radians
        )
        if spec.module <= 0:
            raise FusionPartsError("Module must be greater than zero.")

        low = math.radians(MIN_PRESSURE_ANGLE_DEG)
        high = math.radians(MAX_PRESSURE_ANGLE_DEG)
        if not low <= spec.pressure_angle <= high:
            raise FusionPartsError(
                "Pressure angle must be between %d and %d degrees."
                % (MIN_PRESSURE_ANGLE_DEG, MAX_PRESSURE_ANGLE_DEG)
            )
        return spec
