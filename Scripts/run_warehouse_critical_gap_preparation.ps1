param(
  [string]$ManifestPath = "Data/WarehouseCriticalGapPreparationTrainV2.json",
  [string]$WarehouseRoot = "C:\actions-runner\_warehouse\ShireJourney",
  [string]$OutputRoot = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path $PSScriptRoot -Parent
if ([string]::IsNullOrWhiteSpace($OutputRoot)) {
  $OutputRoot = Join-Path $WarehouseRoot "_prepared_v2"
}
if (-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)) {
  $candidate = Join-Path $ProjectRoot $ManifestPath
  if (Test-Path -LiteralPath $candidate -PathType Leaf) { $ManifestPath = $candidate }
}
if (-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)) {
  throw "Critical-gap manifest missing: $ManifestPath"
}

$manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null
$ExpandedRoot = Join-Path $OutputRoot "expanded"
New-Item -ItemType Directory -Path $ExpandedRoot -Force | Out-Null

function Get-SizeSum {
  param([object[]]$Items)
  [int64]$total=0
  foreach($item in $Items){$total += [int64]$item.size}
  return $total
}

function Get-OptionalPropertyValue {
  param(
    [object]$Object,
    [string]$Name,
    [object]$Default = $null
  )
  if ($null -eq $Object) { return $Default }
  $prop = $Object.PSObject.Properties[$Name]
  if ($null -eq $prop) { return $Default }
  return $prop.Value
}

$dangerous = @(".exe",".msi",".cmd",".bat",".ps1",".vbs",".js",".scr",".com")
$audioExt = @(".wav",".ogg",".mp3",".flac")
$textureExt = @(".png",".tga",".jpg",".jpeg",".bmp",".exr",".hdr")
$meshExt = @(".fbx",".obj",".gltf",".glb",".blend")
$archiveExt = @(".zip",".7z",".rar")

$receiptRows = @()
$badReceipts = @()
if (Test-Path -LiteralPath $WarehouseRoot -PathType Container) {
  foreach ($receiptFile in @(Get-ChildItem -LiteralPath $WarehouseRoot -Recurse -File -Filter "receipt_*.json")) {
    try { $receipt = Get-Content -LiteralPath $receiptFile.FullName -Raw | ConvertFrom-Json }
    catch {
      $badReceipts += [ordered]@{ receipt=$receiptFile.FullName; reason="invalid_json"; detail=$_.Exception.Message }
      continue
    }

    $receiptProvider=[string](Get-OptionalPropertyValue -Object $receipt -Name "provider" -Default "")
    $receiptBatchId=[string](Get-OptionalPropertyValue -Object $receipt -Name "batch_id" -Default "")
    $receiptItems=@(Get-OptionalPropertyValue -Object $receipt -Name "files" -Default @())

    foreach ($row in $receiptItems) {
      $path = [string](Get-OptionalPropertyValue -Object $row -Name "file" -Default "")
      $declared = ([string](Get-OptionalPropertyValue -Object $row -Name "sha256" -Default "")).ToLowerInvariant()
      if ([string]::IsNullOrWhiteSpace($path)) {
        $path = [string](Get-OptionalPropertyValue -Object $row -Name "archive" -Default "")
        $declared = ([string](Get-OptionalPropertyValue -Object $row -Name "archive_sha256" -Default "")).ToLowerInvariant()
      }
      if ([string]::IsNullOrWhiteSpace($path)) { continue }

      $rowState=[string](Get-OptionalPropertyValue -Object $row -Name "state" -Default "STAGED")
      if([string]::IsNullOrWhiteSpace($rowState)){$rowState="STAGED"}

      $receiptRows += [pscustomobject]@{
        provider=$receiptProvider
        batch_id=$receiptBatchId
        asset_id=[string](Get-OptionalPropertyValue -Object $row -Name "asset_id" -Default "")
        asset_slug=[string](Get-OptionalPropertyValue -Object $row -Name "asset_slug" -Default "")
        category=[string](Get-OptionalPropertyValue -Object $row -Name "category" -Default "")
        path=$path
        declared_sha256=$declared
        source_page=[string](Get-OptionalPropertyValue -Object $row -Name "source_page" -Default "")
        state=$rowState
        receipt_file=$receiptFile.FullName
      }
    }
  }
}

$verified=@(); $blocked=@(); $pending=@()
foreach($row in $receiptRows){
  if(-not (Test-Path -LiteralPath $row.path -PathType Leaf)){
    $blocked += [ordered]@{provider=$row.provider;asset_id=$row.asset_id;path=$row.path;reason="receipt_file_missing"}
    continue
  }
  $actual=(Get-FileHash -LiteralPath $row.path -Algorithm SHA256).Hash.ToLowerInvariant()
  if([string]::IsNullOrWhiteSpace($row.declared_sha256) -or $actual -ne $row.declared_sha256){
    $blocked += [ordered]@{provider=$row.provider;asset_id=$row.asset_id;path=$row.path;reason="receipt_sha256_mismatch";expected=$row.declared_sha256;actual=$actual}
    continue
  }
  $file=Get-Item -LiteralPath $row.path
  $verified += [pscustomobject]@{
    provider=$row.provider;batch_id=$row.batch_id;asset_id=$row.asset_id;asset_slug=$row.asset_slug;
    category=$row.category;path=$row.path;extension=$file.Extension.ToLowerInvariant();
    size=[int64]$file.Length;sha256=$actual;source_page=$row.source_page;receipt_file=$row.receipt_file
  }
}

$scanFiles = New-Object 'System.Collections.Generic.List[object]'
foreach($row in $verified){
  $ext=$row.extension
  if($dangerous -contains $ext){
    $blocked += [ordered]@{provider=$row.provider;asset_id=$row.asset_id;path=$row.path;reason="dangerous_payload_extension"}
    continue
  }
  if($ext -eq ".zip"){
    $safeId=if(-not [string]::IsNullOrWhiteSpace($row.asset_id)){$row.asset_id}else{[IO.Path]::GetFileNameWithoutExtension($row.path)}
    $dest=Join-Path $ExpandedRoot (($row.provider+"_"+$safeId) -replace '[^A-Za-z0-9_.-]','_')
    if(Test-Path -LiteralPath $dest){Remove-Item -LiteralPath $dest -Recurse -Force}
    New-Item -ItemType Directory -Path $dest -Force | Out-Null
    try{
      Expand-Archive -LiteralPath $row.path -DestinationPath $dest -Force
      foreach($x in @(Get-ChildItem -LiteralPath $dest -Recurse -File)){
        $scanFiles.Add([pscustomobject]@{
          provider=$row.provider;asset_id=$row.asset_id;category=$row.category;source_page=$row.source_page;
          source_archive=$row.path;path=$x.FullName;extension=$x.Extension.ToLowerInvariant();size=[int64]$x.Length
        })
      }
    }catch{
      $blocked += [ordered]@{provider=$row.provider;asset_id=$row.asset_id;path=$row.path;reason="archive_extract_failed";detail=$_.Exception.Message}
    }
  }
  elseif($ext -in @(".7z",".rar")){
    $pending += [ordered]@{provider=$row.provider;asset_id=$row.asset_id;path=$row.path;reason="archive_requires_approved_extractor"}
  }
  else{
    $scanFiles.Add([pscustomobject]@{
      provider=$row.provider;asset_id=$row.asset_id;category=$row.category;source_page=$row.source_page;
      source_archive="";path=$row.path;extension=$ext;size=$row.size
    })
  }
}

$inventory=@()
foreach($f in $scanFiles){
  $ext=$f.extension
  if($dangerous -contains $ext){
    $blocked += [ordered]@{provider=$f.provider;asset_id=$f.asset_id;path=$f.path;reason="dangerous_extracted_extension"}
    continue
  }
  if($ext -eq ".bmp"){
    $blocked += [ordered]@{provider=$f.provider;asset_id=$f.asset_id;path=$f.path;reason="forbidden_bmp"}
    continue
  }

  $name=[IO.Path]::GetFileNameWithoutExtension($f.path).ToLowerInvariant()
  $role="OTHER"
  if($ext -eq ".fbx"){
    if($name -match 'anim|walk|run|idle|attack|jump|turn|sit|mount|death|hit'){ $role="FBX_ANIMATION_CANDIDATE" }
    elseif($name -match 'character|human|hobbit|wizard|dwarf|orc|uruk|skeleton'){ $role="FBX_CHARACTER_CANDIDATE" }
    elseif($name -match 'animal|horse|pony|cow|sheep|pig|dog|wolf|warg|spider|eagle|troll|monster'){ $role="FBX_CREATURE_FAUNA_CANDIDATE" }
    else { $role="FBX_STATIC_MESH_CANDIDATE" }
  }
  elseif($ext -in @(".obj",".gltf",".glb",".blend")){ $role="MESH_CONVERSION_DEBT" }
  elseif($ext -in @(".png",".tga")){
    if($name -match 'normal|_n$|nor'){ $role="TEXTURE_NORMAL" }
    elseif($name -match 'rough'){ $role="TEXTURE_ROUGHNESS" }
    elseif($name -match 'metal'){ $role="TEXTURE_METALLIC" }
    elseif($name -match 'ao|ambientocclusion'){ $role="TEXTURE_AO" }
    elseif($name -match 'height|disp'){ $role="TEXTURE_HEIGHT_SOURCE" }
    else { $role="TEXTURE_COLOR_OR_UI" }
  }
  elseif($ext -in @(".jpg",".jpeg",".exr",".hdr")){ $role="TEXTURE_OR_HDR_SOURCE_DEBT" }
  elseif($ext -eq ".wav"){ $role="AUDIO_WAV_MASTER_CANDIDATE" }
  elseif($ext -in @(".ogg",".mp3",".flac")){ $role="AUDIO_CONVERSION_DEBT" }
  elseif($ext -in @(".svg",".ttf",".otf")){ $role="UI_FONT_VECTOR_SUPPORT" }
  elseif($ext -in @(".r16",".raw",".tif",".tiff")){ $role="TERRAIN_HEIGHTMAP_SOURCE" }

  $inventory += [pscustomobject]@{
    provider=$f.provider;asset_id=$f.asset_id;category=$f.category;path=$f.path;
    extension=$ext;size=[int64]$f.size;role=$role;source_page=$f.source_page
  }
}

$roleSummary=@($inventory | Group-Object role | Sort-Object Name | ForEach-Object{
  [ordered]@{role=$_.Name;files=$_.Count;bytes=(Get-SizeSum -Items @($_.Group))}
})
$providerSummary=@($inventory | Group-Object provider | Sort-Object Name | ForEach-Object{
  [ordered]@{provider=$_.Name;files=$_.Count;bytes=(Get-SizeSum -Items @($_.Group))}
})

$cars=@()
foreach($car in @($manifest.cars|Sort-Object order)){
  $matchRoles=@()
  switch -Wildcard ([string]$car.scope) {
    "CHARACTER" {$matchRoles=@("FBX_CHARACTER_CANDIDATE")}
    "ANIMATION" {$matchRoles=@("FBX_ANIMATION_CANDIDATE")}
    "CREATURE_FAUNA" {$matchRoles=@("FBX_CREATURE_FAUNA_CANDIDATE")}
    "STATIC_3D" {$matchRoles=@("FBX_STATIC_MESH_CANDIDATE","MESH_CONVERSION_DEBT")}
    "ARCHITECTURE" {$matchRoles=@("FBX_STATIC_MESH_CANDIDATE","MESH_CONVERSION_DEBT")}
    "PROPS_INTERIOR" {$matchRoles=@("FBX_STATIC_MESH_CANDIDATE","MESH_CONVERSION_DEBT")}
    "VEGETATION" {$matchRoles=@("FBX_STATIC_MESH_CANDIDATE","MESH_CONVERSION_DEBT","TEXTURE_COLOR_OR_UI")}
    "MATERIAL" {$matchRoles=@("TEXTURE_NORMAL","TEXTURE_ROUGHNESS","TEXTURE_METALLIC","TEXTURE_AO","TEXTURE_HEIGHT_SOURCE","TEXTURE_COLOR_OR_UI")}
    "TEXTURE" {$matchRoles=@("TEXTURE_NORMAL","TEXTURE_ROUGHNESS","TEXTURE_METALLIC","TEXTURE_AO","TEXTURE_HEIGHT_SOURCE","TEXTURE_COLOR_OR_UI","TEXTURE_OR_HDR_SOURCE_DEBT")}
    "AUDIO" {$matchRoles=@("AUDIO_WAV_MASTER_CANDIDATE","AUDIO_CONVERSION_DEBT")}
    "UI" {$matchRoles=@("TEXTURE_COLOR_OR_UI","UI_FONT_VECTOR_SUPPORT")}
    "TERRAIN" {$matchRoles=@("TERRAIN_HEIGHTMAP_SOURCE","TEXTURE_OR_HDR_SOURCE_DEBT")}
    default {$matchRoles=@($inventory.role|Select-Object -Unique)}
  }
  $matches=@($inventory|Where-Object{$matchRoles -contains $_.role})
  $cars += [ordered]@{
    order=[int]$car.order;id=[string]$car.id;scope=[string]$car.scope;goal=[string]$car.goal;
    matched_files=$matches.Count;matched_bytes=(Get-SizeSum -Items $matches);
    state=if($matches.Count -gt 0){"INTAKE_QC_DATA_PRESENT"}else{"PENDING_SOURCE_OR_CLASSIFICATION"};
    ceiling="INTAKE_QC"
  }
}

$report=[ordered]@{
  schema_version=1;train_id=[string]$manifest.train_id;generated_at_utc=[DateTime]::UtcNow.ToString("o");
  receipt_records=$receiptRows.Count;verified_receipts=$verified.Count;bad_receipts=$badReceipts;
  blocked=$blocked;pending=$pending;inventory_file_count=$inventory.Count;
  provider_summary=$providerSummary;role_summary=$roleSummary;cars=$cars;
  rules=@(
    "No file is promoted to READY_FOR_IMPORT by this report.",
    "Character/creature FBX classification is filename/format triage only, not proof of skeleton, skin or deformation quality.",
    "Visual/canon/PIE/device/performance acceptance remains open."
  )
}
$manualQueue=@()
foreach($entry in $blocked){
  $manualQueue += [ordered]@{queue="BLOCKED_ASSET_REVIEW";provider=$entry.provider;asset_id=$entry.asset_id;path=$entry.path;reason=$entry.reason;detail=(Get-OptionalPropertyValue -Object $entry -Name "detail" -Default "")}
}
foreach($entry in $pending){
  $manualQueue += [ordered]@{queue="PENDING_APPROVED_TOOLING";provider=$entry.provider;asset_id=$entry.asset_id;path=$entry.path;reason=$entry.reason}
}
foreach($entry in $badReceipts){
  $manualQueue += [ordered]@{queue="RECEIPT_REVIEW";receipt=$entry.receipt;reason=$entry.reason;detail=$entry.detail}
}

$report.outcome=if($manualQueue.Count -gt 0){"PASS_WITH_MANUAL_QUEUE"}else{"PASS"}
$report.manual_queue_count=$manualQueue.Count
$report.manual_queue=$manualQueue
$outPath=Join-Path $OutputRoot "warehouse_critical_gap_preparation_latest.json"
$report|ConvertTo-Json -Depth 12|Set-Content -LiteralPath $outPath -Encoding UTF8

if($manualQueue.Count -gt 0){
  Write-Host ("WAREHOUSE_CRITICAL_GAP_PREP_PASS_WITH_MANUAL_QUEUE verified="+$verified.Count+" inventory="+$inventory.Count+" blocked="+$blocked.Count+" badReceipts="+$badReceipts.Count+" pending="+$pending.Count+" manualQueue="+$manualQueue.Count+" report="+$outPath)
  foreach($entry in $manualQueue){Write-Host ("WAREHOUSE_CRITICAL_GAP_MANUAL_QUEUE "+($entry|ConvertTo-Json -Compress -Depth 6))}
}
else{
  Write-Host ("WAREHOUSE_CRITICAL_GAP_PREP_PASS verified="+$verified.Count+" inventory="+$inventory.Count+" pending=0 manualQueue=0 report="+$outPath)
}
