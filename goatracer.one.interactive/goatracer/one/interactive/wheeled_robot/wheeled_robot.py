
import re
from typing import Optional

import carb
import numpy as np
from isaacsim.core.api.robots.robot import Robot
from isaacsim.core.utils.prims import define_prim, get_prim_at_path
from isaacsim.core.utils.types import ArticulationAction, ArticulationActions


class AckermannRobot(Robot):

    def __init__(
        self,
        prim_path: str,
        name: str, #= "wheeled_robot",
        robot_path: Optional[str] = None,
        throttle_dof_names: Optional[str] = None,
        steering_dof_names: Optional[str] = None,
        throttle_dof_indices: Optional[int] = None,
        steering_dof_indices: Optional[int] = None,
        usd_path: Optional[str] = None,
        create_robot: Optional[bool] = False,
        position: Optional[np.ndarray] = None,
        orientation: Optional[np.ndarray] = None,
    ) -> None:
        prim = get_prim_at_path(prim_path)
        if not prim.IsValid():
            if create_robot:
                prim = define_prim(prim_path, "Xform")
                if usd_path:
                    prim.GetReferences().AddReference(usd_path)
                else:
                    carb.log_error("no valid usd path defined to create new robot")
            else:
                carb.log_error("no prim at path %s", prim_path)

        if robot_path is not None:
            robot_path = "/" + robot_path
            # regex: remove all prefixing "/", need at least one prefix "/" to work
            robot_path = re.sub("^([^\/]*)\/*", "", "/" + robot_path)
            prim_path = prim_path + "/" + robot_path

        super().__init__(
            prim_path=prim_path, name=name, position=position, orientation=orientation, articulation_controller=None
        )

        self._throttle_dof_names = throttle_dof_names
        self._steering_dof_names = steering_dof_names
        self._throttle_dof_indices = throttle_dof_indices
        self._steering_dof_indices = steering_dof_indices

        return
    
    @property
    def throttle_dof_indices(self):
        """[summary]

        Returns:
            int: [description]
        """
        return self._throttle_dof_indices
    
    @property
    def steering_dof_indices(self):
        """[summary]

        Returns:
            int: [description]
        """
        return self._steering_dof_indices

    def get_wheel_positions(self):
        """[summary]

        Returns:
            List[float]: [description]
        """
        full_dofs_positions = self.get_joint_positions()
        wheel_joint_positions = [full_dofs_positions[i] for i in self._steering_dof_indices]
        return wheel_joint_positions

    def set_wheel_positions(self, positions) -> None:
        """[summary]

        Args:
            positions (Tuple[float, float]): [description]
        """
        full_dofs_positions = [None] * self._num_steering_dof
        for i in range(self._num_steering_dof):
            full_dofs_positions[self._steering_dof_indices[i]] = positions[i]
        self.set_joint_positions(positions=np.array(full_dofs_positions))
        return

    def get_wheel_velocities(self):
        """[summary]

        Returns:
            Tuple[np.ndarray, np.ndarray]: [description]
        """

        full_dofs_velocities = self.get_joint_velocities()
        wheel_dof_velocities = [full_dofs_velocities[i] for i in self._throttle_dof_indices]
        return wheel_dof_velocities

    def set_wheel_velocities(self, velocities) -> None:
        """[summary]

        Args:
            velocities (Tuple[float, float]): [description]
        """
        full_dofs_velocities = [None] * self._num_wheel_dof
        for i in range(self._num_wheel_dof):
            full_dofs_velocities[self._throttle_dof_indices[i]] = velocities[i]
        self.set_joint_velocities(velocities=np.array(full_dofs_velocities))
        return

    def apply_wheel_actions(self, actions: ArticulationAction) -> None:
        """
        applying action to the wheels to move the robot

        Args:
            actions (ArticulationAction): [description]
        """
        actions_length = self.get_size(actions)
        
        if actions_length is not None and actions_length != (self._num_wheel_dof + self._num_steering_dof):# using get_length() should be 4 --- (self._num_wheel_dof + self._num_steering_dof):
            raise Exception("ArticulationAction passed should be the same length as the number of Joints. e.g.: 4 wheels + 2 steering")
        
        steering_action = ArticulationAction(
            joint_positions=actions.joint_positions,
            joint_indices=self._steering_dof_indices,
        )
        throttle_action = ArticulationAction(
            joint_velocities=actions.joint_velocities,
            joint_indices=self._throttle_dof_indices,
        )

        self.apply_action(control_actions=steering_action)
        self.apply_action(control_actions=throttle_action)
        
        return

    def initialize(self, physics_sim_view=None) -> None:
        """
        _wheel_dof_indices replaced by _throttle_dof_indices and _steering_dof_indices
        _throttle_dof_indices the joint indices related to the _throttle_dof_names
        
        """
        super().initialize(physics_sim_view=physics_sim_view)
        if self._throttle_dof_names is not None:
            self._throttle_dof_indices = [
                self.get_dof_index(self._throttle_dof_names[i]) for i in range(len(self._throttle_dof_names))
            ]
        if self._steering_dof_names is not None:
            self._steering_dof_indices = [
                self.get_dof_index(self._steering_dof_names[i]) for i in range(len(self._steering_dof_names))
            ]
        elif self._throttle_dof_indices or self._steering_dof_indices is None:
            carb.log_error("need to have either joint names or joint indices")

        self._num_wheel_dof = len(self._throttle_dof_indices)
        self._num_steering_dof = len(self._steering_dof_indices)

        return

    def post_reset(self) -> None:
        """[summary]"""
        super().post_reset()
        # self._articulation_controller.switch_control_mode(mode="velocity")
        return
    
    def get_articulation_controller_properties(self):
        return self._throttle_dof_names, self._steering_dof_names, self._steering_dof_indices, self._throttle_dof_indices
    
    def get_size(self, actions):
        """[summary]
        This is to overcome the issues with get_length() in ArticulationAction
        Returns:
            Optional[int]: [description]
        """
        size = None
        if actions.joint_positions is not None:
            if size is None:
                size = 0
            if isinstance(actions.joint_positions, np.ndarray):
                size += max(size, actions.joint_positions.shape[0])
            else:
                size += max(size, len(actions.joint_positions))
        if actions.joint_velocities is not None:
            if size is None:
                size = 0
            if isinstance(actions.joint_velocities, np.ndarray):
                size += max(size, actions.joint_velocities.shape[0])
            else:
                size += max(size, len(actions.joint_velocities))
        if actions.joint_efforts is not None:
            if size is None:
                size = 0
            if isinstance(actions.joint_efforts, np.ndarray):
                size += max(size, actions.joint_efforts.shape[0])
            else:
                size += max(size, len(actions.joint_efforts))
        return size
