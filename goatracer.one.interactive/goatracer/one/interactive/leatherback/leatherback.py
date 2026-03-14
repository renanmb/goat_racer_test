from typing import Optional
import os
import numpy as np
import omni
import omni.kit.commands
from isaacsim.core.utils.rotations import quat_to_rot_matrix
from isaacsim.storage.native import get_assets_root_path

# region change
# from leatherback.example.ackermann.controller import PolicyController
from goatracer.one.interactive.controller import PolicyController

class LeatherbackPolicy(PolicyController):
    """The Leatherback racer"""

    def __init__(
        self,
        prim_path: str,
        root_path: Optional[str] = None,
        name: str = "spot",
        usd_path: Optional[str] = None,
        policy_path: Optional[str] = None,
        position: Optional[np.ndarray] = None,
        orientation: Optional[np.ndarray] = None,
    ) -> None:
        """
        Initialize robot and load RL policy.

        Args:
            prim_path (str) -- prim path of the robot on the stage
            root_path (Optional[str]): The path to the articulation root of the robot
            name (str) -- name of the quadruped
            usd_path (str) -- robot usd filepath in the directory
            policy_path (str) -- 
            position (np.ndarray) -- position of the robot
            orientation (np.ndarray) -- orientation of the robot

        """
        assets_root_path = get_assets_root_path()
        script_dir = os.path.dirname(__file__)
        relative_path = os.path.join("../../../../", "assets")
        full_path = os.path.abspath(os.path.join(script_dir, relative_path))

        if usd_path == None:
            # Later might be able to add an Asset to show it doesnt exist - easter egg
            usd_path = os.path.abspath(os.path.join(full_path, "leatherback_simple_better.usd"))
            print("File not found")
        
        super().__init__(name, prim_path, root_path, usd_path, policy_path, position, orientation)

        if policy_path == None:
            self.load_policy(
                full_path + "/policy.onnx",
                full_path + "/env.yaml",
            )
            print("Policy not found")
        else:
            self.load_policy(
                    policy_path + "/policy.onnx",
                    policy_path + "/env.yaml",
                ) 
    
        self._action_scale = 1
        # Leatherback has action space = 2
        self._previous_action = np.zeros(2)
        self._policy_counter = 0

    def _compute_observation(self, command):
        """
        Compute the observation vector for the policy

        Argument:
        command (np.ndarray) -- the waypoint goal (x, y, z)

        Returns:
        np.ndarray -- The observation vector.

        """

        """
        Multiplier for the throttle velocity and steering position. 
        The action is in the range [-1, 1] and the radius of the wheel is 0.06m
        """
        throttle_scale = 5
        throttle_max = 50
        steering_scale = 0.01
        steering_max = 0.75

        lin_vel_I = self.robot.get_linear_velocity()
        ang_vel_I = self.robot.get_angular_velocity()
        pos_IB, q_IB = self.robot.get_world_pose()
        R_IB = quat_to_rot_matrix(q_IB)
        R_BI = R_IB.transpose()
        lin_vel_b = np.matmul(R_BI, lin_vel_I)
        ang_vel_b = np.matmul(R_BI, ang_vel_I)
        gravity_b = np.matmul(R_BI, np.array([0.0, 0.0, -1.0]))

        # Calculate the Position Error
        _position_error_vector = command - pos_IB
        _position_error = np.linalg.norm(_position_error_vector) # , axis=-1

        # Calculate the Heading Error
        FORWARD_VEC_B = np.array([1.0, 0.0, 0.0])
        quat = q_IB.reshape(-1, 4)
        vec = FORWARD_VEC_B.reshape(-1, 3)
        xyz = quat[:, 1:]
        t = 2 * np.cross(xyz, vec)
        w = quat[:, 0:1]
        forward_w = vec + w * t + np.cross(xyz, t)
        heading_w = np.arctan2(forward_w[:, 1], forward_w[:, 0])  # shape (N,)

        target_heading_w = np.arctan2(command[1]-pos_IB[1], command[0]-pos_IB[0])
        _heading_error = target_heading_w - heading_w
        
        # _throttle_state
        throttle_action = self._previous_action[0]*throttle_scale
        _throttle_state = np.clip(throttle_action, -throttle_max, throttle_max*1) # 0.1
        # _steering_state
        steering_action = self._previous_action[1]*steering_scale
        _steering_state = np.clip(steering_action, -steering_max, steering_max)

        # leatherback has 8 observations
        """
        Observations:
            position error
            heading error cosine
            heading error sine
            root_lin_vel_b[:, 0]
            root_lin_vel_b[:, 1]
            root_ang_vel_w[:, 2]
            _throttle_state
            _steering_state
        """
        obs = np.zeros(8)
        obs[0] = _position_error
        obs[1] = np.cos(_heading_error)[:, np.newaxis]
        obs[2] = np.sin(_heading_error)[:, np.newaxis]
        obs[3] = lin_vel_b[0] # Linear Velocity X
        obs[4] = lin_vel_b[1] # Linear Velocity Y
        obs[5] = ang_vel_b[2] # Angular Velocity vZ
        obs[6] = _throttle_state # self._previous_action[0]
        obs[7] = _steering_state # self._previous_action[1]

        return obs

    def forward(self, dt, command):
        """
        Compute the desired torques and apply them to the articulation

        Argument:
        dt (float) -- Timestep update in the world.
        command (np.ndarray) -- the robot command (v_x, v_y, w_z)

        """
        if self._policy_counter % self._decimation == 0:
            obs = self._compute_observation(command)

            self.action, self.actions = self._compute_action(obs)
            self.repeated_arr = np.repeat(self.action, [4, 2])
            self._previous_action = self.action.copy()

        self.robot.apply_wheel_actions(self.actions)
        self._policy_counter += 1
