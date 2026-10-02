$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$root = Split-Path -Parent $PSScriptRoot
$helper = Join-Path $root "Scripts\runner_log_timestamp.ps1"
if (-not (Test-Path -LiteralPath $helper -PathType Leaf)) { throw "RUNNER_TIMESTAMP_HELPER_MISSING" }
. $helper

$actual = "[2026-10-02 15:19:29Z INFO BrokerMessageListener] Acknowledging runner request '79d3d284-24ea-5de7-a8cc-3679bb35a8c6'."
$legacy = "[RUNNER 2026-10-02 15:19:29Z INFO] Acknowledging runner request."
$invalid = "2026-10-02 15:19:29Z no-brackets"

$a = ConvertFrom-RunnerLogTimestampUtc -Line $actual
$l = ConvertFrom-RunnerLogTimestampUtc -Line $legacy
$n = ConvertFrom-RunnerLogTimestampUtc -Line $invalid

if ($null -eq $a -or $a.ToString("o") -notlike "2026-10-02T15:19:29*") { throw "RUNNER_TIMESTAMP_ACTUAL_FORMAT_FAIL" }
if ($null -eq $l -or $l.ToString("o") -notlike "2026-10-02T15:19:29*") { throw "RUNNER_TIMESTAMP_LEGACY_FORMAT_FAIL" }
if ($null -ne $n) { throw "RUNNER_TIMESTAMP_INVALID_LINE_FAIL" }

Write-Host "RUNNER_TIMESTAMP_CONTRACT_PASS actual=true legacy=true invalidRejected=true"
