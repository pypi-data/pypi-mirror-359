import importlib.metadata
import pathlib

import anywidget
import traitlets
import json

try:
    __version__ = importlib.metadata.version("trial_jcircuit_widget")
except importlib.metadata.PackageNotFoundError:
    __version__ = "unknown"


class JCircuitWidget(anywidget.AnyWidget):

    _esm = pathlib.Path(__file__).parent / "static" / "widget.js"
    # _css = pathlib.Path(__file__).parent / "static" / "gui.css"
    _css = """
    .controls button { margin-top: 10px; }
    """
    circuitElements = traitlets.List().tag(sync=True)
    exportTrigger = traitlets.Int(0).tag(sync=True)

    def on_export_triggered(self, change):
        """
        This function is triggered whenever `exportTrigger` changes
        (i.e., whenever the front-end button is pressed).
        """
        # Grab the new exportTrigger value
        # (though we rarely need it if we’re just saving circuitElements)
        new_trigger_value = change["new"]
        print(f"Export trigger observed; new value is {new_trigger_value}")

        # Now read the current circuit data from the widget trait
        circuit_data = change["owner"].circuitElements

        # Write it to a file or handle however you want
        with open("exported_circuit.json", "w") as f:
            json.dump(circuit_data, f, indent=4)
        print("Wrote exported_circuit.json")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.observe(self.on_export_triggered, "exportTrigger")
