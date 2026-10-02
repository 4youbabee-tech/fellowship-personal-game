param(
  [Parameter(Mandatory=$true)][string]$CandidateReport,
  [Parameter(Mandatory=$true)][string]$StaticQcReport,
  [Parameter(Mandatory=$true)][string]$Workspace,
  [string]$ManifestPath = "Data/P1C01FrodoSkeletalImportV1.json"
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot=Split-Path $PSScriptRoot -Parent
if(-not [IO.Path]::IsPathRooted($ManifestPath)){ $ManifestPath=Join-Path $ProjectRoot $ManifestPath }
foreach($path in @($CandidateReport,$StaticQcReport,$ManifestPath)){
  if(-not (Test-Path -LiteralPath $path -PathType Leaf)){ throw "P1C01_FRODO_IMPORT_INPUT_MISSING path=$path" }
}
if(-not (Test-Path -LiteralPath $Workspace -PathType Container)){ throw "P1C01_FRODO_IMPORT_WORKSPACE_MISSING root=$Workspace" }

$manifest=Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
$candidate=Get-Content -LiteralPath $CandidateReport -Raw | ConvertFrom-Json
$static=Get-Content -LiteralPath $StaticQcReport -Raw | ConvertFrom-Json

if([string]$manifest.character -ne "FRODO"){ throw "P1C01_FRODO_IMPORT_MANIFEST_CHARACTER_FAIL" }
if([string]$static.character -ne "FRODO"){ throw "P1C01_FRODO_IMPORT_STATIC_CHARACTER_FAIL" }

$frodoRows=@($candidate.characters | Where-Object { [string]$_.character -eq "FRODO" })
if($frodoRows.Count -ne 1){ throw "P1C01_FRODO_IMPORT_POOL_FAIL count=$($frodoRows.Count)" }

$selected=$null
$technicalRejections=@()
if($null -ne $manifest.PSObject.Properties["technical_rejections"]){
  $technicalRejections=@($manifest.technical_rejections)
}
$appliedRejections=@()
foreach($preferred in @($manifest.preferred_candidate_order)){
  $qc=@($static.candidates | Where-Object { [string]$_.filename -ieq [string]$preferred -and [bool]$_.static_structure_pass })
  if($qc.Count -ne 1){ continue }

  $qcSha=([string]$qc[0].sha256).ToLowerInvariant()
  $rejections=@($technicalRejections | Where-Object {
    [string]$_.filename -ieq [string]$preferred -and
    ([string]$_.source_sha256).ToLowerInvariant() -eq $qcSha
  })
  if($rejections.Count -gt 0){
    $appliedRejections += [string]$preferred
    Write-Host ("P1C01_FRODO_IMPORT_SKIP_TECHNICAL_REJECTION file="+[string]$preferred+" sha256="+$qcSha+" state="+[string]$rejections[0].state)
    continue
  }

  $candidateRows=@($frodoRows[0].candidates | Where-Object { [string]$_.filename -ieq [string]$preferred })
  if($candidateRows.Count -ne 1){ continue }
  $source=[string]$candidateRows[0].source_fbx
  if(-not (Test-Path -LiteralPath $source -PathType Leaf)){ continue }
  $sha=(Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant()
  if($sha -ne $qcSha){ throw "P1C01_FRODO_IMPORT_HASH_MISMATCH file=$preferred" }
  $selected=[pscustomobject]@{ filename=[string]$preferred; source=$source; sha256=$sha; bytes=(Get-Item -LiteralPath $source).Length }
  break
}
if($null -eq $selected){
  $preferredSourceIds=@()
  if($null -ne $manifest.PSObject.Properties["preferred_candidate_source_asset_ids"]){
    $preferredSourceIds=@($manifest.preferred_candidate_source_asset_ids | ForEach-Object { [string]$_ })
  }
  foreach($sourceId in $preferredSourceIds){
    $sourceCandidates=@($frodoRows[0].candidates | Where-Object { [string]$_.source_asset_id -ieq $sourceId } | Sort-Object -Property @{Expression="score";Descending=$true}, @{Expression="bytes";Descending=$false})
    foreach($candidateRow in $sourceCandidates){
      $preferred=[string]$candidateRow.filename
      $source=[string]$candidateRow.source_fbx
      if(-not (Test-Path -LiteralPath $source -PathType Leaf)){ continue }
      $sha=(Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant()
      $qc=@($static.candidates | Where-Object {
        [string]$_.filename -ieq $preferred -and
        [string]$_.source_asset_id -ieq $sourceId -and
        ([string]$_.sha256).ToLowerInvariant() -eq $sha -and
        [bool]$_.static_structure_pass
      })
      if($qc.Count -ne 1){ continue }
      $rejections=@($technicalRejections | Where-Object {
        [string]$_.filename -ieq $preferred -and
        ([string]$_.source_sha256).ToLowerInvariant() -eq $sha
      })
      if($rejections.Count -gt 0){
        $appliedRejections += $preferred
        Write-Host ("P1C01_FRODO_IMPORT_SKIP_TECHNICAL_REJECTION file="+$preferred+" sha256="+$sha+" state="+[string]$rejections[0].state)
        continue
      }
      $selected=[pscustomobject]@{ filename=$preferred; source=$source; sha256=$sha; bytes=(Get-Item -LiteralPath $source).Length }
      break
    }
    if($null -ne $selected){ break }
  }
}
if($null -eq $selected){ throw "P1C01_FRODO_IMPORT_NO_STATIC_VALIDATED_NONREJECTED_CANDIDATE" }

$relative=[string]$manifest.temporary_source_destination
$destination=Join-Path $Workspace ($relative -replace '/','\')
$parent=Split-Path $destination -Parent
New-Item -ItemType Directory -Path $parent -Force | Out-Null
Copy-Item -LiteralPath $selected.source -Destination $destination -Force
$destSha=(Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLowerInvariant()
if($destSha -ne $selected.sha256){ throw "P1C01_FRODO_IMPORT_COPY_HASH_MISMATCH" }

$receiptRoot=Join-Path $Workspace "Saved\P1C01FrodoImport"
New-Item -ItemType Directory -Path $receiptRoot -Force | Out-Null
$receipt=[ordered]@{
  schema_version=1
  import_id=[string]$manifest.import_id
  character="FRODO"
  selected_filename=[string]$selected.filename
  selected_sha256=[string]$selected.sha256
  selected_bytes=[int64]$selected.bytes
  technical_rejections_applied=@($appliedRejections)
  staged_relative_path=$relative
  unreal_destination=[string]$manifest.unreal_destination
  unreal_asset_name=[string]$manifest.unreal_asset_name
  state="TEMP_SOURCE_STAGED_FOR_UE4_SKELETAL_IMPORT"
  runtime_integration_allowed=$false
  evidence_boundary=[string]$manifest.evidence_boundary
}
$receiptPath=Join-Path $receiptRoot "frodo_skeletal_import_staging_receipt.json"
$receipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $receiptPath -Encoding UTF8
Write-Host ("P1C01_FRODO_IMPORT_STAGE_PASS file="+$selected.filename+" bytes="+$selected.bytes+" sha256="+$selected.sha256+" destination="+$destination+" receipt="+$receiptPath)
exit 0
