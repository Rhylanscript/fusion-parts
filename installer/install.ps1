# Install FusionParts on Windows
#
# Install or upgrade by pasting this one line into PowerShell:
#   - irm https://github.com/Rhylanscript/FusionParts/releases/latest/download/install.ps1 | iex

function Assert-SafeToReplace {
    param($Folder)

    if (-not (Test-Path $Folder)) { return }

    $item = Get-Item $Folder
    $isLink = $item.Attributes -band [IO.FileAttributes]::ReparsePoint
    $isGitClone = Test-Path (Join-Path $Folder ".git")
    if ($isLink -or $isGitClone) {
        throw "$Folder looks like a dev copy (link or git clone), so it was ignored"
    }
}

function Install-AddIn {
    param($Name, $Source, $AddInsFolder, $WorkFolder)

    $zipPath = Join-Path $WorkFolder "$Name.zip"
    $unpacked = Join-Path $WorkFolder $Name

    Write-Host "Getting $Name..."
    if ($Source -match '^https?://') {
        Invoke-WebRequest -Uri $Source -OutFile $zipPath -UseBasicParsing
    } else {
        Copy-Item $Source $zipPath
    }
    Expand-Archive -Path $zipPath -DestinationPath $unpacked -Force

    $manifest = Get-ChildItem -Path $unpacked -Recurse -Filter "$Name.manifest" | Select-Object -First 1
    if (-not $manifest) {
        throw "The $Name download has no $Name.manifest in it, so it isnt a valid add in"
    }

    $target = Join-Path $AddInsFolder $Name
    Assert-SafeToReplace $target
    if (Test-Path $target) {
        Remove-Item -Recurse -Force $target
    }
    Copy-Item -Recurse -Path $manifest.Directory.FullName -Destination $target
}

function Install-FusionParts {
    $ErrorActionPreference = "Stop"
    $ProgressPreference = "SilentlyContinue"
    [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12

    # --- Settings ---------------------------------------------------------
    # which FusionkitRibbonAPI release to install. change this in dev to move to a newer one

    $fusionkitVersion = "v0.1.0"
    $fusionkitUrl = "https://github.com/Rhylanscript/FusionkitRibbonAPI/releases/download/$fusionkitVersion/FusionkitAPI-$fusionkitVersion.zip"
    $partsSource = "https://github.com/Rhylanscript/FusionParts/releases/latest/download/FusionParts.zip"

    # for testing only: point FUSIONPARTS_ZIP at a local zip to use it instead of downloading
    if ($env:FUSIONPARTS_ZIP) { $partsSource = $env:FUSIONPARTS_ZIP }

    # -----------------------------------------------------------------------

    $addIns = Join-Path $env:APPDATA "Autodesk\Autodesk Fusion 360\API\AddIns"
    if (-not (Test-Path $addIns)) {
        throw "Couldn't find Fusion 360s add ins folder at $addIns. Install and open Fusion once, then run this again."
    }

    $work = Join-Path ([IO.Path]::GetTempPath()) ("FusionParts-install-" + [guid]::NewGuid())
    New-Item -ItemType Directory -Path $work | Out-Null
    try {
        if (Test-Path (Join-Path $addIns "FusionkitRibbonAPI")) {
            Write-Host "FusionkitRibbonAPI is already installed, skipping download"
        } else {
            Install-AddIn "FusionkitRibbonAPI" $fusionkitUrl $addIns $work
        }
        Install-AddIn "FusionParts" $partsSource $addIns $work
    } finally {
        Remove-Item -Recurse -Force $work -ErrorAction SilentlyContinue
    }

    Write-Host ""
    Write-Host "Installed to $addIns"
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "  1. Relaunch Fusion 360"
    Write-Host "  2. Press Shift+S and open the add ins tab"
    Write-Host "  3. Select FusionkitRibbonAPI, tick Run on Startup, and enable"
    Write-Host "  4. Select FusionParts and click run (tick run on startup too if you want it every time)"
    Write-Host "FusionkitRibbonAPI has to be running before FusionParts starts, so do it in that order"
}

try {
    Install-FusionParts
} catch {
    Write-Host ""
    Write-Host "Install failed: $($_.Exception.Message)" -ForegroundColor Red
}
