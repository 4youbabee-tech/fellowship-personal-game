@echo off
echo Build/import logs were already printed into the workflow log.
echo Self-hosted local log directory: %GITHUB_WORKSPACE%\Saved\Logs
echo Artifact upload is intentionally skipped to avoid storage-quota failures masking the primary error.
exit /b 0
