param(
    [string]$EngineRoot = "C:\Program Files\Epic Games\UE_4.27\Engine"
)

$ErrorActionPreference = "Stop"
$contentRoot = Join-Path $EngineRoot "Content"
$probeFile = Join-Path $contentRoot "EngineMaterials\WorldGridMaterial.uasset"
$networkServiceSid = "*S-1-5-20"

function Test-ReadableFile([string]$Path) {
    try {
        $share = [System.IO.FileShare]::ReadWrite -bor [System.IO.FileShare]::Delete
        $stream = [System.IO.File]::Open($Path,[System.IO.FileMode]::Open,[System.IO.FileAccess]::Read,$share)
        try {
            $buffer = New-Object byte[] 4
            return ($stream.Read($buffer, 0, 4) -eq 4)
        }
        finally { $stream.Dispose() }
    }
    catch {
        Write-Host "UE4 ACL probe read failure: $($_.Exception.Message)"
        return $false
    }
}

Write-Host "UE4 ACL remediation identity: $([System.Security.Principal.WindowsIdentity]::GetCurrent().Name)"
Write-Host "UE4 ACL remediation target: $contentRoot"

if (-not (Test-Path -LiteralPath $probeFile -PathType Leaf)) {
    Write-Host "UE4_ACL_REMEDIATION_SKIP reason=probe-file-missing path=$probeFile"
    exit 0
}
if (Test-ReadableFile $probeFile) {
    Write-Host "UE4_ACL_REMEDIATION_PASS action=none reason=already-readable"
    exit 0
}

$currentIdentity = [System.Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object System.Security.Principal.WindowsPrincipal($currentIdentity)
$isAdmin = $principal.IsInRole([System.Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "UE4_ACL_REMEDIATION_DEFERRED reason=runner-not-elevated"
    Write-Host "Required elevated command:"
    Write-Host ('icacls "' + $contentRoot + '" /grant ' + $networkServiceSid + ':(OI)(CI)(RX) /T /C /Q')
    exit 0
}

Write-Host "UE4 ACL remediation: granting read/execute only to NETWORK SERVICE over Engine Content."
$grantSpec = $networkServiceSid + ":(OI)(CI)(RX)"
& icacls.exe $contentRoot /grant $grantSpec /T /C /Q
$icaclsExit = $LASTEXITCODE
Write-Host "UE4 ACL remediation icacls exit=$icaclsExit"
if ($icaclsExit -ne 0) {
    Write-Host "UE4_ACL_REMEDIATION_DEFERRED reason=icacls-failed exit=$icaclsExit"
    exit 0
}
if (Test-ReadableFile $probeFile) {
    Write-Host "UE4_ACL_REMEDIATION_PASS action=grant-network-service-rx"
    exit 0
}
Write-Host "UE4_ACL_REMEDIATION_DEFERRED reason=still-unreadable-after-grant"
exit 0
