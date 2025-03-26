# MAI-BIAS modules

[![Integration Tests](https://github.com/mammoth-eu/mammoth-commons/actions/workflows/integration.yml/badge.svg)](https://github.com/mammoth-eu/mammoth-commons/actions/workflows/integration.yml)
![Coverage](./coverage-badge.svg)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](code_of_conduct.md) 

*Quickly develop and locally run MAI-BIAS toolkit modules.*

This repository holds the mammoth-commons library, which contains 
supporting datatypes and decorators for developing fairness modules.
It also hosts a catalogue of 20+ modules. 
Finally, find desktop and terminal applications that 
run those modules in your local machine.

![logo](mai_bias/logo.png)

## 🔬 Run locally

1. Make **sure** you are on Python 3.12.
2. Install the *mai-bias* package. This will take time due to supporting many AI tools.
3. Launch the desktop app.

```bash
# may need to replace python with python3
python --version
pip install mai-bias
python -m mai_bias.app
```

<details><summary>Ubuntu: Example of full installation pipeline</summary>

```bash
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.12
sudo apt install python3.12-pip
sudo apt install python3.12-venv
python3 -m venv venv
source venv/bin/activate
python3 install mai-bias
python3 -m mai_bias.app
```
</details>

<details><summary>Windows: WSL missing .so files</summary>
    
If you are in WSL, you are likely to get errors like this *ImportError: libGL.so.1: cannot open shared object file: No such file or directory*.
This is due to the lack of a graphical environment. Install one like like below, including missing font symbols needed to properly display certain UI element.

```bash
sudo apt update
sudo apt install fonts-noto-color-emoji fonts-symbola
sudo apt install libgl1
sudo apt install libxkbcommon-x11-0
sudo apt install libegl1
sudo apt install libnss3
sudo apt install libxcomposite1
sudo apt install libxdamage1
sudo apt install libxrender1
sudo apt install libxrandr2
sudo apt install libxtst6
sudo apt install libxi6
sudo apt install libasound2
sudo apt install libxkbfile-dev
sudo apt install --reinstall qt6-wayland libxcb-cursor0 libxkbcommon-x11-0
sudo apt install libx11-xcb1 libxcb-xinerama0 libxcb-cursor0
```

</details>

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


## 🖥️ Run in terminal

Follow the previous instructions, with the difference that the command line interface
module is launched at the last step per `python -m mai_bias.cli`. This has equivalent
functionality to the desktop app but does not leave the terminal.

![Terminal demo](docs/terminal_demo.gif)
 
## ☁️ [Deploy in a server](https://github.com/mammoth-eu/mammoth-toolkit-releases)

## 🦣 [Module catalogue](https://mammoth-eu.github.io/mammoth-commons/)

## 👍 [Contribute](CONTRIBUTING.md)
