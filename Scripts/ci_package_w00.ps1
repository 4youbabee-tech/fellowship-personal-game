param(
    [string]$ProjectRoot = $env:GITHUB_WORKSPACE,
    [int]$TimeoutMinutes = 45,
    [int]$HeartbeatSeconds = 30
)

$ErrorActionPreference = "Stop"
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) { throw "ProjectRoot is required" }

$project = Join-Path $ProjectRoot "ShireJourney.uproject"
$uat = "C:\Program Files\Epic Games\UE_4.27\Engine\Build\BatchFiles\RunUAT.bat"
$dbgHelp = "C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\ThirdParty\DbgHelp\dbghelp.dll"
$archive = Join-Path $ProjectRoot "Saved\W00Package"
$runId = if ($env:GITHUB_RUN_ID) { $env:GITHUB_RUN_ID } else { "local" }
$attempt = if ($env:GITHUB_RUN_ATTEMPT) { $env:GITHUB_RUN_ATTEMPT } else { "1" }
$stage = Join-Path $ProjectRoot ("Saved\W00Stage-" + $runId + "-" + $attempt)
$logDir = Join-Path $ProjectRoot "Saved\Logs"
$log = Join-Path $logDir "CI-W00-Package.log"

if (-not (Test-Path -LiteralPath $project -PathType Leaf)) { throw "Project missing: $project" }
if (-not (Test-Path -LiteralPath $uat -PathType Leaf)) { throw "RunUAT missing: $uat" }
if (-not (Test-Path -LiteralPath $dbgHelp -PathType Leaf)) { throw "DbgHelp source missing: $dbgHelp" }
New-Item -ItemType Directory -Path $logDir -Force | Out-Null

foreach ($path in @($archive, $stage)) {
    if (Test-Path -LiteralPath $path) {
        try { attrib -R -S -H ($path + "\*") /S /D 2>$null | Out-Null } catch {}
        Remove-Item -LiteralPath $path -Recurse -Force
    }
    New-Item -ItemType Directory -Path $path -Force | Out-Null
}

$probeDir = Join-Path $stage "Engine\Binaries\ThirdParty\DbgHelp"
New-Item -ItemType Directory -Path $probeDir -Force | Out-Null
$probe = Join-Path $probeDir "dbghelp.dll"
Copy-Item -LiteralPath $dbgHelp -Destination $probe -Force
if (-not (Test-Path -LiteralPath $probe -PathType Leaf)) { throw "W00_PACKAGE_PREFLIGHT_FAIL dbghelp copy probe missing" }
Remove-Item -LiteralPath $probe -Force
Write-Host ("W00_PACKAGE_PREFLIGHT_PASS stage=" + $stage)

$argList = @(
    "BuildCookRun",
    ("-project=`"" + $project + "`""),
    "-noP4",
    "-platform=Win64",
    "-clientconfig=Development",
    "-build",
    "-cook",
    "-map=/Engine/Maps/Templates/Template_Default",
    "-stage",
    ("-stagingdirectory=`"" + $stage + "`""),
    "-pak",
    "-archive",
    ("-archivedirectory=`"" + $archive + "`""),
    "-utf8output",
    "-unattended"
)

Write-Host ("W00_PACKAGE_BEGIN sha=" + $env:TARGET_SHA + " timeoutMinutes=" + $TimeoutMinutes)
$stdout = Join-Path $logDir "CI-W00-Package-stdout.log"
$stderr = Join-Path $logDir "CI-W00-Package-stderr.log"
if (Test-Path $stdout) { Remove-Item $stdout -Force }
if (Test-Path $stderr) { Remove-Item $stderr -Force }
$proc = Start-Process -FilePath $uat -ArgumentList $argList -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru
$start = Get-Date
while (-not $proc.HasExited) {
    $elapsed = [int]((Get-Date) - $start).TotalSeconds
    if ($elapsed -ge ($TimeoutMinutes * 60)) {
        Write-Host ("W00_PACKAGE_TIMEOUT elapsedSeconds=" + $elapsed)
        taskkill.exe /PID $proc.Id /T /F 2>$null | Out-Null
        throw "W00 package exceeded bounded timeout"
    }
    Write-Host ("W00_PACKAGE_HEARTBEAT elapsedSeconds=" + $elapsed)
    if (Test-Path $stdout) { Get-Content -LiteralPath $stdout -Tail 8 }
    Start-Sleep -Seconds $HeartbeatSeconds
    $proc.Refresh()
}

if (Test-Path $stdout) { Get-Content -LiteralPath $stdout | Set-Content -LiteralPath $log -Encoding UTF8 }
if (Test-Path $stderr) { Get-Content -LiteralPath $stderr | Add-Content -LiteralPath $log -Encoding UTF8 }

if ($proc.ExitCode -ne 0) {
    Write-Host ("W00_PACKAGE_FAIL exit=" + $proc.ExitCode)
    if (Test-Path $log) { Get-Content -LiteralPath $log -Tail 250 }
    exit $proc.ExitCode
}

$exe = Join-Path $archive "WindowsNoEditor\ShireJourney.exe"
if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) { throw "Packaged executable missing after successful UAT: $exe" }
Write-Host ("W00_PACKAGE_PASS elapsedSeconds=" + [int]((Get-Date) - $start).TotalSeconds + " exe=" + $exe)
