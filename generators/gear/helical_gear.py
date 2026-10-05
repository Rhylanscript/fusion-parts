from ...core.fusion.bore_cut import cut_bore
from ...core.fusion.command import DialogCommand
from ...core.fusion.output import add_output_dropdown, resolve_target
from ...core.inputs.bore_inputs import add_bore_inputs, check_bore_fits, read_bore

from .gear_inputs import (
    add_gear_inputs,
    add_thickness_input,
    read_gear_spec,
    read_thickness,
)
from .helical_teeth import add_helical_teeth
from .helix_inputs import add_helix_input, read_helix_angle


class HelicalGearCommand(DialogCommand):
    cmd_id = "fp_helical_gear_cmd"
    cmd_name = "Helical Gear"
    cmd_tooltip = "Generate a helical gear."

    def build_inputs(self, inputs):
        add_gear_inputs(inputs)
        add_helix_input(inputs)
        add_thickness_input(inputs)
        add_bore_inputs(inputs)
        add_output_dropdown(inputs)

    def on_execute(self, inputs):
        spec = read_gear_spec(inputs)
        helix_angle = read_helix_angle(inputs)
        thickness = read_thickness(inputs)
        bore_choice = read_bore(inputs)
        check_bore_fits(bore_choice, spec.root_radius, "Use more teeth or a larger module.")

        target = resolve_target(inputs, "Helical Gear")
        body = add_helical_teeth(target, spec, helix_angle, thickness)
        cut_bore(target, bore_choice, thickness, body, "Gear bore")
