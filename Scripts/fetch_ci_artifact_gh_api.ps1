<#
Download an exact-name GitHub Actions artifact via GitHub REST.
Avoid actions/download-artifact bootstrap on the unreliable Windows codeload path.
This script is one read-only source step within the single serialized Windows UE writer.
#>
param(
  [Parameter(Mandatory=$true)][long]$RunId,
  [Parameter(Mandatory=$true)][string]$ArtifactName,
  [Parameter(Mandatory=$true)][string]$Destination
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$token = $env:GH_ARTIFACT_TOKEN
$repo = $env:GITHUB_REPOSITORY
if ([string]::IsNullOrWhiteSpace($token) -or
    $repo -notmatch '^[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+$') {
  throw "CI_ARTIFACT_AUTH_OR_REPO_INVALID"
}
$headers = @{
  Authorization = "Bearer $token"
  Accept = "application/vnd.github+json"
  "X-GitHub-Api-Version" = "2022-11-28"
}
$endpoint = "https://api.github.com/repos/$repo/actions/runs/$RunId/artifacts?per_page=100"
$artifacts = Invoke-RestMethod -Uri $endpoint -Headers $headers -TimeoutSec 120
$hits = @($artifacts.artifacts | Where-Object {
  $_.name -ceq $ArtifactName -and -not $_.expired
})
if ($hits.Count -ne 1) {
  throw "CI_ARTIFACT_PIN_MISSING_OR_DUPLICATE name=$ArtifactName run=$RunId count=$($hits.Count)"
}
$artifactId = [long]$hits[0].id
$downloadEndpoint = "https://api.github.com/repos/$repo/actions/artifacts/$artifactId/zip"
$zip = Join-Path $env:RUNNER_TEMP ("shiresource-" + $artifactId + ".zip")
$success = $false
for ($attempt = 1; $attempt -le 3 -and -not $success; $attempt++) {
  try {
    # Never forward the bearer token to the redirect's Azure blob URL.
    $req = [Net.HttpWebRequest][Net.WebRequest]::Create($downloadEndpoint)
    $req.Method = "GET"
    $req.Accept = "application/vnd.github+json"
    $req.Headers["Authorization"] = "Bearer $token"
    $req.AllowAutoRedirect = $false
    $req.Timeout = 120000
    $response = $null
    try { $response = $req.GetResponse() }
    catch [Net.WebException] {
      if ($_.Exception.Response) { $response = $_.Exception.Response }
      else { throw }
    }
    if (-not $response) { throw "CI_ARTIFACT_NO_REDIRECT_RESPONSE" }
    $status = [int]$response.StatusCode
    $location = [string]$response.Headers["Location"]
    $response.Close()
    if ($status -ne 302 -or -not $location.StartsWith("https://")) {
      throw "CI_ARTIFACT_REDIRECT_REJECT status=$status"
    }
    Invoke-WebRequest -Uri $location -OutFile $zip -UseBasicParsing -TimeoutSec 600
    if (!(Test-Path -LiteralPath $zip -PathType Leaf) -or
        (Get-Item -LiteralPath $zip).Length -lt 1000) {
      throw "CI_ARTIFACT_EMPTY_ZIP"
    }
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $archive = [IO.Compression.ZipFile]::OpenRead($zip)
    try {
      if ($archive.Entries.Count -le 0) { throw "CI_ARTIFACT_EMPTY_ENTRIES" }
      foreach ($entry in $archive.Entries) {
        if ($entry.FullName.StartsWith("/") -or $entry.FullName.Contains("..") -or
            $entry.FullName.Contains(":")) {
          throw "CI_ARTIFACT_PATH_TRAVERSAL_REJECT"
        }
      }
    } finally { $archive.Dispose() }
    New-Item -ItemType Directory -Path $Destination -Force | Out-Null
    Expand-Archive -LiteralPath $zip -DestinationPath $Destination -Force
    if ($ArtifactName -like "kaykit-character-source-*") {
      if (!(Test-Path -LiteralPath (Join-Path $Destination "source_receipt.json"))) {
        throw "CI_CHARACTER_SOURCE_RECEIPT_MISSING"
      }
    }
    elseif ($ArtifactName -like "whole-game-original-support-source-*") {
      foreach ($required in @("index.json", "WHOLEGAME_28_SUPPORT.zip")) {
        if (!(Test-Path -LiteralPath (Join-Path $Destination $required))) {
          throw "CI_REGIONAL_SOURCE_ARTIFACT_INCOMPLETE missing=$required"
        }
      }
    }
    $success = $true
  }
  catch {
    Write-Warning "CI_ARTIFACT_DOWNLOAD_RETRY id=$artifactId attempt=$attempt reason=$($_.Exception.Message)"
    if ($attempt -eq 3) { throw }
    Start-Sleep -Seconds (5 * $attempt)
  }
  finally {
    if (Test-Path -LiteralPath $zip) {
      Remove-Item -LiteralPath $zip -Force -ErrorAction SilentlyContinue
    }
  }
}
if (-not $success) { throw "CI_ARTIFACT_DOWNLOAD_NOT_COMPLETED" }
Write-Host "CI_ARTIFACT_REST_VERIFIED run=$RunId id=$artifactId name=$ArtifactName localExtract=pass"
