param(
  [string]$ManifestPath = "Data/P1C01ArchitectureInteriorPropMegabatchV1.json",
  [string]$WarehouseRoot = "C:\actions-runner\_warehouse\ShireJourney",
  [string]$OutputRoot = "",
  [switch]$Refresh
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path $PSScriptRoot -Parent
if ([string]::IsNullOrWhiteSpace($OutputRoot)) {
  $OutputRoot = Join-Path $ProjectRoot "Saved\ArchitectureIntake\P1C01"
}
if (-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)) {
  $candidate = Join-Path $ProjectRoot $ManifestPath
  if (Test-Path -LiteralPath $candidate -PathType Leaf) { $ManifestPath = $candidate }
}
if (-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)) {
  throw "Architecture intake manifest missing: $ManifestPath"
}

$manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
if ($Refresh -and (Test-Path -LiteralPath $OutputRoot)) {
  Remove-Item -LiteralPath $OutputRoot -Recurse -Force
}
New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null
$ExpandedRoot = Join-Path $OutputRoot "Expanded"
New-Item -ItemType Directory -Path $ExpandedRoot -Force | Out-Null

$receiptRows = @()
if (Test-Path -LiteralPath $WarehouseRoot -PathType Container) {
  foreach ($receiptFile in @(Get-ChildItem -LiteralPath $WarehouseRoot -Recurse -File -Filter "receipt_*.json")) {
    try { $receipt = Get-Content -LiteralPath $receiptFile.FullName -Raw | ConvertFrom-Json } catch { continue }
    foreach ($row in @($receipt.files)) {
      $receiptRows += [pscustomobject]@{
        provider = [string]$receipt.provider
        asset_slug = [string]$row.asset_slug
        asset_id = [string]$row.asset_id
        file = [string]$row.file
        sha256 = ([string]$row.sha256).ToLowerInvariant()
        receipt_file = $receiptFile.FullName
      }
    }
  }
}

$dangerous = @(".exe",".msi",".cmd",".bat",".ps1",".vbs",".js",".scr",".com")
$meshExt = @(".fbx",".obj")
$textureExt = @(".png",".tga")
$prepared = @()
$pending = @()
$blocked = @()

foreach ($item in @($manifest.external_items)) {
  $provider = [string]$item.provider
  $id = [string]$item.id
  $matches = @($receiptRows | Where-Object {
    $_.provider -eq $provider -and ($_.asset_slug -eq $id -or $_.asset_id -eq $id)
  })

  if ($matches.Count -eq 0) {
    $pending += [ordered]@{ id=$id; provider=$provider; reason="warehouse_source_not_staged_yet" }
    continue
  }

  $verifiedPayloads = @()
  foreach ($row in $matches) {
    if ([string]::IsNullOrWhiteSpace($row.file) -or -not (Test-Path -LiteralPath $row.file -PathType Leaf)) {
      $blocked += [ordered]@{ id=$id; provider=$provider; file=$row.file; reason="receipt_file_missing" }
      continue
    }

    $actualHash = (Get-FileHash -LiteralPath $row.file -Algorithm SHA256).Hash.ToLowerInvariant()
    if ([string]::IsNullOrWhiteSpace($row.sha256) -or $actualHash -ne $row.sha256) {
      $blocked += [ordered]@{
        id=$id; provider=$provider; file=$row.file; reason="receipt_sha256_mismatch";
        expected=$row.sha256; actual=$actualHash
      }
      continue
    }

    $verifiedPayloads += [ordered]@{
      file=$row.file; sha256=$actualHash; receipt_file=$row.receipt_file
    }
  }

  if ($verifiedPayloads.Count -eq 0) { continue }

  $itemRoot = Join-Path $ExpandedRoot $id
  if (Test-Path -LiteralPath $itemRoot) { Remove-Item -LiteralPath $itemRoot -Recurse -Force }
  New-Item -ItemType Directory -Path $itemRoot -Force | Out-Null

  $scanFiles = New-Object 'System.Collections.Generic.List[string]'
  foreach ($payload in $verifiedPayloads) {
    $p = [string]$payload.file
    $ext = [IO.Path]::GetExtension($p).ToLowerInvariant()

    if ($dangerous -contains $ext) {
      $blocked += [ordered]@{ id=$id; provider=$provider; file=$p; reason="dangerous_payload_extension" }
      continue
    }

    if ($ext -eq ".zip") {
      $extractRoot = Join-Path $itemRoot ([IO.Path]::GetFileNameWithoutExtension($p))
      New-Item -ItemType Directory -Path $extractRoot -Force | Out-Null
      try {
        Expand-Archive -LiteralPath $p -DestinationPath $extractRoot -Force
        foreach ($x in @(Get-ChildItem -LiteralPath $extractRoot -Recurse -File)) {
          $scanFiles.Add($x.FullName)
        }
      }
      catch {
        $blocked += [ordered]@{ id=$id; provider=$provider; file=$p; reason="archive_extract_failed"; detail=$_.Exception.Message }
      }
    }
    elseif ($ext -in @(".7z",".rar")) {
      $pending += [ordered]@{ id=$id; provider=$provider; file=$p; reason="archive_requires_external_extractor" }
    }
    else {
      $scanFiles.Add($p)
    }
  }

  $fbx = New-Object 'System.Collections.Generic.List[string]'
  $obj = New-Object 'System.Collections.Generic.List[string]'
  $textures = New-Object 'System.Collections.Generic.List[string]'
  foreach ($file in @($scanFiles | Select-Object -Unique)) {
    $ext = [IO.Path]::GetExtension($file).ToLowerInvariant()
    if ($dangerous -contains $ext) {
      $blocked += [ordered]@{ id=$id; provider=$provider; file=$file; reason="dangerous_extracted_extension" }
      continue
    }
    if ($ext -eq ".bmp") {
      $blocked += [ordered]@{ id=$id; provider=$provider; file=$file; reason="forbidden_bmp" }
      continue
    }
    if ($ext -eq ".fbx") { $fbx.Add($file); continue }
    if ($ext -eq ".obj") { $obj.Add($file); continue }
    if ($textureExt -contains $ext) { $textures.Add($file); continue }
  }

  $finalExchangeReady = $fbx.Count -gt 0
  $technicalState = if ($finalExchangeReady) { "INTAKE_QC_PREPARED" } else { "STAGED_NEEDS_FBX_PREPARATION" }

  $prepared += [ordered]@{
    id=$id
    provider=$provider
    license=[string]$item.license
    source_page=[string]$item.source_page
    state=$technicalState
    verified_payload_count=$verifiedPayloads.Count
    fbx_count=$fbx.Count
    obj_support_count=$obj.Count
    texture_png_tga_count=$textures.Count
    fbx_files=@($fbx)
    obj_support_files=@($obj)
    texture_files=@($textures)
    class_qc_pending=@("scale","pivot","UVs","normals/tangents","material slots","collision","triangle count","LOD/cull plan")
    ready_for_import=$false
    rule="Prepared/scanned only. READY_FOR_IMPORT requires class-specific QC and explicit promotion evidence."
  }
}

$report = [ordered]@{
  schema_version=1
  batch_id=[string]$manifest.batch_id
  generated_at_utc=[DateTime]::UtcNow.ToString("o")
  requested_external_items=@($manifest.external_items).Count
  project_owned_fallback_count=@($manifest.project_owned_fallback_bank).Count
  prepared_count=$prepared.Count
  pending_count=$pending.Count
  blocked_count=$blocked.Count
  prepared=$prepared
  pending=$pending
  blocked=$blocked
  rule="No item is promoted to READY_FOR_IMPORT by this script. Source/license/receipt/SHA256 and payload scanning are preparation gates only."
}

$receiptPath = Join-Path $OutputRoot "p1c01_architecture_intake_receipt.json"
$report | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $receiptPath -Encoding UTF8

if ($blocked.Count -gt 0) {
  Write-Host ("P1C01_ARCH_INTAKE_BLOCKED requested="+@($manifest.external_items).Count+" prepared="+$prepared.Count+" pending="+$pending.Count+" blocked="+$blocked.Count+" receipt="+$receiptPath)
  exit 2
}

Write-Host ("P1C01_ARCH_INTAKE_PASS requested="+@($manifest.external_items).Count+" prepared="+$prepared.Count+" pending="+$pending.Count+" blocked=0 receipt="+$receiptPath)
