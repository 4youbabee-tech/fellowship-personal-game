param(
  [string]$GatePath = "Data/P1C01Gate67AcceptanceChecklistV1.json",
  [string]$NextManifest = "Data/P1C02ShadowPastChapterPackV1.json"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path $PSScriptRoot -Parent
if(-not [IO.Path]::IsPathRooted($GatePath)){ $GatePath = Join-Path $ProjectRoot $GatePath }
if(-not [IO.Path]::IsPathRooted($NextManifest)){ $NextManifest = Join-Path $ProjectRoot $NextManifest }

if(-not (Test-Path -LiteralPath $GatePath -PathType Leaf)){ throw "Sequential queue gate file missing: $GatePath" }
if(-not (Test-Path -LiteralPath $NextManifest -PathType Leaf)){ throw "Sequential queue manifest missing: $NextManifest" }

$gate = Get-Content -LiteralPath $GatePath -Raw | ConvertFrom-Json
$next = Get-Content -LiteralPath $NextManifest -Raw | ConvertFrom-Json
$required = [string]$next.queue_contract.required_gate_status
$current = [string]$gate.status

if($current -ne $required){
  Write-Host ("SEQUENTIAL_CHAPTER_QUEUE_WAIT predecessor=P1C01 currentGate=" + $current + " required=" + $required + " next=P1C02")
  exit 0
}

Write-Host ("SEQUENTIAL_CHAPTER_QUEUE_RELEASE predecessor=P1C01 gate=" + $current + " next=P1C02")
Write-Host "SEQUENTIAL_CHAPTER_QUEUE_PASS next=P1C02 source-prep-authorized runtime-gate-open"
exit 0
