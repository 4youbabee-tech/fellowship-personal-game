$ErrorActionPreference="Stop"
Set-StrictMode -Version Latest
$root=Split-Path -Parent $PSScriptRoot
$p=Join-Path $root "Data\ContinuousProductionWaveQueueV2.json"
if(-not(Test-Path -LiteralPath $p -PathType Leaf)){throw "CONTINUOUS_QUEUE_V2_MISSING"}
$j=Get-Content -LiteralPath $p -Raw | ConvertFrom-Json
$w=@($j.waves)
if($w.Count -ne 64){throw "CONTINUOUS_QUEUE_V2_WAVE_COUNT_FAIL count=$($w.Count)"}
$ids=@($w|ForEach-Object{[string]$_.id})
if(@($ids|Sort-Object -Unique).Count -ne 64){throw "CONTINUOUS_QUEUE_V2_DUPLICATE_IDS"}
$expectedChapters=@("F1-01","F1-02","F1-03","F1-04","F1-05","F1-06","F1-07","F1-08","F2-01","F2-02","F2-03","F2-04","F2-05","F2-06","F2-07","F2-08","F3-01","F3-02","F3-03","F3-04","F3-05","F3-06","F3-07")
$chapterRows=@($w|Where-Object{$_.mode -eq "SOURCE_PREPRODUCTION_ONLY"})
if($chapterRows.Count -ne 23){throw "CONTINUOUS_QUEUE_V2_CHAPTER_COUNT_FAIL count=$($chapterRows.Count)"}
foreach($chapter in $expectedChapters){
  $rows=@($chapterRows|Where-Object{[string]$_.source_chapter_id -eq $chapter})
  if($rows.Count -ne 1){throw "CONTINUOUS_QUEUE_V2_CHAPTER_PARITY_FAIL chapter=$chapter count=$($rows.Count)"}
  if([bool]$rows[0].runtime_integration_allowed){throw "CONTINUOUS_QUEUE_V2_FUTURE_RUNTIME_FORBIDDEN chapter=$chapter"}
}
$runtime=@($w|Where-Object{$_.mode -eq "P1C01_RUNTIME"})
if($runtime.Count -ne 12){throw "CONTINUOUS_QUEUE_V2_RUNTIME_COUNT_FAIL count=$($runtime.Count)"}
if(@($runtime|Where-Object{[string]$_.runtime_chapter -ne "P1C01"}).Count){throw "CONTINUOUS_QUEUE_V2_RUNTIME_SCOPE_FAIL"}
$total=($w|Measure-Object -Property target_items -Sum).Sum
if($total -lt 10000){throw "CONTINUOUS_QUEUE_V2_CAPACITY_FAIL total=$total"}
if([string]$j.project_manager_registration.state -ne "REGISTERED"){throw "CONTINUOUS_QUEUE_V2_PM_REGISTRATION_FAIL"}
if([bool]$j.active_runtime_scope.future_runtime_activation){throw "CONTINUOUS_QUEUE_V2_GATE_FAIL"}
if([string]$j.target_profile.engine -ne "UE4.27.2"){throw "CONTINUOUS_QUEUE_V2_ENGINE_FAIL"}
if([string]$j.target_profile.animated_asset_format -ne "FBX"){throw "CONTINUOUS_QUEUE_V2_ANIMATED_FORMAT_FAIL"}
Write-Host "CONTINUOUS_MEGA_QUEUE_V2_PASS waves=$($w.Count) chapters=$($chapterRows.Count) targetItems=$total runtime=P1C01_ONLY"
