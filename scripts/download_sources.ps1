# Download public sources listed in the manifest. Existing originals are preserved.
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$entries = Get-Content -LiteralPath (Join-Path $projectRoot 'data/source_manifest.json') -Raw | ConvertFrom-Json
foreach ($entry in $entries) {
    $targetPath = Join-Path $projectRoot $entry.path
    if (Test-Path -LiteralPath $targetPath) { continue }
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $targetPath) | Out-Null
    $partialPath = "$targetPath.partial"
    try {
        Invoke-WebRequest -Uri $entry.url -OutFile $partialPath -TimeoutSec 300
        Move-Item -LiteralPath $partialPath -Destination $targetPath
        Write-Output "Downloaded $($entry.id)"
    } catch {
        Write-Warning "Could not download $($entry.id). Retry later; the importer reports unavailable sources."
        if (Test-Path -LiteralPath $partialPath) { Remove-Item -LiteralPath $partialPath }
    }
}
