param(
    [string]$IsaacRoot = "G:\Isaac\RL_UR5",
    [string]$ProjectDir = "D:\Sis\Documents\RL_UR5",
    [string]$TorchVersion = "2.11.0",
    [string]$IsaacSimVersion = "6.0.1.0",
    [string]$IsaacLabVersion = "v3.0.0-beta2.patch1",
    [switch]$InstallIsaacSim,
    [switch]$InstallIsaacLab,
    [switch]$SkipVenv
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $ProjectDir)) {
    throw "Project directory does not exist: $ProjectDir"
}

$VenvDir = Join-Path $IsaacRoot ".venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"

# Keep package managers, wheels, and temporary extraction files off C:.
$env:UV_PYTHON_INSTALL_DIR = Join-Path $IsaacRoot "python"
$env:UV_CACHE_DIR = Join-Path $IsaacRoot "cache\uv"
$env:PIP_CACHE_DIR = Join-Path $IsaacRoot "cache\pip"
$env:TMP = Join-Path $IsaacRoot "tmp"
$env:TEMP = $env:TMP

$directories = @(
    $env:UV_PYTHON_INSTALL_DIR,
    $env:UV_CACHE_DIR,
    $env:PIP_CACHE_DIR,
    $env:TMP
)
foreach ($directory in $directories) {
    New-Item -ItemType Directory -Force -Path $directory | Out-Null
}

if (-not $SkipVenv) {
    if (Test-Path -LiteralPath $VenvPython) {
        Write-Host "Using existing virtual environment: $VenvDir"
    }
    else {
        Write-Host "Creating Python 3.12 environment in $VenvDir"
        uv venv --python 3.12 --seed $VenvDir
    }
}

if (-not (Test-Path -LiteralPath $VenvPython)) {
    throw "Virtual environment Python was not found: $VenvPython"
}

& $VenvPython -m pip install --upgrade pip

if ($InstallIsaacSim) {
    Write-Host "Installing PyTorch $TorchVersion (CUDA 12.8)"
    & $VenvPython -m pip install "torch==$TorchVersion" `
        --index-url https://download.pytorch.org/whl/cu128
    if ($LASTEXITCODE -ne 0) { throw "PyTorch installation failed" }

    Write-Host "Installing Isaac Sim $IsaacSimVersion"
    & $VenvPython -m pip install "isaacsim[all,extscache]==$IsaacSimVersion" `
        --extra-index-url https://pypi.nvidia.com
    if ($LASTEXITCODE -ne 0) { throw "Isaac Sim installation failed" }
}

$IsaacLabDir = Join-Path $IsaacRoot "IsaacLab"
if ($InstallIsaacLab) {
    if (-not (Test-Path -LiteralPath $IsaacLabDir)) {
        Write-Host "Cloning Isaac Lab $IsaacLabVersion"
        git clone https://github.com/isaac-sim/IsaacLab.git $IsaacLabDir `
            --branch $IsaacLabVersion
        if ($LASTEXITCODE -ne 0) { throw "Isaac Lab clone failed" }
    }

    Push-Location $IsaacLabDir
    try {
        Write-Host "Installing Isaac Lab source package"
        .\isaaclab.bat --install
        if ($LASTEXITCODE -ne 0) { throw "Isaac Lab installation failed" }
    }
    finally {
        Pop-Location
    }

    Write-Host "Installing this project in editable mode"
    & $VenvPython -m pip install -e $ProjectDir
    if ($LASTEXITCODE -ne 0) { throw "Project installation failed" }
}

Write-Host ""
Write-Host "Environment root: $IsaacRoot"
Write-Host "Project: $ProjectDir"
Write-Host "Python: $VenvPython"
if (-not $InstallIsaacSim) {
    Write-Host "Isaac Sim was not installed. Re-run with -InstallIsaacSim when network allows."
}
if (-not $InstallIsaacLab) {
    Write-Host "Isaac Lab was not downloaded or installed."
}
