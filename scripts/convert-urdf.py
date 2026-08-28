"""Convert the project UR5 URDF into a USD asset.

The generated USD is written below ``assets/ur5/usd`` and is gitignored, matching
the repository policy for large generated simulation artifacts.

Usage:
    G:\\Isaac\\RL_UR5\\.venv\\Scripts\\python.exe scripts\\convert-urdf.py --headless
"""

from __future__ import annotations

import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

from isaaclab.app import AppLauncher  # noqa: E402

parser = argparse.ArgumentParser(description="Convert the project UR5 URDF into USD.")
parser.add_argument(
    "--input",
    type=Path,
    default=PROJECT_ROOT / "assets" / "ur5" / "ur5.urdf",
    help="Path to the input URDF file.",
)
parser.add_argument(
    "--output-dir",
    type=Path,
    default=PROJECT_ROOT / "assets" / "ur5" / "usd",
    help="Directory where the generated USD asset is stored.",
)
parser.add_argument(
    "--force",
    action="store_true",
    help="Re-run the conversion even if the USD output already exists.",
)
parser.add_argument(
    "--merge-fixed-joints",
    action="store_true",
    help="Merge fixed joints into their parent link (drops the flange tool frame).",
)

AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()

app_launcher = AppLauncher(args)
simulation_app = app_launcher.app

"""Rest everything follows."""

from ur5_rl.configs.ur5 import DAMPING, JOINT_NAMES, STIFFNESS  # noqa: E402
from isaaclab.sim.converters import UrdfConverter, UrdfConverterCfg  # noqa: E402
from isaaclab.utils.assets import check_file_path  # noqa: E402


def inspect_usd(usd_path: Path) -> None:
    """Print the revolute joints found in the generated USD stage."""
    from pxr import Usd, UsdPhysics

    stage = Usd.Stage.Open(str(usd_path))
    joints = [
        prim.GetName()
        for prim in stage.Traverse()
        if prim.IsA(UsdPhysics.RevoluteJoint)
    ]
    print(f"Revolute joints ({len(joints)}): {joints}")


def main() -> None:
    input_path = args.input.resolve()
    output_dir = args.output_dir.resolve()

    if not check_file_path(str(input_path)):
        raise ValueError(f"Invalid URDF path: {input_path}")

    output_dir.mkdir(parents=True, exist_ok=True)
    if args.force:
        import shutil

        expected_dir = output_dir / input_path.stem
        if expected_dir.is_dir() and expected_dir.resolve().is_relative_to(output_dir.resolve()):
            shutil.rmtree(expected_dir.resolve())

    converter_cfg = UrdfConverterCfg(
        asset_path=str(input_path),
        usd_dir=str(output_dir),
        fix_base=True,
        merge_fixed_joints=args.merge_fixed_joints,
        force_usd_conversion=args.force,
        robot_type="Manipulator",
        joint_drive=UrdfConverterCfg.JointDriveCfg(
            gains=UrdfConverterCfg.JointDriveCfg.PDGainsCfg(
                stiffness=dict(zip(JOINT_NAMES, STIFFNESS)),
                damping=dict(zip(JOINT_NAMES, DAMPING)),
            ),
            drive_type="force",
            target_type="position",
        ),
    )

    print(f"Input URDF: {input_path}")
    print(f"Output directory: {output_dir}")

    converter = UrdfConverter(converter_cfg)
    usd_path = Path(converter.usd_path)
    if not usd_path.exists():
        raise FileNotFoundError(f"Conversion did not produce USD file: {usd_path}")

    print(f"Generated USD file: {usd_path}")
    inspect_usd(usd_path)


if __name__ == "__main__":
    main()
    simulation_app.close()
