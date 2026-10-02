$ErrorActionPreference="Stop"
Set-StrictMode -Version Latest
$root=Split-Path -Parent $PSScriptRoot
$manifest=Join-Path $root "Data\P1C01FrodoSkeletalImportV1.json"
$stage=Join-Path $root "Scripts\prepare_p1c01_frodo_skeletal_import.ps1"
$cpp=Join-Path $root "Source\ShireJourneyEditorTools\Private\ShireProductionImportCommandlet.cpp"
$workflow=Join-Path $root ".github\workflows\p1c01-frodo-skeletal-import-validation.yml"
foreach($p in @($manifest,$stage,$cpp,$workflow)){ if(-not(Test-Path -LiteralPath $p -PathType Leaf)){throw "P1C01_FRODO_IMPORT_CONTRACT_FILE_MISSING path=$p"} }
$m=Get-Content -LiteralPath $manifest -Raw | ConvertFrom-Json
$c=Get-Content -LiteralPath $cpp -Raw
$s=Get-Content -LiteralPath $stage -Raw
$w=Get-Content -LiteralPath $workflow -Raw
if([string]$m.character -ne "FRODO"){throw "P1C01_FRODO_IMPORT_CONTRACT_CHARACTER_FAIL"}
if([bool]$m.import_contract.runtime_integration_allowed){throw "P1C01_FRODO_IMPORT_CONTRACT_RUNTIME_FORBIDDEN"}
foreach($marker in @(
  'FindFilesRecursive(RigFbxFiles',
  'Characters/Rigs/',
  'FBXIT_SkeletalMesh',
  'bImportAsSkeletal = true',
  'bImportAnimations = false',
  'bImportMaterials = false',
  'bImportTextures = false',
  'GetAssetByObjectPath',
  'USkeletalMesh::StaticClass()->GetFName()',
  'skeletal-registered=%s'
)){ if(-not $c.Contains($marker)){throw "P1C01_FRODO_IMPORT_CONTRACT_CPP_MARKER_MISSING marker=$marker"} }
$skeletalStart=$c.IndexOf("if (bCharacterRigFbx)",[StringComparison]::Ordinal)
if($skeletalStart -lt 0){throw "P1C01_FRODO_IMPORT_CONTRACT_SKELETAL_BRANCH_MISSING"}
$nonSkeletalElse=$c.IndexOf("else",$skeletalStart,[StringComparison]::Ordinal)
if($nonSkeletalElse -le $skeletalStart){throw "P1C01_FRODO_IMPORT_CONTRACT_SKELETAL_ELSE_MISSING"}
$skeletalBranch=$c.Substring($skeletalStart,$nonSkeletalElse-$skeletalStart)
if($skeletalBranch.Contains("LoadObject<")){throw "P1C01_FRODO_IMPORT_CONTRACT_SYNC_SKELETAL_LOAD_FORBIDDEN"}
if(-not $skeletalBranch.Contains("GetAssetByObjectPath")){throw "P1C01_FRODO_IMPORT_CONTRACT_ASSETREGISTRY_BRANCH_MISSING"}
foreach($marker in @("P1C01_FRODO_IMPORT_STAGE_PASS","Get-FileHash","static_structure_pass","SK_FRODO.fbx")){
  if(-not $s.Contains($marker)){throw "P1C01_FRODO_IMPORT_CONTRACT_STAGE_MARKER_MISSING marker=$marker"}
}
foreach($marker in @("Build ShireJourneyEditor","Stage Frodo skeletal source","Import Frodo skeletal mesh in UE4.27.2","Verify SK_FRODO import evidence")){
  if(-not $w.Contains($marker)){throw "P1C01_FRODO_IMPORT_CONTRACT_WORKFLOW_MARKER_MISSING marker=$marker"}
}
Write-Host "P1C01_FRODO_IMPORT_CONTRACT_PASS runtime=false boundedRigFbx=true asyncRuntimePreserved=true"
