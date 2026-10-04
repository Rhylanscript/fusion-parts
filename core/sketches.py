import adsk.core
import adsk.fusion

from .bores import bore_segments

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

def largest_profile(sketch):
    """Return the profile with the biggest area.

    When a sketch has a shape with a hole in it, Fusion finds two profiles:
    the shape with a hole, and the holes own area. The largest is the one we
    want to extrude.
    """
    accuracy = adsk.fusion.CalculationAccuracy.LowCalculationAccuracy
    best = None
    best_area = 0.0
    for index in range(sketch.profiles.count):
        profile = sketch.profiles.item(index)
        area = profile.areaProperties(accuracy).area
        if area > best_area:
            best = profile
            best_area = area
    return best

def draw_bore(sketch, bore_choice):
    """Draw the shaft bore into `sketch`. Does nothing when there is no bore."""
    if bore_choice is None:
        return
    bore, clearance = bore_choice
    draw_segments(sketch, bore_segments(bore, clearance))

def polygon_segments(points):
    """Turn corner points into closed ("line", start, end) pieces for draw_segments()."""
    return [
        ("line", points[index], points[(index + 1) % len(points)])
        for index in range(len(points))
    ]

def model_to_sketch(sketch, x, y, z):
    """Return the sketch (u, v) position of a model-space point on the sketch plane.

    Sketch axes don't always line up with the model's axes (on the XZ plane,
    sketch "up" can be model -Z). So we ask Fusion where the sketch's own
    axes point and measure along them.
    """
    to_model = sketch.sketchToModelSpace
    origin = to_model(adsk.core.Point3D.create(0, 0, 0))
    u_axis = origin.vectorTo(to_model(adsk.core.Point3D.create(1, 0, 0)))
    v_axis = origin.vectorTo(to_model(adsk.core.Point3D.create(0, 1, 0)))
    offset = origin.vectorTo(adsk.core.Point3D.create(x, y, z))
    return (offset.dotProduct(u_axis), offset.dotProduct(v_axis))

def ring_profile(sketch):
    """Return the profile that has a hole in it, or None if there isn't one.

    A belt is a thin ring, so the empty space inside it has MORE area than
    the ring itself. largest_profile() would pick the empty space. Instead we
    look for the profile made of two loops: an outer edge and an inner edge.
    """
    for index in range(sketch.profiles.count):
        profile = sketch.profiles.item(index)
        if profile.profileLoops.count == 2:
            return profile
    return None
