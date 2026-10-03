param(
  [string]$ManifestPath = "Data/P1C01OpenGameArtKenneyAnimatedHeroCandidateBatchV1.json",
  [string]$RejectionHistoryPath = "Data/P1C01FrodoTechnicalRejectionHistoryV1.json",
  [string]$OutputRoot = "",
  [switch]$StageForUnreal
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.IO.Compression.FileSystem

$root = Split-Path $PSScriptRoot -Parent
foreach($name in @("ManifestPath","RejectionHistoryPath")) {
  $value = Get-Variable -Name $name -ValueOnly
  if(-not [IO.Path]::IsPathRooted($value)) { Set-Variable -Name $name -Value (Join-Path $root $value) }
}
if(-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)) { throw "FRODO_KENNEY_MANIFEST_MISSING path=$ManifestPath" }
if(-not (Test-Path -LiteralPath $RejectionHistoryPath -PathType Leaf)) { throw "FRODO_KENNEY_REJECTION_HISTORY_MISSING path=$RejectionHistoryPath" }

$manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
$history = Get-Content -LiteralPath $RejectionHistoryPath -Raw | ConvertFrom-Json
if(@($manifest.assets).Count -ne 1) { throw "FRODO_KENNEY_ASSET_COUNT_FAIL count=$(@($manifest.assets).Count)" }
$asset = $manifest.assets[0]
if(([string]$manifest.license).ToUpperInvariant() -ne "CC0-1.0") { throw "FRODO_KENNEY_LICENSE_FAIL" }
if(([string]$asset.required_final_format).ToUpperInvariant() -ne "FBX") { throw "FRODO_KENNEY_FORMAT_FAIL" }

if([string]::IsNullOrWhiteSpace($OutputRoot)) {
  $OutputRoot = Join-Path $env:RUNNER_TEMP "shire-frodo-kenney-animated-probe"
}
$warehouse = Join-Path $OutputRoot "warehouse"
$extractRoot = Join-Path $OutputRoot "extracted"
New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null
New-Item -ItemType Directory -Path $warehouse -Force | Out-Null
if(Test-Path -LiteralPath $extractRoot) { Remove-Item -LiteralPath $extractRoot -Recurse -Force }
New-Item -ItemType Directory -Path $extractRoot -Force | Out-Null

& (Join-Path $root "Scripts\stage_opengameart_character_candidate.ps1") -ManifestPath $ManifestPath -WarehouseRoot $warehouse

$archive = Join-Path $warehouse ("OpenGameArt\Characters\" + [string]$asset.filename)
if(-not (Test-Path -LiteralPath $archive -PathType Leaf)) { throw "FRODO_KENNEY_ARCHIVE_MISSING path=$archive" }
$archiveSha = (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant()
$archiveBytes = [int64](Get-Item -LiteralPath $archive).Length
$rejected = @{}
foreach($row in @($history.rejections)) {
  $hash = ([string]$row.sha256).ToLowerInvariant()
  if(-not [string]::IsNullOrWhiteSpace($hash)) { $rejected[$hash] = $true }
}

function Get-FbxVersion {
  param([byte[]]$Bytes,[string]$Ascii)
  if($Bytes.Length -ge 27) {
    $prefix = [Text.Encoding]::ASCII.GetString($Bytes,0,[Math]::Min(32,$Bytes.Length))
    if($prefix.StartsWith("Kaydara FBX Binary")) { return [BitConverter]::ToInt32($Bytes,23) }
  }
  if($Ascii -match 'FBXVersion\s*:\s*(\d+)') { return [int]$Matches[1] }
  return 0
}

$rows = @()
$zip = [IO.Compression.ZipFile]::OpenRead($archive)
try {
  $fbxEntries = @($zip.Entries | Where-Object { [IO.Path]::GetExtension($_.FullName).ToLowerInvariant() -eq ".fbx" })
  if($fbxEntries.Count -lt 1) { throw "FRODO_KENNEY_ARCHIVE_NO_FBX" }
  $index = 0
  foreach($entry in $fbxEntries) {
    $safeName = ("{0:D3}_{1}" -f $index, ([IO.Path]::GetFileName($entry.FullName)))
    $temp = Join-Path $extractRoot $safeName
    [IO.Compression.ZipFileExtensions]::ExtractToFile($entry,$temp,$true)
    $bytes = [IO.File]::ReadAllBytes($temp)
    $ascii = [Text.Encoding]::ASCII.GetString($bytes)
    $version = Get-FbxVersion -Bytes $bytes -Ascii $ascii
    $sha = (Get-FileHash -LiteralPath $temp -Algorithm SHA256).Hash.ToLowerInvariant()
    $nameLower = ([string]$entry.FullName).ToLowerInvariant()
    $hasGeometry = $ascii.Contains("Geometry")
    $hasModel = $ascii.Contains("Model")
    $hasLimb = $ascii.Contains("LimbNode")
    $hasSkin = $ascii.Contains("Skin")
    $hasCluster = $ascii.Contains("Cluster")
    $hasAnim = $ascii.Contains("AnimationStack") -or $ascii.Contains("AnimationCurve")
    $knownRejected = $rejected.ContainsKey($sha)
    $compatibleVersion = $version -gt 0 -and $version -le 7500
    $staticPass = $compatibleVersion -and $hasGeometry -and $hasModel -and $hasLimb -and $hasSkin -and $hasCluster -and (-not $knownRejected)
    $score = 0
    if($staticPass) { $score += 1000 }
    if($hasAnim) { $score += 40 }
    if($nameLower.Contains("male")) { $score += 20 }
    if($nameLower.Contains("character")) { $score += 12 }
    if($nameLower.Contains("skin")) { $score += 3 }
    if($nameLower.Contains("female")) { $score -= 100 }
    $rows += [pscustomobject]@{
      entry = [string]$entry.FullName
      bytes = [int64]$entry.Length
      extracted_path = $temp
      sha256 = $sha
      fbx_version = [int]$version
      geometry = $hasGeometry
      model = $hasModel
      limb_node = $hasLimb
      skin = $hasSkin
      cluster = $hasCluster
      animation = $hasAnim
      known_rejection = $knownRejected
      static_pass = $staticPass
      score = $score
    }
    Write-Host ("FRODO_KENNEY_FBX entry="+$entry.FullName+" bytes="+$entry.Length+" sha256="+$sha+" version="+$version+" limb="+$hasLimb+" skin="+$hasSkin+" cluster="+$hasCluster+" anim="+$hasAnim+" knownRejected="+$knownRejected+" staticPass="+$staticPass+" score="+$score)
    $index++
  }
}
finally {
  $zip.Dispose()
}

$selected = @($rows | Where-Object { $_.static_pass } | Sort-Object -Property @{Expression="score";Descending=$true}, @{Expression="bytes";Descending=$false}, @{Expression="entry";Descending=$false} | Select-Object -First 1)
if($selected.Count -ne 1) {
  $receipt = [ordered]@{
    schema_version = 1
    status = "REJECTED_STATIC_NO_COMPATIBLE_FBX"
    archive_sha256 = $archiveSha
    archive_bytes = $archiveBytes
    fbx_count = $rows.Count
    candidates = @($rows | Select-Object entry,bytes,sha256,fbx_version,geometry,model,limb_node,skin,cluster,animation,known_rejection,static_pass,score)
    runtime_integration_allowed = $false
  }
  $receiptPath = Join-Path $OutputRoot "p1c01_frodo_kenney_animated_inventory.json"
  $receipt | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $receiptPath -Encoding UTF8
  throw "FRODO_KENNEY_STATIC_CANDIDATE_MISSING receipt=$receiptPath"
}

$pick = $selected[0]
$receipt = [ordered]@{
  schema_version = 1
  status = "STATIC_CANDIDATE_SELECTED_UE4_PROBE_REQUIRED"
  archive_sha256 = $archiveSha
  archive_bytes = $archiveBytes
  fbx_count = $rows.Count
  selected = [ordered]@{
    entry = [string]$pick.entry
    bytes = [int64]$pick.bytes
    sha256 = [string]$pick.sha256
    fbx_version = [int]$pick.fbx_version
    animation = [bool]$pick.animation
    score = [int]$pick.score
  }
  candidates = @($rows | Select-Object entry,bytes,sha256,fbx_version,geometry,model,limb_node,skin,cluster,animation,known_rejection,static_pass,score)
  runtime_integration_allowed = $false
  evidence_boundary = "Hosted/static candidate identity only until the dedicated UE4.27 skeletal import probe completes."
}
$receiptPath = Join-Path $OutputRoot "p1c01_frodo_kenney_animated_inventory.json"
$receipt | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $receiptPath -Encoding UTF8

if($StageForUnreal) {
  $destination = Join-Path $root "SourceAssets\Production\Characters\Rigs\FRODO\SK_FRODO.fbx"
  New-Item -ItemType Directory -Path (Split-Path $destination -Parent) -Force | Out-Null
  Copy-Item -LiteralPath ([string]$pick.extracted_path) -Destination $destination -Force
  $copiedSha = (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLowerInvariant()
  if($copiedSha -ne [string]$pick.sha256) { throw "FRODO_KENNEY_COPY_HASH_FAIL expected=$($pick.sha256) actual=$copiedSha" }
  Write-Host ("FRODO_KENNEY_STAGE_FOR_UE4_PASS entry="+$pick.entry+" sha256="+$pick.sha256+" bytes="+$pick.bytes+" version="+$pick.fbx_version+" destination="+$destination)
}

Write-Host ("FRODO_KENNEY_STATIC_PASS archiveSha256="+$archiveSha+" archiveBytes="+$archiveBytes+" fbx="+$rows.Count+" selected="+$pick.entry+" selectedSha256="+$pick.sha256+" selectedBytes="+$pick.bytes+" version="+$pick.fbx_version+" animation="+$pick.animation+" receipt="+$receiptPath)
