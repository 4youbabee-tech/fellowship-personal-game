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
Write-Host "Project build intermediates reset."
exit 0
