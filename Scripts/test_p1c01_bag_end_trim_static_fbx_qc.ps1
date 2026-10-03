param(
  [string]$ManifestPath = "Data/P1C01BagEndHeroTrimSourceProbeV1.json",
  [string]$OutputRoot = ""
)
Set-StrictMode -Version Latest
$ErrorActionPreference="Stop"
[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12
$root=Split-Path $PSScriptRoot -Parent
if(-not [IO.Path]::IsPathRooted($ManifestPath)){ $ManifestPath=Join-Path $root $ManifestPath }
$m=Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
if([string]::IsNullOrWhiteSpace($OutputRoot)){ $OutputRoot=Join-Path $env:RUNNER_TEMP "shire-bag-end-trim-static-qc" }
New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null
$zip=Join-Path $OutputRoot "kenney_building-kit.zip"
$extract=Join-Path $OutputRoot "extract"
if(Test-Path $zip){Remove-Item $zip -Force}
if(Test-Path $extract){Remove-Item $extract -Recurse -Force}
Invoke-WebRequest -UseBasicParsing -Uri ([string]$m.official_staging_plan.official_download_url) -OutFile $zip -TimeoutSec 180
$archiveSha=(Get-FileHash $zip -Algorithm SHA256).Hash.ToLowerInvariant()
if($archiveSha -ne ([string]$m.official_staging_plan.archive_sha256).ToLowerInvariant()){ throw "BAG_END_TRIM_QC_ARCHIVE_HASH_FAIL actual=$archiveSha" }
Expand-Archive -LiteralPath $zip -DestinationPath $extract -Force

$names=@("door-rotate-round-a.fbx","wall-doorway-round.fbx","wall-window-round-detailed.fbx")
$expected=@{}
foreach($row in @($m.exact_file_discovery.candidate_files)){ $expected[[string]$row.file]=([string]$row.payload_sha256).ToLowerInvariant() }
$rows=@()
foreach($name in $names){
  $matches=@(Get-ChildItem $extract -Recurse -File | Where-Object {$_.Name -ieq $name})
  $match=$null
  foreach($item in $matches){
    $sha=(Get-FileHash $item.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    if($sha -eq $expected[$name]){ $match=$item; break }
  }
  if($null -eq $match){ throw "BAG_END_TRIM_QC_EXACT_FILE_MISSING file=$name" }
  $bytes=[IO.File]::ReadAllBytes($match.FullName)
  if($bytes.Length -lt 64){ throw "BAG_END_TRIM_QC_TOO_SMALL file=$name" }
  $prefix=[Text.Encoding]::ASCII.GetString($bytes,0,[Math]::Min(32,$bytes.Length))
  $ascii=[Text.Encoding]::ASCII.GetString($bytes)
  $binary=$prefix.StartsWith("Kaydara FBX Binary")
  $version=0
  if($binary -and $bytes.Length -ge 27){ $version=[BitConverter]::ToInt32($bytes,23) }
  elseif($ascii -match 'FBXVersion\s*:\s*(\d+)'){ $version=[int]$Matches[1] }
  $geometry=$ascii.Contains("Geometry")
  $model=$ascii.Contains("Model")
  $uv=$ascii.Contains("LayerElementUV")
  $material=$ascii.Contains("Material")
  $supported=($version -ge 7000 -and $version -le 7500)
  $pass=$supported -and $geometry -and $model -and $uv -and $material
  $row=[ordered]@{file=$name;bytes=[int64]$bytes.Length;sha256=(Get-FileHash $match.FullName -Algorithm SHA256).Hash.ToLowerInvariant();encoding=if($binary){"BINARY"}else{"ASCII_OR_UNKNOWN"};fbx_version=$version;ue4_probe_version_supported=$supported;geometry_marker=$geometry;model_marker=$model;uv_marker=$uv;material_marker=$material;static_qc_pass=$pass}
  $rows += $row
  Write-Host ("BAG_END_TRIM_STATIC_QC file="+$name+" version="+$version+" geometry="+$geometry+" model="+$model+" uv="+$uv+" material="+$material+" pass="+$pass)
  # A rejected candidate is a valid completed QC outcome; preserve the evidence
  # instead of failing the workflow before the report can be merged.
}
$allPass=@($rows | Where-Object { -not [bool]$_.static_qc_pass }).Count -eq 0
$result=if($allPass){"PASS"}else{"REJECTED_STATIC_QC"}
$report=[ordered]@{schema_version=1;archive_sha256=$archiveSha;candidates=$rows;result=$result;runtime_integration_allowed=$false;evidence_boundary="Static binary/header marker QC only; real UE4.27.2 import is allowed only when result=PASS. No visual/runtime acceptance is implied."}
$out=Join-Path $OutputRoot "p1c01_bag_end_trim_static_fbx_qc.json"
$report | ConvertTo-Json -Depth 8 | Set-Content $out -Encoding UTF8
if($allPass){
  Write-Host "BAG_END_TRIM_STATIC_QC_PASS candidates=$($rows.Count) report=$out"
}else{
  $rejected=@($rows | Where-Object { -not [bool]$_.static_qc_pass } | ForEach-Object { ([string]$_.file)+":FBX_"+([string]$_.fbx_version) })
  Write-Host ("BAG_END_TRIM_STATIC_QC_REJECTED candidates="+($rejected -join ",")+" report="+$out)
}
