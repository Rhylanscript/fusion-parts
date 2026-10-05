from ...core.fusion.command import DialogCommand
from ...core.fusion.features import extrude_profile
from ...core.fusion.output import add_output_dropdown, resolve_target
from ...core.fusion.sketches import draw_bore, draw_segments, largest_profile, new_sketch
from ...core.inputs.bore_inputs import add_bore_inputs, check_bore_fits, read_bore

from .gear_inputs import (
    add_gear_inputs,
    add_thickness_input,
    read_gear_spec,
    read_thickness,
)
from .gear_profile import outline_segments


class SpurGearCommand(DialogCommand):
    cmd_id = "fp_spur_gear_cmd"
    cmd_name = "Spur Gear"
    cmd_tooltip = "Generate a spur gear."

    def build_inputs(self, inputs):
        add_gear_inputs(inputs)
        add_thickness_input(inputs)
        add_bore_inputs(inputs)
        add_output_dropdown(inputs)

    def on_execute(self, inputs):
        spec = read_gear_spec(inputs)
        bore_choice = read_bore(inputs)
        thickness = read_thickness(inputs)
        check_bore_fits(bore_choice, spec.root_radius, "Use more teeth or a larger module.")

        target = resolve_target(inputs, "Spur Gear")
        sketch = new_sketch(target, name="Gear outline")
        draw_segments(sketch, outline_segments(spec))
        draw_bore(sketch, bore_choice)
        extrude_profile(target, largest_profile(sketch), thickness)
