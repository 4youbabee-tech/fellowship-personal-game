# Process/job-local environment only. No registry, service or security changes.
$ErrorActionPreference = 'Stop'

# Use one stable compiler temp root on this single supervised self-hosted runner.
# UE4/UBT incremental action metadata can retain compiler command lines between jobs.
# A run-id-specific TEMP path therefore becomes invalid as soon as the next job starts
# and has caused C1083 failures against deleted _CL_* files from the previous run.
$root = Join-Path $env:RUNNER_TEMP 'shire-msvc-active'
$stamp = Join-Path $env:GITHUB_WORKSPACE 'Intermediate\.shire-ci-msvc-temp-root.txt'
$buildRoot = Join-Path $env:GITHUB_WORKSPACE 'Intermediate\Build\Win64'
$previousRoot = ''
if (Test-Path -LiteralPath $stamp -PathType Leaf) {
    $previousRoot = (Get-Content -LiteralPath $stamp -Raw).Trim()
}

$needsCompileReset = (Test-Path -LiteralPath $buildRoot -PathType Container) -and
    ([string]::IsNullOrWhiteSpace($previousRoot) -or
     -not $previousRoot.Equals($root, [System.StringComparison]::OrdinalIgnoreCase))

if ($needsCompileReset) {
    Write-Host ("MSVC_TEMP_ROOT_MIGRATION_RESET previous=" + $previousRoot + " current=" + $root)
    & (Join-Path $env:GITHUB_WORKSPACE 'Scripts\reset_project_build_intermediates.ps1')
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to reset project intermediates during compiler-temp root migration."
    }
}

if (Test-Path -LiteralPath $root) {
    try { attrib -R -S -H ($root + '\*') /S /D 2>$null | Out-Null } catch {}
    Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction Stop
}
New-Item -ItemType Directory -Path $root -Force | Out-Null

$stampDir = Split-Path -Parent $stamp
New-Item -ItemType Directory -Path $stampDir -Force | Out-Null
Set-Content -LiteralPath $stamp -Value $root -Encoding ASCII

$probe = Join-Path $root 'compiler_probe.cpp'
Set-Content -LiteralPath $probe -Value 'int shire_compiler_probe() { return 42; }' -Encoding ascii
$env:TEMP = $root
$env:TMP = $root
Add-Content -LiteralPath $env:GITHUB_ENV -Value "TEMP=$root" -Encoding utf8
Add-Content -LiteralPath $env:GITHUB_ENV -Value "TMP=$root" -Encoding utf8

# Exact-head CI validates compile/runtime correctness, not debugger symbol quality.
$env:SHIRE_CI_NO_DEBUGINFO = "1"
Add-Content -LiteralPath $env:GITHUB_ENV -Value "SHIRE_CI_NO_DEBUGINFO=1" -Encoding utf8
Write-Host "CI editor target debug info: disabled (SHIRE_CI_NO_DEBUGINFO=1)"
if ([string]::IsNullOrWhiteSpace($env:USERPROFILE)) {
    $profilePath = [Environment]::GetFolderPath([Environment+SpecialFolder]::UserProfile)
    if ($profilePath -and (Test-Path -LiteralPath $profilePath)) {
        $env:USERPROFILE = $profilePath
        Add-Content -LiteralPath $env:GITHUB_ENV -Value "USERPROFILE=$profilePath" -Encoding utf8
    }
}
Write-Host "Compiler temp directory is writable: $root"
Write-Host "Compiler temp root policy: stable-single-runner root with stale-intermediate migration reset"
Write-Host "Service profile present: $(-not [string]::IsNullOrWhiteSpace($env:USERPROFILE))"
$compiler = 'C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\bin\HostX64\x64\cl.exe'
if (-not (Test-Path -LiteralPath $compiler)) {
    Write-Host 'Known toolchain path absent; UnrealBuildTool will select and diagnose the installed compiler.'
    exit 0
}
$failed = $false
foreach ($mode in @('plain', 'Z7', 'Zi')) {
    $object = Join-Path $root ("probe_$mode.obj")
    $pdb = Join-Path $root ("probe_$mode.pdb")
    $arguments = @('/nologo', '/c', $probe, "/Fo$object", "/Fd$pdb")
    if ($mode -ne 'plain') { $arguments += "/$mode" }
    Write-Host "MSVC isolated probe: $mode"
    $ErrorActionPreference = 'Continue'
    & $compiler @arguments 2>&1 | ForEach-Object { Write-Host $_ }
    $code = $LASTEXITCODE
    $ErrorActionPreference = 'Stop'
    Write-Host "MSVC probe $mode exit=$code objectExists=$(Test-Path -LiteralPath $object)"
    if ($code -ne 0 -or -not (Test-Path -LiteralPath $object)) { $failed = $true }
}
if ($failed) {
    Write-Host 'MSVC failed an isolated one-line source probe. This is toolchain/environment failure, not evidence of a gameplay compilation error.'
    exit 76
}
exit 0
