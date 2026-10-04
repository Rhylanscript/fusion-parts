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
