import math

import adsk.core
import adsk.fusion

NEW_BODY = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
JOIN = adsk.fusion.FeatureOperations.JoinFeatureOperation
CUT = adsk.fusion.FeatureOperations.CutFeatureOperation

def extrude_profile(
    component,
    profile,
    distance,
    operation=NEW_BODY,
    start_offset=0.0,
    participants=None,
):
    """Extrude `profile` upward by `distance` and return the feature.

    `profile` is a sketch profile or a SketchText. `distance` and
    `start_offset` are in Fusion units (use mm()). `start_offset` lifts the
    starting face above the sketch plane, so one sketch on the XY plane can
    make pieces at different heights.

    `participants` is a list of bodies a CUT is allowed to affect. Without
    it, a cut affects every body it touches.
    """
    extrudes = component.features.extrudeFeatures
    extrude_input = extrudes.createInput(profile, operation)

    extent = adsk.fusion.DistanceExtentDefinition.create(
        adsk.core.ValueInput.createByReal(distance)
    )
    extrude_input.setOneSideExtent(
        extent, adsk.fusion.ExtentDirections.PositiveExtentDirection
    )
    if start_offset != 0:
        extrude_input.startExtent = adsk.fusion.OffsetStartDefinition.create(
            adsk.core.ValueInput.createByReal(start_offset)
        )
    if participants:
        extrude_input.participantBodies = participants
    return extrudes.add(extrude_input)

def revolve_profile(component, profile, axis, operation=NEW_BODY):
    """Spin `profile` a full turn around `axis` and return the feature."""
    revolves = component.features.revolveFeatures
    revolve_input = revolves.createInput(profile, axis, operation)
    revolve_input.setAngleExtent(
        False, adsk.core.ValueInput.createByReal(2 * math.pi)
    )
    return revolves.add(revolve_input)

def sweep_with_twist(component, profile, path_line, twist, operation=NEW_BODY):
    """drag `profile` along `path_line` while rotating it by `twist` rad

    `path_line` is a sketch line (see up_line() in sketches.py). The profile
    turns gradually, so by the end of the path it has rotated by `twist`
    in total. returns the feature.
    """
    path = component.features.createPath(path_line)
    sweeps = component.features.sweepFeatures
    sweep_input = sweeps.createInput(profile, path, operation)
    sweep_input.twistAngle = adsk.core.ValueInput.createByReal(twist)
    return sweeps.add(sweep_input)

def mirror_join(component, body, plane):
    """Mirror `body` across `plane` and join the copy onto it, returns `body`

    The mirrored copy touches the original along the plane, so the two end
    up as one solid
    """
    originals = adsk.core.ObjectCollection.create()
    originals.add(body)
    mirrors = component.features.mirrorFeatures
    mirror = mirrors.add(mirrors.createInput(originals, plane))

    copies = adsk.core.ObjectCollection.create()
    copies.add(mirror.bodies.item(0))
    combines = component.features.combineFeatures
    combine_input = combines.createInput(body, copies)
    combine_input.operation = JOIN
    combines.add(combine_input)
    return body
