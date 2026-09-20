# Stable tracked exact-head checkout script for the self-hosted Windows runner.
$ErrorActionPreference = "Stop"
Set-Location $env:GITHUB_WORKSPACE

if (-not (Test-Path ".git")) {
    & git init
    if ($LASTEXITCODE -ne 0) { exit 70 }
}

Remove-Item -LiteralPath ".git\index.lock" -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath ".git\shallow.lock" -Force -ErrorAction SilentlyContinue

$repoUrl = "https://x-access-token:$env:GH_TOKEN@github.com/$env:GITHUB_REPOSITORY.git"
$origin = & git remote get-url origin 2>$null
if ($LASTEXITCODE -eq 0) {
    & git remote set-url origin $repoUrl
} else {
    & git remote add origin $repoUrl
}
if ($LASTEXITCODE -ne 0) { exit 71 }

$attempt = 1
$fetched = $false
while ($attempt -le 7) {
    Write-Host "Fetching exact PR head attempt $attempt of 7..."
    & git fetch --no-tags --prune --depth=1 origin $env:TARGET_SHA
    if ($LASTEXITCODE -eq 0) {
        $fetched = $true
        break
    }
    if ($attempt -lt 7) {
        Write-Host "Fetch failed; retrying in 5 seconds."
        Start-Sleep -Seconds 5
    }
    $attempt++
}
if (-not $fetched) {
    Write-Error "Failed to fetch exact PR head after 7 attempts."
    exit 72
}

& git checkout -f FETCH_HEAD
if ($LASTEXITCODE -ne 0) { exit 73 }
& git reset --hard $env:TARGET_SHA
if ($LASTEXITCODE -ne 0) { exit 73 }

Write-Host "Exact-head checkout complete: $env:TARGET_SHA"
exit 0
