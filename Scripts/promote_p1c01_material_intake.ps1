param(
  [string]$IntakeRoot = "",
  [switch]$RunUnrealImport
)
$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path $PSScriptRoot -Parent
if ([string]::IsNullOrWhiteSpace($IntakeRoot)) { $IntakeRoot = Join-Path $ProjectRoot "Saved\MaterialIntake\P1C01" }
$receiptPath=Join-Path $IntakeRoot "p1c01_material_intake_receipt.json"
if(-not (Test-Path -LiteralPath $receiptPath -PathType Leaf)){ throw "Material intake receipt missing: $receiptPath" }
$receipt=Get-Content -LiteralPath $receiptPath -Raw | ConvertFrom-Json
if(@($receipt.blocked_technical).Count -gt 0){ throw "Material intake has technical blockers; promotion refused." }
$overlay=Join-Path $ProjectRoot "SourceAssets\Production\Imported\P1C01Materials"
if(Test-Path -LiteralPath $overlay){ Remove-Item -LiteralPath $overlay -Recurse -Force }
New-Item -ItemType Directory -Path $overlay -Force | Out-Null
$promoted=@()
try {
  foreach($item in @($receipt.prepared)) {
    if([string]$item.state -ne "INTAKE_QC_PREPARED"){ continue }
    $dest=Join-Path $overlay ([string]$item.id)
    New-Item -ItemType Directory -Path $dest -Force | Out-Null
    foreach($src in @([string]$item.basecolor_file,[string]$item.mtl_file)) {
      if(-not (Test-Path -LiteralPath $src -PathType Leaf)){ throw "Prepared source missing: $src" }
      Copy-Item -LiteralPath $src -Destination (Join-Path $dest ([IO.Path]::GetFileName($src))) -Force
    }
    $promoted += [ordered]@{id=[string]$item.id;material_name=[string]$item.material_name;destination=$dest;state="LOCAL_SOURCE_OVERLAY_READY"}
  }
  if($promoted.Count -eq 0){ Write-Host "P1C01_MATERIAL_PROMOTION_SKIP no prepared items"; exit 0 }
  $promotionPath=Join-Path $IntakeRoot "p1c01_material_promotion_receipt.json"
  [ordered]@{schema_version=1;generated_at_utc=[DateTime]::UtcNow.ToString("o");overlay_root=$overlay;promoted=$promoted;run_unreal_import=[bool]$RunUnrealImport} |
    ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $promotionPath -Encoding UTF8
  if($RunUnrealImport) {
    $cmd=Join-Path $ProjectRoot "Scripts\ci_import_production_assets.cmd"
    & cmd.exe /d /c ('"'+$cmd+'"')
    if($LASTEXITCODE -ne 0){ throw "UE4 production import failed with exit code $LASTEXITCODE" }
    Write-Host ("P1C01_MATERIAL_UE_IMPORT_PASS promoted="+$promoted.Count+" receipt="+$promotionPath)
  } else {
    Write-Host ("P1C01_MATERIAL_OVERLAY_READY promoted="+$promoted.Count+" receipt="+$promotionPath)
  }
}
finally {
  if(Test-Path -LiteralPath $overlay){ Remove-Item -LiteralPath $overlay -Recurse -Force }
}
