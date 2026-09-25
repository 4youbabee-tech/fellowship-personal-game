param(
    [string]$ManifestPath = "Data/WarehouseQuaterniusAcquisitionBatchV1.json",
    [switch]$Refresh
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "warehouse_network.ps1")
if (-not (Test-Path $ManifestPath)) { throw "Quaternius manifest not found: $ManifestPath" }

$manifest = Get-Content $ManifestPath -Raw | ConvertFrom-Json
$root = [string]$manifest.staging_root
New-Item -ItemType Directory -Path $root -Force | Out-Null
$headers = @{ "User-Agent" = "ShireJourneyWarehouse/1.0" }
$receiptPath = Join-Path $root ("receipt_" + $manifest.batch_id + ".json")
if (-not $Refresh -and (Test-WarehouseReceiptReusable -ReceiptPath $receiptPath -BatchId ([string]$manifest.batch_id))) { exit 0 }

$receipt = [ordered]@{
    batch_id = $manifest.batch_id
    provider = $manifest.provider
    license = $manifest.license
    staged_at_utc = [DateTime]::UtcNow.ToString("o")
    files = @()
    unresolved = @()
}

foreach ($pack in $manifest.source_pages) {
    $id = [string]$pack.id
    $page = [string]$pack.url
    $observedLicense = [string]$pack.observed_page_license
    if ([string]::IsNullOrWhiteSpace($observedLicense)) {
        $receipt.unresolved += [ordered]@{
            asset_id = $id
            source_page = $page
            reason = "license_not_verified_per_pack"
        }
        Write-Warning "Skipping Quaternius pack $id because no per-page license is recorded."
        continue
    }
    Write-Host "Resolving Quaternius pack $id license=$observedLicense"

    try {
        $response = Invoke-WarehousePage -Uri $page -Headers $headers
    }
    catch {
        $receipt.unresolved += [ordered]@{ asset_id=$id; source_page=$page; reason="page_fetch_failed"; detail=$_.Exception.Message }
        continue
    }

    $hrefs = @()
    foreach ($link in $response.Links) {
        if ($null -ne $link.href -and -not [string]::IsNullOrWhiteSpace([string]$link.href)) {
            $hrefs += [string]$link.href
        }
    }

    # Fallback regex because older PowerShell/HTML parsers can miss JS-light anchors.
    $regex = [regex]'href\s*=\s*["'']([^"'']+)["'']'
    foreach ($match in $regex.Matches([string]$response.Content)) {
        $hrefs += [string]$match.Groups[1].Value
    }

    $resolved = New-Object 'System.Collections.Generic.List[string]'
    foreach ($href in ($hrefs | Select-Object -Unique)) {
        try {
            $uri = [Uri]::new([Uri]$page, $href)
        }
        catch { continue }
        $u = $uri.AbsoluteUri
        $lower = $u.ToLowerInvariant()
        if ($lower.EndsWith(".zip") -or $lower.EndsWith(".7z") -or $lower.EndsWith(".rar") -or $lower.EndsWith(".fbx")) {
            $resolved.Add($u)
        }
    }

    if ($resolved.Count -eq 0) {
        $storeLinks = @($hrefs | Where-Object { $_ -match 'itch\.io|patreon|gumroad|member' } | Select-Object -Unique)
        $receipt.unresolved += [ordered]@{
            asset_id = $id
            source_page = $page
            reason = "no_public_direct_archive_discovered"
            store_links = $storeLinks
        }
        continue
    }

    $destDir = Join-Path $root ([string]$pack.category)
    New-Item -ItemType Directory -Path $destDir -Force | Out-Null

    foreach ($url in $resolved) {
        try {
            $uri = [Uri]$url
            $name = [IO.Path]::GetFileName($uri.LocalPath)
            if ([string]::IsNullOrWhiteSpace($name)) { continue }
            $dest = Join-Path $destDir $name
            if (-not (Test-Path $dest)) {
                Invoke-WarehouseDownload -Uri $url -Headers $headers -OutFile $dest | Out-Null
            }
            $file = Get-Item $dest
            $hash = (Get-FileHash $dest -Algorithm SHA256).Hash.ToLowerInvariant()
            $receipt.files += [ordered]@{
                asset_id = $id
                category = [string]$pack.category
                source_page = $page
                source_url = $url
                file = $dest
                size = [int64]$file.Length
                sha256 = $hash
                state = "STAGED"
                observed_page_license = $observedLicense
            }
        }
        catch {
            $receipt.unresolved += [ordered]@{ asset_id=$id; source_page=$page; source_url=$url; reason="download_failed"; detail=$_.Exception.Message }
        }
    }
}

$receipt | ConvertTo-Json -Depth 8 | Set-Content -Path $receiptPath -Encoding UTF8
Write-Host "QUATERNIUS_WAREHOUSE_STAGE_PASS files=$($receipt.files.Count) unresolved=$($receipt.unresolved.Count) receipt=$receiptPath"
