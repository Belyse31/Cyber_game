Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$root    = Split-Path -Parent $PSScriptRoot
$distDir = Join-Path $root "dist"
$outZip  = Join-Path $distDir "CyberGame.zip"
$stage   = Join-Path $distDir "_stage"
if (!(Test-Path $distDir)) { New-Item -ItemType Directory -Path $distDir | Out-Null }
if (Test-Path $stage)      { Remove-Item -Recurse -Force $stage }
New-Item -ItemType Directory -Path $stage | Out-Null
$embedZip  = Join-Path $root "runtime\python-embed.zip"
$pythonDir = Join-Path $root "runtime\python"
if (Test-Path $embedZip) {
    if (!(Test-Path $pythonDir)) {
        Write-Host "[build] extracting portable Python..."
        Expand-Archive -Path $embedZip -DestinationPath $pythonDir -Force
    } else {
        Write-Host "[build] portable Python already extracted, skipping."
    }
} else {
    Write-Warning "[build] runtime\python-embed.zip not found -- VM will need to download Python."
}
Write-Host "[build] staging files..."
@("game","server","tools","runtime","wheelhouse","requirements.txt","run_game.py","README.md") | ForEach-Object {
    $src = Join-Path $root $_
    if (Test-Path $src) { Copy-Item -Recurse -Force $src $stage }
}
Copy-Item -Force (Join-Path $PSScriptRoot "start.bat") (Join-Path $stage "start.bat")
Copy-Item -Force (Join-Path $root "tools\remove_game.bat") (Join-Path $stage "remove_game.bat")
Write-Host "[build] writing zip: $outZip"
if (Test-Path $outZip) { Remove-Item -Force $outZip }
Compress-Archive -Path (Join-Path $stage "*") -DestinationPath $outZip -Force
Remove-Item -Recurse -Force $stage
Write-Host "[build] done. Output: $outZip"