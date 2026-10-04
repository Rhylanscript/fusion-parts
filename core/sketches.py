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

def draw_segments(sketch, segments):
    """Draw a list of ("line" / "arc" / "spline", ...) pieces into a sketch.

    See outline_segments() in generators/gear_profile.py for the format.
    """
    curves = sketch.sketchCurves
    sketch.isComputeDeferred = True
    
    try:
        for segment in segments:
            kind = segment[0]
            if kind == "line":
                _, start, end = segment
                curves.sketchLines.addByTwoPoints(_to_point(start), _to_point(end))
            elif kind == "arc":
                _, start, middle, end = segment
                curves.sketchArcs.addByThreePoints(
                    _to_point(start), _to_point(middle), _to_point(end)
                )
            elif kind == "spline":
                _, points = segment
                collection = adsk.core.ObjectCollection.create()
                for point in points:
                    collection.add(_to_point(point))
                curves.sketchFittedSplines.add(collection)
            else:
                raise ValueError("Unknown segment type: " + str(kind))
    finally:
        sketch.isComputeDeferred = False

def _to_point(xy):
    """Turn an (x, y) tuple into a Fusion Point3D."""
    return adsk.core.Point3D.create(xy[0], xy[1], 0)
