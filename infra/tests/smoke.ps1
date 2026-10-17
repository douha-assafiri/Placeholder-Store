param(
    [Parameter(Mandatory = $true)]
    [uri] $FrontendUrl,
    [Parameter(Mandatory = $true)]
    [uri] $ApiHealthUrl,
    [Parameter(Mandatory = $true)]
    [uri] $UptimeUrl
)

$ErrorActionPreference = "Stop"

foreach ($check in @(
    @{ Name = "frontend"; Url = $FrontendUrl },
    @{ Name = "api readiness"; Url = $ApiHealthUrl },
    @{ Name = "uptime kuma"; Url = $UptimeUrl }
)) {
    $response = Invoke-WebRequest -Uri $check.Url -UseBasicParsing
    if ($response.StatusCode -ne 200) {
        throw "$($check.Name) returned HTTP $($response.StatusCode)."
    }
    Write-Host "$($check.Name): OK"
}

$api = Invoke-RestMethod -Uri $ApiHealthUrl
if ($api.status -ne "ok" -or $api.database -ne "ok") {
    throw "API readiness did not report an available database."
}
