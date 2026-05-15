# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A KiCad library of schematic symbols, PCB footprints, and 3D STEP models for components on JLCPCB's basic and preferred parts list. The Python scripts in the root regenerate the library from JLCPCB's daily-updated parts CSV. The library is distributed as a KiCad PCM package (see `metadata.json`, `repository.json`).

This is a fork of Chris Dirks' (`CDFER`) library. Footprints still reference 3D models at the legacy path `/3dmodels/com_github_CDFER_JLCPCB-Kicad-Library/JLCPCB.3dshapes/...` — `check_models()` in `libraryCreatorScript.py` expects this path; do not "fix" it without updating every `.kicad_mod`.

## Common commands

```bash
# One-time setup (Python 3.13 required — pinned by CI in .github/workflows/update-library.yml)
python -m venv .venv
. .venv/bin/activate            # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# Regenerate the entire library from the latest JLCPCB CSV
python libraryCreatorScript.py

# Format Python (Black, line-length 120 — configured in pyproject.toml)
black .
```

There are no tests and no lint config beyond Black. `libraryCreatorScript.py` is the single end-to-end script — it downloads `jlcpcb-components-basic-preferred.csv` from `https://cdfer.github.io/jlcpcb-parts-database`, regenerates symbols, updates stock on hand-maintained symbols, archives/un-archives parts and 3D models, bumps `metadata.json`, and builds a release ZIP.

`setup_kicad.py`, `cleanup_kicad.py`, `create_package.py` are **Windows end-user helpers** for installing the library manually, removing it, or building a local ZIP. They are not part of the build pipeline and the CI workflow does not call them.

## Architecture

### The two kinds of symbols

The library mixes **auto-generated** symbols (rebuilt from scratch every run) with **hand-maintained** symbols (edited in place). Knowing which category a part falls into is critical before changing code or files:

- **Auto-generated** — keys in the `symbols` dict at `libraryCreatorScript.py:526` (`Resistors`, `Capacitors`, `Diodes`, `Transistors`, `Inductors`, `Variable-Resistors`). For each CSV row that matches one of these categories, the script extracts a value (e.g. `extract_resistance_value`, `extract_capacitor_value`), calls `generate_kicad_symbol()` from `autoLibrarySymbols.py`, accumulates the resulting S-expression strings, and at the end `generate_kicad_symbol_libs()` overwrites `symbols/JLCPCB-<Name>.kicad_sym` wholesale.
- **Hand-maintained** — `Analog`, `Connectors_Buttons`, `Crystals`, `Diode-Packages`, `ICs`, `Interface`, `MCUs`, `Memory`, `Optocouplers`, `Power`, `Transformers`, `Transistor-Packages`. These `.kicad_sym` files are committed to git as the source of truth. The script only **patches them in place** via `update_component_inplace()` (updates price/stock/datasheet/etc.) and `update_library_stock_inplace()` (archives parts with no stock to `Archived-Symbols-Footprints/JLCPCB-Kicad-Symbols/<lcsc>.kicad_sym`, zeros their stock). Editing these symbol files by hand in KiCad is the intended workflow for adding new ICs.

The dispatch logic that decides "auto-generate vs. patch in place" is the long if/elif chain at `libraryCreatorScript.py:615-765`. Each branch matches by `category` / `subcategory` from the CSV, plus per-LCSC overrides (see e.g. `extract_diode_type`, `extract_transistor_type`).

### Archive / un-archive flow

Out-of-stock parts and orphaned footprints/3D models are **moved** (not deleted) into `Archived-Symbols-Footprints/`:

- `Archived-Symbols-Footprints/JLCPCB-Kicad-Symbols/<lcsc>.kicad_sym` — one symbol per file, written by `create_archived_symbol_file()` in `handmadeLibrarySymbols.py`.
- `Archived-Symbols-Footprints/JLCPCB-Kicad-Footprints/*.kicad_mod` — footprints no symbol references, moved by `check_footprints()`.
- `Archived-Symbols-Footprints/JLCPCB-Kicad-Footprints/3dModels/*.step` — STEP files no footprint references, moved by `check_models()`.

When a part comes back into stock or a new symbol references a footprint that lives only in the archive, `check_footprints()` / `check_models()` move it back. This means the archive is **not** dead storage — never `git rm` from it casually.

### Module layout

- `libraryCreatorScript.py` — orchestrator. Reads the CSV, dispatches by category, drops rows from the DataFrame as they're handled, writes any unhandled rows to `leftover.csv` for inspection.
- `autoLibrarySymbols.py` — emits KiCad S-expression text. `generate_header`, `generate_property`, `generate_rectangle`, `generate_polyline`, `generate_pin_pair`, and the big `generate_kicad_symbol()` (≈1300 lines) which hardcodes the geometry/pins for each `mode` (Resistors, Capacitors, Diodes, NMOS, PMOS, NPN, PNP, Schottky, Zener, TVS, LED, Inductor, Ferrite, Fuse, NTC, MOV, …).
- `handmadeLibrarySymbols.py` — patch-in-place helpers for hand-maintained libs: `update_component_inplace`, `update_library_stock_inplace`, `create_archived_symbol_file`.
- `packageTools.py` — `update_version()` rewrites `metadata.json` versions array; `create_zip_archive()` zips the release skipping files ≤128 bytes.
- `LLM-Check-Pinswaps.ipynb` — notebook for spot-checking pin assignments. Not part of the build.

### CI / release pipeline

`.github/workflows/update-library.yml` runs daily at 06:00 UTC (25 min after the upstream `jlcpcb-parts-database` rebuild) and on manual dispatch:
1. `pip install -r requirements.txt`
2. `python libraryCreatorScript.py`
3. `stefanzweifel/git-auto-commit-action` commits all changes
4. Builds `JLCPCB-KiCad-Library-YYYY.MM.DD.zip` from `metadata.json`, `LICENSE`, `README.md`, `symbols/`, `footprints/`, `3dmodels/`, `resources/`
5. `softprops/action-gh-release` cuts a release tagged with the current date

`repository.json` (consumed by the KiCad Plugin & Content Manager) lives in a **separate** repo (`HenriqueAleixo/Kicad-Library`); the copy in this repo is a template/reference. After each release the `download_sha256` and `download_size` in that other repo need to be updated — see `SETUP_GUIDE.md` step 4.

## Conventions

- **Do not commit `metadata.json` version bumps** — the CI workflow rewrites it on every run via `update_version()`. Local runs will modify it; revert before committing.
- **Do not commit changes to auto-generated `.kicad_sym` files** (the six listed above) when your change is purely Python — the CI run will regenerate them and produce a merge conflict otherwise. The README explicitly calls this out.
- Per-component overrides (a quirky LCSC ID, an off-pattern description) go as `if lcsc == <id>: return ...` blocks at the top of the relevant `extract_*` function. There are dozens of these — follow the existing pattern rather than adding a separate exception table.
- Parts with `price > 3.0 USD`, footprint `0201`, or `stock < min_order_qty` are dropped early at `libraryCreatorScript.py:583`. If a part you expect is missing from the output, check this filter first.
- Unicode `℃` is normalized to `°C` in every emitted file (`libraryCreatorScript.py:374`, `handmadeLibrarySymbols.py:110`). Keep that replacement in any new generator.
- Black with `line-length = 120` (see `pyproject.toml`). The cSpell dictionary in `.vscode/settings.json` lists project-specific terms (LCSC, JLCPCB, transistor package names, etc.) — add new acronyms there to keep the spell-checker quiet.

## Branch policy for this session

Development for this task happens on `claude/add-claude-documentation-6QiuB`. Push with `git push -u origin claude/add-claude-documentation-6QiuB`. Do not push to `main`.
