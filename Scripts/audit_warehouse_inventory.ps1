param(
    [string]$Root = "C:\actions-runner\_warehouse\ShireJourney"
)

$ErrorActionPreference = "Stop"
if (-not (Test-Path -LiteralPath $Root -PathType Container)) { throw "Warehouse root missing: $Root" }

function Get-WarehouseNormalizedPathKey {
    param(
        [string]$Path,
        [string]$BaseRoot
    )

    if ([string]::IsNullOrWhiteSpace($Path)) { return "" }
    $expanded = [Environment]::ExpandEnvironmentVariables($Path)
    if (-not [IO.Path]::IsPathRooted($expanded)) {
        $expanded = Join-Path $BaseRoot $expanded
    }
    try {
        $full = [IO.Path]::GetFullPath($expanded)
    } catch {
        $full = $expanded
    }
    return ($full.Replace("/", "\").TrimEnd("\")).ToLowerInvariant()
}

function Get-WarehouseReceiptTimestampUtc {
    param(
        $Receipt,
        [System.IO.FileInfo]$ReceiptFile
    )

    $raw = [string]$Receipt.staged_at_utc
    if (-not [string]::IsNullOrWhiteSpace($raw)) {
        try {
            return ([DateTime]::Parse(
                $raw,
                [Globalization.CultureInfo]::InvariantCulture,
                [Globalization.DateTimeStyles]::AssumeUniversal -bor [Globalization.DateTimeStyles]::AdjustToUniversal
            )).ToUniversalTime()
        } catch {
            Write-Warning ("WAREHOUSE_RECEIPT_TIMESTAMP_FALLBACK receipt=" + $ReceiptFile.FullName + " staged_at_utc=" + $raw)
        }
    }
    return $ReceiptFile.LastWriteTimeUtc
}

$receiptFiles = @(Get-ChildItem -LiteralPath $Root -Recurse -File -Filter "receipt_*.json")
$allFiles = @(Get-ChildItem -LiteralPath $Root -Recurse -File)
$payloadFiles = @($allFiles | Where-Object { $_.Name -notlike "receipt_*.json" -and $_.Name -ne "warehouse_inventory_latest.json" })

$badReceipt = @()
$candidates = @()
foreach($receiptFile in $receiptFiles){
    try { $receipt = Get-Content -LiteralPath $receiptFile.FullName -Raw | ConvertFrom-Json }
    catch { $badReceipt += [ordered]@{ receipt=$receiptFile.FullName; reason="invalid_json"; detail=$_.Exception.Message }; continue }

    $provider = [string]$receipt.provider
    $batchId = [string]$receipt.batch_id
    $receiptTimestamp = Get-WarehouseReceiptTimestampUtc -Receipt $receipt -ReceiptFile $receiptFile
    $recordIndex = 0

    foreach($item in @($receipt.files)){
        $path = [string]$item.file
        $declaredHash = ([string]$item.sha256).ToLowerInvariant()
        $recordKind = "file"
        if([string]::IsNullOrWhiteSpace($path)){
            $path = [string]$item.archive
            $declaredHash = ([string]$item.archive_sha256).ToLowerInvariant()
            $recordKind = "archive"
        }
        if([string]::IsNullOrWhiteSpace($path)){
            $recordIndex++
            continue
        }

        $normalizedPath = Get-WarehouseNormalizedPathKey -Path $path -BaseRoot $Root
        $candidates += [pscustomobject]@{
            provider=$provider
            batch_id=$batchId
            asset_id=[string]$item.asset_id
            asset_slug=[string]$item.asset_slug
            category=[string]$item.category
            record_kind=$recordKind
            path=$path
            normalized_path=$normalizedPath
            declared_sha256=$declaredHash
            source_page=[string]$item.source_page
            source_url=[string]$item.source_url
            state=if([string]::IsNullOrWhiteSpace([string]$item.state)){"STAGED"}else{[string]$item.state}
            license_snapshot=[string]$item.license_snapshot
            license_sha256=([string]$item.license_sha256).ToLowerInvariant()
            receipt_path=$receiptFile.FullName
            receipt_staged_at_utc=$receiptTimestamp
            receipt_file_last_write_utc=$receiptFile.LastWriteTimeUtc
            receipt_record_index=$recordIndex
        }
        $recordIndex++
    }
}

$activeCandidates = @()
$superseded = @()
$sortProperties = @(
    @{ Expression={ $_.receipt_staged_at_utc }; Descending=$true },
    @{ Expression={ $_.receipt_file_last_write_utc }; Descending=$true },
    @{ Expression={ $_.receipt_path }; Descending=$true },
    @{ Expression={ $_.receipt_record_index }; Descending=$true }
)
foreach($group in @($candidates | Group-Object normalized_path)){
    $ordered = @($group.Group | Sort-Object -Property $sortProperties)
    if($ordered.Count -eq 0){ continue }

    $active = $ordered[0]
    $activeCandidates += $active

    for($i=1; $i -lt $ordered.Count; $i++){
        $older = $ordered[$i]
        $superseded += [ordered]@{
            normalized_path=[string]$older.normalized_path
            path=[string]$older.path
            provider=[string]$older.provider
            superseded_batch_id=[string]$older.batch_id
            superseded_receipt=[string]$older.receipt_path
            superseded_staged_at_utc=([DateTime]$older.receipt_staged_at_utc).ToUniversalTime().ToString("o")
            declared_sha256=[string]$older.declared_sha256
            active_batch_id=[string]$active.batch_id
            active_receipt=[string]$active.receipt_path
            active_staged_at_utc=([DateTime]$active.receipt_staged_at_utc).ToUniversalTime().ToString("o")
            active_declared_sha256=[string]$active.declared_sha256
            reason="newer_receipt_for_same_payload_path"
        }
    }
}

$missing = @()
$licenseHashMismatch = @()
$records = @()
foreach($candidate in $activeCandidates){
    $path = [string]$candidate.path
    if(-not (Test-Path -LiteralPath $path -PathType Leaf)){
        $missing += [ordered]@{
            provider=[string]$candidate.provider
            batch_id=[string]$candidate.batch_id
            path=$path
            record_kind=[string]$candidate.record_kind
            receipt=[string]$candidate.receipt_path
        }
        continue
    }

    $actual = Get-Item -LiteralPath $path
    $actualHash = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()

    $licensePath = [string]$candidate.license_snapshot
    $declaredLicenseHash = ([string]$candidate.license_sha256).ToLowerInvariant()
    if(-not [string]::IsNullOrWhiteSpace($licensePath)){
        if(-not (Test-Path -LiteralPath $licensePath -PathType Leaf)){
            $missing += [ordered]@{
                provider=[string]$candidate.provider
                batch_id=[string]$candidate.batch_id
                path=$licensePath
                record_kind="license_snapshot"
                receipt=[string]$candidate.receipt_path
            }
        } elseif(-not [string]::IsNullOrWhiteSpace($declaredLicenseHash)){
            $actualLicenseHash = (Get-FileHash -LiteralPath $licensePath -Algorithm SHA256).Hash.ToLowerInvariant()
            if($actualLicenseHash -ne $declaredLicenseHash){
                $licenseHashMismatch += [ordered]@{
                    provider=[string]$candidate.provider
                    batch_id=[string]$candidate.batch_id
                    asset_id=[string]$candidate.asset_id
                    path=$licensePath
                    declared_sha256=$declaredLicenseHash
                    actual_sha256=$actualLicenseHash
                    receipt=[string]$candidate.receipt_path
                }
            }
        }
    }

    $records += [pscustomobject]@{
        provider=[string]$candidate.provider
        batch_id=[string]$candidate.batch_id
        asset_id=[string]$candidate.asset_id
        asset_slug=[string]$candidate.asset_slug
        category=[string]$candidate.category
        record_kind=[string]$candidate.record_kind
        path=$path
        normalized_path=[string]$candidate.normalized_path
        extension=$actual.Extension.ToLowerInvariant()
        size=[int64]$actual.Length
        sha256=$actualHash
        declared_sha256=[string]$candidate.declared_sha256
        hash_match=([string]::IsNullOrWhiteSpace([string]$candidate.declared_sha256) -or [string]$candidate.declared_sha256 -eq $actualHash)
        source_page=[string]$candidate.source_page
        source_url=[string]$candidate.source_url
        state=[string]$candidate.state
        receipt=[string]$candidate.receipt_path
        receipt_staged_at_utc=([DateTime]$candidate.receipt_staged_at_utc).ToUniversalTime().ToString("o")
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
    schema_version=2
    generated_at_utc=[DateTime]::UtcNow.ToString("o")
    root=$Root
    receipt_count=$receiptFiles.Count
    receipt_record_count=$candidates.Count
    active_receipt_record_count=$activeCandidates.Count
    audited_active_file_count=$records.Count
    superseded_receipt_record_count=$superseded.Count
    superseded_receipt_records=$superseded
    provenance_rule="latest_valid_receipt_per_normalized_payload_path"
    payload_file_count=$payloadFiles.Count
    payload_bytes=[int64](($payloadFiles | Measure-Object -Property Length -Sum).Sum)
    provider_summary=$providerSummary
    extension_summary=$extensionSummary
    duplicate_hash_groups=$duplicateGroups
    missing_referenced_files=$missing
    hash_mismatches=$hashMismatch
    license_hash_mismatches=$licenseHashMismatch
    dangerous_payloads=@($dangerous.FullName)
    bad_receipts=$badReceipt
}

$outPath = Join-Path $Root "warehouse_inventory_latest.json"
$inventory | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $outPath -Encoding UTF8

Write-Host ("WAREHOUSE_PROVENANCE_RESOLUTION active="+$activeCandidates.Count+" superseded="+$superseded.Count+" receipts="+$receiptFiles.Count+" rule=latest_valid_receipt_per_normalized_payload_path")

if($missing.Count -gt 0 -or $hashMismatch.Count -gt 0 -or $licenseHashMismatch.Count -gt 0 -or $dangerous.Count -gt 0 -or $badReceipt.Count -gt 0){
    foreach($row in $hashMismatch | Select-Object -First 20){
        Write-Host ("WAREHOUSE_HASH_MISMATCH provider="+[string]$row.provider+
            " batch="+[string]$row.batch_id+
            " asset="+[string]$row.asset_id+
            " kind="+[string]$row.record_kind+
            " path="+[string]$row.path+
            " declared="+[string]$row.declared_sha256+
            " actual="+[string]$row.sha256+
            " receipt="+[string]$row.receipt)
    }
    foreach($row in $licenseHashMismatch | Select-Object -First 20){
        Write-Host ("WAREHOUSE_LICENSE_HASH_MISMATCH provider="+[string]$row.provider+
            " batch="+[string]$row.batch_id+
            " asset="+[string]$row.asset_id+
            " path="+[string]$row.path+
            " declared="+[string]$row.declared_sha256+
            " actual="+[string]$row.actual_sha256+
            " receipt="+[string]$row.receipt)
    }
    foreach($row in $missing | Select-Object -First 20){
        Write-Host ("WAREHOUSE_MISSING_REFERENCE provider="+[string]$row.provider+
            " batch="+[string]$row.batch_id+
            " kind="+[string]$row.record_kind+
            " path="+[string]$row.path+
            " receipt="+[string]$row.receipt)
    }
    Write-Host ("WAREHOUSE_INVENTORY_AUDIT_FAIL missing="+$missing.Count+" hashMismatch="+$hashMismatch.Count+" licenseHashMismatch="+$licenseHashMismatch.Count+" dangerous="+$dangerous.Count+" badReceipts="+$badReceipt.Count+" activeRecords="+$activeCandidates.Count+" superseded="+$superseded.Count+" report="+$outPath)
    exit 2
}

Write-Host ("WAREHOUSE_INVENTORY_AUDIT_PASS payloadFiles="+$payloadFiles.Count+" bytes="+$inventory.payload_bytes+" receipts="+$receiptFiles.Count+" receiptRecords="+$candidates.Count+" activeRecords="+$activeCandidates.Count+" superseded="+$superseded.Count+" duplicateGroups="+$duplicateGroups.Count+" report="+$outPath)
