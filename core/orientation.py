import adsk.core


def _is_y_up():
    """True when new designs use Y as the up axis

    Fusion doesn't let addins ask a design which way is up, so read the
    users "default modeling orientation" preference instead, tHat preference
    decides the up axis of every new design
    """
    preferences = adsk.core.Application.get().preferences.generalPreferences
    return (
        preferences.defaultModelingOrientation
        == adsk.core.DefaultModelingOrientations.YUpModelingOrientation
    )


def ground_plane(component):
    """The flat plane parts are drawn on, so they lie flat for printing"""
    if _is_y_up():
        return component.xZConstructionPlane
    return component.xYConstructionPlane


def up_axis(component):
    """The construction axis that points straight up from the ground plane"""
    if _is_y_up():
        return component.yConstructionAxis
    return component.zConstructionAxis


def side_plane(component):
    """An upright plane that contains the up axis (used to draw side profiles)"""
    if _is_y_up():
        return component.xYConstructionPlane
    return component.xZConstructionPlane


def up_point(radius, height):
    """Model space (x, y, z) of a point `radius` along X and `height` up"""
    if _is_y_up():
        return (radius, height, 0.0)
    return (radius, 0.0, height)
