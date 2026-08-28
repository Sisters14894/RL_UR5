"""UR5 reach task registration."""

import gymnasium as gym

from ur5_rl.tasks.reach.ur5_reach_env_cfg import UR5ReachEnvCfg, UR5ReachEnvCfg_PLAY

##
# Register Gym environments.
##

gym.register(
    id="Ur5Reach-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.ur5_reach_env_cfg:UR5ReachEnvCfg",
        "rsl_rl_cfg_entry_point": f"{__name__}.agents.rsl_rl_ppo_cfg:UR5ReachPPORunnerCfg",
    },
)

gym.register(
    id="Ur5Reach-Play-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.ur5_reach_env_cfg:UR5ReachEnvCfg_PLAY",
        "rsl_rl_cfg_entry_point": f"{__name__}.agents.rsl_rl_ppo_cfg:UR5ReachPPORunnerCfg",
    },
)
