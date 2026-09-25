param(
  [string]$ManifestPath = "Data/P1C01MaterialImportWaveV1.json",
  [string]$WarehouseRoot = "C:\actions-runner\_warehouse\ShireJourney",
  [string]$OutputRoot = "",
  [switch]$Refresh
)
$ErrorActionPreference = "Stop"
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
    foreach ($row in @($receipt.files)) {
      $rows += [pscustomobject]@{
        provider=[string]$receipt.provider
        asset_slug=[string]$row.asset_slug
        asset_id=[string]$row.asset_id
        file=[string]$row.file
        sha256=([string]$row.sha256).ToLowerInvariant()
      }
    }
  }
}

function Select-BaseColor([string[]]$Files) {
  $ranked=@()
  foreach($f in $Files) {
    $e=[IO.Path]::GetExtension($f).ToLowerInvariant()
    if($e -notin @(".png",".tga")){ continue }
    $n=[IO.Path]::GetFileName($f).ToLowerInvariant()
    $score=100
    if($n -match 'basecolor|base_color|albedo|diffuse|diff|color'){ $score=0 }
    elseif($n -match 'preview|thumb|render|normal|rough|ao|metal|height|disp'){ $score=200 }
    $ranked += [pscustomobject]@{file=$f;score=$score;name=$n}
  }
  return ($ranked | Sort-Object score,name | Select-Object -First 1).file
}

$prepared=@(); $pending=@(); $blocked=@()
foreach($item in @($manifest.immediate_open_source_items)) {
  $matches=@($rows | Where-Object { $_.provider -eq [string]$item.provider -and ($_.asset_slug -eq [string]$item.asset_slug -or $_.asset_id -eq [string]$item.asset_slug) })
  if($matches.Count -eq 0) {
    $pending += [ordered]@{id=[string]$item.id;asset_slug=[string]$item.asset_slug;reason="warehouse_source_not_staged_yet"}
    continue
  }
  $files=New-Object 'System.Collections.Generic.List[string]'
  foreach($row in $matches) {
    $p=[string]$row.file
    if([string]::IsNullOrWhiteSpace($p) -or -not (Test-Path -LiteralPath $p -PathType Leaf)){ continue }
    $ext=[IO.Path]::GetExtension($p).ToLowerInvariant()
    if($ext -in @(".exe",".msi",".cmd",".bat",".ps1",".vbs",".js",".scr",".com")) {
      $blocked += [ordered]@{id=[string]$item.id;file=$p;reason="dangerous_payload_extension"}; continue
    }
    if($ext -eq ".bmp") { $blocked += [ordered]@{id=[string]$item.id;file=$p;reason="forbidden_bmp"}; continue }
    if($ext -in @(".png",".tga")) { $files.Add($p); continue }
    if($ext -eq ".zip") {
      $dir=Join-Path $expandedRoot ([string]$item.id)
      if(Test-Path -LiteralPath $dir){ Remove-Item -LiteralPath $dir -Recurse -Force }
      New-Item -ItemType Directory -Path $dir -Force | Out-Null
      try {
        Expand-Archive -LiteralPath $p -DestinationPath $dir -Force
        foreach($x in @(Get-ChildItem -LiteralPath $dir -Recurse -File)) {
          $xe=$x.Extension.ToLowerInvariant()
          if($xe -eq ".bmp"){ $blocked += [ordered]@{id=[string]$item.id;file=$x.FullName;reason="forbidden_bmp_in_archive"} }
          elseif($xe -in @(".png",".tga")){ $files.Add($x.FullName) }
        }
      } catch { $blocked += [ordered]@{id=[string]$item.id;file=$p;reason="archive_extract_failed";detail=$_.Exception.Message} }
    }
  }
  $unique=@($files | Select-Object -Unique)
  $base=Select-BaseColor -Files $unique
  if([string]::IsNullOrWhiteSpace($base)) {
    $pending += [ordered]@{id=[string]$item.id;asset_slug=[string]$item.asset_slug;reason="no_png_tga_basecolor_candidate"}; continue
  }
  $destDir=Join-Path $preparedRoot ([string]$item.id)
  New-Item -ItemType Directory -Path $destDir -Force | Out-Null
  $dest=Join-Path $destDir ("TX_"+[string]$item.id+"_BaseColor"+[IO.Path]::GetExtension($base).ToLowerInvariant())
  Copy-Item -LiteralPath $base -Destination $dest -Force
  $mtl=Join-Path $destDir (([string]$item.material_name)+".mtl")
  @(
    "# Generated P1C01 external material intake.",
    "newmtl "+[string]$item.material_name,
    "Kd 1.0 1.0 1.0",
    "Pr "+[string]$item.roughness,
    "Pm "+[string]$item.metallic,
    "map_Kd "+[IO.Path]::GetFileName($dest),
    ""
  ) | Set-Content -LiteralPath $mtl -Encoding ASCII
  $prepared += [ordered]@{
    id=[string]$item.id; provider=[string]$item.provider; asset_slug=[string]$item.asset_slug;
    material_name=[string]$item.material_name; basecolor_file=$dest;
    basecolor_sha256=(Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash.ToLowerInvariant();
    mtl_file=$mtl; mtl_sha256=(Get-FileHash -LiteralPath $mtl -Algorithm SHA256).Hash.ToLowerInvariant();
    state="INTAKE_QC_PREPARED"
  }
}
$report=[ordered]@{
  schema_version=1; wave_id=[string]$manifest.wave_id; generated_at_utc=[DateTime]::UtcNow.ToString("o");
  prepared=$prepared; pending_source=$pending; blocked_technical=$blocked;
  rule="Missing warehouse candidates are pending, not a failure. Dangerous/corrupt/BMP payloads remain blocking."
}
$receiptPath=Join-Path $OutputRoot "p1c01_material_intake_receipt.json"
$report | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $receiptPath -Encoding UTF8
if($blocked.Count -gt 0){ Write-Host ("P1C01_MATERIAL_INTAKE_BLOCKED prepared="+$prepared.Count+" pending="+$pending.Count+" blocked="+$blocked.Count+" receipt="+$receiptPath); exit 2 }
Write-Host ("P1C01_MATERIAL_INTAKE_PASS prepared="+$prepared.Count+" pending="+$pending.Count+" blocked=0 receipt="+$receiptPath)
