param([Parameter(Mandatory=$true)][ValidateSet('stage','activate')][string]$Phase)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$root=$env:GITHUB_WORKSPACE
if([string]::IsNullOrWhiteSpace($root)){ $root=Split-Path $PSScriptRoot -Parent }
$warehouse='D:\actions-runner\_warehouse\ShireJourney'
$pythonCandidates=@('D:\actions-runner\_work\_tool\Python\3.11.9\x64\python.exe')
if($env:RUNNER_TOOL_CACHE){$pythonCandidates+=(Join-Path $env:RUNNER_TOOL_CACHE 'Python\3.11.9\x64\python.exe')}
foreach($tool in @(Get-Command python.exe -All -ErrorAction SilentlyContinue)){if($tool -and $tool.Source){$pythonCandidates += [string]$tool.Source}}
$python=$null
foreach($candidate in @($pythonCandidates | Select-Object -Unique)){
  if($candidate -and $candidate -notmatch '(?i)\\Microsoft\\WindowsApps\\' -and
     (Test-Path -LiteralPath $candidate -PathType Leaf)){
    & $candidate -c 'import sys;sys.exit(0 if sys.version_info >= (3,9) else 1)'
    if($LASTEXITCODE -eq 0){$python=$candidate;break}
  }
}
if(-not $python){throw 'P1C01_VERIFIED_PBR_PYTHON_MISSING'}
if($Phase -eq 'stage'){
  $script=Join-Path $root 'Scripts\stage_p1c01_verified_pbr_into_unreal.py'
  & $python $script --warehouse-root $warehouse --project-root $root --max-items 9
}else{
  $script=Join-Path $root 'Scripts\activate_p1c01_verified_pbr_unreal.py'
  & $python $script $root
}
if($LASTEXITCODE -ne 0){throw "P1C01_VERIFIED_PBR_PHASE_FAILED phase=$Phase exit=$LASTEXITCODE"}
Write-Host "P1C01_VERIFIED_PBR_PHASE_PASS phase=$Phase"
