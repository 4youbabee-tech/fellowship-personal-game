param(
    [string]$ManifestPath = "Data/WarehouseAcquisitionBatchV1.json"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $ManifestPath)) {
    throw "Warehouse manifest not found: $ManifestPath"
}

$manifest = Get-Content $ManifestPath -Raw | ConvertFrom-Json
$root = [string]$manifest.staging_root
$resolution = [string]$manifest.target_resolution
$maxBytes = [int64]$manifest.max_download_bytes

New-Item -ItemType Directory -Path $root -Force | Out-Null

$receipt = [ordered]@{
    batch_id = $manifest.batch_id
    provider = $manifest.provider
    license = $manifest.license
    staged_at_utc = [DateTime]::UtcNow.ToString("o")
    staging_root = $root
    files = @()
    total_bytes = 0
}

function Add-FileCandidate {
    param(
        [object]$Node,
        [string]$LogicalPath,
        [System.Collections.Generic.List[object]]$Out
    )

    if ($null -eq $Node) { return }

    if ($Node -is [System.Collections.IDictionary]) {
        foreach ($key in $Node.Keys) {
            Add-FileCandidate -Node $Node[$key] -LogicalPath ($LogicalPath + "/" + $key) -Out $Out
        }
        return
    }

    if ($Node -is [PSCustomObject]) {
        $props = $Node.PSObject.Properties
        $urlProp = $props | Where-Object { $_.Name -eq "url" } | Select-Object -First 1
        if ($urlProp) {
            $sizeProp = $props | Where-Object { $_.Name -eq "size" } | Select-Object -First 1
            $Out.Add([PSCustomObject]@{
                path = $LogicalPath
                url = [string]$urlProp.Value
                size = if ($sizeProp) { [int64]$sizeProp.Value } else { 0 }
            })
        }
        foreach ($p in $props) {
            if ($p.Name -ne "url" -and $p.Name -ne "size") {
                Add-FileCandidate -Node $p.Value -LogicalPath ($LogicalPath + "/" + $p.Name) -Out $Out
            }
        }
        return
    }

    if (($Node -is [System.Collections.IEnumerable]) -and -not ($Node -is [string])) {
        $index = 0
        foreach ($item in $Node) {
            Add-FileCandidate -Node $item -LogicalPath ($LogicalPath + "/" + $index) -Out $Out
            $index++
        }
    }
}

foreach ($asset in $manifest.assets) {
    $slug = [string]$asset.slug
    $apiUrl = "$($manifest.provider_api)/files/$slug"
    Write-Host "Warehouse stage: querying $apiUrl"

    $headers = @{ "User-Agent" = "ShireJourneyWarehouse/1.0" }
    $filesTree = Invoke-RestMethod -Uri $apiUrl -Headers $headers -Method Get

    $candidates = New-Object 'System.Collections.Generic.List[object]'
    Add-FileCandidate -Node $filesTree -LogicalPath "" -Out $candidates

    $chosen = @()
    foreach ($candidate in $candidates) {
        $url = [string]$candidate.url
        if ([string]::IsNullOrWhiteSpace($url)) { continue }

        $lower = $url.ToLowerInvariant()
        $pathLower = ([string]$candidate.path).ToLowerInvariant()

        $isAllowedExt =
            $lower.EndsWith(".png") -or
            $lower.EndsWith(".tga") -or
            $lower.EndsWith(".fbx") -or
            $lower.EndsWith(".zip")

        if (-not $isAllowedExt) { continue }

        $matchesResolution =
            $pathLower.Contains("/$resolution/") -or
            $pathLower.Contains("_$resolution") -or
            $lower.Contains("/$resolution/") -or
            $lower.Contains("_$resolution")

        if (-not $matchesResolution) { continue }

        # Prefer compact production maps; displacement/high-poly archives are intentionally skipped in V1.
        if ($pathLower.Contains("disp") -or $pathLower.Contains("displacement")) { continue }

        $chosen += $candidate
    }

    if ($chosen.Count -eq 0) {
        Write-Warning "No eligible $resolution PNG/TGA/FBX/ZIP files found for $slug"
        continue
    }

    $assetDir = Join-Path $root $slug
    New-Item -ItemType Directory -Path $assetDir -Force | Out-Null

    foreach ($candidate in $chosen) {
        $expected = [int64]$candidate.size
        if (($receipt.total_bytes + $expected) -gt $maxBytes) {
            Write-Warning "Warehouse byte cap reached; skipping remaining files."
            break
        }

        $uri = [Uri]$candidate.url
        $name = [IO.Path]::GetFileName($uri.LocalPath)
        if ([string]::IsNullOrWhiteSpace($name)) {
            $name = [Guid]::NewGuid().ToString("N") + ".bin"
        }

        $dest = Join-Path $assetDir $name
        if (-not (Test-Path $dest)) {
            Write-Host "Downloading $slug/$name"
            Invoke-WebRequest -Uri $candidate.url -Headers $headers -OutFile $dest -UseBasicParsing
        } else {
            Write-Host "Already staged: $slug/$name"
        }

        $file = Get-Item $dest
        $hash = (Get-FileHash $dest -Algorithm SHA256).Hash.ToLowerInvariant()
        $receipt.files += [ordered]@{
            asset_slug = $slug
            logical_path = [string]$candidate.path
            source_url = [string]$candidate.url
            file = $dest
            size = [int64]$file.Length
            sha256 = $hash
        }
        $receipt.total_bytes += [int64]$file.Length
    }
}

$receiptPath = Join-Path $root ("receipt_" + $manifest.batch_id + ".json")
$receipt | ConvertTo-Json -Depth 8 | Set-Content -Path $receiptPath -Encoding UTF8

Write-Host "WAREHOUSE_STAGE_PASS batch=$($manifest.batch_id) files=$($receipt.files.Count) bytes=$($receipt.total_bytes) receipt=$receiptPath"
