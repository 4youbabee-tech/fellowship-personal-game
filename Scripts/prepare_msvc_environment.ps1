# Process/job-local environment only. No registry, service or security changes.
$ErrorActionPreference = 'Stop'
$root = Join-Path $env:RUNNER_TEMP ("shire-msvc-" + $env:GITHUB_RUN_ID + '-' + $env:GITHUB_RUN_ATTEMPT)
New-Item -ItemType Directory -Path $root -Force | Out-Null
$probe = Join-Path $root 'compiler_probe.cpp'
Set-Content -LiteralPath $probe -Value 'int shire_compiler_probe() { return 42; }' -Encoding ascii
$env:TEMP = $root
$env:TMP = $root
Add-Content -LiteralPath $env:GITHUB_ENV -Value "TEMP=$root" -Encoding utf8
Add-Content -LiteralPath $env:GITHUB_ENV -Value "TMP=$root" -Encoding utf8

# The self-hosted service has repeatedly hit MSVC D8050 while c1xx records full
# debug command lines during UE builds. Exact-head CI validates compile/runtime
# correctness, not debugger symbol quality, so disable debug info only for this
# CI target. Local/editor developer builds remain untouched.
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
