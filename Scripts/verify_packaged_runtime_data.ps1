param(
    [string]$ProjectRoot = $env:GITHUB_WORKSPACE,
    [string]$ArchiveRoot = ""
)

$ErrorActionPreference = "Stop"
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) { throw "ProjectRoot is required" }
if ([string]::IsNullOrWhiteSpace($ArchiveRoot)) {
    $ArchiveRoot = Join-Path $ProjectRoot "Saved\W00Package\WindowsNoEditor"
}

$buildCs = Join-Path $ProjectRoot "Source\ShireJourney\ShireJourney.Build.cs"
if (-not (Test-Path -LiteralPath $buildCs -PathType Leaf)) { throw "Build.cs missing: $buildCs" }
if (-not (Test-Path -LiteralPath $ArchiveRoot -PathType Container)) { throw "Archive root missing: $ArchiveRoot" }

$text = Get-Content -LiteralPath $buildCs -Raw
$matches = [regex]::Matches($text, 'RuntimeDependencies\.Add\("\$\(ProjectDir\)/([^"]+)"\)')
$expected = @($matches | ForEach-Object { $_.Groups[1].Value })
if ($expected.Count -eq 0) { throw "No RuntimeDependencies discovered in Build.cs" }

$missing = @()
$invalidJson = @()
$verified = @()
foreach ($relative in $expected) {
    $normalized = $relative -replace '/', '\'
    $candidates = @(
        (Join-Path $ArchiveRoot ("ShireJourney\" + $normalized)),
        (Join-Path $ArchiveRoot $normalized)
    )
    $found = $null
    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            $found = $candidate
            break
        }
    }
    if (-not $found) {
        $missing += $relative
        continue
    }

    try {
        $null = Get-Content -LiteralPath $found -Raw | ConvertFrom-Json
    }
    catch {
        $invalidJson += [ordered]@{ file=$relative; path=$found; error=$_.Exception.Message }
        continue
    }

    $item = Get-Item -LiteralPath $found
    $verified += [ordered]@{
        file=$relative
        path=$found
        size=[int64]$item.Length
        sha256=(Get-FileHash -LiteralPath $found -Algorithm SHA256).Hash.ToLowerInvariant()
    }
}

$report = [ordered]@{
    schema_version=1
    generated_at_utc=[DateTime]::UtcNow.ToString("o")
    archive_root=$ArchiveRoot
    expected_count=$expected.Count
    verified_count=$verified.Count
    missing=$missing
    invalid_json=$invalidJson
    verified=$verified
}
$reportPath = Join-Path $ProjectRoot "Saved\Logs\CI-W00-PackagedData.json"
$report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $reportPath -Encoding UTF8

if ($missing.Count -gt 0 -or $invalidJson.Count -gt 0) {
    Write-Host ("W00_PACKAGED_DATA_FAIL expected=" + $expected.Count + " verified=" + $verified.Count + " missing=" + $missing.Count + " invalidJson=" + $invalidJson.Count + " report=" + $reportPath)
    $missing | ForEach-Object { Write-Host ("MISSING_RUNTIME_DATA " + $_) }
    $invalidJson | ForEach-Object { Write-Host ("INVALID_RUNTIME_JSON " + $_.file + " " + $_.error) }
    exit 2
}

Write-Host ("W00_PACKAGED_DATA_PASS expected=" + $expected.Count + " verified=" + $verified.Count + " report=" + $reportPath)
