"""Lets the tests import the add in the same way Fusion does: as FusionParts.*"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

assert ROOT.name == "FusionParts", (
    "The repo folder must be named FusionParts (the add-in folder name has to "
    "match FusionParts.py and FusionParts.manifest)."
)

sys.path[:] = [p for p in sys.path if Path(p or ".").resolve() != ROOT]
sys.path.insert(0, str(ROOT.parent))
