# Remove only project-generated compile products after UE4Editor is closed.
# A stale DLL can remain briefly locked by the self-hosted runner after the Editor exits.
# Retry cleanup for a bounded interval; never terminate a process to release the file.
$ErrorActionPreference = "Stop"
$paths = @(
    (Join-Path $env:GITHUB_WORKSPACE "Intermediate\Build\Win64"),
    (Join-Path $env:GITHUB_WORKSPACE "Binaries\Win64")
)
$maxAttempts = 12
$retryDelaySeconds = 5

foreach ($path in $paths) {
    if (-not (Test-Path -LiteralPath $path)) {
        continue
    }

    Write-Host "Removing stale project build product: $path"
    for ($attempt = 1; $attempt -le $maxAttempts; $attempt++) {
        try {
            Remove-Item -LiteralPath $path -Recurse -Force -ErrorAction Stop
            break
        }
        catch {
            if ($attempt -ge $maxAttempts) {
                throw "Could not remove stale project build product after $maxAttempts attempts: $path. The runner still has an open file handle; no process was terminated. Last error: $($_.Exception.Message)"
            }

            Write-Warning "Build product remains locked (attempt $attempt/$maxAttempts): $path. Waiting $retryDelaySeconds seconds before retry."
            Start-Sleep -Seconds $retryDelaySeconds
        }
    }

    if (Test-Path -LiteralPath $path) {
        throw "Stale project build product still exists after cleanup: $path"
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
