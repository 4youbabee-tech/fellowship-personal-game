param(
  [string]$ManifestPath = "Data/P1C01AudioFoleyAmbiencePrepV1.json",
  [string]$WarehouseRoot = "C:\actions-runner\_warehouse\ShireJourney",
  [string]$OutputRoot = ""
)
Set-StrictMode -Version Latest
$ErrorActionPreference="Stop"
$ProjectRoot=Split-Path $PSScriptRoot -Parent
if([string]::IsNullOrWhiteSpace($OutputRoot)){ $OutputRoot=Join-Path $ProjectRoot "Saved\AudioIntake\P1C01" }
if(-not (Test-Path -LiteralPath $ManifestPath)){ $c=Join-Path $ProjectRoot $ManifestPath; if(Test-Path -LiteralPath $c){$ManifestPath=$c} }
if(-not (Test-Path -LiteralPath $ManifestPath)){ throw "Audio intake manifest missing: $ManifestPath" }
$manifest=Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null
$rows=@()
if(Test-Path -LiteralPath $WarehouseRoot){
  foreach($rf in @(Get-ChildItem -LiteralPath $WarehouseRoot -Recurse -File -Filter "receipt_*.json")){
    try{$r=Get-Content -LiteralPath $rf.FullName -Raw | ConvertFrom-Json}catch{continue}
    foreach($x in @($r.files)){ $rows += [pscustomobject]@{provider=[string]$r.provider;asset_id=[string]$x.asset_id;asset_slug=[string]$x.asset_slug;file=[string]$x.file;sha256=([string]$x.sha256).ToLowerInvariant()} }
  }
}
$prepared=@();$pending=@();$blocked=@()
foreach($item in @($manifest.items)){
  $matches=@($rows|Where-Object{$_.provider -eq [string]$item.provider -and ($_.asset_id -eq [string]$item.id -or $_.asset_slug -eq [string]$item.id)})
  if($matches.Count -eq 0){$pending += [ordered]@{id=[string]$item.id;reason="warehouse_source_not_staged_yet"};continue}
  $wav=0;$sourceOther=0
  foreach($row in $matches){
    if(-not (Test-Path -LiteralPath $row.file -PathType Leaf)){$blocked += [ordered]@{id=[string]$item.id;file=$row.file;reason="receipt_file_missing"};continue}
    $actual=(Get-FileHash -LiteralPath $row.file -Algorithm SHA256).Hash.ToLowerInvariant()
    if([string]::IsNullOrWhiteSpace($row.sha256) -or $actual -ne $row.sha256){$blocked += [ordered]@{id=[string]$item.id;file=$row.file;reason="receipt_sha256_mismatch"};continue}
    $ext=[IO.Path]::GetExtension($row.file).ToLowerInvariant()
    if($ext -eq ".wav"){$wav++} elseif($ext -in @(".ogg",".mp3",".flac",".zip")){$sourceOther++}
  }
  $prepared += [ordered]@{
    id=[string]$item.id; role=[string]$item.role; wav_master_count=$wav; staged_source_count=$sourceOther;
    state=if($wav -gt 0){"INTAKE_QC_PREPARED"}else{"STAGED_NEEDS_WAV_MASTER"};
    ready_for_import=$false; qc_pending=@("audition","trim/fade","loudness","loop seam where applicable","attenuation/concurrency","memory/decompression")
  }
}
$report=[ordered]@{schema_version=1;batch_id=[string]$manifest.batch_id;prepared=$prepared;pending=$pending;blocked=$blocked;rule="WAV master required before UE import."}
$receipt=Join-Path $OutputRoot "p1c01_audio_intake_receipt.json"
$report|ConvertTo-Json -Depth 10|Set-Content -LiteralPath $receipt -Encoding UTF8
if($blocked.Count -gt 0){Write-Host ("P1C01_AUDIO_INTAKE_BLOCKED prepared="+$prepared.Count+" pending="+$pending.Count+" blocked="+$blocked.Count);exit 2}
Write-Host ("P1C01_AUDIO_INTAKE_PASS prepared="+$prepared.Count+" pending="+$pending.Count+" blocked=0 receipt="+$receipt)
