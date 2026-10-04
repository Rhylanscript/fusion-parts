import adsk.core
import adsk.fusion

NEW_BODY = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
JOIN = adsk.fusion.FeatureOperations.JoinFeatureOperation
CUT = adsk.fusion.FeatureOperations.CutFeatureOperation

def extrude_profile(component, profile, distance, operation=NEW_BODY):
    """Extrude `profile` by `distance` (Fusion units, use mm()) and return the feature."""
    extrudes = component.features.extrudeFeatures
    extrude_input = extrudes.createInput(profile, operation)
    extrude_input.setDistanceExtent(
        False, adsk.core.ValueInput.createByReal(distance)
    )
    return extrudes.add(extrude_input)
