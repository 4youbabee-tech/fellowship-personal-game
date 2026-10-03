param(
  [string]$ManifestPath = "Data/P1C01OpenGameArtRpgHeroCandidateBatchV1.json",
  [string]$RejectionHistoryPath = "Data/P1C01FrodoTechnicalRejectionHistoryV1.json",
  [string]$OutputRoot = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.IO.Compression.FileSystem

$root = Split-Path $PSScriptRoot -Parent
foreach($name in @("ManifestPath","RejectionHistoryPath")) {
  $value = Get-Variable -Name $name -ValueOnly
  if(-not [IO.Path]::IsPathRooted($value)) { Set-Variable -Name $name -Value (Join-Path $root $value) }
}
if(-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)) { throw "FRODO_RPG_MANIFEST_MISSING path=$ManifestPath" }
if(-not (Test-Path -LiteralPath $RejectionHistoryPath -PathType Leaf)) { throw "FRODO_RPG_REJECTION_HISTORY_MISSING path=$RejectionHistoryPath" }

$manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
$history = Get-Content -LiteralPath $RejectionHistoryPath -Raw | ConvertFrom-Json
if(@($manifest.assets).Count -ne 1) { throw "FRODO_RPG_ASSET_COUNT_FAIL count=$(@($manifest.assets).Count)" }
$asset = $manifest.assets[0]
if(([string]$manifest.license).ToUpperInvariant() -ne "CC0-1.0") { throw "FRODO_RPG_LICENSE_FAIL" }
if(([string]$asset.required_final_format).ToUpperInvariant() -ne "FBX") { throw "FRODO_RPG_FORMAT_FAIL" }

if([string]::IsNullOrWhiteSpace($OutputRoot)) { $OutputRoot = Join-Path $env:RUNNER_TEMP "shire-frodo-rpg-gauntlet" }
$warehouse = Join-Path $OutputRoot "warehouse"
$extractRoot = Join-Path $OutputRoot "extracted"
New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null
New-Item -ItemType Directory -Path $warehouse -Force | Out-Null
if(Test-Path -LiteralPath $extractRoot) { Remove-Item -LiteralPath $extractRoot -Recurse -Force }
New-Item -ItemType Directory -Path $extractRoot -Force | Out-Null

& (Join-Path $root "Scripts\stage_opengameart_character_candidate.ps1") -ManifestPath $ManifestPath -WarehouseRoot $warehouse

$archive = Join-Path $warehouse ("OpenGameArt\Characters\" + [string]$asset.filename)
if(-not (Test-Path -LiteralPath $archive -PathType Leaf)) { throw "FRODO_RPG_ARCHIVE_MISSING path=$archive" }
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

function Get-IdentityScore {
  param([string]$Entry,[bool]$HasAnimation)
  $n = $Entry.ToLowerInvariant()
  $score = 0
  foreach($term in @("hobbit","small","short")) { if($n.Contains($term)) { $score += 35 } }
  foreach($term in @("male","rogue","ranger","adventurer","villager","worker")) { if($n.Contains($term)) { $score += 20 } }
  foreach($term in @("monk","archer","character","base","human")) { if($n.Contains($term)) { $score += 8 } }
  if($HasAnimation) { $score += 12 }
  foreach($term in @("female","goblin","zombie","skeleton","orc","monster","demon")) { if($n.Contains($term)) { $score -= 400 } }
  foreach($term in @("knight","soldier","viking","pirate","ninja")) { if($n.Contains($term)) { $score -= 35 } }
  return $score
}

$rows = @()
$zip = [IO.Compression.ZipFile]::OpenRead($archive)
try {
  $fbxEntries = @($zip.Entries | Where-Object { [IO.Path]::GetExtension($_.FullName).ToLowerInvariant() -eq ".fbx" })
  if($fbxEntries.Count -lt 1) { throw "FRODO_RPG_ARCHIVE_NO_FBX" }
  $index = 0
  foreach($entry in $fbxEntries) {
    if([int64]$entry.Length -gt 67108864) {
      Write-Host ("FRODO_RPG_FBX_SKIPPED_OVERSIZE entry="+$entry.FullName+" bytes="+$entry.Length)
      $index++
      continue
    }
    $safeName = ("{0:D4}_{1}" -f $index, ([IO.Path]::GetFileName($entry.FullName)))
    $temp = Join-Path $extractRoot $safeName
    [IO.Compression.ZipFileExtensions]::ExtractToFile($entry,$temp,$true)
    $bytes = [IO.File]::ReadAllBytes($temp)
    $ascii = [Text.Encoding]::ASCII.GetString($bytes)
    $version = Get-FbxVersion -Bytes $bytes -Ascii $ascii
    $sha = (Get-FileHash -LiteralPath $temp -Algorithm SHA256).Hash.ToLowerInvariant()
    $hasGeometry = $ascii.Contains("Geometry")
    $hasModel = $ascii.Contains("Model")
    $hasLimb = $ascii.Contains("LimbNode")
    $hasSkin = $ascii.Contains("Skin")
    $hasCluster = $ascii.Contains("Cluster")
    $hasAnim = $ascii.Contains("AnimationStack") -or $ascii.Contains("AnimationCurve")
    $knownRejected = $rejected.ContainsKey($sha)
    $versionOk = $version -gt 0 -and $version -le [int]$manifest.gauntlet.fbx_version_ceiling
    $staticPass = $versionOk -and $hasGeometry -and $hasModel -and $hasLimb -and $hasSkin -and $hasCluster -and (-not $knownRejected)
    $score = Get-IdentityScore -Entry ([string]$entry.FullName) -HasAnimation $hasAnim
    if($staticPass) { $score += 1000 }
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
      score = [int]$score
    }
    Write-Host ("FRODO_RPG_FBX entry="+$entry.FullName+" bytes="+$entry.Length+" sha256="+$sha+" version="+$version+" limb="+$hasLimb+" skin="+$hasSkin+" cluster="+$hasCluster+" anim="+$hasAnim+" knownRejected="+$knownRejected+" staticPass="+$staticPass+" score="+$score)
    $index++
  }
}
finally { $zip.Dispose() }

$max = [int]$manifest.gauntlet.maximum_ue4_candidates
$selected = @($rows | Where-Object { $_.static_pass } | Sort-Object -Property @{Expression="score";Descending=$true}, @{Expression="bytes";Descending=$false}, @{Expression="entry";Descending=$false} | Select-Object -First $max)
$receipt = [ordered]@{
  schema_version = 1
  status = if($selected.Count -gt 0){"STATIC_GAUNTLET_READY_FOR_UE4"}else{"REJECTED_STATIC_NO_COMPATIBLE_FBX"}
  archive_sha256 = $archiveSha
  archive_bytes = $archiveBytes
  fbx_scanned = $rows.Count
  static_pass_count = @($rows | Where-Object { $_.static_pass }).Count
  selected_count = $selected.Count
  selected_candidates = @($selected | Select-Object entry,bytes,extracted_path,sha256,fbx_version,animation,score)
  candidates = @($rows | Select-Object entry,bytes,sha256,fbx_version,geometry,model,limb_node,skin,cluster,animation,known_rejection,static_pass,score)
  runtime_integration_allowed = $false
  evidence_boundary = "Static identity/structure only. Selected candidates require the unchanged real UE4.27 skeletal technical gate."
}
$receiptPath = Join-Path $OutputRoot "p1c01_frodo_rpg_static_gauntlet.json"
$receipt | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $receiptPath -Encoding UTF8

if($selected.Count -lt 1) { throw "FRODO_RPG_STATIC_GAUNTLET_EMPTY receipt=$receiptPath" }
Write-Host ("FRODO_RPG_STATIC_GAUNTLET_PASS archiveSha256="+$archiveSha+" archiveBytes="+$archiveBytes+" scanned="+$rows.Count+" staticPass="+$receipt.static_pass_count+" selected="+$selected.Count+" receipt="+$receiptPath)
foreach($row in $selected) { Write-Host ("FRODO_RPG_SELECTED entry="+$row.entry+" sha256="+$row.sha256+" bytes="+$row.bytes+" version="+$row.fbx_version+" score="+$row.score) }
