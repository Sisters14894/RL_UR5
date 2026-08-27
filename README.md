# RL_UR5

UR5 强化学习工作区。源代码和 Git 历史保存在 `D:` 盘；可重建的 Python 环境、包缓存和大型依赖保存在 `G:` 盘。

## 目录结构

本地仓库位于：

```text
D:\Sis\Documents\RL_UR5
├── .env.example          # 本机路径配置示例
├── .gitattributes
├── .gitignore
├── README.md
├── assets/               # 机器人和场景资产，按需手动加入
├── configs/              # 机器人、任务、训练和评测配置
├── pyproject.toml
├── scripts/
│   ├── setup-env.ps1     # 环境创建和完整复现脚本
│   └── verify-env.py     # 无下载的环境检查脚本
└── src/ur5_rl/           # 项目 Python 包
```

`G:` 盘保存可随时重建的大型环境：

```text
G:\Isaac\RL_UR5
├── .venv/                # Python 3.12 虚拟环境
├── python/               # uv 管理的 Python 安装
├── cache/
│   ├── pip/              # pip wheel 缓存
│   └── uv/               # uv 包缓存
├── tmp/                  # 安装期间的临时解包文件
└── IsaacLab/             # Isaac Lab 源码
```

只有 `D:` 盘目录是 Git 仓库。`G:` 盘目录是可丢弃、可重建的，通过安装脚本恢复。

## 基础环境

只创建 Python 3.12 虚拟环境：

```powershell
cd D:\Sis\Documents\RL_UR5
powershell -ExecutionPolicy Bypass -File .\scripts\setup-env.ps1
```

这一步**不会**下载 Isaac Sim 或 Isaac Lab，只会在 `G:` 盘创建环境，并在虚拟环境中安装当前版本的 pip。

不下载任何文件，检查当前环境：

```powershell
$env:ISAAC_ROOT = "G:\Isaac\RL_UR5"
G:\Isaac\RL_UR5\.venv\Scripts\python.exe .\scripts\verify-env.py
```

日常开发时激活虚拟环境：

```powershell
G:\Isaac\RL_UR5\.venv\Scripts\Activate.ps1
```

## 完整复现

当网络可以承受大文件下载时，运行：

```powershell
cd D:\Sis\Documents\RL_UR5
powershell -ExecutionPolicy Bypass -File .\scripts\setup-env.ps1 `
  -InstallIsaacSim `
  -InstallIsaacLab
```

完整复现流程会依次完成：

1. 创建 `G:\Isaac\RL_UR5` 以及缓存、临时目录。
2. 在 `G:\Isaac\RL_UR5\.venv` 创建 Python 3.12 虚拟环境。
3. 从 CUDA 12.8 wheel 源安装 PyTorch 2.11.0。
4. 安装 Isaac Sim 6.0.1.0，并启用 `all` 和 `extscache` extras。
5. 克隆 `v3.0.0-beta2.patch1` 版本的 Isaac Lab。
6. 安装 Isaac Lab，并以 editable 模式安装本项目。
7. 不改动 `D:` 盘 Git 仓库，除了项目源码本身。

换新机器时，可以显式传入 `IsaacRoot` 和 `ProjectDir`：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup-env.ps1 `
  -IsaacRoot "G:\Isaac\RL_UR5" `
  -ProjectDir "D:\Sis\Documents\RL_UR5" `
  -InstallIsaacSim `
  -InstallIsaacLab
```

## 路径配置

如果本地工具需要读取 `G:` 盘环境根目录，复制一份 `.env.example`：

```powershell
Copy-Item .env.example .env
```

`.env` 已被 Git 忽略，因为它记录的是当前机器的路径。

## Git 工作流

日常修改可以在 VS Code 的 Source Control 面板完成，也可以使用命令行：

```powershell
git status
git add .
git commit -m "Describe the change"
git push
```

训练日志、TensorBoard 事件、checkpoint、生成的 USD 文件和模型权重默认不进入 Git。小型源码资产可以直接提交；最终大型权重建议放在 GitHub Release 或使用 Git LFS，而不是存入普通 Git 历史。
