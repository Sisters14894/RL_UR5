"""MDP terms specific to the UR5 reach task."""

from ur5_rl.tasks.reach.mdp.rewards import (  # noqa: F401
    orientation_command_error,
    position_command_error,
    position_command_error_tanh,
)
