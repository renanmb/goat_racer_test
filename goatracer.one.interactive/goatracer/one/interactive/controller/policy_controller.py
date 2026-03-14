import io
from typing import Optional

import carb
import numpy as np
import omni
import torch
from isaacsim.core.api.controllers.base_controller import BaseController
from isaacsim.robot.wheeled_robots.controllers.ackermann_controller import AckermannController
from isaacsim.core.prims import SingleArticulation
from isaacsim.core.utils.prims import define_prim, get_prim_at_path

import os
try:
    import onnxruntime as ort
except ImportError:
    import omni.kit.pipapi
    omni.kit.pipapi.install(
        package="onnxruntime",
        version="1.20.0", 
        ignore_cache=False,
        use_online_index=True
    )
    import onnxruntime as ort
# region Change
# from leatherback.example.ackermann.wheeled_robot import AckermannRobot
from goatracer.one.interactive.wheeled_robot import AckermannRobot

from .config_loader import get_articulation_props, get_physics_properties, get_robot_joint_properties, parse_env_config

class PolicyController(BaseController):
    """
    A controller that loads and executes a policy from a file.

    Args:
        name (str): The name of the controller.
        prim_path (str): The path to the prim in the stage.
        root_path (Optional[str], None): The path to the articulation root of the robot
        usd_path (Optional[str], optional): The path to the USD file. Defaults to None.
        position (Optional[np.ndarray], optional): The initial position of the robot. Defaults to None.
        orientation (Optional[np.ndarray], optional): The initial orientation of the robot. Defaults to None.

    Attributes:
        robot (SingleArticulation): The robot articulation.
    """

    def __init__(
        self,
        name: str,
        prim_path: str,
        root_path: Optional[str] = None,
        usd_path: Optional[str] = None,
        policy_path: Optional[str] = None,
        position: Optional[np.ndarray] = None,
        orientation: Optional[np.ndarray] = None,
    ) -> None:

        prim = get_prim_at_path(prim_path)
        """
        AckermannController uses a bicycle model for Ackermann steering. The controller computes the left turning angle, right turning angle, and the rotation velocity of each wheel of a robot with no slip angle. The controller can be used to find the appropriate joint values of a wheeled robot with an Ackermann steering mechanism.

        Args:

            name (str):                          [description]
            wheel_base (float):                  0.32   Distance between front and rear axles in m
            track_width (float):                 0.24   Distance between left and right wheels of the robot in m
            front_wheel_radius (float):          0.052  Radius of the front wheels of the robot in m. Defaults to 0.0 m but will equal back_wheel_radius if no value is inputted.
            back_wheel_radius (float):           0.052  Radius of the back wheels of the robot in m. Defaults to 0.0 m but will equal front_wheel_radius if no value is inputted.
            max_wheel_velocity (float):          20     Maximum angular velocity of the robot wheel in rad/s. Parameter is ignored if set to 0.0.
            invert_steering (bool):              Set to true for rear wheel steering
            max_wheel_rotation_angle (float):    0.7854 The maximum wheel steering angle for the steering wheels. Defaults to 6.28 rad. Parameter is ignored if set to 0.0.
            max_acceleration (float):            1.0    The maximum magnitude of acceleration for the robot in m/s^2. Parameter is ignored if set to 0.0.
            max_steering_angle_velocity (float): 1.0    The maximum magnitude of desired rate of change for steering angle in rad/s. Parameter is ignored if set to 0.0.
        """

        wheel_base = 0.32
        track_width = 0.24
        front_wheel_radius = 0.052
        back_wheel_radius = 0.052
        max_wheel_velocity = 50.0
        # invert_steering: bool = False,
        max_wheel_rotation_angle = 0.7854
        max_acceleration = 1.0
        max_steering_angle_velocity = 1.0

        self.wheel_base = wheel_base # np.fabs(wheel_base)
        self.track_width = track_width # np.fabs(track_width)
        self.front_wheel_radius = front_wheel_radius # np.fabs(front_wheel_radius)
        self.back_wheel_radius = back_wheel_radius # np.fabs(back_wheel_radius)
        self.max_wheel_velocity = max_wheel_velocity # np.fabs(max_wheel_velocity)
        # self.invert_steering = invert_steering
        self.max_wheel_rotation_angle = max_wheel_rotation_angle # np.fabs(max_wheel_rotation_angle)
        self.max_acceleration = max_acceleration # np.fabs(max_acceleration)
        self.max_steering_angle_velocity = max_steering_angle_velocity # np.fabs(max_steering_angle_velocity)

        self.controller = AckermannController(
            name = name,
            wheel_base =                  self.wheel_base,
            track_width =                 self.track_width,
            front_wheel_radius =          self.front_wheel_radius,
            # back_wheel_radius =           self.back_wheel_radius,
            max_wheel_velocity =          self.max_wheel_velocity,
            # invert_steering =             self.invert_steering,
            max_wheel_rotation_angle =    self.max_wheel_rotation_angle,
            max_acceleration =            self.max_acceleration,
            max_steering_angle_velocity = self.max_steering_angle_velocity,
        )

        if not prim.IsValid():
            prim = define_prim(prim_path, "Xform")
            if usd_path:
                prim.GetReferences().AddReference(usd_path)
            else:
                carb.log_error("unable to add robot usd, usd_path not provided")

        if root_path == None:
            self.robot = AckermannRobot(
                            prim_path=prim_path,
                            name=name,
                            position=position,
                            throttle_dof_names=[
                                "Wheel__Knuckle__Front_Left", 
                                "Wheel__Knuckle__Front_Right",
                                "Wheel__Upright__Rear_Right",
                                "Wheel__Upright__Rear_Left"
                            ],
                            steering_dof_names=[
                                "Knuckle__Upright__Front_Right",
                                "Knuckle__Upright__Front_Left"
                            ]
                        )
        else:
            self.robot = AckermannRobot(
                            prim_path=root_path,
                            name=name,
                            position=position,
                            throttle_dof_names=[
                                "Wheel__Knuckle__Front_Left", 
                                "Wheel__Knuckle__Front_Right",
                                "Wheel__Upright__Rear_Right",
                                "Wheel__Upright__Rear_Left"
                            ],
                            steering_dof_names=[
                                "Knuckle__Upright__Front_Right",
                                "Knuckle__Upright__Front_Left"
                            ]
                        )

    def load_policy(self, policy_file_path, policy_env_path) -> None:
        """
        Loads a policy from a file.

        Args:
            policy_file_path (str): The path to the policy file. Example: spot_policy.pt
            policy_env_path (str): The path to the environment configuration file. Example: spot_env.yaml
        """
        if policy_file_path.endswith('.pt') or policy_file_path.endswith('.pth'):
            file_content = omni.client.read_file(policy_file_path)[2]
            file = io.BytesIO(memoryview(file_content).tobytes())
            self.policy = torch.jit.load(file)
            self._isJIT = 1
        elif policy_file_path.endswith('.onnx'):
            file_content = omni.client.read_file(policy_file_path)[2]
            file = io.BytesIO(memoryview(file_content).tobytes())
            self.session = ort.InferenceSession(policy_file_path)
            self._isJIT = 0

        self.policy_env_params = parse_env_config(policy_env_path)
        self._decimation, self._dt, self.render_interval = get_physics_properties(self.policy_env_params)
    
    def _compute_action(self, obs: np.ndarray) -> np.ndarray:
        """
        Computes the action from the observation using the loaded policy.

        Args:
            obs (np.ndarray): The observation.

        Returns:
            np.ndarray: The action.
        """
        if self._isJIT == 1:
            with torch.no_grad():
                obs = torch.from_numpy(obs).view(1, -1).float()
                action = self.policy(obs).detach().view(-1).numpy()   
        elif self._isJIT == 0:
            obs = torch.from_numpy(obs).view(1, -1).float()
            ort_inputs = {self.session.get_inputs()[0].name: obs.numpy()}
            output_names = [output.name for output in self.session.get_outputs()]
            outputs = self.session.run(output_names, ort_inputs)
            action = outputs[0].reshape(-1)

        # Setting acceleration, steering velocity, and dt to 0 to instantly reach the target steering and velocity
        acceleration = 0.0  # m/s^2
        steering_velocity = 0.0  # rad/s
        dt = 0.0  # secs
        
        """
        Multiplier for the throttle velocity and steering position. 
        The action is in the range [-1, 1] and the radius of the wheel is 0.06m
        """
        throttle_scale = 5 
        throttle_max = 1 
        steering_scale = 0.01 
        steering_max = 0.75 
        
        _throttle = np.clip(action[0]*throttle_scale, -throttle_max, throttle_max*1)
        _steering = np.clip(action[1]*steering_scale, -steering_max, steering_max)
        
        desired_forward_vel = _throttle # action[0]
        desired_steering_angle = _steering  # action[1]

        actions = self.controller.forward([desired_steering_angle, steering_velocity, desired_forward_vel, acceleration, dt])
        return action, actions

    def _compute_observation(self) -> NotImplementedError:
        """
        Computes the observation. Not implemented.
        """

        raise NotImplementedError(
            "Compute observation need to be implemented, expects np.ndarray in the structure specified by env yaml"
        )

    def forward(self) -> NotImplementedError:
        """
        Forwards the controller. Not implemented.
        """
        raise NotImplementedError(
            "Forward needs to be implemented to compute and apply robot control from observations"
        )

    def post_reset(self) -> None:
        """
        Called after the controller is reset.
        """
        self.robot.post_reset()

