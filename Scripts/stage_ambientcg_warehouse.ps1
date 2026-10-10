param(
  [string]$ManifestPath = "Data/WarehouseAmbientCGAcquisitionBatchV1.json",
  [switch]$Refresh
)
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "warehouse_network.ps1")
$manifest = Get-Content $ManifestPath -Raw | ConvertFrom-Json
$root = [string]$manifest.staging_root
New-Item -ItemType Directory -Path $root -Force | Out-Null
$receiptPath=Join-Path $root ("receipt_"+$manifest.batch_id+".json")
if (-not $Refresh -and (Test-WarehouseReceiptReusable -ReceiptPath $receiptPath -BatchId ([string]$manifest.batch_id))) { exit 0 }
$headers = @{ "User-Agent" = "ShireJourneyWarehouse/1.0"; "Accept" = "application/json" }
$receipt = [ordered]@{ batch_id=$manifest.batch_id; provider=$manifest.provider; license=$manifest.license; staged_at_utc=[DateTime]::UtcNow.ToString("o"); files=@(); skipped=@(); total_bytes=0 }
# Keep one physical acquisition per CC0 asset ID across all regional search lanes.
# A repeat query may mention the same source, but must not download it again.
$acceptedIds = @{}
foreach($lane in $manifest.search_lanes){
  $q=[uri]::EscapeDataString([string]$lane.q)
  $limit=[int]$lane.limit
  $url="$($manifest.api_base)?type=Material&sort=Popular&limit=$limit&include=downloadData&offset=0&q=$q"
  try { $data=Invoke-WarehouseRestJson -Uri $url -Headers $headers } catch { $receipt.skipped += [ordered]@{ query=$lane.q; reason="api_query_failed"; detail=$_.Exception.Message }; continue }
  $assets=@()
  if($data.foundAssets){ $assets=@($data.foundAssets) } elseif($data.assets){ $assets=@($data.assets) } elseif($data -is [System.Collections.IEnumerable]){ $assets=@($data) }
  $taken=0
  foreach($asset in $assets){
    if($taken -ge 3){ break }
    $id=[string]$asset.assetId
    if([string]::IsNullOrWhiteSpace($id)){ $id=[string]$asset.id }
    if([string]::IsNullOrWhiteSpace($id)){ continue }
    $idKey=$id.ToLowerInvariant()
    if($acceptedIds.ContainsKey($idKey)){
      $receipt.skipped += [ordered]@{ asset_id=$id; category=[string]$lane.category; query=[string]$lane.q; reason="duplicate_in_current_wave" }
      Write-Host ("WAREHOUSE_AMBIENTCG_DUPLICATE_SKIP id=" + $id + " query=" + $lane.q)
      continue
    }
    if([int64]$receipt.total_bytes -ge [int64]$manifest.max_download_bytes){
      $receipt.skipped += [ordered]@{ asset_id=$id; reason="batch_byte_cap_before_download" }
      continue
    }
    $downloads=$null
    try { $downloads=$asset.downloadFolders.default.downloadFiletypeCategories.zip.downloads } catch {}
    if($null -eq $downloads){ continue }
    $match=$downloads | Where-Object { [string]$_.attribute -eq [string]$manifest.target_attribute } | Select-Object -First 1
    if($null -eq $match -or [string]::IsNullOrWhiteSpace([string]$match.downloadLink)){ continue }
    $destDir=Join-Path $root ([string]$lane.category)
    New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    $name=($id + "_" + [string]$manifest.target_attribute + ".zip")
    $dest=Join-Path $destDir $name
    $downloadedThisAttempt=$false
    try {
      if($Refresh -and (Test-Path -LiteralPath $dest -PathType Leaf)){
        Write-Host ("WAREHOUSE_REFRESH_REMOVE provider=AMBIENTCG path=" + $dest)
        Remove-Item -LiteralPath $dest -Force
      }
      if((Test-Path -LiteralPath $dest -PathType Leaf) -and -not (Test-WarehouseZipReadable -Path $dest)){
        Write-Warning ("AMBIENTCG_WAREHOUSE_REPAIR removing corrupt archive asset_id=" + $id + " path=" + $dest)
        Remove-Item -LiteralPath $dest -Force -ErrorAction SilentlyContinue
      }
      if(-not (Test-Path -LiteralPath $dest -PathType Leaf)){
        Invoke-WarehouseDownload -Uri ([string]$match.downloadLink) -Headers $headers -OutFile $dest | Out-Null
        $downloadedThisAttempt=$true
      }
      if(-not (Test-WarehouseZipReadable -Path $dest)){ throw "downloaded ZIP failed structural validation: $dest" }
      $file=Get-Item $dest
      if(($receipt.total_bytes + [int64]$file.Length) -gt [int64]$manifest.max_download_bytes){
        # Never delete a previously valid cached source because this wave is full.
        if($downloadedThisAttempt){ Remove-Item -LiteralPath $dest -Force }
        $receipt.skipped += [ordered]@{ asset_id=$id; reason="batch_byte_cap" }
        continue
      }
      $hash=(Get-FileHash $dest -Algorithm SHA256).Hash.ToLowerInvariant()
      $receipt.files += [ordered]@{ asset_id=$id; category=[string]$lane.category; query=[string]$lane.q; source_page=("https://ambientcg.com/view?id="+$id); source_url=[string]$match.downloadLink; file=$dest; size=[int64]$file.Length; sha256=$hash; state="STAGED" }
      $receipt.total_bytes += [int64]$file.Length
      $acceptedIds[$idKey] = $true
      $taken++
    } catch { $receipt.skipped += [ordered]@{ asset_id=$id; reason="download_failed"; detail=$_.Exception.Message } }
  }
}
$receipt | ConvertTo-Json -Depth 10 | Set-Content -Path $receiptPath -Encoding UTF8
Write-Host ("AMBIENTCG_WAREHOUSE_STAGE_PASS files="+$receipt.files.Count+" skipped="+$receipt.skipped.Count+" bytes="+$receipt.total_bytes+" receipt="+$receiptPath)
