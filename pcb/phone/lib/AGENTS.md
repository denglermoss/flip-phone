# AGENTS.md — KiCad Symbol Library Directory

This directory contains the project's custom KiCad symbol libraries, footprints,
and 3D models. The libraries were built from LCSC/JLC parts downloaded via
`easyeda2kicad.py`, then categorized into 4 libraries and hand-curated (pin
types fixed, descriptions added) during the 2026-07-22 library rebuild.

## Directory Structure

```
lib/
  passives.kicad_sym      # Resistors, caps, inductors, ferrites, LEDs, tantalum polymer
  ics.kicad_sym           # MCU, modem, codec, power ICs, level shifters, ESD
  connectors.kicad_sym    # USB-C, SIM, microSD, FPC, U.FL, JST, mini-PCIe, headphone jack
  electromech.kicad_sym   # Tactile switches, slide switch, crystal
  easyeda2kicad.pretty/   # Footprints (.kicad_mod) — all footprints live here
  easyeda2kicad.3dshapes/ # 3D models (.step, .wrl) — all 3D models live here
  tensility.pretty/       # Tensility connector footprints (DigiKey-sourced, e.g. 54-00298 headphone jack)
```

## Library Tables

The project's `sym-lib-table` and `fp-lib-table` (in `pcb/phone/`) register
these libraries. There are no temporary or source libraries — the 4 categorized
`.kicad_sym` files are the single source of truth for symbols.

## CRITICAL: Encoding Rules (read this before editing any .kicad_sym file)

KiCad symbol libraries are S-expression text files. They must be:

1. **UTF-8 encoded, NO BOM.** A UTF-8 Byte Order Mark (`EF BB BF`) before the
   opening `(kicad_symbol_lib` paren will cause KiCad to silently fail parsing
   and load the library as **empty**. This has happened before (2026-07-22) and
   was caused by a Windows editor saving the file with a BOM.

2. **LF line endings.** Git will warn about CRLF conversion. If you edit a
   `.kicad_sym` file manually, ensure your editor uses LF, not CRLF.

3. **CJK characters must be preserved as real UTF-8.** Many LCSC parts have
   Chinese manufacturer names (e.g. `华德共创`, `首韩`, `广濑`, `硕方`) and
   Chinese punctuation (e.g. `，` U+FF0C). If a Windows editor opens the file
   as CP1252 (its default codepage) and re-saves as UTF-8, these characters
   become **irreversible mojibake** — the original UTF-8 bytes are interpreted
   as CP1252 characters, re-encoded to UTF-8, and bytes at undefined CP1252
   positions (0x81, 0x8D, 0x8F, 0x90, 0x9D) are permanently lost.

### How to safely edit .kicad_sym files

- **Use VS Code** (set encoding to UTF-8 without BOM in the status bar) or
  KiCad's own Symbol Editor. **Never** open a `.kicad_sym` file in Notepad or
  a Windows editor that auto-detects encoding as CP1252.

- **After any manual edit**, verify the file:
  ```powershell
  # Check for BOM (should be empty / start with 28 = '(')
  Get-Content pcb/phone/lib/connectors.kicad_sym -Encoding Byte -TotalCount 3 | ForEach-Object { '{0:X2}' -f $_ }
  # Check for mojibake (should find 0)
  python -c "import re; c=open(r'pcb/phone/lib/connectors.kicad_sym','r',encoding='utf-8').read(); bad=[s for s in re.findall(r'\"([^\"]*)\"',c) if any(0x80<=ord(c)<0x4E00 and not(0xFF00<=ord(c)<=0xFFEF) for c in s)]; print(f'mojibake strings: {len(bad)}')"
  ```

## Adding a new part

1. Download the symbol via `easyeda2kicad.py` (outputs to a temporary file).
2. Open the downloaded symbol in KiCad's Symbol Editor and save it into the
   appropriate project library (`passives`, `ics`, `connectors`, or
   `electromech`).
3. Verify pin types are correct (easyeda2kicad auto-generates `unspecified`/
   `input` for most pins — fix them per datasheet: power pins → `power_in`,
   NC → `no_connect`, bidirectional data → `bidirectional`, etc.).
4. Add a `ki_description` property (<20 char) to the symbol.
5. Ensure the `Footprint` property points to `easyeda2kicad:<footprint_name>`
   (or `tensility:<footprint_name>` for Tensility parts).
6. If the schematic references the new symbol, update the `lib_id` in the
   schematic file to use the new library prefix.

## History

The original `easyeda2kicad.kicad_sym` (single monolithic library) and
`missing_parts.kicad_sym` (manually-created symbols) were split into 4
categorized libraries on 2026-07-22. The rebuild scripts (`rebuild_lib.py`,
`update_sch_refs.py`, `extract_pins.py`) were one-time migration tools and
have been deleted — the 4 output libraries are now the source of truth. See
`docs/ref/project-log.md` 2026-07-22 Library Rebuild entry for details.

The `temp_switch`, `temp_470uf`, and `temp_10uf` temporary libraries
(created 2026-07-24 for parts added after the rebuild) were merged into the
main libraries on 2026-07-28: `SSSS811101` → `electromech`,
`6TPF470MAH` → `passives`, `CL10A106KP8NNNC` (temp_10uf) was unused and
deleted.
