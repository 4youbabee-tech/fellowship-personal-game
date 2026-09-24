param(
    [string]$ProjectRoot = $env:GITHUB_WORKSPACE,
    [int]$TimeoutMinutes = 45,
    [int]$HeartbeatSeconds = 30
)

$ErrorActionPreference = "Stop"
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) { throw "ProjectRoot is required" }

$project = Join-Path $ProjectRoot "ShireJourney.uproject"
$uat = "C:\Program Files\Epic Games\UE_4.27\Engine\Build\BatchFiles\RunUAT.bat"
$archive = Join-Path $ProjectRoot "Saved\W00Package"
$runId = if ($env:GITHUB_RUN_ID) { $env:GITHUB_RUN_ID } else { "local" }
$attempt = if ($env:GITHUB_RUN_ATTEMPT) { $env:GITHUB_RUN_ATTEMPT } else { "1" }
$stage = Join-Path $ProjectRoot ("Saved\W00Stage-" + $runId + "-" + $attempt)
$logDir = Join-Path $ProjectRoot "Saved\Logs"
$log = Join-Path $logDir "CI-W00-Package.log"

if (-not (Test-Path -LiteralPath $project -PathType Leaf)) { throw "Project missing: $project" }
if (-not (Test-Path -LiteralPath $uat -PathType Leaf)) { throw "RunUAT missing: $uat" }
New-Item -ItemType Directory -Path $logDir -Force | Out-Null

foreach ($path in @($archive, $stage)) {
    if (Test-Path -LiteralPath $path) {
        try { attrib -R -S -H ($path + "\*") /S /D 2>$null | Out-Null } catch {}
        Remove-Item -LiteralPath $path -Recurse -Force
    }
    New-Item -ItemType Directory -Path $path -Force | Out-Null
}

$probeDir = Join-Path $stage "_write_probe"
New-Item -ItemType Directory -Path $probeDir -Force | Out-Null
$probe = Join-Path $probeDir "probe.txt"
Set-Content -LiteralPath $probe -Value "w00-package-stage-write-probe" -Encoding ASCII
if (-not (Test-Path -LiteralPath $probe -PathType Leaf)) { throw "W00_PACKAGE_PREFLIGHT_FAIL stage write probe missing" }
Remove-Item -LiteralPath $probe -Force
Remove-Item -LiteralPath $probeDir -Force
$runnerIdentity = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$dbghelpSource = "C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\ThirdParty\DbgHelp\dbghelp.dll"
if (-not (Test-Path -LiteralPath $dbghelpSource -PathType Leaf)) {
    throw "W00_DBGHELP_SOURCE_MISSING path=$dbghelpSource"
}

$dbghelpStream = $null
try {
    $dbghelpStream = [System.IO.File]::Open(
        $dbghelpSource,
        [System.IO.FileMode]::Open,
        [System.IO.FileAccess]::Read,
        [System.IO.FileShare]::ReadWrite
    )
    $null = $dbghelpStream.ReadByte()
}
catch {
    throw ("W00_DBGHELP_SOURCE_READ_FAIL identity=" + $runnerIdentity + " path=" + $dbghelpSource + " error=" + $_.Exception.Message)
}
finally {
    if ($null -ne $dbghelpStream) { $dbghelpStream.Dispose() }
}

$dbghelpProbeDir = Join-Path $stage "WindowsNoEditor\Engine\Binaries\ThirdParty\DbgHelp"
New-Item -ItemType Directory -Path $dbghelpProbeDir -Force | Out-Null
$dbghelpProbePath = Join-Path $dbghelpProbeDir "dbghelp.dll"
try {
    [System.IO.File]::WriteAllText($dbghelpProbePath, "shire-w00-dbghelp-destination-probe")
    if (-not (Test-Path -LiteralPath $dbghelpProbePath -PathType Leaf)) {
        throw "exact destination probe was not created"
    }
    $dbghelpDestinationOwner = (Get-Acl -LiteralPath $dbghelpProbeDir).Owner
    Remove-Item -LiteralPath $dbghelpProbePath -Force
}
catch {
    throw ("W00_DBGHELP_DESTINATION_WRITE_FAIL identity=" + $runnerIdentity + " path=" + $dbghelpProbePath + " error=" + $_.Exception.Message)
}

$windowsProbeRoot = Join-Path $stage "WindowsNoEditor"
if (Test-Path -LiteralPath $windowsProbeRoot) {
    Remove-Item -LiteralPath $windowsProbeRoot -Recurse -Force
}
Write-Host ("W00_PACKAGE_PREFLIGHT_PASS stageWritable=true dbghelpSourceReadable=true dbghelpDestinationWritable=true identity=" + $runnerIdentity + " destinationOwner=" + $dbghelpDestinationOwner + " stage=" + $stage)

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
    "-unattended",
    "-nodebuginfo"
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

$proc.WaitForExit()
$proc.Refresh()
$exitCode = $proc.ExitCode
if ($null -eq $exitCode) {
    Write-Host "W00_PACKAGE_EXITCODE_FAIL exitCode=<null>"
    exit 97
}
$exitCode = [int]$exitCode

if (Test-Path $stdout) { Get-Content -LiteralPath $stdout | Set-Content -LiteralPath $log -Encoding UTF8 }
if (Test-Path $stderr) { Get-Content -LiteralPath $stderr | Add-Content -LiteralPath $log -Encoding UTF8 }

if ($exitCode -ne 0) {
    Write-Host ("W00_PACKAGE_FAIL exit=" + $exitCode)
    if (Test-Path $log) {
        $dbghelpFailure = @(Select-String -LiteralPath $log -Pattern 'DbgHelp\\dbghelp\.dll' -ErrorAction SilentlyContinue)
        if ($dbghelpFailure.Count -gt 0) {
            Write-Host ("W00_DBGHELP_STAGE_FAILURE_OBSERVED matches=" + $dbghelpFailure.Count + " identity=" + $runnerIdentity)
        }
        Get-Content -LiteralPath $log -Tail 250
    }
    exit $exitCode
}

$exe = Join-Path $archive "WindowsNoEditor\ShireJourney.exe"
if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) { throw "Packaged executable missing after successful UAT: $exe" }
Write-Host ("W00_PACKAGE_PASS elapsedSeconds=" + [int]((Get-Date) - $start).TotalSeconds + " exe=" + $exe)
