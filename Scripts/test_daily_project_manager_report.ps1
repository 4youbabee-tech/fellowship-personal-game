$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$projectRoot = Split-Path -Parent $PSScriptRoot
$generatorPath = Join-Path $projectRoot "Scripts\generate_daily_project_manager_report.ps1"

if (-not (Test-Path -LiteralPath $generatorPath -PathType Leaf)) {
    throw "DAILY_MANAGER_REPORT_TEST_GENERATOR_MISSING"
}

$tokens = $null
$errors = $null
[System.Management.Automation.Language.Parser]::ParseFile(
    $generatorPath,
    [ref]$tokens,
    [ref]$errors
) | Out-Null

if (@($errors).Count -gt 0) {
    $message = (@($errors) | ForEach-Object { $_.Message }) -join " | "
    throw "DAILY_MANAGER_REPORT_PARSE_FAIL errors=$message"
}

$tempDir = Join-Path ([IO.Path]::GetTempPath()) ("shire-daily-manager-" + [Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
try {
    $outPath = Join-Path $tempDir "daily_manager_report.md"
    & $generatorPath -ProjectRoot $projectRoot -OutputPath $outPath -NowUtc ([datetime]"2026-10-01T20:00:00Z")

    if ($LASTEXITCODE -ne 0) {
        throw "DAILY_MANAGER_REPORT_TEST_EXECUTION_FAIL exit=$LASTEXITCODE"
    }
    if (-not (Test-Path -LiteralPath $outPath -PathType Leaf)) {
        throw "DAILY_MANAGER_REPORT_TEST_OUTPUT_MISSING"
    }

    $content = Get-Content -LiteralPath $outPath -Raw
    foreach ($needle in @(
        "# Shire Journey - Daily Project Manager Report",
        "Planning / production completion:",
        "Active lane:",
        "Active gate:",
        "## Meaningful movement in the last 24 hours",
        "## Evidence boundary"
    )) {
        if (-not $content.Contains($needle)) {
            throw "DAILY_MANAGER_REPORT_TEST_CONTENT_MISSING needle=$needle"
        }
    }

    if ($content.Contains([char]0xFFFD) -or $content.Contains("â€”")) {
        throw "DAILY_MANAGER_REPORT_TEST_ENCODING_CORRUPTION"
    }
}
finally {
    Remove-Item -LiteralPath $tempDir -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "DAILY_MANAGER_REPORT_TEST_PASS parse=true execution=true encoding=true"
