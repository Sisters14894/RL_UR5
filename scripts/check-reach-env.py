"""Smoke-test the Ur5Reach-v0 environment without training."""

from __future__ import annotations

import argparse

import torch

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="Smoke-test the UR5 reach environment.")
parser.add_argument("--num_envs", type=int, default=8, help="Number of parallel environments.")
parser.add_argument("--num_steps", type=int, default=20, help="Number of random policy steps.")

AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()

app_launcher = AppLauncher(args)
simulation_app = app_launcher.app

"""Rest everything follows."""

import gymnasium as gym

import ur5_rl  # noqa: F401
from ur5_rl.tasks.reach.ur5_reach_env_cfg import UR5ReachEnvCfg


def main() -> None:
    env_cfg = UR5ReachEnvCfg()
    env_cfg.scene.num_envs = args.num_envs

    env = gym.make("Ur5Reach-v0", cfg=env_cfg)
    obs, _ = env.reset()

    print(f"Observation groups: {list(obs.keys())}")
    print(f"Policy observation shape: {tuple(obs['policy'].shape)}")
    print(f"Single action space: {env.unwrapped.single_action_space}")

    for step in range(args.num_steps):
        actions = torch.randn(
            env.unwrapped.num_envs,
            env.unwrapped.action_manager.total_action_dim,
            device=env.unwrapped.device,
        )
        obs, reward, terminated, truncated, _ = env.step(actions)
        print(
            f"step {step + 1:02d}: reward mean={reward.mean().item():.4f} "
            f"terminated={int(terminated.sum().item())} truncated={int(truncated.sum().item())}"
        )

    env.close()


if __name__ == "__main__":
    main()
    simulation_app.close()
