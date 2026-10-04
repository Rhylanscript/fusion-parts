from ..core.app import safe_handler
from ..core.components import new_component
from ..core.features import extrude_profile
from ..core.sketches import add_circle, new_sketch
from ..core.units import mm

@safe_handler
def run():
    """Make a cylinder: 20 mm wide, 20 mm tall."""
    component = new_component("Test Cylinder")
    sketch = new_sketch(component, name="Base circle")
    add_circle(sketch, radius=mm(10))
    profile = sketch.profiles.item(0)
    extrude_profile(component, profile, distance=mm(20))
