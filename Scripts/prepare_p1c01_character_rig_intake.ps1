param(
  [string]$ManifestPath = "Data/P1C01CharacterRigAnimationPrepV1.json",
  [string]$WarehouseRoot = "D:\actions-runner\_warehouse\ShireJourney",
  [string]$OutputRoot = ""
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-OptionalPropertyValue {
  param([object]$Object,[string]$Name,[object]$Default=$null)
  if($null -eq $Object){ return $Default }
  $p=$Object.PSObject.Properties[$Name]
  if($null -eq $p){ return $Default }
  return $p.Value
}

Add-Type -AssemblyName System.IO.Compression.FileSystem
$ProjectRoot = Split-Path $PSScriptRoot -Parent
if ([string]::IsNullOrWhiteSpace($OutputRoot)) { $OutputRoot = Join-Path $ProjectRoot "Saved\CharacterIntake\P1C01" }
if (-not (Test-Path -LiteralPath $ManifestPath)) {
  $candidate = Join-Path $ProjectRoot $ManifestPath
  if (Test-Path -LiteralPath $candidate) { $ManifestPath = $candidate }
}
if (-not (Test-Path -LiteralPath $ManifestPath)) { throw "Character intake manifest missing: $ManifestPath" }
$manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null

$dangerous=@(".exe",".msi",".cmd",".bat",".ps1",".vbs",".js",".scr",".com")
$receipts=@()
if (Test-Path -LiteralPath $WarehouseRoot) {
  foreach($rf in @(Get-ChildItem -LiteralPath $WarehouseRoot -Recurse -File -Filter "receipt_*.json")) {
    try { $r=Get-Content -LiteralPath $rf.FullName -Raw | ConvertFrom-Json } catch { continue }
    foreach($row in @(Get-OptionalPropertyValue $r "files" @())) {
      $payloadPath=[string](Get-OptionalPropertyValue $row "file" "")
      $payloadHash=([string](Get-OptionalPropertyValue $row "sha256" "")).ToLowerInvariant()
      if([string]::IsNullOrWhiteSpace($payloadPath)){
        $payloadPath=[string](Get-OptionalPropertyValue $row "archive" "")
        $payloadHash=([string](Get-OptionalPropertyValue $row "archive_sha256" "")).ToLowerInvariant()
      }
      if([string]::IsNullOrWhiteSpace($payloadPath)){ continue }
      $receipts += [pscustomobject]@{
        provider=[string](Get-OptionalPropertyValue $r "provider" "")
        asset_id=[string](Get-OptionalPropertyValue $row "asset_id" "")
        asset_slug=[string](Get-OptionalPropertyValue $row "asset_slug" "")
        file=$payloadPath
        sha256=$payloadHash
        receipt=$rf.FullName
      }
    }
  }
}

$prepared=@(); $pending=@(); $blocked=@()
foreach($item in @($manifest.external_candidates)) {
  if ([string]$item.state -ne "AUTHORIZED_FOR_STAGING") {
    $pending += [ordered]@{provider=[string]$item.provider;id=[string]$item.id;reason="license_capture_required_before_staging"}
    continue
  }
  $rows=@($receipts | Where-Object { $_.provider -eq [string]$item.provider -and ($_.asset_id -eq [string]$item.id -or $_.asset_slug -eq [string]$item.id) })
  if($rows.Count -eq 0){ $pending += [ordered]@{provider=[string]$item.provider;id=[string]$item.id;reason="warehouse_source_not_staged_yet"}; continue }

  $fbx=0; $pngtga=0; $obj=0; $verifiedArchives=0
  foreach($row in $rows){
    if(-not (Test-Path -LiteralPath $row.file -PathType Leaf)){ $blocked += [ordered]@{id=[string]$item.id;file=$row.file;reason="receipt_file_missing"}; continue }
    $actual=(Get-FileHash -LiteralPath $row.file -Algorithm SHA256).Hash.ToLowerInvariant()
    if([string]::IsNullOrWhiteSpace($row.sha256) -or $actual -ne $row.sha256){ $blocked += [ordered]@{id=[string]$item.id;file=$row.file;reason="receipt_sha256_mismatch"}; continue }
    $ext=[IO.Path]::GetExtension($row.file).ToLowerInvariant()
    if($dangerous -contains $ext){ $blocked += [ordered]@{id=[string]$item.id;file=$row.file;reason="dangerous_payload_extension"}; continue }
    if($ext -eq ".bmp"){ $blocked += [ordered]@{id=[string]$item.id;file=$row.file;reason="forbidden_bmp"}; continue }
    if($ext -eq ".zip"){
      $verifiedArchives++
      $destination=Join-Path $OutputRoot ("Expanded_"+([string]$item.id -replace '[^A-Za-z0-9_.-]','_')+"_"+$actual.Substring(0,12))
      try {
                $archive=[IO.Compression.ZipFile]::OpenRead($row.file)
        try {
          $totalBytes=[int64]0; $entryCount=0
          foreach($entry in $archive.Entries){
            $entryCount++
            $entryName=$entry.FullName.Replace([char]92,'/')
            $parts=@($entryName.Split('/') | Where-Object { $_ -ne '' })
            if($entryCount -gt 20000 -or $entry.Length -gt 536870912 -or $totalBytes + $entry.Length -gt 2147483648){
              throw "archive_budget_exceeded"
            }
            if($entryName.StartsWith('/') -or $entryName -match '^[A-Za-z]:' -or @($parts | Where-Object { $_ -eq '..' }).Count -gt 0){
              throw "archive_path_unsafe"
            }
            $totalBytes += $entry.Length
            $inside=[IO.Path]::GetExtension($entryName).ToLowerInvariant()
            if($dangerous -contains $inside -or $inside -eq ".bmp"){ throw "archive_forbidden_extension" }
          }
        } finally { $archive.Dispose() }
        if(Test-Path -LiteralPath $destination){ Remove-Item -LiteralPath $destination -Recurse -Force }
        New-Item -ItemType Directory -Path $destination -Force | Out-Null
        Expand-Archive -LiteralPath $row.file -DestinationPath $destination -Force
        foreach($extracted in @(Get-ChildItem -LiteralPath $destination -Recurse -File)){
          $inside=$extracted.Extension.ToLowerInvariant()
          if($inside -eq ".fbx"){ $fbx++ }
          elseif($inside -in @(".png",".tga")){ $pngtga++ }
          elseif($inside -eq ".obj"){ $obj++ }
        }
      } catch {
        $blocked += [ordered]@{id=[string]$item.id;file=$row.file;reason="archive_scan_or_extract_failed";detail=$_.Exception.Message}
        if(Test-Path -LiteralPath $destination){ Remove-Item -LiteralPath $destination -Recurse -Force }
      }
    }
    elseif($ext -in @(".7z",".rar")){ $pending += [ordered]@{id=[string]$item.id;file=$row.file;reason="archive_requires_approved_extractor"} }
    elseif($ext -eq ".fbx"){ $fbx++ }
    elseif($ext -in @(".png",".tga")){ $pngtga++ }
    elseif($ext -eq ".obj"){ $obj++ }
  }
  $prepared += [ordered]@{
    provider=[string]$item.provider; id=[string]$item.id;
    verified_archive_count=$verifiedArchives; fbx_count=$fbx; texture_png_tga_count=$pngtga; obj_support_count=$obj;
    state=if($fbx -gt 0){"INTAKE_QC_PREPARED"}else{"STAGED_NEEDS_FBX"};
    ready_for_import=$false;
    qc_pending=@("skeleton","skin weights","retarget","deformation","animation coverage","materials","LOD/cull","equipment sockets")
  }
}

$projectOwnedRoot=Join-Path $ProjectRoot "SourceAssets\Production\Characters"
$fallbackCount=0
if(Test-Path -LiteralPath $projectOwnedRoot){ $fallbackCount=@(Get-ChildItem -LiteralPath $projectOwnedRoot -Recurse -File).Count }

$report=[ordered]@{
  schema_version=1; batch_id=[string]$manifest.batch_id; generated_at_utc=[DateTime]::UtcNow.ToString("o");
  project_owned_fallback_file_count=$fallbackCount;
  prepared_count=$prepared.Count; pending_count=$pending.Count; blocked_count=$blocked.Count;
  prepared=$prepared; pending=$pending; blocked=$blocked;
  rule="No final animated-character promotion without FBX + provenance + skeleton/skin/retarget/deformation QC."
}
$receipt=Join-Path $OutputRoot "p1c01_character_rig_intake_receipt.json"
$report | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $receipt -Encoding UTF8
if($blocked.Count -gt 0){ Write-Host ("P1C01_CHARACTER_INTAKE_BLOCKED prepared="+$prepared.Count+" pending="+$pending.Count+" blocked="+$blocked.Count); exit 2 }
Write-Host ("P1C01_CHARACTER_INTAKE_PASS prepared="+$prepared.Count+" pending="+$pending.Count+" blocked=0 receipt="+$receipt)
