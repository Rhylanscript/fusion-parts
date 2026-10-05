import traceback
import adsk.core

from .core.fusion.icons import icon_folder
from .generators.gear.spur_gear import SpurGearCommand
from .generators.gear.helical_gear import HelicalGearCommand
from .generators.pulley.pulley import PulleyCommand
from .generators.belt.belt import BeltCommand

try:
    import FusionkitRibbonAPI as fusionkit
except ImportError:
    fusionkit = None

PANEL_ID = "fusionparts_panel"

spur_gear = SpurGearCommand()
helical_gear = HelicalGearCommand()
pulley = PulleyCommand()
belt = BeltCommand()

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
        helical_gear.register()
        pulley.register()
        belt.register()

        panel = fusionkit.register_panel(PANEL_ID, "Parts")
        panel.add_button(
            id="fp_spur_gear",
            name="Spur Gear",
            tooltip="Generate a spur gear.",
            icon_path=icon_folder("spur_gear"),
            on_execute=spur_gear.open,
        )
        panel.add_button(
            id="fp_helical_gear",
            name="Helical Gear",
            tooltip="Generate a helical gear.",
            icon_path=icon_folder("helical_gear"),
            on_execute=helical_gear.open,
        )
        panel.add_button(
            id="fp_pulley",
            name="Timing Pulley",
            tooltip="Generate a timing belt pulley.",
            icon_path=icon_folder("pulley"),
            on_execute=pulley.open,
        )
        panel.add_button(
            id="fp_belt",
            name="Timing Belt",
            tooltip="Generate a timing belt around two pulleys",
            icon_path=icon_folder("belt"),
            on_execute=belt.open,
        )
    except Exception:
        ui.messageBox("Failed to start:\n" + traceback.format_exc())


def stop(context):
    """Fusion calls this when the add-in stops. Clean up everything we made."""
    if fusionkit is not None:
        fusionkit.unregister_panel(PANEL_ID)
    spur_gear.unregister()
    helical_gear.unregister()
    pulley.unregister()
    belt.unregister()
