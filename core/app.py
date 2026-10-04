import functools
import traceback

import adsk.core
import adsk.fusion


class FusionPartsError(Exception):
    """An error we expect might happen, with a message meant for the user."""


def get_ui():
    """Return Fusions ui object (used to show message boxes)"""
    return adsk.core.Application.get().userInterface


def get_design():
    """Return the design the user currently has open.

    Raises FusionPartsError if the user isn't in a Design (for example,
    if they're in a Drawing or have no document open).
    """
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    if design is None:
        raise FusionPartsError(
            "Please open a Design (Model workspace) before using this tool."
        )
    return design


def safe_handler(func):
    """Decorator: wrap a function so errors show a message box"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FusionPartsError as error:
            get_ui().messageBox(str(error), "FusionParts")
        except Exception:
            get_ui().messageBox(
                "Unexpected error:\n" + traceback.format_exc(), "FusionParts"
            )

    return wrapper
