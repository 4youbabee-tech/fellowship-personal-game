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

$knownRejected=@{}
foreach($row in @($manifest.known_technical_rejections)){
  $hash=([string]$row.sha256).ToLowerInvariant()
  if(-not [string]::IsNullOrWhiteSpace($hash)){ $knownRejected[$hash]=$row }
}

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
# Inspect additional entries when the first candidates have exact-SHA rejection
# evidence, without ever sending more than maxCandidates to the UE4 runner.
$maxScanCandidates=[Math]::Min(8, @($manifest.source.direct_candidates).Count)
$rows=@()
$candidates=@($manifest.source.direct_candidates)
if($candidates.Count -lt 1){ throw "KAYKIT_RIG_DIRECT_CANDIDATES_EMPTY" }

foreach($candidate in @($candidates | Select-Object -First $maxScanCandidates)){
  $filename=[string]$candidate.filename
  $url=[string]$candidate.url
  if([IO.Path]::GetExtension($filename).ToLowerInvariant() -ne ".fbx"){ throw "KAYKIT_RIG_NON_FBX_CANDIDATE file=$filename" }
  if(-not $url.StartsWith("https://raw.githubusercontent.com/KayKit-Game-Assets/KayKit-Character-Pack-Adventures-1.0/")){
    throw "KAYKIT_RIG_UNAPPROVED_RAW_SOURCE url=$url"
  }

  # A source URL pinned to an immutable commit plus its known rejected SHA is
  # enough to avoid downloading or re-probing a previously rejected FBX.
  # Preserve the exclusion reason in the receipt; do NOT claim a fresh hash check.
  $expectedSha=([string]$candidate.expected_sha256).ToLowerInvariant()
  if(-not [string]::IsNullOrWhiteSpace($expectedSha) -and $knownRejected.ContainsKey($expectedSha)){
    $rows += [pscustomobject]@{
      entry=[string]$candidate.repository_path
      filename=$filename
      source_url=$url
      extracted_path=""
      bytes=[int64]0
      sha256=$expectedSha
      fbx_version=0
      geometry=$false
      model=$false
      limb_node=$false
      skin=$false
      cluster=$false
      animation=$false
      smoothing_groups=$false
      expected_sha256=$expectedSha
      source_git_blob_sha=[string]$candidate.source_git_blob_sha
      p1c01_candidate_roles=@($candidate.p1c01_candidate_roles)
      known_rejection=$true
      rejection_reason="EXACT_SHA_PREVIOUS_UE4_REJECTION"
      freshly_downloaded=$false
      static_pass=$false
    }
    Write-Host ("KAYKIT_RIG_EARLY_REJECT file="+$filename+" sha256="+$expectedSha+" reason=EXACT_SHA_PREVIOUS_UE4_REJECTION hostedDownload=no ue4Probe=no")
    continue
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
  $expectedSha=([string]$candidate.expected_sha256).ToLowerInvariant()
  if(-not [string]::IsNullOrWhiteSpace($expectedSha) -and $sha -ne $expectedSha){
    throw "KAYKIT_RIG_PAYLOAD_HASH_FAIL file=$filename expected=$expectedSha actual=$sha"
  }
  $hasGeometry=$ascii.Contains("Geometry")
  $hasModel=$ascii.Contains("Model")
  $hasLimb=$ascii.Contains("LimbNode")
  $hasSkin=$ascii.Contains("Skin")
  $hasCluster=$ascii.Contains("Cluster")
  # UE4.27's import policy explicitly rejects "No smoothing group information".
  # Require FBX smoothing-layer metadata before reserving the scarce UE4 runner;
  # final validity is still determined by the real UE4 import.
  $hasSmoothingGroups=$ascii.Contains("LayerElementSmoothing")
  $hasAnim=$ascii.Contains("AnimationStack") -or $ascii.Contains("AnimationCurve")
  $versionOk=$version -gt 0 -and $version -le [int]$manifest.candidate_policy.fbx_version_ceiling
  $knownRejection=$knownRejected.ContainsKey($sha)
  $staticPass=$versionOk -and $hasGeometry -and $hasModel -and $hasLimb -and $hasSkin -and $hasCluster -and $hasSmoothingGroups -and (-not $knownRejection)

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
    smoothing_groups=$hasSmoothingGroups
    rejection_reason=if(-not $hasSmoothingGroups){"MISSING_FBX_SMOOTHING_LAYER"}else{""}
    freshly_downloaded=$true
    expected_sha256=$expectedSha
    source_git_blob_sha=[string]$candidate.source_git_blob_sha
    p1c01_candidate_roles=@($candidate.p1c01_candidate_roles)
    known_rejection=$knownRejection
    static_pass=$staticPass
  }
  Write-Host ("KAYKIT_RIG_FBX file="+$filename+" bytes="+$item.Length+" sha256="+$sha+" version="+$version+" limb="+$hasLimb+" skin="+$hasSkin+" cluster="+$hasCluster+" smoothingGroups="+$hasSmoothingGroups+" anim="+$hasAnim+" knownRejected="+$knownRejection+" staticPass="+$staticPass)
}

$selected=@($rows | Where-Object { $_.static_pass } | Select-Object -First $maxCandidates)
$knownRejectedRows=@($rows | Where-Object { $_.known_rejection })
$bridgeStatus=if($selected.Count -gt 0){"STATIC_BRIDGE_READY_FOR_UE4"}elseif($rows.Count -gt 0 -and $knownRejectedRows.Count -eq $rows.Count){"STATIC_BRIDGE_EXHAUSTED_KNOWN_REJECTIONS"}else{"STATIC_BRIDGE_NO_QUALIFIED_CANDIDATES"}
$receipt=[ordered]@{
  schema_version=3
  status=$bridgeStatus
  delivery_mode="DIRECT_OFFICIAL_RAW_FBX"
  license_sha256=$licenseSha
  scanned_count=$rows.Count
  known_rejection_count=$knownRejectedRows.Count
  selected_count=$selected.Count
  target_character=[string]$manifest.target_character
  technical_import_target=[ordered]@{
    source_relative="Characters/Rigs/P1C01_TECHNICAL_BRIDGE/SK_P1C01_KAYKIT_TECHNICAL.fbx"
    content_dir="Content/Production/Characters/Rigs/P1C01_TECHNICAL_BRIDGE"
    asset_name="SK_P1C01_KAYKIT_TECHNICAL"
  }
  selected_candidates=@($selected | Select-Object entry,filename,source_url,extracted_path,bytes,sha256,expected_sha256,source_git_blob_sha,fbx_version,animation,p1c01_candidate_roles)
  candidates=@($rows | Select-Object entry,filename,source_url,bytes,sha256,expected_sha256,source_git_blob_sha,fbx_version,geometry,model,limb_node,skin,cluster,animation,smoothing_groups,rejection_reason,freshly_downloaded,p1c01_candidate_roles,known_rejection,static_pass)
  runtime_integration_allowed=$false
  final_likeness=$false
  evidence_boundary="Official raw-source/license/hash/static FBX structure only. Real UE4.27 skeletal technical import gate is next."
}
$receiptPath=Join-Path $OutputRoot "p1c01_kaykit_rig_bridge_static.json"
$receipt | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $receiptPath -Encoding UTF8

if($selected.Count -lt 1){
  if($bridgeStatus -eq "STATIC_BRIDGE_EXHAUSTED_KNOWN_REJECTIONS"){
    Write-Host ("KAYKIT_RIG_STATIC_BRIDGE_EXHAUSTED_KNOWN_REJECTIONS known="+$knownRejectedRows.Count+" selected=0 ue4RunnerRequired=false receipt="+$receiptPath)
    exit 0
  }
  # Candidate rejection is a successful source QC decision, not a broken CI
  # runner. The receipt remains explicit: no usable candidate and no UE4 gate.
  Write-Host ("KAYKIT_RIG_STATIC_NO_QUALIFIED_CANDIDATE scanned="+$rows.Count+" selected=0 ue4RunnerRequired=false receipt="+$receiptPath)
  exit 0
}
Write-Host ("KAYKIT_RIG_STATIC_BRIDGE_PASS delivery=raw selected="+$selected.Count+" receipt="+$receiptPath)
