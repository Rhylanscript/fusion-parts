import math

from FusionParts.generators.gear.helix import twist_angle

def test_no_helix_angle_means_no_twist():
    assert twist_angle(5.0, 10.0, 0.0) == 0.0

def test_forty_five_degrees_twists_one_radian_when_thickness_equals_radius():
    assert math.isclose(twist_angle(10.0, 10.0, math.radians(45)), 1.0)

def test_twice_as_thick_twists_twice_as_much():
    thin = twist_angle(5.0, 10.0, math.radians(20))
    thick = twist_angle(10.0, 10.0, math.radians(20))
    assert math.isclose(thick, 2 * thin)
