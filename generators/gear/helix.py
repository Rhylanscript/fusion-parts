import math

def twist_angle(thickness, pitch_radius, helix_angle):
    """How far the gear outline must rotate over its full thickness (radians).

    thickness:      gear thickness. Any unit, as long as it matches pitch_radius.
    pitch_radius:   radius of the gear's pitch circle, same unit as thickness.
    helix_angle:    how steeply the teeth lean, in radians. 0 means a spur gear.
    """
    return thickness * math.tan(helix_angle) / pitch_radius
