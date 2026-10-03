$ErrorActionPreference="Stop"
Set-StrictMode -Version Latest
$root=Split-Path -Parent $PSScriptRoot
$cpp=Get-Content -LiteralPath (Join-Path $root "Source\ShireJourneyEditorTools\Private\ShireProductionImportCommandlet.cpp") -Raw
$stage=Get-Content -LiteralPath (Join-Path $root "Scripts\stage_opengameart_character_candidate.ps1") -Raw
$cmd=Get-Content -LiteralPath (Join-Path $root "Scripts\ci_import_production_assets.cmd") -Raw
foreach($marker in @(
 'FParse::Param(*Params, TEXT("EnableCharacterRigImport"))',
 'FBXIT_SkeletalMesh',
 'bImportAsSkeletal = true',
 'Characters/Rigs/',
 'GetAssetByObjectPath',
 'USkeletalMesh::StaticClass()->GetFName()',
 'GetRefSkeleton().GetNum()',
 'skeletal-registered=%s',
 'skeletal-bones=%d'
)){ if(-not $cpp.Contains($marker)){ throw "FRODO_SKELETAL_CURRENT_IMPORT_MARKER_MISSING marker=$marker" } }
$start=$cpp.IndexOf("if (bCharacterRigFbx)",[StringComparison]::Ordinal)
$end=$cpp.IndexOf('else if (SourceExtension == TEXT("fbx"))',$start,[StringComparison]::Ordinal)
if($start -lt 0 -or $end -le $start){ throw "FRODO_SKELETAL_CURRENT_BRANCH_MISSING" }
$branch=$cpp.Substring($start,$end-$start)
if($branch.Contains("LoadObject<")){ throw "FRODO_SKELETAL_CURRENT_SYNC_LOAD_FORBIDDEN" }
foreach($marker in @("DIRECT_FBX","Test-DirectFbx","Test-CandidatePayload","OGA_CHARACTER_DIRECT_FBX_HEADER_FAIL")){
 if(-not $stage.Contains($marker)){ throw "FRODO_DIRECT_STAGE_MARKER_MISSING marker=$marker" }
}
if(-not $cmd.Contains("ShireProductionImport %* -unattended")){ throw "FRODO_IMPORT_FLAG_FORWARDING_MISSING" }
Write-Host "FRODO_SKELETAL_CURRENT_IMPORT_CONTRACT_PASS optIn=true directFbx=true syncSkeletalLoad=false"
