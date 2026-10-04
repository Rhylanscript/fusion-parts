import adsk.core

def new_sketch(component, plane=None, name=None):
    """Create a sketch in `component`. Defaults to the XY (top) plane."""
    if plane is None:
        plane = component.xYConstructionPlane
    sketch = component.sketches.add(plane)
    if name:
        sketch.name = name
    return sketch

def add_circle(sketch, radius, center=(0.0, 0.0)):
    """Draw a circle. `radius` and `center` are in Fusion units (use mm())."""
    center_point = adsk.core.Point3D.create(center[0], center[1], 0)
    return sketch.sketchCurves.sketchCircles.addByCenterRadius(center_point, radius)
