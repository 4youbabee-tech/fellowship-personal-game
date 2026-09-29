param(
    [string]$Root = "C:\actions-runner\_warehouse\ShireJourney"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-LatestHashRecords {
  param([object[]]$Rows)

  $hard = @()
  $superseded = @()
  $tracked = @($Rows | Where-Object { [bool]$_.hash_declared })

  foreach($group in @($tracked | Group-Object path)){
    $ordered = @($group.Group | Sort-Object -Property @{Expression="receipt_sort_ticks";Descending=$true}, @{Expression="receipt";Descending=$true})
    if($ordered.Count -eq 0){ continue }

    $latest = $ordered[0]
    if(-not [bool]$latest.hash_match){
      $hard += $latest
    }

    if($ordered.Count -gt 1){
      foreach($row in @($ordered | Select-Object -Skip 1)){
        if(-not [bool]$row.hash_match){
          $superseded += [pscustomobject]@{
            provider = [string]$row.provider
            path = [string]$row.path
            asset_id = [string]$row.asset_id
            superseded_batch_id = [string]$row.batch_id
            superseded_receipt = [string]$row.receipt
            superseded_declared_sha256 = [string]$row.declared_sha256
            current_batch_id = [string]$latest.batch_id
            current_receipt = [string]$latest.receipt
            current_declared_sha256 = [string]$latest.declared_sha256
            actual_sha256 = [string]$latest.actual_sha256
            current_hash_match = [bool]$latest.hash_match
          }
        }
      }
    }
  }

  return [pscustomobject]@{
    hard = @($hard)
    superseded = @($superseded)
  }
}

if (-not (Test-Path -LiteralPath $Root -PathType Container)) { throw "Warehouse root missing: $Root" }

$receiptFiles = @(Get-ChildItem -LiteralPath $Root -Recurse -File -Filter "receipt_*.json")
$allFiles = @(Get-ChildItem -LiteralPath $Root -Recurse -File)
$payloadFiles = @($allFiles | Where-Object { $_.Name -notlike "receipt_*.json" -and $_.Name -ne "warehouse_inventory_latest.json" })

$missing = @()
$badReceipt = @()
$records = @()
$licenseRecords = @()

foreach($receiptFile in $receiptFiles){
  try { $receipt = Get-Content -LiteralPath $receiptFile.FullName -Raw | ConvertFrom-Json }
  catch {
    $badReceipt += [ordered]@{ receipt=$receiptFile.FullName; reason="invalid_json"; detail=$_.Exception.Message }
    continue
  }

  $provider = [string]$receipt.provider
  $batchId = [string]$receipt.batch_id

  $receiptStamp = [DateTime]::MinValue
  $receiptStampRaw = [string]$receipt.staged_at_utc
  if([string]::IsNullOrWhiteSpace($receiptStampRaw) -or -not [DateTime]::TryParse($receiptStampRaw,[ref]$receiptStamp)){
    $receiptStamp = $receiptFile.LastWriteTimeUtc
  } else {
    $receiptStamp = $receiptStamp.ToUniversalTime()
  }
  $receiptStampText = $receiptStamp.ToString("o")
  $receiptSortTicks = [int64]$receiptStamp.Ticks

  foreach($item in @($receipt.files)){
    $path = [string]$item.file
    $declaredHash = ([string]$item.sha256).ToLowerInvariant()
    $recordKind = "file"

    if([string]::IsNullOrWhiteSpace($path)){
      $path = [string]$item.archive
      $declaredHash = ([string]$item.archive_sha256).ToLowerInvariant()
      $recordKind = "archive"
    }
    if([string]::IsNullOrWhiteSpace($path)){ continue }

    if(-not (Test-Path -LiteralPath $path -PathType Leaf)){
      $missing += [ordered]@{
        provider=$provider
        batch_id=$batchId
        receipt=$receiptFile.FullName
        path=$path
        record_kind=$recordKind
      }
      continue
    }

    $actual = Get-Item -LiteralPath $path
    $actualHash = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
    $hashDeclared = -not [string]::IsNullOrWhiteSpace($declaredHash)

    $records += [pscustomobject]@{
      provider=$provider
      batch_id=$batchId
      receipt=$receiptFile.FullName
      receipt_staged_at_utc=$receiptStampText
      receipt_sort_ticks=$receiptSortTicks
      asset_id=[string]$item.asset_id
      asset_slug=[string]$item.asset_slug
      category=[string]$item.category
      record_kind=$recordKind
      path=$path
      extension=$actual.Extension.ToLowerInvariant()
      size=[int64]$actual.Length
      actual_sha256=$actualHash
      declared_sha256=$declaredHash
      hash_declared=$hashDeclared
      hash_match=(-not $hashDeclared -or $declaredHash -eq $actualHash)
      source_page=[string]$item.source_page
      source_url=[string]$item.source_url
      state=if([string]::IsNullOrWhiteSpace([string]$item.state)){"STAGED"}else{[string]$item.state}
    }

    $licensePath = [string]$item.license_snapshot
    $declaredLicenseHash = ([string]$item.license_sha256).ToLowerInvariant()
    if(-not [string]::IsNullOrWhiteSpace($licensePath)){
      if(-not (Test-Path -LiteralPath $licensePath -PathType Leaf)){
        $missing += [ordered]@{
          provider=$provider
          batch_id=$batchId
          receipt=$receiptFile.FullName
          path=$licensePath
          record_kind="license_snapshot"
        }
      } else {
        $actualLicenseHash = (Get-FileHash -LiteralPath $licensePath -Algorithm SHA256).Hash.ToLowerInvariant()
        $licenseHashDeclared = -not [string]::IsNullOrWhiteSpace($declaredLicenseHash)
        $licenseRecords += [pscustomobject]@{
          provider=$provider
          batch_id=$batchId
          receipt=$receiptFile.FullName
          receipt_staged_at_utc=$receiptStampText
          receipt_sort_ticks=$receiptSortTicks
          asset_id=[string]$item.asset_id
          path=$licensePath
          record_kind="license_snapshot"
          actual_sha256=$actualLicenseHash
          declared_sha256=$declaredLicenseHash
          hash_declared=$licenseHashDeclared
          hash_match=(-not $licenseHashDeclared -or $declaredLicenseHash -eq $actualLicenseHash)
        }
      }
    }
  }
}

$payloadHashState = Resolve-LatestHashRecords -Rows @($records)
$licenseHashState = Resolve-LatestHashRecords -Rows @($licenseRecords)
$hashMismatch = @($payloadHashState.hard)
$licenseHashMismatch = @($licenseHashState.hard)
$supersededHashRecords = @($payloadHashState.superseded)
$supersededLicenseHashRecords = @($licenseHashState.superseded)

$dangerous = @($payloadFiles | Where-Object { $_.Extension.ToLowerInvariant() -in @(".exe",".msi",".cmd",".bat",".ps1",".vbs",".js",".scr",".com") })
$duplicateGroups = @($records | Group-Object actual_sha256 | Where-Object { $_.Name -and $_.Count -gt 1 } | ForEach-Object {
  [ordered]@{ sha256=$_.Name; count=$_.Count; paths=@($_.Group.path) }
})
$providerSummary = @($records | Group-Object provider | ForEach-Object {
  $bytes=($_.Group | Measure-Object -Property size -Sum).Sum
  [ordered]@{ provider=$_.Name; files=$_.Count; bytes=[int64]$bytes }
})
$extensionSummary = @($payloadFiles | Group-Object Extension | Sort-Object Count -Descending | ForEach-Object {
  [ordered]@{ extension=$_.Name.ToLowerInvariant(); files=$_.Count; bytes=[int64](($_.Group | Measure-Object -Property Length -Sum).Sum) }
})

$inventory = [ordered]@{
  schema_version=1
  generated_at_utc=[DateTime]::UtcNow.ToString("o")
  root=$Root
  receipt_count=$receiptFiles.Count
  payload_file_count=$payloadFiles.Count
  payload_bytes=[int64](($payloadFiles | Measure-Object -Property Length -Sum).Sum)
  receipt_record_count=$records.Count
  provider_summary=$providerSummary
  extension_summary=$extensionSummary
  duplicate_hash_groups=$duplicateGroups
  missing_referenced_files=$missing
  hash_mismatches=$hashMismatch
  superseded_hash_records=$supersededHashRecords
  license_hash_mismatches=$licenseHashMismatch
  superseded_license_hash_records=$supersededLicenseHashRecords
  dangerous_payloads=@($dangerous.FullName)
  bad_receipts=$badReceipt
}

$outPath = Join-Path $Root "warehouse_inventory_latest.json"
$inventory | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $outPath -Encoding UTF8

foreach($row in $supersededHashRecords | Select-Object -First 20){
  Write-Host ("WAREHOUSE_SUPERSEDED_HASH_RECORD provider="+[string]$row.provider+
    " asset="+[string]$row.asset_id+
    " path="+[string]$row.path+
    " supersededBatch="+[string]$row.superseded_batch_id+
    " supersededReceipt="+[string]$row.superseded_receipt+
    " supersededDeclared="+[string]$row.superseded_declared_sha256+
    " currentBatch="+[string]$row.current_batch_id+
    " currentReceipt="+[string]$row.current_receipt+
    " currentDeclared="+[string]$row.current_declared_sha256+
    " actual="+[string]$row.actual_sha256+
    " currentMatch="+[string]$row.current_hash_match)
}

foreach($row in $supersededLicenseHashRecords | Select-Object -First 20){
  Write-Host ("WAREHOUSE_SUPERSEDED_LICENSE_HASH_RECORD provider="+[string]$row.provider+
    " asset="+[string]$row.asset_id+
    " path="+[string]$row.path+
    " supersededReceipt="+[string]$row.superseded_receipt+
    " currentReceipt="+[string]$row.current_receipt+
    " actual="+[string]$row.actual_sha256+
    " currentMatch="+[string]$row.current_hash_match)
}

if($missing.Count -gt 0 -or $hashMismatch.Count -gt 0 -or $licenseHashMismatch.Count -gt 0 -or $dangerous.Count -gt 0 -or $badReceipt.Count -gt 0){
  foreach($row in $hashMismatch | Select-Object -First 20){
    Write-Host ("WAREHOUSE_HASH_MISMATCH provider="+[string]$row.provider+
      " batch="+[string]$row.batch_id+
      " asset="+[string]$row.asset_id+
      " receipt="+[string]$row.receipt+
      " kind="+[string]$row.record_kind+
      " path="+[string]$row.path+
      " declared="+[string]$row.declared_sha256+
      " actual="+[string]$row.actual_sha256)
  }
  foreach($row in $licenseHashMismatch | Select-Object -First 20){
    Write-Host ("WAREHOUSE_LICENSE_HASH_MISMATCH provider="+[string]$row.provider+
      " batch="+[string]$row.batch_id+
      " asset="+[string]$row.asset_id+
      " receipt="+[string]$row.receipt+
      " path="+[string]$row.path+
      " declared="+[string]$row.declared_sha256+
      " actual="+[string]$row.actual_sha256)
  }
  foreach($row in $missing | Select-Object -First 20){
    Write-Host ("WAREHOUSE_MISSING_REFERENCE provider="+[string]$row.provider+
      " batch="+[string]$row.batch_id+
      " receipt="+[string]$row.receipt+
      " kind="+[string]$row.record_kind+
      " path="+[string]$row.path)
  }
  Write-Host ("WAREHOUSE_INVENTORY_AUDIT_FAIL missing="+$missing.Count+
    " hashMismatch="+$hashMismatch.Count+
    " supersededHashRecords="+$supersededHashRecords.Count+
    " licenseHashMismatch="+$licenseHashMismatch.Count+
    " supersededLicenseHashRecords="+$supersededLicenseHashRecords.Count+
    " dangerous="+$dangerous.Count+
    " badReceipts="+$badReceipt.Count+
    " report="+$outPath)
  exit 2
}

Write-Host ("WAREHOUSE_INVENTORY_AUDIT_PASS payloadFiles="+$payloadFiles.Count+
  " bytes="+$inventory.payload_bytes+
  " receipts="+$receiptFiles.Count+
  " receiptRecords="+$records.Count+
  " duplicateGroups="+$duplicateGroups.Count+
  " supersededHashRecords="+$supersededHashRecords.Count+
  " supersededLicenseHashRecords="+$supersededLicenseHashRecords.Count+
  " report="+$outPath)
