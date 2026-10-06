import adsk.core


def plane_through(component, origin, normal):
    """Make a hidden construction plane through `origin`, facing along `normal`.

    `origin` and `normal` are (x, y, z) tuples in model space. Sketches drawn
    on this plane extrude along `normal`
    """
    geometry = adsk.core.Plane.create(
        adsk.core.Point3D.create(*origin),
        adsk.core.Vector3D.create(*normal),
    )
    planes = component.constructionPlanes
    plane_input = planes.createInput()
    plane_input.setByPlane(geometry)
    plane = planes.add(plane_input)
    plane.isLightBulbOn = False
    return plane
