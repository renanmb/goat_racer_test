# Copyright (c) 2022-2024, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Configuration for the leatherback robot."""

import os
import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets import ArticulationCfg

# 1. Start from the directory of the current script
current_dir = os.path.abspath(os.path.dirname(__file__))

# 2. Traverse upwards to find the GitHub repository root (indicated by the .git folder)
repo_root = current_dir
while not os.path.exists(os.path.join(repo_root, ".git")):
    parent_dir = os.path.dirname(repo_root)
    if parent_dir == repo_root:  # Reached the root of the file system
        raise RuntimeError("Could not find the GitHub repository root (.git folder).")
    repo_root = parent_dir

# 3. Set WORKSPACE_ROOT to the true repository root
WORKSPACE_ROOT = repo_root

# 4. Construct the precise path to the asset from the repo root
USD_PATH = os.path.join(
    WORKSPACE_ROOT, 
    "source", 
    "leatherback", 
    "leatherback", 
    "tasks", 
    "direct", 
    "leatherback", 
    "custom_assets", 
    "leatherback_simple_better.usd"
)

# Optional: Verify the file actually exists before Isaac Lab tries to open it
if not os.path.exists(USD_PATH):
    raise FileNotFoundError(f"USD asset not found at the constructed path:\n{USD_PATH}")

LEATHERBACK_CFG = ArticulationCfg(
    spawn=sim_utils.UsdFileCfg(
        usd_path=USD_PATH,
        rigid_props=sim_utils.RigidBodyPropertiesCfg(
            rigid_body_enabled=True,
            max_linear_velocity=1000.0,
            max_angular_velocity=1000.0,
            max_depenetration_velocity=100.0,
            enable_gyroscopic_forces=True,
        ),
        articulation_props=sim_utils.ArticulationRootPropertiesCfg(
            enabled_self_collisions=False,
            solver_position_iteration_count=4,
            solver_velocity_iteration_count=0,
            sleep_threshold=0.005,
            stabilization_threshold=0.001,
        ),
    ),
    init_state=ArticulationCfg.InitialStateCfg(
        pos=(0.0, 0.0, 0.05),
        joint_pos={
            "Wheel__Knuckle__Front_Left": 0.0,
            "Wheel__Knuckle__Front_Right": 0.0,
            "Wheel__Upright__Rear_Right": 0.0,
            "Wheel__Upright__Rear_Left": 0.0,
            "Knuckle__Upright__Front_Right": 0.0,
            "Knuckle__Upright__Front_Left": 0.0,
        },
    ),
    actuators={
        "throttle": ImplicitActuatorCfg(
            joint_names_expr=["Wheel.*"],
            effort_limit=40000.0,
            velocity_limit=100.0,
            stiffness=0.0,
            damping=100000.0,
        ),
        "steering": ImplicitActuatorCfg(
            joint_names_expr=["Knuckle__Upright__Front.*"],
            effort_limit=40000.0,
            velocity_limit=100.0,
            stiffness=1000.0,
            damping=0.0, # whyu is this zero!?!? changing this causes steering to be really impossible
            # we need to goto full ackermann steering
        ),
    },
)
