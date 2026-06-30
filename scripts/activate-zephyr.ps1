# Activate the Zephyr development environment for this terminal session.
# Usage: . .\scripts\activate-zephyr.ps1
#
# This script must be dot-sourced (run with leading ". ") so the PATH and venv
# activation persist in the current shell.

$ZephyrWorkspace = "$env:HOMEPATH\zephyrproject"

if (-not (Test-Path "$ZephyrWorkspace\.venv\Scripts\Activate.ps1")) {
    Write-Error "Zephyr venv not found at $ZephyrWorkspace\.venv. Run the setup first."
    return
}

# Refresh PATH from the registry (picks up tools installed by winget: cmake,
# ninja, dtc, gperf, 7zip) — needed because winget modifies the system PATH
# but existing shells don't see the changes until restarted.
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
            [System.Environment]::GetEnvironmentVariable("Path", "User")

# Activate the Python 3.12 venv (contains west + Zephyr Python deps)
& "$ZephyrWorkspace\.venv\Scripts\Activate.ps1"

Write-Host "Zephyr environment active." -ForegroundColor Green
Write-Host "  Workspace : $ZephyrWorkspace"
Write-Host "  Zephyr    : $(west --version)"
Write-Host "  Board     : nucleo_h753zi"
Write-Host ""
Write-Host "Build a sample:"
Write-Host "  cd $ZephyrWorkspace\zephyr"
Write-Host "  west build -p always -b nucleo_h753zi samples/basic/blinky"
