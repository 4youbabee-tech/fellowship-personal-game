param([int]$StartupTimeoutSeconds = 240, [int]$CaptureSettleSeconds = 12, [switch]$PIE)
$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$exe = "C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\UE4Editor.exe"
$project = Join-Path $root "ShireJourney.uproject"
$proof = Join-Path $root "Saved\PES002VisualProof"
$shotDir = Join-Path $root "Saved\Screenshots\Windows"
New-Item -ItemType Directory -Force -Path $proof | Out-Null
if (!(Test-Path $exe) -or !(Test-Path $project)) { throw "PES002_EDITOR_OR_PROJECT_MISSING" }
$started = Get-Date
$log = Join-Path $proof "PES002VisualEditor.log"
# A previous run's view=3 marker can be observed before UE truncates its log.
# Clear only this proof's stale files before launch; never kill another writer.
Remove-Item -LiteralPath $log -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath (Join-Path $proof 'GPUProcessMemory.csv') -Force -ErrorAction SilentlyContinue
Get-ChildItem -LiteralPath $proof -Filter 'BagEnd-P1C01-view*-actual-runtime.png' -File |
    Remove-Item -Force
Get-ChildItem -LiteralPath $proof -Filter 'PES002_BagEnd_View*.png' -File | Remove-Item -Force
$arguments = @('"' + $project + '"', '-game', '-windowed', '-ResX=1280', '-ResY=720', '-NoSplash', '-log', '-PES002VisualProof', '-abslog="' + $log + '"')
# UE4.27 editor throttles an unfocused PIE/editor window to exactly 3 FPS.
# Our last run showed 15 frames per 5-second window and ~251ms render-thread
# EventWait although GPU/Total was only ~44ms. For this disposable proof
# process ONLY, disable editor background throttling in its project-local
# user preferences. Restore the original preference file on exit; never
# change the owner's interactive editor performance settings permanently.
$proofEditorSettings = Join-Path $root 'Saved\Config\Windows\EditorPerProjectUserSettings.ini'
$hadProofSettings = Test-Path -LiteralPath $proofEditorSettings
$originalProofSettings = if ($hadProofSettings) {
    [System.IO.File]::ReadAllText($proofEditorSettings)
} else { $null }
if ($PIE) {
    New-Item -ItemType Directory -Force -Path (Split-Path $proofEditorSettings) | Out-Null
    $unthrottledProof = @"

[/Script/UnrealEd.EditorPerformanceSettings]
bThrottleCPUWhenNotForeground=False
[/Script/UnrealEd.EditorPerProjectUserSettings]
bThrottleCPUWhenNotForeground=False
"@
    [System.IO.File]::AppendAllText($proofEditorSettings, $unthrottledProof)
    Write-Host 'PES002_EDITOR_BACKGROUND_THROTTLE_DISABLED proofOnly=true expectedNo3FPSCap=true'
}
if ($PIE) {
    $preview = Join-Path $root 'SHIRE_FAST_PIE_PREVIEW.bat'
    if (!(Test-Path -LiteralPath $preview)) { throw 'PES002_PIE_PREVIEW_BATCH_MISSING' }
    # Own the wrapper and its editor child; never terminate unrelated writers.
    $proc = Start-Process -FilePath $env:ComSpec -ArgumentList ('/d /s /c ""' + $preview + '" --proof"') -PassThru
} else {
    $proc = Start-Process -FilePath $exe -ArgumentList ($arguments -join ' ') -PassThru
}
$gpuSamples = @()
$gpuCounterUnavailable = $false
$editorPid = if ($PIE) { 0 } else { $proc.Id }
try {
    # UE4.27 may spend over a minute rebuilding its local shader/DDC state on
    # the 8 GB runner. Wait for the last of FOUR real screenshot requests,
    # not a hard-coded process lifetime; never fall back to an older PNG.
    $deadline = (Get-Date).AddSeconds($StartupTimeoutSeconds)
    $ready = $false
    while ((Get-Date) -lt $deadline) {
        $proc.Refresh()
        if ($PIE -and $editorPid -eq 0) {
            $child = Get-CimInstance Win32_Process -Filter "ParentProcessId=$($proc.Id)" -ErrorAction SilentlyContinue |
                Where-Object { $_.Name -eq 'UE4Editor.exe' } | Select-Object -First 1
            if ($child) { $editorPid = [int]$child.ProcessId }
        }
        if ($editorPid -gt 0 -and -not $gpuCounterUnavailable) {
            try {
                $counter = Get-Counter -Counter '\GPU Process Memory(*)\Dedicated Usage','\GPU Process Memory(*)\Shared Usage' -ErrorAction Stop
                $owned = @($counter.CounterSamples | Where-Object { $_.InstanceName -like "pid_${editorPid}_*" -and $_.Status -eq 0 })
                if ($owned.Count -gt 0) {
                    $dedicated = ($owned | Where-Object { $_.Path -like '*\Dedicated Usage' } | Measure-Object CookedValue -Sum).Sum
                    $shared = ($owned | Where-Object { $_.Path -like '*\Shared Usage' } | Measure-Object CookedValue -Sum).Sum
                    $gpuSamples += [pscustomobject]@{ utc=(Get-Date).ToUniversalTime().ToString('o'); pid=$editorPid; dedicatedBytes=[int64]$dedicated; sharedBytes=[int64]$shared }
                }
            } catch {
                $gpuCounterUnavailable = $true
                Write-Host "PES002_GPU_PROCESS_MEMORY_UNAVAILABLE reason=$($_.Exception.Message)"
            }
        }
        if ((Test-Path -LiteralPath $log) -and
            (Select-String -Path $log -SimpleMatch -Pattern 'PES002_SCREENSHOT_REQUESTED target=BagEnd view=3' -Quiet) -and
            (!$PIE -or (Select-String -Path $log -SimpleMatch -Pattern 'PES002_PIE_SESSION_ENDED active=0' -Quiet))) {
            $ready = $true
            break
        }
        if ($proc.HasExited) {
            throw "PES002_EDITOR_EXITED_EARLY exitCode=$($proc.ExitCode); inspect $log"
        }
        Start-Sleep -Seconds 3
    }
    if (-not $ready) {
        throw "PES002_CAPTURE_STARTUP_TIMEOUT seconds=$StartupTimeoutSeconds; inspect $log"
    }
    Start-Sleep -Seconds $CaptureSettleSeconds
} finally {
    $proc.Refresh()
    if (!$proc.HasExited) {
        if ($PIE) { & taskkill.exe /PID $proc.Id /T /F | Out-Null }
        else { Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue }
    }
    if ($PIE) {
        if ($hadProofSettings) {
            [System.IO.File]::WriteAllText($proofEditorSettings, $originalProofSettings)
        } else {
            Remove-Item -LiteralPath $proofEditorSettings -Force -ErrorAction SilentlyContinue
        }
        Write-Host 'PES002_EDITOR_BACKGROUND_THROTTLE_RESTORED proofOnly=true'
    }
}
if ($gpuSamples.Count -gt 0) {
    $gpuSamples | Export-Csv -NoTypeInformation -LiteralPath (Join-Path $proof 'GPUProcessMemory.csv')
    $peakDedicated = ($gpuSamples | Measure-Object dedicatedBytes -Maximum).Maximum / 1048576.0
    $peakShared = ($gpuSamples | Measure-Object sharedBytes -Maximum).Maximum / 1048576.0
    Write-Host ("PES002_GPU_PROCESS_MEMORY source=Windows-GPU-Process-Memory pid={0} samples={1} peakDedicatedMiB={2:N2} peakSharedMiB={3:N2} targetDeviceAccepted=false" -f $editorPid,$gpuSamples.Count,$peakDedicated,$peakShared)
}
if ($PIE -and (!(Select-String -Path $log -SimpleMatch -Pattern 'PES002_CAPTURE_WORLD mode=PIE' -Quiet) -or
    !(Select-String -Path $log -SimpleMatch -Pattern 'PES002_PIE_CAPTURE_WINDOW_COMPLETE worldType=PIE' -Quiet))) {
    throw 'PES002_REAL_PIE_WORLD_NOT_PROVEN'
}
$csvCaptures = @(Get-ChildItem -Path (Join-Path $root 'Saved/Profiling/CSV') -Filter '*.csv' -File -Recurse -ErrorAction SilentlyContinue |
    Where-Object { $_.LastWriteTime -ge $started.AddSeconds(-2) })
foreach ($capture in $csvCaptures) {
    Copy-Item -LiteralPath $capture.FullName -Destination (Join-Path $proof ('CPU-GPU-' + $capture.Name)) -Force
    Write-Host "PES002_ENGINE_CSV_PROFILE source=$($capture.FullName) bytes=$($capture.Length) actualCapture=true targetDeviceAccepted=false"
}
if (!(Test-Path $log) -or !(Select-String -Path $log -Pattern 'PES002_CAPTURE_CAMERA_READY target=BagEnd' -Quiet)) {
    throw "PES002_CAPTURE_CAMERA_NOT_CONFIRMED; inspect $log"
}
# Retain original engine pixels even when resolution/acceptance rejects them.
Get-ChildItem -Path $shotDir -Filter 'PES002_BagEnd_View*.png' -File -Recurse -ErrorAction SilentlyContinue |
    Where-Object { $_.LastWriteTime -ge $started.AddSeconds(-2) } |
    ForEach-Object { Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $proof $_.Name) -Force }
for ($view = 0; $view -lt 4; $view++) {
    if (!(Select-String -Path $log -SimpleMatch -Pattern "PES002_CAPTURE_VIEW_READY view=$view target=BagEnd" -Quiet)) {
        throw "PES002_CAPTURE_VIEW_NOT_READY view=$view"
    }
    if (!(Select-String -Path $log -SimpleMatch -Pattern "PES002_SCREENSHOT_REQUESTED target=BagEnd view=$view" -Quiet)) {
        throw "PES002_CAPTURE_SCREENSHOT_REQUEST_NOT_CONFIRMED view=$view"
    }
    $shots = @(Get-ChildItem -Path $shotDir -File -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -like "PES002_BagEnd_View$view*.png" -and $_.LastWriteTime -ge $started.AddSeconds(-2) } |
        Sort-Object LastWriteTime -Descending)
    if ($shots.Count -eq 0) { throw "PES002_BAG_END_SCREENSHOT_MISSING view=$view; inspect $log" }
    $source = $shots[0].FullName
    $bytes = [System.IO.File]::ReadAllBytes($source)
    if ($bytes.Length -lt 24 -or $bytes[0] -ne 137 -or $bytes[1] -ne 80 -or $bytes[2] -ne 78 -or $bytes[3] -ne 71) {
        throw "PES002_SCREENSHOT_NOT_PNG view=$view"
    }
    $width = [int]($bytes[16] * 16777216 + $bytes[17] * 65536 + $bytes[18] * 256 + $bytes[19])
    $height = [int]($bytes[20] * 16777216 + $bytes[21] * 65536 + $bytes[22] * 256 + $bytes[23])
    if ($width -ne 1280 -or $height -ne 720) { throw "PES002_SCREENSHOT_WRONG_DIMENSIONS view=$view width=$width height=$height" }
    $destination = Join-Path $proof "BagEnd-P1C01-view$view-actual-runtime.png"
    Copy-Item $source $destination -Force
    $hash = (Get-FileHash $destination -Algorithm SHA256).Hash
    # Use actual RGB pixels, not file size or success code. Sample only the
    # central frame to avoid bright sky falsely masking black architecture.
    Add-Type -AssemblyName System.Drawing
    $bitmap = [System.Drawing.Bitmap]::FromFile($destination)
    try {
        [double]$total = 0
        [int]$count = 0
        for ($y = 144; $y -lt 648; $y += 24) {
            for ($x = 128; $x -lt 1152; $x += 24) {
                $pixel = $bitmap.GetPixel($x, $y)
                $total += (0.2126 * $pixel.R + 0.7152 * $pixel.G + 0.0722 * $pixel.B)
                $count++
            }
        }
        if ($count -lt 500) { throw "PES002_LUMINANCE_NO_SAMPLES view=$view" }
        $mean = $total / $count
    } finally {
        $bitmap.Dispose()
    }
    Write-Host ("PES002_LUMINANCE_METRIC view={0} mean={1:N2} threshold=35.0 samples={2}" -f $view,$mean,$count)
    if ($mean -lt 35.0) { throw ("PES002_LUMINANCE_TOO_DARK view={0} mean={1:N2}" -f $view,$mean) }
    Write-Host "PES002_BAG_END_CAPTURE_PRESENT view=$view width=$width height=$height sha256=$hash image=$destination camera=BagEnd visualAccepted=false traversal=unproven"
}

# The editor is running the real game RHI and must emit actual frame and RAM
# windows; a screenshot alone is not performance evidence. This CI machine is
# not the target laptop, so no 30-FPS/device or VRAM acceptance is inferred.
$runtimeSamples = @(Select-String -Path $log -SimpleMatch -Pattern 'PES002_RUNTIME_METRICS source=UE4-game-frame')
if ($runtimeSamples.Count -lt 1) {
    throw "PES002_RUNTIME_FRAME_METRICS_MISSING: inspect $log"
}
Write-Host "PES002_RUNTIME_SAMPLE_COUNT count=$($runtimeSamples.Count) deviceAccepted=false gpuVRAM=UNMEASURED"
$runtimeSamples | Select-Object -Last 3 | ForEach-Object { Write-Host $_.Line.Trim() }

# The current PES-002 deliverable is a real data-driven Bag End garden and a
# count of skinned residents. Fail from real PIE log evidence, not a JSON test.
$garden = @(Select-String -Path $log -Pattern 'PES002_BAG_END_DATA_GARDEN loaded=(\d+) placed=(\d+) rejected=(\d+)')
if ($garden.Count -lt 1) { throw 'PES002_GARDEN_PIE_EVIDENCE_MISSING' }
$gardenLine = $garden[-1].Line
$gardenMatch = [regex]::Match($gardenLine, 'PES002_BAG_END_DATA_GARDEN loaded=(\d+) placed=(\d+) rejected=(\d+)')
if (!$gardenMatch.Success -or [int]$gardenMatch.Groups[1].Value -ne 25 -or
    [int]$gardenMatch.Groups[2].Value -lt 1) {
    throw "PES002_GARDEN_WORLD_PLACEMENT_REJECT source=$gardenLine"
}
Write-Host "PES002_REAL_GARDEN_EVIDENCE $($gardenMatch.Value) world=PIE"
$residents = @(Select-String -Path $log -Pattern 'PES002_RESIDENT_PRESENTATION_SNAPSHOT localManaged=(\d+) skeletal=(\d+) modular=(\d+)')
if ($residents.Count -lt 1) { throw 'PES002_RESIDENT_PIE_COUNT_MISSING' }
Write-Host "PES002_REAL_RESIDENT_EVIDENCE $($residents[-1].Line.Trim())"

# Preserve four PNGs before rejecting incorrect curated PBR runtime shaders.
# A bright screenshot with default-grey instanced foliage is still a failure.
if (Select-String -Path $log -SimpleMatch -Pattern 'P1C01_CURATED_NATURE_WORLD families=9' -Quiet) {
    $shaderDefects = @(Select-String -Path $log -Pattern 'M_P1C01VerifiedPBR.*Failed to compile Material|M_P1C01VerifiedPBR.*missing bUsedWithInstancedStaticMeshes')
    if ($shaderDefects.Count -gt 0) {
        $issues = ($shaderDefects | ForEach-Object { $_.Line.Trim() }) -join ' | '
        throw "PES002_CURATED_PBR_DEFAULT_SHADER_FALLBACK count=$($shaderDefects.Count) issues=$issues"
    }
    Write-Host "PES002_CURATED_PBR_RUNTIME_SHADER_NO_FALLBACK_PASS families=9"
}
