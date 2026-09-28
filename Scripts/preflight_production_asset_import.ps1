param(
    [string]$Workspace = $env:GITHUB_WORKSPACE
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if([string]::IsNullOrWhiteSpace($Workspace) -or -not (Test-Path -LiteralPath $Workspace -PathType Container)){
    throw "PRODUCTION_IMPORT_PREFLIGHT_WORKSPACE_INVALID root=$Workspace"
}

$running=@()
foreach($name in @("UE4Editor","UE4Editor-Cmd")){
    $running += @(Get-Process -Name $name -ErrorAction SilentlyContinue)
}
if($running.Count -gt 0){
    $pids=($running | ForEach-Object { $_.Id }) -join ","
    throw "PRODUCTION_IMPORT_PREFLIGHT_EDITOR_RUNNING pids=$pids"
}

$contentRoot=Join-Path $Workspace "Content\Production"
if(-not (Test-Path -LiteralPath $contentRoot -PathType Container)){
    New-Item -ItemType Directory -Path $contentRoot -Force | Out-Null
}

$probe=Join-Path $contentRoot ".ci-import-write-probe.tmp"
try{
    [IO.File]::WriteAllText($probe,"probe")
    if(-not (Test-Path -LiteralPath $probe -PathType Leaf)){ throw "write probe not materialized" }
}
finally{
    if(Test-Path -LiteralPath $probe){ Remove-Item -LiteralPath $probe -Force -ErrorAction SilentlyContinue }
}
if(Test-Path -LiteralPath $probe){ throw "PRODUCTION_IMPORT_PREFLIGHT_PROBE_DELETE_FAIL path=$probe" }

$git=(Get-Command git.exe -ErrorAction SilentlyContinue).Source
if(-not $git){
    foreach($candidate in @("C:\Program Files\Git\cmd\git.exe","C:\Program Files (x86)\Git\cmd\git.exe")){
        if(Test-Path -LiteralPath $candidate -PathType Leaf){ $git=$candidate; break }
    }
}
$tracked=New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
if($git){
    foreach($relative in @(& $git -C $Workspace ls-files -- "Content/Production")){
        if(-not [string]::IsNullOrWhiteSpace([string]$relative)){ [void]$tracked.Add(([string]$relative).Replace("\","/")) }
    }
}

$files=@(Get-ChildItem -LiteralPath $contentRoot -Recurse -File -Filter "*.uasset" -ErrorAction SilentlyContinue)
$clearedReadOnly=0
$locked=@()
$trackedReadonly=@()
foreach($file in $files){
    $relative=$file.FullName.Substring($Workspace.TrimEnd("\").Length+1).Replace("\","/")
    if($file.IsReadOnly){
        if($tracked.Contains($relative)){
            $trackedReadonly += $relative
            continue
        }
        $file.IsReadOnly=$false
        $file.Refresh()
        if($file.IsReadOnly){
            $locked += [ordered]@{path=$relative;reason="readonly_clear_failed"}
            continue
        }
        $clearedReadOnly++
    }

    try{
        $stream=[IO.File]::Open($file.FullName,[IO.FileMode]::Open,[IO.FileAccess]::ReadWrite,[IO.FileShare]::None)
        $stream.Dispose()
    }catch{
        $locked += [ordered]@{path=$relative;reason="exclusive_write_open_failed";detail=$_.Exception.Message}
    }
}

if($trackedReadonly.Count -gt 0){
    foreach($path in $trackedReadonly){ Write-Host ("PRODUCTION_IMPORT_PREFLIGHT_TRACKED_READONLY path="+$path) }
    throw "PRODUCTION_IMPORT_PREFLIGHT_TRACKED_READONLY_FAIL count=$($trackedReadonly.Count)"
}
if($locked.Count -gt 0){
    foreach($entry in $locked){ Write-Host ("PRODUCTION_IMPORT_PREFLIGHT_LOCKED "+($entry | ConvertTo-Json -Compress -Depth 4)) }
    throw "PRODUCTION_IMPORT_PREFLIGHT_LOCK_FAIL count=$($locked.Count)"
}

Write-Host ("PRODUCTION_IMPORT_PREFLIGHT_PASS existingUassets="+$files.Count+" clearedUntrackedReadOnly="+$clearedReadOnly+" locked=0")
exit 0
