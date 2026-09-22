param(
    [string]$Root = "C:\actions-runner\_warehouse\ShireJourney"
)

$ErrorActionPreference = "Stop"
if (-not (Test-Path -LiteralPath $Root -PathType Container)) { throw "Warehouse root missing: $Root" }

$receiptFiles = @(Get-ChildItem -LiteralPath $Root -Recurse -File -Filter "receipt_*.json")
$allFiles = @(Get-ChildItem -LiteralPath $Root -Recurse -File)
$payloadFiles = @($allFiles | Where-Object { $_.Name -notlike "receipt_*.json" -and $_.Name -ne "warehouse_inventory_latest.json" })

$missing = @()
$badReceipt = @()
$records = @()
foreach($receiptFile in $receiptFiles){
  try { $receipt = Get-Content -LiteralPath $receiptFile.FullName -Raw | ConvertFrom-Json }
  catch { $badReceipt += [ordered]@{ receipt=$receiptFile.FullName; reason="invalid_json"; detail=$_.Exception.Message }; continue }
  $provider = [string]$receipt.provider
  $batchId = [string]$receipt.batch_id
  foreach($item in @($receipt.files)){
    $path = [string]$item.file
    if([string]::IsNullOrWhiteSpace($path)){ continue }
    if(-not (Test-Path -LiteralPath $path -PathType Leaf)){
      $missing += [ordered]@{ provider=$provider; batch_id=$batchId; path=$path }
      continue
    }
    $actual = Get-Item -LiteralPath $path
    $actualHash = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
    $declaredHash = ([string]$item.sha256).ToLowerInvariant()
    $records += [pscustomobject]@{
      provider=$provider
      batch_id=$batchId
      asset_id=[string]$item.asset_id
      asset_slug=[string]$item.asset_slug
      category=[string]$item.category
      path=$path
      extension=$actual.Extension.ToLowerInvariant()
      size=[int64]$actual.Length
      sha256=$actualHash
      declared_sha256=$declaredHash
      hash_match=([string]::IsNullOrWhiteSpace($declaredHash) -or $declaredHash -eq $actualHash)
      source_page=[string]$item.source_page
      source_url=[string]$item.source_url
      state=if([string]::IsNullOrWhiteSpace([string]$item.state)){"STAGED"}else{[string]$item.state}
    }
  }
}

$hashMismatch = @($records | Where-Object { -not $_.hash_match })
$dangerous = @($payloadFiles | Where-Object { $_.Extension.ToLowerInvariant() -in @(".exe",".msi",".cmd",".bat",".ps1",".vbs",".js",".scr",".com") })
$duplicateGroups = @($records | Group-Object sha256 | Where-Object { $_.Name -and $_.Count -gt 1 } | ForEach-Object {
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
  dangerous_payloads=@($dangerous.FullName)
  bad_receipts=$badReceipt
}

$outPath = Join-Path $Root "warehouse_inventory_latest.json"
$inventory | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $outPath -Encoding UTF8

if($missing.Count -gt 0 -or $hashMismatch.Count -gt 0 -or $dangerous.Count -gt 0 -or $badReceipt.Count -gt 0){
  Write-Host ("WAREHOUSE_INVENTORY_AUDIT_FAIL missing="+$missing.Count+" hashMismatch="+$hashMismatch.Count+" dangerous="+$dangerous.Count+" badReceipts="+$badReceipt.Count+" report="+$outPath)
  exit 2
}

Write-Host ("WAREHOUSE_INVENTORY_AUDIT_PASS payloadFiles="+$payloadFiles.Count+" bytes="+$inventory.payload_bytes+" receipts="+$receiptFiles.Count+" receiptRecords="+$records.Count+" duplicateGroups="+$duplicateGroups.Count+" report="+$outPath)

