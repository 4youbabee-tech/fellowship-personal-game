param(
  [string]$ManifestPath = "Data/P1C01OpenGameArtLowpolyDummyCandidateV1.json",
  [string]$OutputRoot = ""
)
Set-StrictMode -Version Latest
$ErrorActionPreference="Stop"
Add-Type -AssemblyName System.IO.Compression.FileSystem
$root=Split-Path $PSScriptRoot -Parent
if(-not [IO.Path]::IsPathRooted($ManifestPath)){ $ManifestPath=Join-Path $root $ManifestPath }
$m=Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
if([string]::IsNullOrWhiteSpace($OutputRoot)){ $OutputRoot=Join-Path $env:RUNNER_TEMP "shire-frodo-lowpoly-dummy" }
$warehouse=Join-Path $OutputRoot "warehouse"
New-Item -ItemType Directory -Path $warehouse -Force | Out-Null
& (Join-Path $root "Scripts\stage_opengameart_character_candidate.ps1") -ManifestPath $ManifestPath -WarehouseRoot $warehouse
if($LASTEXITCODE -ne 0){ throw "FRODO_DUMMY_STAGE_FAIL exit=$LASTEXITCODE" }
$asset=$m.assets[0]
$zip=Join-Path $warehouse ("OpenGameArt\Characters\"+[string]$asset.filename)
if(-not (Test-Path -LiteralPath $zip -PathType Leaf)){ throw "FRODO_DUMMY_ZIP_MISSING path=$zip" }
$archiveSha=(Get-FileHash $zip -Algorithm SHA256).Hash.ToLowerInvariant()
$z=[IO.Compression.ZipFile]::OpenRead($zip)
try{
  $rows=@()
  foreach($entry in $z.Entries){
    if([IO.Path]::GetExtension($entry.FullName).ToLowerInvariant() -ne ".fbx"){ continue }
    if($entry.Length -lt 64){ continue }
    $tmp=Join-Path $OutputRoot ([Guid]::NewGuid().ToString()+".fbx")
    [IO.Compression.ZipFileExtensions]::ExtractToFile($entry,$tmp,$true)
    try{
      $bytes=[IO.File]::ReadAllBytes($tmp)
      $prefix=[Text.Encoding]::ASCII.GetString($bytes,0,[Math]::Min(32,$bytes.Length))
      $ascii=[Text.Encoding]::ASCII.GetString($bytes)
      $binary=$prefix.StartsWith("Kaydara FBX Binary")
      $version=0
      if($binary -and $bytes.Length -ge 27){$version=[BitConverter]::ToInt32($bytes,23)}
      elseif($ascii -match 'FBXVersion\s*:\s*(\d+)'){$version=[int]$Matches[1]}
      $row=[ordered]@{
        entry=$entry.FullName
        bytes=[int64]$entry.Length
        sha256=(Get-FileHash $tmp -Algorithm SHA256).Hash.ToLowerInvariant()
        fbx_version=$version
        geometry=$ascii.Contains("Geometry")
        model=$ascii.Contains("Model")
        limb_node=$ascii.Contains("LimbNode")
        deformer=$ascii.Contains("Deformer")
        skin=$ascii.Contains("Skin")
        cluster=$ascii.Contains("Cluster")
        animation=$ascii.Contains("AnimationStack") -or $ascii.Contains("AnimationCurve")
        ue4_probe_version_supported=($version -ge 7000 -and $version -le 7500)
      }
      $rows += $row
      Write-Host ("FRODO_DUMMY_FBX entry="+$row.entry+" bytes="+$row.bytes+" version="+$row.fbx_version+" limb="+$row.limb_node+" skin="+$row.skin+" cluster="+$row.cluster+" anim="+$row.animation)
    } finally { Remove-Item $tmp -Force -ErrorAction SilentlyContinue }
  }
} finally { $z.Dispose() }
if($rows.Count -lt 1){ throw "FRODO_DUMMY_NO_FBX" }
$technical=@($rows | Where-Object { $_.ue4_probe_version_supported -and $_.geometry -and $_.model -and $_.limb_node -and $_.deformer -and $_.skin -and $_.cluster })
$report=[ordered]@{
 schema_version=1
 archive_sha256=$archiveSha
 archive_bytes=[int64](Get-Item $zip).Length
 fbx_count=$rows.Count
 technical_candidate_count=$technical.Count
 fbx_entries=$rows
 next_state=if($technical.Count -gt 0){"UE4_TECHNICAL_PROBE_CANDIDATE_AVAILABLE"}else{"NO_STATIC_SKELETAL_CANDIDATE"}
 runtime_integration_allowed=$false
 evidence_boundary="Hosted archive inventory/static FBX marker evidence only; UE4 skeletal import and visual/runtime acceptance remain pending."
}
$out=Join-Path $OutputRoot "p1c01_frodo_lowpoly_dummy_inventory.json"
$report | ConvertTo-Json -Depth 10 | Set-Content $out -Encoding UTF8
Write-Host ("FRODO_DUMMY_INVENTORY_PASS fbx="+$rows.Count+" technicalCandidates="+$technical.Count+" report="+$out)
