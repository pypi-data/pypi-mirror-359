import { Circuit } from '../node_modules/gui-circuit-generator/src/domain/aggregates/Circuit.js';
import { CircuitService } from '../node_modules/gui-circuit-generator/src/application/CircuitService.js';
import { GUIAdapter } from '../node_modules/gui-circuit-generator/src/gui/adapters/GUIAdapter.js';

import {
  ElementRegistry,
  rendererFactory,
  GUICommandRegistry,
  setupCommands
} from "../node_modules/gui-circuit-generator/src/config/settings.js";


function render({ model, el }) {
    let resistorButton = document.createElement("button");
    resistorButton.id = "addResistor";
    resistorButton.textContent = "Add Resistor";
    let wireButton = document.createElement("button");
    wireButton.id = "addWire";
    wireButton.textContent = "Add Wire";
    let exportButton = document.createElement("button");
    exportButton.id = "export";
    exportButton.textContent = "Export circuit";
    let canvas = document.createElement("canvas");
    canvas.id = 'circuitCanvas';
    canvas.width = 800;
    canvas.height = 600;
    canvas.style.border = '1px solid black';

    let controls = document.createElement("div");
    controls.className = "controls";
    controls.appendChild(resistorButton);
    controls.appendChild(wireButton);
    controls.appendChild(exportButton);

    el.appendChild(controls);
    el.appendChild(canvas);

    // Set up the circuit and services
    const circuit = new Circuit();
    const circuitService = new CircuitService(circuit, ElementRegistry);

    const guiAdapter = new GUIAdapter(controls, canvas, circuitService, ElementRegistry, rendererFactory, GUICommandRegistry);

    // Wait for commands to be set up
    setupCommands(circuitService, guiAdapter.circuitRenderer).then(() => {
        guiAdapter.initialize();
    });

    // Export button event handler
    
    model.set("exportTrigger", 0);
    exportButton.addEventListener('click', () => {
        model.set("circuitElements", circuitService.getElements());
        model.set("exportTrigger", model.get("exportTrigger") + 1);
        model.save_changes();
    });

}

export default { render };
