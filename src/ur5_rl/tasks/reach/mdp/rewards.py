"""Reward terms for the UR5 reach task.

The functions are adapted from the Isaac Lab reach task reference
(BSD-3-Clause, copyright (c) 2022-2026 The Isaac Lab Project Developers).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import torch

from isaaclab.managers import SceneEntityCfg
from isaaclab.utils.math import combine_frame_transforms, quat_error_magnitude, quat_mul

if TYPE_CHECKING:
    from isaaclab.assets import RigidObject
    from isaaclab.envs import ManagerBasedRLEnv


def position_command_error(env: ManagerBasedRLEnv, command_name: str, asset_cfg: SceneEntityCfg) -> torch.Tensor:
    """L2-norm penalty for the end-effector position tracking error."""
    asset: RigidObject = env.scene[asset_cfg.name]
    command = env.command_manager.get_command(command_name)
    des_pos_b = command[:, :3]
    des_pos_w, _ = combine_frame_transforms(asset.data.root_pos_w.torch, asset.data.root_quat_w.torch, des_pos_b)
    curr_pos_w = asset.data.body_pos_w.torch[:, asset_cfg.body_ids[0]]
    return torch.linalg.norm(curr_pos_w - des_pos_w, dim=1)


def position_command_error_tanh(
    env: ManagerBasedRLEnv, std: float, command_name: str, asset_cfg: SceneEntityCfg
) -> torch.Tensor:
    """Dense reward for position tracking using a tanh kernel."""
    asset: RigidObject = env.scene[asset_cfg.name]
    command = env.command_manager.get_command(command_name)
    des_pos_b = command[:, :3]
    des_pos_w, _ = combine_frame_transforms(asset.data.root_pos_w.torch, asset.data.root_quat_w.torch, des_pos_b)
    curr_pos_w = asset.data.body_pos_w.torch[:, asset_cfg.body_ids[0]]
    distance = torch.linalg.norm(curr_pos_w - des_pos_w, dim=1)
    return 1 - torch.tanh(distance / std)


def orientation_command_error(env: ManagerBasedRLEnv, command_name: str, asset_cfg: SceneEntityCfg) -> torch.Tensor:
    """Shortest-path orientation error between the commanded and current poses."""
    asset: RigidObject = env.scene[asset_cfg.name]
    command = env.command_manager.get_command(command_name)
    des_quat_b = command[:, 3:7]
    des_quat_w = quat_mul(asset.data.root_quat_w.torch, des_quat_b)
    curr_quat_w = asset.data.body_quat_w.torch[:, asset_cfg.body_ids[0]]
    return quat_error_magnitude(curr_quat_w, des_quat_w)
