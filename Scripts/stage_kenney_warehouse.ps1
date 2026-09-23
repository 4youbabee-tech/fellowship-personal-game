param(
  [string]$ManifestPath = "Data/WarehouseKenneyAcquisitionBatchV1.json",
  [switch]$Refresh
)
$ErrorActionPreference="Stop"
. (Join-Path $PSScriptRoot "warehouse_network.ps1")
$manifest=Get-Content $ManifestPath -Raw | ConvertFrom-Json
$root=[string]$manifest.staging_root
New-Item -ItemType Directory -Path $root -Force | Out-Null
$receiptPath=Join-Path $root ("receipt_"+$manifest.batch_id+".json")
if (-not $Refresh -and (Test-WarehouseReceiptReusable -ReceiptPath $receiptPath -BatchId ([string]$manifest.batch_id))) { exit 0 }
$headers=@{ "User-Agent"="ShireJourneyWarehouse/1.0" }
$receipt=[ordered]@{ batch_id=$manifest.batch_id; provider=$manifest.provider; license=$manifest.license; staged_at_utc=[DateTime]::UtcNow.ToString("o"); files=@(); unresolved=@() }
foreach($pack in $manifest.pack_pages){
  try { $resp=Invoke-WarehousePage -Uri ([string]$pack.url) -Headers $headers } catch { $receipt.unresolved += [ordered]@{ asset_id=$pack.id; source_page=$pack.url; reason="page_fetch_failed"; detail=$_.Exception.Message }; continue }
  $hrefs=@()
  foreach($link in $resp.Links){ if($null -ne $link.href -and -not [string]::IsNullOrWhiteSpace([string]$link.href)){ $hrefs += [string]$link.href } }
  $direct=@()
  foreach($href in ($hrefs | Select-Object -Unique)){
    try { $uri=[Uri]::new([Uri]$pack.url,$href) } catch { continue }
    $u=$uri.AbsoluteUri
    if($u.ToLowerInvariant().EndsWith(".zip")){ $direct += $u }
  }
  if($direct.Count -eq 0){ $receipt.unresolved += [ordered]@{ asset_id=$pack.id; source_page=$pack.url; reason="no_public_zip_discovered" }; continue }
  $destDir=Join-Path $root ([string]$pack.category)
  New-Item -ItemType Directory -Path $destDir -Force | Out-Null
  foreach($url in ($direct | Select-Object -Unique)){
    try {
      $name=[IO.Path]::GetFileName(([Uri]$url).LocalPath)
      if([string]::IsNullOrWhiteSpace($name)){ continue }
      $dest=Join-Path $destDir $name
      if(-not (Test-Path $dest)){ Invoke-WarehouseDownload -Uri $url -Headers $headers -OutFile $dest | Out-Null }
      $file=Get-Item $dest
      $hash=(Get-FileHash $dest -Algorithm SHA256).Hash.ToLowerInvariant()
      $receipt.files += [ordered]@{ asset_id=$pack.id; category=$pack.category; source_page=$pack.url; source_url=$url; file=$dest; size=[int64]$file.Length; sha256=$hash; state="STAGED" }
    } catch { $receipt.unresolved += [ordered]@{ asset_id=$pack.id; source_page=$pack.url; source_url=$url; reason="download_failed"; detail=$_.Exception.Message } }
  }
}
$receipt | ConvertTo-Json -Depth 8 | Set-Content -Path $receiptPath -Encoding UTF8
Write-Host ("KENNEY_WAREHOUSE_STAGE_PASS files="+$receipt.files.Count+" unresolved="+$receipt.unresolved.Count+" receipt="+$receiptPath)
