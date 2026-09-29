param(
    [string]$ManifestPath = "Data/Part1SequentialRuntimeChapterTrainV1.json",
    [string]$WarehouseRoot = "C:\actions-runner\_warehouse\ShireJourney",
    [string]$ChapterId = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path $PSScriptRoot -Parent
if(-not [IO.Path]::IsPathRooted($ManifestPath)){ $ManifestPath = Join-Path $ProjectRoot $ManifestPath }
if(-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)){ throw "PART1_PREP_MANIFEST_MISSING path=$ManifestPath" }
if(-not (Test-Path -LiteralPath $WarehouseRoot -PathType Container)){ throw "PART1_PREP_WAREHOUSE_MISSING root=$WarehouseRoot" }

$manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
$outputRoot = [string]$manifest.shared_preparation.output_root
if([string]::IsNullOrWhiteSpace($outputRoot)){ $outputRoot = Join-Path $WarehouseRoot "_part1_runtime_chapter_prep_v1" }
New-Item -ItemType Directory -Path $outputRoot -Force | Out-Null

$allowed = @{}
foreach($ext in @($manifest.shared_preparation.allowed_extensions)){ $allowed[[string]$ext.ToLowerInvariant()] = $true }
$blocked = @{}
foreach($ext in @($manifest.shared_preparation.blocked_extensions)){ $blocked[[string]$ext.ToLowerInvariant()] = $true }
$maxCandidates = [int]$manifest.shared_preparation.max_candidates_per_chapter
if($maxCandidates -le 0){ $maxCandidates = 1200 }

$chapters = @($manifest.chapters)
if(-not [string]::IsNullOrWhiteSpace($ChapterId)){
    $chapters = @($chapters | Where-Object { [string]$_.runtime_chapter -eq $ChapterId })
    if($chapters.Count -ne 1){ throw "PART1_PREP_UNKNOWN_CHAPTER chapter=$ChapterId" }
}

Write-Host ("PART1_CHAPTER_PREP_BEGIN train=" + [string]$manifest.train_id + " chapters=" + $chapters.Count)

$files = @(Get-ChildItem -LiteralPath $WarehouseRoot -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notlike ($outputRoot.TrimEnd("\") + "\*") })

$blockedSeen = @($files | Where-Object { $blocked.ContainsKey($_.Extension.ToLowerInvariant()) })
if($blockedSeen.Count -gt 0){
    Write-Host ("PART1_CHAPTER_PREP_BLOCKED_STOCK_IGNORED count=" + $blockedSeen.Count)
}

$eligible = @($files | Where-Object { $allowed.ContainsKey($_.Extension.ToLowerInvariant()) })
$summary = @()
foreach($chapter in $chapters){
    $keywords = @($chapter.keywords | ForEach-Object { ([string]$_).ToLowerInvariant() })
    $matches = New-Object System.Collections.Generic.List[object]
    foreach($file in $eligible){
        if($matches.Count -ge $maxCandidates){ break }
        $haystack = $file.FullName.ToLowerInvariant()
        $matchedKeyword = $null
        foreach($keyword in $keywords){
            if(-not [string]::IsNullOrWhiteSpace($keyword) -and $haystack.Contains($keyword)){
                $matchedKeyword = $keyword
                break
            }
        }
        if($null -ne $matchedKeyword){
            $matches.Add([ordered]@{
                path = $file.FullName
                extension = $file.Extension.ToLowerInvariant()
                bytes = [int64]$file.Length
                matched_keyword = $matchedKeyword
            })
        }
    }

    $report = [ordered]@{
        schema_version = 1
        train_id = [string]$manifest.train_id
        runtime_chapter = [string]$chapter.runtime_chapter
        predecessor = [string]$chapter.predecessor
        story_scope = [string]$chapter.story_scope
        status = "SOURCE_CANDIDATE_INDEX_PREPARED"
        warehouse_root = $WarehouseRoot
        candidate_count = $matches.Count
        candidate_ceiling = $maxCandidates
        candidates = @($matches)
        runtime_integration = "NOT_STARTED"
        evidence_boundary = "Candidate indexing only; no READY_FOR_IMPORT, UE import, PIE, device, visual or performance claim."
    }

    $reportPath = Join-Path $outputRoot (([string]$chapter.runtime_chapter) + ".json")
    $report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $reportPath -Encoding UTF8
    Write-Host ("PART1_CHAPTER_PREP_PASS chapter=" + [string]$chapter.runtime_chapter +
        " predecessor=" + [string]$chapter.predecessor +
        " candidates=" + $matches.Count +
        " report=" + $reportPath)
    $summary += [ordered]@{ chapter=[string]$chapter.runtime_chapter; candidates=$matches.Count; report=$reportPath }
}

$summaryPath = Join-Path $outputRoot "summary.json"
[ordered]@{
    schema_version = 1
    train_id = [string]$manifest.train_id
    generated_utc = [DateTime]::UtcNow.ToString("o")
    eligible_warehouse_files = $eligible.Count
    blocked_stock_ignored = $blockedSeen.Count
    chapters = $summary
    runtime_integration = "NOT_STARTED"
} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $summaryPath -Encoding UTF8

Write-Host ("PART1_CHAPTER_PREP_COMPLETE chapters=" + $summary.Count + " eligibleFiles=" + $eligible.Count + " summary=" + $summaryPath)
exit 0
