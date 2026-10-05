from ...core.fusion.bore_cut import cut_bore
from ...core.fusion.command import DialogCommand
from ...core.fusion.features import mirror_join
from ...core.fusion.orientation import offset_ground_plane
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

class HerringboneGearCommand(DialogCommand):
    cmd_id = "fp_herringbone_gear_cmd"
    cmd_name = "Herringbone Gear"
    cmd_tooltip = "Generate a herringbone (double helical) gear."

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

        target = resolve_target(inputs, "Herringbone Gear")
        half = thickness / 2
        body = add_helical_teeth(target, spec, helix_angle, half)
        mirror_join(target, body, offset_ground_plane(target, half))
        cut_bore(target, bore_choice, thickness, body, "Gear bore")
