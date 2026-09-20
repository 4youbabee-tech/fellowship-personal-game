# Remove only project-generated compile products after UE4Editor is closed.
$ErrorActionPreference = "Stop"
$paths = @(
    (Join-Path $env:GITHUB_WORKSPACE "Intermediate\Build\Win64"),
    (Join-Path $env:GITHUB_WORKSPACE "Binaries\Win64")
)
foreach ($path in $paths) {
    if (Test-Path -LiteralPath $path) {
        Write-Host "Removing stale project build product: $path"
        Remove-Item -LiteralPath $path -Recurse -Force
    }
}
$logDir = Join-Path $env:GITHUB_WORKSPACE "Saved\Logs"
if (Test-Path -LiteralPath $logDir) {
    Get-ChildItem -LiteralPath $logDir -Filter "CI-*.log" -File -ErrorAction SilentlyContinue |
        ForEach-Object {
            Write-Host "Removing stale CI evidence log: $($_.FullName)"
            Remove-Item -LiteralPath $_.FullName -Force
        }
    Get-ChildItem -LiteralPath $logDir -Filter "CI-*-result.json" -File -ErrorAction SilentlyContinue |
        ForEach-Object {
            Write-Host "Removing stale CI result file: $($_.FullName)"
            Remove-Item -LiteralPath $_.FullName -Force
        }
}
Write-Host "Project build intermediates and stale CI evidence reset."
exit 0
