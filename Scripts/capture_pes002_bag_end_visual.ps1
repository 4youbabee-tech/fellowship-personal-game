param([int]$WaitSeconds = 55)
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
$arguments = @('"' + $project + '"', '-game', '-windowed', '-ResX=1280', '-ResY=720', '-NoSplash', '-log', '-ExecCmds="HighResShot 1280x720"', '-abslog="' + $log + '"')
$proc = Start-Process -FilePath $exe -ArgumentList ($arguments -join ' ') -PassThru
try {
    Start-Sleep -Seconds $WaitSeconds
} finally {
    if (!$proc.HasExited) { Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue }
}
$shots = @(Get-ChildItem -Path $shotDir -File -ErrorAction SilentlyContinue | Where-Object { $_.Extension -in @('.png','.bmp') -and $_.LastWriteTime -ge $started.AddSeconds(-2) } | Sort-Object LastWriteTime -Descending)
if ($shots.Count -eq 0) { throw "PES002_VISUAL_CAPTURE_MISSING; inspect $log" }
$source = $shots[0].FullName
$destination = Join-Path $proof "BagEnd-P1C01-actual-runtime.png"
if ($shots[0].Extension -eq '.bmp') { throw "PES002_UNCOMPRESSED_CAPTURE_REJECTED: $source" }
Copy-Item $source $destination -Force
$hash = (Get-FileHash $destination -Algorithm SHA256).Hash
Write-Host "PES002_VISUAL_CAPTURE_PRESENT sha256=$hash image=$destination; VISUAL_ACCEPTED=false traversal=unproven"
