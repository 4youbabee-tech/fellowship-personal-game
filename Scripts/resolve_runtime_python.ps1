# Use an existing interpreter; never install software or modify Windows aliases.
$ErrorActionPreference = 'Stop'
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
    } catch { Write-Host 'Python launcher unavailable; checking local installations.' }
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
foreach ($candidate in @($candidates | Select-Object -Unique)) {
    # App execution aliases may open the Store rather than run Python.
    if ($candidate -match '(?i)\\Microsoft\\WindowsApps\\' -or
        -not (Test-Path -LiteralPath $candidate -PathType Leaf)) { continue }
    try {
        $probe = & $candidate -c 'import sys, argparse, json, pathlib, re, subprocess, time; sys.exit(0 if sys.version_info >= (3,7) else 1)' 2>&1
        if ($LASTEXITCODE -ne 0) { continue }
        & $candidate --version
        Add-Content -LiteralPath $env:GITHUB_ENV -Value "PYTHON_EXE=$candidate" -Encoding utf8
        Write-Host "Validated runtime observer Python: $candidate"
        exit 0
    } catch {
        Write-Host "Skipping unusable Python candidate: $candidate"
    }
}
Write-Error 'No working local Python 3.7+ interpreter found, including the UE4 bundled interpreter. Runtime audits were not executed.'
exit 60
