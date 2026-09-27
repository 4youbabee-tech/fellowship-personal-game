$ErrorActionPreference = "Stop"

function Write-Flag([string]$Name, [bool]$Value) {
    $text = if ($Value) { "true" } else { "false" }
    Add-Content -LiteralPath $env:GITHUB_ENV -Value "$Name=$text"
}

function Enable-All {
    foreach($name in @(
        "WH_STAGE_POLYHAVEN","WH_STAGE_OGA","WH_STAGE_QUATERNIUS","WH_STAGE_AMBIENTCG",
        "WH_STAGE_AMBIENTCG_TRILOGY","WH_STAGE_KENNEY","WH_STAGE_KAYKIT",
        "WH_RUN_AUDIT","WH_RUN_SATURATION","WH_RUN_PREP","WH_RUN_PROVIDER_RESOLUTION"
    )) {
        Write-Flag $name $true
    }
    Write-Host "WAREHOUSE_CLASSIFY mode=all reason=manual-or-fail-safe"
}

$eventName = [string]$env:GITHUB_EVENT_NAME
if($eventName -eq "workflow_dispatch") {
    Enable-All
    exit 0
}

$git = (Get-Command git.exe -ErrorAction SilentlyContinue).Source
if(-not $git) {
    foreach($candidate in @("C:\Program Files\Git\cmd\git.exe","C:\Program Files (x86)\Git\cmd\git.exe")) {
        if(Test-Path -LiteralPath $candidate){ $git=$candidate; break }
    }
}
if(-not $git) {
    Enable-All
    exit 0
}

$baseSha = ([string]$env:BASE_SHA).Trim()
$headSha = ([string]$env:TARGET_SHA).Trim()
if([string]::IsNullOrWhiteSpace($headSha)) {
    Enable-All
    exit 0
}
if([string]::IsNullOrWhiteSpace($baseSha) -or $baseSha -match '^0+$') {
    $baseSha = (& $git rev-parse "$headSha^").Trim()
}

$changed = @(& $git diff --name-only $baseSha $headSha 2>$null)
if($LASTEXITCODE -ne 0) {
    & $git fetch --no-tags --depth=2 origin $baseSha 2>$null
    $changed = @(& $git diff --name-only $baseSha $headSha 2>$null)
}
if($LASTEXITCODE -ne 0 -or $changed.Count -eq 0) {
    Enable-All
    exit 0
}

$flags = [ordered]@{
    WH_STAGE_POLYHAVEN=$false
    WH_STAGE_OGA=$false
    WH_STAGE_QUATERNIUS=$false
    WH_STAGE_AMBIENTCG=$false
    WH_STAGE_AMBIENTCG_TRILOGY=$false
    WH_STAGE_KENNEY=$false
    WH_STAGE_KAYKIT=$false
    WH_RUN_AUDIT=$false
    WH_RUN_SATURATION=$false
    WH_RUN_PREP=$false
    WH_RUN_PROVIDER_RESOLUTION=$false
}

$providerTouched=$false
$unknown=$false
foreach($raw in $changed) {
    $p = ($raw -replace "\\","/")
    Write-Host "WAREHOUSE_CHANGED $p"

    switch -Wildcard ($p) {
        ".github/workflows/warehouse-stage.yml" { $unknown=$true; continue }
        "Scripts/warehouse_network.ps1" { $unknown=$true; continue }

        "Data/WarehouseAcquisitionBatchV1.json" { $flags.WH_STAGE_POLYHAVEN=$true; $providerTouched=$true; continue }
        "Scripts/stage_polyhaven_warehouse.ps1" { $flags.WH_STAGE_POLYHAVEN=$true; $providerTouched=$true; continue }

        "Data/WarehouseAudioAcquisitionBatchV1.json" { $flags.WH_STAGE_OGA=$true; $providerTouched=$true; continue }
        "Scripts/stage_opengameart_audio.ps1" { $flags.WH_STAGE_OGA=$true; $providerTouched=$true; continue }

        "Data/WarehouseQuaterniusAcquisitionBatchV1.json" { $flags.WH_STAGE_QUATERNIUS=$true; $providerTouched=$true; continue }
        "Scripts/stage_quaternius_warehouse.ps1" { $flags.WH_STAGE_QUATERNIUS=$true; $providerTouched=$true; continue }

        "Data/WarehouseAmbientCGAcquisitionBatchV1.json" { $flags.WH_STAGE_AMBIENTCG=$true; $providerTouched=$true; continue }
        "Data/WarehouseAmbientCGTrilogyBatchV2.json" { $flags.WH_STAGE_AMBIENTCG_TRILOGY=$true; $providerTouched=$true; continue }
        "Scripts/stage_ambientcg_warehouse.ps1" {
            $flags.WH_STAGE_AMBIENTCG=$true
            $flags.WH_STAGE_AMBIENTCG_TRILOGY=$true
            $providerTouched=$true
            continue
        }

        "Data/WarehouseKenneyAcquisitionBatchV1.json" { $flags.WH_STAGE_KENNEY=$true; $providerTouched=$true; continue }
        "Scripts/stage_kenney_warehouse.ps1" { $flags.WH_STAGE_KENNEY=$true; $providerTouched=$true; continue }

        "Data/WarehouseKayKitGitHubAcquisitionBatchV1.json" { $flags.WH_STAGE_KAYKIT=$true; $providerTouched=$true; continue }
        "Scripts/stage_kaykit_github_warehouse.ps1" { $flags.WH_STAGE_KAYKIT=$true; $providerTouched=$true; continue }

        "Scripts/audit_warehouse_inventory.ps1" {
            $flags.WH_RUN_AUDIT=$true
            $flags.WH_RUN_SATURATION=$true
            $flags.WH_RUN_PREP=$true
            $flags.WH_RUN_PROVIDER_RESOLUTION=$true
            continue
        }
        "Data/WarehouseSaturationTrainV1.json" {
            $flags.WH_RUN_SATURATION=$true
            $flags.WH_RUN_PREP=$true
            $flags.WH_RUN_PROVIDER_RESOLUTION=$true
            continue
        }
        "Scripts/run_warehouse_saturation_train.ps1" {
            $flags.WH_RUN_SATURATION=$true
            $flags.WH_RUN_PREP=$true
            $flags.WH_RUN_PROVIDER_RESOLUTION=$true
            continue
        }
        "Data/WarehouseCriticalGapPreparationTrainV2.json" {
            $flags.WH_RUN_PREP=$true
            $flags.WH_RUN_PROVIDER_RESOLUTION=$true
            continue
        }
        "Scripts/run_warehouse_critical_gap_preparation.ps1" {
            $flags.WH_RUN_PREP=$true
            $flags.WH_RUN_PROVIDER_RESOLUTION=$true
            continue
        }
        "Data/WarehouseProviderAccessPolicyV1.json" { $flags.WH_RUN_PROVIDER_RESOLUTION=$true; continue }
        "Data/WarehouseProviderResolutionTrainV3.json" { $flags.WH_RUN_PROVIDER_RESOLUTION=$true; continue }
        "Scripts/run_warehouse_provider_resolution.ps1" { $flags.WH_RUN_PROVIDER_RESOLUTION=$true; continue }
        "Scripts/classify_warehouse_validation.ps1" { continue }
        default { $unknown=$true }
    }
}

if($unknown) {
    Enable-All
    exit 0
}

if($providerTouched) {
    $flags.WH_RUN_AUDIT=$true
    $flags.WH_RUN_SATURATION=$true
    $flags.WH_RUN_PREP=$true
    $flags.WH_RUN_PROVIDER_RESOLUTION=$true
}

foreach($entry in $flags.GetEnumerator()) {
    Write-Flag $entry.Key ([bool]$entry.Value)
}
Write-Host ("WAREHOUSE_CLASSIFY mode=selective base=" + $baseSha + " head=" + $headSha + " providers=" +
    (@($flags.GetEnumerator() | Where-Object { $_.Key -like "WH_STAGE_*" -and $_.Value } | ForEach-Object { $_.Key }) -join ",") +
    " phases=" +
    (@($flags.GetEnumerator() | Where-Object { $_.Key -like "WH_RUN_*" -and $_.Value } | ForEach-Object { $_.Key }) -join ","))
