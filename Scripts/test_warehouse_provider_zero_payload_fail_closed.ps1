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

# AmbientCG repeat search terms must not re-download the same licensed source, or
# erase a prior valid archive when another region exhausts the bounded byte cap.
$ambientCGPath = Join-Path $projectRoot "Scripts\stage_ambientcg_warehouse.ps1"
if(-not (Test-Path -LiteralPath $ambientCGPath -PathType Leaf)){ throw "AMBIENTCG_DEDUP_SCRIPT_MISSING" }
$ambientCGScript = Get-Content -LiteralPath $ambientCGPath -Raw
foreach($token in @(
    '$acceptedIds = @{}',
    '$idKey=$id.ToLowerInvariant()',
    '$acceptedIds.ContainsKey($idKey)',
    'reason="duplicate_in_current_wave"',
    'WAREHOUSE_AMBIENTCG_DUPLICATE_SKIP',
    'reason="batch_byte_cap_before_download"',
    '$downloadedThisAttempt=$false',
    '$downloadedThisAttempt=$true',
    'if($downloadedThisAttempt){ Remove-Item -LiteralPath $dest -Force }',
    '$acceptedIds[$idKey] = $true',
    'Test-WarehouseReceiptReusable',
    'Test-WarehouseZipReadable',
    'Get-FileHash $dest -Algorithm SHA256'
)){
    if(-not $ambientCGScript.Contains($token)){ throw "AMBIENTCG_DEDUP_GUARD_MISSING token=$token" }
}
$dedupPos=$ambientCGScript.IndexOf('$acceptedIds.ContainsKey($idKey)')
$downloadPos=$ambientCGScript.IndexOf('Invoke-WarehouseDownload -Uri')
$recordPos=$ambientCGScript.IndexOf('$receipt.files += [ordered]@{')
$acceptPos=$ambientCGScript.IndexOf('$acceptedIds[$idKey] = $true')
if(-not ($dedupPos -lt $downloadPos -and $downloadPos -lt $recordPos -and $recordPos -lt $acceptPos)){
    throw "AMBIENTCG_DEDUP_GUARD_ORDER_INVALID"
}
if($ambientCGScript.Contains('max_download_bytes){ Remove-Item $dest -Force')){
    throw "AMBIENTCG_EXISTING_CACHE_REMOVAL_UNSAFE"
}
Write-Host "WAREHOUSE_AMBIENTCG_DEDUP_CONTRACT_PASS networkFree=true shaGuard=true acceptedOnce=true"


# Regression: a prior valid archive cannot prove that an edited regional manifest
# (new search terms, region mappings, texture attribute, or source rules) was staged.
$networkScript = Join-Path $projectRoot "Scripts\\warehouse_network.ps1"
$network = Get-Content -LiteralPath $networkScript -Raw
foreach($token in @('ManifestSha256', 'WAREHOUSE_REUSE_MANIFEST_CHANGED')){
    if(-not $network.Contains($token)){ throw "WAREHOUSE_MANIFEST_CACHE_GUARD_MISSING token=$token" }
}
foreach($token in @('$manifestSha256 = (Get-FileHash', '-ManifestSha256 $manifestSha256', 'manifest_sha256=$manifestSha256')){
    if(-not $ambientCGScript.Contains($token)){ throw "AMBIENTCG_MANIFEST_FINGERPRINT_MISSING token=$token" }
}
if($ambientCGScript.Contains('WAREHOUSE_REFRESH_REMOVE')){ throw "AMBIENTCG_REFRESH_MUST_PRESERVE_VALID_CACHE" }
. $networkScript
$tmp = Join-Path ([IO.Path]::GetTempPath()) ("shire-ambientcg-cache-" + [Guid]::NewGuid().ToString("N"))
try {
    $source = Join-Path $tmp "source"
    New-Item -ItemType Directory -Path $source -Force | Out-Null
    [IO.File]::WriteAllText((Join-Path $source "tiny.txt"), "Licensed CC0 cache regression")
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $zip = Join-Path $tmp "sample.zip"
    [IO.Compression.ZipFile]::CreateFromDirectory($source, $zip)
    $sum = (Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash.ToLowerInvariant()
    $receipt = Join-Path $tmp "receipt.json"
    $original = ('a' * 64)
    $changed = ('b' * 64)
    $sample = [ordered]@{batch_id='CACHE_TEST';manifest_sha256=$original;files=@([ordered]@{file=$zip;size=(Get-Item $zip).Length;sha256=$sum})}
    $sample | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $receipt -Encoding UTF8
    if(-not (Test-WarehouseReceiptReusable -ReceiptPath $receipt -BatchId 'CACHE_TEST' -ManifestSha256 $original)){ throw 'AMBIENTCG_UNCHANGED_CACHE_FALSE_NEGATIVE' }
    if(Test-WarehouseReceiptReusable -ReceiptPath $receipt -BatchId 'CACHE_TEST' -ManifestSha256 $changed){ throw 'AMBIENTCG_STALE_MANIFEST_FALSE_GREEN' }
    if(-not (Test-Path -LiteralPath $zip -PathType Leaf)){ throw 'AMBIENTCG_STALE_RECEIPT_MUST_PRESERVE_ARCHIVE' }
    $sample.Remove('manifest_sha256')
    $sample | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $receipt -Encoding UTF8
    if(Test-WarehouseReceiptReusable -ReceiptPath $receipt -BatchId 'CACHE_TEST' -ManifestSha256 $original){ throw 'AMBIENTCG_LEGACY_RECEIPT_FALSE_GREEN' }
    if(-not (Test-Path -LiteralPath $zip -PathType Leaf)){ throw 'AMBIENTCG_LEGACY_RECEIPT_MUST_PRESERVE_ARCHIVE' }
    Write-Host 'AMBIENTCG_MANIFEST_CACHE_REGRESSION_PASS unchanged=true changed=false legacy=false preservesArchive=true'
} finally {
    Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction SilentlyContinue
}
