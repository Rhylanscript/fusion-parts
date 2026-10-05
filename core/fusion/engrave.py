import adsk.core

from .features import CUT, extrude_profile
from .sketches import new_sketch

def engrave_text(component, text, height, centre, depth, top, bodies):
    """Cut `text` into the top face of the part. Lengths are Fusion units.

    centre: (x, y) of the middle of the text.
    top:    height of the face being engraved.
    bodies: the bodies the cut may affect.
    """
    sketch = new_sketch(component, name="Engraved text")

    half_width = (len(text) + 1) * height / 2
    half_height = height
    corner = adsk.core.Point3D.create(centre[0] - half_width, centre[1] - half_height, 0)
    diagonal = adsk.core.Point3D.create(centre[0] + half_width, centre[1] + half_height, 0)

    texts = sketch.sketchTexts
    text_input = texts.createInput3(
        "'%s'" % text, adsk.core.ValueInput.createByReal(height)
    )
    text_input.setAsMultiLine(
        corner,
        diagonal,
        adsk.core.HorizontalAlignments.CenterHorizontalAlignment,
        adsk.core.VerticalAlignments.MiddleVerticalAlignment,
        0,
    )
    sketch_text = texts.add(text_input)

    extrude_profile(
        component, sketch_text, 2 * depth, CUT,
        start_offset=top - depth, participants=bodies,
    )
