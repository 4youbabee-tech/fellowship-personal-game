param(
  [string]$ManifestPath = "Data/P1C01MaterialImportWaveV1.json",
  [string]$WarehouseRoot = "C:\actions-runner\_warehouse\ShireJourney",
  [string]$GeneratedBranch = "generated/p1c01-material-source-v1",
  [int64]$MaxSingleSourceBytes = 33554432,
  [int64]$MaxBatchSourceBytes = 268435456,
  [int]$MinimumExportedMaterials = 6
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if($MaxSingleSourceBytes -le 0){ throw "MaxSingleSourceBytes must be > 0" }
if($MaxBatchSourceBytes -lt $MaxSingleSourceBytes){ throw "MaxBatchSourceBytes must be >= MaxSingleSourceBytes" }
if($MinimumExportedMaterials -lt 1){ throw "MinimumExportedMaterials must be >= 1" }

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
if($prepared.Count -lt $MinimumExportedMaterials){
  throw "P1C01 material source export requires at least $MinimumExportedMaterials prepared materials; got $($prepared.Count)"
}

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

  $ResolvedManifestPath =
  if([IO.Path]::IsPathRooted($ManifestPath)){
    $ManifestPath
  } else {
    Join-Path $ProjectRoot $ManifestPath
  }
  $manifest=Get-Content -LiteralPath $ResolvedManifestPath -Raw | ConvertFrom-Json

  $attributesPath=Join-Path $worktree ".gitattributes"
  $attributesText=if(Test-Path -LiteralPath $attributesPath){ Get-Content -LiteralPath $attributesPath -Raw }else{ "" }
  $tgaLfsReady=($attributesText -match '(?m)^\*\.tga\s+filter=lfs\b')

  $outRows=@()
  $quarantined=@()
  $totalBytes=[int64]0

  foreach($item in $prepared){
    $sources=@([string]$item.basecolor_file,[string]$item.mtl_file)
    $sourceItems=@()
    $itemBytes=[int64]0
    $itemBlocked=$false

    foreach($src in $sources){
      if(-not (Test-Path -LiteralPath $src -PathType Leaf)){ throw "Prepared material file missing: $src" }
      $f=Get-Item -LiteralPath $src
      $ext=$f.Extension.ToLowerInvariant()

      if($ext -eq ".tga" -and -not $tgaLfsReady){
        $quarantined += [ordered]@{
          id=[string]$item.id
          reason="tga_lfs_not_configured"
          file=$src
          bytes=[int64]$f.Length
        }
        $itemBlocked=$true
        break
      }

      if($f.Length -gt $MaxSingleSourceBytes){
        $quarantined += [ordered]@{
          id=[string]$item.id
          reason="single_source_budget_exceeded"
          file=$src
          bytes=[int64]$f.Length
          max_bytes=$MaxSingleSourceBytes
        }
        $itemBlocked=$true
        break
      }

      $sourceItems += $f
      $itemBytes += [int64]$f.Length
    }

    if($itemBlocked){ continue }

    if(($totalBytes + $itemBytes) -gt $MaxBatchSourceBytes){
      $quarantined += [ordered]@{
        id=[string]$item.id
        reason="batch_source_budget_exceeded"
        item_bytes=$itemBytes
        current_batch_bytes=$totalBytes
        max_batch_bytes=$MaxBatchSourceBytes
      }
      continue
    }

    $destDir=Join-Path $overlay ([string]$item.id)
    New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    foreach($f in $sourceItems){
      Copy-Item -LiteralPath $f.FullName -Destination (Join-Path $destDir $f.Name) -Force
    }
    $totalBytes += $itemBytes

    $outRows += [ordered]@{
      id=[string]$item.id
      provider=[string]$item.provider
      license=[string]$item.license
      asset_slug=[string]$item.asset_slug
      source_page=[string]$item.source_page
      source_url=[string]$item.source_url
      selected_source_filename=[string]$item.selected_source_filename
      selected_source_kind=[string]$item.selected_source_kind
      material_name=[string]$item.material_name
      roughness=[double]$item.roughness
      metallic=[double]$item.metallic
      specular=[double]$item.specular
      basecolor_sha256=[string]$item.basecolor_sha256
      mtl_sha256=[string]$item.mtl_sha256
      source_bytes=$itemBytes
      state="SOURCE_READY_FOR_UE_IMPORT"
    }
  }

  if($outRows.Count -lt $MinimumExportedMaterials){
    throw "P1C01 material export fell below minimum after item quarantine: exported=$($outRows.Count) minimum=$MinimumExportedMaterials quarantined=$($quarantined.Count)"
  }

  $sourceReceipt=[ordered]@{
    schema_version=2
    wave_id=[string]$manifest.wave_id
    generated_from_develop_sha=$targetSha
    generated_at_utc=[DateTime]::UtcNow.ToString("o")
    material_count=$outRows.Count
    quarantined_count=$quarantined.Count
    total_source_bytes=$totalBytes
    budget=[ordered]@{
      max_single_source_bytes=$MaxSingleSourceBytes
      max_batch_source_bytes=$MaxBatchSourceBytes
      minimum_exported_materials=$MinimumExportedMaterials
    }
    items=$outRows
    quarantined=$quarantined
    runtime_rule="One PNG/TGA base color plus scalar Roughness/Metallic/Specular; no extra PBR samples in this low-spec wave."
    acceptance_boundary="Source promotion only. UE import, runtime binding, PIE, device, visual and performance acceptance require separate evidence."
  }
  $sourceReceipt | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $overlay "P1C01MaterialSourceReceipt.json") -Encoding UTF8

  & $git -C $worktree config user.name "shire-journey-warehouse-bot"
  & $git -C $worktree config user.email "shire-journey-warehouse-bot@users.noreply.github.com"
  & $git -C $worktree add -- "SourceAssets/Production/Imported/P1C01Materials"
  & $git -C $worktree diff --cached --quiet
  if($LASTEXITCODE -eq 0){
    if($quarantined.Count -gt 0){
      Write-Host ("P1C01_MATERIAL_SOURCE_BRANCH_NO_CHANGE_WITH_QUARANTINE branch="+$GeneratedBranch+" materials="+$outRows.Count+" quarantined="+$quarantined.Count+" bytes="+$totalBytes)
    } else {
      Write-Host ("P1C01_MATERIAL_SOURCE_BRANCH_NO_CHANGE branch="+$GeneratedBranch+" materials="+$outRows.Count+" bytes="+$totalBytes)
    }
    exit 0
  }

  & $git -C $worktree commit -m ("P1C01: promote "+$outRows.Count+" receipt-verified Shire material sources")
  if($LASTEXITCODE -ne 0){ throw "generated material commit failed" }
  $generatedSha=(& $git -C $worktree rev-parse HEAD).Trim()

  # Root-cause guard: a plain --force-with-lease relies on the caller's local
  # remote-tracking ref. Warehouse exact-head checkouts intentionally do not fetch
  # generated branches, so that ref can be stale even when the remote is healthy.
  # Read the authoritative remote head and lease against that exact SHA instead.
  $remoteRef="refs/heads/"+$GeneratedBranch
  $remoteLine=(& $git -c credential.helper= -C $worktree ls-remote --heads origin $remoteRef | Select-Object -First 1)
  if($LASTEXITCODE -ne 0){ throw "generated material remote-head lookup failed" }

  $remoteGeneratedSha=""
  if(-not [string]::IsNullOrWhiteSpace([string]$remoteLine)){
    $parts=@(([string]$remoteLine) -split "\s+")
    if($parts.Count -lt 2 -or $parts[1] -ne $remoteRef){
      throw "generated material remote-head parse failed: $remoteLine"
    }
    $remoteGeneratedSha=([string]$parts[0]).Trim()
    if($remoteGeneratedSha -notmatch '^[0-9a-fA-F]{40}

  if($quarantined.Count -gt 0){
    foreach($entry in $quarantined){ Write-Host ("P1C01_MATERIAL_SOURCE_QUARANTINE "+($entry|ConvertTo-Json -Compress -Depth 6)) }
    Write-Host ("P1C01_MATERIAL_SOURCE_BRANCH_PASS_WITH_QUARANTINE branch="+$GeneratedBranch+" sha="+$generatedSha+" materials="+$outRows.Count+" quarantined="+$quarantined.Count+" bytes="+$totalBytes)
  } else {
    Write-Host ("P1C01_MATERIAL_SOURCE_BRANCH_PASS branch="+$GeneratedBranch+" sha="+$generatedSha+" materials="+$outRows.Count+" bytes="+$totalBytes)
  }
}
finally{
  & $git -C $ProjectRoot worktree remove --force $worktree 2>$null
}
){
      throw "generated material remote-head SHA invalid: $remoteGeneratedSha"
    }
  }

  if([string]::IsNullOrWhiteSpace($remoteGeneratedSha)){
    Write-Host ("P1C01_MATERIAL_SOURCE_PUBLISH_CREATE branch="+$GeneratedBranch+" local="+$generatedSha)
    & $git -c credential.helper= -C $worktree push origin ("HEAD:"+$remoteRef)
  } else {
    $leaseArg="--force-with-lease="+$remoteRef+":"+$remoteGeneratedSha
    Write-Host ("P1C01_MATERIAL_SOURCE_PUBLISH_LEASE branch="+$GeneratedBranch+" remote="+$remoteGeneratedSha+" local="+$generatedSha)
    & $git -c credential.helper= -C $worktree push $leaseArg origin ("HEAD:"+$remoteRef)
  }
  if($LASTEXITCODE -ne 0){
    throw "generated material branch push failed after explicit remote-SHA lease"
  }

  if($quarantined.Count -gt 0){
    foreach($entry in $quarantined){ Write-Host ("P1C01_MATERIAL_SOURCE_QUARANTINE "+($entry|ConvertTo-Json -Compress -Depth 6)) }
    Write-Host ("P1C01_MATERIAL_SOURCE_BRANCH_PASS_WITH_QUARANTINE branch="+$GeneratedBranch+" sha="+$generatedSha+" materials="+$outRows.Count+" quarantined="+$quarantined.Count+" bytes="+$totalBytes)
  } else {
    Write-Host ("P1C01_MATERIAL_SOURCE_BRANCH_PASS branch="+$GeneratedBranch+" sha="+$generatedSha+" materials="+$outRows.Count+" bytes="+$totalBytes)
  }
}
finally{
  & $git -C $ProjectRoot worktree remove --force $worktree 2>$null
}
