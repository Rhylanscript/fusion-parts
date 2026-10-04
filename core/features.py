import adsk.core
import adsk.fusion

NEW_BODY = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
JOIN = adsk.fusion.FeatureOperations.JoinFeatureOperation
CUT = adsk.fusion.FeatureOperations.CutFeatureOperation

def extrude_profile(component, profile, distance, operation=NEW_BODY, start_offset=0.0):
    """Extrude `profile` upward by `distance` and return the feature.

    `distance` and `start_offset` are in Fusion units (use mm()).
    `start_offset` lifts the starting face above the sketch plane, so one
    sketch on the XY plane can make pieces stacked at different heights.
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
    return extrudes.add(extrude_input)
