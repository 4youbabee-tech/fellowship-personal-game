param(
    [string]$ProjectRoot = $env:GITHUB_WORKSPACE
)
$ErrorActionPreference = "Stop"
$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
$os = Get-CimInstance Win32_OperatingSystem
$gpu = Get-CimInstance Win32_VideoController | Select-Object Name,AdapterRAM,DriverVersion
$computer = Get-CimInstance Win32_ComputerSystem

$report = [ordered]@{
  schema_version=1
  generated_at_utc=[DateTime]::UtcNow.ToString("o")
  machine_name=$env:COMPUTERNAME
  cpu=[ordered]@{ name=[string]$cpu.Name; cores=[int]$cpu.NumberOfCores; logical=[int]$cpu.NumberOfLogicalProcessors }
  ram_bytes=[int64]$computer.TotalPhysicalMemory
  os=[ordered]@{ caption=[string]$os.Caption; version=[string]$os.Version; build=[string]$os.BuildNumber }
  gpu=@($gpu | ForEach-Object { [ordered]@{ name=[string]$_.Name; adapter_ram=[int64]$_.AdapterRAM; driver=[string]$_.DriverVersion } })
  target_contract=[ordered]@{ cpu_model="Intel Core i7-6498DU @ 2.50GHz"; gpu_model="AMD Radeon R5 M330"; gpu_vram_reported_mb=2039; ram_gb=8; os="Windows 11 Pro 64-bit"; os_directx_installed="DirectX 12"; dx12_ultimate_supported=$false; renderer="DX11"; resolution="1280x720"; fps_floor=30; stable_fps_unproven=$true }
  classification="RUNNER_HARDWARE_SNAPSHOT_ONLY"
  note="Do not promote to DEVICE_TESTED unless this runner is confirmed to be the intended target laptop and representative runtime frame/memory measurements are captured."
}
$out = Join-Path $ProjectRoot "Saved\Logs\CI-W00-RunnerHardware.json"
$report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $out -Encoding UTF8
Write-Host ("W00_RUNNER_HARDWARE_SNAPSHOT_PASS cpu=" + $report.cpu.name + " ramBytes=" + $report.ram_bytes + " gpuCount=" + $report.gpu.Count + " report=" + $out)
