param(
  [string]$ManifestPath = "Data/P1C01OpenGameArtHeroCandidateBatchV1.json",
  [string]$WarehouseRoot = "D:\actions-runner\_warehouse\ShireJourney"
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Add-Type -AssemblyName System.IO.Compression.FileSystem

$ProjectRoot = Split-Path $PSScriptRoot -Parent
if(-not [IO.Path]::IsPathRooted($ManifestPath)){ $ManifestPath = Join-Path $ProjectRoot $ManifestPath }
if(-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)){ throw "OGA_CHARACTER_MANIFEST_MISSING path=$ManifestPath" }
$manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
$assets = @($manifest.assets)
if($assets.Count -ne 1){ throw "OGA_CHARACTER_BOUNDED_ASSET_COUNT_FAIL count=$($assets.Count)" }
$asset = $assets[0]
if(([string]$asset.observed_page_license).ToUpperInvariant() -ne "CC0"){ throw "OGA_CHARACTER_LICENSE_FAIL" }
if(([string]$asset.required_final_format).ToUpperInvariant() -ne "FBX"){ throw "OGA_CHARACTER_FORMAT_FAIL" }
$payloadKind="ARCHIVE_ZIP"
if($null -ne $asset.PSObject.Properties["download_kind"]){ $payloadKind=([string]$asset.download_kind).ToUpperInvariant() }
elseif([IO.Path]::GetExtension([string]$asset.filename).ToLowerInvariant() -eq ".fbx"){ $payloadKind="DIRECT_FBX" }
if($payloadKind -notin @("ARCHIVE_ZIP","DIRECT_FBX")){ throw "OGA_CHARACTER_PAYLOAD_KIND_FAIL kind=$payloadKind" }

$archiveMinimumBytesDefault=[int64]1048576
$archiveMinimumBytesFloor=[int64]262144
$archiveMinimumBytes=$archiveMinimumBytesDefault
if($null -ne $asset.PSObject.Properties["minimum_archive_bytes"]){
  $archiveMinimumBytes=[int64]$asset.minimum_archive_bytes
}
if($archiveMinimumBytes -lt $archiveMinimumBytesFloor -or $archiveMinimumBytes -gt 104857600){
  throw "OGA_CHARACTER_ARCHIVE_MINIMUM_INVALID bytes=$archiveMinimumBytes floor=$archiveMinimumBytesFloor ceiling=104857600"
}

$stageRoot = Join-Path $WarehouseRoot "OpenGameArt\Characters"
New-Item -ItemType Directory -Path $stageRoot -Force | Out-Null
$archivePath = Join-Path $stageRoot ([string]$asset.filename)
$receiptPath = Join-Path $stageRoot ("receipt_"+[string]$manifest.batch_id+".json")
$partialPath = $archivePath+".partial"

function Test-CandidateArchive {
  param([string]$Path,[int64]$MinimumBytes)
  if(-not (Test-Path -LiteralPath $Path -PathType Leaf)){ throw "OGA_CHARACTER_ARCHIVE_MISSING path=$Path" }
  $file = Get-Item -LiteralPath $Path
  if($file.Length -lt $MinimumBytes){ throw "OGA_CHARACTER_ARCHIVE_TOO_SMALL bytes=$($file.Length) required=$MinimumBytes" }
  $zip = [IO.Compression.ZipFile]::OpenRead($Path)
  try {
    $entryCount=0; $fbxCount=0; $totalBytes=[int64]0
    $dangerous=@(".exe",".msi",".cmd",".bat",".ps1",".vbs",".js",".scr",".com")
    foreach($entry in $zip.Entries){
      $entryCount++
      $entryName=$entry.FullName.Replace([char]92,'/')
      $parts=@($entryName.Split('/') | Where-Object { $_ -ne '' })
      if($entryCount -gt 20000 -or $entry.Length -gt 536870912 -or ($totalBytes+$entry.Length) -gt 2147483648){ throw "OGA_CHARACTER_ARCHIVE_BUDGET_FAIL" }
      if($entryName.StartsWith('/') -or $entryName -match '^[A-Za-z]:' -or @($parts | Where-Object { $_ -eq '..' }).Count -gt 0){ throw "OGA_CHARACTER_ARCHIVE_PATH_UNSAFE entry=$entryName" }
      $ext=[IO.Path]::GetExtension($entryName).ToLowerInvariant()
      if($dangerous -contains $ext -or $ext -eq ".bmp"){ throw "OGA_CHARACTER_ARCHIVE_EXTENSION_FORBIDDEN entry=$entryName" }
      if($ext -eq ".fbx"){ $fbxCount++ }
      $totalBytes += [int64]$entry.Length
    }
    if($fbxCount -lt 1){ throw "OGA_CHARACTER_ARCHIVE_FBX_MISSING" }
    return [ordered]@{entry_count=$entryCount;fbx_count=$fbxCount;expanded_bytes=$totalBytes}
  } finally { $zip.Dispose() }
}

function Test-DirectFbx {
  param([string]$Path)
  if(-not (Test-Path -LiteralPath $Path -PathType Leaf)){ throw "OGA_CHARACTER_DIRECT_FBX_MISSING path=$Path" }
  $file=Get-Item -LiteralPath $Path
  if($file.Length -lt 1048576){ throw "OGA_CHARACTER_DIRECT_FBX_TOO_SMALL bytes=$($file.Length)" }
  $stream=[IO.File]::OpenRead($Path)
  try {
    $buffer=New-Object byte[] 96
    $count=$stream.Read($buffer,0,$buffer.Length)
    $header=[Text.Encoding]::ASCII.GetString($buffer,0,$count)
    if(-not ($header.StartsWith("Kaydara FBX Binary") -or $header.Contains("FBXHeaderExtension"))){
      throw "OGA_CHARACTER_DIRECT_FBX_HEADER_FAIL"
    }
  } finally { $stream.Dispose() }
  return [ordered]@{entry_count=1;fbx_count=1;expanded_bytes=[int64]$file.Length;payload_kind="DIRECT_FBX"}
}

function Test-CandidatePayload {
  param([string]$Path,[string]$Kind)
  if($Kind -eq "DIRECT_FBX"){ return Test-DirectFbx -Path $Path }
  $scan=Test-CandidateArchive -Path $Path -MinimumBytes $archiveMinimumBytes
  $scan["payload_kind"]="ARCHIVE_ZIP"
  return $scan
}

$reuse=$false
if((Test-Path -LiteralPath $archivePath -PathType Leaf) -and (Test-Path -LiteralPath $receiptPath -PathType Leaf)){
  try {
    $old=Get-Content -LiteralPath $receiptPath -Raw | ConvertFrom-Json
    $oldRows=@($old.files)
    if($oldRows.Count -eq 1 -and [string]$oldRows[0].asset_id -eq [string]$asset.id){
      $actual=(Get-FileHash -LiteralPath $archivePath -Algorithm SHA256).Hash.ToLowerInvariant()
      $expected=([string]$oldRows[0].sha256).ToLowerInvariant()
      if($actual -eq $expected -and -not [string]::IsNullOrWhiteSpace($expected)){
        $scan=Test-CandidatePayload -Path $archivePath -Kind $payloadKind
        $reuse=$true
        Write-Host "OGA_CHARACTER_REUSE_PASS asset=$($asset.id) sha256=$actual fbx=$($scan.fbx_count)"
      }
    }
  } catch {
    Write-Warning ("OGA character reuse rejected: "+$_.Exception.Message)
  }
}
if(-not $reuse){
  if(Test-Path -LiteralPath $partialPath){ Remove-Item -LiteralPath $partialPath -Force }
  if(Test-Path -LiteralPath $archivePath){ Remove-Item -LiteralPath $archivePath -Force }
  $downloaded=$false
  for($attempt=1;$attempt -le 3;$attempt++){
    try {
      Write-Host "OGA_CHARACTER_DOWNLOAD_BEGIN asset=$($asset.id) attempt=$attempt/3"
      Invoke-WebRequest -UseBasicParsing -Uri ([string]$asset.download_url) -OutFile $partialPath -TimeoutSec 180
      Move-Item -LiteralPath $partialPath -Destination $archivePath -Force
      $downloaded=$true
      break
    } catch {
      if(Test-Path -LiteralPath $partialPath){ Remove-Item -LiteralPath $partialPath -Force }
      if(Test-Path -LiteralPath $archivePath){ Remove-Item -LiteralPath $archivePath -Force }
      if($attempt -eq 3){ throw }
      Start-Sleep -Seconds (3*$attempt)
    }
  }
  if(-not $downloaded){ throw "OGA_CHARACTER_DOWNLOAD_FAIL asset=$($asset.id)" }
  $scan=Test-CandidatePayload -Path $archivePath -Kind $payloadKind
}

$sha=(Get-FileHash -LiteralPath $archivePath -Algorithm SHA256).Hash.ToLowerInvariant()
$file=Get-Item -LiteralPath $archivePath
$receipt=[ordered]@{
 schema_version=1
 batch_id=[string]$manifest.batch_id
 provider=[string]$manifest.provider
 creator=[string]$manifest.creator
 license=[string]$manifest.license
 staged_at_utc=[DateTime]::UtcNow.ToString("o")
 state=if($reuse){"REUSED_VERIFIED_PAYLOAD"}else{"STAGED_VERIFIED_PAYLOAD"}
 payload_kind=$payloadKind
 files=@([ordered]@{
  asset_id=[string]$asset.id
  file=$archivePath
  sha256=$sha
  bytes=[int64]$file.Length
  source_page=[string]$asset.source_page
  source_url=[string]$asset.download_url
  source_author=[string]$asset.source_author
  license=[string]$manifest.license
  archive_entries=[int]$scan.entry_count
  archive_fbx_count=[int]$scan.fbx_count
 })
}
$receipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $receiptPath -Encoding UTF8
Write-Host "OGA_CHARACTER_STAGE_PASS asset=$($asset.id) kind=$payloadKind reuse=$reuse bytes=$($file.Length) sha256=$sha fbx=$($scan.fbx_count) receipt=$receiptPath"
