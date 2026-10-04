import json
import re

from conftest import ROOT

def test_manifest_matches_folder_and_entry_file():
    manifest = json.loads((ROOT / "FusionParts.manifest").read_text())
    assert (ROOT / "FusionParts.py").is_file()
    assert manifest["type"] == "addin"
    assert re.fullmatch(r"\d+\.\d+\.\d+", manifest["version"])
    assert "windows" in manifest["supportedOS"]
    assert "mac" in manifest["supportedOS"]


def test_icon_folders_are_complete():
    for icon in (ROOT / "resources").iterdir():
        for name in ("16x16.png", "32x32.png", "16x16@2x.png"):
            assert (icon / name).is_file(), "%s is missing %s" % (icon.name, name)
