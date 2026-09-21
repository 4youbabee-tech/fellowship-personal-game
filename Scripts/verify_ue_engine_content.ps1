param(
    [int]$StableSeconds = 4,
    [int]$Attempts = 6
)

$ErrorActionPreference = 'Stop'
$engineRoot = 'C:\Program Files\Epic Games\UE_4.27\Engine'
$materialPath = Join-Path $engineRoot 'Content\EngineMaterials\WorldGridMaterial.uasset'
$baseEngineIni = Join-Path $engineRoot 'Config\BaseEngine.ini'

function Get-PackageFingerprint([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }

    $item = Get-Item -LiteralPath $Path -Force
    $share = [System.IO.FileShare]::ReadWrite -bor [System.IO.FileShare]::Delete
    $stream = [System.IO.File]::Open(
        $Path,
        [System.IO.FileMode]::Open,
        [System.IO.FileAccess]::Read,
        $share
    )
    try {
        $header = New-Object byte[] 4
        $read = $stream.Read($header, 0, 4)
        if ($read -ne 4) {
            throw "Engine package header is truncated: $Path"
        }
    }
    finally {
        $stream.Dispose()
    }

    $packageTagOk = (
        $header[0] -eq 0xC1 -and
        $header[1] -eq 0x83 -and
        $header[2] -eq 0x2A -and
        $header[3] -eq 0x9E
    )
    $hash = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash

    return [pscustomobject]@{
        Length = [int64]$item.Length
        LastWriteUtc = $item.LastWriteTimeUtc.ToString('o')
        Sha256 = $hash
        PackageTagOk = $packageTagOk
    }
}

Write-Host "UE4 engine-content preflight identity: $([System.Security.Principal.WindowsIdentity]::GetCurrent().Name)"
Write-Host "Engine root: $engineRoot"

if (-not (Test-Path -LiteralPath $baseEngineIni -PathType Leaf)) {
    Write-Error "UE4 BaseEngine.ini is missing: $baseEngineIni"
    exit 34
}

$defaultMaterialLine = Select-String -LiteralPath $baseEngineIni -Pattern '^DefaultMaterialName=' -ErrorAction SilentlyContinue | Select-Object -First 1
if ($defaultMaterialLine) {
    Write-Host "Configured default material: $($defaultMaterialLine.Line)"
}

for ($attempt = 1; $attempt -le $Attempts; $attempt++) {
    Write-Host "Engine content stability probe $attempt of $Attempts"
    try {
        $before = Get-PackageFingerprint $materialPath
        if ($null -eq $before) {
            Write-Warning "Required UE4 default material is missing: $materialPath"
        }
        elseif (-not $before.PackageTagOk) {
            Write-Warning "WorldGridMaterial exists but does not begin with the UE package tag."
        }
        elseif ($before.Length -lt 1024) {
            Write-Warning "WorldGridMaterial is implausibly small: $($before.Length) bytes"
        }
        else {
            Write-Host "Before: size=$($before.Length) lastWriteUtc=$($before.LastWriteUtc) sha256=$($before.Sha256)"
            Start-Sleep -Seconds $StableSeconds
            $after = Get-PackageFingerprint $materialPath
            if (
                $null -ne $after -and
                $after.PackageTagOk -and
                $after.Length -eq $before.Length -and
                $after.LastWriteUtc -eq $before.LastWriteUtc -and
                $after.Sha256 -eq $before.Sha256
            ) {
                Write-Host "UE4 engine content is present, readable by the runner service, package-tag valid, and stable across $StableSeconds seconds."
                exit 0
            }
            Write-Warning "WorldGridMaterial changed during the stability window; an Epic verify/update or other writer may still be mutating the engine install."
        }
    }
    catch {
        Write-Warning "Engine content probe failed: $($_.Exception.Message)"
    }

    if ($attempt -lt $Attempts) {
        Start-Sleep -Seconds 5
    }
}

Write-Error "UE4 engine content is missing, unreadable, corrupt-looking, or still changing. Do not spend a full project build until the engine installation is stable."
exit 35
