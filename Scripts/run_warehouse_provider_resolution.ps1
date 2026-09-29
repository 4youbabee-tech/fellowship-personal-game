param(
  [string]$ManifestPath="Data/WarehouseProviderResolutionTrainV3.json",
  [string]$RegistryPath="Data/GlobalWarehouseSourceRegistryV2.json",
  [string]$PolicyPath="Data/WarehouseProviderAccessPolicyV1.json",
  [string]$WarehouseRoot="D:\actions-runner\_warehouse\ShireJourney",
  [string]$OutputRoot=""
)

Set-StrictMode -Version Latest
$ErrorActionPreference="Stop"

$ProjectRoot=Split-Path $PSScriptRoot -Parent
foreach($name in @("ManifestPath","RegistryPath","PolicyPath")){
  $value=Get-Variable -Name $name -ValueOnly
  if(-not(Test-Path -LiteralPath $value -PathType Leaf)){
    $candidate=Join-Path $ProjectRoot $value
    if(Test-Path -LiteralPath $candidate -PathType Leaf){ Set-Variable -Name $name -Value $candidate }
  }
}
if([string]::IsNullOrWhiteSpace($OutputRoot)){$OutputRoot=Join-Path $ProjectRoot "Saved\WarehouseProviderResolution"}
New-Item -ItemType Directory -Path $OutputRoot -Force|Out-Null

$manifest=Get-Content -LiteralPath $ManifestPath -Raw|ConvertFrom-Json
$registry=Get-Content -LiteralPath $RegistryPath -Raw|ConvertFrom-Json
$policy=Get-Content -LiteralPath $PolicyPath -Raw|ConvertFrom-Json

$receiptProviders=@{}
if(Test-Path -LiteralPath $WarehouseRoot -PathType Container){
  foreach($rf in @(Get-ChildItem -LiteralPath $WarehouseRoot -Recurse -File -Filter "receipt_*.json")){
    try{$r=Get-Content -LiteralPath $rf.FullName -Raw|ConvertFrom-Json}catch{continue}
    $provider=[string]$r.provider
    if([string]::IsNullOrWhiteSpace($provider)){continue}
    if(-not $receiptProviders.ContainsKey($provider)){$receiptProviders[$provider]=0}
    $receiptProviders[$provider] += @($r.files).Count
  }
}

$sourceMap=@{}
foreach($source in @($registry.sources)){
  $sourceMap[[string]$source.id]=$source
}

function Resolve-ProviderState {
  param([string]$Provider)
  if($Provider -eq "PROJECT_OWNED"){
    return [ordered]@{provider=$Provider;state="LOCAL_ONLY";automation="LOCAL_ONLY";access="LOCAL_ONLY";license="PROJECT_OWNED";receipt_records=0}
  }
  if(-not $sourceMap.ContainsKey($Provider)){
    return [ordered]@{provider=$Provider;state="REGISTRY_MISSING";automation="UNKNOWN";access="UNKNOWN";license="UNKNOWN";receipt_records=0}
  }
  $s=$sourceMap[$Provider]
  $automation=[string]$s.automation
  $access=[string]$s.access
  $license=[string]$s.license
  $receipts=if($receiptProviders.ContainsKey($Provider)){[int]$receiptProviders[$Provider]}else{0}
  $state="MANUAL_OR_REVIEW"
  if($automation -in @("AUTO_STAGE","AUTO_RESOLVE_STAGE","AUTO_STAGE_WHEN_DIRECT_FILE_AND_LICENSE_KNOWN")){$state="AUTO_CAPABLE"}
  elseif($automation -match "AUTH_REQUIRED"){$state="AUTH_REQUIRED"}
  elseif($automation -match "REFERENCE|NONE"){$state="REFERENCE_ONLY"}
  elseif($automation -match "REVIEW|MARKETPLACE|PER_ITEM|PER_PACK"){$state="REVIEW_REQUIRED"}
  elseif($automation -match "MANUAL|DISCOVER"){$state="MANUAL_ONLY"}
  return [ordered]@{provider=$Provider;state=$state;automation=$automation;access=$access;license=$license;receipt_records=$receipts}
}

$cars=@()
foreach($car in @($manifest.cars|Sort-Object order)){
  $preferred=@()
  foreach($p in @($car.preferred)){ $preferred += Resolve-ProviderState -Provider ([string]$p) }
  $fallback=@()
  foreach($p in @($car.fallback)){ $fallback += Resolve-ProviderState -Provider ([string]$p) }

  $autoPreferred=@($preferred|Where-Object{$_.state -eq "AUTO_CAPABLE"})
  $stagedPreferred=@($preferred|Where-Object{$_.receipt_records -gt 0})
  $selected=$null
  if($stagedPreferred.Count -gt 0){$selected=$stagedPreferred[0]}
  elseif($autoPreferred.Count -gt 0){$selected=$autoPreferred[0]}
  else{
    $autoFallback=@($fallback|Where-Object{$_.state -eq "AUTO_CAPABLE"})
    $stagedFallback=@($fallback|Where-Object{$_.receipt_records -gt 0})
    if($stagedFallback.Count -gt 0){$selected=$stagedFallback[0]}
    elseif($autoFallback.Count -gt 0){$selected=$autoFallback[0]}
  }

  $state=if($null -ne $selected){
    if($selected.receipt_records -gt 0){"STAGED_PROVIDER_AVAILABLE"}else{"AUTO_PROVIDER_AVAILABLE"}
  }else{"MANUAL_AUTH_OR_REVIEW_REQUIRED"}

  $cars += [ordered]@{
    order=[int]$car.order
    id=[string]$car.id
    slot=[string]$car.slot
    selected_provider=if($null -eq $selected){""}else{[string]$selected.provider}
    state=$state
    preferred=$preferred
    fallback=$fallback
    ceiling=[string]$car.ceiling
  }
}

$unresolved=@($cars|Where-Object{$_.state -eq "MANUAL_AUTH_OR_REVIEW_REQUIRED"})
$report=[ordered]@{
  schema_version=1
  train_id=[string]$manifest.train_id
  generated_at_utc=[DateTime]::UtcNow.ToString("o")
  cars=$cars
  unresolved_count=$unresolved.Count
  unresolved=@($unresolved|ForEach-Object{[ordered]@{order=$_.order;id=$_.id;slot=$_.slot}})
  provider_receipt_records=$receiptProviders
  rules=@(
    "No auth/paywall/store bypass.",
    "AUTO_PROVIDER_AVAILABLE means access policy permits automated staging; it does not prove a file was downloaded.",
    "STAGED_PROVIDER_AVAILABLE means at least one receipt record exists for the provider; slot-specific suitability still requires intake QC.",
    "Provider resolution never promotes READY_FOR_IMPORT."
  )
}

$out=Join-Path $OutputRoot "warehouse_provider_resolution_latest.json"
$report|ConvertTo-Json -Depth 12|Set-Content -LiteralPath $out -Encoding UTF8
Write-Host ("WAREHOUSE_PROVIDER_RESOLUTION_PASS cars="+$cars.Count+" unresolved="+$unresolved.Count+" report="+$out)
