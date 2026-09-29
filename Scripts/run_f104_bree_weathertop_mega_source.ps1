param(
  [string]$ManifestPath = "Data/F104BreeWeathertopMegaSourceSuperpackV1.json",
  [string]$WarehouseRoot = "D:\actions-runner\_warehouse\ShireJourney",
  [string]$OutputRoot = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path $PSScriptRoot -Parent
if(-not [IO.Path]::IsPathRooted($ManifestPath)){ $ManifestPath = Join-Path $ProjectRoot $ManifestPath }
if(-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)){ throw "F104_MEGA_SOURCE_MANIFEST_MISSING path=$ManifestPath" }
if(-not (Test-Path -LiteralPath $WarehouseRoot -PathType Container)){ throw "F104_MEGA_SOURCE_WAREHOUSE_MISSING root=$WarehouseRoot" }

$manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
if([string]::IsNullOrWhiteSpace($OutputRoot)){ $OutputRoot = Join-Path $WarehouseRoot "_f104_bree_weathertop_mega_source_v1" }
New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null

$warehouseItem = Get-Item -LiteralPath $WarehouseRoot
$drive = [IO.DriveInfo]::new($warehouseItem.PSDrive.Root)
$reserve = [int64]$manifest.source_policy.minimum_free_disk_reserve_bytes
$free = [int64]$drive.AvailableFreeSpace
if($free -lt $reserve){ throw "F104_MEGA_SOURCE_DISK_RESERVE_FAIL free=$free reserve=$reserve" }

$allFiles = @(Get-ChildItem -LiteralPath $WarehouseRoot -Recurse -File -ErrorAction SilentlyContinue |
  Where-Object { $_.FullName -notlike ($OutputRoot.TrimEnd("\") + "\*") })

$textureAllowed = @{}
foreach($x in @($manifest.source_policy.texture_extensions)){ $textureAllowed[([string]$x).ToLowerInvariant()] = $true }
$textureBlocked = @{}
foreach($x in @($manifest.source_policy.forbidden_texture_extensions)){ $textureBlocked[([string]$x).ToLowerInvariant()] = $true }
$staticAllowed = @{}
foreach($x in @($manifest.source_policy.static_source_extensions)){ $staticAllowed[([string]$x).ToLowerInvariant()] = $true }
$audioAllowed = @{}
foreach($x in @($manifest.source_policy.audio_extensions)){ $audioAllowed[([string]$x).ToLowerInvariant()] = $true }
$metadataAllowed = @{}
foreach($x in @($manifest.source_policy.metadata_extensions)){ $metadataAllowed[([string]$x).ToLowerInvariant()] = $true }
$animatedExt = ([string]$manifest.source_policy.animated_candidate_extension).ToLowerInvariant()

$eligible = New-Object System.Collections.ArrayList
$blockedBmp = 0
foreach($file in $allFiles){
  $ext = $file.Extension.ToLowerInvariant()
  if($textureBlocked.ContainsKey($ext)){ $blockedBmp++; continue }
  if($textureAllowed.ContainsKey($ext) -or $staticAllowed.ContainsKey($ext) -or $audioAllowed.ContainsKey($ext) -or $metadataAllowed.ContainsKey($ext)){
    [void]$eligible.Add($file)
  }
}
[object[]]$eligibleRows = $eligible.ToArray()

$perCategory = [int]$manifest.source_policy.max_candidates_per_category
$totalCeiling = [int]$manifest.source_policy.max_total_candidates
$totalSelected = 0
$categoryReports = @()

Write-Host ("F104_MEGA_SOURCE_BEGIN pack=" + [string]$manifest.pack_id +
  " warehouseFiles=" + $allFiles.Count +
  " eligibleFiles=" + $eligibleRows.Count +
  " blockedBmp=" + $blockedBmp +
  " freeBytes=" + $free)

foreach($category in @($manifest.categories)){
  if($totalSelected -ge $totalCeiling){ break }
  $kind = ([string]$category.kind).ToLowerInvariant()
  $keywords = @($category.keywords | ForEach-Object { ([string]$_).ToLowerInvariant() })
  $scored = New-Object System.Collections.ArrayList

  foreach($file in $eligibleRows){
    $ext = $file.Extension.ToLowerInvariant()
    if($kind -eq "animated" -and $ext -ne $animatedExt){ continue }
    if($kind -eq "audio" -and -not $audioAllowed.ContainsKey($ext)){ continue }
    if($kind -eq "surface" -and -not $textureAllowed.ContainsKey($ext) -and -not $metadataAllowed.ContainsKey($ext)){ continue }

    $haystack = $file.FullName.ToLowerInvariant()
    $matches = New-Object System.Collections.ArrayList
    foreach($keyword in $keywords){
      if(-not [string]::IsNullOrWhiteSpace($keyword) -and $haystack.Contains($keyword)){ [void]$matches.Add($keyword) }
    }
    if($matches.Count -eq 0){ continue }

    $score = [int]$matches.Count
    if($haystack.Contains("production")){ $score += 2 }
    if($haystack.Contains("imported")){ $score += 1 }
    if($ext -eq ".fbx"){ $score += 2 }
    if($textureAllowed.ContainsKey($ext)){ $score += 1 }

    [object[]]$matchedTerms = $matches.ToArray()
    [void]$scored.Add([pscustomobject]@{
      path = $file.FullName
      extension = $ext
      bytes = [int64]$file.Length
      score = $score
      matched_terms = $matchedTerms
    })
  }

  [object[]]$ranked = @($scored.ToArray() | Sort-Object -Property @{Expression="score";Descending=$true}, @{Expression="bytes";Descending=$false})
  $remaining = $totalCeiling - $totalSelected
  $take = [Math]::Min($perCategory,$remaining)
  [object[]]$selected = @($ranked | Select-Object -First $take)
  $totalSelected += $selected.Count

  $report = [ordered]@{
    schema_version = 1
    pack_id = [string]$manifest.pack_id
    category = [string]$category.id
    runtime_consumer = [string]$category.runtime
    kind = [string]$category.kind
    candidate_count = $selected.Count
    candidate_ceiling = $take
    candidates = $selected
    evidence_boundary = "Source index only; not READY_FOR_IMPORT or runtime acceptance."
  }
  $reportPath = Join-Path $OutputRoot (([string]$category.id) + ".json")
  $report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $reportPath -Encoding UTF8

  $categoryReports += [ordered]@{
    category=[string]$category.id
    runtime=[string]$category.runtime
    kind=[string]$category.kind
    candidates=$selected.Count
    report=$reportPath
  }
  Write-Host ("F104_MEGA_SOURCE_CATEGORY_PASS id=" + [string]$category.id +
    " kind=" + [string]$category.kind +
    " candidates=" + $selected.Count +
    " totalSelected=" + $totalSelected)
}

$summaryPath = Join-Path $OutputRoot "summary.json"
[ordered]@{
  schema_version = 1
  pack_id = [string]$manifest.pack_id
  canonical_mission_id = [string]$manifest.canonical_mission_id
  runtime_consumers = @($manifest.runtime_consumers)
  generated_utc = [DateTime]::UtcNow.ToString("o")
  warehouse_files = $allFiles.Count
  eligible_files = $eligibleRows.Count
  blocked_bmp = $blockedBmp
  total_selected = $totalSelected
  total_ceiling = $totalCeiling
  categories = $categoryReports
  runtime_integration = "GATED_NOT_STARTED"
  acceptance_boundary = [string]$manifest.acceptance_boundary
} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $summaryPath -Encoding UTF8

Write-Host ("F104_MEGA_SOURCE_PASS categories=" + $categoryReports.Count +
  " selected=" + $totalSelected +
  " ceiling=" + $totalCeiling +
  " summary=" + $summaryPath)
exit 0
