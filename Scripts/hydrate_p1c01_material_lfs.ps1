[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location -LiteralPath $RepoRoot

$GitCommand = Get-Command git.exe -ErrorAction Stop
$GitExe = $GitCommand.Source
$IncludePatterns = @(
    'SourceAssets/Production/Imported/P1C01Materials/**',
    'SourceAssets/ValidatedRuntime/FRODO/*.fbx'
)
$IncludePattern = ($IncludePatterns -join ',')

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

$FrodoRoot = Join-Path $RepoRoot 'SourceAssets\ValidatedRuntime\FRODO'
$FrodoChecks = @(
    @('SK_FRODO_Validated.fbx','75d715f6ce4673a650a4382bc4f86b7ae0baf0fe548cc63f9b6ded1800f669be'),
    @('Frodo_Idle_Retarget.fbx','ee81650714587d2a1a638f3ff0c1a8239ea555bf84959e96ce5d037af3f33cd3'),
    @('Frodo_Walk_Retarget.fbx','c4091b7881a4e9e810e70bb7f3abed58683dff5bacf54e26ccb2e926e4c9e688'),
    @('Frodo_Run_Retarget.fbx','4a4d10d91343dbd701c535d30ea9d9384ca74596cd7720cf6bfdd1c6328e1fc1')
)
foreach ($Row in $FrodoChecks) {
    $Path = Join-Path $FrodoRoot $Row[0]
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "P1C01_LFS_HYDRATION_FAILED reason=frodo-fbx-missing path=$Path"
    }
    $Actual = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($Actual -ne $Row[1]) {
        throw "P1C01_LFS_HYDRATION_FAILED reason=frodo-hash path=$Path expected=$($Row[1]) actual=$Actual"
    }
}
Write-Host "P1C01_LFS_TEXTURE_HYDRATION_PASS pngs=$($Pngs.Count) include=$IncludePattern"
Write-Host "P1C01_LFS_FRODO_HYDRATION_PASS assets=$($FrodoChecks.Count)"
