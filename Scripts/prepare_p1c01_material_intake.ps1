param(
  [string]$ManifestPath = "Data/P1C01MaterialImportWaveV1.json",
  [string]$WarehouseRoot = "C:\actions-runner\_warehouse\ShireJourney",
  [string]$OutputRoot = "",
  [switch]$Refresh
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.IO.Compression.FileSystem

function Get-OptionalPropertyValue {
  param([object]$Object,[string]$Name,[object]$Default=$null)
  if($null -eq $Object){ return $Default }
  $p=$Object.PSObject.Properties[$Name]
  if($null -eq $p){ return $Default }
  return $p.Value
}

function Test-DangerousExtension([string]$Extension) {
  return ([string]$Extension).ToLowerInvariant() -in @(".exe",".msi",".cmd",".bat",".ps1",".vbs",".js",".scr",".com")
}

function Test-ZipSafe([string]$ArchivePath) {
  $archive=[IO.Compression.ZipFile]::OpenRead($ArchivePath)
  try {
    $count=0
    $total=[int64]0
    foreach($entry in $archive.Entries){
      $count++
      $name=$entry.FullName.Replace([char]92,'/')
      $parts=@($name.Split('/') | Where-Object { $_ -ne '' })
      if($count -gt 20000 -or $entry.Length -gt 536870912 -or ($total + $entry.Length) -gt 2147483648){ throw "archive_budget_exceeded" }
      if($name.StartsWith('/') -or $name -match '^[A-Za-z]:' -or @($parts | Where-Object { $_ -eq '..' }).Count -gt 0){ throw "archive_path_unsafe" }
      $ext=[IO.Path]::GetExtension($name).ToLowerInvariant()
      if(Test-DangerousExtension $ext -or $ext -eq ".bmp"){ throw "archive_forbidden_extension:$ext" }
      $total += [int64]$entry.Length
    }
  } finally { $archive.Dispose() }
}

$ProjectRoot = Split-Path $PSScriptRoot -Parent
if ([string]::IsNullOrWhiteSpace($OutputRoot)) { $OutputRoot = Join-Path $ProjectRoot "Saved\MaterialIntake\P1C01" }
if (-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)) {
  $candidate = Join-Path $ProjectRoot $ManifestPath
  if (Test-Path -LiteralPath $candidate -PathType Leaf) { $ManifestPath = $candidate }
}
if (-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)) { throw "Material intake manifest missing: $ManifestPath" }
$manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
if ($Refresh -and (Test-Path -LiteralPath $OutputRoot)) { Remove-Item -LiteralPath $OutputRoot -Recurse -Force }
New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null
$preparedRoot = Join-Path $OutputRoot "Prepared"
$expandedRoot = Join-Path $OutputRoot "Expanded"
New-Item -ItemType Directory -Path $preparedRoot -Force | Out-Null
New-Item -ItemType Directory -Path $expandedRoot -Force | Out-Null

$rows = @()
if (Test-Path -LiteralPath $WarehouseRoot -PathType Container) {
  foreach ($receiptFile in @(Get-ChildItem -LiteralPath $WarehouseRoot -Recurse -File -Filter "receipt_*.json")) {
    try { $receipt = Get-Content -LiteralPath $receiptFile.FullName -Raw | ConvertFrom-Json } catch { continue }
    $provider=[string](Get-OptionalPropertyValue $receipt "provider" "")
    $license=[string](Get-OptionalPropertyValue $receipt "license" "")
    foreach ($row in @(Get-OptionalPropertyValue $receipt "files" @())) {
      $payload=[string](Get-OptionalPropertyValue $row "file" "")
      $declared=([string](Get-OptionalPropertyValue $row "sha256" "")).ToLowerInvariant()
      if([string]::IsNullOrWhiteSpace($payload)){
        $payload=[string](Get-OptionalPropertyValue $row "archive" "")
        $declared=([string](Get-OptionalPropertyValue $row "archive_sha256" "")).ToLowerInvariant()
      }
      if([string]::IsNullOrWhiteSpace($payload)){ continue }
      $rows += [pscustomobject]@{
        provider=$provider
        license=$license
        asset_slug=[string](Get-OptionalPropertyValue $row "asset_slug" "")
        asset_id=[string](Get-OptionalPropertyValue $row "asset_id" "")
        file=$payload
        sha256=$declared
        source_page=[string](Get-OptionalPropertyValue $row "source_page" "")
        source_url=[string](Get-OptionalPropertyValue $row "source_url" "")
        receipt=$receiptFile.FullName
      }
    }
  }
}

function Test-ExplicitBaseColorName([string]$FilePath) {
  $name=[IO.Path]::GetFileNameWithoutExtension($FilePath).ToLowerInvariant()

  # Never let support maps silently become visible color. This is deliberately
  # fail-closed for the low-spec P1C01 wave: ambiguous names stay pending.
  if($name -match '(^|[_-])(normal|nor|nrm|rough|roughness|ao|ambientocclusion|occlusion|metal|metallic|height|disp|displacement|arm|orm)([_-]|$)'){
    return $false
  }
  if($name -match 'preview|thumbnail|thumb|render'){
    return $false
  }

  return (
    $name -match 'basecolor|base_color|albedo|diffuse' -or
    $name -match '(^|[_-])diff([_-]|$)' -or
    $name -match '(^|[_-])colou?r([_-]|$)'
  )
}

function Select-BaseColor([string[]]$Files) {
  $ranked=@()
  foreach($f in $Files) {
    $e=[IO.Path]::GetExtension($f).ToLowerInvariant()
    if($e -notin @(".png",".tga")){ continue }
    if(-not (Test-ExplicitBaseColorName -FilePath $f)){ continue }

    $n=[IO.Path]::GetFileName($f).ToLowerInvariant()
    $score=30
    if($n -match 'basecolor|base_color'){ $score=0 }
    elseif($n -match 'albedo'){ $score=5 }
    elseif($n -match 'diffuse'){ $score=10 }
    elseif($n -match '(^|[_-])diff([_-]|$)'){ $score=15 }
    elseif($n -match '(^|[_-])colou?r([_-]|$)'){ $score=20 }

    $ranked += [pscustomobject]@{file=$f;score=$score;name=$n}
  }
  $selected=$ranked | Sort-Object score,name | Select-Object -First 1
  if($null -eq $selected){ return $null }
  return [string]$selected.file
}

$prepared=@()
$pending=@()
$manualQueue=@()
foreach($item in @($manifest.immediate_open_source_items)) {
  $matches=@($rows | Where-Object {
    $_.provider -eq [string]$item.provider -and
    ($_.asset_slug -eq [string]$item.asset_slug -or $_.asset_id -eq [string]$item.asset_slug)
  })
  if($matches.Count -eq 0) {
    $pending += [ordered]@{id=[string]$item.id;asset_slug=[string]$item.asset_slug;reason="warehouse_source_not_staged_yet"}
    continue
  }

  $files=New-Object 'System.Collections.Generic.List[string]'
  $provenanceByFile=@{}
  foreach($row in $matches) {
    $p=[string]$row.file
    if([string]::IsNullOrWhiteSpace($p) -or -not (Test-Path -LiteralPath $p -PathType Leaf)){
      $manualQueue += [ordered]@{id=[string]$item.id;asset_slug=[string]$item.asset_slug;file=$p;reason="receipt_file_missing"}
      continue
    }
    $actual=(Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant()
    if([string]::IsNullOrWhiteSpace([string]$row.sha256) -or $actual -ne [string]$row.sha256){
      $manualQueue += [ordered]@{id=[string]$item.id;asset_slug=[string]$item.asset_slug;file=$p;reason="receipt_sha256_mismatch";expected=[string]$row.sha256;actual=$actual}
      continue
    }
    $ext=[IO.Path]::GetExtension($p).ToLowerInvariant()
    if(Test-DangerousExtension $ext) {
      $manualQueue += [ordered]@{id=[string]$item.id;file=$p;reason="dangerous_payload_extension"}; continue
    }
    if($ext -eq ".bmp") {
      $manualQueue += [ordered]@{id=[string]$item.id;file=$p;reason="forbidden_bmp"}; continue
    }
    if($ext -in @(".png",".tga")) {
      $files.Add($p)
      $provenanceByFile[[IO.Path]::GetFullPath($p)]=$row
      continue
    }
    if($ext -eq ".zip") {
      $dir=Join-Path $expandedRoot (([string]$item.id)+"_"+$actual.Substring(0,12))
      if(Test-Path -LiteralPath $dir){ Remove-Item -LiteralPath $dir -Recurse -Force }
      New-Item -ItemType Directory -Path $dir -Force | Out-Null
      try {
        Test-ZipSafe -ArchivePath $p
        Expand-Archive -LiteralPath $p -DestinationPath $dir -Force
        foreach($x in @(Get-ChildItem -LiteralPath $dir -Recurse -File)) {
          $xe=$x.Extension.ToLowerInvariant()
          if($xe -eq ".bmp" -or (Test-DangerousExtension $xe)){
            $manualQueue += [ordered]@{id=[string]$item.id;file=$x.FullName;reason="forbidden_archive_payload"}
          }
          elseif($xe -in @(".png",".tga")){
            $files.Add($x.FullName)
            $provenanceByFile[[IO.Path]::GetFullPath($x.FullName)]=$row
          }
        }
      } catch {
        $manualQueue += [ordered]@{id=[string]$item.id;file=$p;reason="archive_scan_or_extract_failed";detail=$_.Exception.Message}
      }
    }
  }

  $unique=@($files | Select-Object -Unique)
  $base=Select-BaseColor -Files $unique
  if([string]::IsNullOrWhiteSpace($base)) {
    $pending += [ordered]@{
      id=[string]$item.id
      asset_slug=[string]$item.asset_slug
      reason="no_explicit_albedo_png_tga_candidate"
      candidate_count=$unique.Count
    }
    continue
  }

  $baseKey=[IO.Path]::GetFullPath($base)
  $baseProvenance=$null
  if($provenanceByFile.ContainsKey($baseKey)){ $baseProvenance=$provenanceByFile[$baseKey] }
  if($null -eq $baseProvenance){
    $manualQueue += [ordered]@{
      id=[string]$item.id
      asset_slug=[string]$item.asset_slug
      file=$base
      reason="selected_basecolor_provenance_missing"
    }
    continue
  }

  $destDir=Join-Path $preparedRoot ([string]$item.id)
  if(Test-Path -LiteralPath $destDir){ Remove-Item -LiteralPath $destDir -Recurse -Force }
  New-Item -ItemType Directory -Path $destDir -Force | Out-Null
  $dest=Join-Path $destDir ("TX_"+[string]$item.id+"_BaseColor"+[IO.Path]::GetExtension($base).ToLowerInvariant())
  Copy-Item -LiteralPath $base -Destination $dest -Force

  $mtl=Join-Path $destDir (([string]$item.material_name)+".mtl")
  $specular = 0.10
  if ($null -ne $item.specular) { $specular = [double]$item.specular }
  $ks = [Math]::Max(0.005, [Math]::Min(0.1625, $specular / 4.0))
  $ksText = $ks.ToString("0.0000", [Globalization.CultureInfo]::InvariantCulture)
  @(
    "# Generated P1C01 external material intake.",
    "newmtl "+[string]$item.material_name,
    "Kd 1.0 1.0 1.0",
    "Pr "+([double]$item.roughness).ToString("0.0000", [Globalization.CultureInfo]::InvariantCulture),
    "Pm "+([double]$item.metallic).ToString("0.0000", [Globalization.CultureInfo]::InvariantCulture),
    "Ks $ksText $ksText $ksText",
    "map_Kd "+[IO.Path]::GetFileName($dest),
    ""
  ) | Set-Content -LiteralPath $mtl -Encoding ASCII

  $prepared += [ordered]@{
    id=[string]$item.id
    provider=[string]$item.provider
    license=[string]$baseProvenance.license
    asset_slug=[string]$item.asset_slug
    source_page=[string]$baseProvenance.source_page
    source_url=[string]$baseProvenance.source_url
    selected_source_filename=[IO.Path]::GetFileName($base)
    selected_source_kind="EXPLICIT_ALBEDO"
    material_name=[string]$item.material_name
    basecolor_file=$dest
    roughness=[double]$item.roughness
    metallic=[double]$item.metallic
    specular=$specular
    basecolor_sha256=(Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash.ToLowerInvariant()
    mtl_file=$mtl
    mtl_sha256=(Get-FileHash -LiteralPath $mtl -Algorithm SHA256).Hash.ToLowerInvariant()
    state="INTAKE_QC_PREPARED"
  }
}

$report=[ordered]@{
  schema_version=3
  wave_id=[string]$manifest.wave_id
  generated_at_utc=[DateTime]::UtcNow.ToString("o")
  requested_count=@($manifest.immediate_open_source_items).Count
  prepared_count=$prepared.Count
  pending_count=$pending.Count
  manual_queue_count=$manualQueue.Count
  prepared=$prepared
  pending_source=$pending
  manual_queue=$manualQueue
  rule="Only receipt-hash-verified PNG/TGA files with explicit base-color/albedo/diffuse/color semantics are prepared. Normal/AO/roughness/metal/height/support maps and ambiguous names are rejected from visible color intake; selected-file provenance is retained."
}
$receiptPath=Join-Path $OutputRoot "p1c01_material_intake_receipt.json"
$report | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $receiptPath -Encoding UTF8

if($prepared.Count -eq 0 -and $manualQueue.Count -gt 0){
  Write-Host ("P1C01_MATERIAL_INTAKE_BLOCKED prepared=0 pending="+$pending.Count+" manual="+$manualQueue.Count+" receipt="+$receiptPath)
  exit 2
}
if($manualQueue.Count -gt 0){
  Write-Host ("P1C01_MATERIAL_INTAKE_PASS_WITH_MANUAL_QUEUE prepared="+$prepared.Count+" pending="+$pending.Count+" manual="+$manualQueue.Count+" receipt="+$receiptPath)
  foreach($entry in $manualQueue){ Write-Host ("P1C01_MATERIAL_MANUAL_QUEUE "+($entry|ConvertTo-Json -Compress -Depth 6)) }
  exit 0
}
Write-Host ("P1C01_MATERIAL_INTAKE_PASS prepared="+$prepared.Count+" pending="+$pending.Count+" manual=0 receipt="+$receiptPath)
exit 0
