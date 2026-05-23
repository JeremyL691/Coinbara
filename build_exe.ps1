$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

Set-Location $projectRoot

if (Get-Command python -ErrorAction SilentlyContinue) {
    $python = "python"
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $python = "py"
} else {
    throw "Python was not found on PATH. Install Python 3.11+ or run PyInstaller manually with your Python executable."
}

& $python -m pip install -r requirements.txt
& $python -m pip install -r requirements-packaging.txt
& $python -m PyInstaller --noconfirm --clean Coinbara.spec
