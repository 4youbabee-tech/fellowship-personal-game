param(
    [string]$ManifestPath = "Data/WarehouseAudioAcquisitionBatchV1.json",
    [switch]$Refresh
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "warehouse_network.ps1")

if (-not (Test-Path $ManifestPath)) {
    throw "Audio warehouse manifest not found: $ManifestPath"
}

$manifest = Get-Content $ManifestPath -Raw | ConvertFrom-Json
$root = [string]$manifest.staging_root
$maxBytes = [int64]$manifest.max_download_bytes
New-Item -ItemType Directory -Path $root -Force | Out-Null
$receiptPath = Join-Path $root ("receipt_" + $manifest.batch_id + ".json")
if (-not $Refresh -and (Test-WarehouseReceiptReusable -ReceiptPath $receiptPath -BatchId ([string]$manifest.batch_id))) { exit 0 }

$receipt = [ordered]@{
    batch_id = $manifest.batch_id
    provider = $manifest.provider
    license = $manifest.license
    staged_at_utc = [DateTime]::UtcNow.ToString("o")
    staging_root = $root
    files = @()
    skipped_assets = @()
    total_bytes = 0
}

$headers = @{ "User-Agent" = "ShireJourneyWarehouse/1.0" }

foreach ($asset in $manifest.assets) {
    $id = [string]$asset.id
    $url = [string]$asset.download_url
    $name = [string]$asset.filename

    if ([string]::IsNullOrWhiteSpace($url) -or [string]::IsNullOrWhiteSpace($name)) {
        $receipt.skipped_assets += [ordered]@{
            asset_id = $id
            reason = "missing_download_url_or_filename"
        }
        continue
    }

    $destDir = Join-Path $root ([string]$asset.category)
    New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    $dest = Join-Path $destDir $name

    try {
        if (-not (Test-Path $dest)) {
            Write-Host "Downloading audio warehouse asset $id -> $name"
            Invoke-WarehouseDownload -Uri $url -Headers $headers -OutFile $dest | Out-Null
        } else {
            Write-Host "Already staged: $id -> $name"
        }

        $file = Get-Item $dest
        if (($receipt.total_bytes + [int64]$file.Length) -gt $maxBytes) {
            Remove-Item $dest -Force
            $receipt.skipped_assets += [ordered]@{
                asset_id = $id
                reason = "batch_byte_cap"
            }
            continue
        }

        $hash = (Get-FileHash $dest -Algorithm SHA256).Hash.ToLowerInvariant()
        $receipt.files += [ordered]@{
            asset_id = $id
            category = [string]$asset.category
            source_page = [string]$asset.source_page
            source_url = $url
            file = $dest
            size = [int64]$file.Length
            sha256 = $hash
            state = "STAGED"
        }
        $receipt.total_bytes += [int64]$file.Length
    }
    catch {
        Write-Warning "Audio warehouse download failed for $id : $($_.Exception.Message)"
        if (Test-Path $dest) {
            Remove-Item $dest -Force -ErrorAction SilentlyContinue
        }
        $receipt.skipped_assets += [ordered]@{
            asset_id = $id
            reason = "download_failed"
            detail = $_.Exception.Message
        }
    }
}

$receipt | ConvertTo-Json -Depth 8 | Set-Content -Path $receiptPath -Encoding UTF8

Write-Host "AUDIO_WAREHOUSE_STAGE_PASS batch=$($manifest.batch_id) files=$($receipt.files.Count) bytes=$($receipt.total_bytes) skipped=$($receipt.skipped_assets.Count) receipt=$receiptPath"
