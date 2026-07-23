---
name: kicad-bom
description: Generate/validate BOM from the KiCad schematic and cross-check against docs/bom.md.
triggers:
  - user
  - model
subagent: true
agent: kicad-inspector
---

Generate a BOM from the current KiCad schematic and cross-check it against the documented BOM in `docs/bom.md`. This is a read-only operation — no files are modified.

## Steps

1. **Generate BOM** from the schematic using `kicad` MCP server tools or `kicad-cli sch export python-bom` (or equivalent). If MCP/CLI unavailable, parse the `.kicad_sch` file directly to extract component list (refdes, value, footprint, datasheet).
2. **Read `docs/bom.md`** to get the documented BOM.
3. **Cross-check**:
   - Components in the schematic but not in `docs/bom.md` (undocumented parts).
   - Components in `docs/bom.md` but not in the schematic (documented but not placed).
   - Mismatches in value, footprint, or part number between schematic and docs.
4. **Report**:
   - Schematic BOM summary (total components, by type).
   - Discrepancies table (refdes, schematic value, documented value, issue).
   - Recommended actions (add to docs, update schematic, etc.).

If discrepancies are found, do NOT fix them — report back and let the user decide. BOM/doc updates may require the `/kicad-schematic-edit` skill or manual doc editing.
