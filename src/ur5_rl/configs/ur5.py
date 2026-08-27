"""Canonical UR5 parameters shared by environment and task code.

Kinematic, limit, and inertial values originate from the ROS Industrial UR
description package; actuator gains are explicit simulation starting values.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ASSET_ROOT = Path(__file__).resolve().parents[3] / "assets"
URDF_PATH = ASSET_ROOT / "ur5" / "ur5.urdf"

N_JOINTS = 6
JOINT_NAMES = (
    "shoulder_pan_joint",
    "shoulder_lift_joint",
    "elbow_joint",
    "wrist_1_joint",
    "wrist_2_joint",
    "wrist_3_joint",
)
BASE_FRAME = "base_link"
TOOL_FRAME = "flange"

POSITION_LOWER = (
    -6.283185307179586,
    -6.283185307179586,
    -3.141592653589793,
    -6.283185307179586,
    -6.283185307179586,
    -6.283185307179586,
)
POSITION_UPPER = (
    6.283185307179586,
    6.283185307179586,
    3.141592653589793,
    6.283185307179586,
    6.283185307179586,
    6.283185307179586,
)
VELOCITY_LIMIT = (3.141592653589793,) * N_JOINTS
EFFORT_LIMIT = (150.0, 150.0, 150.0, 28.0, 28.0, 28.0)

INITIAL_POSITION = (0.0, -1.5707963267948966, 1.5707963267948966, 0.0, 0.0, 0.0)

# Implicit-actuator initial values for simulation tuning.
STIFFNESS = (400.0, 400.0, 300.0, 80.0, 80.0, 20.0)
DAMPING = (8.0, 8.0, 6.0, 1.5, 1.5, 0.5)
FRICTION = 0.0

DH_D = (0.089159, 0.0, 0.0, 0.10915, 0.09465, 0.0823)
DH_A = (0.0, -0.425, -0.39225, 0.0, 0.0, 0.0)
DH_ALPHA = (
    1.5707963267948966,
    0.0,
    0.0,
    1.5707963267948966,
    -1.5707963267948966,
    0.0,
)
SHOULDER_OFFSET = 0.13585
ELBOW_OFFSET = 0.0165


@dataclass(frozen=True)
class Ur5Config:
    urdf_path: Path = URDF_PATH
    joint_names: tuple[str, ...] = JOINT_NAMES
    base_frame: str = BASE_FRAME
    tool_frame: str = TOOL_FRAME
    initial_position: tuple[float, ...] = INITIAL_POSITION
    effort_limit: tuple[float, ...] = EFFORT_LIMIT
    velocity_limit: tuple[float, ...] = VELOCITY_LIMIT


UR5_CONFIG = Ur5Config()
