$ErrorActionPreference = "Stop"

param(
  [switch]$IncludeHeavy,
  [string]$Mirror = "https://pypi.tuna.tsinghua.edu.cn/simple"
)

$repoRoot = Split-Path -Parent $PSScriptRoot
$venvDir = Join-Path $repoRoot ".venv"
$pythonExe = Join-Path $venvDir "Scripts\\python.exe"
$pipExe = Join-Path $venvDir "Scripts\\pip3.11.exe"

Write-Host "[1/4] Create or reuse .venv"
if (-not (Test-Path $pythonExe)) {
  uv venv $venvDir --python 3.11 | Out-Null
}

Write-Host "[2/4] Ensure pip"
& $pythonExe -m ensurepip --upgrade | Out-Null

Write-Host "[3/4] Install core packages"
& $pipExe install -i $Mirror pyyaml markdown markitdown mineru-open-sdk

if ($IncludeHeavy) {
  Write-Host "[4/4] Install heavy package: magic-pdf"
  & $pipExe install -i $Mirror --default-timeout 1000 magic-pdf
} else {
  Write-Host "[4/4] Skip heavy package: magic-pdf"
}

Write-Host "Done. Run:"
Write-Host "  .\\.venv\\Scripts\\python.exe .\\scripts\\tooling_doctor.py"
Write-Host "  .\\.venv\\Scripts\\python.exe .\\scripts\\mineru_api_doctor.py"
