$ErrorActionPreference = "Stop"

function Set-Decision([bool]$Capture,[string]$Reason,[string]$BaseSha){
  $captureValue=if($Capture){"true"}else{"false"}
  Add-Content -LiteralPath $env:GITHUB_OUTPUT -Value "capture=$captureValue"
  Add-Content -LiteralPath $env:GITHUB_OUTPUT -Value "reason=$Reason"
  Add-Content -LiteralPath $env:GITHUB_OUTPUT -Value "base_sha=$BaseSha"
  Write-Host "P1C01_RENDER_DECISION capture=$captureValue base=$BaseSha reason=$Reason"
}

if($env:GITHUB_EVENT_NAME -eq "workflow_dispatch"){
  Set-Decision $true "manual-dispatch" ""
  exit 0
}

$base=[string]$env:BASE_SHA
$head=[string]$env:TARGET_SHA
if([string]::IsNullOrWhiteSpace($base) -or $base -match '^0+$'){
  Set-Decision $true "no-previous-head-fail-safe" $base
  exit 0
}

$git=(Get-Command git -ErrorAction Stop).Source
$changed=@(& $git diff --name-only $base $head)
if($LASTEXITCODE -ne 0){
  & $git fetch --no-tags --depth=1 origin $base
  if($LASTEXITCODE -eq 0){$changed=@(& $git diff --name-only $base $head)}
}
if($LASTEXITCODE -ne 0 -or $changed.Count -eq 0){
  Set-Decision $true "delta-unavailable-fail-safe" $base
  exit 0
}

$visualImpact=@()
foreach($path in $changed){
  $n=$path -replace "\\","/"
  $impact=(
    $n.StartsWith("Source/") -or
    $n.StartsWith("Config/") -or
    $n.StartsWith("SourceAssets/Production/") -or
    $n -eq "ShireJourney.uproject" -or
    $n -eq "Scripts/ci_capture_p1c01_visuals.cmd" -or
    $n -eq "Scripts/ci_import_production_assets.cmd" -or
    $n -eq ".github/workflows/p1c01-shire-render-capture.yml"
  )
  if($impact){$visualImpact += $n}
}

if($visualImpact.Count -gt 0){
  $visualImpact | ForEach-Object {Write-Host "P1C01_RENDER_IMPACT_FILE $_"}
  Set-Decision $true "visual-impact-delta" $base
  exit 0
}

function Test-GreenRender([string]$Sha){
  if(-not $env:GH_TOKEN){return $false}
  try{
    $headers=@{
      Authorization="Bearer $($env:GH_TOKEN)"
      Accept="application/vnd.github+json"
      "X-GitHub-Api-Version"="2022-11-28"
      "User-Agent"="ShireJourney-RenderClassifier"
    }
    $uri="https://api.github.com/repos/$($env:GITHUB_REPOSITORY)/actions/runs?head_sha=$Sha&per_page=100"
    $r=Invoke-RestMethod -Uri $uri -Headers $headers -Method Get -TimeoutSec 20
    return @($r.workflow_runs | Where-Object {
      $_.name -eq "P1C01 Shire Render Capture" -and $_.status -eq "completed" -and $_.conclusion -eq "success"
    }).Count -gt 0
  }catch{
    Write-Host "P1C01_RENDER_PROOF_LOOKUP_FAIL sha=$Sha error=$($_.Exception.Message)"
    return $false
  }
}

function Test-VisualContentUnchanged([string]$FromSha,[string]$ToSha){
  $delta=@(& $git diff --name-only $FromSha $ToSha)
  if($LASTEXITCODE -ne 0){return $false}
  foreach($path in $delta){
    $n=$path -replace "\\","/"
    $impact=(
      $n.StartsWith("Source/") -or
      $n.StartsWith("Config/") -or
      $n.StartsWith("SourceAssets/Production/") -or
      $n -eq "ShireJourney.uproject" -or
      $n -eq "Scripts/ci_capture_p1c01_visuals.cmd" -or
      $n -eq "Scripts/ci_import_production_assets.cmd"
    )
    if($impact){
      Write-Host "P1C01_RENDER_TRANSITIVE_BLOCKED file=$n ancestor=$FromSha head=$ToSha"
      return $false
    }
  }
  return $true
}

if(Test-GreenRender $base){
  Set-Decision $false "visual-tree-unchanged-inherit-green-parent" $base
  exit 0
}

$ancestors=@(& $git rev-list --first-parent --max-count=24 $base)
foreach($candidate in $ancestors){
  if(-not (Test-GreenRender $candidate)){continue}
  if(-not (Test-VisualContentUnchanged $candidate $head)){continue}
  Write-Host "P1C01_RENDER_TRANSITIVE_PROOF_PASS ancestor=$candidate head=$head"
  Set-Decision $false "visual-content-unchanged-inherit-green-ancestor" $candidate
  exit 0
}

Set-Decision $true "visual-tree-unchanged-but-no-safe-green-proof" $base
