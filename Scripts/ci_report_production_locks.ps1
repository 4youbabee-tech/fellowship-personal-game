param(
    [Parameter(Mandatory = $true)]
    [string]$Root
)

$ErrorActionPreference = 'Stop'
$resolvedRoot = Resolve-Path -LiteralPath $Root -ErrorAction SilentlyContinue
if (-not $resolvedRoot) {
    Write-Output "PRODUCTION_LOCK_SCAN_SKIP reason=root-not-found root=$Root"
    exit 0
}

try {
    $resources = @(
        Get-ChildItem -LiteralPath $resolvedRoot.Path -File -Recurse -Force -ErrorAction Stop |
            ForEach-Object { $_.FullName }
    )
} catch {
    Write-Output "PRODUCTION_LOCK_SCAN_ERROR api=EnumerateFiles detail=$($_.Exception.Message)"
    exit 81
}
if ($resources.Count -eq 0) {
    Write-Output "PRODUCTION_LOCK_SCAN_SKIP reason=no-files root=$Root"
    exit 0
}

try {
    Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;

namespace ShireProductionLocks
{
    [StructLayout(LayoutKind.Sequential)]
    public struct FileTime
    {
        public uint LowDateTime;
        public uint HighDateTime;
    }

    [StructLayout(LayoutKind.Sequential)]
    public struct UniqueProcess
    {
        public int ProcessId;
        public FileTime ProcessStartTime;
    }

    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
    public struct ProcessInfo
    {
        public UniqueProcess Process;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 256)]
        public string AppName;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 64)]
        public string ServiceShortName;
        public uint ApplicationType;
        public uint AppStatus;
        public uint SessionId;
        [MarshalAs(UnmanagedType.Bool)]
        public bool Restartable;
    }

    public static class RestartManager
    {
        [DllImport("rstrtmgr.dll", CharSet = CharSet.Unicode)]
        public static extern int RmStartSession(
            out uint sessionHandle,
            int flags,
            string sessionKey);

        [DllImport("rstrtmgr.dll", CharSet = CharSet.Unicode)]
        public static extern int RmRegisterResources(
            uint sessionHandle,
            uint fileCount,
            string[] fileNames,
            uint applicationCount,
            UniqueProcess[] applications,
            uint serviceCount,
            string[] serviceNames);

        [DllImport("rstrtmgr.dll", CharSet = CharSet.Unicode)]
        public static extern int RmGetList(
            uint sessionHandle,
            ref uint processInfoNeeded,
            ref uint processInfoCount,
            [In, Out] ProcessInfo[] processInfo,
            ref uint rebootReasons);

        [DllImport("rstrtmgr.dll")]
        public static extern int RmEndSession(uint sessionHandle);
    }
}
'@ -ErrorAction Stop | Out-Null
} catch {
    Write-Output "PRODUCTION_LOCK_SCAN_ERROR api=Add-Type detail=$($_.Exception.ToString())"
    exit 80
}

$reported = @{}
$scanErrors = $false
$batchSize = 100
for ($offset = 0; $offset -lt $resources.Count; $offset += $batchSize) {
    $end = [Math]::Min($offset + $batchSize - 1, $resources.Count - 1)
    $batch = [string[]]$resources[$offset..$end]
    [uint32]$sessionHandle = 0
    $sessionKey = [Guid]::NewGuid().ToString()
    $code = [ShireProductionLocks.RestartManager]::RmStartSession(
        [ref]$sessionHandle,
        0,
        $sessionKey)
    if ($code -ne 0) {
        $scanErrors = $true
        Write-Output "PRODUCTION_LOCK_SCAN_ERROR api=RmStartSession code=$code"
        continue
    }

    try {
        $code = [ShireProductionLocks.RestartManager]::RmRegisterResources(
            $sessionHandle,
            [uint32]$batch.Length,
            $batch,
            [uint32]0,
            $null,
            [uint32]0,
            $null)
        if ($code -ne 0) {
            $scanErrors = $true
            Write-Output "PRODUCTION_LOCK_SCAN_ERROR api=RmRegisterResources code=$code batch=$offset"
            continue
        }

        [uint32]$needed = 0
        [uint32]$count = 0
        [uint32]$rebootReasons = 0
        $code = [ShireProductionLocks.RestartManager]::RmGetList(
            $sessionHandle,
            [ref]$needed,
            [ref]$count,
            $null,
            [ref]$rebootReasons)
        if ($code -eq 234 -and $needed -gt 0) {
            $processInfo = New-Object 'ShireProductionLocks.ProcessInfo[]' ([int]$needed)
            $count = $needed
            $code = [ShireProductionLocks.RestartManager]::RmGetList(
                $sessionHandle,
                [ref]$needed,
                [ref]$count,
                $processInfo,
                [ref]$rebootReasons)
            if ($code -eq 0) {
                for ($index = 0; $index -lt $count; $index++) {
                    $process = $processInfo[$index]
                    $key = "$($process.Process.ProcessId)|$($process.AppName)"
                    if (-not $reported.ContainsKey($key)) {
                        $reported[$key] = $true
                        Write-Output "PRODUCTION_LOCK_SCAN_PROCESS pid=$($process.Process.ProcessId) app=$($process.AppName) service=$($process.ServiceShortName)"
                    }
                }
            }
        } elseif ($code -eq 0 -and $count -eq 0) {
            Write-Output "PRODUCTION_LOCK_SCAN_BATCH_CLEAR offset=$offset count=$($batch.Length)"
        } elseif ($code -ne 0) {
            $scanErrors = $true
            Write-Output "PRODUCTION_LOCK_SCAN_ERROR api=RmGetList code=$code batch=$offset"
        }
    } catch {
        $scanErrors = $true
        Write-Output "PRODUCTION_LOCK_SCAN_ERROR exception=$($_.Exception.Message)"
    } finally {
        [void][ShireProductionLocks.RestartManager]::RmEndSession($sessionHandle)
    }
}

if ($scanErrors) {
    Write-Output "PRODUCTION_LOCK_SCAN_RESULT incomplete resources=$($resources.Count)"
    exit 82
}
if ($reported.Count -eq 0) {
    Write-Output "PRODUCTION_LOCK_SCAN_RESULT no-file-locks-reported resources=$($resources.Count)"
} else {
    Write-Output "PRODUCTION_LOCK_SCAN_RESULT processes=$($reported.Count) resources=$($resources.Count)"
}
