import adsk.core

from .app import FusionPartsError, get_ui, safe_handler

class _CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    """Fusion calls this when the dialog is about to open."""

    def __init__(self, owner):
        super().__init__()
        self._owner = owner

    @safe_handler
    def notify(self, eventArgs):
        self._owner._handle_created(eventArgs.command)

class _CommandExecuteHandler(adsk.core.CommandEventHandler):
    """Fusion calls this when the user clicks OK."""

    def __init__(self, owner):
        super().__init__()
        self._owner = owner

    @safe_handler
    def notify(self, eventArgs):
        self._owner.on_execute(eventArgs.command.commandInputs)

class _InputChangedHandler(adsk.core.InputChangedEventHandler):
    """Fusion calls this whenever the user changes a field in the dialog."""

    def __init__(self, owner):
        super().__init__()
        self._owner = owner

    @safe_handler
    def notify(self, eventArgs):
        self._owner.on_inputs_changed(eventArgs.inputs, eventArgs.input)


class DialogCommand:
    """Base class for a generator that has a Fusion dialog.

    To make a generator, subclass this and fill in:
      cmd_id, cmd_name, cmd_tooltip  (plain text)
      build_inputs(inputs)           (add the dialog fields)
      on_execute(inputs)             (read the fields and build the part)
    """

    cmd_id = ""
    cmd_name = ""
    cmd_tooltip = ""

    def __init__(self):
        self._definition = None
        self._created_handler = None
        # Fusion drops event handlers that Python no longer references,
        # so we keep them in these attributes on purpose.
        self._dialog_handlers = []

    # --- Override these two in each generator -------------------------

    def build_inputs(self, inputs):
        raise NotImplementedError

    def on_execute(self, inputs):
        raise NotImplementedError

    def on_inputs_changed(self, inputs, changed_input):
        """Optional: runs each time a field changes. Does nothing by default."""

    # --- Called from FusionParts.py ---

    def register(self):
        """Create the command. Call once from run()."""
        ui = get_ui()
        old = ui.commandDefinitions.itemById(self.cmd_id)
        if old:
            old.deleteMe()

        self._definition = ui.commandDefinitions.addButtonDefinition(
            self.cmd_id, self.cmd_name, self.cmd_tooltip, ""
        )
        self._created_handler = _CommandCreatedHandler(self)
        self._definition.commandCreated.add(self._created_handler)

    def unregister(self):
        """Remove the command. Call from stop()."""
        if self._definition is not None:
            self._definition.deleteMe()
            self._definition = None

    @safe_handler
    def open(self):
        """Open the dialog. This is what the ribbon button calls."""
        if self._definition is None:
            raise FusionPartsError("Command isn't registered yet. Restart the ad in.")
        self._definition.execute()

    # --- Internal ---

    def _handle_created(self, command):
        self._dialog_handlers = []
        self.build_inputs(command.commandInputs)

        execute_handler = _CommandExecuteHandler(self)
        command.execute.add(execute_handler)
        self._dialog_handlers.append(execute_handler)
        
        changed_handler = _InputChangedHandler(self)
        command.inputChanged.add(changed_handler)
        self._dialog_handlers.append(changed_handler)
