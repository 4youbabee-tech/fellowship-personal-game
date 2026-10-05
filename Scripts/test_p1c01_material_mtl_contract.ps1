Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Root = Split-Path $PSScriptRoot -Parent
$ScriptPath = Join-Path $Root "Scripts\prepare_p1c01_material_intake.ps1"
if(-not (Test-Path -LiteralPath $ScriptPath -PathType Leaf)){
  throw "P1C01_MATERIAL_MTL_CONTRACT_FAIL reason=script_missing"
}

$Text = Get-Content -LiteralPath $ScriptPath -Raw

$Required = @(
  '("newmtl {0}" -f [string]$item.material_name)',
  '("Pr {0}" -f $roughnessText)',
  '("Pm {0}" -f $metallicText)',
  '("Ks {0} {0} {0}" -f $ksText)',
  '("map_Kd {0}" -f [IO.Path]::GetFileName($dest))'
)
foreach($Token in $Required){
  if(-not $Text.Contains($Token)){
    throw "P1C01_MATERIAL_MTL_CONTRACT_FAIL missing=$Token"
  }
}

$Forbidden = @(
  '"newmtl "+[string]$item.material_name',
  '"Pr "+([double]$item.roughness)',
  '"Pm "+([double]$item.metallic)',
  '"map_Kd "+[IO.Path]::GetFileName($dest)'
)
foreach($Token in $Forbidden){
  if($Text.Contains($Token)){
    throw "P1C01_MATERIAL_MTL_CONTRACT_FAIL legacy_fragment=$Token"
  }
}

Write-Host "P1C01_MATERIAL_MTL_CONTRACT_PASS directives=5"
exit 0
