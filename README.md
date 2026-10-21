# OOO

[![Progress](https://bytematch.dev/chrispl1920-debug/OOO.svg)](https://bytematch.dev/chrispl1920-debug/OOO)

A new reverse-engineering project for **Out of Ore**, version label **0.36.5552**.
The executable SHA-256 in `config/0.36.5552.json` pins the actual input. The version
label was provided by the maintainer; it has not been independently recovered from
the encrypted game content.

Current result: **four recovered money setters, 27 native code bytes**, each matching
its captured original instructions in isolation. The partial object layouts are
reconstructed views, not recovered original class declarations. This project does
not yet rebuild or relink the game. All objdiff units therefore have `complete: false`.
Fuel setter and Unreal wrapper drafts are in `research/0.36.5552/fuel/`.

## Build the recovered code

Use Windows x64, Python 3.12+, and Visual Studio with the C++ build tools and Windows
SDK. The build discovers the installed MSVC and MASM tools automatically.

```powershell
python configure.py
python build.py
python -m unittest discover -s tests -p 'test_*.py'
objdiff-cli report generate -o build/0.36.5552/report.json
python tools/check_report.py
```

Use objdiff-cli **3.8.3**. `build.py` assembles the fixed original-instruction references,
compiles the reconstructed C++, runs 20 boundary/adjacent-field preservation cases,
and generates `objdiff.json`. Edit `configure.py` or the version manifest, not the
ignored generated JSON. Unit names follow `src/`, paths use `/`, and `complete`
requires both a verified match and linkage from source. There are no progress categories yet.

## Start analyzing the installed game

```powershell
python -m pip install -r requirements.txt
python tools/inspect_install.py --game-dir 'D:\SteamLibrary\steamapps\common\OutofOre'
```

For a fresh code capture, launch your game normally and obtain the shipping process ID:

```powershell
Get-Process -Name 'OutOfOre-Win64-Shipping' | Select-Object Id
python tools/capture_code.py --game-dir 'D:\SteamLibrary\steamapps\common\OutofOre' --pid <PID>
```

The capture reads only the main executable's `.text`, verifies its known functions,
and creates an ignored local analysis copy. It does not write to the game process
or the install. After capture, the game can be left running or closed.

Install [Ghidra 12.1.4](https://github.com/NationalSecurityAgency/ghidra/releases/tag/Ghidra_12.1.4_build)
and a compatible JDK, then export the identified functions:

```powershell
./tools/decompile.ps1 -GhidraHome 'C:/tools/ghidra_12.1.4_PUBLIC'
```

Generated C is an analysis draft: review its types, calling convention, control flow,
and references before moving it into `src/`. The current scripts export selected
functions rather than attempt automatic analysis of the entire engine.

## CI and ByteMatch

The workflow builds and tests on `main` pushes and pull requests, generates
`build/0.36.5552/report.json`, verifies the original reference hashes, and uploads it.
No secrets or upload tokens are needed.

**The current artifact is `0.36.5552_research`.** Its 100% result covers just the four
setters. Publishing it as whole-game progress would incorrectly show the game as
100% matched. The badge will remain pending until real whole-game tracking is ready.

ByteMatch's [artifact rules](https://bytematch.dev/docs/getting-started) require a
successful default-branch push run and a `<VERSION>_report` artifact. Once an audited
whole-game target baseline and build coverage exist, set `scope` to `whole-game` and
`bytematch_ready` to `true` in the version manifest. The same verified workflow then
uploads `0.36.5552_report` automatically. Keep `linked_from_source` false until the
actual game build links that unit from reconstructed source.

There is no functional-C list: raw Ghidra drafts are not evidence of working code.
Register the repository on ByteMatch when the full baseline is ready; the README
badge already uses its project URL.

See [the first analysis and remaining work](docs/first-analysis.md).
