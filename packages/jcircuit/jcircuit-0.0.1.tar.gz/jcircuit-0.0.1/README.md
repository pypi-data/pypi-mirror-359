# jcircuit: Jupyter Circuit Designer

Jupyter Notebook widget for creating and exporting quantum circuits using the [QuCAT Circuit generator](https://github.com/qucat/gui-circuit-generator). Built with [AnyWidget](https://anywidget.dev/) and [esbuild](https://esbuild.github.io/).

# Users' Documentation

You can install jcircuit with pip:
```bash
pip install jcircuit
```
Open a Jupyter Notebook and run:
```python
from jcircuit import JCircuitWidget

my_widget = JCircuitWidget()
my_widget
```
Once you have created your QuCAT circuit, you can click on the `Export circuit` button. Only then can you view the netlist elements in the Jupyter Notebook with:
```python
my_widget.circuitElements
```
See `example.ipynb`.

# Developers' Documentation

## Overview
This Python Jupyter Notebook widget is built with `AnyWidget` and uses `esbuild` to bundle the JavaScript code.

You can change the QuCAT Circuit Generator version in the `dependencies` section of `package.json`. This file defines the npm dependencies and the build scripts needed for the JavaScript code.

The JavaScript code is in `src/widget.js`. This has to be kept in sync with `gui-circuit-generator/src/gui/main.js` and just enough of `gui-circuit-generator/src/gui/gui.html`, converted to JavaScript.

You can change the (Test)PyPI version number in `pyproject.toml`. This file defines the Python package metadata and dependencies.

The Python code is in `jcircuit/__init__.py`. The building process creates a `jcircuit/static` directory with the bundled JavaScript code and other static files needed for the widget.

The `environment.yml` file defines the conda environment with the necessary dependencies for development.

## Conda Environment
You can create a conda environment with:
```bash
conda env create -y -f environment.yml
```
Activate the environment with:
```bash
conda activate jcircuit
```

## Javascript part
You can create and activate an npm environment with:
```bash
nodeenv node_env
# source node_env/bin/activate  # linux
# Windows is more complicated, but these 2 lines should work:
export NODE_VIRTUAL_ENV=${PWD}/node_env
export PATH=${NODE_VIRTUAL_ENV}/Scripts:${PATH}
```
Install the npm dependencies with:
```bash
npm install
```
Build the Javascript module with:
```bash
npm run build
```

## Python part
Build the Python package with:
```bash
python -m build
```
Upload to TestPyPI with:
```bash
python -m twine upload --repository testpypi dist/*
```
Upload to PyPI (production) with:
```bash
python -m twine upload dist/*
```
