# Remove project-generated compile products after the Unreal Editor is closed.
# Diagnose file owners immediately. Never wait through repeated blind retries or kill an unknown process.
$ErrorActionPreference = "Stop"

if (-not ("ShireRestartManager" -as [type])) {
    Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
using System.Text;

public static class ShireRestartManager
{
    [StructLayout(LayoutKind.Sequential)]
    public struct RM_UNIQUE_PROCESS
    {
        public int dwProcessId;
        public System.Runtime.InteropServices.ComTypes.FILETIME ProcessStartTime;
    }

    public enum RM_APP_TYPE
    {
        Unknown = 0,
        MainWindow = 1,
        OtherWindow = 2,
        Service = 3,
        Explorer = 4,
        Console = 5,
        Critical = 1000
    }

    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
    public struct RM_PROCESS_INFO
    {
        public RM_UNIQUE_PROCESS Process;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 256)]
        public string strAppName;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 64)]
        public string strServiceShortName;
        public RM_APP_TYPE ApplicationType;
        public uint AppStatus;
        public uint TSSessionId;
        [MarshalAs(UnmanagedType.Bool)]
        public bool bRestartable;
    }

    [DllImport("rstrtmgr.dll", CharSet = CharSet.Unicode)]
    public static extern int RmStartSession(out uint pSessionHandle, int dwSessionFlags, StringBuilder strSessionKey);

    [DllImport("rstrtmgr.dll", CharSet = CharSet.Unicode)]
    public static extern int RmRegisterResources(
        uint dwSessionHandle,
        uint nFiles,
        [MarshalAs(UnmanagedType.LPArray, ArraySubType = UnmanagedType.LPWStr)] string[] rgsFilenames,
        uint nApplications,
        RM_UNIQUE_PROCESS[] rgApplications,
        uint nServices,
        [MarshalAs(UnmanagedType.LPArray, ArraySubType = UnmanagedType.LPWStr)] string[] rgsServiceNames);

    [DllImport("rstrtmgr.dll")]
    public static extern int RmGetList(
        uint dwSessionHandle,
        out uint pnProcInfoNeeded,
        ref uint pnProcInfo,
        [In, Out] RM_PROCESS_INFO[] rgAffectedApps,
        ref uint lpdwRebootReasons);

    [DllImport("rstrtmgr.dll")]
    public static extern int RmEndSession(uint dwSessionHandle);
}
"@
}

function Get-FileLockOwners {
    param([Parameter(Mandatory = $true)][string]$FilePath)

    [uint32]$session = 0
    $sessionKey = New-Object System.Text.StringBuilder ([Guid]::NewGuid().ToString("N"))
    $startResult = [ShireRestartManager]::RmStartSession([ref]$session, 0, $sessionKey)
    if ($startResult -ne 0) {
        throw "Restart Manager session failed with Win32 code $startResult"
    }

    try {
        $registerResult = [ShireRestartManager]::RmRegisterResources(
            $session, 1, [string[]]@($FilePath), 0, $null, 0, $null
        )
        if ($registerResult -ne 0) {
            throw "Restart Manager resource registration failed with Win32 code $registerResult"
        }

        [uint32]$needed = 0
        [uint32]$count = 0
        [uint32]$rebootReasons = 0
        $emptyApps = [Array]::CreateInstance(("ShireRestartManager+RM_PROCESS_INFO" -as [type]), 0)
        $listResult = [ShireRestartManager]::RmGetList(
            $session, [ref]$needed, [ref]$count, $emptyApps, [ref]$rebootReasons
        )
        if ($listResult -eq 234) {
            $count = $needed
            $apps = [Array]::CreateInstance(("ShireRestartManager+RM_PROCESS_INFO" -as [type]), [int]$count)
            $listResult = [ShireRestartManager]::RmGetList(
                $session, [ref]$needed, [ref]$count, $apps, [ref]$rebootReasons
            )
        }
        if ($listResult -ne 0) {
            throw "Restart Manager owner query failed with Win32 code $listResult"
        }

        $owners = @()
        foreach ($app in $apps) {
            $lowBits = [BitConverter]::ToUInt32([BitConverter]::GetBytes([int]$app.Process.ProcessStartTime.dwLowDateTime), 0)
            $highBits = [BitConverter]::ToUInt32([BitConverter]::GetBytes([int]$app.Process.ProcessStartTime.dwHighDateTime), 0)
            [long]$startFileTime = ([long]$highBits * 4294967296L) + [long]$lowBits
            $owners += [pscustomobject]@{
                ProcessId = [int]$app.Process.dwProcessId
                ProcessStartFileTime = $startFileTime
                AppName = [string]$app.strAppName
                Service = [string]$app.strServiceShortName
            }
        }
        return $owners
    }
    finally {
        [void][ShireRestartManager]::RmEndSession($session)
    }
}

function Get-AccessDiagnostic {
    param(
        [Parameter(Mandatory = $true)][string]$TargetPath,
        [Parameter(Mandatory = $true)][string]$Identity
    )

    try {
        $acl = Get-Acl -LiteralPath $TargetPath -ErrorAction Stop
        $rules = @($acl.Access | ForEach-Object {
            "$($_.IdentityReference):$($_.FileSystemRights):$($_.AccessControlType)"
        }) -join "; "
        return "aclOwner=$($acl.Owner) aclRules=[$rules]"
    }
    catch {
        return "aclQueryError=$($_.Exception.Message)"
    }
}

$workspace = [IO.Path]::GetFullPath($env:GITHUB_WORKSPACE).TrimEnd('\')
$identity = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$cleanupStartFileTime = (Get-Date).ToUniversalTime().ToFileTimeUtc()
$projectPath = Join-Path $workspace "ShireJourney.uproject"
$paths = @(
    (Join-Path $workspace "Intermediate\Build\Win64"),
    (Join-Path $workspace "Binaries\Win64")
)

foreach ($path in $paths) {
    if (-not (Test-Path -LiteralPath $path)) {
        continue
    }

    $fullPath = [IO.Path]::GetFullPath($path)
    if (-not $fullPath.StartsWith($workspace + '\', [StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to clean a build path outside GITHUB_WORKSPACE: $fullPath"
    }

    Write-Host "Removing stale project build product: $fullPath"
    try {
        Remove-Item -LiteralPath $fullPath -Recurse -Force -ErrorAction Stop
    }
    catch {
        $deleteError = $_.Exception.Message
        $leafMatch = [regex]::Match($deleteError, "'(?<leaf>[^']+)' is denied", [Text.RegularExpressions.RegexOptions]::IgnoreCase)
        if (-not $leafMatch.Success) {
            throw "BUILD_CLEANUP_DIAGNOSTIC path=$fullPath identity=$identity error=$deleteError"
        }

        $leaf = [IO.Path]::GetFileName($leafMatch.Groups['leaf'].Value)
        $blockedFiles = @(Get-ChildItem -LiteralPath $fullPath -Filter $leaf -File -Recurse -ErrorAction SilentlyContinue)
        if ($blockedFiles.Count -ne 1) {
            throw "BUILD_CLEANUP_DIAGNOSTIC path=$fullPath deniedLeaf=$leaf matchingFiles=$($blockedFiles.Count) identity=$identity error=$deleteError"
        }

        $blockedFile = $blockedFiles[0].FullName
        try {
            $owners = @(Get-FileLockOwners -FilePath $blockedFile)
        }
        catch {
            $aclDiagnostic = Get-AccessDiagnostic -TargetPath $blockedFile -Identity $identity
            throw "BUILD_CLEANUP_DIAGNOSTIC path=$blockedFile identity=$identity lockQuery=unavailable detail=$($_.Exception.Message) $aclDiagnostic"
        }

        $verifiedOrphans = @()
        $unknownLiveOwners = @()
        foreach ($owner in $owners) {
            $process = Get-Process -Id $owner.ProcessId -ErrorAction SilentlyContinue
            if (-not $process) {
                continue
            }

            try {
                [long]$observedStartFileTime = $process.StartTime.ToUniversalTime().ToFileTimeUtc()
            }
            catch {
                $unknownLiveOwners += $owner
                continue
            }

            if ($observedStartFileTime -ne $owner.ProcessStartFileTime) {
                continue
            }

            $candidate = Get-CimInstance Win32_Process -Filter ("ProcessId = " + $owner.ProcessId) -ErrorAction SilentlyContinue
            if (-not $candidate) {
                $unknownLiveOwners += $owner
                continue
            }

            try {
                $ownerResult = Invoke-CimMethod -InputObject $candidate -MethodName GetOwner -ErrorAction Stop
                $candidateOwner = if ($ownerResult.ReturnValue -eq 0) { $ownerResult.Domain + '\' + $ownerResult.User } else { '' }
                $parent = Get-CimInstance Win32_Process -Filter ("ProcessId = " + $candidate.ParentProcessId) -ErrorAction SilentlyContinue
                $commandLine = [string]$candidate.CommandLine
                $engineMatch = $candidate.ExecutablePath -match '(?i)\\UE_4\.27\\Engine\\Binaries\\Win64\\UE4Editor-Cmd\.exe$'
                $projectMatch = $commandLine.IndexOf($projectPath, [StringComparison]::OrdinalIgnoreCase) -ge 0
                $ciFlags = ($commandLine -match '(?i)(?:^|\s)-AuditPendingTransition(?:\s|$)') -and ($commandLine -match '(?i)(?:^|\s)-ShireCIAssetReadyDelay=2\.0(?:\s|$)')
                $orphanCiCommandlet = ($candidate.ProcessId -eq $owner.ProcessId) -and ($observedStartFileTime -eq $owner.ProcessStartFileTime) -and ($candidateOwner -ieq $identity) -and $engineMatch -and $projectMatch -and $ciFlags -and (-not $parent) -and ($observedStartFileTime -lt $cleanupStartFileTime)
                if ($orphanCiCommandlet) {
                    $verifiedOrphans += [pscustomobject]@{ ProcessId = $owner.ProcessId; StartFileTime = $observedStartFileTime; AppName = $owner.AppName }
                }
                else {
                    $unknownLiveOwners += $owner
                }
            }
            catch {
                $unknownLiveOwners += $owner
            }
        }

        if ($unknownLiveOwners.Count -gt 0) {
            $ownerDetails = ($unknownLiveOwners | ForEach-Object { "$($_.AppName)(PID=$($_.ProcessId),StartFileTime=$($_.ProcessStartFileTime),Service=$($_.Service))" }) -join ", "
            throw "BUILD_FILE_LOCKED path=$blockedFile owners=[$ownerDetails]; failing immediately without terminating any process."
        }

        foreach ($orphan in $verifiedOrphans) {
            $current = Get-Process -Id $orphan.ProcessId -ErrorAction SilentlyContinue
            $sameProcess = $false
            if ($current) {
                try {
                    $current.Refresh()
                    $sameProcess = (-not $current.HasExited) -and ($current.StartTime.ToUniversalTime().ToFileTimeUtc() -eq $orphan.StartFileTime)
                }
                catch {
                    $sameProcess = $true
                }
            }

            if ($sameProcess) {
                Write-Warning "Releasing verified orphan Shire CI commandlet PID=$($orphan.ProcessId) after exact engine/project/owner/command-line/start-time checks."
                Stop-Process -Id $orphan.ProcessId -Force -ErrorAction SilentlyContinue
                $current = Get-Process -Id $orphan.ProcessId -ErrorAction SilentlyContinue
                $sameProcess = $false
                if ($current) {
                    try {
                        $current.Refresh()
                        $sameProcess = (-not $current.HasExited) -and ($current.StartTime.ToUniversalTime().ToFileTimeUtc() -eq $orphan.StartFileTime)
                    }
                    catch {
                        $sameProcess = $true
                    }
                }

                if ($sameProcess) {
                    $previousErrorActionPreference = $ErrorActionPreference
                    try {
                        $ErrorActionPreference = "Continue"
                        $taskkillOutput = & (Join-Path $env:SystemRoot "System32\taskkill.exe") /PID $orphan.ProcessId /F 2>&1
                        $taskkillExit = $LASTEXITCODE
                    }
                    finally {
                        $ErrorActionPreference = $previousErrorActionPreference
                    }

                    $current = Get-Process -Id $orphan.ProcessId -ErrorAction SilentlyContinue
                    $sameProcess = $false
                    if ($current) {
                        try {
                            $current.Refresh()
                            $sameProcess = (-not $current.HasExited) -and ($current.StartTime.ToUniversalTime().ToFileTimeUtc() -eq $orphan.StartFileTime)
                        }
                        catch {
                            $sameProcess = $true
                        }
                    }

                    if ($sameProcess) {
                        $taskkillDetail = ($taskkillOutput | ForEach-Object { [string]$_ }) -join ' '
                        throw "BUILD_ORPHAN_RELEASE_FAILED PID=$($orphan.ProcessId) taskkillExit=$taskkillExit detail=$taskkillDetail; exact process remains live."
                    }
                }
            }
        }

        $retriedAfterOwnerExit = $false
        if ($owners.Count -gt 0) {
            $endedDetails = ($owners | ForEach-Object { "$($_.AppName)(PID=$($_.ProcessId))" }) -join ", "
            Write-Warning "Restart Manager owners are no longer live or were safely released for $($blockedFile): [$endedDetails]. Retrying cleanup once immediately."
            try {
                Remove-Item -LiteralPath $fullPath -Recurse -Force -ErrorAction Stop
                $retriedAfterOwnerExit = $true
            }
            catch {
                $deleteError = $_.Exception.Message
            }
        }

        if (-not $retriedAfterOwnerExit) {
            $aclDiagnostic = Get-AccessDiagnostic -TargetPath $blockedFile -Identity $identity
            Write-Warning "No live Restart Manager owner holds $($blockedFile). Granting Modify only on generated build output $fullPath to runner identity $identity. $aclDiagnostic"
            $grant = & (Join-Path $env:SystemRoot "System32\\icacls.exe") $fullPath /grant ($identity + ":(OI)(CI)M") /T /C 2>&1
            $grantExit = $LASTEXITCODE
            if ($grantExit -ne 0) {
                $afterGrantAcl = Get-AccessDiagnostic -TargetPath $blockedFile -Identity $identity
                throw "BUILD_CLEANUP_ACL_REPAIR_FAILED path=$fullPath identity=$identity icaclsExit=$grantExit output=$(($grant -join ' ')) $afterGrantAcl"
            }

            # Build outputs may retain a short-lived kernel file handle after the exact
            # orphan owner has exited. Repair the generated DLL ACL too, then retry only
            # this bounded transient window instead of failing on the first stale handle.
            $fileGrant = & (Join-Path $env:SystemRoot "System32\\icacls.exe") $blockedFile /grant ("${identity}:(F)") /C 2>&1
            $fileGrantExit = $LASTEXITCODE
            if ($fileGrantExit -ne 0) {
                $afterGrantAcl = Get-AccessDiagnostic -TargetPath $blockedFile -Identity $identity
                throw "BUILD_CLEANUP_FILE_ACL_REPAIR_FAILED path=$blockedFile identity=$identity icaclsExit=$fileGrantExit output=$(($fileGrant -join ' ')) $afterGrantAcl"
            }

            $cleanupError = $null
            for ($attempt = 1; $attempt -le 4; $attempt++) {
                try {
                    Remove-Item -LiteralPath $fullPath -Recurse -Force -ErrorAction Stop
                    $cleanupError = $null
                    break
                }
                catch {
                    $cleanupError = $_.Exception.Message
                    if (($attempt -lt 4) -and ($owners.Count -gt 0) -and ($cleanupError -match '(?i)access.*denied|being used by another process')) {
                        $delayMs = [int](250 * [Math]::Pow(2, $attempt - 1))
                        Write-Warning "Generated build cleanup is still settling after a verified owner exit; retry $($attempt + 1)/4 in ${delayMs}ms."
                        Start-Sleep -Milliseconds $delayMs
                        continue
                    }
                    break
                }
            }

            if ($null -ne $cleanupError) {
                $afterGrantAcl = Get-AccessDiagnostic -TargetPath $blockedFile -Identity $identity
                throw "BUILD_CLEANUP_RETRY_FAILED path=$fullPath blockedFile=$blockedFile identity=$identity attempts=$attempt error=$cleanupError $afterGrantAcl"
            }
        }
    }

    if (Test-Path -LiteralPath $fullPath) {
        throw "Stale project build product still exists after one cleanup attempt: $fullPath"
    }
}

$logDir = Join-Path $workspace "Saved\Logs"
if (Test-Path -LiteralPath $logDir) {
    Get-ChildItem -LiteralPath $logDir -Filter "CI-*.log" -File -ErrorAction SilentlyContinue |
        ForEach-Object {
            Write-Host "Removing stale CI evidence log: $($_.FullName)"
            Remove-Item -LiteralPath $_.FullName -Force
        }
    Get-ChildItem -LiteralPath $logDir -Filter "CI-*-result.json" -File -ErrorAction SilentlyContinue |
        ForEach-Object {
            Write-Host "Removing stale CI result file: $($_.FullName)"
            Remove-Item -LiteralPath $_.FullName -Force
        }
}
Write-Host "Project build intermediates and stale CI evidence reset."
exit 0
