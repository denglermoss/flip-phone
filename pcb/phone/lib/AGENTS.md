# AGENTS.md — KiCad Symbol Library Directory

This directory contains the project's custom KiCad symbol libraries, footprints,
3D models, and the Python scripts that generate and verify them.

## Directory Structure

```
lib/
  rebuild_lib.py          # Merges + categorizes + transforms source libs into 4 output libs
  verify_lib.py           # Sanity-checks output libs (pin types, ki_description coverage)
  extract_pins.py         # Extracts pin info from symbols (utility)
  update_sch_refs.py      # Updates schematic symbol references after lib changes
  easyeda2kicad.kicad_sym # Source: symbols downloaded via easyeda2kicad.py (DO NOT hand-edit)
  missing_parts.kicad_sym # Source: manually-created symbols not on LCSC (DO NOT hand-edit)
  passives.kicad_sym      # Output: resistors, caps, inductors, ferrites, LEDs
  ics.kicad_sym           # Output: MCU, modem, codec, power ICs, level shifters, ESD
  connectors.kicad_sym    # Output: USB-C, SIM, microSD, FPC, U.FL, JST, mini-PCIe
  electromech.kicad_sym   # Output: tactile switches, crystal
  easyeda2kicad.pretty/   # Footprints (.kicad_mod)
  easyeda2kicad.3dshapes/ # 3D models (.step, .wrl)
```

## CRITICAL: Encoding Rules (read this before editing any .kicad_sym file)

KiCad symbol libraries are S-expression text files. They must be:

1. **UTF-8 encoded, NO BOM.** A UTF-8 Byte Order Mark (`EF BB BF`) before the
   opening `(kicad_symbol_lib` paren will cause KiCad to silently fail parsing
   and load the library as **empty**. This has happened before (2026-07-22) and
   was caused by a Windows editor saving the file with a BOM.

2. **LF line endings.** Git will warn about CRLF conversion. The `rebuild_lib.py`
   script writes with `newline='\n'` to enforce this. If you edit a `.kicad_sym`
   file manually, ensure your editor uses LF, not CRLF.

3. **CJK characters must be preserved as real UTF-8.** Many LCSC parts have
   Chinese manufacturer names (e.g. `华德共创`, `首韩`, `广濑`, `硕方`) and
   Chinese punctuation (e.g. `，` U+FF0C). If a Windows editor opens the file
   as CP1252 (its default codepage) and re-saves as UTF-8, these characters
   become **irreversible mojibake** — the original UTF-8 bytes are interpreted
   as CP1252 characters, re-encoded to UTF-8, and bytes at undefined CP1252
   positions (0x81, 0x8D, 0x8F, 0x90, 0x9D) are permanently lost.

### How to safely edit .kicad_sym files

- **Preferred:** Edit the source files (`easyeda2kicad.kicad_sym` or
  `missing_parts.kicad_sym`) and re-run `python rebuild_lib.py` to regenerate
  all 4 output libraries. The script reads/writes with `encoding='utf-8'` and
  `newline='\n'`, so it cannot introduce BOM or mojibake.

- **If you must edit an output .kad_sym file directly** (e.g. KiCad's Symbol
  Editor), verify the file afterward:
  ```powershell
  # Check for BOM (should be empty / start with 28 = '(')
  Get-Content pcb/phone/lib/connectors.kicad_sym -Encoding Byte -TotalCount 3 | ForEach-Object { '{0:X2}' -f $_ }
  # Check for mojibake (should find 0)
  python -c "import re; c=open(r'pcb/phone/lib/connectors.kicad_sym','r',encoding='utf-8').read(); bad=[s for s in re.findall(r'\"([^\"]*)\"',c) if any(0x80<=ord(c)<0x4E00 and not(0xFF00<=ord(c)<=0xFFEF) for c in s)]; print(f'mojibake strings: {len(bad)}')"
  ```

- **Never** open a `.kicad_sym` file in Notepad or a Windows editor that
  auto-detects encoding as CP1252. Use VS Code (set encoding to UTF-8 without
  BOM in the status bar) or KiCad's own Symbol Editor.

- **After any manual edit**, run `python verify_lib.py` to confirm pin types
  and ki_description coverage are intact.

## Rebuild Workflow

```powershell
cd pcb/phone/lib
python rebuild_lib.py    # Regenerates passives/ics/connectors/electromech .kicad_sym
python verify_lib.py     # Verify pin types + descriptions
```

`rebuild_lib.py` reads from `easyeda2kicad.kicad_sym` + `missing_parts.kicad_sym`,
applies pin-type fixes, adds ki_description properties, and writes 4 categorized
libraries. The categorization sets (`PASSIVES`, `ICS`, `CONNECTORS`, `ELECTROMECH`)
and descriptions (`DESCRIPTIONS`) are defined in the script itself.

### Adding a new part

1. Download the symbol via `easyeda2kicad.py` (outputs to `easyeda2kicad.kicad_sym`)
   or create it manually in `missing_parts.kicad_sym`.
2. Add the part name to the appropriate category set in `rebuild_lib.py`.
3. Add a short description (<20 chars) to the `DESCRIPTIONS` dict.
4. Add pin-type rules in `get_pin_type()` if the part has IC pins (not needed
   for passives/connectors — they default to `passive`).
5. Run `python rebuild_lib.py` then `python verify_lib.py`.
6. If the schematic references the new symbol, run `python update_sch_refs.py`.
