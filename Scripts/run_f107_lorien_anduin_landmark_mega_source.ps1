param(
  [string]$ManifestPath = "Data/F107LorienAnduinLandmarkMegaSourceSuperpackV1.json",
  [string]$WarehouseRoot = "D:\actions-runner\_warehouse\ShireJourney",
  [string]$OutputRoot = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path $PSScriptRoot -Parent
if(-not [IO.Path]::IsPathRooted($ManifestPath)){ $ManifestPath = Join-Path $ProjectRoot $ManifestPath }
if(-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)){ throw "F107_MEGA_SOURCE_MANIFEST_MISSING path=$ManifestPath" }
if(-not (Test-Path -LiteralPath $WarehouseRoot -PathType Container)){ throw "F107_MEGA_SOURCE_WAREHOUSE_MISSING root=$WarehouseRoot" }

$manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json

Write-Host "F107_MEGA_SOURCE_INVENTORY_GATE_BEGIN"
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "audit_warehouse_inventory.ps1") -Root $WarehouseRoot
$auditExit=[int]$LASTEXITCODE
if($auditExit -ne 0){ throw "F107_MEGA_SOURCE_INVENTORY_GATE_FAIL exit=$auditExit" }
Write-Host "F107_MEGA_SOURCE_INVENTORY_GATE_PASS"

if([string]::IsNullOrWhiteSpace($OutputRoot)){ $OutputRoot = Join-Path $WarehouseRoot "_f107_lorien_anduin_landmark_mega_v1" }
New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null

$warehouseItem=Get-Item -LiteralPath $WarehouseRoot
$drive=[IO.DriveInfo]::new($warehouseItem.PSDrive.Root)
$reserve=[int64]$manifest.source_policy.minimum_free_disk_reserve_bytes
$free=[int64]$drive.AvailableFreeSpace
if($free -lt $reserve){ throw "F107_MEGA_SOURCE_DISK_RESERVE_FAIL free=$free reserve=$reserve" }

$allFiles=@(Get-ChildItem -LiteralPath $WarehouseRoot -Recurse -File -ErrorAction SilentlyContinue |
  Where-Object { $_.FullName -notlike ($OutputRoot.TrimEnd("\") + "\*") })

$textureAllowed=@{}
foreach($x in @($manifest.source_policy.texture_extensions)){ $textureAllowed[([string]$x).ToLowerInvariant()]=$true }
$textureBlocked=@{}
foreach($x in @($manifest.source_policy.forbidden_texture_extensions)){ $textureBlocked[([string]$x).ToLowerInvariant()]=$true }
$staticAllowed=@{}
foreach($x in @($manifest.source_policy.static_source_extensions)){ $staticAllowed[([string]$x).ToLowerInvariant()]=$true }
$audioAllowed=@{}
foreach($x in @($manifest.source_policy.audio_extensions)){ $audioAllowed[([string]$x).ToLowerInvariant()]=$true }
$metadataAllowed=@{}
foreach($x in @($manifest.source_policy.metadata_extensions)){ $metadataAllowed[([string]$x).ToLowerInvariant()]=$true }
$animatedExt=([string]$manifest.source_policy.animated_candidate_extension).ToLowerInvariant()

$eligible=New-Object System.Collections.ArrayList
$blockedBmp=0
foreach($file in $allFiles){
  $ext=$file.Extension.ToLowerInvariant()
  if($textureBlocked.ContainsKey($ext)){ $blockedBmp++; continue }
  if($textureAllowed.ContainsKey($ext) -or $staticAllowed.ContainsKey($ext) -or $audioAllowed.ContainsKey($ext) -or $metadataAllowed.ContainsKey($ext)){
    [void]$eligible.Add($file)
  }
}
[object[]]$eligibleRows=$eligible.ToArray()

$perCategory=[int]$manifest.source_policy.max_candidates_per_category
$totalCeiling=[int]$manifest.source_policy.max_total_candidates
$landmarkBonus=[int]$manifest.source_policy.landmark_score_bonus
$totalSelected=0
$categoryReports=@()
$landmarkReports=@()

Write-Host ("F107_MEGA_SOURCE_BEGIN pack=" + [string]$manifest.pack_id +
  " warehouseFiles=" + $allFiles.Count +
  " eligibleFiles=" + $eligibleRows.Count +
  " blockedBmp=" + $blockedBmp +
  " freeBytes=" + $free)

foreach($category in @($manifest.categories)){
  if($totalSelected -ge $totalCeiling){ break }

  $kind=([string]$category.kind).ToLowerInvariant()
  $isLandmark=[bool]$category.landmark
  $keywords=@($category.keywords | ForEach-Object { ([string]$_).ToLowerInvariant() })
  $scored=New-Object System.Collections.ArrayList

  foreach($file in $eligibleRows){
    $ext=$file.Extension.ToLowerInvariant()
    if($kind -eq "animated" -and $ext -ne $animatedExt){ continue }
    if($kind -eq "audio" -and -not $audioAllowed.ContainsKey($ext)){ continue }
    if($kind -eq "surface" -and -not $textureAllowed.ContainsKey($ext) -and -not $metadataAllowed.ContainsKey($ext)){ continue }

    $haystack=$file.FullName.ToLowerInvariant()
    $matches=New-Object System.Collections.ArrayList
    foreach($keyword in $keywords){
      if(-not [string]::IsNullOrWhiteSpace($keyword) -and $haystack.Contains($keyword)){ [void]$matches.Add($keyword) }
    }
    if($matches.Count -eq 0){ continue }

    $score=[int]$matches.Count
    if($isLandmark){ $score+=$landmarkBonus }
    if($haystack.Contains("production")){ $score+=2 }
    if($haystack.Contains("imported")){ $score+=1 }
    if($ext -eq ".fbx"){ $score+=2 }
    if($textureAllowed.ContainsKey($ext)){ $score+=1 }

    [object[]]$matchedTerms=$matches.ToArray()
    [void]$scored.Add([pscustomobject]@{
      path=$file.FullName
      extension=$ext
      bytes=[int64]$file.Length
      score=$score
      matched_terms=$matchedTerms
    })
  }

  [object[]]$ranked=@($scored.ToArray() | Sort-Object -Property @{Expression="score";Descending=$true}, @{Expression="bytes";Descending=$false})
  $remaining=$totalCeiling-$totalSelected
  $take=[Math]::Min($perCategory,$remaining)
  [object[]]$selected=@($ranked | Select-Object -First $take)
  $totalSelected+=$selected.Count

  $report=[ordered]@{
    schema_version=1
    pack_id=[string]$manifest.pack_id
    category=[string]$category.id
    kind=[string]$category.kind
    landmark=$isLandmark
    candidate_count=$selected.Count
    candidate_ceiling=$take
    candidates=$selected
    evidence_boundary="Source index only; not READY_FOR_IMPORT or visual/runtime acceptance."
  }
  $reportPath=Join-Path $OutputRoot (([string]$category.id)+".json")
  $report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $reportPath -Encoding UTF8

  $categoryReports += [ordered]@{
    category=[string]$category.id
    kind=[string]$category.kind
    landmark=$isLandmark
    candidates=$selected.Count
    report=$reportPath
  }

  if($isLandmark){
    $landmarkReports += [ordered]@{
      category=[string]$category.id
      candidates=$selected.Count
      has_candidates=($selected.Count -gt 0)
    }
  }

  Write-Host ("F107_MEGA_SOURCE_CATEGORY_PASS id=" + [string]$category.id +
    " kind=" + [string]$category.kind +
    " landmark=" + $isLandmark +
    " candidates=" + $selected.Count +
    " totalSelected=" + $totalSelected)
}

$landmarkCategoryCount=@($landmarkReports).Count
$landmarkReadyCount=@($landmarkReports | Where-Object { [bool]$_.has_candidates }).Count
$minimumLandmark=[int]$manifest.landmark_policy.minimum_landmark_categories
if($landmarkCategoryCount -lt $minimumLandmark){
  throw "F107_LANDMARK_CONTRACT_FAIL configured=$landmarkCategoryCount required=$minimumLandmark"
}
if($landmarkReadyCount -lt $minimumLandmark){
  throw "F107_LANDMARK_SOURCE_COVERAGE_FAIL ready=$landmarkReadyCount required=$minimumLandmark"
}

$landmarkPath=Join-Path $OutputRoot "landmark_coverage.json"
[ordered]@{
  schema_version=1
  pack_id=[string]$manifest.pack_id
  configured_landmark_categories=$landmarkCategoryCount
  ready_landmark_categories=$landmarkReadyCount
  minimum_required=$minimumLandmark
  landmark_categories=$landmarkReports
  visual_acceptance="NOT_CLAIMED"
} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $landmarkPath -Encoding UTF8

$summaryPath=Join-Path $OutputRoot "summary.json"
[ordered]@{
  schema_version=1
  pack_id=[string]$manifest.pack_id
  canonical_mission_id=[string]$manifest.canonical_mission_id
  runtime_consumers=@($manifest.runtime_consumers)
  generated_utc=[DateTime]::UtcNow.ToString("o")
  warehouse_files=$allFiles.Count
  eligible_files=$eligibleRows.Count
  blocked_bmp=$blockedBmp
  total_selected=$totalSelected
  total_ceiling=$totalCeiling
  landmark_categories=$landmarkCategoryCount
  landmark_ready=$landmarkReadyCount
  categories=$categoryReports
  landmark_report=$landmarkPath
  runtime_integration="GATED_NOT_STARTED"
  visual_acceptance="NOT_CLAIMED"
  acceptance_boundary=[string]$manifest.acceptance_boundary
} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $summaryPath -Encoding UTF8

Write-Host ("F107_LANDMARK_SOURCE_PASS configured=" + $landmarkCategoryCount +
  " ready=" + $landmarkReadyCount +
  " required=" + $minimumLandmark)
Write-Host ("F107_MEGA_SOURCE_PASS categories=" + $categoryReports.Count +
  " selected=" + $totalSelected +
  " ceiling=" + $totalCeiling +
  " summary=" + $summaryPath)
exit 0
