param(
    [switch]$Apply
)

$ErrorActionPreference = 'Stop'
$target = 'C:\Program Files\Epic Games\UE_4.27\Engine\Content\EngineMaterials\WorldGridMaterial.uasset'

if (-not (Test-Path -LiteralPath $target -PathType Leaf)) {
    Write-Error "Target file is missing: $target"
    exit 40
}

Write-Host 'Current ACL:'
& icacls.exe $target
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if (-not $Apply) {
    Write-Host ''
    Write-Host 'Dry run only. Re-run this script from an elevated PowerShell with -Apply to reset this file to inherited parent permissions.'
    exit 0
}

$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error 'This repair must be run from an elevated Administrator PowerShell.'
    exit 41
}

Write-Host 'Resetting file ACL to inherit from the EngineMaterials parent directory...'
& icacls.exe $target /reset
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host 'ACL after reset:'
& icacls.exe $target
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host 'Testing read access as the current elevated user...'
$stream = [System.IO.File]::OpenRead($target)
$stream.Dispose()
Write-Host 'WorldGridMaterial ACL reset completed. The self-hosted runner preflight must still verify NETWORK SERVICE access on the next CI run.'
exit 0
