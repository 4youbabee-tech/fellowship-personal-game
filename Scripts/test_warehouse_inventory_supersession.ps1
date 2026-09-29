Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$auditScript = Join-Path $PSScriptRoot "audit_warehouse_inventory.ps1"
if(-not (Test-Path -LiteralPath $auditScript -PathType Leaf)){ throw "WAREHOUSE_SUPERSESSION_TEST_AUDIT_MISSING path=$auditScript" }

$tempRoot = Join-Path $env:TEMP ("shire-warehouse-supersession-" + [Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $tempRoot -Force | Out-Null

try {
  $payloadDir = Join-Path $tempRoot "ambientCG\PLASTER"
  New-Item -ItemType Directory -Path $payloadDir -Force | Out-Null
  $payloadPath = Join-Path $payloadDir "Plaster007_2K-PNG.zip"

  $oldTemp = Join-Path $tempRoot "old-payload.bin"
  [IO.File]::WriteAllText($oldTemp,"old payload v1")
  $oldHash = (Get-FileHash -LiteralPath $oldTemp -Algorithm SHA256).Hash.ToLowerInvariant()
  Remove-Item -LiteralPath $oldTemp -Force

  [IO.File]::WriteAllText($payloadPath,"current payload v2")
  $currentHash = (Get-FileHash -LiteralPath $payloadPath -Algorithm SHA256).Hash.ToLowerInvariant()

  $oldReceipt = [ordered]@{
    batch_id = "WAREHOUSE_AMBIENTCG_P1C01_V1"
    provider = "AMBIENTCG"
    staged_at_utc = "2026-01-01T00:00:00Z"
    files = @([ordered]@{
      asset_id = "Plaster007"
      file = $payloadPath
      sha256 = $oldHash
      state = "STAGED"
    })
  }
  $newReceipt = [ordered]@{
    batch_id = "WAREHOUSE_AMBIENTCG_TRILOGY_FOUNDATION_V2"
    provider = "AMBIENTCG"
    staged_at_utc = "2026-01-02T00:00:00Z"
    files = @([ordered]@{
      asset_id = "Plaster007"
      file = $payloadPath
      sha256 = $currentHash
      state = "STAGED"
    })
  }

  $oldReceipt | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $tempRoot "receipt_WAREHOUSE_AMBIENTCG_P1C01_V1.json") -Encoding UTF8
  $newReceipt | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $tempRoot "receipt_WAREHOUSE_AMBIENTCG_TRILOGY_FOUNDATION_V2.json") -Encoding UTF8

  $passOutput = @(& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $auditScript -Root $tempRoot 2>&1)
  $passCode = [int]$LASTEXITCODE
  $passText = $passOutput -join [Environment]::NewLine

  if($passCode -ne 0){ throw "WAREHOUSE_SUPERSESSION_TEST_EXPECTED_PASS exit=$passCode output=$passText" }
  if($passText -notmatch "WAREHOUSE_SUPERSEDED_HASH_RECORD"){ throw "WAREHOUSE_SUPERSESSION_TEST_MISSING_SUPERSEDED_MARKER output=$passText" }
  if($passText -notmatch "WAREHOUSE_INVENTORY_AUDIT_PASS"){ throw "WAREHOUSE_SUPERSESSION_TEST_MISSING_PASS_MARKER output=$passText" }
  Write-Host "WAREHOUSE_SUPERSESSION_TEST_PASS latest-receipt-match=true"

  [IO.File]::WriteAllText($payloadPath,"mutated after latest receipt")
  $failOutput = @(& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $auditScript -Root $tempRoot 2>&1)
  $failCode = [int]$LASTEXITCODE
  $failText = $failOutput -join [Environment]::NewLine

  if($failCode -ne 2){ throw "WAREHOUSE_SUPERSESSION_TEST_EXPECTED_HARD_FAIL exit=$failCode output=$failText" }
  if($failText -notmatch "WAREHOUSE_HASH_MISMATCH"){ throw "WAREHOUSE_SUPERSESSION_TEST_MISSING_HARD_MISMATCH output=$failText" }
  Write-Host "WAREHOUSE_SUPERSESSION_TEST_PASS latest-receipt-mismatch-hard-fail=true"

  Write-Host "WAREHOUSE_RECEIPT_SUPERSESSION_TEST_PASS"
  exit 0
}
finally {
  if(Test-Path -LiteralPath $tempRoot){ Remove-Item -LiteralPath $tempRoot -Recurse -Force -ErrorAction SilentlyContinue }
}
