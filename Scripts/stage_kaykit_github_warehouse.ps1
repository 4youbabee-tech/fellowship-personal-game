param(
    [string]$ManifestPath = "Data/WarehouseKayKitGitHubAcquisitionBatchV1.json"
)

$ErrorActionPreference = "Stop"
if (-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)) {
    throw "KayKit manifest not found: $ManifestPath"
}

$manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
$root = [string]$manifest.staging_root
New-Item -ItemType Directory -Path $root -Force | Out-Null
$headers = @{ "User-Agent" = "ShireJourneyWarehouse/1.0" }
$totalBytes = [int64]0

$receipt = [ordered]@{
    batch_id = [string]$manifest.batch_id
    provider = [string]$manifest.provider
    license = [string]$manifest.license
    staged_at_utc = [DateTime]::UtcNow.ToString("o")
    files = @()
    skipped = @()
}

foreach ($pack in $manifest.packs) {
    $id = [string]$pack.id
    $category = [string]$pack.category
    $destDir = Join-Path $root $category
    New-Item -ItemType Directory -Path $destDir -Force | Out-Null

    $archivePath = Join-Path $destDir ($id + ".zip")
    $licensePath = Join-Path $destDir ($id + "_LICENSE.txt")

    try {
        if (-not (Test-Path -LiteralPath $archivePath -PathType Leaf)) {
            Invoke-WebRequest -Uri ([string]$pack.archive_url) -Headers $headers -OutFile $archivePath -UseBasicParsing
        }

        $archiveFile = Get-Item -LiteralPath $archivePath
        $size = [int64]$archiveFile.Length
        if ($size -le 0 -or $size -gt [int64]$pack.max_bytes) {
            Remove-Item -LiteralPath $archivePath -Force -ErrorAction SilentlyContinue
            $receipt.skipped += [ordered]@{
                asset_id = $id
                reason = "archive_size_out_of_bounds"
                observed_bytes = $size
                max_bytes = [int64]$pack.max_bytes
            }
            continue
        }

        if (($totalBytes + $size) -gt [int64]$manifest.max_total_download_bytes) {
            Remove-Item -LiteralPath $archivePath -Force -ErrorAction SilentlyContinue
            $receipt.skipped += [ordered]@{
                asset_id = $id
                reason = "batch_byte_cap_exceeded"
                observed_bytes = $size
            }
            continue
        }

        Invoke-WebRequest -Uri ([string]$pack.license_url) -Headers $headers -OutFile $licensePath -UseBasicParsing
        $licenseText = Get-Content -LiteralPath $licensePath -Raw
        if ($licenseText -notmatch "Creative Commons Zero|CC0") {
            Remove-Item -LiteralPath $archivePath -Force -ErrorAction SilentlyContinue
            Remove-Item -LiteralPath $licensePath -Force -ErrorAction SilentlyContinue
            $receipt.skipped += [ordered]@{
                asset_id = $id
                reason = "cc0_license_marker_missing"
            }
            continue
        }

        $archiveHash = (Get-FileHash -LiteralPath $archivePath -Algorithm SHA256).Hash.ToLowerInvariant()
        $licenseHash = (Get-FileHash -LiteralPath $licensePath -Algorithm SHA256).Hash.ToLowerInvariant()
        $totalBytes += $size

        $receipt.files += [ordered]@{
            asset_id = $id
            category = $category
            source_page = [string]$pack.source_page
            source_url = [string]$pack.archive_url
            license_url = [string]$pack.license_url
            archive = $archivePath
            archive_size = $size
            archive_sha256 = $archiveHash
            license_snapshot = $licensePath
            license_sha256 = $licenseHash
            expected_formats = @($pack.expected_formats)
            regional_use = @($pack.regional_use)
            suitability = [string]$pack.suitability
            state = "STAGED"
        }
    }
    catch {
        $receipt.skipped += [ordered]@{
            asset_id = $id
            source_page = [string]$pack.source_page
            reason = "download_or_validation_failed"
            detail = $_.Exception.Message
        }
    }
}

$receiptPath = Join-Path $root ("receipt_" + [string]$manifest.batch_id + ".json")
$receipt | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $receiptPath -Encoding UTF8
Write-Host "KAYKIT_WAREHOUSE_STAGE_PASS files=$($receipt.files.Count) skipped=$($receipt.skipped.Count) bytes=$totalBytes receipt=$receiptPath"
