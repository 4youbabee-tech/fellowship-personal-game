param(
  [string]$ManifestPath = "Data/P1C01KayKitRigTechnicalBridgeV1.json",
  [string]$OutputRoot = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.IO.Compression.FileSystem

$root = Split-Path $PSScriptRoot -Parent
if(-not [IO.Path]::IsPathRooted($ManifestPath)){ $ManifestPath = Join-Path $root $ManifestPath }
if(-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)){ throw "KAYKIT_RIG_MANIFEST_MISSING path=$ManifestPath" }

$manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
if(([string]$manifest.source.license).ToUpperInvariant() -ne "CC0-1.0"){ throw "KAYKIT_RIG_LICENSE_POLICY_FAIL" }
if(([string]$manifest.source.required_final_format).ToUpperInvariant() -ne "FBX"){ throw "KAYKIT_RIG_FORMAT_POLICY_FAIL" }
if([string]::IsNullOrWhiteSpace($OutputRoot)){ $OutputRoot = Join-Path $env:RUNNER_TEMP "shire-kaykit-rig-bridge" }

$downloadRoot = Join-Path $OutputRoot "download"
$extractRoot = Join-Path $OutputRoot "extracted"
if(Test-Path -LiteralPath $OutputRoot){ Remove-Item -LiteralPath $OutputRoot -Recurse -Force }
New-Item -ItemType Directory -Path $downloadRoot -Force | Out-Null
New-Item -ItemType Directory -Path $extractRoot -Force | Out-Null

$archive = Join-Path $downloadRoot "kaykit_adventurers_main.zip"
$license = Join-Path $downloadRoot "LICENSE.txt"
$headers = @{ "User-Agent" = "ShireJourney-KayKit-RigBridge/1.0" }

Invoke-WebRequest -UseBasicParsing -Uri ([string]$manifest.source.archive_url) -Headers $headers -OutFile $archive
Invoke-WebRequest -UseBasicParsing -Uri ([string]$manifest.source.license_url) -Headers $headers -OutFile $license

if(-not (Test-Path -LiteralPath $archive -PathType Leaf)){ throw "KAYKIT_RIG_ARCHIVE_MISSING" }
if(-not (Test-Path -LiteralPath $license -PathType Leaf)){ throw "KAYKIT_RIG_LICENSE_MISSING" }

$archiveFile = Get-Item -LiteralPath $archive
if($archiveFile.Length -le 0 -or $archiveFile.Length -gt 167772160){ throw "KAYKIT_RIG_ARCHIVE_SIZE_FAIL bytes=$($archiveFile.Length)" }
$licenseText = Get-Content -LiteralPath $license -Raw
if($licenseText -notmatch "Creative Commons Zero|CC0"){ throw "KAYKIT_RIG_LICENSE_MARKER_MISSING" }

$archiveSha = (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant()
$licenseSha = (Get-FileHash -LiteralPath $license -Algorithm SHA256).Hash.ToLowerInvariant()

function Get-FbxVersion {
  param([byte[]]$Bytes,[string]$Ascii)
  if($Bytes.Length -ge 27){
    $prefix = [Text.Encoding]::ASCII.GetString($Bytes,0,[Math]::Min(32,$Bytes.Length))
    if($prefix.StartsWith("Kaydara FBX Binary")){ return [BitConverter]::ToInt32($Bytes,23) }
  }
  if($Ascii -match 'FBXVersion\s*:\s*(\d+)'){ return [int]$Matches[1] }
  return 0
}

$preferred = @($manifest.candidate_policy.preferred_entries | ForEach-Object { ([string]$_).ToLowerInvariant() })
$maxBytes = [int64]$manifest.candidate_policy.max_single_fbx_bytes
$rows = @()
$zip = [IO.Compression.ZipFile]::OpenRead($archive)
try {
  foreach($entry in $zip.Entries){
    $name = ([string]$entry.FullName).Replace([char]92,'/')
    $parts = @($name.Split('/') | Where-Object { $_ -ne '' })
    if($name.StartsWith('/') -or $name -match '^[A-Za-z]:' -or @($parts | Where-Object { $_ -eq '..' }).Count -gt 0){
      throw "KAYKIT_RIG_ARCHIVE_PATH_UNSAFE entry=$name"
    }
    if($entry.Length -gt 536870912){ throw "KAYKIT_RIG_ARCHIVE_ENTRY_OVERSIZE entry=$name bytes=$($entry.Length)" }
  }

  $fbxEntries = @($zip.Entries | Where-Object {
    $n = ([string]$_.FullName).Replace([char]92,'/')
    $lower = $n.ToLowerInvariant()
    $leaf = @($lower.Split('/') | Where-Object { $_ -ne '' })[-1]
    ($lower -like "*/characters/fbx/*") -and ($preferred -contains $leaf)
  })
  if($fbxEntries.Count -lt 1){ throw "KAYKIT_RIG_NO_PREFERRED_FBX" }

  foreach($entry in $fbxEntries){
    if([int64]$entry.Length -le 0 -or [int64]$entry.Length -gt $maxBytes){ continue }
    $leaf = [IO.Path]::GetFileName([string]$entry.FullName)
    $dest = Join-Path $extractRoot $leaf
    [IO.Compression.ZipFileExtensions]::ExtractToFile($entry,$dest,$true)
    $bytes = [IO.File]::ReadAllBytes($dest)
    $ascii = [Text.Encoding]::ASCII.GetString($bytes)
    $version = Get-FbxVersion -Bytes $bytes -Ascii $ascii
    $sha = (Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash.ToLowerInvariant()
    $hasGeometry = $ascii.Contains("Geometry")
    $hasModel = $ascii.Contains("Model")
    $hasLimb = $ascii.Contains("LimbNode")
    $hasSkin = $ascii.Contains("Skin")
    $hasCluster = $ascii.Contains("Cluster")
    $hasAnim = $ascii.Contains("AnimationStack") -or $ascii.Contains("AnimationCurve")
    $versionOk = $version -gt 0 -and $version -le [int]$manifest.candidate_policy.fbx_version_ceiling
    $staticPass = $versionOk -and $hasGeometry -and $hasModel -and $hasLimb -and $hasSkin -and $hasCluster
    $priority = [Array]::IndexOf($preferred,$leaf.ToLowerInvariant())
    if($priority -lt 0){ $priority = 999 }
    $rows += [pscustomobject]@{
      entry=[string]$entry.FullName
      filename=$leaf
      extracted_path=$dest
      bytes=[int64]$entry.Length
      sha256=$sha
      fbx_version=[int]$version
      geometry=$hasGeometry
      model=$hasModel
      limb_node=$hasLimb
      skin=$hasSkin
      cluster=$hasCluster
      animation=$hasAnim
      static_pass=$staticPass
      priority=$priority
    }
    Write-Host ("KAYKIT_RIG_FBX file="+$leaf+" bytes="+$entry.Length+" sha256="+$sha+" version="+$version+" limb="+$hasLimb+" skin="+$hasSkin+" cluster="+$hasCluster+" anim="+$hasAnim+" staticPass="+$staticPass+" priority="+$priority)
  }
}
finally { $zip.Dispose() }

$selected = @($rows | Where-Object { $_.static_pass } | Sort-Object priority,bytes | Select-Object -First ([int]$manifest.candidate_policy.maximum_ue4_candidates))
$receipt = [ordered]@{
  schema_version=1
  status=if($selected.Count -gt 0){"STATIC_BRIDGE_READY_FOR_UE4"}else{"REJECTED_STATIC_NO_COMPATIBLE_FBX"}
  source_repository=[string]$manifest.source.repository
  archive_sha256=$archiveSha
  archive_bytes=[int64]$archiveFile.Length
  license_sha256=$licenseSha
  scanned_count=$rows.Count
  selected_count=$selected.Count
  selected_candidates=@($selected | Select-Object entry,filename,extracted_path,bytes,sha256,fbx_version,animation,priority)
  candidates=@($rows | Select-Object entry,filename,bytes,sha256,fbx_version,geometry,model,limb_node,skin,cluster,animation,static_pass,priority)
  runtime_integration_allowed=$false
  final_likeness=$false
  evidence_boundary="Hosted source/license/hash/static FBX structure only. Real UE4.27 technical import gate is next."
}
$receiptPath = Join-Path $OutputRoot "p1c01_kaykit_rig_bridge_static.json"
$receipt | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $receiptPath -Encoding UTF8

if($selected.Count -lt 1){ throw "KAYKIT_RIG_STATIC_BRIDGE_EMPTY receipt=$receiptPath" }
Write-Host ("KAYKIT_RIG_STATIC_BRIDGE_PASS archiveSha="+$archiveSha+" selected="+$selected.Count+" receipt="+$receiptPath)
