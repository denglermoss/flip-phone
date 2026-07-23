---
name: kicad-review
description: Run DRC/ERC and inspect the current KiCad design. Read-only — reports findings without modifying files.
triggers:
  - user
  - model
subagent: true
agent: kicad-inspector
---

Run a full design review on the current KiCad project (`pcb/phone/phone.kicad_pro`). This is a read-only operation — no files are modified.

## What to check

1. **ERC (Electrical Rules Check)** on the schematic — run via `kicad` MCP server tools or `kicad-cli sch erc`. Report all errors and warnings.
2. **DRC (Design Rules Check)** on the PCB (if a `.kicad_pcb` exists) — run via `kicad` MCP server tools or `kicad-cli pcb drc`. Report all errors and warnings.
3. **Netlist consistency** — verify the schematic netlist is internally consistent (no floating nets, no unconnected pins that should be connected).
4. **BOM cross-check** — if a BOM exists in `docs/bom.md`, verify the schematic components match the documented parts.

## Report format

- **ERC results**: pass/fail, list of errors with severity, location (sheet + component/refdes)
- **DRC results**: pass/fail, list of errors with severity, location (layer + coordinates/component)
- **Netlist issues**: any inconsistencies found
- **BOM discrepancies**: any mismatch between schematic and `docs/bom.md`
- **Summary**: overall design health, recommended actions

If MCP tools are unavailable, fall back to reading the `.kicad_sch` / `.kicad_pcb` files directly and report what can be determined from inspection.
