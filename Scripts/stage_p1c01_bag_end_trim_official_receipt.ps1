param(
  [string]$ManifestPath = "Data/P1C01BagEndHeroTrimSourceProbeV1.json",
  [string]$OutputRoot = ""
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$root = Split-Path $PSScriptRoot -Parent
if(-not [IO.Path]::IsPathRooted($ManifestPath)){ $ManifestPath = Join-Path $root $ManifestPath }
if(-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)){ throw "BAG_END_TRIM_MANIFEST_MISSING path=$ManifestPath" }
$m = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
$url = [string]$m.official_staging_plan.official_download_url
if([string]::IsNullOrWhiteSpace($url) -or -not $url.StartsWith("https://kenney.nl/")){ throw "BAG_END_TRIM_OFFICIAL_URL_FAIL url=$url" }
if([string]::IsNullOrWhiteSpace($OutputRoot)){ $OutputRoot = Join-Path $env:RUNNER_TEMP "shire-bag-end-trim-official" }
New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null
$zip = Join-Path $OutputRoot "kenney_building-kit.zip"
$extract = Join-Path $OutputRoot "extract"
if(Test-Path -LiteralPath $zip){ Remove-Item -LiteralPath $zip -Force }
if(Test-Path -LiteralPath $extract){ Remove-Item -LiteralPath $extract -Recurse -Force }

Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $zip -TimeoutSec 180
$f = Get-Item -LiteralPath $zip
if($f.Length -lt 100000){ throw "BAG_END_TRIM_ARCHIVE_TOO_SMALL bytes=$($f.Length)" }
$archiveSha=(Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash.ToLowerInvariant()
Expand-Archive -LiteralPath $zip -DestinationPath $extract -Force

$expected=@{}
foreach($row in @($m.exact_file_discovery.candidate_files)){
  $expected[[string]$row.file]=([string]$row.payload_sha256).ToLowerInvariant()
}
$subset=@($m.exact_file_discovery.primary_static_qc_subset | ForEach-Object { [string]$_ })
$rows=@()
foreach($name in $subset){
  $matches=@(Get-ChildItem -LiteralPath $extract -Recurse -File | Where-Object { $_.Name -ieq $name })
  if($matches.Count -lt 1){ throw "BAG_END_TRIM_CANDIDATE_MISSING file=$name" }
  $exp=[string]$expected[$name]
  if([string]::IsNullOrWhiteSpace($exp)){ throw "BAG_END_TRIM_EXPECTED_HASH_MISSING file=$name" }

  $matched=@()
  foreach($candidate in $matches){
    $candidateSha=(Get-FileHash -LiteralPath $candidate.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    if($candidateSha -eq $exp){
      $matched += [pscustomobject]@{ item=$candidate; sha=$candidateSha }
    }
  }
  if($matched.Count -lt 1){
    throw "BAG_END_TRIM_EXPECTED_HASH_MATCH_MISSING file=$name discovered=$($matches.Count)"
  }
  $item=$matched[0].item
  $sha=[string]$matched[0].sha
  $rows += [ordered]@{ file=$name; relative_path=$item.FullName.Substring($extract.Length).TrimStart('\'); bytes=[int64]$item.Length; sha256=$sha; match=$true; identical_match_count=[int]$matched.Count }
  Write-Host "BAG_END_TRIM_OFFICIAL_FILE_MATCH file=$name bytes=$($item.Length) sha256=$sha identicalMatches=$($matched.Count) path=$($item.FullName)"
}
$receipt=[ordered]@{
  schema_version=1
  source_page=[string]$m.exact_file_discovery.official_source_authority.source_page
  download_url=$url
  archive_bytes=[int64]$f.Length
  archive_sha256=$archiveSha
  candidate_files=$rows
  candidate_hash_match=$true
}
$receiptPath=Join-Path $OutputRoot "p1c01_bag_end_trim_official_receipt.json"
$receipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $receiptPath -Encoding UTF8
Write-Host "BAG_END_TRIM_OFFICIAL_RECEIPT_PASS archiveBytes=$($f.Length) archiveSha256=$archiveSha candidates=$($rows.Count) receipt=$receiptPath"
