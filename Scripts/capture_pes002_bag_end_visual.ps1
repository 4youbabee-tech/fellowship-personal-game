param([int]$WaitSeconds = 72)
$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$exe = "C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\UE4Editor.exe"
$project = Join-Path $root "ShireJourney.uproject"
$proof = Join-Path $root "Saved\PES002VisualProof"
$shotDir = Join-Path $root "Saved\Screenshots\Windows"
New-Item -ItemType Directory -Force -Path $proof | Out-Null
if (!(Test-Path $exe) -or !(Test-Path $project)) { throw "PES002_EDITOR_OR_PROJECT_MISSING" }
$started = Get-Date
$log = Join-Path $proof "PES002VisualEditor.log"
$arguments = @('"' + $project + '"', '-game', '-windowed', '-ResX=1280', '-ResY=720', '-NoSplash', '-log', '-PES002VisualProof', '-abslog="' + $log + '"')
$proc = Start-Process -FilePath $exe -ArgumentList ($arguments -join ' ') -PassThru
try {
    Start-Sleep -Seconds $WaitSeconds
} finally {
    if (!$proc.HasExited) { Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue }
}
if (!(Test-Path $log) -or !(Select-String -Path $log -Pattern 'PES002_CAPTURE_CAMERA_READY target=BagEnd' -Quiet)) {
    throw "PES002_CAPTURE_CAMERA_NOT_CONFIRMED; inspect $log"
}
for ($view = 0; $view -lt 3; $view++) {
    if (!(Select-String -Path $log -SimpleMatch -Pattern "PES002_CAPTURE_VIEW_READY view=$view target=BagEnd" -Quiet)) {
        throw "PES002_CAPTURE_VIEW_NOT_READY view=$view"
    }
    if (!(Select-String -Path $log -SimpleMatch -Pattern "PES002_SCREENSHOT_REQUESTED target=BagEnd view=$view" -Quiet)) {
        throw "PES002_CAPTURE_SCREENSHOT_REQUEST_NOT_CONFIRMED view=$view"
    }
    $shots = @(Get-ChildItem -Path $shotDir -File -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -like "PES002_BagEnd_View$view*.png" -and $_.LastWriteTime -ge $started.AddSeconds(-2) } |
        Sort-Object LastWriteTime -Descending)
    if ($shots.Count -eq 0) { throw "PES002_BAG_END_SCREENSHOT_MISSING view=$view; inspect $log" }
    $source = $shots[0].FullName
    $bytes = [System.IO.File]::ReadAllBytes($source)
    if ($bytes.Length -lt 24 -or $bytes[0] -ne 137 -or $bytes[1] -ne 80 -or $bytes[2] -ne 78 -or $bytes[3] -ne 71) {
        throw "PES002_SCREENSHOT_NOT_PNG view=$view"
    }
    $width = [int]($bytes[16] * 16777216 + $bytes[17] * 65536 + $bytes[18] * 256 + $bytes[19])
    $height = [int]($bytes[20] * 16777216 + $bytes[21] * 65536 + $bytes[22] * 256 + $bytes[23])
    if ($width -ne 1280 -or $height -ne 720) { throw "PES002_SCREENSHOT_WRONG_DIMENSIONS view=$view width=$width height=$height" }
    $destination = Join-Path $proof "BagEnd-P1C01-view$view-actual-runtime.png"
    Copy-Item $source $destination -Force
    $hash = (Get-FileHash $destination -Algorithm SHA256).Hash
    Write-Host "PES002_BAG_END_CAPTURE_PRESENT view=$view width=$width height=$height sha256=$hash image=$destination camera=BagEnd visualAccepted=false traversal=unproven"
}
