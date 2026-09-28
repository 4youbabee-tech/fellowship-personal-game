$ErrorActionPreference = "Stop"

$scriptPath = Join-Path $PSScriptRoot "run_warehouse_critical_gap_preparation.ps1"
$uriCases = @(
    @{ url = "https://assets.example.test/pack.zip?download=1&token=abc"; expected = ".zip" },
    @{ url = "https://assets.example.test/rig.FBX?dl=1"; expected = ".fbx" },
    @{ url = "https://assets.example.test/page.html?file=pack.zip"; expected = ".html" },
    @{ url = "https://assets.example.test/pack.7z#download"; expected = ".7z" }
)
foreach ($case in $uriCases) {
    $actual = [IO.Path]::GetExtension(([Uri]$case.url).AbsolutePath).ToLowerInvariant()
    if ($actual -ne $case.expected) {
        throw "URL extension classification failed for $($case.url): expected=$($case.expected) actual=$actual"
    }
}

$testRoot = Join-Path ([IO.Path]::GetTempPath()) ("shire-warehouse-contract-" + [Guid]::NewGuid().ToString("N"))
$warehouseRoot = Join-Path $testRoot "warehouse"
$outputRoot = Join-Path $testRoot "prepared"
$inputRoot = Join-Path $testRoot "input"
New-Item -ItemType Directory -Path $warehouseRoot, $inputRoot -Force | Out-Null

try {
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $goodSourceRoot = Join-Path $inputRoot "good"
    New-Item -ItemType Directory -Path $goodSourceRoot -Force | Out-Null
    Set-Content -LiteralPath (Join-Path $goodSourceRoot "shire_grass_basecolor.png") -Value "synthetic test payload" -Encoding ASCII
    $goodArchive = Join-Path $warehouseRoot "good.zip"
    [IO.Compression.ZipFile]::CreateFromDirectory($goodSourceRoot, $goodArchive)

    $badArchive = Join-Path $warehouseRoot "bad.zip"
    Set-Content -LiteralPath $badArchive -Value "not a zip archive" -Encoding ASCII
    $goodHash = (Get-FileHash -LiteralPath $goodArchive -Algorithm SHA256).Hash.ToLowerInvariant()
    $badHash = (Get-FileHash -LiteralPath $badArchive -Algorithm SHA256).Hash.ToLowerInvariant()

    $receiptPath = Join-Path $warehouseRoot "receipt_TEST.json"
    $receipt = [ordered]@{
        batch_id = "WAREHOUSE_CONTRACT_TEST"
        provider = "TEST_PROVIDER"
        files = @(
            [ordered]@{ asset_id = "GOOD_ARCHIVE"; file = $goodArchive; sha256 = $goodHash; source_page = "https://example.test/good" },
            [ordered]@{ asset_id = "BAD_ARCHIVE"; file = $badArchive; sha256 = $badHash; source_page = "https://example.test/bad" },
            [ordered]@{ asset_id = "BAD_ARCHIVE"; file = $badArchive; sha256 = $badHash; source_page = "https://example.test/bad" }
        )
    }
    $receipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $receiptPath -Encoding UTF8

    $manifestPath = Join-Path $testRoot "manifest.json"
    @{ schema_version = 1; train_id = "WAREHOUSE_CONTRACT_TEST"; cars = @() } |
        ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $manifestPath -Encoding UTF8

    $powershellExe = Join-Path $PSHOME "powershell.exe"
    if (-not (Test-Path -LiteralPath $powershellExe -PathType Leaf)) {
        throw "Windows PowerShell executable not found: $powershellExe"
    }
    $childOutput = & $powershellExe -NoLogo -NoProfile -ExecutionPolicy Bypass -File $scriptPath -ManifestPath $manifestPath -WarehouseRoot $warehouseRoot -OutputRoot $outputRoot 2>&1
    $childExitCode = $LASTEXITCODE
    if ($childExitCode -ne 0) {
        throw "Critical-gap preparation should isolate corrupt archives and continue. Exit=$childExitCode Output=$($childOutput -join ' ')"
    }

    $reportPath = Join-Path $outputRoot "warehouse_critical_gap_preparation_latest.json"
    if (-not (Test-Path -LiteralPath $reportPath -PathType Leaf)) {
        throw "Critical-gap report missing: $reportPath"
    }
    $report = Get-Content -LiteralPath $reportPath -Raw | ConvertFrom-Json
    if ([string]$report.outcome -ne "PASS_WITH_MANUAL_QUEUE") {
        throw "Expected PASS_WITH_MANUAL_QUEUE, got $($report.outcome)"
    }
    if ([int]$report.inventory_file_count -lt 1) {
        throw "Valid archive was not inventoried after the corrupt archive was isolated."
    }
    if ([int]$report.blocked.Count -lt 1 -or [int]$report.manual_queue_count -ne 1) {
        throw "Corrupt archive rows were not isolated and deduplicated in the manual queue."
    }
    $manualItem = @($report.manual_queue)[0]
    if ([int]$report.duplicate_receipt_records_skipped -ne 1 -or [int]$manualItem.seen_count -ne 1) {
        throw "Repeated receipt must be skipped and the blocked archive must remain in the manual queue."
    }
    Write-Host "WAREHOUSE_TRAIN_CONTRACT_TEST_PASS valid_archive_continued=true corrupt_archive_manual_queue=true duplicate_records_preserved=true query_extension=true"
}
finally {
    if (Test-Path -LiteralPath $testRoot -PathType Container) {
        Remove-Item -LiteralPath $testRoot -Recurse -Force
    }
}
