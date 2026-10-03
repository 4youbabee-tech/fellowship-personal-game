$ErrorActionPreference="Stop"
Set-StrictMode -Version Latest
$root=Split-Path -Parent $PSScriptRoot
$p=Join-Path $root "Data\WholeGameChapterProductionPacketsV1.json"
if(-not(Test-Path -LiteralPath $p -PathType Leaf)){throw "WHOLE_GAME_CHAPTER_PACKETS_MISSING"}
$j=Get-Content -LiteralPath $p -Raw | ConvertFrom-Json
$rows=@($j.packets)
if($rows.Count -ne 23){throw "WHOLE_GAME_CHAPTER_PACKETS_COUNT_FAIL count=$($rows.Count)"}
$ids=@($rows|ForEach-Object{[string]$_.id})
if(@($ids|Sort-Object -Unique).Count -ne 23){throw "WHOLE_GAME_CHAPTER_PACKETS_DUPLICATE_IDS"}
$expected=@("F1-01","F1-02","F1-03","F1-04","F1-05","F1-06","F1-07","F1-08","F2-01","F2-02","F2-03","F2-04","F2-05","F2-06","F2-07","F2-08","F3-01","F3-02","F3-03","F3-04","F3-05","F3-06","F3-07")
foreach($id in $expected){
  $match=@($rows|Where-Object{[string]$_.id -eq $id})
  if($match.Count -ne 1){throw "WHOLE_GAME_CHAPTER_PACKETS_PARITY_FAIL id=$id count=$($match.Count)"}
  if([bool]$match[0].runtime_integration_allowed){throw "WHOLE_GAME_CHAPTER_PACKETS_RUNTIME_FORBIDDEN id=$id"}
  if([string]::IsNullOrWhiteSpace([string]$match[0].locked_postcondition)){throw "WHOLE_GAME_CHAPTER_PACKETS_POSTCONDITION_MISSING id=$id"}
}
$f3=@($rows|Where-Object{[string]$_.id -match '^F3-'})
if(@($f3|Where-Object{[string]$_.source_boundary -ne "FILM_CANON_MASTER_SUMMARY_NOT_SCRIPT_VERIFIED"}).Count){throw "WHOLE_GAME_CHAPTER_PACKETS_ROTK_EVIDENCE_BOUNDARY_FAIL"}
Write-Host "WHOLE_GAME_CHAPTER_PACKETS_PASS chapters=23 runtime=false rotkBoundary=true"
