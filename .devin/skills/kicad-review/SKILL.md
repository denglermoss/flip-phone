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
4. **BOM cross-check** — if a BOM exists in `docs/ref/bom.md`, verify the schematic components match the documented parts.

## Pin-level wiring review — use netlists, NOT coordinates

When reviewing a specific component's pin wiring (e.g., "is U10 wired correctly?"):

- **Export the netlist** via `kicad-cli sch export netlist` (or the `kicad` MCP server's netlist tools) and use it to get the authoritative pin → net mapping for every pin of the target component.
- **Do NOT parse `.kicad_sch` coordinates** to infer which wire connects to which pin. Coordinate-based analysis is fragile (depends on correct symbol pin-offset math), verbose, and error-prone. The netlist is the source of truth for connectivity.
- Report findings as a pin-by-pin table: pin number, pin name, net name (from netlist), expected net (from datasheet), pass/fail.
- If netlist export is unavailable, say so explicitly rather than falling back to coordinate guessing.

## Report format

- **ERC results**: pass/fail, list of errors with severity, location (sheet + component/refdes)
- **DRC results**: pass/fail, list of errors with severity, location (layer + coordinates/component)
- **Netlist issues**: any inconsistencies found
- **BOM discrepancies**: any mismatch between schematic and `docs/ref/bom.md`
- **Summary**: overall design health, recommended actions

If MCP tools are unavailable, fall back to reading the `.kicad_sch` / `.kicad_pcb` files directly and report what can be determined from inspection.
