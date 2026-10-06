#!/usr/bin/env bash
# FusionParts installer for macOS
#
# Install or upgrade by pasting this one line into Terminal:
#   curl -fsSL https://github.com/Rhylanscript/FusionParts/releases/latest/download/install.sh | bash

set -euo pipefail

# --- Settings -------------------------------------------------------------
# Which FusionkitRibbonAPI release to instal. change this to move to a newer one

FUSIONKIT_VERSION="v0.1.0"
FUSIONKIT_URL="https://github.com/Rhylanscript/FusionkitRibbonAPI/releases/download/${FUSIONKIT_VERSION}/FusionkitAPI-${FUSIONKIT_VERSION}.zip"

# For testing set FUSIONPARTS_ZIP to a local zip to use it instead of downloading
PARTS_SOURCE="${FUSIONPARTS_ZIP:-https://github.com/Rhylanscript/FusionParts/releases/latest/download/FusionParts.zip}"

# ---------------------------------------------------------------------------

ADDINS="$HOME/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns"

fail() {
    echo "" >&2
    echo "Install failed: $1" >&2
    exit 1
}

check_safe_to_replace() {
    local folder="$1"
    if [ -L "$folder" ] || [ -e "$folder/.git" ]; then
        fail "$folder looks like a development copy (a link or git clone), so it was left alone."
    fi
}

install_addin() {
    local name="$1"
    local from="$2"
    local zip_file="$WORK/$name.zip"
    local unpacked="$WORK/$name"

    echo "Getting $name..."
    case "$from" in
        http*) curl -fsSL "$from" -o "$zip_file" || fail "couldn't download $from" ;;
        *)     cp "$from" "$zip_file" || fail "couldn't read $from" ;;
    esac
    mkdir -p "$unpacked"
    unzip -q "$zip_file" -d "$unpacked" || fail "couldn't unzip the $name download"

    local manifest
    manifest="$(find "$unpacked" -name "$name.manifest" -not -path "*/__MACOSX/*" | sed -n 1p)"
    [ -n "$manifest" ] || fail "the $name download has no $name.manifest in it, so it isnt a valid add-in."

    local target="$ADDINS/$name"
    check_safe_to_replace "$target"
    rm -rf "$target"
    cp -R "$(dirname "$manifest")" "$target"
}

[ -d "$ADDINS" ] || fail "couldn't find Fusion's add-ins folder at $ADDINS. Install and open Fusion once, then run this again."

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

if [ -d "$ADDINS/FusionkitRibbonAPI" ]; then
    echo "FusionkitRibbonAPI is already installed, skipping download"
else
    install_addin "FusionkitRibbonAPI" "$FUSIONKIT_URL"
fi
install_addin "FusionParts" "$PARTS_SOURCE"

echo ""
echo "Installed to $ADDINS"
echo ""
echo "Next steps:"
echo "  1. Relaunch Fusion 360"
echo "  2. Press Shift+S and open the add ins tab"
echo "  3. Select FusionkitRibbonAPI, tick Run on Startup, and enable"
echo "  4. Select FusionParts and click run (tick run on startup too if you want it every time)"
echo "FusionkitRibbonAPI has to be running before FusionParts starts, so do it in that order"
