param(
    [string]$Workspace = $env:GITHUB_WORKSPACE,
    [int]$TimeoutMinutes = 20,
    [int]$StaleCommandletMinutes = 20
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-UnrealProcessSnapshots {
    $items = @()
    foreach($name in @("UE4Editor","UE4Editor-Cmd")){
        foreach($process in @(Get-Process -Name $name -ErrorAction SilentlyContinue)){
            $cim = Get-CimInstance Win32_Process -Filter ("ProcessId = " + $process.Id) -ErrorAction SilentlyContinue
            $owner = "unknown"
            $commandLine = ""
            $parentPid = 0
            $sessionId = $process.SessionId
            $created = $process.StartTime
            if($cim){
                $commandLine = [string]$cim.CommandLine
                $parentPid = [int]$cim.ParentProcessId
                $sessionId = [int]$cim.SessionId
                try {
                    $ownerResult = Invoke-CimMethod -InputObject $cim -MethodName GetOwner -ErrorAction Stop
                    if($ownerResult -and -not [string]::IsNullOrWhiteSpace([string]$ownerResult.User)){
                        $owner = if([string]::IsNullOrWhiteSpace([string]$ownerResult.Domain)){
                            [string]$ownerResult.User
                        } else {
                            ([string]$ownerResult.Domain) + "\" + ([string]$ownerResult.User)
                        }
                    }
                } catch {}
            }
            $items += [pscustomobject]@{
                Name = [string]$process.ProcessName
                Id = [int]$process.Id
                ParentProcessId = $parentPid
                SessionId = $sessionId
                Owner = $owner
                StartTime = $created
                CommandLine = $commandLine
            }
        }
    }
    return @($items)
}

function Write-UnrealProcessDiagnostic($snapshot, [string]$prefix) {
    $ageSeconds = [math]::Max(0, [int]((Get-Date) - $snapshot.StartTime).TotalSeconds)
    $cmd = ([string]$snapshot.CommandLine).Replace([char]13," ").Replace([char]10," ")
    Write-Host ($prefix +
        " name=" + $snapshot.Name +
        " pid=" + $snapshot.Id +
        " ppid=" + $snapshot.ParentProcessId +
        " sessionId=" + $snapshot.SessionId +
        " owner=" + $snapshot.Owner +
        " ageSeconds=" + $ageSeconds +
        " commandLine=" + $cmd)
}

function Test-StaleOwnedCommandlet($snapshot) {
    if($snapshot.Name -ne "UE4Editor-Cmd"){ return $false }
    if([string]::IsNullOrWhiteSpace([string]$snapshot.CommandLine)){ return $false }
    if([string]::IsNullOrWhiteSpace($Workspace)){ return $false }

    $cmd = [string]$snapshot.CommandLine
    $workspaceOwned = $cmd.IndexOf($Workspace, [StringComparison]::OrdinalIgnoreCase) -ge 0
    $projectOwned = $cmd.IndexOf("ShireJourney.uproject", [StringComparison]::OrdinalIgnoreCase) -ge 0
    $unattended = $cmd.IndexOf("-unattended", [StringComparison]::OrdinalIgnoreCase) -ge 0
    $knownCiCommandlet =
        $cmd.IndexOf("-run=ShireProductionImport", [StringComparison]::OrdinalIgnoreCase) -ge 0 -or
        $cmd.IndexOf("-ExecCmds=Automation", [StringComparison]::OrdinalIgnoreCase) -ge 0 -or
        $cmd.IndexOf("-nullrhi", [StringComparison]::OrdinalIgnoreCase) -ge 0

    $ageMinutes = ((Get-Date) - $snapshot.StartTime).TotalMinutes
    $currentIdentity = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
    $sameOwner = -not [string]::IsNullOrWhiteSpace([string]$snapshot.Owner) -and
        ([string]$snapshot.Owner).Equals($currentIdentity, [StringComparison]::OrdinalIgnoreCase)
    $parentAlive = $false
    if($snapshot.ParentProcessId -gt 0){
        $parentAlive = $null -ne (Get-Process -Id $snapshot.ParentProcessId -ErrorAction SilentlyContinue)
    }

    return $workspaceOwned -and $projectOwned -and $unattended -and $knownCiCommandlet -and
        $sameOwner -and (-not $parentAlive) -and $ageMinutes -ge $StaleCommandletMinutes
}

$deadline = (Get-Date).AddMinutes($TimeoutMinutes)
while($true){
    $snapshots = @(Get-UnrealProcessSnapshots)
    if($snapshots.Count -eq 0){
        Write-Host "UNREAL_PROCESS_WAIT_PASS editors=0 commandlets=0"
        exit 0
    }

    $recovered = 0
    foreach($snapshot in $snapshots){
        Write-UnrealProcessDiagnostic $snapshot "UNREAL_PROCESS_DIAGNOSTIC"
        if(Test-StaleOwnedCommandlet $snapshot){
            Write-Host ("UNREAL_STALE_CI_COMMANDLET_RECOVERY_BEGIN pid=" + $snapshot.Id)
            Stop-Process -Id $snapshot.Id -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 2
            if(Get-Process -Id $snapshot.Id -ErrorAction SilentlyContinue){
                Write-Host ("UNREAL_STALE_CI_COMMANDLET_TASKKILL_FALLBACK pid=" + $snapshot.Id)
                $taskkill = Start-Process -FilePath "taskkill.exe" -ArgumentList @("/PID",[string]$snapshot.Id,"/T","/F") -NoNewWindow -Wait -PassThru
                Write-Host ("UNREAL_STALE_CI_COMMANDLET_TASKKILL_RESULT pid=" + $snapshot.Id + " exit=" + $taskkill.ExitCode)
                Start-Sleep -Seconds 2
            }
            if(Get-Process -Id $snapshot.Id -ErrorAction SilentlyContinue){
                throw ("UNREAL_STALE_CI_COMMANDLET_RECOVERY_FAIL pid=" + $snapshot.Id)
            }
            Write-Host ("UNREAL_STALE_CI_COMMANDLET_RECOVERED pid=" + $snapshot.Id)
            $recovered++
        }
    }

    if($recovered -gt 0){
        Start-Sleep -Seconds 1
        continue
    }

    if((Get-Date) -ge $deadline){
        $pids = ($snapshots | ForEach-Object { $_.Id }) -join ","
        throw ("UNREAL_PROCESS_WAIT_TIMEOUT pids=" + $pids + " action=close-interactive-editor-or-investigate-non-orphan-commandlet")
    }

    Write-Host "UNREAL_PROCESS_WAIT active=true sleepSeconds=10 policy=never-kill-interactive-editor"
    Start-Sleep -Seconds 10
}
