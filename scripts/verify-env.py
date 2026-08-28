from __future__ import annotations

import importlib.util
import os
import platform
import sys
from pathlib import Path


def main() -> int:
    print(f"Python version: {platform.python_version()}")
    print(f"Python executable: {sys.executable}")
    print(f"Platform: {platform.platform()}")
    print(f"ISAAC_ROOT: {os.environ.get('ISAAC_ROOT', '<not set>')}")

    expected_root = os.environ.get("ISAAC_ROOT")
    if expected_root:
        print(f"Isaac root exists: {Path(expected_root).exists()}")

    for package in ("torch", "isaacsim", "isaaclab", "isaaclab_rl", "isaaclab_tasks", "rsl_rl"):
        status = "installed" if importlib.util.find_spec(package) else "not installed"
        print(f"{package}: {status}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
