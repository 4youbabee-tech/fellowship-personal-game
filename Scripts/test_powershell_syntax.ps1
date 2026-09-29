param(
  [string]$Root = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path $PSScriptRoot -Parent
if([string]::IsNullOrWhiteSpace($Root)){ $Root = Join-Path $ProjectRoot "Scripts" }
if(-not (Test-Path -LiteralPath $Root -PathType Container)){ throw "PowerShell syntax root missing: $Root" }

$files=@(Get-ChildItem -LiteralPath $Root -Recurse -File -Filter "*.ps1" | Sort-Object FullName)
$failures=@()

foreach($file in $files){
  $tokens=$null
  $parseErrors=$null
  [void][System.Management.Automation.Language.Parser]::ParseFile($file.FullName,[ref]$tokens,[ref]$parseErrors)
  foreach($err in @($parseErrors)){
    $failures += [ordered]@{
      file=$file.FullName
      line=[int]$err.Extent.StartLineNumber
      column=[int]$err.Extent.StartColumnNumber
      message=[string]$err.Message
      text=[string]$err.Extent.Text
    }
  }
}

if($failures.Count -gt 0){
  foreach($failure in $failures){
    Write-Host ("POWERSHELL_SYNTAX_FAIL "+($failure | ConvertTo-Json -Compress -Depth 4))
  }
  Write-Host ("POWERSHELL_SYNTAX_SUMMARY status=FAIL files="+$files.Count+" errors="+$failures.Count)
  exit 1
}

Write-Host ("POWERSHELL_SYNTAX_PASS files="+$files.Count+" errors=0")
exit 0
