$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$scriptPath = Join-Path $projectRoot "Scripts\stage_quaternius_warehouse.ps1"
$policyPath = Join-Path $projectRoot "Data\WarehouseProviderAccessPolicyV1.json"
$registryPath = Join-Path $projectRoot "Data\GlobalWarehouseSourceRegistryV2.json"

foreach($path in @($scriptPath,$policyPath,$registryPath)){
    if(-not (Test-Path -LiteralPath $path -PathType Leaf)){ throw "WAREHOUSE_ZERO_PAYLOAD_GUARD_MISSING path=$path" }
}

$script = Get-Content -LiteralPath $scriptPath -Raw
$policy = Get-Content -LiteralPath $policyPath -Raw | ConvertFrom-Json
$registry = Get-Content -LiteralPath $registryPath -Raw | ConvertFrom-Json

if(-not $script.Contains("QUATERNIUS_WAREHOUSE_STAGE_ZERO_PAYLOAD_FAIL")){
    throw "WAREHOUSE_ZERO_PAYLOAD_GUARD_SCRIPT_MARKER_MISSING"
}
if(-not $script.Contains('if ($receipt.files.Count -eq 0 -and $receipt.unresolved.Count -gt 0)')){
    throw "WAREHOUSE_ZERO_PAYLOAD_GUARD_CONDITION_MISSING"
}
if(-not $script.Contains("exit 3")){
    throw "WAREHOUSE_ZERO_PAYLOAD_GUARD_EXIT_MISSING"
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

Write-Host "WAREHOUSE_ZERO_PAYLOAD_GUARD_PASS quaternius=manual failClosed=true"
