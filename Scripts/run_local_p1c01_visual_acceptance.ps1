param(
    [string]$EvidenceRoot = "",
    [string]$UERoot = "C:\Program Files\Epic Games\UE_4.27",
    [switch]$SkipImport
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path $PSScriptRoot -Parent
$Project = Join-Path $ProjectRoot "ShireJourney.uproject"
$Editor = Join-Path $UERoot "Engine\Binaries\Win64\UE4Editor.exe"
$EditorCmd = Join-Path $UERoot "Engine\Binaries\Win64\UE4Editor-Cmd.exe"
$Importer = Join-Path $ProjectRoot "Scripts\ci_import_production_assets.cmd"
$FrodoSourceRoot = Join-Path $ProjectRoot "SourceAssets\ValidatedRuntime\FRODO"
$FrodoTargetFbx = Join-Path $FrodoSourceRoot "SK_FRODO_Validated.fbx"
$FrodoAnimationDir = $FrodoSourceRoot
$RouteContract = Join-Path $ProjectRoot "Data\P1C01LocalVisualAcceptanceRouteV1.json"
$env:GITHUB_WORKSPACE = $ProjectRoot

if($env:OS -ne "Windows_NT"){
    throw "P1C01_LOCAL_ACCEPTANCE_FAIL reason=windows_required"
}
foreach($Required in @($Project,$Editor,$EditorCmd,$Importer,$RouteContract)){
    if(-not (Test-Path -LiteralPath $Required -PathType Leaf)){
        throw "P1C01_LOCAL_ACCEPTANCE_FAIL reason=required_file_missing path=$Required"
    }
}
if(Get-Process -Name "UE4Editor" -ErrorAction SilentlyContinue){
    throw "P1C01_LOCAL_ACCEPTANCE_FAIL reason=ue4_editor_already_running"
}

$SessionId = Get-Date -Format "yyyyMMdd-HHmmss"
if([string]::IsNullOrWhiteSpace($EvidenceRoot)){
    $EvidenceRoot = Join-Path $ProjectRoot ("Saved\P1C01Acceptance\" + $SessionId)
}
New-Item -ItemType Directory -Path $EvidenceRoot -Force | Out-Null
$EvidenceRoot = (Resolve-Path -LiteralPath $EvidenceRoot).Path
$StartedAt = Get-Date

$Hardware = [ordered]@{
    captured_at_utc = [DateTime]::UtcNow.ToString("o")
    computer = $env:COMPUTERNAME
    os = $null
    cpu = @()
    gpu = @()
    ram_bytes = $null
}
try {
    $Os = Get-CimInstance Win32_OperatingSystem -ErrorAction Stop
    $Hardware.os = [ordered]@{
        caption = [string]$Os.Caption
        version = [string]$Os.Version
        build_number = [string]$Os.BuildNumber
    }
} catch {}
try {
    foreach($Cpu in @(Get-CimInstance Win32_Processor -ErrorAction Stop)){
        $Hardware.cpu += [ordered]@{
            name = [string]$Cpu.Name
            cores = [int]$Cpu.NumberOfCores
            logical_processors = [int]$Cpu.NumberOfLogicalProcessors
        }
    }
} catch {}
try {
    foreach($Gpu in @(Get-CimInstance Win32_VideoController -ErrorAction Stop)){
        $Hardware.gpu += [ordered]@{
            name = [string]$Gpu.Name
            adapter_ram = if($null -ne $Gpu.AdapterRAM){ [int64]$Gpu.AdapterRAM } else { $null }
            driver_version = [string]$Gpu.DriverVersion
        }
    }
} catch {}
try {
    $System = Get-CimInstance Win32_ComputerSystem -ErrorAction Stop
    $Hardware.ram_bytes = [int64]$System.TotalPhysicalMemory
} catch {}
$Hardware | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $EvidenceRoot "hardware.json") -Encoding UTF8

Copy-Item -LiteralPath $RouteContract -Destination (Join-Path $EvidenceRoot "review_route.json") -Force

if(-not $SkipImport){
    Write-Host "P1C01_LOCAL_ACCEPTANCE_IMPORT_BEGIN importer=$Importer"
    & $Importer
    $ImportExit = [int]$LASTEXITCODE
    if($ImportExit -ne 0){
        throw "P1C01_LOCAL_ACCEPTANCE_FAIL reason=production_import exit=$ImportExit"
    }
}

$FrodoRequiredSources = @(
    @($FrodoTargetFbx, "75d715f6ce4673a650a4382bc4f86b7ae0baf0fe548cc63f9b6ded1800f669be"),
    @((Join-Path $FrodoSourceRoot "Frodo_Idle_Retarget.fbx"), "ee81650714587d2a1a638f3ff0c1a8239ea555bf84959e96ce5d037af3f33cd3"),
    @((Join-Path $FrodoSourceRoot "Frodo_Walk_Retarget.fbx"), "c4091b7881a4e9e810e70bb7f3abed58683dff5bacf54e26ccb2e926e4c9e688"),
    @((Join-Path $FrodoSourceRoot "Frodo_Run_Retarget.fbx"), "4a4d10d91343dbd701c535d30ea9d9384ca74596cd7720cf6bfdd1c6328e1fc1")
)
foreach($Row in $FrodoRequiredSources){
    if(-not (Test-Path -LiteralPath $Row[0] -PathType Leaf)){
        throw "P1C01_LOCAL_ACCEPTANCE_FAIL reason=frodo_validated_source_missing path=$($Row[0])"
    }
    $Actual=(Get-FileHash -LiteralPath $Row[0] -Algorithm SHA256).Hash.ToLowerInvariant()
    if($Actual -ne $Row[1]){
        throw "P1C01_LOCAL_ACCEPTANCE_FAIL reason=frodo_validated_source_hash_mismatch path=$($Row[0])"
    }
}

if(-not $SkipImport){
    $FrodoImportLog = Join-Path $EvidenceRoot "P1C01-FrodoRuntimeImport.log"
    Write-Host "P1C01_LOCAL_FRODO_IMPORT_BEGIN target=$FrodoTargetFbx"
    & $EditorCmd $Project "-run=ShireFrodoAnimationImport" "-TargetFbx=$FrodoTargetFbx" "-AnimationDir=$FrodoAnimationDir" "-unattended" "-nop4" "-nosplash" "-NoSound" "-abslog=$FrodoImportLog"
    $FrodoImportExit=[int]$LASTEXITCODE
    if($FrodoImportExit -ne 0){
        throw "P1C01_LOCAL_ACCEPTANCE_FAIL reason=frodo_runtime_import exit=$FrodoImportExit"
    }
    $FrodoImportText=Get-Content -LiteralPath $FrodoImportLog -Raw
    if($FrodoImportText -notmatch "UE4_ANIMATION_PACKAGE_PERSISTENCE_PASS assets=5" -or
       $FrodoImportText -notmatch "UE4_ANIMATION_IMPORT_TECHNICAL_PASS clips=3 bones=48"){
        throw "P1C01_LOCAL_ACCEPTANCE_FAIL reason=frodo_runtime_import_markers_missing"
    }
}

$FrodoPackages=@(
    (Join-Path $ProjectRoot "Content\Production\Characters\Rigs\FRODO\SK_FRODO.uasset"),
    (Join-Path $ProjectRoot "Content\Production\Characters\Rigs\FRODO\SK_FRODO_Skeleton.uasset"),
    (Join-Path $ProjectRoot "Content\Production\Characters\Animations\FRODO\A_Frodo_Idle.uasset"),
    (Join-Path $ProjectRoot "Content\Production\Characters\Animations\FRODO\A_Frodo_Walk.uasset"),
    (Join-Path $ProjectRoot "Content\Production\Characters\Animations\FRODO\A_Frodo_Run.uasset")
)
foreach($Package in $FrodoPackages){
    if(-not (Test-Path -LiteralPath $Package -PathType Leaf)){
        throw "P1C01_LOCAL_ACCEPTANCE_FAIL reason=frodo_runtime_package_missing path=$Package"
    }
}
Write-Host "P1C01_LOCAL_FRODO_RUNTIME_PACKAGES_PASS assets=5"

$ContentRoot = Join-Path $ProjectRoot "Content\Production"
$GeneratedUassets = if(Test-Path -LiteralPath $ContentRoot){
    @(Get-ChildItem -LiteralPath $ContentRoot -Recurse -File -Filter "*.uasset" -ErrorAction Stop)
}else{
    @()
}
if($GeneratedUassets.Count -lt 1){
    throw "P1C01_LOCAL_ACCEPTANCE_FAIL reason=no_generated_production_uassets root=$ContentRoot"
}

$ReviewTemplate = [ordered]@{
    schema_version = 1
    session_id = $SessionId
    exact_git_head = (& git.exe -C $ProjectRoot rev-parse HEAD 2>$null)
    generated_uasset_count = $GeneratedUassets.Count
    reviewer = ""
    checkpoints = @()
    overall = [ordered]@{
        visual_acceptance = "PENDING_HUMAN_REVIEW"
        pacing_acceptance = "PENDING_HUMAN_REVIEW"
        performance_acceptance = "PENDING_TARGET_DEVICE_MEASUREMENT"
        notes = ""
    }
}
$Route = Get-Content -LiteralPath $RouteContract -Raw | ConvertFrom-Json
foreach($Checkpoint in @($Route.checkpoints)){
    $ReviewTemplate.checkpoints += [ordered]@{
        id = [string]$Checkpoint.id
        location_read = [string]$Checkpoint.location_read
        screenshot_review = "PENDING"
        traversal_readability = "PENDING"
        visual_defects = @()
        notes = ""
    }
}
$ReviewTemplate | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath (Join-Path $EvidenceRoot "human_review_template.json") -Encoding UTF8

Write-Host ""
Write-Host "============================================================"
Write-Host "SHIRE JOURNEY - P1C01 LOCAL VISUAL ACCEPTANCE CAPTURE"
Write-Host "============================================================"
Write-Host "Evidence: $EvidenceRoot"
Write-Host "Map: /Engine/Maps/Entry | DX11 | 1280x720"
Write-Host ""
Write-Host "Walk the route in review_route.json."
Write-Host "At EACH checkpoint open the UE console and run: HighResShot 1"
Write-Host "Before quitting run: stat stopfile"
Write-Host "Stats start automatically: stat fps / stat unit / stat streaming / stat startfile"
Write-Host "This capture does NOT itself mean PIE-TESTED, DEVICE-TESTED, VISUALLY-ACCEPTED or PERFORMANCE-ACCEPTED."
Write-Host ""

$LogPath = Join-Path $EvidenceRoot "P1C01-VisualAcceptance.log"
$ArgumentLine = '"' + $Project + '" /Engine/Maps/Entry -game -log -d3d11 -ResX=1280 -ResY=720 -Windowed -NoSplash ' +
    '-ExecCmds="stat fps,stat unit,stat streaming,stat startfile" -ABSLOG="' + $LogPath + '"'

$Process = Start-Process -FilePath $Editor -ArgumentList $ArgumentLine -PassThru
if($null -eq $Process){
    throw "P1C01_LOCAL_ACCEPTANCE_FAIL reason=launch_failed"
}
Write-Host ("P1C01_LOCAL_ACCEPTANCE_LAUNCHED pid=" + $Process.Id)
$Process.WaitForExit()
$ExitCode = $Process.ExitCode

$ScreenshotOut = Join-Path $EvidenceRoot "Screenshots"
$StatsOut = Join-Path $EvidenceRoot "UnrealStats"
New-Item -ItemType Directory -Path $ScreenshotOut -Force | Out-Null
New-Item -ItemType Directory -Path $StatsOut -Force | Out-Null

$ScreenshotsRoot = Join-Path $ProjectRoot "Saved\Screenshots"
$Screenshots = @()
if(Test-Path -LiteralPath $ScreenshotsRoot){
    foreach($File in @(Get-ChildItem -LiteralPath $ScreenshotsRoot -Recurse -File -Filter "*.png" -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -ge $StartedAt })){
        $Screenshots += $File
        $RelativeParent = Split-Path ($File.FullName.Substring($ScreenshotsRoot.Length).TrimStart('\')) -Parent
        $DestinationDir = if([string]::IsNullOrWhiteSpace($RelativeParent)){ $ScreenshotOut } else { Join-Path $ScreenshotOut $RelativeParent }
        New-Item -ItemType Directory -Path $DestinationDir -Force | Out-Null
        Copy-Item -LiteralPath $File.FullName -Destination (Join-Path $DestinationDir $File.Name) -Force
    }
}

$Stats = @()
$StatsRoot = Join-Path $ProjectRoot "Saved\Profiling\UnrealStats"
if(Test-Path -LiteralPath $StatsRoot){
    foreach($File in @(Get-ChildItem -LiteralPath $StatsRoot -Recurse -File -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -ge $StartedAt })){
        $Stats += $File
        Copy-Item -LiteralPath $File.FullName -Destination (Join-Path $StatsOut $File.Name) -Force
    }
}

$Receipt = [ordered]@{
    schema_version = 1
    session_id = $SessionId
    started_at_utc = $StartedAt.ToUniversalTime().ToString("o")
    ended_at_utc = [DateTime]::UtcNow.ToString("o")
    exact_git_head = $ReviewTemplate.exact_git_head
    ue4_process_exit_code = $ExitCode
    generated_uasset_count = $GeneratedUassets.Count
    screenshot_count = $Screenshots.Count
    unreal_stats_file_count = $Stats.Count
    evidence_root = $EvidenceRoot
    status = "CAPTURE_FINISHED_HUMAN_REVIEW_PENDING"
    pie_tested = $false
    device_tested = $false
    visually_accepted = $false
    performance_accepted = $false
    evidence_boundary = "Local capture session only. Human chapter review and measured target-device acceptance remain explicit separate decisions."
}
$Receipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $EvidenceRoot "capture_receipt.json") -Encoding UTF8

Write-Host ("P1C01_LOCAL_ACCEPTANCE_CAPTURE_FINISHED exit=" + $ExitCode +
    " screenshots=" + $Screenshots.Count +
    " statsFiles=" + $Stats.Count +
    " evidence=" + $EvidenceRoot)
Write-Host "Fill human_review_template.json only after actually reviewing this session."
exit $ExitCode
