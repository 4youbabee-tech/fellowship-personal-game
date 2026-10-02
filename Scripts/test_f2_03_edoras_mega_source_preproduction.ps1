$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$root = Split-Path -Parent $PSScriptRoot
$path = Join-Path $root "Data\F2_03EdorasMegaSourcePreproductionV1.json"
if(-not (Test-Path -LiteralPath $path -PathType Leaf)){ throw "F2_03_EDORAS_PACK_MISSING" }
$j = Get-Content -LiteralPath $path -Raw | ConvertFrom-Json

if([string]$j.timeline_chapter_id -ne "F2-03"){ throw "F2_03_EDORAS_ID_FAIL" }
if([string]$j.status -ne "SOURCE_PREPRODUCTION_ONLY_RUNTIME_PREDECESSOR_GATED"){ throw "F2_03_EDORAS_STATUS_FAIL" }
if(-not ([string]$j.runtime_promotion_status -match "FORBIDDEN")){ throw "F2_03_EDORAS_RUNTIME_GATE_FAIL" }
if([string]$j.source_routing.film_story_primary -ne "SRC_FILM_TTT_SCREENPLAY"){ throw "F2_03_EDORAS_FILM_SOURCE_FAIL" }
if([string]$j.source_routing.deep_lore_primary -ne "SRC_TOLKIEN_LOTR_2010"){ throw "F2_03_EDORAS_LORE_SOURCE_FAIL" }
if(@($j.world_cells).Count -lt 7){ throw "F2_03_EDORAS_WORLD_CELL_COUNT_FAIL" }
if(@($j.world_state_variants).Count -lt 3){ throw "F2_03_EDORAS_STATE_VARIANT_FAIL" }
if(@($j.character_source_contracts).Count -lt 6){ throw "F2_03_EDORAS_CHARACTER_CONTRACT_FAIL" }
if(@($j.gameplay_preproduction.safe_window_activities).Count -lt 4){ throw "F2_03_EDORAS_SAFE_WINDOW_FAIL" }
foreach($a in @($j.gameplay_preproduction.safe_window_activities)){
  if([string]::IsNullOrWhiteSpace([string]$a.expiry)){ throw "F2_03_EDORAS_ACTIVITY_EXPIRY_FAIL id=$($a.id)" }
}
if(-not ([string]$j.canonical_contract.locked_postcondition -match "Helm")){ throw "F2_03_EDORAS_LOCKED_OUTCOME_FAIL" }
if(-not ([string]$j.culture_and_material_language.texture_rule -match "PNG/TGA")){ throw "F2_03_EDORAS_TEXTURE_RULE_FAIL" }
if(-not (@($j.performance_preproduction.rules) -match "FStreamableManager")){ throw "F2_03_EDORAS_ASYNC_RULE_FAIL" }
if(-not (@($j.performance_preproduction.rules) -match "HISM/ISM")){ throw "F2_03_EDORAS_INSTANCING_RULE_FAIL" }
if(-not (@($j.living_world_preproduction.lifecycle_rule) -match "pooled")){ throw "F2_03_EDORAS_POOLING_RULE_FAIL" }
if(-not ([string]$j.source_routing.verification_boundary -match "screenplay")){ throw "F2_03_EDORAS_SCREENPLAY_VERIFICATION_BOUNDARY_FAIL" }
if(-not ([string]$j.qa_and_acceptance_preproduction.evidence_boundary -match "SOURCE/PREPRODUCTION ONLY")){ throw "F2_03_EDORAS_EVIDENCE_BOUNDARY_FAIL" }

$futureLeak=@($j.chronology_and_knowledge.forbidden_early_state)
if($futureLeak.Count -lt 3){ throw "F2_03_EDORAS_FUTURE_STATE_GUARD_FAIL" }

$dispositions=@($j.meaningful_detail_disposition)
if($dispositions.Count -lt 7){ throw "F2_03_EDORAS_DETAIL_DISPOSITION_FAIL" }
$allowed=@("IMPLEMENTED","LINKED_FOR_LATER","DEFERRED_PERFORMANCE","BOOK_ONLY_COMPATIBLE","BLOCKED_BY_FILM_CONTINUITY","NOT_APPLICABLE","NEEDS_SOURCE_RESOLUTION")
foreach($row in $dispositions){
  if([string]$row.disposition -notin $allowed){ throw "F2_03_EDORAS_DISPOSITION_VALUE_FAIL value=$($row.disposition)" }
}

Write-Host "F2_03_EDORAS_MEGA_SOURCE_PASS cells=$(@($j.world_cells).Count) states=$(@($j.world_state_variants).Count) characters=$(@($j.character_source_contracts).Count) runtimeGated=true"
