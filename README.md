
# Franka Emika Panda Demo in Binder

[![Binder](https://binder.intel4coro.de/badge_logo.svg)](https://binder.intel4coro.de/v2/gh/sourinkrpal/my-franka-lab/HEAD)

A minimal Binder-ready demo for running the **Franka Emika Panda** MuJoCo simulation inside a Jupyter Notebook with VNC support.

---

## Quick Start

### Launcher URLs

- **JupyterLab:**  
  https://binder.intel4coro.de/v2/gh/sourinkrpal/my-franka-lab/main?urlpath=lab/tree/notebooks/my_franka.ipynb

- **VS Code:**  
  https://binder.intel4coro.de/v2/gh/sourinkrpal/my-franka-lab/main?urlpath=vscode?folder=/home/jovyan/work

---

## Running the Demo

### 1. Launch the VNC Desktop

Run this cell first:

```python
from scripts.utils import display_desktop
display_desktop()
```
### 2. Start the MuJoCo Franka Demo

```python
from scripts.franka_mujoco_demo import start_demo
start_demo()
```
