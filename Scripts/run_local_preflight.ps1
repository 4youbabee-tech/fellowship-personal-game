$ErrorActionPreference = 'Stop'

$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$candidates = New-Object 'System.Collections.Generic.List[string]'

foreach ($command in @(Get-Command python.exe -All -ErrorAction SilentlyContinue)) {
    $candidates.Add($command.Source)
}
$launcher = Get-Command py.exe -ErrorAction SilentlyContinue
if ($launcher) {
    try {
        $resolved = & $launcher.Source -3 -c 'import sys; print(sys.executable)' 2>$null
        if ($LASTEXITCODE -eq 0) {
            foreach ($path in @($resolved)) { $candidates.Add([string]$path) }
        }
    } catch {}
}
foreach ($pattern in @(
    "$env:LOCALAPPDATA\Programs\Python\Python*\python.exe",
    'C:\Python*\python.exe',
    'C:\Program Files\Python*\python.exe',
    "$env:RUNNER_TOOL_CACHE\Python\*\x64\python.exe",
    'C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\ThirdParty\Python3\Win64\python.exe'
)) {
    foreach ($file in @(Get-ChildItem -Path $pattern -File -ErrorAction SilentlyContinue)) {
        $candidates.Add($file.FullName)
    }
}

$PythonExe = $null
foreach ($candidate in @($candidates | Select-Object -Unique)) {
    if ($candidate -match '(?i)\Microsoft\WindowsApps\' -or -not (Test-Path -LiteralPath $candidate -PathType Leaf)) { continue }
    try {
        & $candidate -c 'import sys, argparse, json, pathlib, re, subprocess, time; sys.exit(0 if sys.version_info >= (3,7) else 1)' 2>$null
        if ($LASTEXITCODE -eq 0) { $PythonExe = $candidate; break }
    } catch {}
}
if (-not $PythonExe) {
    Write-Error 'No working local Python 3.7+ interpreter found. Pre-Unreal checks were not executed.'
    exit 60
}

Set-Location -LiteralPath $Root
Write-Host "Local Pre-Unreal Python: $PythonExe"

function Invoke-PythonStep {
    param([string]$Label,[string[]]$CommandArgs)
    Write-Host ""
    Write-Host "== $Label =="
    & $PythonExe @CommandArgs
    if ($LASTEXITCODE -ne 0) {
        Write-Error "$Label failed with exit code $LASTEXITCODE."
        exit $LASTEXITCODE
    }
}

Invoke-PythonStep 'Project structure / static validation' @('Scripts/pre_unreal_validate.py')
Invoke-PythonStep 'Project Governor validation' @('Scripts/project_governor.py')
Invoke-PythonStep 'Production asset source audit' @('Scripts/asset_quality_audit.py')
Invoke-PythonStep 'Production readiness contracts' @('Scripts/production_readiness_audit.py')
Invoke-PythonStep 'Deep project architecture audit' @('Scripts/deep_project_audit.py')
Invoke-PythonStep 'Runtime observer regression tests' @('-m','unittest','discover','-s','Scripts','-p','test_runtime_smoke.py','-v')
Invoke-PythonStep 'Warning-debt guard tests' @('-m','unittest','discover','-s','Scripts','-p','test_warning_debt_guard.py','-v')
Invoke-PythonStep 'Deep-audit regression tests' @('-m','unittest','discover','-s','Scripts','-p','test_deep_project_audit.py','-v')
Invoke-PythonStep 'Governor handoff evidence tests' @('-m','unittest','discover','-s','Scripts','-p','test_governor_handoff.py','-v')
Invoke-PythonStep 'Streaming cancellation contract tests' @('-m','unittest','discover','-s','Scripts','-p','test_streaming_cancellation_contract.py','-v')

Write-Host ""
Write-Host 'LOCAL PRE-UNREAL PREFLIGHT PASSED'
exit 0
