param(
  [string]$ManifestPath = "Data/F108AmonHenMaximumSafeSourceSuperpackV1.json",
  [string]$WarehouseRoot = "C:\actions-runner\_warehouse\ShireJourney",
  [string]$OutputRoot = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path $PSScriptRoot -Parent
if(-not [IO.Path]::IsPathRooted($ManifestPath)){ $ManifestPath = Join-Path $ProjectRoot $ManifestPath }
if(-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)){ throw "F108_MAX_SAFE_MANIFEST_MISSING path=$ManifestPath" }
if(-not (Test-Path -LiteralPath $WarehouseRoot -PathType Container)){ throw "F108_MAX_SAFE_WAREHOUSE_MISSING root=$WarehouseRoot" }

$manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json

Write-Host "F108_MAX_SAFE_INVENTORY_GATE_BEGIN"
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "audit_warehouse_inventory.ps1") -Root $WarehouseRoot
$auditExit=[int]$LASTEXITCODE
if($auditExit -ne 0){ throw "F108_MAX_SAFE_INVENTORY_GATE_FAIL exit=$auditExit" }
Write-Host "F108_MAX_SAFE_INVENTORY_GATE_PASS"

if([string]::IsNullOrWhiteSpace($OutputRoot)){ $OutputRoot = Join-Path $WarehouseRoot "_f108_amon_hen_max_safe_v1" }
New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null

$warehouseItem=Get-Item -LiteralPath $WarehouseRoot
$drive=[IO.DriveInfo]::new($warehouseItem.PSDrive.Root)
$reserve=[int64]$manifest.safety_gate.minimum_free_disk_reserve_bytes
$free=[int64]$drive.AvailableFreeSpace
if($free -lt $reserve){ throw "F108_MAX_SAFE_DISK_RESERVE_FAIL free=$free reserve=$reserve" }

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
$totalCeiling=[int]$manifest.source_policy.max_total_candidate_assignments
$maxReuse=[int]$manifest.source_policy.max_category_reuse_per_source_path
$landmarkBonus=[int]$manifest.source_policy.landmark_score_bonus
$storyBonus=[int]$manifest.source_policy.story_critical_score_bonus
$totalSelected=0
$categoryReports=@()
$landmarkReports=@()
$usageByPath=@{}

Write-Host ("F108_MAX_SAFE_BEGIN pack=" + [string]$manifest.pack_id +
  " warehouseFiles=" + $allFiles.Count +
  " eligibleFiles=" + $eligibleRows.Count +
  " blockedBmp=" + $blockedBmp +
  " assignmentCeiling=" + $totalCeiling +
  " perCategory=" + $perCategory +
  " reuseCap=" + $maxReuse +
  " freeBytes=" + $free)

foreach($category in @($manifest.categories)){
  if($totalSelected -ge $totalCeiling){ break }

  $kind=([string]$category.kind).ToLowerInvariant()
  $group=([string]$category.coverage_group).ToLowerInvariant()
  $isLandmark=[bool]$category.landmark
  $isStoryCritical=[bool]$category.story_critical
  $keywords=@($category.keywords | ForEach-Object { ([string]$_).ToLowerInvariant() })
  $scored=New-Object System.Collections.ArrayList

  foreach($file in $eligibleRows){
    $pathKey=$file.FullName.ToLowerInvariant()
    $reuse=0
    if($usageByPath.ContainsKey($pathKey)){ $reuse=[int]$usageByPath[$pathKey] }
    if($reuse -ge $maxReuse){ continue }

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
    if($isStoryCritical){ $score+=$storyBonus }
    if($haystack.Contains("production")){ $score+=2 }
    if($haystack.Contains("imported")){ $score+=1 }
    if($ext -eq ".fbx"){ $score+=2 }
    if($textureAllowed.ContainsKey($ext)){ $score+=1 }
    $score-=$reuse

    [object[]]$matchedTerms=$matches.ToArray()
    [void]$scored.Add([pscustomobject]@{
      path=$file.FullName
      extension=$ext
      bytes=[int64]$file.Length
      score=$score
      prior_category_reuse=$reuse
      matched_terms=$matchedTerms
    })
  }

  [object[]]$ranked=@($scored.ToArray() | Sort-Object -Property @{Expression="score";Descending=$true}, @{Expression="bytes";Descending=$false})
  $remaining=$totalCeiling-$totalSelected
  $take=[Math]::Min($perCategory,$remaining)
  [object[]]$selected=@($ranked | Select-Object -First $take)

  foreach($row in $selected){
    $pathKey=([string]$row.path).ToLowerInvariant()
    if($usageByPath.ContainsKey($pathKey)){ $usageByPath[$pathKey]=[int]$usageByPath[$pathKey]+1 }
    else { $usageByPath[$pathKey]=1 }
  }
  $totalSelected+=$selected.Count

  $report=[ordered]@{
    schema_version=1
    pack_id=[string]$manifest.pack_id
    category=[string]$category.id
    kind=[string]$category.kind
    coverage_group=$group
    landmark=$isLandmark
    story_critical=$isStoryCritical
    candidate_count=$selected.Count
    candidate_ceiling=$take
    max_source_path_reuse=$maxReuse
    candidates=$selected
    evidence_boundary="Source index only; not READY_FOR_IMPORT or visual/runtime acceptance."
  }
  $reportPath=Join-Path $OutputRoot (([string]$category.id)+".json")
  $report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $reportPath -Encoding UTF8

  $categoryReports += [ordered]@{
    category=[string]$category.id
    kind=[string]$category.kind
    coverage_group=$group
    landmark=$isLandmark
    story_critical=$isStoryCritical
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

  Write-Host ("F108_MAX_SAFE_CATEGORY_PASS id=" + [string]$category.id +
    " group=" + $group +
    " kind=" + [string]$category.kind +
    " landmark=" + $isLandmark +
    " critical=" + $isStoryCritical +
    " candidates=" + $selected.Count +
    " totalAssignments=" + $totalSelected +
    " uniquePaths=" + $usageByPath.Count)
}

$populatedCount=@($categoryReports | Where-Object { [int]$_.candidates -gt 0 }).Count
$landmarkCategoryCount=@($landmarkReports).Count
$landmarkReadyCount=@($landmarkReports | Where-Object { [bool]$_.has_candidates }).Count
$minimumPopulated=[int]$manifest.source_policy.minimum_populated_categories
$minimumLandmark=[int]$manifest.source_policy.minimum_landmark_categories

if($populatedCount -lt $minimumPopulated){
  throw "F108_MAX_SAFE_POPULATED_COVERAGE_FAIL populated=$populatedCount required=$minimumPopulated"
}
if($landmarkCategoryCount -lt $minimumLandmark){
  throw "F108_MAX_SAFE_LANDMARK_CONTRACT_FAIL configured=$landmarkCategoryCount required=$minimumLandmark"
}
if($landmarkReadyCount -lt $minimumLandmark){
  throw "F108_MAX_SAFE_LANDMARK_COVERAGE_FAIL ready=$landmarkReadyCount required=$minimumLandmark"
}

$groupCoverage=@()
foreach($prop in @($manifest.coverage_targets.soft_group_targets.PSObject.Properties)){
  $groupId=([string]$prop.Name).ToLowerInvariant()
  $target=[int]$prop.Value
  $configured=@($categoryReports | Where-Object { ([string]$_.coverage_group).ToLowerInvariant() -eq $groupId }).Count
  $ready=@($categoryReports | Where-Object { ([string]$_.coverage_group).ToLowerInvariant() -eq $groupId -and [int]$_.candidates -gt 0 }).Count
  $groupCoverage += [ordered]@{
    coverage_group=$groupId
    configured_categories=$configured
    ready_categories=$ready
    soft_target=$target
    target_met=($ready -ge $target)
  }
  if($ready -lt $target){
    Write-Host ("F108_MAX_SAFE_SOFT_GAP group=" + $groupId + " ready=" + $ready + " target=" + $target)
  }
}

$coveragePath=Join-Path $OutputRoot "coverage_report.json"
[ordered]@{
  schema_version=1
  pack_id=[string]$manifest.pack_id
  populated_categories=$populatedCount
  minimum_populated_categories=$minimumPopulated
  configured_landmark_categories=$landmarkCategoryCount
  ready_landmark_categories=$landmarkReadyCount
  minimum_landmark_categories=$minimumLandmark
  unique_selected_paths=$usageByPath.Count
  total_candidate_assignments=$totalSelected
  max_category_reuse_per_source_path=$maxReuse
  soft_group_coverage=$groupCoverage
  visual_acceptance="NOT_CLAIMED"
} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $coveragePath -Encoding UTF8

$summaryPath=Join-Path $OutputRoot "summary.json"
[ordered]@{
  schema_version=1
  pack_id=[string]$manifest.pack_id
  canonical_mission_id=[string]$manifest.canonical_mission_id
  runtime_consumers=@($manifest.runtime_consumers)
  chapter_plan=[string]$manifest.chapter_plan
  generated_utc=[DateTime]::UtcNow.ToString("o")
  warehouse_files=$allFiles.Count
  eligible_files=$eligibleRows.Count
  blocked_bmp=$blockedBmp
  total_candidate_assignments=$totalSelected
  unique_selected_paths=$usageByPath.Count
  total_assignment_ceiling=$totalCeiling
  populated_categories=$populatedCount
  landmark_categories=$landmarkCategoryCount
  landmark_ready=$landmarkReadyCount
  categories=$categoryReports
  coverage_report=$coveragePath
  runtime_integration="GATED_NOT_STARTED"
  visual_acceptance="NOT_CLAIMED"
  acceptance_boundary=[string]$manifest.acceptance_boundary
} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $summaryPath -Encoding UTF8

Write-Host ("F108_MAX_SAFE_COVERAGE_PASS populated=" + $populatedCount +
  " requiredPopulated=" + $minimumPopulated +
  " landmarkReady=" + $landmarkReadyCount +
  " requiredLandmark=" + $minimumLandmark +
  " uniquePaths=" + $usageByPath.Count)
Write-Host ("F108_MAX_SAFE_SOURCE_PASS categories=" + $categoryReports.Count +
  " assignments=" + $totalSelected +
  " uniquePaths=" + $usageByPath.Count +
  " ceiling=" + $totalCeiling +
  " summary=" + $summaryPath)
exit 0
