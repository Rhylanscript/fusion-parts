import traceback
import adsk.core

from .generators.spur_gear import SpurGearCommand

try:
    import FusionkitRibbonAPI as fusionkit
except ImportError:
    fusionkit = None

PANEL_ID = "fusionparts_panel"

spur_gear = SpurGearCommand()

# pyright: reportAttributeAccessIssue=false

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

        spur_gear.register()

        panel = fusionkit.register_panel(PANEL_ID, "Parts")
        panel.add_button(
            id="fp_spur_gear",
            name="Spur Gear",
            tooltip="Generate a spur gear.",
            icon_path="",  # placeholder until we make icons
            on_execute=spur_gear.open,
        )
    except Exception:
        ui.messageBox("Failed to start:\n" + traceback.format_exc())


def stop(context):
    """Fusion calls this when the add-in stops. Clean up everything we made."""
    if fusionkit is not None:
        fusionkit.unregister_panel(PANEL_ID)
    spur_gear.unregister()
