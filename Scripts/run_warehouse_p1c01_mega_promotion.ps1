param(
  [string]$ManifestPath = "Data/WarehouseP1C01MegaPromotionTrainV1.json",
  [string]$WarehouseRoot = "D:\actions-runner\_warehouse\ShireJourney",
  [string]$OutputRoot = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.IO.Compression.FileSystem

function Get-OptionalPropertyValue {
  param([object]$Object,[string]$Name,[object]$Default=$null)
  if($null -eq $Object){ return $Default }
  $p=$Object.PSObject.Properties[$Name]
  if($null -eq $p){ return $Default }
  return $p.Value
}

function Test-DangerousExtension([string]$Extension) {
  return ([string]$Extension).ToLowerInvariant() -in @(".exe",".msi",".cmd",".bat",".ps1",".vbs",".js",".scr",".com")
}

# Receipts from the legacy C: runner must resolve to the current Warehouse
# on D: ONLY under the canonical /ShireJourney/ root. Per-file SHA is checked
# after rebasing, so this is never permission to trust a fabricated receipt.
function Resolve-WarehousePayloadPath {
  param([string]$Path,[string]$WarehouseRoot)
  if([string]::IsNullOrWhiteSpace($Path)){ return $Path }
  if(Test-Path -LiteralPath $Path -PathType Leaf){ return $Path }
  $normalized=$Path.Replace([char]92,'/')
  $marker='/ShireJourney/'
  $index=$normalized.IndexOf($marker,[StringComparison]::OrdinalIgnoreCase)
  if($index -lt 0){ return $Path }
  $relative=$normalized.Substring($index + $marker.Length)
  if([string]::IsNullOrWhiteSpace($relative)){ return $Path }
  $pieces=@($relative.Split('/') | Where-Object { $_ -ne '' })
  if(@($pieces | Where-Object { $_ -eq '..' -or $_ -eq '.' }).Count -gt 0){ return $Path }
  $rootFull=[IO.Path]::GetFullPath($WarehouseRoot).TrimEnd([char]92,[char]47)
  $candidate=[IO.Path]::GetFullPath((Join-Path $rootFull ($relative.Replace('/',[IO.Path]::DirectorySeparatorChar))))
  if(-not $candidate.StartsWith(($rootFull + [IO.Path]::DirectorySeparatorChar),[StringComparison]::OrdinalIgnoreCase)){ return $Path }
  if(Test-Path -LiteralPath $candidate -PathType Leaf){
    $script:RebasedReceiptCount++
    return $candidate
  }
  return $Path
}

function Test-SelectorMatch {
  param([object]$Selector,[object]$Row)
  $providers=@($Selector.providers | ForEach-Object { ([string]$_).ToUpperInvariant() })
  if($providers.Count -gt 0 -and $providers -notcontains ([string]$Row.provider).ToUpperInvariant()){ return $false }

  $assetIds=@($Selector.asset_ids | ForEach-Object { ([string]$_).ToLowerInvariant() })
  $keywords=@($Selector.category_keywords | ForEach-Object { ([string]$_).ToLowerInvariant() })
  $assetId=([string]$Row.asset_id).ToLowerInvariant()
  $assetSlug=([string]$Row.asset_slug).ToLowerInvariant()
  $category=([string]$Row.category).ToLowerInvariant()
  $path=([string]$Row.path).ToLowerInvariant()

  if($assetIds.Count -gt 0 -and ($assetIds -contains $assetId -or $assetIds -contains $assetSlug)){ return $true }
  $haystack=($assetId+" "+$assetSlug+" "+$category+" "+$path)
  foreach($k in $keywords){ if($k -and $haystack.Contains($k)){ return $true } }
  return $false
}

function Get-SafeArchiveEntries {
  param([string]$ArchivePath)
    $archive=[IO.Compression.ZipFile]::OpenRead($ArchivePath)
  try {
    $entries=@()
    $total=[int64]0
    $count=0
    foreach($entry in $archive.Entries){
      $count++
      if($count -gt 20000){ throw "archive_entry_budget_exceeded" }
      $name=$entry.FullName.Replace([char]92,'/')
      $parts=@($name.Split('/') | Where-Object { $_ -ne '' })
      if($name.StartsWith('/') -or $name -match '^[A-Za-z]:' -or @($parts | Where-Object { $_ -eq '..' }).Count -gt 0){
        throw "archive_path_unsafe"
      }
      $ext=[IO.Path]::GetExtension($name).ToLowerInvariant()
      if(Test-DangerousExtension $ext){ throw "archive_dangerous_extension:$ext" }
      if($ext -eq ".bmp"){ throw "archive_forbidden_bmp" }
      if($entry.Length -gt 536870912){ throw "archive_single_entry_budget_exceeded" }
      $total += [int64]$entry.Length
      if($total -gt 2147483648){ throw "archive_total_budget_exceeded" }
      if(-not [string]::IsNullOrWhiteSpace($entry.Name)){
        $entries += [pscustomobject]@{ entry=$entry; name=$name; extension=$ext; size=[int64]$entry.Length }
      }
    }
    return ,$entries
  }
  finally { $archive.Dispose() }
}

function Copy-SelectedArchive {
  param([string]$ArchivePath,[string]$Destination,[string[]]$AllowedExtensions)
    if(Test-Path -LiteralPath $Destination){ Remove-Item -LiteralPath $Destination -Recurse -Force }
  New-Item -ItemType Directory -Path $Destination -Force | Out-Null
  $archive=[IO.Compression.ZipFile]::OpenRead($ArchivePath)
  $written=0
  $bytes=[int64]0
  try {
    foreach($entry in $archive.Entries){
      if([string]::IsNullOrWhiteSpace($entry.Name)){ continue }
      $name=$entry.FullName.Replace([char]92,'/')
      $parts=@($name.Split('/') | Where-Object { $_ -ne '' })
      if($name.StartsWith('/') -or $name -match '^[A-Za-z]:' -or @($parts | Where-Object { $_ -eq '..' }).Count -gt 0){ throw "archive_path_unsafe" }
      $ext=[IO.Path]::GetExtension($name).ToLowerInvariant()
      if(Test-DangerousExtension $ext -or $ext -eq ".bmp"){ throw "archive_forbidden_extension:$ext" }
      if($AllowedExtensions.Count -gt 0 -and $AllowedExtensions -notcontains $ext){ continue }
      $target=Join-Path $Destination ($name -replace '/',[IO.Path]::DirectorySeparatorChar)
      $targetDir=Split-Path $target -Parent
      if(-not (Test-Path -LiteralPath $targetDir)){ New-Item -ItemType Directory -Path $targetDir -Force | Out-Null }
      [IO.Compression.ZipFileExtensions]::ExtractToFile($entry,$target,$true)
      $written++
      $bytes += [int64]$entry.Length
      if($written -gt 6000 -or $bytes -gt 2147483648){ throw "selected_extraction_budget_exceeded" }
    }
  }
  finally { $archive.Dispose() }
  return [pscustomobject]@{ files=$written; bytes=$bytes }
}

$ProjectRoot=Split-Path $PSScriptRoot -Parent
if(-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)){
  $candidate=Join-Path $ProjectRoot $ManifestPath
  if(Test-Path -LiteralPath $candidate -PathType Leaf){ $ManifestPath=$candidate }
}
if(-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)){ throw "P1C01 mega promotion manifest missing: $ManifestPath" }
if(-not (Test-Path -LiteralPath $WarehouseRoot -PathType Container)){ throw "Warehouse root missing: $WarehouseRoot" }

$manifest=Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
if([string]::IsNullOrWhiteSpace($OutputRoot)){ $OutputRoot=[string]$manifest.output_root }
if([string]::IsNullOrWhiteSpace($OutputRoot)){ throw "Output root missing" }
New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null

# DEC-109: A valid receipt of prepared output files lets us skip old archive
# extraction. Reuse is proven by the original source SHA and each output SHA.
$previousPrepared=@{}
$previousReportPath=Join-Path $OutputRoot "p1c01_mega_promotion_latest.json"
if(Test-Path -LiteralPath $previousReportPath -PathType Leaf){
  try{
    $previousReport=Get-Content -LiteralPath $previousReportPath -Raw | ConvertFrom-Json
    foreach($old in @($previousReport.prepared)){
      $key=([string]$old.class+"|"+[string]$old.provider+"|"+[string]$old.staged_sha256+"|"+[string]$old.prepared_root).ToLowerInvariant()
      $previousPrepared[$key]=$old
    }
    Write-Host ("P1C01_NEW_ONLY_RECEIPT_RESUME previous="+$previousPrepared.Count)
  }catch{
    Write-Host ("P1C01_NEW_ONLY_RECEIPT_REFRESH reason="+$_.Exception.Message)
  }
}
$reusedCount=0
$newlyPreparedCount=0
$newlyPreparedBytes=[int64]0
$minimumFreeReserveBytes=[int64]6442450944

$RebasedReceiptCount=0
$receiptRows=@()
$seen=@{}
$badReceipts=@()
foreach($receiptFile in @(Get-ChildItem -LiteralPath $WarehouseRoot -Recurse -File -Filter "receipt_*.json")){
  try { $receipt=Get-Content -LiteralPath $receiptFile.FullName -Raw | ConvertFrom-Json }
  catch {
    $badReceipts += [ordered]@{receipt=$receiptFile.FullName;reason="invalid_json";detail=$_.Exception.Message}
    continue
  }
  $provider=[string](Get-OptionalPropertyValue $receipt "provider" "")
  $batch=[string](Get-OptionalPropertyValue $receipt "batch_id" "")
  foreach($item in @(Get-OptionalPropertyValue $receipt "files" @())){
    $path=[string](Get-OptionalPropertyValue $item "file" "")
    $sha=([string](Get-OptionalPropertyValue $item "sha256" "")).ToLowerInvariant()
    if([string]::IsNullOrWhiteSpace($path)){
      $path=[string](Get-OptionalPropertyValue $item "archive" "")
      $sha=([string](Get-OptionalPropertyValue $item "archive_sha256" "")).ToLowerInvariant()
    }
    if([string]::IsNullOrWhiteSpace($path)){ continue }
    $path=Resolve-WarehousePayloadPath -Path $path -WarehouseRoot $WarehouseRoot
    $key=($path.ToLowerInvariant()+"|"+$sha)
    if($seen.ContainsKey($key)){ continue }
    $seen[$key]=$true
    $receiptRows += [pscustomobject]@{
      provider=$provider
      batch_id=$batch
      asset_id=[string](Get-OptionalPropertyValue $item "asset_id" "")
      asset_slug=[string](Get-OptionalPropertyValue $item "asset_slug" "")
      category=[string](Get-OptionalPropertyValue $item "category" "")
      path=$path
      declared_sha256=$sha
      source_page=[string](Get-OptionalPropertyValue $item "source_page" "")
      source_url=[string](Get-OptionalPropertyValue $item "source_url" "")
      receipt=$receiptFile.FullName
    }
  }
}

$prepared=@()
$pending=@()
$manualQueue=@()
foreach($selector in @($manifest.classes | Sort-Object order)){
  $matches=@($receiptRows | Where-Object { Test-SelectorMatch -Selector $selector -Row $_ })
  if($matches.Count -eq 0){
    $pending += [ordered]@{class=[string]$selector.id;reason="no_matching_staged_receipt"}
    continue
  }

  # Old fixed per-class First N cap could consume every slot with existing
  # receipts and starve newly downloaded sources. Walk all matching receipts,
  # deduplicating valid prepared outputs and checking live storage per new file.
  $selected=@($matches | Sort-Object provider,asset_id,asset_slug,path)
  Write-Host ("P1C01_NEW_ONLY_CLASS_SCAN class="+[string]$selector.id+" eligible="+$selected.Count+" legacy_cap_ignored=yes")
  foreach($row in $selected){
    if(-not (Test-Path -LiteralPath $row.path -PathType Leaf)){
      $manualQueue += [ordered]@{class=[string]$selector.id;provider=$row.provider;asset_id=$row.asset_id;path=$row.path;reason="receipt_file_missing"}
      continue
    }
    $actual=(Get-FileHash -LiteralPath $row.path -Algorithm SHA256).Hash.ToLowerInvariant()
    if([string]::IsNullOrWhiteSpace($row.declared_sha256) -or $actual -ne $row.declared_sha256){
      $manualQueue += [ordered]@{class=[string]$selector.id;provider=$row.provider;asset_id=$row.asset_id;path=$row.path;reason="receipt_sha256_mismatch";expected=$row.declared_sha256;actual=$actual}
      continue
    }

    $ext=[IO.Path]::GetExtension($row.path).ToLowerInvariant()
    if(Test-DangerousExtension $ext -or $ext -eq ".bmp"){
      $manualQueue += [ordered]@{class=[string]$selector.id;provider=$row.provider;asset_id=$row.asset_id;path=$row.path;reason="forbidden_payload_extension";extension=$ext}
      continue
    }

    $safeId=(([string]$row.asset_id)+([string]$row.asset_slug))
    if([string]::IsNullOrWhiteSpace($safeId)){ $safeId=[IO.Path]::GetFileNameWithoutExtension($row.path) }
    $safeId=$safeId -replace '[^A-Za-z0-9_.-]','_'
    $dest=Join-Path $OutputRoot (([string]$selector.id)+"\"+(([string]$row.provider) -replace '[^A-Za-z0-9_.-]','_')+"\"+$safeId)
    if($ext -eq ".zip"){
      # ExtractToFile on stock Windows has a practical MAX_PATH limit.
      # Preserve archive-relative paths, but shorten only the extraction root
      # for an archive whose eligible entry would otherwise exceed 240 chars.
      try{
        $archiveEntries=@(Get-SafeArchiveEntries -ArchivePath $row.path)
        $maxRelativeLength=0
        foreach($entry in $archiveEntries){
          if(([string]$entry.extension).ToLowerInvariant() -in @(".fbx",".png",".tga",".wav",".obj")){
            $maxRelativeLength=[Math]::Max($maxRelativeLength,([string]$entry.name).Length)
          }
        }
        if(($dest.Length + 1 + $maxRelativeLength) -gt 238){
          $category=([string]$selector.id).Replace("P1C01_","")
          if($category.Length -gt 8){ $category=$category.Substring(0,8) }
          $shortRoot=Join-Path $WarehouseRoot "_pj"
          $dest=Join-Path $shortRoot ($category+"_"+$actual.Substring(0,22))
          if(($dest.Length + 1 + $maxRelativeLength) -gt 242){
            $manualQueue += [ordered]@{class=[string]$selector.id;path=$row.path;reason="archive_relative_path_exceeds_windows_limit";longest_relative=$maxRelativeLength}
            continue
          }
          Write-Host ("P1C01_NEW_ONLY_COMPACT_ARCHIVE_ROOT class="+[string]$selector.id+" sha="+$actual.Substring(0,12))
        }
      }catch{
        $manualQueue += [ordered]@{class=[string]$selector.id;path=$row.path;reason="archive_path_preflight_failed";detail=$_.Exception.Message}
        continue
      }
    }
    $reuseKey=([string]$selector.id+"|"+[string]$row.provider+"|"+$actual+"|"+$dest).ToLowerInvariant()
    if($previousPrepared.ContainsKey($reuseKey)){
      $old=$previousPrepared[$reuseKey]
      $oldProof=@(Get-OptionalPropertyValue $old "prepared_hashes" @())
      $stillValid=($oldProof.Count -gt 0 -and $oldProof.Count -eq [int]$old.prepared_files)
      if($stillValid){
        foreach($part in $oldProof){
          $rel=[string]$part.path
          $pieces=@($rel.Replace([char]92,'/').Split('/') | Where-Object { $_ -ne '' })
          if([IO.Path]::IsPathRooted($rel) -or @($pieces | Where-Object { $_ -eq '..' }).Count -gt 0){
            $stillValid=$false; break
          }
          $outputFile=Join-Path $dest $rel
          if(-not (Test-Path -LiteralPath $outputFile -PathType Leaf)){
            $stillValid=$false; break
          }
          $existingFile=Get-Item -LiteralPath $outputFile
          if([int64]$existingFile.Length -ne [int64]$part.size -or (Get-FileHash -LiteralPath $outputFile -Algorithm SHA256).Hash.ToLowerInvariant() -ne ([string]$part.sha256).ToLowerInvariant()){
            $stillValid=$false; break
          }
        }
      }
      if($stillValid){
        $prepared += $old
        $reusedCount++
        Write-Host ("P1C01_NEW_ONLY_REUSED class="+[string]$selector.id+" source_sha256="+$actual+" files="+$old.prepared_files)
        continue
      }
    }

    $allowed=@()
    foreach($f in @($selector.required_formats)){
      switch(([string]$f).ToUpperInvariant()){
        "PNG" {$allowed += ".png"}
        "TGA" {$allowed += ".tga"}
        "FBX" {$allowed += ".fbx"}
        "OBJ" {$allowed += ".obj"}
        "WAV" {$allowed += ".wav"}
      }
    }
    $allowed=@($allowed | Select-Object -Unique)

    # No arbitrary count cap: storage, archive safety and real source QC
    # determine how much can be added to this wave.
    try{
      $requiredBytes=[int64](Get-Item -LiteralPath $row.path).Length
      if($ext -eq ".zip"){
        $entries=@(Get-SafeArchiveEntries -ArchivePath $row.path)
        $requiredBytes=[int64]0
        foreach($entry in $entries){
          if($allowed.Count -eq 0 -or $allowed -contains [string]$entry.extension){
            $requiredBytes += [int64]$entry.size
          }
        }
      }
      $targetDrive=[IO.DriveInfo]::new((Get-Item -LiteralPath $OutputRoot).PSDrive.Root)
      $freeBytes=[int64]$targetDrive.AvailableFreeSpace
      if($freeBytes -lt $minimumFreeReserveBytes + $requiredBytes){
        $pending += [ordered]@{class=[string]$selector.id;provider=$row.provider;asset_id=$row.asset_id;path=$row.path;reason="safe_storage_reserve_exhausted";free_bytes=$freeBytes;required_bytes=$requiredBytes;reserve_bytes=$minimumFreeReserveBytes}
        Write-Host ("P1C01_NEW_ONLY_STORAGE_DEFER class="+[string]$selector.id+" free="+$freeBytes+" need="+$requiredBytes)
        continue
      }
    }catch{
      $manualQueue += [ordered]@{class=[string]$selector.id;provider=$row.provider;asset_id=$row.asset_id;path=$row.path;reason="new_asset_preflight_rejected";detail=$_.Exception.Message}
      continue
    }

    $copiedFiles=0
    $copiedBytes=[int64]0
    $formatCounts=@{}
    if($ext -eq ".zip"){
      try{
        [void](Get-SafeArchiveEntries -ArchivePath $row.path)
        $x=Copy-SelectedArchive -ArchivePath $row.path -Destination $dest -AllowedExtensions $allowed
        $copiedFiles=[int]$x.files
        $copiedBytes=[int64]$x.bytes
        foreach($f in @(Get-ChildItem -LiteralPath $dest -Recurse -File)){
          $k=$f.Extension.ToLowerInvariant()
          if(-not $formatCounts.ContainsKey($k)){ $formatCounts[$k]=0 }
          $formatCounts[$k]=[int]$formatCounts[$k]+1
        }
      }catch{
        $manualQueue += [ordered]@{class=[string]$selector.id;provider=$row.provider;asset_id=$row.asset_id;path=$row.path;reason="selected_archive_materialization_failed";detail=$_.Exception.Message}
        if(Test-Path -LiteralPath $dest){ Remove-Item -LiteralPath $dest -Recurse -Force }
        continue
      }
    } else {
      if($allowed.Count -gt 0 -and $allowed -notcontains $ext){
        $pending += [ordered]@{class=[string]$selector.id;provider=$row.provider;asset_id=$row.asset_id;path=$row.path;reason="format_not_in_class_contract";extension=$ext}
        continue
      }
      $target=Join-Path $dest ([IO.Path]::GetFileName($row.path))
      New-Item -ItemType Directory -Path $dest -Force | Out-Null
      Copy-Item -LiteralPath $row.path -Destination $target -Force
      $copiedFiles=1
      $copiedBytes=(Get-Item -LiteralPath $target).Length
      $formatCounts[$ext]=1
    }

    $required=@($selector.required_formats | ForEach-Object { "."+([string]$_).ToLowerInvariant() })
    $requiredPresent=$false
    foreach($rf in $required){ if($formatCounts.ContainsKey($rf) -and [int]$formatCounts[$rf] -gt 0){ $requiredPresent=$true; break } }
    $state=if($copiedFiles -le 0){"STAGED_NO_SELECTED_FILES"}elseif($requiredPresent){"INTAKE_QC_PREPARED"}else{"STAGED_FORMAT_DEBT"}

    $fileHashes=@()
    foreach($preparedFile in @(Get-ChildItem -LiteralPath $dest -Recurse -File -ErrorAction Stop)){
      $relative=$preparedFile.FullName.Substring($dest.Length).TrimStart([char]92,[char]47)
      $fileHashes += [ordered]@{
        path=$relative
        size=[int64]$preparedFile.Length
        sha256=(Get-FileHash -LiteralPath $preparedFile.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
      }
    }
    $newlyPreparedCount++
    $newlyPreparedBytes += $copiedBytes
    $prepared += [ordered]@{
      prepared_hashes=$fileHashes
      class=[string]$selector.id
      provider=$row.provider
      batch_id=$row.batch_id
      asset_id=$row.asset_id
      asset_slug=$row.asset_slug
      source_page=$row.source_page
      source_url=$row.source_url
      staged_sha256=$actual
      prepared_root=$dest
      prepared_files=$copiedFiles
      prepared_bytes=$copiedBytes
      formats=$formatCounts
      state=$state
      ready_for_import=$false
    }
  }
}

$report=[ordered]@{
  schema_version=1
  train_id=[string]$manifest.train_id
  generated_at_utc=[DateTime]::UtcNow.ToString("o")
  source_receipt_rows=$receiptRows.Count
  source_paths_rebased_from_legacy_runner=$RebasedReceiptCount
  bad_receipt_count=$badReceipts.Count
  prepared_count=$prepared.Count
  intake_qc_prepared_count=@($prepared | Where-Object {$_.state -eq "INTAKE_QC_PREPARED"}).Count
  reused_existing_count=$reusedCount
  newly_prepared_count=$newlyPreparedCount
  newly_prepared_bytes=$newlyPreparedBytes
  selection_rule="ALL_ELIGIBLE_NEW_NOT_LEGACY_FIRST_N"
  minimum_free_storage_reserve_bytes=$minimumFreeReserveBytes
  pending_count=$pending.Count
  manual_queue_count=$manualQueue.Count
  prepared=$prepared
  pending=$pending
  manual_queue=$manualQueue
  bad_receipts=$badReceipts
  promotion_ceiling="INTAKE_QC"
  rules=@(
    "Prepared files are copies/extractions; original warehouse payloads remain untouched.",
    "No prepared item is READY_FOR_IMPORT until class-specific QC is completed.",
    "Animated classes require FBX before runtime promotion.",
    "Runtime integration, PIE, device, visual and performance acceptance remain open."
  )
}
$outPath=Join-Path $OutputRoot "p1c01_mega_promotion_latest.json"
$report | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $outPath -Encoding UTF8

Write-Host ("P1C01_NEW_ONLY_SOURCE_SUMMARY new="+$newlyPreparedCount+" new_bytes="+$newlyPreparedBytes+" reused="+$reusedCount+" rebased="+$RebasedReceiptCount+" deferred="+$pending.Count)
if($badReceipts.Count -gt 0 -or $manualQueue.Count -gt 0){
  Write-Host ("P1C01_MEGA_PROMOTION_PASS_WITH_MANUAL_QUEUE prepared="+$prepared.Count+" intakeQC="+$report.intake_qc_prepared_count+" pending="+$pending.Count+" manual="+$manualQueue.Count+" badReceipts="+$badReceipts.Count+" report="+$outPath)
  foreach($entry in $manualQueue){ Write-Host ("P1C01_MEGA_PROMOTION_MANUAL_QUEUE "+($entry | ConvertTo-Json -Compress -Depth 6)) }
  foreach($entry in $badReceipts){ Write-Host ("P1C01_MEGA_PROMOTION_BAD_RECEIPT "+($entry | ConvertTo-Json -Compress -Depth 6)) }
  exit 0
}
Write-Host ("P1C01_MEGA_PROMOTION_PASS prepared="+$prepared.Count+" intakeQC="+$report.intake_qc_prepared_count+" pending="+$pending.Count+" manual=0 badReceipts=0 report="+$outPath)
exit 0
