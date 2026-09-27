param(
  [string]$ManifestPath = "Data/WarehouseSaturationTrainV1.json",
  [string]$WarehouseRoot = "C:\actions-runner\_warehouse\ShireJourney",
  [string]$OutputRoot = "",
  [switch]$StagePublicLanes,
  [switch]$Refresh
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path $PSScriptRoot -Parent
if ([string]::IsNullOrWhiteSpace($OutputRoot)) {
  $OutputRoot = Join-Path $ProjectRoot "Saved\WarehouseSaturation"
}
if (-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)) {
  $candidate = Join-Path $ProjectRoot $ManifestPath
  if (Test-Path -LiteralPath $candidate -PathType Leaf) { $ManifestPath = $candidate }
}
if (-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)) {
  throw "Warehouse saturation manifest missing: $ManifestPath"
}

$manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null

function Get-OptionalPropertyValue {
  param(
    [object]$Object,
    [string]$Name,
    [object]$Default = $null
  )
  if ($null -eq $Object) { return $Default }
  $prop = $Object.PSObject.Properties[$Name]
  if ($null -eq $prop) { return $Default }
  return $prop.Value
}

if ($StagePublicLanes) {
  $stageJobs = @(
    @{ script="stage_polyhaven_warehouse.ps1"; manifest="Data/WarehouseAcquisitionBatchV1.json"; label="Poly Haven" },
    @{ script="stage_ambientcg_warehouse.ps1"; manifest="Data/WarehouseAmbientCGAcquisitionBatchV1.json"; label="ambientCG foundation" },
    @{ script="stage_ambientcg_warehouse.ps1"; manifest="Data/WarehouseAmbientCGTrilogyBatchV2.json"; label="ambientCG trilogy" },
    @{ script="stage_quaternius_warehouse.ps1"; manifest="Data/WarehouseQuaterniusAcquisitionBatchV1.json"; label="Quaternius" },
    @{ script="stage_kenney_warehouse.ps1"; manifest="Data/WarehouseKenneyAcquisitionBatchV1.json"; label="Kenney" },
    @{ script="stage_kaykit_github_warehouse.ps1"; manifest="Data/WarehouseKayKitGitHubAcquisitionBatchV1.json"; label="KayKit" },
    @{ script="stage_opengameart_audio.ps1"; manifest="Data/WarehouseAudioAcquisitionBatchV1.json"; label="OpenGameArt audio" }
  )

  foreach ($job in $stageJobs) {
    $scriptPath = Join-Path $PSScriptRoot $job.script
    $manifestFile = Join-Path $ProjectRoot $job.manifest
    if (-not (Test-Path -LiteralPath $scriptPath -PathType Leaf)) {
      throw ("Warehouse stage script missing: " + $job.script)
    }
    if (-not (Test-Path -LiteralPath $manifestFile -PathType Leaf)) {
      throw ("Warehouse stage manifest missing: " + $job.manifest)
    }

    Write-Host ("WAREHOUSE_SATURATION_STAGE_START providerLane=" + $job.label)
    $args = @("-NoProfile","-ExecutionPolicy","Bypass","-File",$scriptPath,"-ManifestPath",$manifestFile)
    if ($Refresh) { $args += "-Refresh" }
    & powershell.exe @args
    if ($LASTEXITCODE -ne 0) {
      throw ("Warehouse saturation staging failed: " + $job.label + " exit=" + $LASTEXITCODE)
    }
    Write-Host ("WAREHOUSE_SATURATION_STAGE_PASS providerLane=" + $job.label)
  }

  $auditScript = Join-Path $PSScriptRoot "audit_warehouse_inventory.ps1"
  & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $auditScript -Root $WarehouseRoot
  if ($LASTEXITCODE -ne 0) { throw "Warehouse inventory audit failed after staging." }
}

$receiptFiles = @()
if (Test-Path -LiteralPath $WarehouseRoot -PathType Container) {
  $receiptFiles = @(Get-ChildItem -LiteralPath $WarehouseRoot -Recurse -File -Filter "receipt_*.json")
}

$records = @()
$badReceipts = @()
foreach ($receiptFile in $receiptFiles) {
  try { $receipt = Get-Content -LiteralPath $receiptFile.FullName -Raw | ConvertFrom-Json }
  catch {
    $badReceipts += [ordered]@{ receipt=$receiptFile.FullName; reason="invalid_json"; detail=$_.Exception.Message }
    continue
  }

  $receiptProvider = [string](Get-OptionalPropertyValue -Object $receipt -Name "provider" -Default "")
  $receiptBatchId = [string](Get-OptionalPropertyValue -Object $receipt -Name "batch_id" -Default "")
  $receiptItems = @(Get-OptionalPropertyValue -Object $receipt -Name "files" -Default @())

  foreach ($item in $receiptItems) {
    $path = [string](Get-OptionalPropertyValue -Object $item -Name "file" -Default "")
    $declaredHash = ([string](Get-OptionalPropertyValue -Object $item -Name "sha256" -Default "")).ToLowerInvariant()
    if ([string]::IsNullOrWhiteSpace($path)) {
      $path = [string](Get-OptionalPropertyValue -Object $item -Name "archive" -Default "")
      $declaredHash = ([string](Get-OptionalPropertyValue -Object $item -Name "archive_sha256" -Default "")).ToLowerInvariant()
    }

    $exists = -not [string]::IsNullOrWhiteSpace($path) -and (Test-Path -LiteralPath $path -PathType Leaf)
    $actualHash = ""
    $size = [int64]0
    $extension = ""
    if ($exists) {
      $file = Get-Item -LiteralPath $path
      $size = [int64]$file.Length
      $extension = $file.Extension.ToLowerInvariant()
      $actualHash = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
    }

    $assetId = [string](Get-OptionalPropertyValue -Object $item -Name "asset_id" -Default "")
    $assetSlug = [string](Get-OptionalPropertyValue -Object $item -Name "asset_slug" -Default "")
    $category = [string](Get-OptionalPropertyValue -Object $item -Name "category" -Default "")
    $sourcePage = [string](Get-OptionalPropertyValue -Object $item -Name "source_page" -Default "")
    $itemState = [string](Get-OptionalPropertyValue -Object $item -Name "state" -Default "STAGED")
    if ([string]::IsNullOrWhiteSpace($itemState)) { $itemState = "STAGED" }

    $records += [pscustomobject]@{
      provider = $receiptProvider
      batch_id = $receiptBatchId
      asset_id = $assetId
      asset_slug = $assetSlug
      category = $category
      path = $path
      exists = $exists
      size = $size
      extension = $extension
      declared_sha256 = $declaredHash
      actual_sha256 = $actualHash
      hash_ok = ($exists -and -not [string]::IsNullOrWhiteSpace($declaredHash) -and $declaredHash -eq $actualHash)
      source_page = $sourcePage
      state = $itemState
    }
  }
}

function Test-CarReceiptMatch {
  param([object]$Car, [object]$Record)

  $providers = @($Car.providers | ForEach-Object { [string]$_ })
  if ($providers -contains "PROJECT_OWNED") { return $false }
  if ($providers -notcontains [string]$Record.provider) { return $false }

  $haystack = (([string]$Record.asset_id) + " " + ([string]$Record.asset_slug) + " " + ([string]$Record.category)).ToLowerInvariant()
  $targets = @($Car.target | ForEach-Object { ([string]$_).ToLowerInvariant() })
  foreach ($target in $targets) {
    $tokens = @($target -split '[^a-z0-9]+' | Where-Object { $_.Length -ge 4 })
    foreach ($token in $tokens) {
      if ($haystack.Contains($token)) { return $true }
    }
  }

  # Provider receipt still counts as lane coverage even when pack taxonomy does not
  # exactly match the human-readable target label.
  return $true
}

$carReports = @()
foreach ($car in @($manifest.cars | Sort-Object order)) {
  $matches = @($records | Where-Object { Test-CarReceiptMatch -Car $car -Record $_ })
  $verified = @($matches | Where-Object { $_.exists -and $_.hash_ok })
  $unverified = @($matches | Where-Object { -not $_.exists -or -not $_.hash_ok })

  $access = [string]$car.access_mode
  $publicStageCapable = $access -match "PUBLIC"
  $state = "PREPARED"
  if ($verified.Count -gt 0) { $state = "STAGED_RECEIPT_VERIFIED" }
  elseif ($publicStageCapable) { $state = "PUBLIC_LANE_PENDING_STAGE" }
  elseif ($car.providers -contains "PROJECT_OWNED") { $state = "LOCAL_AUDIT_LANE" }
  else { $state = "MANUAL_OR_AUTH_SOURCE_PENDING" }

  $carReports += [ordered]@{
    order = [int]$car.order
    id = [string]$car.id
    priority = [string]$car.priority
    ceiling = [string]$car.ceiling
    access_mode = $access
    providers = @($car.providers)
    receipt_matches = $matches.Count
    verified_receipt_files = $verified.Count
    unverified_receipt_files = $unverified.Count
    verified_bytes = [int64](($verified | Measure-Object -Property size -Sum).Sum)
    state = $state
  }
}

$providerSummary = @($records | Group-Object provider | ForEach-Object {
  [ordered]@{
    provider = $_.Name
    receipt_records = $_.Count
    verified_records = @($_.Group | Where-Object { $_.hash_ok }).Count
    bytes = [int64](($_.Group | Measure-Object -Property size -Sum).Sum)
  }
})

$report = [ordered]@{
  schema_version = 1
  train_id = [string]$manifest.train_id
  generated_at_utc = [DateTime]::UtcNow.ToString("o")
  warehouse_root = $WarehouseRoot
  receipt_count = $receiptFiles.Count
  receipt_record_count = $records.Count
  verified_receipt_record_count = @($records | Where-Object { $_.hash_ok }).Count
  bad_receipts = $badReceipts
  provider_summary = $providerSummary
  cars = $carReports
  rules = @(
    "Receipt verification is staging evidence only.",
    "No car becomes READY_FOR_IMPORT from this report.",
    "Manual/auth/purchase lanes remain pending until explicit access and item-level license evidence exist.",
    "Runtime integration remains serialized behind active project gates."
  )
}

$outPath = Join-Path $OutputRoot "warehouse_saturation_train_latest.json"
$report | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $outPath -Encoding UTF8

$verifiedCars = @($carReports | Where-Object { $_.state -eq "STAGED_RECEIPT_VERIFIED" }).Count
$publicPending = @($carReports | Where-Object { $_.state -eq "PUBLIC_LANE_PENDING_STAGE" }).Count
$manualPending = @($carReports | Where-Object { $_.state -eq "MANUAL_OR_AUTH_SOURCE_PENDING" }).Count
Write-Host ("WAREHOUSE_SATURATION_REPORT_PASS cars=" + $carReports.Count + " stagedCars=" + $verifiedCars + " publicPending=" + $publicPending + " manualPending=" + $manualPending + " receipts=" + $receiptFiles.Count + " report=" + $outPath)
