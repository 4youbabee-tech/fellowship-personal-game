param(
  [string]$GatePath = "Data/P1C01Gate67AcceptanceChecklistV1.json",
  [string]$TrainManifest = "Data/Part1SequentialRuntimeChapterTrainV1.json"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path $PSScriptRoot -Parent
if(-not [IO.Path]::IsPathRooted($GatePath)){ $GatePath = Join-Path $ProjectRoot $GatePath }
if(-not [IO.Path]::IsPathRooted($TrainManifest)){ $TrainManifest = Join-Path $ProjectRoot $TrainManifest }

if(-not (Test-Path -LiteralPath $GatePath -PathType Leaf)){ throw "Sequential queue gate file missing: $GatePath" }
if(-not (Test-Path -LiteralPath $TrainManifest -PathType Leaf)){ throw "Sequential queue train manifest missing: $TrainManifest" }

$gate = Get-Content -LiteralPath $GatePath -Raw | ConvertFrom-Json
$train = Get-Content -LiteralPath $TrainManifest -Raw | ConvertFrom-Json
$required = [string]$train.runtime_release_contract.required_predecessor_gate_status
$next = [string]$train.runtime_release_contract.current_successor
$current = [string]$gate.status

if($next -ne "P1C02"){ throw "Sequential queue first successor contract mismatch: $next" }

if($current -ne $required){
  if(-not [string]::IsNullOrWhiteSpace($env:GITHUB_ENV)){
    Add-Content -LiteralPath $env:GITHUB_ENV -Value "P1C02_QUEUE_RELEASE=false"
    Add-Content -LiteralPath $env:GITHUB_ENV -Value ("SHIRE_NEXT_RUNTIME_CHAPTER=" + $next)
  }
  Write-Host ("SEQUENTIAL_CHAPTER_QUEUE_WAIT predecessor=P1C01 currentGate=" + $current + " required=" + $required + " next=" + $next)
  exit 0
}

if(-not [string]::IsNullOrWhiteSpace($env:GITHUB_ENV)){
  Add-Content -LiteralPath $env:GITHUB_ENV -Value "P1C02_QUEUE_RELEASE=true"
  Add-Content -LiteralPath $env:GITHUB_ENV -Value ("SHIRE_NEXT_RUNTIME_CHAPTER=" + $next)
}
Write-Host ("SEQUENTIAL_CHAPTER_QUEUE_RELEASE predecessor=P1C01 gate=" + $current + " next=" + $next)
Write-Host ("SEQUENTIAL_CHAPTER_QUEUE_PASS next=" + $next + " source-prep-authorized runtime-gate-open")
exit 0
