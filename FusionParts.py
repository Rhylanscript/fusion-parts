import traceback
import adsk.core

from .core.fusion.icons import icon_folder
from .generators.gear.spur_gear import SpurGearCommand
from .generators.gear.herringbone_gear import HerringboneGearCommand
from .generators.gear.helical_gear import HelicalGearCommand
from .generators.pulley.pulley import PulleyCommand
from .generators.belt.belt import BeltCommand
from .generators.belt.belt_from_circles import BeltFromCirclesCommand

PANEL_ID = "fusionparts_panel"

spur_gear = SpurGearCommand()
helical_gear = HelicalGearCommand()
herringbone_gear = HerringboneGearCommand()
pulley = PulleyCommand()
belt = BeltCommand()
belt_from_circles = BeltFromCirclesCommand()

# pyright: reportAttributeAccessIssue=false

fusionkit = None

_started = False
_startup_handler = None

class _StartupCompletedHandler(adsk.core.ApplicationEventHandler):
    """Fusion calls this once it has finished loading every startup add in"""

    def notify(self, eventArgs):
        _start()

def _load_fusionkit():
    """try to import FusionkitRibbonAPI. Returns True if success"""
    global fusionkit
    try:
        import FusionkitRibbonAPI
    except ImportError:
        return False
    fusionkit = FusionkitRibbonAPI
    return True

def _start():
    """Create the commands and the ribbon buttons (needs FusionkitRibbonAPI)"""
    global _started
    ui = adsk.core.Application.get().userInterface

    try:
        if _started: return
        if not _load_fusionkit():
            ui.messageBox(
                "FusionkitRibbonAPI is not installed.\n"
                "Install it from: https://github.com/rhylanscript/FusionkitRibbonAPI",
                "FusionParts",
            )
            return

        spur_gear.register()
        helical_gear.register()
        herringbone_gear.register()
        pulley.register()
        belt.register()
        belt_from_circles.register()

        panel = fusionkit.register_panel(PANEL_ID, "Parts")
        panel.add_button(
            id="fp_spur_gear",
            name="Spur Gear",
            tooltip="Generate a spur gear.",
            icon_path=icon_folder("spur_gear"),
            on_execute=spur_gear.open,
            promoted=True,
        )
        panel.add_button(
            id="fp_helical_gear",
            name="Helical Gear",
            tooltip="Generate a helical gear.",
            icon_path=icon_folder("helical_gear"),
            on_execute=helical_gear.open,
        )
        panel.add_button(
            id="fp_herringbone_gear",
            name="Herringbone Gear",
            tooltip="Generate a herringbone gear.",
            icon_path=icon_folder("herringbone_gear"),
            on_execute=herringbone_gear.open,
            promoted=True,
        )
        panel.add_button(
            id="fp_pulley",
            name="Timing Pulley",
            tooltip="Generate a timing belt pulley.",
            icon_path=icon_folder("pulley"),
            on_execute=pulley.open,
            promoted=True,
        )
        panel.add_button(
            id="fp_belt",
            name="Timing Belt",
            tooltip="Generate a timing belt around two pulleys",
            icon_path=icon_folder("belt"),
            on_execute=belt.open,
        )
        panel.add_button(
            id="fp_belt_from_circles",
            name="Belt From Surfaces",
            tooltip="Generate a timing belt around two selected circular objects",
            icon_path=icon_folder("belt_from_circles"),
            on_execute=belt_from_circles.open,
        )
        _started = True
    except Exception:
        ui.messageBox("Failed to start:\n" + traceback.format_exc())

def run(context):
    """Fusion calls this when the add in starts"""
    global _startup_handler
    app = adsk.core.Application.get()
    ui = app.userInterface

    try:
        if app.isStartupComplete:
            _start()
        else:
            _startup_handler = _StartupCompletedHandler()
            app.startupCompleted.add(_startup_handler)
    except Exception:
        ui.messageBox("Failed to start:\n" + traceback.format_exc())


def stop(context):
    """Fusion calls this when the add-in stops. Clean up everything we made."""
    global _startup_handler, _started
    app = adsk.core.Application.get()

    if _startup_handler is not None:
        app.startupCompleted.remove(_startup_handler)
        _startup_handler = None

    if fusionkit is not None and _started:
        fusionkit.unregister_panel(PANEL_ID)
    
    spur_gear.unregister()
    helical_gear.unregister()
    herringbone_gear.unregister()
    pulley.unregister()
    belt.unregister()
    belt_from_circles.unregister()

    _started = False
