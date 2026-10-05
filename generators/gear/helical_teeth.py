from ...core.fusion.features import sweep_with_twist
from ...core.fusion.sketches import draw_segments, largest_profile, new_sketch, up_line

from .gear_profile import outline_segments
from .helix import twist_angle


def add_helical_teeth(target, spec, helix_angle, height):
    """Sweep the gear outline up `height` while twisting it. Returns the body.

    The twist is worked out for `height`, so a shorter piece twists less.
    """
    sketch = new_sketch(target, name="Gear outline")
    draw_segments(sketch, outline_segments(spec))
    path = up_line(target, height)
    twist = twist_angle(height, spec.pitch_radius, helix_angle)
    feature = sweep_with_twist(target, largest_profile(sketch), path, twist)
    return feature.bodies.item(0)
