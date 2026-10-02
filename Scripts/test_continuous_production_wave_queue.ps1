$ErrorActionPreference="Stop"
Set-StrictMode -Version Latest
$root=Split-Path -Parent $PSScriptRoot
$p=Join-Path $root "Data\ContinuousProductionWaveQueueV1.json"
if(-not(Test-Path $p -PathType Leaf)){throw "CONTINUOUS_QUEUE_MISSING"}
$j=Get-Content $p -Raw|ConvertFrom-Json
$w=@($j.waves)
if($w.Count -lt 24){throw "CONTINUOUS_QUEUE_TOO_SMALL count=$($w.Count)"}
$ids=@($w|ForEach-Object{$_.id})
if(@($ids|Sort-Object -Unique).Count -ne $w.Count){throw "CONTINUOUS_QUEUE_DUPLICATE_IDS"}
if(-not(@($w|Where-Object{$_.mode -eq "SOURCE_ONLY"}).Count)){throw "CONTINUOUS_QUEUE_NO_SOURCE_FALLBACK"}
if(-not(@($w|Where-Object{$_.mode -eq "SOURCE_PREPRODUCTION_ONLY"}).Count)){throw "CONTINUOUS_QUEUE_NO_PREPROD_FALLBACK"}
if(@($w|Where-Object{$_.chapter -match "^P[23]" -and $_.mode -eq "RUNTIME"}).Count){throw "CONTINUOUS_QUEUE_FUTURE_RUNTIME_FORBIDDEN"}
$total=($w|Measure-Object -Property target_items -Sum).Sum
if($total -lt 3000){throw "CONTINUOUS_QUEUE_CAPACITY_TOO_SMALL total=$total"}
Write-Host "CONTINUOUS_MEGA_QUEUE_PASS waves=$($w.Count) targetItems=$total"
