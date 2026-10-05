from ..shapes.units import mm

from .features import CUT, extrude_profile
from .sketches import draw_bore, largest_profile, new_sketch

BORE_OVERSHOOT = mm(1.0)


def cut_bore(component, bore_choice, height, body, name="Bore"):
    """Cut the shaft bore straight through `body`. Does nothing for no bore.

    `height` (Fusion units) is the full height of the part, measured up from
    the ground plane. Only `body` is cut, so other bodies are left alone.
    """
    if bore_choice is None:
        return
    sketch = new_sketch(component, name=name)
    draw_bore(sketch, bore_choice)
    extrude_profile(
        component,
        largest_profile(sketch),
        height + 2 * BORE_OVERSHOOT,
        CUT,
        start_offset=-BORE_OVERSHOOT,
        participants=[body],
    )
