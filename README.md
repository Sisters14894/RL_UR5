# RL\_UR5

UR5 reinforcement learning workspace. Source code and Git history live on `D:`; the reproducible Python environment and package caches live on `G:`.

## Directory Layout

Repository on the local machine:

```text
D:\Sis\Documents\RL_UR5
├── .env.example          # Example machine-specific path configuration
├── .gitattributes
├── .gitignore
├── README.md
├── assets/               # Robot and scene assets added intentionally
├── configs/              # Robot, task, training, and evaluation configs
├── pyproject.toml
├── scripts/
│   ├── setup-env.ps1     # Environment creation and full reproduction script
│   └── verify-env.py     # No-download environment inspection
└── src/ur5_rl/           # Project package
```

Recreatable heavyweight environment on `G:`:

```text
G:\Isaac\RL_UR5
├── .venv/                # Python 3.12 virtual environment
├── python/               # Managed Python installations used by uv
├── cache/
│   ├── pip/              # pip wheel cache
│   └── uv/               # uv package/cache
├── tmp/                  # Temporary extraction files during installation
└── IsaacLab/             # Isaac Lab source checkout
```

Only the `D:` directory is a Git repository. The `G:` directory is disposable and can be recreated with the setup script.

## Basic Environment

Create only the Python 3.12 virtual environment:

```powershell
cd D:\Sis\Documents\RL_UR5
powershell -ExecutionPolicy Bypass -File .\scripts\setup-env.ps1
```

This does **not** download Isaac Sim or Isaac Lab. It only creates the G-drive environment and installs the current version of pip inside it.

Inspect the environment without downloading anything:

```powershell
$env:ISAAC_ROOT = "G:\Isaac\RL_UR5"
G:\Isaac\RL_UR5\.venv\Scripts\python.exe .\scripts\verify-env.py
```

Activate the environment for development:

```powershell
G:\Isaac\RL_UR5\.venv\Scripts\Activate.ps1
```

## Full Reproduction

When the network can handle the large downloads, run:

```powershell
cd D:\Sis\Documents\RL_UR5
powershell -ExecutionPolicy Bypass -File .\scripts\setup-env.ps1 `
  -InstallIsaacSim `
  -InstallIsaacLab
```

The full reproduction path performs these actions:

1. Creates `G:\Isaac\RL_UR5` and its cache/temp directories.
2. Creates a Python 3.12 virtual environment at `G:\Isaac\RL_UR5\.venv`.
3. Installs PyTorch 2.11.0 from the CUDA 12.8 wheel index.
4. Installs Isaac Sim 6.0.1.0 with the `all` and `extscache` extras.
5. Clones Isaac Lab at `v3.0.0-beta2.patch1`.
6. Installs Isaac Lab and this project in editable mode.
7. Leaves the Git repository on `D:` untouched except for source code edits.

For a new machine, change the default `IsaacRoot` and `ProjectDir` parameters:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup-env.ps1 `
  -IsaacRoot "G:\Isaac\RL_UR5" `
  -ProjectDir "D:\Sis\Documents\RL_UR5" `
  -InstallIsaacSim `
  -InstallIsaacLab
```

## Path Configuration

Copy `.env.example` to `.env` for local tools that need the G-drive root:

```powershell
Copy-Item .env.example .env
```

`.env` is ignored by Git because it describes this particular machine.

## Git Workflow

Use the Source Control panel in VS Code for daily changes, or:

```powershell
git status
git add .
git commit -m "Describe the change"
git push
```

Training artifacts such as logs, TensorBoard events, checkpoints, generated USD files, and model weights are intentionally ignored. Small source assets can be committed directly. Large final weights should be attached to a GitHub Release or tracked with Git LFS rather than stored in ordinary Git history.
