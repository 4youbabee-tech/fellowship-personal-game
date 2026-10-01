$ErrorActionPreference = "Stop"

$scriptPath = Join-Path $PSScriptRoot "audit_warehouse_inventory.ps1"
$networkScriptPath = Join-Path $PSScriptRoot "warehouse_network.ps1"
. $networkScriptPath

$testRoot = Join-Path ([IO.Path]::GetTempPath()) ("shire-warehouse-supersession-" + [Guid]::NewGuid().ToString("N"))
$warehouseRoot = Join-Path $testRoot "warehouse"
$payloadDir = Join-Path $warehouseRoot "ambientCG\PLASTER"
New-Item -ItemType Directory -Path $payloadDir -Force | Out-Null

try {
    $reuseRoot = Join-Path $testRoot "reuse"
    New-Item -ItemType Directory -Path $reuseRoot -Force | Out-Null
    $reusePayload = Join-Path $reuseRoot "same-size-corrupt.bin"
    [IO.File]::WriteAllBytes($reusePayload, [byte[]](1,2,3,4,5,6,7,8))
    $reuseExpectedHash = (Get-FileHash -LiteralPath $reusePayload -Algorithm SHA256).Hash.ToLowerInvariant()
    $reuseReceiptPath = Join-Path $reuseRoot "receipt_REUSE_HASH_TEST.json"
    $reuseReceipt = [ordered]@{
        batch_id = "REUSE_HASH_TEST"
        files = @(
            [ordered]@{
                file = $reusePayload
                size = [int64](Get-Item -LiteralPath $reusePayload).Length
                sha256 = $reuseExpectedHash
            }
        )
    }
    $reuseReceipt | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $reuseReceiptPath -Encoding UTF8
    if (-not (Test-WarehouseReceiptReusable -ReceiptPath $reuseReceiptPath -BatchId "REUSE_HASH_TEST")) {
        throw "A valid receipt payload should be reusable."
    }

    [IO.File]::WriteAllBytes($reusePayload, [byte[]](8,7,6,5,4,3,2,1))
    if (Test-WarehouseReceiptReusable -ReceiptPath $reuseReceiptPath -BatchId "REUSE_HASH_TEST") {
        throw "A same-size SHA256 mismatch must not be reusable."
    }
    if (Test-Path -LiteralPath $reusePayload -PathType Leaf) {
        throw "The mismatched payload must be purged so the staging script can redownload only that file."
    }

    $payloadPath = Join-Path $payloadDir "Plaster007_2K-PNG.zip"
    [IO.File]::WriteAllText($payloadPath, "current-valid-payload")
    $currentHash = (Get-FileHash -LiteralPath $payloadPath -Algorithm SHA256).Hash.ToLowerInvariant()

    $oldProbe = Join-Path $testRoot "old-payload.bin"
    [IO.File]::WriteAllText($oldProbe, "historical-payload")
    $oldHash = (Get-FileHash -LiteralPath $oldProbe -Algorithm SHA256).Hash.ToLowerInvariant()
    Remove-Item -LiteralPath $oldProbe -Force

    $oldPathVariant = "C:\actions-runner\_warehouse\ShireJourney\ambientCG\PLASTER\Plaster007_2K-PNG.zip"
    $receiptV1 = [ordered]@{
        batch_id = "WAREHOUSE_AMBIENTCG_P1C01_V1"
        provider = "ambientCG"
        staged_at_utc = "2026-09-20T08:00:00Z"
        files = @(
            [ordered]@{
                asset_id = "Plaster007"
                file = $oldPathVariant
                sha256 = $oldHash
                state = "STAGED"
            }
        )
    }
    $receiptV2 = [ordered]@{
        batch_id = "WAREHOUSE_AMBIENTCG_TRILOGY_FOUNDATION_V2"
        provider = "ambientCG"
        staged_at_utc = "2026-09-29T08:00:00Z"
        files = @(
            [ordered]@{
                asset_id = "Plaster007"
                file = $payloadPath
                sha256 = $currentHash
                state = "STAGED"
            }
        )
    }

    $receiptV1 | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $warehouseRoot "receipt_WAREHOUSE_AMBIENTCG_P1C01_V1.json") -Encoding UTF8
    $receiptV2 | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $warehouseRoot "receipt_WAREHOUSE_AMBIENTCG_TRILOGY_FOUNDATION_V2.json") -Encoding UTF8

    $powershellExe = Join-Path $PSHOME "powershell.exe"
    if (-not (Test-Path -LiteralPath $powershellExe -PathType Leaf)) {
        throw "Windows PowerShell executable not found: $powershellExe"
    }

    $passOutput = & $powershellExe -NoLogo -NoProfile -ExecutionPolicy Bypass -File $scriptPath -Root $warehouseRoot 2>&1
    $passExit = $LASTEXITCODE
    if ($passExit -ne 0) {
        throw "Expected superseded historical receipt to be non-failing. Exit=$passExit Output=$($passOutput -join ' ')"
    }

    $reportPath = Join-Path $warehouseRoot "warehouse_inventory_latest.json"
    $report = Get-Content -LiteralPath $reportPath -Raw | ConvertFrom-Json
    if ([string]$report.provenance_rule -ne "latest_valid_receipt_per_normalized_payload_path") {
        throw "Unexpected provenance rule: $($report.provenance_rule)"
    }
    if ([int]$report.receipt_record_count -ne 2 -or [int]$report.active_receipt_record_count -ne 1 -or [int]$report.superseded_receipt_record_count -ne 1) {
        throw "Unexpected supersession counts total=$($report.receipt_record_count) active=$($report.active_receipt_record_count) superseded=$($report.superseded_receipt_record_count)"
    }
    if (@($report.hash_mismatches).Count -ne 0) {
        throw "Historical superseded hash must not fail the active payload."
    }
    if (($passOutput -join " ") -notmatch "WAREHOUSE_RECEIPT_ROOT_REBASE") {
        throw "Migrated legacy receipt path was not explicitly rebased to the active warehouse root."
    }

    $superseded = @($report.superseded_receipt_records)
    if ($superseded.Count -ne 1 -or [string]$superseded[0].superseded_batch_id -ne "WAREHOUSE_AMBIENTCG_P1C01_V1" -or [string]$superseded[0].active_batch_id -ne "WAREHOUSE_AMBIENTCG_TRILOGY_FOUNDATION_V2") {
        throw "Supersession report did not preserve V1 as history and V2 as active provenance."
    }

    [IO.File]::WriteAllText($payloadPath, "tampered-after-v2")
    $failOutput = & $powershellExe -NoLogo -NoProfile -ExecutionPolicy Bypass -File $scriptPath -Root $warehouseRoot 2>&1
    $failExit = $LASTEXITCODE
    if ($failExit -ne 2) {
        throw "Expected active V2 hash mismatch to remain fail-closed. Exit=$failExit Output=$($failOutput -join ' ')"
    }

    $failedReport = Get-Content -LiteralPath $reportPath -Raw | ConvertFrom-Json
    $mismatches = @($failedReport.hash_mismatches)
    if ($mismatches.Count -ne 1 -or [string]$mismatches[0].batch_id -ne "WAREHOUSE_AMBIENTCG_TRILOGY_FOUNDATION_V2") {
        throw "Active provenance mismatch must point to V2 only."
    }
    if (($failOutput -join " ") -notmatch "WAREHOUSE_HASH_MISMATCH provider=ambientCG batch=WAREHOUSE_AMBIENTCG_TRILOGY_FOUNDATION_V2") {
        throw "Fail-closed output did not identify the active V2 receipt."
    }

    Write-Host "WAREHOUSE_RECEIPT_SUPERSESSION_TEST_PASS historical_v1_superseded=true active_v2_enforced=true normalized_path=true real_windows_root_rebased=true migrated_root_rebased=true fail_closed=true hash_mismatch_targeted_purge=true"
}
finally {
    if (Test-Path -LiteralPath $testRoot -PathType Container) {
        Remove-Item -LiteralPath $testRoot -Recurse -Force
    }
}
