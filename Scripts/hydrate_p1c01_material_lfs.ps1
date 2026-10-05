[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location -LiteralPath $RepoRoot

$GitCommand = Get-Command git.exe -ErrorAction Stop
$GitExe = $GitCommand.Source
$IncludePattern = 'SourceAssets/Production/Imported/P1C01Materials/**'

& $GitExe lfs version
if ($LASTEXITCODE -ne 0) {
    throw 'P1C01_LFS_HYDRATION_FAILED reason=git-lfs-unavailable'
}

& $GitExe lfs install --local
if ($LASTEXITCODE -ne 0) {
    throw 'P1C01_LFS_HYDRATION_FAILED reason=git-lfs-install'
}

& $GitExe lfs pull --include="$IncludePattern" origin
if ($LASTEXITCODE -ne 0) {
    throw 'P1C01_LFS_HYDRATION_FAILED reason=git-lfs-pull'
}

$TextureRoot = Join-Path $RepoRoot 'SourceAssets\Production\Imported\P1C01Materials'
if (-not (Test-Path -LiteralPath $TextureRoot)) {
    throw "P1C01_LFS_HYDRATION_FAILED reason=missing-texture-root path=$TextureRoot"
}

$Pngs = @(Get-ChildItem -LiteralPath $TextureRoot -Recurse -File -Filter '*.png')
if ($Pngs.Count -eq 0) {
    throw "P1C01_LFS_HYDRATION_FAILED reason=no-png-sources root=$TextureRoot"
}

$ExpectedSignature = [byte[]](0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A)
$BadFiles = @()

foreach ($File in $Pngs) {
    $Header = New-Object byte[] 8
    $Read = 0
    $Stream = [System.IO.File]::OpenRead($File.FullName)
    try {
        $Read = $Stream.Read($Header, 0, $Header.Length)
    }
    finally {
        $Stream.Dispose()
    }

    $ValidSignature = ($Read -eq $ExpectedSignature.Length)
    if ($ValidSignature) {
        for ($Index = 0; $Index -lt $ExpectedSignature.Length; ++$Index) {
            if ($Header[$Index] -ne $ExpectedSignature[$Index]) {
                $ValidSignature = $false
                break
            }
        }
    }

    if (-not $ValidSignature) {
        $Reason = 'invalid-png-signature'
        if ($File.Length -lt 1024) {
            $SmallText = [System.IO.File]::ReadAllText($File.FullName)
            if ($SmallText.StartsWith('version https://git-lfs.github.com/spec/v1')) {
                $Reason = 'git-lfs-pointer'
            }
        }

        $RelativePath = $File.FullName.Substring($RepoRoot.Length).TrimStart('\', '/')
        $BadFiles += "$RelativePath reason=$Reason bytes=$($File.Length)"
    }
}

if ($BadFiles.Count -gt 0) {
    foreach ($BadFile in $BadFiles) {
        Write-Error "P1C01_LFS_HYDRATION_FAILED $BadFile"
    }
    throw "P1C01_LFS_HYDRATION_FAILED invalid=$($BadFiles.Count)"
}

Write-Host "P1C01_LFS_TEXTURE_HYDRATION_PASS pngs=$($Pngs.Count) include=$IncludePattern"
