param(
    [string]$WarehouseRoot = $env:SHIRE_WAREHOUSE_ROOT,
    [string]$OutputPath = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$manifestPath = Join-Path $root "Data\P1C01VisualProductionMegaWaveV2.json"
if(-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)){
    throw "P1C01_MEGA_WAVE_MANIFEST_MISSING path=$manifestPath"
}
$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
if([int]$manifest.total_slots -lt 150){
    throw "P1C01_MEGA_WAVE_TOO_SMALL slots=$($manifest.total_slots)"
}

if([string]::IsNullOrWhiteSpace($OutputPath)){
    $OutputPath = Join-Path $root "Saved\P1C01VisualProductionMegaWaveReport.json"
}
$outDir = Split-Path -Parent $OutputPath
if($outDir -and -not (Test-Path -LiteralPath $outDir)){
    New-Item -ItemType Directory -Path $outDir -Force | Out-Null
}

$allowedByFamily = @{
    architecture = @(".fbx")
    props = @(".fbx")
    vegetation = @(".fbx")
    materials = @(".png",".tga")
    audio = @(".wav")
    vfx = @(".png",".tga",".fbx")
    animation = @(".fbx")
    creature_support = @(".fbx")
}

$warehouseFiles = @()
if(-not [string]::IsNullOrWhiteSpace($WarehouseRoot) -and (Test-Path -LiteralPath $WarehouseRoot -PathType Container)){
    $warehouseFiles = @(Get-ChildItem -LiteralPath $WarehouseRoot -Recurse -File -ErrorAction SilentlyContinue)
}

$familyCounts = @{}
foreach($slot in @($manifest.slots)){
    $family=[string]$slot.family
    if(-not $familyCounts.ContainsKey($family)){ $familyCounts[$family]=0 }
    $familyCounts[$family]++
}

$candidates = @()
foreach($file in $warehouseFiles){
    $ext = [IO.Path]::GetExtension($file.Name).ToLowerInvariant()
    foreach($family in $allowedByFamily.Keys){
        if($allowedByFamily[$family] -contains $ext){
            $candidates += [ordered]@{
                family=$family
                file=$file.FullName
                extension=$ext
                bytes=$file.Length
                state="CANDIDATE_ONLY_PROVENANCE_QC_REQUIRED"
            }
        }
    }
}

$report=[ordered]@{
    wave_id=$manifest.wave_id
    total_slots=[int]$manifest.total_slots
    warehouse_root=$WarehouseRoot
    warehouse_files_scanned=$warehouseFiles.Count
    raw_format_candidates=$candidates.Count
    family_slot_counts=$familyCounts
    candidates=$candidates
    rule="Candidate discovery is not promotion. Receipt/license/SHA256 and family-specific QC are required before copying into SourceAssets/Production."
}
$report | ConvertTo-Json -Depth 7 | Set-Content -LiteralPath $OutputPath -Encoding UTF8
Write-Host "P1C01_VISUAL_MEGA_WAVE_SCAN_PASS slots=$($manifest.total_slots) warehouseFiles=$($warehouseFiles.Count) candidates=$($candidates.Count) report=$OutputPath"
