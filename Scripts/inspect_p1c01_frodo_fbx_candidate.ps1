param(
  [string]$ManifestPath = "Data/P1C01HeroSkeletalCandidateWaveV1.json",
  [Parameter(Mandatory=$true)][string]$CandidateReport,
  [string]$OutputRoot = "",
  [switch]$SchemaSelfTest
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-OptionalPropertyValue {
  param([object]$Object,[string]$Name,[object]$Default=$null)
  if($null -eq $Object){ return $Default }
  $property=$Object.PSObject.Properties[$Name]
  if($null -eq $property){ return $Default }
  return $property.Value
}

function Resolve-CandidateCharacterRows {
  param([object]$RootObject)

  if($null -eq $RootObject){
    throw "P1C01_FRODO_STATIC_QC_SCHEMA_UNSUPPORTED schema=null keys="
  }

  $charactersProperty=$RootObject.PSObject.Properties["characters"]
  if($null -ne $charactersProperty){
    return @($charactersProperty.Value)
  }

  $legacyProperty=$RootObject.PSObject.Properties["character_reports"]
  if($null -ne $legacyProperty){
    return @($legacyProperty.Value)
  }

  $rootRows=@($RootObject)
  $flat=@($rootRows | Where-Object {
    $null -ne $_.PSObject.Properties["character"] -and
    $null -ne $_.PSObject.Properties["candidates"]
  })
  if($flat.Count -gt 0){
    return $flat
  }

  $schema="unknown"
  $schemaProperty=$RootObject.PSObject.Properties["schema_version"]
  if($null -ne $schemaProperty){ $schema=[string]$schemaProperty.Value }
  $keys=@($RootObject.PSObject.Properties | ForEach-Object { $_.Name })
  throw ("P1C01_FRODO_STATIC_QC_SCHEMA_UNSUPPORTED schema="+$schema+" keys="+($keys -join ","))
}

$ProjectRoot=Split-Path $PSScriptRoot -Parent
if(-not [IO.Path]::IsPathRooted($ManifestPath)){ $ManifestPath=Join-Path $ProjectRoot $ManifestPath }
if(-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)){ throw "P1C01_FRODO_STATIC_QC_MANIFEST_MISSING path=$ManifestPath" }
if(-not (Test-Path -LiteralPath $CandidateReport -PathType Leaf)){ throw "P1C01_FRODO_STATIC_QC_CANDIDATE_REPORT_MISSING path=$CandidateReport" }
if([string]::IsNullOrWhiteSpace($OutputRoot)){ $OutputRoot=Split-Path $CandidateReport -Parent }
New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null

$manifest=Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
$candidateReportObject=Get-Content -LiteralPath $CandidateReport -Raw | ConvertFrom-Json
$policy=$manifest.frodo_static_fbx_qc
$allow=@($policy.candidate_filename_allowlist | ForEach-Object { [string]$_ })
$sourceAllow=@((Get-OptionalPropertyValue $policy "candidate_source_asset_id_allowlist" @()) | ForEach-Object { [string]$_ })
$minimum=[int]$policy.minimum_static_structure_pass_candidates
$characterRows=@(Resolve-CandidateCharacterRows -RootObject $candidateReportObject)
$frodoRows=@($characterRows | Where-Object { [string](Get-OptionalPropertyValue $_ "character" "") -eq "FRODO" })
if($frodoRows.Count -ne 1){ throw "P1C01_FRODO_STATIC_QC_POOL_MISSING count=$($frodoRows.Count)" }
if($SchemaSelfTest){
  $candidateCount=@(Get-OptionalPropertyValue $frodoRows[0] "candidates" @()).Count
  Write-Host ("P1C01_FRODO_STATIC_QC_SCHEMA_SELF_TEST_PASS schema="+[string](Get-OptionalPropertyValue $candidateReportObject "schema_version" "unknown")+" frodoRows="+$frodoRows.Count+" candidates="+$candidateCount)
  exit 0
}

$selected=@()
foreach($candidate in @((Get-OptionalPropertyValue $frodoRows[0] "candidates" @()))){
  $filename=[string](Get-OptionalPropertyValue $candidate "filename" "")
  $sourceAssetId=[string](Get-OptionalPropertyValue $candidate "source_asset_id" "")
  if(($allow -icontains $filename) -or ($sourceAllow -icontains $sourceAssetId)){
    $selected += $candidate
  }
}
if($selected.Count -eq 0){ throw "P1C01_FRODO_STATIC_QC_NO_ALLOWLIST_CANDIDATE" }

$rows=@()
$passCount=0
foreach($candidate in $selected){
  $path=[string]$candidate.source_fbx
  if(-not (Test-Path -LiteralPath $path -PathType Leaf)){ throw "P1C01_FRODO_STATIC_QC_FILE_MISSING path=$path" }
  $bytes=[IO.File]::ReadAllBytes($path)
  if($bytes.Length -lt 64){ throw "P1C01_FRODO_STATIC_QC_FILE_TOO_SMALL path=$path bytes=$($bytes.Length)" }
  $prefix=[Text.Encoding]::ASCII.GetString($bytes,0,[Math]::Min(32,$bytes.Length))
  $ascii=[Text.Encoding]::ASCII.GetString($bytes)
  $binary=$prefix.StartsWith("Kaydara FBX Binary")
  $version=0
  if($binary -and $bytes.Length -ge 27){ $version=[BitConverter]::ToInt32($bytes,23) }
  elseif($ascii -match 'FBXVersion\s*:\s*(\d+)'){ $version=[int]$Matches[1] }
  $hasGeometry=$ascii.Contains("Geometry")
  $hasModel=$ascii.Contains("Model")
  $hasLimb=$ascii.Contains("LimbNode")
  $hasDeformer=$ascii.Contains("Deformer")
  $hasSkin=$ascii.Contains("Skin")
  $hasCluster=$ascii.Contains("Cluster")
  $hasAnimation=$ascii.Contains("AnimationStack") -or $ascii.Contains("AnimationCurve")
  $supportedProbeVersion=($version -ge 7000 -and $version -le 7500)
  $staticPass=$supportedProbeVersion -and $hasGeometry -and $hasModel -and $hasLimb -and $hasDeformer -and $hasSkin -and $hasCluster
  if($staticPass){ $passCount++ }
  $rows += [ordered]@{
    filename=[IO.Path]::GetFileName($path)
    source_asset_id=[string](Get-OptionalPropertyValue $candidate "source_asset_id" "")
    bytes=[int64]$bytes.Length
    sha256=(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
    fbx_encoding=if($binary){"BINARY"}else{"ASCII_OR_UNKNOWN"}
    fbx_file_version=$version
    probe_version_supported=$supportedProbeVersion
    geometry_marker=$hasGeometry
    model_marker=$hasModel
    limb_node_marker=$hasLimb
    deformer_marker=$hasDeformer
    skin_marker=$hasSkin
    cluster_marker=$hasCluster
    animation_marker=$hasAnimation
    static_structure_pass=$staticPass
    fbx_2018_export_confirmed=$false
    ue4_import_tested=$false
    deformation_tested=$false
    final_character_likeness=$false
    ready_for_import=$false
    state=if($staticPass){"STATIC_FBX_STRUCTURE_PRESENT_UE4_IMPORT_REQUIRED"}else{"STATIC_FBX_STRUCTURE_FAIL"}
  }
}
$report=[ordered]@{
  schema_version=1
  character="FRODO"
  generated_utc=[DateTime]::UtcNow.ToString("o")
  source_candidate_report=[string]$CandidateReport
  allowlist=$allow
  source_asset_id_allowlist=$sourceAllow
  inspected_count=$rows.Count
  static_structure_pass_count=$passCount
  minimum_static_structure_pass_candidates=$minimum
  candidates=$rows
  runtime_integration="NOT_STARTED"
  visual_acceptance="NOT_CLAIMED"
  evidence_boundary="Static FBX marker/header probe only. This does not prove FBX 2018 export, UE4 import, skeleton quality, skin-weight quality, retargeting, deformation, final Frodo likeness, runtime integration, PIE, device, visual or performance acceptance."
}
$output=Join-Path $OutputRoot "p1c01_frodo_fbx_static_qc.json"
$report | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $output -Encoding UTF8
Write-Host ("P1C01_FRODO_STATIC_QC_DIAGNOSTIC inspected="+$rows.Count+" pass="+$passCount+" required="+$minimum+" report="+$output)
foreach($row in $rows){
  Write-Host ("P1C01_FRODO_STATIC_QC_CANDIDATE file="+[string]$row.filename+" version="+[int]$row.fbx_file_version+" skeleton="+[bool]$row.limb_node_marker+" skin="+[bool]$row.skin_marker+" cluster="+[bool]$row.cluster_marker+" pass="+[bool]$row.static_structure_pass)
}
if($passCount -lt $minimum){ throw "P1C01_FRODO_STATIC_QC_FAIL pass=$passCount required=$minimum" }
Write-Host ("P1C01_FRODO_STATIC_QC_PASS pass="+$passCount+" inspected="+$rows.Count+" report="+$output)
exit 0
