# FusionParts

![CI][ci_badge]

Onshape style part generators for Fusion 360: spur gears, timing pulleys and timing belts. Everything runs in normal Fusion dialogs.

## Tools

| Tool              | What it makes                                                                    |
| ----------------- | -------------------------------------------------------------------------------- |
| **Spur Gear**     | Involute spur gear with a shaft bore                                             |
| **Timing Pulley** | HTD 3M and HTD 5M pulleys with flanges, an engraved tooth count and a shaft bore |
| **Timing Belt**   | A smooth belt loop (no teeth) around two pulleys, sized to fit them              |

All three add a button to the **Fusionkit** tab, in the **Parts** panel.

### Spur Gear

Teeth (6 to 200), module, pressure angle (10 to 30 degrees), thickness, shaft bore and output.

### Timing Pulley

Belt profile, teeth (10 to 200), belt width, belt clearance, flanges (both, bottom only or none) with thickness, overhang and cone length, an engraved tooth count (position, offset, depth and text height), shaft bore and output.

### Timing Belt

Belt profile, teeth on each pulley, centre distance, belt width and output. The dialog shows the belt's pitch length and tooth count. Real belts come in whole tooth counts, so adjust the centre distance until the readout is close to a whole number.

The belt sits on the tooth tips of two pulleys made with the Timing Pulley tool. Pulley 1 is at the component origin and pulley 2 is at the centre distance along the X axis.

### Shaft bores

goBILDA 8 mm REX and 12 mm REX, or no bore. A bore clearance field makes the hole slightly larger than the shaft.

### Output

- **New component** builds into a new component.
- **New body** builds a loose body in the root component.

Which choices appear depends on the design: part designs offer body only, assembly designs offer component only, and hybrid designs offer both.

## Requirements

- Autodesk Fusion (Windows or macOS)
- [FusionkitRibbonAPI][fk], the add-in that provides the Fusionkit ribbon tab

## Installation

### Quick install

**Windows:** open PowerShell and paste:

```powershell
irm https://github.com/Rhylanscript/FusionParts/releases/latest/download/install.ps1 | iex
```

**macOS:** open Terminal and paste:

```bash
curl -fsSL https://github.com/Rhylanscript/FusionParts/releases/latest/download/install.sh | bash
```

The script installs FusionParts and, if you don't have it, [FusionkitRibbonAPI][fk]. Running it again upgrades FusionParts. The scripts are short, so you can read them first in the [`installer`][install] folder.

Then in Fusion:

1. Fully close and reopen Fusion, then press `Shift+S` and open the **Add Ins** tab.
2. Select **FusionkitRibbonAPI**, tick **Run on Startup** and click **Run**.
3. Select **FusionParts** and click **Run** (tick **Run on Startup** too if you want it every time).

### Manual install

1. Install FusionkitRibbonAPI by following its README. Turn on **Run on Startup** for it.
2. Download the latest `FusionParts` zip from the [Releases][fp-releases] page and unzip it.
3. Copy the `FusionParts` folder into Fusion's add-ins folder:

   | OS      | Path                                                                     |
   | ------- | ------------------------------------------------------------------------ |
   | Windows | `%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\`                     |
   | macOS   | `~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/` |

4. In Fusion, press `Shift+S`, open the **Add Ins** tab, select **FusionParts** and enable it.

## Accuracy

Tooth shapes and belt dimensions come from example parts and published datasheets, not from official standard drawings. Please check fit with your real pulleys, belts and shafts before you manufacture anything. Report any dimension that is off in an issue.

## Development

Clone the repo into Fusion's add-ins folder (or link it there) so the folder is named `FusionParts`. The folder name, the `.py` file name and the `.manifest` file name must all match.

```files
FusionParts/
    FusionParts.py        entry point (run / stop)
    core/                 shared helpers: sketches, features, dialogs, bores, belts
    generators/           one file (or a few) per tool; the math lives in *_profile / *_path files
    resources/            toolbar and dropdown icons
```

### Running the checks

The geometry math can be tested outside Fusion. From the repo folder, using a normal Python install (not Fusion's):

```bash
py -m pip install pytest ruff
py -m ruff check .
py -m pytest
```

GitHub runs the same checks on every push and pull request.

### Making a release

1. Set `version` in `FusionParts.manifest`.
2. In `CHANGELOG.md`, rename `[Unreleased]` to the new version and date, and add a fresh empty `[Unreleased]` above it.
3. Merge to `main`. GitHub tags the version, builds `FusionParts-vX.Y.Z.zip` and publishes the release.

## License

MIT License. See [LICENSE][license].

<!-- links -->

[license]: LICENSE
[install]: installer

[fk]: https://github.com/rhylanscript/FusionkitRibbonAPI
[fp-releases]: https://github.com/Rhylanscript/fusion-parts/releases
[ci_badge]: https://github.com/Rhylanscript/fusion-parts/actions/workflows/ci.yml/badge.svg
