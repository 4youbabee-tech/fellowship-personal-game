param(
  [string]$ManifestPath = "Data/P1C01MaterialImportWaveV1.json",
  [string]$WarehouseRoot = "C:\actions-runner\_warehouse\ShireJourney",
  [string]$GeneratedBranch = "generated/p1c01-material-source-v1"
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot=Split-Path $PSScriptRoot -Parent
$IntakeRoot=Join-Path $ProjectRoot "Saved\P1C01MaterialSourceExport"
if(Test-Path -LiteralPath $IntakeRoot){ Remove-Item -LiteralPath $IntakeRoot -Recurse -Force }
New-Item -ItemType Directory -Path $IntakeRoot -Force | Out-Null

& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "prepare_p1c01_material_intake.ps1") -ManifestPath $ManifestPath -WarehouseRoot $WarehouseRoot -OutputRoot $IntakeRoot -Refresh
if($LASTEXITCODE -ne 0){ throw "P1C01 material intake failed: $LASTEXITCODE" }

$receiptPath=Join-Path $IntakeRoot "p1c01_material_intake_receipt.json"
if(-not (Test-Path -LiteralPath $receiptPath -PathType Leaf)){ throw "P1C01 material receipt missing" }
$receipt=Get-Content -LiteralPath $receiptPath -Raw | ConvertFrom-Json
$prepared=@($receipt.prepared)
if($prepared.Count -lt 8){ throw "P1C01 material source export requires at least 8 prepared materials; got $($prepared.Count)" }

$git=(Get-Command git.exe -ErrorAction SilentlyContinue).Source
if(-not $git){
  foreach($candidate in @("C:\Program Files\Git\cmd\git.exe","C:\Program Files (x86)\Git\cmd\git.exe")){
    if(Test-Path -LiteralPath $candidate){$git=$candidate;break}
  }
}
if(-not $git){ throw "git.exe unavailable for generated material branch" }

$targetSha=([string]$env:TARGET_SHA).Trim()
if([string]::IsNullOrWhiteSpace($targetSha)){ $targetSha=(& $git -C $ProjectRoot rev-parse HEAD).Trim() }
$runId=if([string]::IsNullOrWhiteSpace([string]$env:GITHUB_RUN_ID)){"local"}else{[string]$env:GITHUB_RUN_ID}
$worktree=Join-Path $env:RUNNER_TEMP ("shire-p1c01-material-source-"+$runId)
if(Test-Path -LiteralPath $worktree){ Remove-Item -LiteralPath $worktree -Recurse -Force }

& $git -C $ProjectRoot worktree add -B $GeneratedBranch $worktree $targetSha
if($LASTEXITCODE -ne 0){ throw "git worktree add failed" }

try{
  $overlay=Join-Path $worktree "SourceAssets\Production\Imported\P1C01Materials"
  if(Test-Path -LiteralPath $overlay){ Remove-Item -LiteralPath $overlay -Recurse -Force }
  New-Item -ItemType Directory -Path $overlay -Force | Out-Null

  $manifest=Get-Content -LiteralPath (Join-Path $ProjectRoot $ManifestPath) -Raw | ConvertFrom-Json
  $outRows=@()
  $totalBytes=[int64]0
  foreach($item in $prepared){
    $destDir=Join-Path $overlay ([string]$item.id)
    New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    foreach($src in @([string]$item.basecolor_file,[string]$item.mtl_file)){
      if(-not (Test-Path -LiteralPath $src -PathType Leaf)){ throw "Prepared material file missing: $src" }
      $f=Get-Item -LiteralPath $src
      if($f.Length -gt 16777216){ throw "Single material source exceeds 16 MB bounded limit: $src" }
      Copy-Item -LiteralPath $src -Destination (Join-Path $destDir $f.Name) -Force
      $totalBytes += [int64]$f.Length
    }
    if($totalBytes -gt 134217728){ throw "P1C01 material source batch exceeds 128 MB bounded limit" }
    $outRows += [ordered]@{
      id=[string]$item.id
      provider=[string]$item.provider
      license=[string]$item.license
      asset_slug=[string]$item.asset_slug
      source_page=[string]$item.source_page
      source_url=[string]$item.source_url
      material_name=[string]$item.material_name
      roughness=[double]$item.roughness
      metallic=[double]$item.metallic
      specular=[double]$item.specular
      basecolor_sha256=[string]$item.basecolor_sha256
      mtl_sha256=[string]$item.mtl_sha256
      state="SOURCE_READY_FOR_UE_IMPORT"
    }
  }

  $sourceReceipt=[ordered]@{
    schema_version=1
    wave_id=[string]$manifest.wave_id
    generated_from_develop_sha=$targetSha
    generated_at_utc=[DateTime]::UtcNow.ToString("o")
    material_count=$outRows.Count
    total_source_bytes=$totalBytes
    items=$outRows
    runtime_rule="One PNG/TGA base color plus scalar Roughness/Metallic/Specular; no extra PBR samples in this low-spec wave."
    acceptance_boundary="Source promotion only. UE import, runtime binding, PIE, device, visual and performance acceptance require separate evidence."
  }
  $sourceReceipt | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $overlay "P1C01MaterialSourceReceipt.json") -Encoding UTF8

  & $git -C $worktree config user.name "shire-journey-warehouse-bot"
  & $git -C $worktree config user.email "shire-journey-warehouse-bot@users.noreply.github.com"
  & $git -C $worktree add -- "SourceAssets/Production/Imported/P1C01Materials"
  & $git -C $worktree diff --cached --quiet
  if($LASTEXITCODE -eq 0){
    Write-Host ("P1C01_MATERIAL_SOURCE_BRANCH_NO_CHANGE branch="+$GeneratedBranch+" materials="+$outRows.Count)
    exit 0
  }
  & $git -C $worktree commit -m ("P1C01: promote "+$outRows.Count+" receipt-verified Shire material sources")
  if($LASTEXITCODE -ne 0){ throw "generated material commit failed" }
  $generatedSha=(& $git -C $worktree rev-parse HEAD).Trim()
  & $git -C $worktree push --force-with-lease origin ("HEAD:refs/heads/"+$GeneratedBranch)
  if($LASTEXITCODE -ne 0){ throw "generated material branch push failed" }
  Write-Host ("P1C01_MATERIAL_SOURCE_BRANCH_PASS branch="+$GeneratedBranch+" sha="+$generatedSha+" materials="+$outRows.Count+" bytes="+$totalBytes)
}
finally{
  & $git -C $ProjectRoot worktree remove --force $worktree 2>$null
}
