# Stable tracked bootstrap used from a CMD step so the self-hosted runner
# does not depend on a transient generated PowerShell script in _work\_temp.
$ErrorActionPreference = "Stop"

$git = Get-Command git.exe -ErrorAction SilentlyContinue
if (-not $git) {
    foreach ($candidate in @(
        "C:\Program Files\Git\cmd\git.exe",
        "C:\Program Files (x86)\Git\cmd\git.exe"
    )) {
        if (Test-Path $candidate) {
            $gitDir = Split-Path -Parent $candidate
            Add-Content -LiteralPath $env:GITHUB_PATH -Value $gitDir
            $env:PATH = "$gitDir;$env:PATH"
            $git = Get-Command git.exe -ErrorAction SilentlyContinue
            if ($git) { break }
        }
    }
}

if (-not $git) {
    Write-Host "Git is not visible to the Windows service. Bootstrapping private MinGit for CI..."
    $root = Join-Path $env:RUNNER_TEMP "mingit-2.55.0.5"
    $zip = Join-Path $env:RUNNER_TEMP "MinGit-2.55.0.5-64-bit.zip"
    $url = "https://github.com/git-for-windows/git/releases/download/v2.55.0.windows.5/MinGit-2.55.0.5-64-bit.zip"

    if (-not (Test-Path (Join-Path $root "cmd\git.exe"))) {
        if (Test-Path $root) { Remove-Item -LiteralPath $root -Recurse -Force }
        if (Test-Path $zip) { Remove-Item -LiteralPath $zip -Force }
        & curl.exe -L --retry 3 --retry-delay 3 -o $zip $url
        if ($LASTEXITCODE -ne 0) { exit 20 }
        Expand-Archive -LiteralPath $zip -DestinationPath $root -Force
    }

    $gitDir = Join-Path $root "cmd"
    $gitBin = Join-Path $root "mingw64\bin"
    Add-Content -LiteralPath $env:GITHUB_PATH -Value $gitDir
    Add-Content -LiteralPath $env:GITHUB_PATH -Value $gitBin
    $env:PATH = "$gitDir;$gitBin;$env:PATH"
    $git = Get-Command git.exe -ErrorAction SilentlyContinue
}

if (-not $git) {
    Write-Error "Git bootstrap did not produce a working git.exe."
    exit 22
}

Write-Host "Found Git: $($git.Source)"
& git --version
if ($LASTEXITCODE -ne 0) { exit 22 }
Write-Host "Runner bootstrap succeeded."
exit 0
