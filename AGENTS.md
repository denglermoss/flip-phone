# AGENTS.md — Project Instructions for AI Assistants

This file provides guidance to any LLM/agent (Devin, Cascade, Claude, etc.) working on this project. It must be read and followed at the start of every session.

## Project Summary

A custom cell phone built from scratch: STM32H743ZI MCU + SIMCom SIM7600 LTE module + Zephyr RTOS + custom PCB. Target: make/receive real VoLTE calls on a US LTE network (T-Mobile/Mint). Long-term vision: the phone is the hub of a personal ecosystem of devices connected via USB. See `docs/ref/problem-definition.md` for full context.

## Documentation Maintenance (MANDATORY)

This project is documentation-driven. The docs are the source of truth for decisions, requirements, and constraints. **Keeping them accurate and consistent is a first-class task, not an afterthought.**

### Document Structure

Docs are organized into folders by lifecycle stage. Each doc has YAML frontmatter (`status: active|reference|archived`, `updated: YYYY-MM-DD`) for metadata/navigation.

```
docs/
  work/         — Active planning & working docs (frequently edited, current work)
  ref/          — Long-term reference & documentation (locked decisions, specs, history)
  datasheets/   — Vendor datasheets (PDFs, gitignored — only README.md tracked)
  archive/      — Completed/superseded plans and prompts (historical reference only)
```

### The Documents

| Doc | Status | Purpose |
|-----|--------|---------|
| `docs/ref/problem-definition.md` | reference | The problem, architecture, MVP, risks, success criteria |
| `docs/ref/requirements.md` | reference | Functional & non-functional requirements, resolved/open questions |
| `docs/ref/constraints.md` | reference | Technical, budget, regulatory, timeline constraints |
| `docs/ref/research-notes.md` | reference | Research findings, component analysis, open research questions |
| `docs/ref/feature-wishlist.md` | reference | Features rated 1-10, ecosystem implications, component selection guide |
| `docs/ref/project-log.md` | reference | Decision log (dated), phase breakdown, progress tracking |
| `docs/ref/bom.md` | reference | Bill of Materials — component list with prices, links, cost estimates |
| `docs/work/block-diagram.md` | active | Design intent, topology, and rationale. Pin-level detail is planning reference (KiCad schematic is the pin-level source of truth). |
| `docs/work/mcu-pin-assignment.md` | active | STM32H743ZI full pin map (73 pins assigned, ~60 spare) |
| `docs/work/task-tracker.md` | active | Comprehensive plan to assembled PCB (Phase 3-5: schematic → layout → DIY assembly) |
| `docs/work/schematic-completion-plan.md` | active | Per-sheet review tracker for Phase 3 schematic fixes |
| `docs/work/ui-design.md` | active | UI screen map, input model, visual style (80s sci-fi HUD) |
| `docs/datasheets/README.md` | reference | Index of vendor datasheets (PDFs are gitignored) |
| `docs/archive/` | archived | Completed/superseded working plans + all 5 revisit prompts |
| `README.md` | — | Project overview, documentation index, status |

### Source of Truth Assignments

Each type of information has **one source of truth**. Other docs link to it — they do not duplicate it.

| Information type | Source of truth | Other docs should... |
|-----------------|-----------------|---------------------|
| Decision rationale + history | `docs/ref/project-log.md` | Link to the dated entry, don't restate |
| Architecture, MVP, risks | `docs/ref/problem-definition.md` | Link, don't restate |
| Functional/non-functional requirements | `docs/ref/requirements.md` | Link, don't restate |
| Technical constraints | `docs/ref/constraints.md` | Link, don't restate |
| Component selection + pricing | `docs/ref/bom.md` | Link, don't restate |
| Research findings | `docs/ref/research-notes.md` | Link, don't restate |
| Feature ratings + ecosystem implications | `docs/ref/feature-wishlist.md` | Link, don't restate |
| Pin assignments | `docs/work/mcu-pin-assignment.md` | Link, don't restate |
| Design intent & topology rationale | `docs/work/block-diagram.md` | Link, don't restate |
| Pin-level wiring (actual) | KiCad schematic (`pcb/phone/phone.kicad_sch`) | Extract via kicad-inspector subagent |
| Current plan/status | `docs/work/task-tracker.md` | Link, don't restate |
| Schematic fixes | `docs/work/schematic-completion-plan.md` | Link, don't restate |
| UI design | `docs/work/ui-design.md` | Link, don't restate |

### Rules

1. **Always read the relevant docs before making changes or recommendations.** Do not assume the state of the project from memory or context alone — verify against the docs.

2. **Single source of truth — no duplication.** Each fact lives in ONE doc (see Source of Truth Assignments above). Other docs may link to it but must not restate it. When a decision is made:
   - Add a dated entry to `docs/ref/project-log.md` (Decision Log section) with rationale and tradeoffs — this is the canonical record.
   - Update the **specific source-of-truth doc** that the decision affects (e.g., constraints.md for a new constraint, bom.md for a part change, requirements.md for a resolved question).
   - Do NOT update every doc that mentions the topic — update only the source of truth + project-log.md. Other docs reference the source.
   - Update `README.md` only if the project overview or phase status changes (brief summary + link, not full details).

3. **When a new issue, risk, or factor is discovered, document it** in the appropriate source-of-truth doc + project-log.md — do not leave it only in chat.

4. **Keep docs consistent.** If a decision is recorded in project-log.md, ensure the relevant source-of-truth doc reflects it. Stale "open questions" that have been resolved are a known failure mode — check for them.

5. **Superseded decisions**: Do not delete old decisions from project-log.md. Strike them through (`~~text~~`) and mark **SUPERSEDED <date>** with a pointer to the replacing decision. History matters.

6. **Reference docs by root-relative path** (e.g., `docs/ref/requirements.md`, not absolute paths) so citations are greppable and work across environments.

7. **When reviewing or auditing the project**, check for:
   - Stale "open questions" that are actually resolved
   - Decisions in project-log.md not reflected in the relevant source-of-truth doc
   - Conflicts between docs (e.g., a constraint that contradicts a decision)
   - Duplicated content that should be a link instead (violation of Rule 2)
   - Missing factors (hardware, firmware, regulatory, power) for the current architecture

8. **AGENTS.md "Key Decisions" section** is a brief index (1-2 lines per decision) pointing to project-log.md entries. It is NOT a duplicate of the full rationale — keep it concise.

## Key Decisions (Quick Reference — full rationale in `docs/ref/project-log.md`)

| Decision | Value | Locked | Source |
|----------|-------|--------|--------|
| MCU | STM32H743ZI (LQFP-144, 480MHz Cortex-M7) | 2026-06-28 | project-log.md |
| Cellular module | SIM7600NA-H (B71, MPCIe primary, LGA fallback) | 2026-06-28 | project-log.md Modem Revisit |
| RTOS | Zephyr | 2026-06-28 | project-log.md |
| Audio codec | ALC5651-CG (dual I2S/PCM, MCU not in voice path) | 2026-07-19 | project-log.md Codec Swap |
| Display | ST7789V SPI TFT 2.0" (outer display dropped 2026-08-16) | 2026-07-19 | project-log.md Display Selection |
| Keypad | SMD tactile switches, 5×4 matrix | 2026-06-28 | project-log.md Keypad Selection |
| Form factor | Candybar / single-board (flip deferred to v2) | 2026-08-16 | project-log.md Form Factor Pivot |
| Camera | OV5640 5MP AF, 8-bit DVP via DCMI (20-pin FPC ZIF) | 2026-08-17 | project-log.md Camera Module Selection |
| Power | TPS63021 buck-boost + MCP73831 charger + MAX17048 gauge | 2026-07-19 | project-log.md, `docs/work/block-diagram.md` |
| USB tethering | SIM7600 USB HS direct (no ULPI) | 2026-06-28 | project-log.md USB HS/ULPI Revisit |
| Schematic | KiCad, flat sheet + global labels | 2026-07-22 | project-log.md Schematic Approach |
| Network | LTE with VoLTE (T-Mobile/Mint) | 2026-06-28 | `docs/ref/constraints.md` |
| Component principle | No feature rated 5+ may be blocked by hardware | 2026-06-28 | `docs/ref/feature-wishlist.md` |

**All revisit items resolved.** See `docs/archive/revisit-prompts/README.md` for the archive index.

## Workflow Preferences

- **Commit messages**: When using a temporary file for the commit message (e.g., `.git/COMMIT_MSG.txt`), always delete it after committing. Do not leave temporary files in the `.git/` directory.
- **Roles**: The user is the project lead and engineer. The agent is the assistant/intern. The user owns all decisions, architecture, and direction. The agent's job is to research, verify, implement, and explain — not to steer the project. Present findings and options with tradeoffs; the user decides. Reserve autonomous action for mechanical/verification tasks (building, installing, checking stock) where there's a clear right answer. For anything involving judgment or tradeoffs, ask first.
- **KiCad work division (updated 2026-08-16)**: The **user handles all KiCad work** — schematic capture, PCB layout, footprint assignment, library edits. The agent acts as **reviewer and guide**: reviewing schematics, running ERC/DRC via the kicad-inspector subagent, checking against docs, flagging issues, and advising on design decisions. The agent does **not** directly edit `.kicad_sch` or `.kicad_pcb` files unless the user explicitly asks. The kicad-author subagent and kicad-schematic-edit / kicad-pcb-edit skills remain available but are only invoked on explicit user request. The kicad-inspector subagent (read-only DRC/ERC, BOM, netlist) remains in active use for review. See `docs/ref/project-log.md` 2026-08-16 Workflow Role Change.
- **Learning is a project goal**: The user wants to understand how things work, not just get answers. Explain the concepts and tradeoffs behind decisions as you go — don't just hand over results. The project docs say "the steep learning curve is a feature, not a bug," and that applies to the collaborative process too.

## Reference Documentation & PDF MCP Server (set up 2026-06-30)

Vendor datasheets, reference manuals, and hardware design docs are stored locally in `docs/datasheets/` (gitignored — only `docs/datasheets/README.md` is tracked, which indexes every file with its exact part number and download URL). When a datasheet is cited in the project docs (e.g., "Hardware Design Manual V1.03 §3.6"), the local PDF is the source of truth.

**PDF MCP server** (`mcp-pdf`, rsp2k/mcp-pdf on PyPI) is configured in the Windsurf MCP config (`~/.codeium/windsurf/mcp_config.json`) and auto-imported by Devin at session start. It provides:
- `textextraction__extract_text` — extract text from any PDF (by page or full doc), via PyMuPDF with auto-fallback to pdfplumber/pypdf
- `tableextraction__extract_tables` — extract tables (electrical characteristics, pin tables, timing)
- `documentanalysis__get_document_structure` — TOC/outline for navigation
- Image/SVG extraction, OCR, and more (14 tool mixins total)

**How to use**: When verifying a spec, pin voltage, register address, or timing parameter, call the MCP tools against the local PDFs in `docs/datasheets/` rather than relying on web search snippets. The MCP server handles encrypted vendor PDFs (e.g., SIMCom manuals) that `webfetch` cannot parse. Example: `textextraction__extract_text` with `pdf_path` pointing to the SIM7600 manual, `pages="35"`, `inline=true` returns the PCM reference design page in ~0.06s.

**Tooling**: `uv`/`uvx` (Astral, installed via winget) manages the isolated Python environment for `mcp-pdf` — no manual venv maintenance. The MCP config uses the full path to `uvx.exe` (`C:\Users\dengle\AppData\Local\Microsoft\WinGet\Links\uvx.exe`).

**Mandatory — add missing datasheets before citing them**: If a datasheet you need to reference is not already in `docs/datasheets/`, you MUST find and download it first (vendor website, LCSC/Mouser/DigiKey product page, etc.) and add a row to `docs/datasheets/README.md`'s PDF index. Do not cite specs from memory, web search snippets, or session context alone — datasheet specs vary by revision and package variant, and citing from memory risks pinout/voltage/package errors that are expensive to catch after PCB fab. If a datasheet genuinely cannot be found, say so in `docs/ref/project-log.md` and flag the spec as unverified. See `docs/datasheets/README.md` "Mandatory: add missing datasheets before citing them" for the full workflow.

## Zephyr Development Environment (set up 2026-06-29)

The Zephyr dev environment is installed on Windows (native, not WSL — WSL flashing is unsupported per Zephyr docs). See `docs/ref/project-log.md` 2026-06-29 entry for full details.

- **Workspace**: `C:\Users\dengle\zephyrproject` (external to the phone repo — multi-GB tree, not version-controlled here)
- **Python venv**: `C:\Users\dengle\zephyrproject\.venv` (Python 3.12, contains west 1.5.0 + Zephyr Python deps)
- **Zephyr SDK**: `C:\Users\dengle\zephyr-sdk-1.0.1` (ARM toolchain `arm-zephyr-eabi-gcc` 14.3.0)
- **Board target**: `nucleo_h753zi` (the prototyping board — NUCLEO-H753ZI, substitute for the obsolete NUCLEO-H743ZI; STM32H753 = H743 + crypto, identical for this project)
- **Activation**: Dot-source `scripts/activate-zephyr.ps1` in a new PowerShell terminal to refresh PATH and activate the venv
- **Build a sample**: `cd ~/zephyrproject/zephyr; west build -p always -b nucleo_h753zi samples/basic/blinky`
- **Build the phone firmware**: `cd C:\Users\dengle\Documents\personal_projects\phone; . .\scripts\activate-zephyr.ps1; $env:ZEPHYR_BASE = "$env:HOMEPATH\zephyrproject\zephyr"; west build -b nucleo_h753zi firmware`
- **Known gap**: Zephyr SDK Windows host tools (QEMU, OpenOCD) are not available. Install OpenOCD separately (xpack-openocd or winget) before flashing via ST-Link. Building works now; flashing needs this extra step.
- **Firmware app**: `firmware/` directory in the phone repo — Zephyr application with `CMakeLists.txt` (build manifest), `prj.conf` (Kconfig features), `app.overlay` (devicetree hardware config), `src/main.c` (application code). Skeleton created 2026-07-05, builds successfully. See `docs/ref/project-log.md` 2026-07-05 entry.
- **Path constraint**: The project directory must NOT contain spaces — Zephyr's devicetree preprocessor splits paths at spaces and fails. Directory renamed from `Personal Projects` to `personal_projects` on 2026-07-05 for this reason.

## KiCad Studio Kit + kicad-mcp-pro MCP Server (set up 2026-07-22)

KiCad Studio Kit (`oaslananka.kicadstudiokit` v1.9.5) is installed as a Devin extension — provides schematic/PCB viewers, DRC/ERC integration, BOM/netlist/export commands, and an MCP dashboard in Windsurf. The companion MCP server `kicad-mcp-pro` (v3.28.0) exposes KiCad tools (inspection, DRC/ERC, BOM, exports, schematic/PCB editing) to AI clients.

- **MCP config**: `~/.codeium/windsurf/mcp_config.json` → `kicad` server entry (auto-imported by Devin at session start)
- **KiCad CLI**: `C:\Users\dengle\AppData\Local\Programs\KiCad\10.0\bin\kicad-cli.exe` (via `KICAD_MCP_KICAD_CLI` env var)
- **Profile**: `agent_full` (full tool surface) · **Mode**: `write` (agent can modify KiCad files)
- **KiCad project**: `pcb/phone/phone.kicad_pro`

**KiCad AI interaction rules** are in `pcb/AGENTS.md` (loaded lazily when working in `pcb/`). They govern write-mode access: clean tree before changes, read-before-write, consequential-change confirmation (with autonomous-mode git checkpoints), no silent renames, validate-after-edit, protected sections (power section locked), documentation sync, and no autonomous manufacturing outputs.

**Custom subagent profiles** (`.devin/agents/`):
- `kicad-inspector` — read-only inspection (DRC/ERC, BOM, netlist). Model: GLM-5.2 High (free, 200k context). Safe to parallelize.
- `kicad-author` — write-capable schematic/PCB edits. Model: GLM-5.2 High. `max-nesting: 2` (can spawn a kicad-inspector child to validate its own work). Plans before implementing; stops and reports back for consequential changes unless explicitly autonomous.

**Skills** (`.devin/skills/`): `/kicad-checkpoint` (git rollback point), `/kicad-review` (DRC/ERC + inspection), `/kicad-schematic-edit` (governed .kicad_sch writes), `/kicad-pcb-edit` (governed .kicad_pcb writes), `/kicad-bom` (BOM generation + cross-check against `docs/ref/bom.md`). All invocable by user (`/name`) and model (when relevant).

See `docs/ref/project-log.md` 2026-07-22 KiCad Studio Kit + kicad-mcp-pro Setup entry for full rationale.
