param()

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path $PSScriptRoot -Parent
Push-Location $ProjectRoot
try {
    $tests = @(
        @("python","Scripts/pre_unreal_validate.py"),
        @("python","Scripts/project_governor.py"),
        @("python","Scripts/asset_quality_audit.py","--strict"),
        @("python","Scripts/production_readiness_audit.py"),
        @("python","Scripts/deep_project_audit.py"),
        @("python","-m","unittest","discover","-s","Scripts","-p","test_runtime_smoke.py","-v"),
        @("python","-m","unittest","discover","-s","Scripts","-p","test_runtime_audit_contracts.py","-v"),
        @("python","-m","unittest","discover","-s","Scripts","-p","test_source_contracts.py","-v"),
        @("python","-m","unittest","discover","-s","Scripts","-p","test_governance_contracts.py","-v"),
        @("python","-m","unittest","discover","-s","Scripts","-p","test_warning_debt_guard.py","-v"),
        @("python","-m","unittest","discover","-s","Scripts","-p","test_deep_project_audit.py","-v"),
        @("python","-m","unittest","discover","-s","Scripts","-p","test_governor_handoff.py","-v"),
        @("python","-m","unittest","discover","-s","Scripts","-p","test_streaming_cancellation_contract.py","-v"),
        @("python","-m","unittest","discover","-s","Scripts","-p","test_live_governor_status.py","-v")
    )
    foreach ($test in $tests) {
        $exe = $test[0]
        $args = @($test[1..($test.Count-1)])
        Write-Host ("RUN " + $exe + " " + ($args -join " "))
        & $exe @args
        if ($LASTEXITCODE -ne 0) { throw "Static validation failed: $exe $($args -join ' ')" }
    }
    Write-Host "SHIRE_LOCAL_STATIC_VALIDATION_PASS"
}
finally {
    Pop-Location
}
