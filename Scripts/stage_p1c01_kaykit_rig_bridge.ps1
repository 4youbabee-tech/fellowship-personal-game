param(
  [string]$ManifestPath = "Data/P1C01KayKitRigTechnicalBridgeV1.json",
  [string]$OutputRoot = "",
  [switch]$ProductionPacket,
  [string]$BlenderExecutable = "blender"
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

if($ProductionPacket){
  # Correct the two observed raw-FBX failures before UE: complete bind pose and
  # explicit smoothing. Never resubmit the byte-identical rejected source.
  $policy=$manifest.production_normalization
  if(-not $policy){ throw "KAYKIT_PRODUCTION_NORMALIZATION_POLICY_MISSING" }
  if([string]::IsNullOrWhiteSpace($OutputRoot)){ $OutputRoot=Join-Path $env:RUNNER_TEMP "shire-kaykit-production" }
  $original=Join-Path $OutputRoot "original"
  $packet=Join-Path $OutputRoot "packet"
  New-Item -ItemType Directory -Force -Path $original,$packet | Out-Null
  $source=$manifest.source.direct_candidates[0]
  $revision=[string]$policy.source_commit
  if($revision -notmatch '^[a-f0-9]{40}$'){ throw "KAYKIT_PRODUCTION_REVISION_INVALID" }
  $inputs=@(
    @{url=([string]$source.url).Replace('/main/',"/$revision/");name='Rogue.fbx';sha=[string]$policy.source_sha256},
    @{url=([string]$source.texture_url).Replace('/main/',"/$revision/");name='rogue_texture.png';sha=[string]$policy.texture_sha256},
    @{url=([string]$manifest.source.license_url).Replace('/main/',"/$revision/");name='LICENSE.txt';sha=[string]$policy.license_sha256}
  )
  foreach($inputFile in $inputs){
    $path=Join-Path $original $inputFile.name
    Invoke-WebRequest -UseBasicParsing -Uri $inputFile.url -OutFile $path
    if((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $inputFile.sha){ throw "KAYKIT_PRODUCTION_INPUT_HASH_REJECT file=$($inputFile.name)" }
  }
  if((Get-Content (Join-Path $original 'LICENSE.txt') -Raw) -notmatch 'Creative Commons Zero|CC0'){ throw "KAYKIT_PRODUCTION_LICENSE_REJECT" }
  & $BlenderExecutable --background --factory-startup --python-exit-code 93 --python (Join-Path $root 'Tools/CloudAssetBuild/prepare_kaykit_character.py') -- --source-fbx (Join-Path $original 'Rogue.fbx') --texture (Join-Path $original 'rogue_texture.png') --license (Join-Path $original 'LICENSE.txt') --out $packet
  if($LASTEXITCODE -ne 0){ throw "KAYKIT_PRODUCTION_BLENDER_REJECT" }
  $proof=Get-Content (Join-Path $packet 'source_receipt.json') -Raw | ConvertFrom-Json
  if($proof.status -ne 'NORMALIZED_KAYKIT_CHARACTER_SOURCE_PASS' -or $proof.mesh.vertex_count -lt 2000 -or $proof.mesh.bone_count -lt 20 -or $proof.mesh.max_influences -gt 4 -or $proof.mesh.zero_weight_vertices -ne 0){ throw "KAYKIT_PRODUCTION_SKIN_REJECT" }
  foreach($file in $proof.files.PSObject.Properties){
    if((Get-FileHash -LiteralPath (Join-Path $packet $file.Name) -Algorithm SHA256).Hash.ToLowerInvariant() -ne [string]$file.Value){ throw "KAYKIT_PRODUCTION_PACKET_HASH_REJECT file=$($file.Name)" }
  }
  Write-Host "KAYKIT_PRODUCTION_PACKET_READY path=$packet license=CC0 unified=1 bones=$($proof.mesh.bone_count) maxInfluences=$($proof.mesh.max_influences) sourceOnly=true UnrealImportPending=true finalLikeness=false"
  exit 0
}

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
  $knownRejection=$knownRejected.ContainsKey($sha)
  $staticPass=$versionOk -and $hasGeometry -and $hasModel -and $hasLimb -and $hasSkin -and $hasCluster -and (-not $knownRejection)

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
    known_rejection=$knownRejection
    static_pass=$staticPass
  }
  Write-Host ("KAYKIT_RIG_FBX file="+$filename+" bytes="+$item.Length+" sha256="+$sha+" version="+$version+" limb="+$hasLimb+" skin="+$hasSkin+" cluster="+$hasCluster+" anim="+$hasAnim+" knownRejected="+$knownRejection+" staticPass="+$staticPass)
}

$selected=@($rows | Where-Object { $_.static_pass } | Select-Object -First $maxCandidates)
$knownRejectedRows=@($rows | Where-Object { $_.known_rejection })
$bridgeStatus=if($selected.Count -gt 0){"STATIC_BRIDGE_READY_FOR_UE4"}elseif($rows.Count -gt 0 -and $knownRejectedRows.Count -eq $rows.Count){"STATIC_BRIDGE_EXHAUSTED_KNOWN_REJECTIONS"}else{"REJECTED_STATIC_NO_COMPATIBLE_FBX"}
$receipt=[ordered]@{
  schema_version=3
  status=$bridgeStatus
  delivery_mode="DIRECT_OFFICIAL_RAW_FBX"
  license_sha256=$licenseSha
  scanned_count=$rows.Count
  known_rejection_count=$knownRejectedRows.Count
  selected_count=$selected.Count
  selected_candidates=@($selected | Select-Object entry,filename,source_url,extracted_path,bytes,sha256,fbx_version,animation)
  candidates=@($rows | Select-Object entry,filename,source_url,bytes,sha256,fbx_version,geometry,model,limb_node,skin,cluster,animation,known_rejection,static_pass)
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
  throw "KAYKIT_RIG_STATIC_BRIDGE_EMPTY receipt=$receiptPath"
}
Write-Host ("KAYKIT_RIG_STATIC_BRIDGE_PASS delivery=raw selected="+$selected.Count+" receipt="+$receiptPath)
