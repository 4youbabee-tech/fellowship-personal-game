param([string]$ManifestPath = "Data/WarehouseAmbientCGAcquisitionBatchV1.json")
$ErrorActionPreference = "Stop"
$manifest = Get-Content $ManifestPath -Raw | ConvertFrom-Json
$root = [string]$manifest.staging_root
New-Item -ItemType Directory -Path $root -Force | Out-Null
$headers = @{ "User-Agent" = "ShireJourneyWarehouse/1.0"; "Accept" = "application/json" }
$receipt = [ordered]@{ batch_id=$manifest.batch_id; provider=$manifest.provider; license=$manifest.license; staged_at_utc=[DateTime]::UtcNow.ToString("o"); files=@(); skipped=@(); total_bytes=0 }
foreach($lane in $manifest.search_lanes){
  $q=[uri]::EscapeDataString([string]$lane.q)
  $limit=[int]$lane.limit
  $url="$($manifest.api_base)?type=Material&sort=Popular&limit=$limit&include=downloadData&offset=0&q=$q"
  try { $data=Invoke-RestMethod -Uri $url -Headers $headers -Method Get } catch { $receipt.skipped += [ordered]@{ query=$lane.q; reason="api_query_failed"; detail=$_.Exception.Message }; continue }
  $assets=@()
  if($data.foundAssets){ $assets=@($data.foundAssets) } elseif($data.assets){ $assets=@($data.assets) } elseif($data -is [System.Collections.IEnumerable]){ $assets=@($data) }
  $taken=0
  foreach($asset in $assets){
    if($taken -ge 3){ break }
    $id=[string]$asset.assetId
    if([string]::IsNullOrWhiteSpace($id)){ $id=[string]$asset.id }
    if([string]::IsNullOrWhiteSpace($id)){ continue }
    $downloads=$null
    try { $downloads=$asset.downloadFolders.default.downloadFiletypeCategories.zip.downloads } catch {}
    if($null -eq $downloads){ continue }
    $match=$downloads | Where-Object { [string]$_.attribute -eq [string]$manifest.target_attribute } | Select-Object -First 1
    if($null -eq $match -or [string]::IsNullOrWhiteSpace([string]$match.downloadLink)){ continue }
    $destDir=Join-Path $root ([string]$lane.category)
    New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    $name=($id + "_" + [string]$manifest.target_attribute + ".zip")
    $dest=Join-Path $destDir $name
    try {
      if(-not (Test-Path $dest)){ Invoke-WebRequest -Uri ([string]$match.downloadLink) -Headers $headers -OutFile $dest -UseBasicParsing }
      $file=Get-Item $dest
      if(($receipt.total_bytes + [int64]$file.Length) -gt [int64]$manifest.max_download_bytes){ Remove-Item $dest -Force; $receipt.skipped += [ordered]@{ asset_id=$id; reason="batch_byte_cap" }; continue }
      $hash=(Get-FileHash $dest -Algorithm SHA256).Hash.ToLowerInvariant()
      $receipt.files += [ordered]@{ asset_id=$id; category=[string]$lane.category; query=[string]$lane.q; source_page=("https://ambientcg.com/view?id="+$id); source_url=[string]$match.downloadLink; file=$dest; size=[int64]$file.Length; sha256=$hash; state="STAGED" }
      $receipt.total_bytes += [int64]$file.Length
      $taken++
    } catch { $receipt.skipped += [ordered]@{ asset_id=$id; reason="download_failed"; detail=$_.Exception.Message } }
  }
}
$receiptPath=Join-Path $root ("receipt_"+$manifest.batch_id+".json")
$receipt | ConvertTo-Json -Depth 10 | Set-Content -Path $receiptPath -Encoding UTF8
Write-Host ("AMBIENTCG_WAREHOUSE_STAGE_PASS files="+$receipt.files.Count+" skipped="+$receipt.skipped.Count+" bytes="+$receipt.total_bytes+" receipt="+$receiptPath)
