# MAMMOth-commons

[![Integration Tests](https://github.com/mammoth-eu/mammoth-commons/actions/workflows/integration.yml/badge.svg)](https://github.com/mammoth-eu/mammoth-commons/actions/workflows/integration.yml)
![Coverage](./coverage-badge.svg)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](code_of_conduct.md) 

Fast module development for the MAMMOth fairness toolkit.
Modules refer to model loaders, dataset loaders, or metrics.
The library holds common datatypes that are shared between
modules, and automates the integration strategy by only
needing to add a decorator. It also provides integration
tests, as well as a lightweight demonstrator that is a thinned
down version of the toolkit.


## :microscope: Investigate fairness

Instructions to quickly launch and install the demonstrator 
web application locally in your machine:

1. Download this repository.
2. Create a virtual environment. This is optional but recommended.
3. Install dependencies with `pip install -r requirements[test].txt`. This can take a bit of time to download and install everything, but you will be able to run all modules and interface with most popular data types.
4. Launch the local app server with `python demonstrator/app.py` or, if this fails on your platform, with `python -m demonstrator.app` (notice that slash is replaced by a dot and there is no file extension). When everything is ready, this script will also open a browser window to the app's serving page at `http://localhost:5050`.

### IDE settings

<details><summary>VSCode launch profile</summary>  

```json 
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python Debugger: Current File",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "justMyCode": false,
            "cwd": "${workspaceFolder}",
        },
        {
            "name": "Python: Test",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "justMyCode": false,
            "cwd": "${workspaceFolder}",
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            }
        },
        {
            "name": "Demonstrator",
            "type": "debugpy",
            "request": "launch",
            "module": "demonstrator.app",
            "justMyCode": false
        }
    ]
}
``` 
</details>

## :clipboard: Catalogue

Find a catalogue of modules implemented by the MAMMOth consortium
[here](https://mammoth-eu.github.io/mammoth-commons/). 
These modules are implemented in the `catalogue/` directory.
They depend on datatypes found in the main commons library, which
resides under the `mammoth/` directory.

## :thumbsup: Contributing

Instructions on how to add new modules are [here](CONTRIBUTING.md).
Use the GitHub issue tracker to ask questions, request 
features/improvements for the core library or modules, or report bugs.
