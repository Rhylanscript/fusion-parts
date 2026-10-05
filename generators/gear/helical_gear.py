import math

import adsk.core

from ...core.fusion.app import FusionPartsError
from ...core.fusion.bore_cut import cut_bore
from ...core.fusion.command import DialogCommand
from ...core.fusion.features import sweep_with_twist
from ...core.fusion.output import add_output_dropdown, resolve_target
from ...core.fusion.sketches import draw_segments, largest_profile, new_sketch, up_line
from ...core.inputs.bore_inputs import add_bore_inputs, check_bore_fits, read_bore

from .gear_inputs import (
    add_gear_inputs,
    add_thickness_input,
    read_gear_spec,
    read_thickness,
)
from .gear_profile import outline_segments
from .helix import twist_angle

HELIX_ID = "helix_angle"

MIN_HELIX_ANGLE_DEG = 1
MAX_HELIX_ANGLE_DEG = 45


class HelicalGearCommand(DialogCommand):
    cmd_id = "fp_helical_gear_cmd"
    cmd_name = "Helical Gear"
    cmd_tooltip = "Generate a helical gear."

    def build_inputs(self, inputs):
        add_gear_inputs(inputs)
        helix = inputs.addValueInput(
            HELIX_ID, "Helix angle", "deg", adsk.core.ValueInput.createByString("20 deg")
        )
        helix.tooltip = "How steeply the teeth lean. Module and pressure angle are measured on the flat face of the gear."
        add_thickness_input(inputs)
        add_bore_inputs(inputs)
        add_output_dropdown(inputs)

    def on_execute(self, inputs):
        spec = read_gear_spec(inputs)
        helix_angle = self._read_helix_angle(inputs)
        thickness = read_thickness(inputs)
        bore_choice = read_bore(inputs)
        check_bore_fits(bore_choice, spec.root_radius, "Use more teeth or a larger module.")

        target = resolve_target(inputs, "Helical Gear")
        body = self._add_teeth(target, spec, helix_angle, thickness)
        cut_bore(target, bore_choice, thickness, body, "Gear bore")

    def _read_helix_angle(self, inputs):
        """Read the helix angle (radians), checking it makes sense."""
        angle = inputs.itemById(HELIX_ID).value
        low = math.radians(MIN_HELIX_ANGLE_DEG)
        high = math.radians(MAX_HELIX_ANGLE_DEG)
        if not low <= angle <= high:
            raise FusionPartsError(
                "Helix angle must be between %d and %d degrees."
                % (MIN_HELIX_ANGLE_DEG, MAX_HELIX_ANGLE_DEG)
            )
        return angle

    def _add_teeth(self, target, spec, helix_angle, thickness):
        """Sweep the gear outline up a straight line while twisting it. Returns the body."""
        sketch = new_sketch(target, name="Gear outline")
        draw_segments(sketch, outline_segments(spec))
        path = up_line(target, thickness)
        twist = twist_angle(thickness, spec.pitch_radius, helix_angle)
        feature = sweep_with_twist(target, largest_profile(sketch), path, twist)
        return feature.bodies.item(0)
