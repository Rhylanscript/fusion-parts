import traceback
import adsk.core

try:
    import FusionkitRibbonAPI as fusionkit
except ImportError:
    fusionkit = None

PANEL_ID = "fusionkit_tools_panel"


def run(context):
    """Fusion calls this when the add in starts"""
    app = adsk.core.Application.get()
    ui = app.userInterface

    try:
        if fusionkit is None:
            ui.messageBox(
                "FusionkitRibbonAPI is not installed.\n"
                "Install it from: https://github.com/rhylanscript/FusionkitRibbonAPI",
                "FusionParts",
            )
            return

        panel = fusionkit.register_panel(PANEL_ID, "Generators")  # type: ignore[attr-defined]
        panel.add_button(
            id="fkt_hello",
            name="Hello",
            tooltip="test button to confirm addin loads.",
            icon_path="",  # placeholder
            on_execute=_on_hello,
        )
    except Exception:
        ui.messageBox("Failed to start:\n" + traceback.format_exc())

def stop(context):
    """Fusion calls this when the add in stops. Clean up everything we made."""
    if fusionkit is not None:
        fusionkit.unregister_panel(PANEL_ID)  # type: ignore[attr-defined]

def _on_hello():
    ui = adsk.core.Application.get().userInterface
    ui.messageBox("FusionParts is alive!")
