"""Train the UR5 reach task with RSL-RL."""

from __future__ import annotations

import argparse
import importlib.metadata as metadata
import os
from datetime import datetime

import torch

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="Train the UR5 reach task with RSL-RL.")
parser.add_argument("--num_envs", type=int, default=1024, help="Number of parallel environments.")
parser.add_argument("--max_iterations", type=int, default=None, help="Override the max training iterations.")
parser.add_argument("--seed", type=int, default=None, help="Override the training seed.")
parser.add_argument("--experiment_name", type=str, default=None, help="Experiment folder name.")
parser.add_argument("--run_name", type=str, default=None, help="Run name suffix for the log directory.")
parser.add_argument("--video", action="store_true", help="Record videos during training.")
parser.add_argument("--video_length", type=int, default=200, help="Video length in steps.")
parser.add_argument("--video_interval", type=int, default=2000, help="Steps between video recordings.")
parser.add_argument("--resume", action="store_true", help="Resume from the latest matching checkpoint.")
parser.add_argument("--load_run", type=str, default=None, help="Run directory regex for resume.")
parser.add_argument("--checkpoint", type=str, default=None, help="Checkpoint file to resume from.")

AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()

app_launcher = AppLauncher(args)
simulation_app = app_launcher.app

"""Rest everything follows."""

import gymnasium as gym
from rsl_rl.runners import OnPolicyRunner

from isaaclab.utils.dict import print_dict
from isaaclab.utils.io import dump_yaml
from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper, handle_deprecated_rsl_rl_cfg

import ur5_rl  # noqa: F401
from ur5_rl.tasks.reach.agents.rsl_rl_ppo_cfg import UR5ReachPPORunnerCfg
from ur5_rl.tasks.reach.ur5_reach_env_cfg import UR5ReachEnvCfg

torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True


def main() -> None:
    env_cfg = UR5ReachEnvCfg()
    env_cfg.scene.num_envs = args.num_envs
    agent_cfg = UR5ReachPPORunnerCfg()

    if args.max_iterations is not None:
        agent_cfg.max_iterations = args.max_iterations
    if args.seed is not None:
        agent_cfg.seed = args.seed
    if args.experiment_name is not None:
        agent_cfg.experiment_name = args.experiment_name
    if args.run_name is not None:
        agent_cfg.run_name = args.run_name
    if args.resume:
        agent_cfg.resume = True
    if args.load_run is not None:
        agent_cfg.load_run = args.load_run
    if args.checkpoint is not None:
        agent_cfg.load_checkpoint = args.checkpoint

    installed_version = metadata.version("rsl-rl-lib")
    agent_cfg = handle_deprecated_rsl_rl_cfg(agent_cfg, installed_version)

    env_cfg.seed = agent_cfg.seed
    if getattr(args, "device", None):
        env_cfg.sim.device = args.device

    log_root_path = os.path.abspath(os.path.join("logs", "rsl_rl", agent_cfg.experiment_name))
    log_dir = os.path.join(log_root_path, datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    if agent_cfg.run_name:
        log_dir += f"_{agent_cfg.run_name}"
    env_cfg.log_dir = log_dir
    os.makedirs(log_dir, exist_ok=True)

    print(f"[INFO] Logging experiment in directory: {log_root_path}")
    print(f"[INFO] Run directory: {log_dir}")
    print_dict(agent_cfg.to_dict(), nesting=1)

    env = gym.make("Ur5Reach-v0", cfg=env_cfg, render_mode="rgb_array" if args.video else None)

    if args.video:
        video_kwargs = {
            "video_folder": os.path.join(log_dir, "videos", "train"),
            "step_trigger": lambda step: step % args.video_interval == 0,
            "video_length": args.video_length,
            "disable_logger": True,
        }
        env = gym.wrappers.RecordVideo(env, **video_kwargs)

    env = RslRlVecEnvWrapper(env, clip_actions=agent_cfg.clip_actions)
    runner = OnPolicyRunner(env, agent_cfg.to_dict(), log_dir=log_dir, device=agent_cfg.device)

    if agent_cfg.resume:
        from isaaclab_tasks.utils import get_checkpoint_path

        resume_path = get_checkpoint_path(log_root_path, agent_cfg.load_run, agent_cfg.load_checkpoint)
        print(f"[INFO] Loading model checkpoint from: {resume_path}")
        runner.load(resume_path)

    os.makedirs(os.path.join(log_dir, "params"), exist_ok=True)
    dump_yaml(os.path.join(log_dir, "params", "env.yaml"), env_cfg)
    dump_yaml(os.path.join(log_dir, "params", "agent.yaml"), agent_cfg)

    try:
        runner.learn(num_learning_iterations=agent_cfg.max_iterations, init_at_random_ep_len=True)
    finally:
        env.close()


if __name__ == "__main__":
    main()
    simulation_app.close()
