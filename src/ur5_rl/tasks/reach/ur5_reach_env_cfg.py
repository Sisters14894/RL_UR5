"""Manager-based reach environment for the UR5 arm."""

from __future__ import annotations

import math
from dataclasses import MISSING

import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets import ArticulationCfg, AssetBaseCfg
from isaaclab.envs import ManagerBasedRLEnvCfg
from isaaclab.envs.mdp import (
    JointPositionActionCfg,
    UniformPoseCommandCfg,
    action_rate_l2,
    generated_commands,
    joint_pos_rel,
    joint_vel_l2,
    joint_vel_rel,
    last_action,
    reset_joints_by_scale,
    time_out,
)
from isaaclab.managers import ActionTermCfg as ActionTerm
from isaaclab.managers import EventTermCfg as EventTerm
from isaaclab.managers import ObservationGroupCfg as ObsGroup
from isaaclab.managers import ObservationTermCfg as ObsTerm
from isaaclab.managers import RewardTermCfg as RewTerm
from isaaclab.managers import SceneEntityCfg
from isaaclab.managers import TerminationTermCfg as DoneTerm
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.sim import ArticulationRootPropertiesCfg, RigidBodyPropertiesCfg, UsdFileCfg
from isaaclab.utils.configclass import configclass
from isaaclab.utils.noise import UniformNoiseCfg as Unoise

from ur5_rl.configs.ur5 import DAMPING, INITIAL_POSITION, JOINT_NAMES, STIFFNESS, USD_PATH
from ur5_rl.tasks.reach.mdp import orientation_command_error, position_command_error, position_command_error_tanh

_JOINT_CFG = SceneEntityCfg("robot", joint_names=list(JOINT_NAMES))

##
# Articulation
##

_ARM_JOINTS = ["shoulder_pan_joint", "shoulder_lift_joint"]
_WRIST_JOINTS = ["wrist_1_joint", "wrist_2_joint", "wrist_3_joint"]

UR5_ARTICULATION_CFG = ArticulationCfg(
    spawn=UsdFileCfg(
        usd_path=str(USD_PATH),
        rigid_props=RigidBodyPropertiesCfg(
            disable_gravity=False,
            max_depenetration_velocity=5.0,
        ),
        articulation_props=ArticulationRootPropertiesCfg(
            enabled_self_collisions=False,
            solver_position_iteration_count=16,
            solver_velocity_iteration_count=1,
        ),
        activate_contact_sensors=False,
    ),
    init_state=ArticulationCfg.InitialStateCfg(joint_pos=dict(zip(JOINT_NAMES, INITIAL_POSITION))),
    actuators={
        "shoulder": ImplicitActuatorCfg(
            joint_names_expr=_ARM_JOINTS,
            stiffness=dict(zip(_ARM_JOINTS, STIFFNESS[:2])),
            damping=dict(zip(_ARM_JOINTS, DAMPING[:2])),
            effort_limit_sim=150.0,
            velocity_limit_sim=math.pi,
        ),
        "elbow": ImplicitActuatorCfg(
            joint_names_expr=["elbow_joint"],
            stiffness=dict(zip(["elbow_joint"], STIFFNESS[2:3])),
            damping=dict(zip(["elbow_joint"], DAMPING[2:3])),
            effort_limit_sim=150.0,
            velocity_limit_sim=math.pi,
        ),
        "wrist": ImplicitActuatorCfg(
            joint_names_expr=_WRIST_JOINTS,
            stiffness=dict(zip(_WRIST_JOINTS, STIFFNESS[3:])),
            damping=dict(zip(_WRIST_JOINTS, DAMPING[3:])),
            effort_limit_sim=28.0,
            velocity_limit_sim=math.pi,
        ),
    },
)

##
# Scene
##


@configclass
class UR5ReachSceneCfg(InteractiveSceneCfg):
    """Scene for the fixed-base UR5 reach task."""

    ground = AssetBaseCfg(
        prim_path="/World/ground",
        spawn=sim_utils.GroundPlaneCfg(),
    )
    robot: ArticulationCfg = MISSING
    light = AssetBaseCfg(
        prim_path="/World/light",
        spawn=sim_utils.DomeLightCfg(color=(0.75, 0.75, 0.75), intensity=2500.0),
    )


##
# MDP
##


@configclass
class CommandsCfg:
    """Command terms for the MDP."""

    ee_pose = UniformPoseCommandCfg(
        asset_name="robot",
        body_name="flange",
        resampling_time_range=(4.0, 4.0),
        debug_vis=True,
        position_success_threshold=0.05,
        ranges=UniformPoseCommandCfg.Ranges(
            pos_x=(0.25, 0.65),
            pos_y=(-0.35, 0.35),
            pos_z=(0.1, 0.55),
            roll=(0.0, 0.0),
            pitch=(math.pi / 2, math.pi / 2),
            yaw=(-math.pi, math.pi),
        ),
    )


@configclass
class ActionsCfg:
    """Action specifications for the MDP."""

    arm_action: ActionTerm = MISSING


@configclass
class ObservationsCfg:
    """Observation specifications for the MDP."""

    @configclass
    class PolicyCfg(ObsGroup):
        """Observations for the policy group."""

        joint_pos = ObsTerm(
            func=joint_pos_rel,
            params={"asset_cfg": _JOINT_CFG},
            noise=Unoise(n_min=-0.01, n_max=0.01),
        )
        joint_vel = ObsTerm(
            func=joint_vel_rel,
            params={"asset_cfg": _JOINT_CFG},
            noise=Unoise(n_min=-0.01, n_max=0.01),
        )
        pose_command = ObsTerm(func=generated_commands, params={"command_name": "ee_pose"})
        actions = ObsTerm(func=last_action)

        def __post_init__(self):
            self.enable_corruption = True
            self.concatenate_terms = True

    policy: PolicyCfg = PolicyCfg()


@configclass
class EventCfg:
    """Configuration for events."""

    reset_robot_joints = EventTerm(
        func=reset_joints_by_scale,
        mode="reset",
        params={
            "position_range": (0.5, 1.5),
            "velocity_range": (0.0, 0.0),
            "asset_cfg": _JOINT_CFG,
        },
    )


@configclass
class RewardsCfg:
    """Reward terms for the MDP."""

    end_effector_position_tracking = RewTerm(
        func=position_command_error,
        weight=-0.2,
        params={"asset_cfg": SceneEntityCfg("robot", body_names=["flange"]), "command_name": "ee_pose"},
    )
    end_effector_position_tracking_fine_grained = RewTerm(
        func=position_command_error_tanh,
        weight=0.1,
        params={"asset_cfg": SceneEntityCfg("robot", body_names=["flange"]), "std": 0.1, "command_name": "ee_pose"},
    )
    end_effector_orientation_tracking = RewTerm(
        func=orientation_command_error,
        weight=-0.05,
        params={"asset_cfg": SceneEntityCfg("robot", body_names=["flange"]), "command_name": "ee_pose"},
    )
    action_rate = RewTerm(func=action_rate_l2, weight=-0.0001)
    joint_vel = RewTerm(func=joint_vel_l2, weight=-0.0001, params={"asset_cfg": _JOINT_CFG})


@configclass
class TerminationsCfg:
    """Termination terms for the MDP."""

    time_out = DoneTerm(func=time_out, time_out=True)


##
# Environment
##


@configclass
class UR5ReachEnvCfg(ManagerBasedRLEnvCfg):
    """Configuration for the UR5 end-effector reach task."""

    scene: UR5ReachSceneCfg = UR5ReachSceneCfg(num_envs=1024, env_spacing=2.5)
    observations: ObservationsCfg = ObservationsCfg()
    actions: ActionsCfg = ActionsCfg()
    commands: CommandsCfg = CommandsCfg()
    rewards: RewardsCfg = RewardsCfg()
    terminations: TerminationsCfg = TerminationsCfg()
    events: EventCfg = EventCfg()

    def __post_init__(self):
        self.decimation = 2
        self.sim.render_interval = self.decimation
        self.episode_length_s = 12.0
        self.viewer.eye = (3.5, 3.5, 3.5)
        self.sim.dt = 1.0 / 60.0
        self.scene.robot = UR5_ARTICULATION_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")
        self.actions.arm_action = JointPositionActionCfg(
            asset_name="robot",
            joint_names=list(JOINT_NAMES),
            scale=0.5,
            use_default_offset=True,
        )


@configclass
class UR5ReachEnvCfg_PLAY(UR5ReachEnvCfg):
    """Smaller, non-randomized configuration for playback."""

    def __post_init__(self):
        super().__post_init__()
        self.scene.num_envs = 50
        self.observations.policy.enable_corruption = False
