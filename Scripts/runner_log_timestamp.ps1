function ConvertFrom-RunnerLogTimestampUtc {
    param([string]$Line)

    if ([string]::IsNullOrWhiteSpace($Line)) { return $null }

    foreach ($pattern in @(
        '^\[(?<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}Z)\s',
        '^\[RUNNER (?<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}Z)\s'
    )) {
        if ($Line -match $pattern) {
            return [DateTime]::ParseExact(
                $Matches["ts"],
                "yyyy-MM-dd HH:mm:ssZ",
                [Globalization.CultureInfo]::InvariantCulture,
                [Globalization.DateTimeStyles]::AssumeUniversal
            ).ToUniversalTime()
        }
    }

    return $null
}
