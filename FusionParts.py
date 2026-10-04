import traceback
import adsk.core

from .generators import test_cylinder

try:
    import FusionkitRibbonAPI as fusionkit
except ImportError:
    fusionkit = None

PANEL_ID = "fusionparts_panel"

def run(context):
    """Fusion calls this when the add-in starts."""
    ui = adsk.core.Application.get().userInterface

    try:
        if fusionkit is None:
            ui.messageBox(
                "FusionkitRibbonAPI is not installed.\n"
                "Install it from: https://github.com/rhylanscript/FusionkitRibbonAPI",
                "FusionParts",
            )
            return

        panel = fusionkit.register_panel(PANEL_ID, "Parts")
        panel.add_button(
            id="fp_test_cylinder",
            name="Test Cylinder",
            tooltip="Creates a test cylinder to confirm the core helpers work.",
            icon_path="",  # placeholder
            on_execute=test_cylinder.run,
        )
    except Exception:
        ui.messageBox("Failed to start:\n" + traceback.format_exc())


def stop(context):
    """Fusion calls this when the add-in stops. Clean up everything we made."""
    if fusionkit is not None:
        fusionkit.unregister_panel(PANEL_ID)
