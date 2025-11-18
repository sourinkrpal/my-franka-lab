import os
import time
import threading
import numpy as np
import mujoco
import mujoco.viewer
from ipywidgets import Button, HBox, Output
from IPython.display import display

# -------------------------
# Load robot
# -------------------------
robot = "franka_emika_panda"
XML_PATH = f"{os.getcwd()}/mujoco_menagerie/{robot}/scene.xml"
m = mujoco.MjModel.from_xml_path(XML_PATH)
d = mujoco.MjData(m)

# -------------------------
# Shared control flag
# -------------------------
running = False
viewer_thread = None

# -------------------------
# Simulation function
# -------------------------
def run_sim():
    global running
    with mujoco.viewer.launch_passive(
        m, d,
        show_left_ui=False,
        show_right_ui=False,
    ) as viewer:

        # Remove shadows, reflections, contact points
        with viewer.lock():
            viewer.user_scn.flags[mujoco.mjtRndFlag.mjRND_SHADOW] = 0
            viewer.user_scn.flags[mujoco.mjtRndFlag.mjRND_REFLECTION] = 0
            viewer.opt.flags[mujoco.mjtVisFlag.mjVIS_CONTACTPOINT] = 0

        viewer.sync()

        while running and viewer.is_running():
            step_start = time.time()
            # Random actuator control
            ctrl_range = m.actuator_ctrlrange
            d.ctrl = np.random.uniform(ctrl_range[:,0], ctrl_range[:,1])
            mujoco.mj_step(m, d)
            viewer.sync()

            # real-time pacing
            dt = m.opt.timestep - (time.time() - step_start)
            if dt > 0:
                time.sleep(dt)

    running = False


# -------------------------
# Handlers for buttons
# -------------------------
def start_clicked(b, out):
    global running, viewer_thread
    if running:
        out.append_stdout("Simulation already running.\n")
        return
    out.append_stdout("Starting simulation...\n")
    running = True
    viewer_thread = threading.Thread(target=run_sim, daemon=True)
    viewer_thread.start()


def stop_clicked(b, out):
    global running
    if running:
        out.append_stdout("Stopping simulation...\n")
        running = False
    else:
        out.append_stdout("Simulation already stopped.\n")


# -------------------------
# Public function to launch UI
# -------------------------
def start_demo():
    out = Output()

    start_button = Button(description="Start Simulation", button_style="success")
    stop_button = Button(description="Stop Simulation", button_style="danger")

    start_button.on_click(lambda b: start_clicked(b, out))
    stop_button.on_click(lambda b: stop_clicked(b, out))

    display(HBox([start_button, stop_button]))
    display(out)