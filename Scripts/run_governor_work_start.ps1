param(
 [Parameter(Mandatory=$true)]
 [ValidateSet('RUNTIME_BUILD','WAREHOUSE_ASSET_INTAKE','SKELETAL_CHARACTER_PREP','VISUAL_WORLD_PREP','GAMEPLAY_PRESENTATION_PREP')]
 [string]$Lane,
 [string]$Workspace = ''
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
if([string]::IsNullOrWhiteSpace($Workspace)){$Workspace=Split-Path $PSScriptRoot -Parent}
$entry=Join-Path $Workspace 'Scripts\governor_work_start.py'
if(-not (Test-Path -LiteralPath $entry -PathType Leaf)){throw 'MANAGER_ENTRY_MISSING'}
$candidates=@('D:\actions-runner\_work\_tool\Python\3.11.9\x64\python.exe')
if($env:RUNNER_TOOL_CACHE){$candidates+=(Join-Path $env:RUNNER_TOOL_CACHE 'Python\3.11.9\x64\python.exe')}
foreach($x in @(Get-Command python.exe -All -ErrorAction SilentlyContinue)){if($x -and $x.Source){$candidates += [string]$x.Source}}
foreach($py in @($candidates | Select-Object -Unique)){
 if(-not $py -or $py -match '(?i)\\Microsoft\\WindowsApps\\' -or -not (Test-Path -LiteralPath $py -PathType Leaf)){continue}
 & $py -c 'import sys;sys.exit(0 if sys.version_info >= (3,9) else 1)' 2>$null
 if($LASTEXITCODE -ne 0){continue}
 & $py $entry --lane $Lane
 if($LASTEXITCODE -ne 0){throw "GOVERNOR_WORK_START_REJECTED lane=$Lane"}
 Write-Host "GOVERNOR_WORK_START_WRAPPER_PASS lane=$Lane"
 exit 0
}
throw 'MANAGER_PYTHON_MISSING'
