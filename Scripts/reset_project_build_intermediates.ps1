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
            $owners += [pscustomobject]@{
                ProcessId = [int]$app.Process.dwProcessId
                AppName = [string]$app.strAppName
                Service = [string]$app.strServiceShortName
            }
        }
        return ,$owners
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

        if ($owners.Count -gt 0) {
            $ownerDetails = ($owners | ForEach-Object { "$($_.AppName)(PID=$($_.ProcessId),Service=$($_.Service))" }) -join ", "
            throw "BUILD_FILE_LOCKED path=$blockedFile owners=[$ownerDetails]; failing immediately without terminating any process."
        }

        $aclDiagnostic = Get-AccessDiagnostic -TargetPath $blockedFile -Identity $identity
        Write-Warning "No live Restart Manager owner holds $blockedFile. Granting Modify only on generated build output $fullPath to runner identity $identity. $aclDiagnostic"
        $grant = & (Join-Path $env:SystemRoot "System32\icacls.exe") $fullPath /grant ($identity + ":(OI)(CI)M") /T /C 2>&1
        $grantExit = $LASTEXITCODE
        if ($grantExit -ne 0) {
            $afterGrantAcl = Get-AccessDiagnostic -TargetPath $blockedFile -Identity $identity
            throw "BUILD_CLEANUP_ACL_REPAIR_FAILED path=$fullPath identity=$identity icaclsExit=$grantExit output=$(($grant -join ' ')) $afterGrantAcl"
        }

        try {
            Remove-Item -LiteralPath $fullPath -Recurse -Force -ErrorAction Stop
        }
        catch {
            $afterGrantAcl = Get-AccessDiagnostic -TargetPath $blockedFile -Identity $identity
            throw "BUILD_CLEANUP_RETRY_FAILED path=$fullPath blockedFile=$blockedFile identity=$identity error=$($_.Exception.Message) $afterGrantAcl"
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
