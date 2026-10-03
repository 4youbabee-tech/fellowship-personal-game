$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
$root = Split-Path -Parent $PSScriptRoot
$cppPath = Join-Path $root "Source\ShireJourneyEditorTools\Private\ShireProductionImportCommandlet.cpp"
if(-not (Test-Path -LiteralPath $cppPath -PathType Leaf)){ throw "STATIC_FBX_WORLD_INTAKE_CPP_MISSING" }
$c = Get-Content -LiteralPath $cppPath -Raw
foreach($marker in @(
  'TArray<FString> StaticFbxFiles',
  'TArray<FString> CharacterFbxFiles',
  'FindFilesRecursive(AllFbxFiles',
  'Characters/Rigs/',
  'FBXIT_StaticMesh',
  'bImportAsSkeletal = false',
  'bImportAnimations = false',
  'bImportMaterials = false',
  'bImportTextures = false',
  'character FBX deferred to skeletal QC lane'
)){
  if(-not $c.Contains($marker)){ throw "STATIC_FBX_WORLD_INTAKE_MARKER_MISSING marker=$marker" }
}
$staticStart = $c.IndexOf('if (SourceExtension == TEXT("fbx"))',[StringComparison]::Ordinal)
if($staticStart -lt 0){ throw "STATIC_FBX_WORLD_INTAKE_BRANCH_MISSING" }
$staticEnd = $c.IndexOf('else if (SourceExtension == TEXT("obj"))',$staticStart,[StringComparison]::Ordinal)
if($staticEnd -le $staticStart){ throw "STATIC_FBX_WORLD_INTAKE_BRANCH_END_MISSING" }
$staticBranch = $c.Substring($staticStart,$staticEnd-$staticStart)
if($staticBranch.Contains("LoadObject<")){ throw "STATIC_FBX_WORLD_INTAKE_SYNC_LOAD_FORBIDDEN" }
Write-Host "STATIC_FBX_WORLD_INTAKE_CONTRACT_PASS staticFbx=true characterDeferred=true syncHeavyLoad=false"
