$ErrorActionPreference="Stop"
Set-StrictMode -Version Latest
$root=Split-Path -Parent $PSScriptRoot
$manifest=Join-Path $root "Data\P1C01FrodoSkeletalImportV1.json"
$stage=Join-Path $root "Scripts\prepare_p1c01_frodo_skeletal_import.ps1"
$cpp=Join-Path $root "Source\ShireJourneyEditorTools\Private\ShireProductionImportCommandlet.cpp"
$workflow=Join-Path $root ".github\workflows\p1c01-frodo-skeletal-import-validation.yml"
$importCmd=Join-Path $root "Scripts\ci_import_production_assets.cmd"
$alternateManifest=Join-Path $root "Data\P1C01OpenGameArtRpgHeroCandidateBatchV1.json"
$kayHoodedManifest=Join-Path $root "Data\P1C01KayKitAdventurersRogueHoodedHeroCandidateBatchV1.json"
$kenneyManifest=Join-Path $root "Data\P1C01KenneyBlockyHeroCandidateBatchV1.json"
$heroManifest=Join-Path $root "Data\P1C01HeroSkeletalCandidateWaveV1.json"
$heroWave=Join-Path $root "Scripts\run_p1c01_hero_skeletal_candidate_wave.ps1"
$characterIntake=Join-Path $root "Scripts\prepare_p1c01_character_rig_intake.ps1"
$candidateStage=Join-Path $root "Scripts\stage_opengameart_character_candidate.ps1"
foreach($p in @($manifest,$stage,$cpp,$workflow,$importCmd,$alternateManifest,$kayHoodedManifest,$kenneyManifest,$candidateStage,$heroManifest,$heroWave,$characterIntake)){ if(-not(Test-Path -LiteralPath $p -PathType Leaf)){throw "P1C01_FRODO_IMPORT_CONTRACT_FILE_MISSING path=$p"} }
$m=Get-Content -LiteralPath $manifest -Raw | ConvertFrom-Json
$c=Get-Content -LiteralPath $cpp -Raw
$s=Get-Content -LiteralPath $stage -Raw
$w=Get-Content -LiteralPath $workflow -Raw
$i=Get-Content -LiteralPath $importCmd -Raw
$a=Get-Content -LiteralPath $alternateManifest -Raw | ConvertFrom-Json
$kh=Get-Content -LiteralPath $kayHoodedManifest -Raw | ConvertFrom-Json
$kn=Get-Content -LiteralPath $kenneyManifest -Raw | ConvertFrom-Json
$g=Get-Content -LiteralPath $candidateStage -Raw
$h=Get-Content -LiteralPath $heroManifest -Raw | ConvertFrom-Json
$hw=Get-Content -LiteralPath $heroWave -Raw
$ci=Get-Content -LiteralPath $characterIntake -Raw
if([string]$m.character -ne "FRODO"){throw "P1C01_FRODO_IMPORT_CONTRACT_CHARACTER_FAIL"}
if([bool]$m.import_contract.runtime_integration_allowed){throw "P1C01_FRODO_IMPORT_CONTRACT_RUNTIME_FORBIDDEN"}
if([string]$a.provider -ne "OPENGAMEART" -or [string]$a.license -ne "CC0-1.0"){throw "P1C01_FRODO_IMPORT_CONTRACT_ALTERNATE_SOURCE_FAIL"}
if([string]$a.assets[0].id -ne "OGA_QTN_RPG_CHARACTERS_CC0"){throw "P1C01_FRODO_IMPORT_CONTRACT_ALTERNATE_ID_FAIL"}
if(@($kh.assets).Count -ne 1 -or [string]$kh.assets[0].id -ne "KAYKIT_ADVENTURERS_ROGUE_HOODED_CC0" -or [string]$kh.assets[0].download_kind -ne "DIRECT_FBX"){throw "P1C01_FRODO_IMPORT_CONTRACT_KAYKIT_HOODED_FAIL"}
if([string]$kh.assets[0].source_revision -ne "672074b73ba276876a19e8816ecdc5241817ab47"){throw "P1C01_FRODO_IMPORT_CONTRACT_KAYKIT_HOODED_REVISION_FAIL"}
if([string]$kn.provider -ne "KENNEY" -or [string]$kn.license -ne "CC0-1.0" -or @($kn.assets).Count -ne 1 -or [string]$kn.assets[0].id -ne "KENNEY_BLOCKY_CHARACTERS_CC0" -or [string]$kn.assets[0].download_kind -ne "ARCHIVE_ZIP"){throw "P1C01_FRODO_IMPORT_CONTRACT_KENNEY_BLOCKY_FAIL"}
if(-not ([string]$kn.assets[0].download_url).StartsWith("https://kenney.nl/media/pages/assets/blocky-characters/")){throw "P1C01_FRODO_IMPORT_CONTRACT_KENNEY_URL_FAIL"}
if([int]$h.candidate_policy.source_asset_priority_bonus.KAYKIT_ADVENTURERS_CC0 -lt 1){throw "P1C01_FRODO_IMPORT_CONTRACT_SOURCE_PRIORITY_MISSING"}
if([int]$h.candidate_policy.source_asset_priority_bonus.KAYKIT_ADVENTURERS_ROGUE_HOODED_CC0 -lt 1){throw "P1C01_FRODO_IMPORT_CONTRACT_HOODED_PRIORITY_MISSING"}
if([int]$h.candidate_policy.source_asset_priority_bonus.KENNEY_BLOCKY_CHARACTERS_CC0 -lt 1){throw "P1C01_FRODO_IMPORT_CONTRACT_KENNEY_PRIORITY_MISSING"}
$rogueRejection=@($m.technical_rejections | Where-Object { [string]$_.source_sha256 -eq "93a9ee0a67ae69b2d815050234acad2004c3b8af7d294b916e52609c8195eb71" })
if($rogueRejection.Count -ne 1 -or [int]$rogueRejection[0].ue4_reference_bones -ne 48){throw "P1C01_FRODO_IMPORT_CONTRACT_ROGUE_REJECTION_MISSING"}
$hoodedRejection=@($m.technical_rejections | Where-Object { [string]$_.source_sha256 -eq "4a773f074695c6c089cc6f059eed85da080928a4a4137af4e38b177139d4cc27" })
if($hoodedRejection.Count -ne 1 -or [int]$hoodedRejection[0].ue4_reference_bones -ne 48){throw "P1C01_FRODO_IMPORT_CONTRACT_HOODED_REJECTION_MISSING"}
foreach($marker in @("P1C01_CHARACTER_INTAKE_DIRECT_FBX_PASS","direct_fbx_copy_sha256_mismatch",'candidate_file=[string]$directCandidate')){
  if(-not $ci.Contains($marker)){throw "P1C01_FRODO_IMPORT_CONTRACT_DIRECT_INTAKE_MARKER_MISSING marker=$marker"}
}
foreach($marker in @("sourcePriorityBonuses","sourcePriorityBonus","source_priority_bonus")){
  if(-not $hw.Contains($marker)){throw "P1C01_FRODO_IMPORT_CONTRACT_SOURCE_PRIORITY_MARKER_MISSING marker=$marker"}
}
foreach($marker in @("DIRECT_FBX","Test-DirectFbx","OGA_CHARACTER_DIRECT_FBX_HEADER_FAIL","Test-CandidatePayload")){
  if(-not $g.Contains($marker)){throw "P1C01_FRODO_IMPORT_CONTRACT_DIRECT_FBX_STAGE_MARKER_MISSING marker=$marker"}
}
foreach($marker in @(
  'FParse::Param(*Params, TEXT("EnableCharacterRigImport"))',
  'if (bEnableCharacterRigImport)',
  'FindFilesRecursive(RigFbxFiles',
  'Characters/Rigs/',
  'FBXIT_SkeletalMesh',
  'bImportAsSkeletal = true',
  'bImportAnimations = false',
  'bImportMaterials = false',
  'bImportTextures = false',
  'GetAssetByObjectPath',
  'USkeletalMesh::StaticClass()->GetFName()',
  'GetRefSkeleton().GetNum()',
  'skeletal-registered=%s',
  'skeletal-bones=%d'
)){ if(-not $c.Contains($marker)){throw "P1C01_FRODO_IMPORT_CONTRACT_CPP_MARKER_MISSING marker=$marker"} }
$skeletalStart=$c.IndexOf("if (bCharacterRigFbx)",[StringComparison]::Ordinal)
if($skeletalStart -lt 0){throw "P1C01_FRODO_IMPORT_CONTRACT_SKELETAL_BRANCH_MISSING"}
$nonSkeletalElse=$c.IndexOf("else",$skeletalStart,[StringComparison]::Ordinal)
if($nonSkeletalElse -le $skeletalStart){throw "P1C01_FRODO_IMPORT_CONTRACT_SKELETAL_ELSE_MISSING"}
$skeletalBranch=$c.Substring($skeletalStart,$nonSkeletalElse-$skeletalStart)
if($skeletalBranch.Contains("LoadObject<")){throw "P1C01_FRODO_IMPORT_CONTRACT_SYNC_SKELETAL_LOAD_FORBIDDEN"}
if(-not $skeletalBranch.Contains("GetAssetByObjectPath")){throw "P1C01_FRODO_IMPORT_CONTRACT_ASSETREGISTRY_BRANCH_MISSING"}
foreach($marker in @("P1C01_FRODO_IMPORT_STAGE_PASS","Get-FileHash","static_structure_pass")){
  if(-not $s.Contains($marker)){throw "P1C01_FRODO_IMPORT_CONTRACT_STAGE_MARKER_MISSING marker=$marker"}
}
if([string]$m.temporary_source_destination -ne "SourceAssets/Production/Characters/Rigs/FRODO/SK_FRODO.fbx"){
  throw "P1C01_FRODO_IMPORT_CONTRACT_DESTINATION_FAIL path=$([string]$m.temporary_source_destination)"
}
if([string]$m.unreal_asset_name -ne "SK_FRODO"){
  throw "P1C01_FRODO_IMPORT_CONTRACT_ASSET_NAME_FAIL name=$([string]$m.unreal_asset_name)"
}
foreach($marker in @("Build ShireJourneyEditor","Stage Frodo skeletal source","Import Frodo skeletal mesh in UE4.27.2","Verify SK_FRODO import evidence","P1C01_FRODO_UE4_IMPORT_BONE_COUNT_FAIL","-EnableCharacterRigImport","P1C01_FRODO_VALIDATION_CLEANUP_PASS","Stage alternate OpenGameArt RPG hero archive","Stage KayKit RogueHooded alternate hero candidate","P1C01KayKitAdventurersRogueHoodedHeroCandidateBatchV1.json","Stage Kenney Blocky alternate hero candidate","P1C01KenneyBlockyHeroCandidateBatchV1.json","P1C01_FRODO_VALIDATION_CLEANUP_GIT_FAIL")){
  if(-not $w.Contains($marker)){throw "P1C01_FRODO_IMPORT_CONTRACT_WORKFLOW_MARKER_MISSING marker=$marker"}
}
foreach($marker in @("%*","ENABLE_CHARACTER_RIG_IMPORT","cleanup_untracked_validation_file","P1C01_FRODO_VALIDATION_RESIDUE_REMOVED")){
  if(-not $i.Contains($marker)){throw "P1C01_FRODO_IMPORT_CONTRACT_CMD_MARKER_MISSING marker=$marker"}
}
Write-Host "P1C01_FRODO_IMPORT_CONTRACT_PASS runtime=false boundedRigFbx=true explicitOptIn=true residueCleanup=true asyncRuntimePreserved=true"
