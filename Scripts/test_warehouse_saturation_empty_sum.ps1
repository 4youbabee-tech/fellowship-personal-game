$ErrorActionPreference = "Stop"

$scriptPath = Join-Path $PSScriptRoot "run_warehouse_saturation_train.ps1"
$testRoot = Join-Path ([IO.Path]::GetTempPath()) ("shire-saturation-empty-sum-" + [Guid]::NewGuid().ToString("N"))
$warehouseRoot = Join-Path $testRoot "warehouse"
$outputRoot = Join-Path $testRoot "out"
New-Item -ItemType Directory -Path $warehouseRoot -Force | Out-Null

try {
    $manifestPath = Join-Path $testRoot "manifest.json"
    $manifest = [ordered]@{
        schema_version = 1
        train_id = "WAREHOUSE_SATURATION_EMPTY_SUM_TEST"
        cars = @(
            [ordered]@{
                order = 1
                id = "CAR_EMPTY_PROVIDER"
                priority = "CRITICAL"
                ceiling = "INTAKE_QC"
                access_mode = "PUBLIC_CLEAR_LICENSE"
                providers = @("TEST_PROVIDER")
                target = @("nonexistent asset family")
            }
        )
    }
    $manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $manifestPath -Encoding UTF8

    $powershellExe = Join-Path $PSHOME "powershell.exe"
    if (-not (Test-Path -LiteralPath $powershellExe -PathType Leaf)) {
        throw "Windows PowerShell executable not found: $powershellExe"
    }

    $output = & $powershellExe -NoLogo -NoProfile -ExecutionPolicy Bypass -File $scriptPath -ManifestPath $manifestPath -WarehouseRoot $warehouseRoot -OutputRoot $outputRoot 2>&1
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        throw "Empty saturation lane must not fail. Exit=$exitCode Output=$($output -join ' ')"
    }

    $reportPath = Join-Path $outputRoot "warehouse_saturation_latest.json"
    if (-not (Test-Path -LiteralPath $reportPath -PathType Leaf)) {
        throw "Saturation report missing: $reportPath"
    }

    $report = Get-Content -LiteralPath $reportPath -Raw | ConvertFrom-Json
    $cars = @($report.cars)
    if ($cars.Count -ne 1) {
        throw "Expected one synthetic car, got $($cars.Count)"
    }
    if ([int64]$cars[0].verified_bytes -ne 0) {
        throw "Empty verified lane must report verified_bytes=0, got $($cars[0].verified_bytes)"
    }
    if ([int]$cars[0].verified_receipt_files -ne 0) {
        throw "Empty verified lane must report zero verified files."
    }

    Write-Host "WAREHOUSE_SATURATION_EMPTY_SUM_TEST_PASS verified_bytes=0 strictmode_safe=true"
}
finally {
    if (Test-Path -LiteralPath $testRoot -PathType Container) {
        Remove-Item -LiteralPath $testRoot -Recurse -Force
    }
}
