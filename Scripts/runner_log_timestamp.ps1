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


function Get-RunnerBrokerEvidenceFromLines {
    param([string[]]$Lines)

    $ackUtc = $null
    $runningUtc = $null
    $errorUtc = $null
    $healthyUtc = $null

    foreach ($line in @($Lines)) {
        $parsed = ConvertFrom-RunnerLogTimestampUtc -Line $line
        if ($null -eq $parsed) { continue }

        if ($line -match 'Acknowledging runner request') {
            $ackUtc = $parsed
            $healthyUtc = $parsed
            continue
        }

        if ($line -match 'Running job:') {
            $runningUtc = $parsed
            $healthyUtc = $parsed
            continue
        }

        if ($line -match 'Listening for Jobs|Get next message|Message received|Session created|Connected to GitHub') {
            $healthyUtc = $parsed
            continue
        }

        if ($line -match 'BrokerServer\].*ERR|SocketException|Unable to read data from the transport connection|I/O operation has been aborted') {
            $errorUtc = $parsed
        }
    }

    return [pscustomobject]@{
        AckUtc = $ackUtc
        RunningUtc = $runningUtc
        ErrorUtc = $errorUtc
        HealthyUtc = $healthyUtc
    }
}
