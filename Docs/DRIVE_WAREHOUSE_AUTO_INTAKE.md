# Automatic Google Drive warehouse intake

Candidate: runs on develop every two hours and queues while the laptop is off; a future scheduled window resumes if a queued job expires. Pull requests only run tests.

One-time setup required on the interactive watchdog runner account: install rclone and real Python, configure a private rclone remote called `shirecloud` using OAuth, scoped to root_folder_id `1bMZp-XKcQjCj3fYxLoISDtqG9W5aSzyq`. Configuration must be saved at `%APPDATA%\rclone\rclone.conf`. ChatGPT's Google Drive connector cannot supply these runner credentials.

The workflow isolates source checkout under RUNNER_TEMP and stages managed source ZIPs under `D:\actions-runner\_warehouse\ShireJourney\_drive_temp_staging`, not the Unreal workspace. Downloaded archives are byte-length, MD5, SHA256, ZIP integrity and path checked. Receipts remain on persistent D. This is NOT Unreal import acceptance.

Cleanup runs only when a separate `E:\ShireJourneyBackup` exists, local and backup file SHA256 match, source remote ID/size/MD5 still match, and a corresponding exact-ID-and-SHA receipt is written by the asset/import acceptance process to `_drive_temp_staging\accepted_for_cleanup` with `disposition=IMPORTED_ACCEPTED_SOURCE_RETAINED_IN_BACKUP` and actual `engine_acceptance_evidence`. No unconditional expiration-based deletion and no modification of unrelated Drive files.

Status: no runner-side OAuth/transfer/import/cleanup proof available yet; status remains SOURCE-CANDIDATE until exact-head CI and first physical sync.
