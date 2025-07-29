import logging

import cv2
import gymnasium as gym
import numpy as np
from gymnasium import spaces
from luckyrobots import ObservationModel

from .task import Navigation, PickandPlace

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("gym_luckyworld")


class LuckyWorld(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 30}

    def __init__(
        self,
        scene: str,
        task: str,
        robot: str,
        obs_type: str,
        namespace: str = "",
        timeout: float = 30.0,
        render_mode: str = "human",
    ):
        super().__init__()

        self.task = task
        self.robot = robot
        self.timeout = timeout
        self.obs_type = obs_type
        self.render_mode = render_mode
        self.latest_observation = None

        self._setup_task(scene, task, robot, render_mode, namespace)
        self._setup_spaces(obs_type)

    def _setup_task(self, scene: str, task: str, robot: str, render_mode: str, namespace: str) -> None:
        if task == "pickandplace":
            self.task = PickandPlace(scene, task, robot, render_mode, namespace)
        elif task == "navigation":
            self.task = Navigation(scene, task, robot, render_mode, namespace)
        else:
            raise ValueError(f"Invalid task type: {task}")

    def _setup_spaces(self, obs_type: str) -> None:
        # Set up action space (same for all observation types)
        robot_configs = self.task.luckyrobots.get_robot_config()
        if self.robot not in robot_configs:
            raise ValueError(f"Invalid robot type: {self.robot}")
        robot_config = robot_configs[self.robot]
        action_limits = robot_config["action_space"]["actuator_limits"]
        action_dim = len(action_limits)
        self.action_space = spaces.Box(
            low=np.array([limit["lower"] for limit in action_limits]),
            high=np.array([limit["upper"] for limit in action_limits]),
            shape=(action_dim,),
            dtype=np.float64,
        )

        # Set up observation space based on obs_type
        obs_dim = len(robot_config["observation_space"]["actuator_names"])
        obs_limits = robot_config["observation_space"]["actuator_limits"]

        if obs_type == "pixels_agent_pos":
            # Nested structure to match training
            self.observation_space = spaces.Dict(
                {
                    "pixels": spaces.Dict(
                        {
                            "Camera_1": spaces.Box(
                                low=0,
                                high=255,
                                shape=(480, 640, 3),
                                dtype=np.uint8,
                            ),
                            "Camera_2": spaces.Box(
                                low=0,
                                high=255,
                                shape=(480, 640, 3),
                                dtype=np.uint8,
                            ),
                        }
                    ),
                    "agent_pos": spaces.Box(
                        low=np.array([limit["lower"] for limit in obs_limits], dtype=np.float32),
                        high=np.array([limit["upper"] for limit in obs_limits], dtype=np.float32),
                        shape=(obs_dim,),
                        dtype=np.float32,
                    ),
                }
            )
        else:
            raise ValueError(f"Unknown observation type: {obs_type}")

    def _convert_observation(self, observation: ObservationModel) -> dict:
        obs_dict = {
            "pixels": {
                "Camera_1": np.zeros((480, 640, 3), dtype=np.uint8),
                "Camera_2": np.zeros((480, 640, 3), dtype=np.uint8),
            },
            "agent_pos": np.zeros(self.observation_space["agent_pos"].shape, dtype=np.float32),
        }

        # Handle agent position
        if hasattr(observation, "observation_state") and observation.observation_state:
            agent_pos_values = list(observation.observation_state.values())
            agent_pos = np.array(agent_pos_values, dtype=np.float32)
            # Ensure values are within bounds
            agent_pos = np.clip(
                agent_pos, self.observation_space["agent_pos"].low, self.observation_space["agent_pos"].high
            )
            obs_dict["agent_pos"] = agent_pos

        # Handle cameras
        if hasattr(observation, "observation_cameras") and observation.observation_cameras:
            for i, camera in enumerate(observation.observation_cameras):
                if camera.image_data is not None:
                    image = camera.image_data
                    if isinstance(image, np.ndarray):
                        # Map each camera to correct name
                        if i == 0:
                            camera_key = "Camera_1"
                        elif i == 1:
                            camera_key = "Camera_2"
                        else:
                            continue

                        # Ensure image is in correct shape and type
                        if image.shape != (480, 640, 3):
                            image = cv2.resize(image, (640, 480))
                        if image.dtype != np.uint8:
                            image = image.astype(np.uint8)
                        obs_dict["pixels"][camera_key] = image

        return obs_dict

    def reset(self, seed: int = None, options: dict = None) -> tuple[np.ndarray, dict]:
        super().reset(seed=seed, options=options)

        raw_observation, info = self.task.reset(seed=seed)
        # Store the raw observation for rendering
        self.latest_observation = raw_observation

        observation = self._convert_observation(raw_observation)

        return observation, info

    def step(self, action: np.ndarray) -> tuple[dict[str, np.ndarray], float, bool, bool, dict]:
        raw_observation, reward, terminated, truncated, info = self.task.step(action)
        # Store the raw observation for rendering
        self.latest_observation = raw_observation

        observation = self._convert_observation(raw_observation)

        return observation, reward, terminated, truncated, info

    def render(self, return_all_cameras: bool = False) -> np.ndarray | None:
        if self.latest_observation is None:
            logger.warning("No observation available for rendering")
            return np.zeros((480, 640, 3), dtype=np.uint8)  # Shape: (num_cameras, height, width, channels)

        if self.render_mode == "human":
            if self.latest_observation.observation_cameras is not None:
                for camera in self.latest_observation.observation_cameras:
                    if camera.image_data is not None:
                        cv2.imshow(camera.camera_name, camera.image_data)
                        cv2.waitKey(1)
            return None
        elif self.render_mode == "rgb_array":
            if self.latest_observation.observation_cameras is not None:
                camera_arrays = []
                for camera in self.latest_observation.observation_cameras:
                    if camera.image_data is not None:
                        # Convert BGR to RGB for external libraries
                        rgb_image = cv2.cvtColor(camera.image_data, cv2.COLOR_BGR2RGB)
                        camera_arrays.append(rgb_image)

                if camera_arrays:
                    if return_all_cameras:
                        # Return all cameras stacked (RGB format)
                        return np.stack(camera_arrays, axis=0)
                    else:
                        # Return just the first camera for video recording (RGB format)
                        return camera_arrays[0]
            else:
                return np.zeros((480, 640, 3), dtype=np.uint8)
        elif self.render_mode is None:
            return None
        else:
            raise ValueError(f"Unsupported render mode: {self.render_mode}")

    def close(self) -> None:
        if self.task:
            self.task.luckyrobots.shutdown()

        logger.info("Environment closed")
