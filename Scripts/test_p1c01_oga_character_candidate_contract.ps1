$ErrorActionPreference = "Stop"
$root=Split-Path -Parent $PSScriptRoot
$manifestPath=Join-Path $root "Data\P1C01OpenGameArtHeroCandidateBatchV1.json"
$stagePath=Join-Path $root "Scripts\stage_opengameart_character_candidate.ps1"
$workflowPath=Join-Path $root ".github\workflows\warehouse-stage.yml"
$prepPath=Join-Path $root "Data\P1C01CharacterRigAnimationPrepV1.json"
$prePath=Join-Path $root ".github\workflows\pre-unreal-validation.yml"
foreach($path in @($manifestPath,$stagePath,$workflowPath,$prepPath,$prePath)){
  if(-not (Test-Path -LiteralPath $path -PathType Leaf)){ throw "OGA_CHARACTER_CONTRACT_FILE_MISSING path=$path" }
}
$m=Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
$p=Get-Content -LiteralPath $prepPath -Raw | ConvertFrom-Json
$s=Get-Content -LiteralPath $stagePath -Raw
$w=Get-Content -LiteralPath $workflowPath -Raw
$pre=Get-Content -LiteralPath $prePath -Raw
$a=@($m.assets)
if($a.Count -ne 1){ throw "OGA_CHARACTER_CONTRACT_BOUNDED_COUNT count=$($a.Count)" }
if([string]$m.provider -ne "OPENGAMEART" -or [string]$m.license -ne "CC0-1.0"){ throw "OGA_CHARACTER_CONTRACT_PROVENANCE_FAIL" }
if([string]$a[0].source_author -ne "Quaternius" -or [string]$a[0].observed_page_license -ne "CC0"){ throw "OGA_CHARACTER_CONTRACT_AUTHOR_LICENSE_FAIL" }
if([string]$a[0].source_page -ne "https://opengameart.org/content/animated-characters-pack"){ throw "OGA_CHARACTER_CONTRACT_SOURCE_PAGE_FAIL" }
if([string]$a[0].download_url -ne "https://opengameart.org/sites/default/files/ultimate_animated_character_pack_by_quaternius.zip"){ throw "OGA_CHARACTER_CONTRACT_DIRECT_URL_FAIL" }
if(([string]$a[0].required_final_format).ToUpperInvariant() -ne "FBX"){ throw "OGA_CHARACTER_CONTRACT_FORMAT_FAIL" }
if(@($p.external_candidates | Where-Object {[string]$_.id -eq [string]$a[0].id -and [string]$_.provider -eq "OPENGAMEART"}).Count -ne 1){ throw "OGA_CHARACTER_CONTRACT_INTAKE_REGISTRATION_FAIL" }
foreach($marker in @("OGA_CHARACTER_REUSE_PASS","OGA_CHARACTER_ARCHIVE_FBX_MISSING","Get-FileHash","REUSED_VERIFIED_PAYLOAD","STAGED_VERIFIED_PAYLOAD")){
  if(-not $s.Contains($marker)){ throw "OGA_CHARACTER_CONTRACT_STAGE_MARKER_MISSING marker=$marker" }
}
if(-not $w.Contains("- name: Stage OpenGameArt Quaternius character candidate")){ throw "OGA_CHARACTER_CONTRACT_WORKFLOW_STEP_MISSING" }
if(@([regex]::Matches($pre,'test_p1c01_oga_character_candidate_contract\.ps1')).Count -ne 1){ throw "OGA_CHARACTER_CONTRACT_PRE_WIRING_FAIL" }
Write-Host "OGA_CHARACTER_CANDIDATE_CONTRACT_PASS bounded=true cc0=true fbxArchiveGate=true reuseSha=true"
