param(
  [string]$ManifestPath = "Data/P1C01KayKitRigTechnicalBridgeV1.json",
  [string]$OutputRoot = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path $PSScriptRoot -Parent
if(-not [IO.Path]::IsPathRooted($ManifestPath)){ $ManifestPath = Join-Path $root $ManifestPath }
if(-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)){ throw "KAYKIT_RIG_MANIFEST_MISSING path=$ManifestPath" }
$manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json

if(([string]$manifest.source.license).ToUpperInvariant() -ne "CC0-1.0"){ throw "KAYKIT_RIG_LICENSE_POLICY_FAIL" }
if(([string]$manifest.source.required_final_format).ToUpperInvariant() -ne "FBX"){ throw "KAYKIT_RIG_FORMAT_POLICY_FAIL" }
if(([string]$manifest.source.delivery_mode) -ne "DIRECT_OFFICIAL_RAW_FBX"){ throw "KAYKIT_RIG_DELIVERY_MODE_FAIL" }

if([string]::IsNullOrWhiteSpace($OutputRoot)){ $OutputRoot = Join-Path $env:RUNNER_TEMP "shire-kaykit-rig-bridge" }
if(Test-Path -LiteralPath $OutputRoot){ Remove-Item -LiteralPath $OutputRoot -Recurse -Force }
$payloadRoot = Join-Path $OutputRoot "extracted"
New-Item -ItemType Directory -Path $payloadRoot -Force | Out-Null

$headers = @{ "User-Agent" = "ShireJourney-KayKit-RigBridge/2.0" }
$licensePath = Join-Path $OutputRoot "LICENSE.txt"
Invoke-WebRequest -UseBasicParsing -Uri ([string]$manifest.source.license_url) -Headers $headers -OutFile $licensePath
if(-not (Test-Path -LiteralPath $licensePath -PathType Leaf)){ throw "KAYKIT_RIG_LICENSE_MISSING" }
$licenseText = Get-Content -LiteralPath $licensePath -Raw
if($licenseText -notmatch "Creative Commons Zero|CC0"){ throw "KAYKIT_RIG_LICENSE_MARKER_MISSING" }
$licenseSha = (Get-FileHash -LiteralPath $licensePath -Algorithm SHA256).Hash.ToLowerInvariant()

function Get-FbxVersion {
  param([byte[]]$Bytes,[string]$Ascii)
  if($Bytes.Length -ge 27){
    $prefix=[Text.Encoding]::ASCII.GetString($Bytes,0,[Math]::Min(32,$Bytes.Length))
    if($prefix.StartsWith("Kaydara FBX Binary")){ return [BitConverter]::ToInt32($Bytes,23) }
  }
  if($Ascii -match 'FBXVersion\s*:\s*(\d+)'){ return [int]$Matches[1] }
  return 0
}

$maxCandidates=[int]$manifest.candidate_policy.maximum_ue4_candidates
$maxBytes=[int64]$manifest.candidate_policy.max_single_fbx_bytes
$rows=@()
$candidates=@($manifest.source.direct_candidates)
if($candidates.Count -lt 1){ throw "KAYKIT_RIG_DIRECT_CANDIDATES_EMPTY" }

foreach($candidate in @($candidates | Select-Object -First $maxCandidates)){
  $filename=[string]$candidate.filename
  $url=[string]$candidate.url
  if([IO.Path]::GetExtension($filename).ToLowerInvariant() -ne ".fbx"){ throw "KAYKIT_RIG_NON_FBX_CANDIDATE file=$filename" }
  if(-not $url.StartsWith("https://raw.githubusercontent.com/KayKit-Game-Assets/KayKit-Character-Pack-Adventures-1.0/")){
    throw "KAYKIT_RIG_UNAPPROVED_RAW_SOURCE url=$url"
  }

  $dest=Join-Path $payloadRoot $filename
  Invoke-WebRequest -UseBasicParsing -Uri $url -Headers $headers -OutFile $dest
  if(-not (Test-Path -LiteralPath $dest -PathType Leaf)){ throw "KAYKIT_RIG_PAYLOAD_MISSING file=$filename" }
  $item=Get-Item -LiteralPath $dest
  if($item.Length -le 0 -or $item.Length -gt $maxBytes){ throw "KAYKIT_RIG_PAYLOAD_SIZE_FAIL file=$filename bytes=$($item.Length)" }

  $bytes=[IO.File]::ReadAllBytes($dest)
  $ascii=[Text.Encoding]::ASCII.GetString($bytes)
  $version=Get-FbxVersion -Bytes $bytes -Ascii $ascii
  $sha=(Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash.ToLowerInvariant()
  $hasGeometry=$ascii.Contains("Geometry")
  $hasModel=$ascii.Contains("Model")
  $hasLimb=$ascii.Contains("LimbNode")
  $hasSkin=$ascii.Contains("Skin")
  $hasCluster=$ascii.Contains("Cluster")
  $hasAnim=$ascii.Contains("AnimationStack") -or $ascii.Contains("AnimationCurve")
  $versionOk=$version -gt 0 -and $version -le [int]$manifest.candidate_policy.fbx_version_ceiling
  $staticPass=$versionOk -and $hasGeometry -and $hasModel -and $hasLimb -and $hasSkin -and $hasCluster

  $rows += [pscustomobject]@{
    entry=[string]$candidate.repository_path
    filename=$filename
    source_url=$url
    extracted_path=$dest
    bytes=[int64]$item.Length
    sha256=$sha
    fbx_version=[int]$version
    geometry=$hasGeometry
    model=$hasModel
    limb_node=$hasLimb
    skin=$hasSkin
    cluster=$hasCluster
    animation=$hasAnim
    static_pass=$staticPass
  }
  Write-Host ("KAYKIT_RIG_FBX file="+$filename+" bytes="+$item.Length+" sha256="+$sha+" version="+$version+" limb="+$hasLimb+" skin="+$hasSkin+" cluster="+$hasCluster+" anim="+$hasAnim+" staticPass="+$staticPass)
}

$selected=@($rows | Where-Object { $_.static_pass } | Select-Object -First $maxCandidates)
$receipt=[ordered]@{
  schema_version=2
  status=if($selected.Count -gt 0){"STATIC_BRIDGE_READY_FOR_UE4"}else{"REJECTED_STATIC_NO_COMPATIBLE_FBX"}
  delivery_mode="DIRECT_OFFICIAL_RAW_FBX"
  license_sha256=$licenseSha
  scanned_count=$rows.Count
  selected_count=$selected.Count
  selected_candidates=@($selected | Select-Object entry,filename,source_url,extracted_path,bytes,sha256,fbx_version,animation)
  candidates=@($rows | Select-Object entry,filename,source_url,bytes,sha256,fbx_version,geometry,model,limb_node,skin,cluster,animation,static_pass)
  runtime_integration_allowed=$false
  final_likeness=$false
  evidence_boundary="Official raw-source/license/hash/static FBX structure only. Real UE4.27 skeletal technical import gate is next."
}
$receiptPath=Join-Path $OutputRoot "p1c01_kaykit_rig_bridge_static.json"
$receipt | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $receiptPath -Encoding UTF8

if($selected.Count -lt 1){ throw "KAYKIT_RIG_STATIC_BRIDGE_EMPTY receipt=$receiptPath" }
Write-Host ("KAYKIT_RIG_STATIC_BRIDGE_PASS delivery=raw selected="+$selected.Count+" receipt="+$receiptPath)
