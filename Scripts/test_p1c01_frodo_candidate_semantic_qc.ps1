$ErrorActionPreference = "Stop"
$root=Split-Path -Parent $PSScriptRoot
$rankPath=Join-Path $root "Scripts\run_p1c01_hero_skeletal_candidate_wave.ps1"
$qcPath=Join-Path $root "Scripts\inspect_p1c01_frodo_fbx_candidate.ps1"
$manifestPath=Join-Path $root "Data\P1C01HeroSkeletalCandidateWaveV1.json"
$warehousePath=Join-Path $root ".github\workflows\warehouse-stage.yml"
$prePath=Join-Path $root ".github\workflows\pre-unreal-validation.yml"
foreach($path in @($rankPath,$qcPath,$manifestPath,$warehousePath,$prePath)){
  if(-not (Test-Path -LiteralPath $path -PathType Leaf)){ throw "P1C01_FRODO_SEMANTIC_QC_FILE_MISSING path=$path" }
}
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $rankPath -ScoreSelfTest
if([int]$LASTEXITCODE -ne 0){ throw "P1C01_FRODO_SEMANTIC_QC_TOKEN_SELF_TEST_FAIL exit=$LASTEXITCODE" }
$rank=Get-Content -LiteralPath $rankPath -Raw
$qc=Get-Content -LiteralPath $qcPath -Raw
$m=Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
$schemaFixture=Join-Path ([IO.Path]::GetTempPath()) ("p1c01_frodo_schema_"+[Guid]::NewGuid().ToString("N")+".json")
try {
  $fixture=[ordered]@{
    schema_version=2
    characters=@(
      [ordered]@{
        character="FRODO"
        candidate_count=1
        candidates=@([ordered]@{ filename="BaseCharacter.fbx"; source_fbx="X:\\fixture\\BaseCharacter.fbx" })
      },
      [ordered]@{
        character="GANDALF"
        candidate_count=1
        candidates=@([ordered]@{ filename="Worker_Male.fbx"; source_fbx="X:\\fixture\\Worker_Male.fbx" })
      }
    )
  }
  $fixture | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $schemaFixture -Encoding UTF8
  & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $qcPath -ManifestPath $manifestPath -CandidateReport $schemaFixture -SchemaSelfTest
  if([int]$LASTEXITCODE -ne 0){ throw "P1C01_FRODO_SEMANTIC_QC_SCHEMA_SELF_TEST_FAIL exit=$LASTEXITCODE" }
}
finally {
  Remove-Item -LiteralPath $schemaFixture -Force -ErrorAction SilentlyContinue
}
$w=Get-Content -LiteralPath $warehousePath -Raw
$pre=Get-Content -LiteralPath $prePath -Raw
if($rank.Contains('$hay.Contains($_)')){ throw "P1C01_FRODO_SEMANTIC_QC_SUBSTRING_REGRESSION" }
foreach($marker in @("EXACT_FILENAME_TOKEN_MATCH","filename_tokens","identity_terms","final_character_likeness")){
  if(-not $rank.Contains($marker)){ throw "P1C01_FRODO_SEMANTIC_QC_RANK_MARKER_MISSING marker=$marker" }
}
$frodo=@($m.priority_characters | Where-Object {[string]$_.id -eq "FRODO"})
$gandalf=@($m.priority_characters | Where-Object {[string]$_.id -eq "GANDALF"})
if($frodo.Count -ne 1 -or $gandalf.Count -ne 1){ throw "P1C01_FRODO_SEMANTIC_QC_CHARACTER_CONFIG_FAIL" }
if(@($frodo[0].required_any_tokens).Count -lt 2 -or @($frodo[0].excluded_tokens) -notcontains "female"){ throw "P1C01_FRODO_SEMANTIC_QC_FRODO_POLICY_FAIL" }
if(@($gandalf[0].required_any_tokens).Count -lt 2 -or @($gandalf[0].excluded_tokens) -notcontains "female"){ throw "P1C01_FRODO_SEMANTIC_QC_GANDALF_POLICY_FAIL" }
if([string]$m.frodo_static_fbx_qc.active_character -ne "FRODO"){ throw "P1C01_FRODO_SEMANTIC_QC_ACTIVE_CHARACTER_FAIL" }
if(@($m.frodo_static_fbx_qc.candidate_filename_allowlist) -notcontains "BaseCharacter.fbx"){ throw "P1C01_FRODO_SEMANTIC_QC_BASE_ALLOWLIST_FAIL" }
foreach($marker in @("Get-CandidateCharacterRows","SchemaSelfTest","P1C01_FRODO_STATIC_QC_SCHEMA_UNSUPPORTED","LimbNode","Deformer","Skin","Cluster","fbx_2018_export_confirmed","ready_for_import","P1C01_FRODO_STATIC_QC_PASS")){
  if(-not $qc.Contains($marker)){ throw "P1C01_FRODO_SEMANTIC_QC_PROBE_MARKER_MISSING marker=$marker" }
}
$rankIndex=$w.IndexOf("- name: Build exact-head P1C01 Frodo Gandalf candidate report",[StringComparison]::Ordinal)
$qcIndex=$w.IndexOf("- name: Inspect Frodo FBX static structure",[StringComparison]::Ordinal)
$uploadIndex=$w.IndexOf("- name: Upload exact-head P1C01 hero candidate evidence",[StringComparison]::Ordinal)
if($rankIndex -lt 0 -or $qcIndex -le $rankIndex -or $uploadIndex -le $qcIndex){ throw "P1C01_FRODO_SEMANTIC_QC_WORKFLOW_ORDER_FAIL rank=$rankIndex qc=$qcIndex upload=$uploadIndex" }
if(-not $w.Contains("p1c01_frodo_fbx_static_qc.json")){ throw "P1C01_FRODO_SEMANTIC_QC_ARTIFACT_MISSING" }
if(@([regex]::Matches($pre,'test_p1c01_frodo_candidate_semantic_qc\.ps1')).Count -ne 1){ throw "P1C01_FRODO_SEMANTIC_QC_PRE_WIRING_FAIL" }
Write-Host "P1C01_FRODO_CANDIDATE_SEMANTIC_QC_CONTRACT_PASS exactTokens=true staticProbe=true frodoFirst=true"
