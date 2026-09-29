param(
    [string]$ProjectRoot = $env:GITHUB_WORKSPACE,
    [int]$TimeoutSeconds = 45,
    [int]$ObservationSeconds = 6
)

$ErrorActionPreference = "Stop"
$packageRoot = Join-Path $ProjectRoot "Saved\W00Package\WindowsNoEditor"
$exe = Join-Path $packageRoot "ShireJourney.exe"
$log = Join-Path $ProjectRoot "Saved\Logs\CI-W00-PackagedStartup.log"
if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) { throw "Packaged executable missing: $exe" }
if (Test-Path -LiteralPath $log) { Remove-Item -LiteralPath $log -Force }

$args = @(
    "/Engine/Maps/Templates/Template_Default",
    "-game",
    "-windowed",
    "-ResX=1280",
    "-ResY=720",
    "-unattended",
    "-nop4",
    "-nosplash",
    "-NoSound",
    "-ShireCIRuntimeAudit",
    ("-abslog=" + $log)
)

$start = Get-Date
$proc = Start-Process -FilePath $exe -ArgumentList $args -PassThru
$readyAt = $null
$failure = $null
$runtimeDataReadyMarker = "NPCContext: ready=yes"
$required = @(
    "ShirePlayableStartup: GameMode ready",
    "ShireStartupGrounding: PASS chapter=P1C01",
    "ShirePlayableStartup: chapter=P1C01 route=FrodoMain",
    $runtimeDataReadyMarker
)

try {
    while ($true) {
        if ($proc.HasExited) {
            $failure = "packaged runtime exited before observation completed exit=$($proc.ExitCode)"
            break
        }
        $elapsed = ((Get-Date) - $start).TotalSeconds
        if ($elapsed -ge $TimeoutSeconds) {
            $failure = "packaged runtime readiness/observation timeout"
            break
        }

        $text = ""
        if (Test-Path -LiteralPath $log -PathType Leaf) {
            $rawText = Get-Content -LiteralPath $log -Raw -ErrorAction SilentlyContinue
            if ($null -ne $rawText) {
                $text = [string]$rawText
            }
        }
        if ($text -match "Fatal error:|Assertion failed|Ensure condition failed") {
            $failure = "fatal/assert/ensure in packaged runtime log"
            break
        }

        $allPresent = $true
        foreach ($marker in $required) {
            if (-not $text.Contains($marker)) { $allPresent = $false; break }
        }
        if ($allPresent -and -not $readyAt) { $readyAt = Get-Date }
        if ($readyAt -and (((Get-Date) - $readyAt).TotalSeconds -ge $ObservationSeconds)) {
            break
        }
        Start-Sleep -Milliseconds 250
    }
}
finally {
    if (-not $proc.HasExited) {
        Stop-Process -Id $proc.Id -Force
        $proc.WaitForExit()
    }
}

if ($failure) {
    Write-Host ("W00_PACKAGED_STARTUP_FAIL " + $failure)
    if (Test-Path -LiteralPath $log) { Get-Content -LiteralPath $log -Tail 300 }
    exit 3
}
Write-Host ("W00_PACKAGED_RUNTIME_DATA_READ_PASS marker=" + $runtimeDataReadyMarker)
Write-Host ("W00_PACKAGED_STARTUP_PASS observed=" + $ObservationSeconds + "s log=" + $log)
