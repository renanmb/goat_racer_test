from isaacsim import SimulationApp

# Start the application
simulation_app = SimulationApp({"headless": False})

# # Get the utility to enable extensions
from isaacsim.core.utils.extensions import enable_extension

# for some reason it cannot find the extension by its name
enable_extension("leatherback.example.ackermann")

# simulation_app.update()

import carb
import numpy as np
import omni.appwindow  # Contains handle to keyboard
from isaacsim.core.api import World
from isaacsim.core.utils.prims import define_prim, get_prim_at_path
from isaacsim.storage.native import get_assets_root_path
from isaacsim.core.api.objects import VisualSphere

# from leatherback.example.ackermann.leatherback import LeatherbackPolicy
from goatracer.one.interactive.leatherback import LeatherbackPolicy

import os
import omni.usd
from pxr import UsdLux, Sdf, Gf

script_dir = os.path.dirname(__file__)
relative_path = os.path.join("..", "assets")
full_path = os.path.abspath(os.path.join(script_dir, relative_path))
usd_path = os.path.abspath(os.path.join(full_path, "leatherback_simple_better.usd"))

first_step = True
reset_needed = False

def is_goal_reached(current_position, command, tolerance=0.15):
    """
    Checks if a current XYZ position is within a specified tolerance of a target XYZ position.

    Args:
        current_position (np.ndarray): A 1D NumPy array representing the current XYZ coordinates (e.g., [x, y, z]).
        command (np.ndarray): A 1D NumPy array representing the target XYZ coordinates.
        tolerance (float, optional): The maximum allowed difference between the current and target coordinates
                                    for them to be considered "reached". Defaults to 0.01.

    Returns:
        bool: True if the current_position is within the tolerance of the command position, False otherwise.
    """
    return np.all(np.isclose(current_position, command, atol=tolerance))

# initialize robot on first step, run robot advance
def on_physics_step(step_size) -> None:
    global first_step
    global reset_needed
    if first_step:
        leatherback.robot.initialize()
        first_step = False
    elif reset_needed:
        my_world.reset(True)
        reset_needed = False
        first_step = True
    else:
        # print(f"Current base command:{base_command}")
        leatherback.forward(step_size, base_command)
        VisualSphere(
            prim_path="/new_sphere_2",
            name="sphere_1",
            position=base_command,
            radius = 0.1,
            color=np.array([255, 0, 0]),
            )


# spawn world
my_world = World(stage_units_in_meters=1.0, physics_dt=1 / 60, rendering_dt=1 / 50)
assets_root_path = get_assets_root_path()
if assets_root_path is None:
    carb.log_error("Could not find Isaac Sim assets folder")

# spawn warehouse scene
prim = define_prim("/World/Ground", "Xform")
asset_path = assets_root_path + "/Isaac/Environments/Grid/default_environment.usd"
prim.GetReferences().AddReference(asset_path)

# Add Lights
stage = omni.usd.get_context().get_stage()
light_prim_path="/World/DomeLight"
intensity=1000
exposure=0.0
dome_light = UsdLux.DomeLight.Define(stage, light_prim_path)
dome_light.GetIntensityAttr().Set(intensity)
dome_light.GetExposureAttr().Set(exposure)

# spawn robot
"""
Initialize robot and load RL policy.

Args:
    prim_path (str) -- prim path of the robot on the stage
    root_path (Optional[str]): The path to the articulation root of the robot
    name (str) -- name of the quadruped
    usd_path (str) -- robot usd filepath in the directory if none it gets from Nucleus
    position (np.ndarray) -- position of the robot
    orientation (np.ndarray) -- orientation of the robot

"""
leatherback = LeatherbackPolicy(
    prim_path="/World/leatherback",
    name="leatherback",
    # policy_path = full_path,
    # usd_path = usd_path,
    position=np.array([-1, 0, 0.05]),
)

my_world.reset()
my_world.add_physics_callback("physics_step", callback_fn=on_physics_step)

# base_command: The position of the waypoint in X , Y , Z
base_command = np.zeros(3)

i = 0
idx = 0
while simulation_app.is_running():
    my_world.step(render=True)
    if my_world.is_stopped():
        reset_needed = True
    if my_world.is_playing():
        position, orientation = leatherback.robot.get_world_pose() 
        goal_reached = is_goal_reached(position, base_command)
        # print(f"Get the current position: {position}")
        # print(f"Is the goal reached: {goal_reached}")

        commands = np.array([[1, 0, 0],[3, 2, 0],[2, 4, 0],[0, 4, 0],[-1, 2, 0]])

        if goal_reached:
            base_command = commands[idx]
            idx += 1
        elif idx == 5:
            idx = 0

simulation_app.close()

