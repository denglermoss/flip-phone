# KiCad MCP-First Rule

When working on KiCad files (`.kicad_sch`, `.kicad_pcb`, `.kicad_pro`, `.kicad_sch` sheets, project files), all agents MUST prefer the **KiCad MCP server** (`kicad`) for inspection, validation, netlist/BOM extraction, DRC/ERC, and any design queries.

## Why

- The MCP server parses the KiCad data model directly and returns structured, reliable results (nets, pins, references, DRC violations, BOM rows).
- **Coordinate-based wiring checks are unreliable.** Reading `(at x y ...)` tuples from the sexp file and inferring whether two pins are connected by geometric proximity produces inconsistent, often wrong results — KiCad's connection model is graph-based (labels, wires, junctions, hierarchical pins), not coordinate-based. Treat coordinate inference as a last resort only.
- Text-dump grep over `.kicad_sch`/`.kicad_pcb` is acceptable for locating a symbol/footprint/refdes by name, but **not** for verifying connectivity.

## How

1. **List tools first**: Before calling any `kicad_*` tool, run `mcp_list_tools` on the `kicad` server to discover the current tool set and schemas. Never guess tool names or arguments.
2. **Use MCP for design queries**: netlist extraction, ERC/DRC, BOM, pin/net lookups, schematic structure, project state — all go through the MCP server.
3. **Use MCP for validation**: After any schematic/PCB edit, validate via the MCP server's ERC/DRC tools rather than re-reading raw sexp coordinates.
4. **Coordinate inference is a last resort**: Only fall back to reading raw `(at ...)` coordinates from the sexp file when (a) the MCP server is unavailable or failing, AND (b) no other tool can answer the question. If you do fall back, state explicitly that you are using coordinate inference and that the result may be unreliable, then recommend re-verifying via MCP once it's available.
5. **Read-only inspection can be parallelized**: Multiple `kicad-inspector` subagents (or direct MCP calls) can run in parallel for independent queries. Write-capable `kicad-author` work must stay serialized per file.

## When the MCP server is unavailable

If `mcp_list_tools` for `kicad` returns nothing or the server errors:
- Note the failure in your response.
- Use `grep`/`read` to locate symbols/refdes by name (string search), not to verify wiring.
- Flag any connectivity claim made without MCP as **unverified** and recommend re-checking once MCP is restored.
