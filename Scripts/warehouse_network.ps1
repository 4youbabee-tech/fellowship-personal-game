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

function Test-WarehouseReceiptReusable {
    param(
        [Parameter(Mandatory=$true)][string]$ReceiptPath,
        [Parameter(Mandatory=$true)][string]$BatchId
    )
    if (-not (Test-Path -LiteralPath $ReceiptPath -PathType Leaf)) { return $false }
    try { $receipt = Get-Content -LiteralPath $ReceiptPath -Raw | ConvertFrom-Json }
    catch {
        Write-Warning "WAREHOUSE_REUSE invalid-receipt path=$ReceiptPath detail=$($_.Exception.Message)"
        return $false
    }
    if ([string]$receipt.batch_id -ne $BatchId) { return $false }
    $files = @($receipt.files)
    if ($files.Count -le 0) { return $false }

    foreach ($record in $files) {
        if ($record.PSObject.Properties.Name -contains "file") {
            $path = [string]$record.file
            if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { return $false }
            if ($record.PSObject.Properties.Name -contains "size") {
                if ([int64](Get-Item -LiteralPath $path).Length -ne [int64]$record.size) { return $false }
            }
            continue
        }
        if ($record.PSObject.Properties.Name -contains "archive") {
            $archive = [string]$record.archive
            if (-not (Test-Path -LiteralPath $archive -PathType Leaf)) { return $false }
            if ($record.PSObject.Properties.Name -contains "archive_size") {
                if ([int64](Get-Item -LiteralPath $archive).Length -ne [int64]$record.archive_size) { return $false }
            }
            if ($record.PSObject.Properties.Name -contains "license_snapshot") {
                $license = [string]$record.license_snapshot
                if (-not (Test-Path -LiteralPath $license -PathType Leaf)) { return $false }
            }
            continue
        }
        return $false
    }

    Write-Host "WAREHOUSE_REUSE_PASS batch=$BatchId files=$($files.Count) receipt=$ReceiptPath"
    return $true
}
