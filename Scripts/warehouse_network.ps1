$ErrorActionPreference = "Stop"

function Invoke-WarehouseRetry {
    param(
        [Parameter(Mandatory=$true)][scriptblock]$Operation,
        [Parameter(Mandatory=$true)][string]$Label,
        [int]$MaxAttempts = 2
    )
    $last = $null
    for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
        try {
            Write-Host "WAREHOUSE_NET begin label=$Label attempt=$attempt/$MaxAttempts"
            $result = & $Operation
            Write-Host "WAREHOUSE_NET pass label=$Label attempt=$attempt/$MaxAttempts"
            return $result
        }
        catch {
            $last = $_.Exception
            Write-Warning "WAREHOUSE_NET fail label=$Label attempt=$attempt/$MaxAttempts detail=$($last.Message)"
            if ($attempt -lt $MaxAttempts) { Start-Sleep -Seconds (2 * $attempt) }
        }
    }
    throw "WAREHOUSE_NET exhausted label=$Label attempts=$MaxAttempts detail=$($last.Message)"
}

function Invoke-WarehouseRestJson {
    param(
        [Parameter(Mandatory=$true)][string]$Uri,
        [hashtable]$Headers = @{},
        [int]$TimeoutSec = 30,
        [int]$MaxAttempts = 2
    )
    return Invoke-WarehouseRetry -Label ("rest:" + $Uri) -MaxAttempts $MaxAttempts -Operation {
        Invoke-RestMethod -Uri $Uri -Headers $Headers -Method Get -TimeoutSec $TimeoutSec
    }
}

function Invoke-WarehousePage {
    param(
        [Parameter(Mandatory=$true)][string]$Uri,
        [hashtable]$Headers = @{},
        [int]$TimeoutSec = 30,
        [int]$MaxAttempts = 2
    )
    return Invoke-WarehouseRetry -Label ("page:" + $Uri) -MaxAttempts $MaxAttempts -Operation {
        Invoke-WebRequest -Uri $Uri -Headers $Headers -UseBasicParsing -TimeoutSec $TimeoutSec
    }
}

function Invoke-WarehouseDownload {
    param(
        [Parameter(Mandatory=$true)][string]$Uri,
        [Parameter(Mandatory=$true)][string]$OutFile,
        [hashtable]$Headers = @{},
        [int]$TimeoutSec = 180,
        [int]$MaxAttempts = 2
    )
    $partial = $OutFile + ".partial"
    return Invoke-WarehouseRetry -Label ("download:" + $Uri) -MaxAttempts $MaxAttempts -Operation {
        Remove-Item -LiteralPath $partial -Force -ErrorAction SilentlyContinue
        try {
            Invoke-WebRequest -Uri $Uri -Headers $Headers -OutFile $partial -UseBasicParsing -TimeoutSec $TimeoutSec
            if (-not (Test-Path -LiteralPath $partial -PathType Leaf)) { throw "partial file was not created" }
            $item = Get-Item -LiteralPath $partial
            if ([int64]$item.Length -le 0) { throw "download produced an empty file" }
            Move-Item -LiteralPath $partial -Destination $OutFile -Force
            return Get-Item -LiteralPath $OutFile
        }
        finally {
            if (Test-Path -LiteralPath $partial -PathType Leaf) {
                Remove-Item -LiteralPath $partial -Force -ErrorAction SilentlyContinue
            }
        }
    }
}

function Test-WarehouseZipReadable {
    param(
        [Parameter(Mandatory=$true)][string]$Path
    )
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $false }
    $archive = $null
    try {
        Add-Type -AssemblyName System.IO.Compression.FileSystem
        $archive = [System.IO.Compression.ZipFile]::OpenRead($Path)
        [void]$archive.Entries.Count
        return $true
    }
    catch {
        Write-Warning "WAREHOUSE_ZIP_INVALID path=$Path detail=$($_.Exception.Message)"
        return $false
    }
    finally {
        if ($null -ne $archive) { $archive.Dispose() }
    }
}

function Test-WarehouseReceiptReusable {
    param(
        [Parameter(Mandatory=$true)][string]$ReceiptPath,
        [Parameter(Mandatory=$true)][string]$BatchId,
        [string]$ManifestSha256 = ""
    )
    if (-not (Test-Path -LiteralPath $ReceiptPath -PathType Leaf)) { return $false }
    try { $receipt = Get-Content -LiteralPath $ReceiptPath -Raw | ConvertFrom-Json }
    catch {
        Write-Warning "WAREHOUSE_REUSE invalid-receipt path=$ReceiptPath detail=$($_.Exception.Message)"
        return $false
    }
    if ([string]$receipt.batch_id -ne $BatchId) { return $false }
    # A valid old receipt does not authorize changed queries, mappings or resolution.
    # Legacy callers are unchanged; ambientCG opts into strict manifest identity.
    if (-not [string]::IsNullOrWhiteSpace($ManifestSha256)) {
        if ($ManifestSha256 -notmatch '^[0-9a-fA-F]{64}
    if ($files.Count -le 0) { return $false }

    foreach ($record in $files) {
        if ($record.PSObject.Properties.Name -contains "file") {
            $path = [string]$record.file
            if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { return $false }
            if ($record.PSObject.Properties.Name -contains "size") {
                if ([int64](Get-Item -LiteralPath $path).Length -ne [int64]$record.size) { return $false }
            }
            if ($record.PSObject.Properties.Name -contains "sha256") {
                $expectedHash = ([string]$record.sha256).ToLowerInvariant()
                if (-not [string]::IsNullOrWhiteSpace($expectedHash)) {
                    $actualHash = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
                    if ($actualHash -ne $expectedHash) {
                        Write-Warning "WAREHOUSE_REUSE_PURGE_HASH_MISMATCH path=$path expected=$expectedHash actual=$actualHash"
                        Remove-Item -LiteralPath $path -Force -ErrorAction SilentlyContinue
                        return $false
                    }
                }
            }
            if ([IO.Path]::GetExtension($path).ToLowerInvariant() -eq ".zip" -and -not (Test-WarehouseZipReadable -Path $path)) {
                Write-Warning "WAREHOUSE_REUSE_PURGE_CORRUPT_ZIP path=$path"
                Remove-Item -LiteralPath $path -Force -ErrorAction SilentlyContinue
                return $false
            }
            continue
        }
        if ($record.PSObject.Properties.Name -contains "archive") {
            $archive = [string]$record.archive
            if (-not (Test-Path -LiteralPath $archive -PathType Leaf)) { return $false }
            if ($record.PSObject.Properties.Name -contains "archive_size") {
                if ([int64](Get-Item -LiteralPath $archive).Length -ne [int64]$record.archive_size) { return $false }
            }
            if ($record.PSObject.Properties.Name -contains "archive_sha256") {
                $expectedArchiveHash = ([string]$record.archive_sha256).ToLowerInvariant()
                if (-not [string]::IsNullOrWhiteSpace($expectedArchiveHash)) {
                    $actualArchiveHash = (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant()
                    if ($actualArchiveHash -ne $expectedArchiveHash) {
                        Write-Warning "WAREHOUSE_REUSE_PURGE_HASH_MISMATCH path=$archive expected=$expectedArchiveHash actual=$actualArchiveHash"
                        Remove-Item -LiteralPath $archive -Force -ErrorAction SilentlyContinue
                        return $false
                    }
                }
            }
            if ($record.PSObject.Properties.Name -contains "license_snapshot") {
                $license = [string]$record.license_snapshot
                if (-not (Test-Path -LiteralPath $license -PathType Leaf)) { return $false }
            }
            if ([IO.Path]::GetExtension($archive).ToLowerInvariant() -eq ".zip" -and -not (Test-WarehouseZipReadable -Path $archive)) {
                Write-Warning "WAREHOUSE_REUSE_PURGE_CORRUPT_ZIP path=$archive"
                Remove-Item -LiteralPath $archive -Force -ErrorAction SilentlyContinue
                return $false
            }
            continue
        }
        return $false
    }

    Write-Host "WAREHOUSE_REUSE_PASS batch=$BatchId files=$($files.Count) receipt=$ReceiptPath"
    return $true
}
) { return $false }
        if (([string]$receipt.manifest_sha256).ToLowerInvariant() -ne $ManifestSha256.ToLowerInvariant()) {
            Write-Host "WAREHOUSE_REUSE_MANIFEST_CHANGED batch=$BatchId"
            return $false
        }
    }
    $files = @($receipt.files)
    if ($files.Count -le 0) { return $false }

    foreach ($record in $files) {
        if ($record.PSObject.Properties.Name -contains "file") {
            $path = [string]$record.file
            if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { return $false }
            if ($record.PSObject.Properties.Name -contains "size") {
                if ([int64](Get-Item -LiteralPath $path).Length -ne [int64]$record.size) { return $false }
            }
            if ($record.PSObject.Properties.Name -contains "sha256") {
                $expectedHash = ([string]$record.sha256).ToLowerInvariant()
                if (-not [string]::IsNullOrWhiteSpace($expectedHash)) {
                    $actualHash = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
                    if ($actualHash -ne $expectedHash) {
                        Write-Warning "WAREHOUSE_REUSE_PURGE_HASH_MISMATCH path=$path expected=$expectedHash actual=$actualHash"
                        Remove-Item -LiteralPath $path -Force -ErrorAction SilentlyContinue
                        return $false
                    }
                }
            }
            if ([IO.Path]::GetExtension($path).ToLowerInvariant() -eq ".zip" -and -not (Test-WarehouseZipReadable -Path $path)) {
                Write-Warning "WAREHOUSE_REUSE_PURGE_CORRUPT_ZIP path=$path"
                Remove-Item -LiteralPath $path -Force -ErrorAction SilentlyContinue
                return $false
            }
            continue
        }
        if ($record.PSObject.Properties.Name -contains "archive") {
            $archive = [string]$record.archive
            if (-not (Test-Path -LiteralPath $archive -PathType Leaf)) { return $false }
            if ($record.PSObject.Properties.Name -contains "archive_size") {
                if ([int64](Get-Item -LiteralPath $archive).Length -ne [int64]$record.archive_size) { return $false }
            }
            if ($record.PSObject.Properties.Name -contains "archive_sha256") {
                $expectedArchiveHash = ([string]$record.archive_sha256).ToLowerInvariant()
                if (-not [string]::IsNullOrWhiteSpace($expectedArchiveHash)) {
                    $actualArchiveHash = (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant()
                    if ($actualArchiveHash -ne $expectedArchiveHash) {
                        Write-Warning "WAREHOUSE_REUSE_PURGE_HASH_MISMATCH path=$archive expected=$expectedArchiveHash actual=$actualArchiveHash"
                        Remove-Item -LiteralPath $archive -Force -ErrorAction SilentlyContinue
                        return $false
                    }
                }
            }
            if ($record.PSObject.Properties.Name -contains "license_snapshot") {
                $license = [string]$record.license_snapshot
                if (-not (Test-Path -LiteralPath $license -PathType Leaf)) { return $false }
            }
            if ([IO.Path]::GetExtension($archive).ToLowerInvariant() -eq ".zip" -and -not (Test-WarehouseZipReadable -Path $archive)) {
                Write-Warning "WAREHOUSE_REUSE_PURGE_CORRUPT_ZIP path=$archive"
                Remove-Item -LiteralPath $archive -Force -ErrorAction SilentlyContinue
                return $false
            }
            continue
        }
        return $false
    }

    Write-Host "WAREHOUSE_REUSE_PASS batch=$BatchId files=$($files.Count) receipt=$ReceiptPath"
    return $true
}
