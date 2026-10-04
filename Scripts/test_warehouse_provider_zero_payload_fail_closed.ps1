$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$scriptPath = Join-Path $projectRoot "Scripts\stage_quaternius_warehouse.ps1"
$policyPath = Join-Path $projectRoot "Data\WarehouseProviderAccessPolicyV1.json"
$registryPath = Join-Path $projectRoot "Data\GlobalWarehouseSourceRegistryV2.json"
$workflowPath = Join-Path $projectRoot ".github\workflows\warehouse-stage.yml"

foreach($path in @($scriptPath,$policyPath,$registryPath,$workflowPath)){
    if(-not (Test-Path -LiteralPath $path -PathType Leaf)){ throw "WAREHOUSE_ZERO_PAYLOAD_GUARD_MISSING path=$path" }
}

$script = Get-Content -LiteralPath $scriptPath -Raw
$policy = Get-Content -LiteralPath $policyPath -Raw | ConvertFrom-Json
$registry = Get-Content -LiteralPath $registryPath -Raw | ConvertFrom-Json
$workflow = Get-Content -LiteralPath $workflowPath -Raw

if(-not $script.Contains("QUATERNIUS_WAREHOUSE_STAGE_ZERO_PAYLOAD_FAIL")){
    throw "WAREHOUSE_ZERO_PAYLOAD_GUARD_SCRIPT_MARKER_MISSING"
}
if(-not $script.Contains('if ($receipt.files.Count -eq 0 -and $receipt.unresolved.Count -gt 0)')){
    throw "WAREHOUSE_ZERO_PAYLOAD_GUARD_CONDITION_MISSING"
}
if(-not $script.Contains("exit 3")){
    throw "WAREHOUSE_ZERO_PAYLOAD_GUARD_EXIT_MISSING"
}
if(-not $script.Contains('[switch]$RecordManualQueue')){
    throw "WAREHOUSE_ZERO_PAYLOAD_MANUAL_QUEUE_SWITCH_MISSING"
}
if(-not $script.Contains('"state"] = "MANUAL_QUEUE_REQUIRED"')){
    throw "WAREHOUSE_ZERO_PAYLOAD_MANUAL_QUEUE_STATE_MISSING"
}
if(-not $script.Contains("QUATERNIUS_WAREHOUSE_MANUAL_QUEUE")){
    throw "WAREHOUSE_ZERO_PAYLOAD_MANUAL_QUEUE_MARKER_MISSING"
}
$manualQueueLines = @(
    [regex]::Split($workflow, "\r?\n") |
    Where-Object { $_ -match 'stage_quaternius_warehouse\.ps1"[^\r\n]*-RecordManualQueue' }
)
$expectedManualQueueManifests = @(
    "WarehouseQuaterniusAcquisitionBatchV1.json",
    "WarehouseQuaterniusAnimationBatchV1.json",
    "WarehouseQuaterniusHeroCandidateBatchV1.json"
)
if($manualQueueLines.Count -ne $expectedManualQueueManifests.Count){
    throw "WAREHOUSE_ZERO_PAYLOAD_WORKFLOW_MANUAL_QUEUE_CALL_COUNT count=$($manualQueueLines.Count) expected=$($expectedManualQueueManifests.Count)"
}
foreach($manifestName in $expectedManualQueueManifests){
    $matches = @($manualQueueLines | Where-Object { $_.Contains($manifestName) })
    if($matches.Count -ne 1){
        throw "WAREHOUSE_ZERO_PAYLOAD_WORKFLOW_MANUAL_QUEUE_MANIFEST_COUNT manifest=$manifestName count=$($matches.Count)"
    }
}
if($workflow -match '(?i)continue-on-error'){
    throw "WAREHOUSE_ZERO_PAYLOAD_WORKFLOW_BROAD_CONTINUE_ON_ERROR_FORBIDDEN"
}

$direct = @($policy.classes.PUBLIC_DIRECT_RESOLVER.current)
$manual = @($policy.classes.MANUAL_CLEAR_LICENSE.current)
if($direct -contains "QUATERNIUS"){ throw "WAREHOUSE_ZERO_PAYLOAD_POLICY_DIRECT_STALE" }
if($manual -notcontains "QUATERNIUS"){ throw "WAREHOUSE_ZERO_PAYLOAD_POLICY_MANUAL_MISSING" }

$q = @($registry.sources | Where-Object { $_.id -eq "QUATERNIUS" })
if($q.Count -ne 1){ throw "WAREHOUSE_ZERO_PAYLOAD_REGISTRY_QUATERNIUS_COUNT count=$($q.Count)" }
if([string]$q[0].automation -notmatch "^MANUAL_"){
    throw "WAREHOUSE_ZERO_PAYLOAD_REGISTRY_AUTOMATION_STALE automation=$([string]$q[0].automation)"
}

Write-Host ("WAREHOUSE_ZERO_PAYLOAD_GUARD_PASS quaternius=manual failClosed=true manualQueueCalls=" + $manualQueueLines.Count + " manifests=" + ($expectedManualQueueManifests -join ","))
