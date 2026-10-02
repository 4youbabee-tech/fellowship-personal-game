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

function Get-CandidateCharacterRows {
  param([object]$CandidateReportObject)

  $roots=@($CandidateReportObject)
  if($roots.Count -eq 1){
    $root=$roots[0]
    $characters=Get-OptionalPropertyValue $root "characters" $null
    if($null -ne $characters){
      return @($characters)
    }

    $legacy=Get-OptionalPropertyValue $root "character_reports" $null
    if($null -ne $legacy){
      return @($legacy)
    }
  }

  $flattened=@($roots | Where-Object {
    $null -ne (Get-OptionalPropertyValue $_ "character" $null) -and
    $null -ne (Get-OptionalPropertyValue $_ "candidates" $null)
  })
  if($flattened.Count -gt 0){
    return $flattened
  }

  $schema="unknown"
  if($roots.Count -eq 1){
    $schemaValue=Get-OptionalPropertyValue $roots[0] "schema_version" $null
    if($null -ne $schemaValue){ $schema=[string]$schemaValue }
  }
  $keys=@()
  if($roots.Count -eq 1 -and $null -ne $roots[0]){
    $keys=@($roots[0].PSObject.Properties | ForEach-Object { $_.Name })
  }
  throw ("P1C01_FRODO_STATIC_QC_SCHEMA_UNSUPPORTED schema="+$schema+" keys="+($keys -join ","))
}

$ProjectRoot=Split-Path $PSScriptRoot -Parent
if(-not [IO.Path]::IsPathRooted($ManifestPath)){ $ManifestPath=Join-Path $ProjectRoot $ManifestPath }
if(-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)){ throw "P1C01_FRODO_STATIC_QC_MANIFEST_MISSING path=$ManifestPath" }
if(-not (Test-Path -LiteralPath $CandidateReport -PathType Leaf)){ throw "P1C01_FRODO_STATIC_QC_CANDIDATE_REPORT_MISSING path=$CandidateReport" }
if([string]::IsNullOrWhiteSpace($OutputRoot)){ $OutputRoot=Split-Path $CandidateReport -Parent }
New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null

$manifest=Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
$candidateReport=Get-Content -LiteralPath $CandidateReport -Raw | ConvertFrom-Json
$policy=$manifest.frodo_static_fbx_qc
$allow=@($policy.candidate_filename_allowlist | ForEach-Object { [string]$_ })
$minimum=[int]$policy.minimum_static_structure_pass_candidates
$characterRows=@(Get-CandidateCharacterRows $candidateReport)
$frodoRows=@($characterRows | Where-Object { [string](Get-OptionalPropertyValue $_ "character" "") -eq "FRODO" })
if($frodoRows.Count -ne 1){ throw "P1C01_FRODO_STATIC_QC_POOL_MISSING count=$($frodoRows.Count)" }
if($SchemaSelfTest){
  $candidateCount=@(Get-OptionalPropertyValue $frodoRows[0] "candidates" @()).Count
  Write-Host ("P1C01_FRODO_STATIC_QC_SCHEMA_SELF_TEST_PASS schema="+[string](Get-OptionalPropertyValue $candidateReport "schema_version" "unknown")+" frodoRows="+$frodoRows.Count+" candidates="+$candidateCount)
  exit 0
}

$selected=@()
foreach($filename in $allow){
  $matches=@((Get-OptionalPropertyValue $frodoRows[0] "candidates" @()) | Where-Object { [string](Get-OptionalPropertyValue $_ "filename" "") -ieq $filename })
  if($matches.Count -gt 1){ throw "P1C01_FRODO_STATIC_QC_DUPLICATE filename=$filename count=$($matches.Count)" }
  if($matches.Count -eq 1){ $selected += $matches[0] }
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
  source_candidate_report=$CandidateReport
  allowlist=$allow
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
