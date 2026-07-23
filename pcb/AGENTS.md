# KiCad AI Interaction Rules

These rules apply when working in the `pcb/` directory. They govern how the AI agent uses the `kicad-mcp-pro` MCP server (profile `agent_full`, mode `write`) to interact with KiCad design files. The user owns all design decisions; the agent implements, verifies, and explains.

## Setup (verified 2026-07-22)

- **MCP server**: `kicad-mcp-pro` v3.28.0 via uvx, configured in `~/.codeium/windsurf/mcp_config.json` as the `kicad` server. Auto-imported by Devin at session start.
- **KiCad CLI**: `C:\Users\dengle\AppData\Local\Programs\KiCad\10.0\bin\kicad-cli.exe` (passed via `KICAD_MCP_KICAD_CLI` env var — without this, export tools are unavailable).
- **KiCad project**: `pcb/phone/phone.kicad_pro`.
- **Profile**: `agent_full` (full tool surface across schematic + PCB + manufacturing).
- **Mode**: `write` (agent can modify `.kicad_sch` / `.kicad_pcb`).
- **IDE extension**: KiCad Studio Kit v1.9.5 (`oaslananka.kicadstudiokit`) — provides schematic/PCB viewers, DRC/ERC integration, BOM/netlist/export commands, and MCP dashboard in Windsurf.

## Core Principles

1. **Clean tree before changes.** Always start KiCad file changes from a clean git working tree. If the tree is dirty, tell the user and ask whether to commit/stash first. Never layer AI edits on top of uncommitted user work.

2. **Read before write.** Inspect the current state of the target file(s) before any modification. Never blind-write.

3. **Consequential changes need confirmation — unless explicitly autonomous.** Changes to nets, net names, reference designators, symbols, footprints, pin assignments, power rails, or already-reviewed sections are "consequential."
   - **Default:** describe the change and wait for approval.
   - **Autonomous mode:** when the user asks for a larger project without intervention, create a git checkpoint (see `/kicad-checkpoint` skill) before each consequential change so work is never lost. Use feature branches or tagged commits as rollback points. Report what you did and the checkpoint ref so the user can review or revert.

4. **No silent renames.** Renaming a net, refdes, symbol, or footprint propagates across the whole design. Always flag and confirm renames — never do them as a side effect of another edit.

5. **Scope discipline.** Only modify what's in scope for the current task. No drive-by refactors or "improvements" to unrelated parts of the schematic/PCB.

6. **Validate after every edit.** Run ERC (schematic) or DRC (PCB) after any modification and report results. Don't claim success without validation. If validation tools are unavailable, say so rather than assert correctness.

7. **Git hygiene.** KiCad files are s-expression text (diffable). Never commit KiCad changes without explicit user approval. Never force-push. Suggest a commit before editing if the tree is clean but the last commit is stale.

8. **Library integrity.** Don't break symbol/footprint library links, delete library symbols, or modify shared library files without explicit approval.

9. **Protected sections.** The power section is schemed + reviewed (project-log 2026-07-22). Treat it as locked — any change requires explicit approval and a documented rationale in `docs/project-log.md`. Other sections become protected as they are reviewed (document in project-log).

10. **Documentation sync.** If a schematic/PCB change affects BOM, net names, component selection, or architecture, update the relevant docs (`docs/bom.md`, `docs/requirements.md`, `docs/project-log.md`) in the same session, per the root `AGENTS.md` doc-maintain rule.

11. **No autonomous manufacturing outputs.** Don't generate Gerbers, drill files, or fab-ready BOM without an explicit user request. Manufacturing handoff is user-initiated.

12. **Report every write.** After any write-mode tool call, report exactly what changed (file, components/nets affected) so the user can verify against the diff.

13. **Stop on uncertainty.** If a tool's effect is unclear or a change is ambiguous, stop and ask rather than guess.

## Subagent Usage

Subagents are useful for parallelizing inspection, validation, and focused implementation work on KiCad files. Two custom profiles are defined in `.devin/agents/`:

- **`kicad-inspector`** — read-only (DRC/ERC, inspection, BOM extraction). Runs on GLM-5.2 High (free tier, 200k context). Use for validation and research tasks. Safe to fan out multiple in parallel (e.g., one runs ERC, another checks netlist against BOM).
- **`kicad-author`** — write-capable (schematic/PCB edits). Runs on GLM-5.2 High. Governed by the rules above. `max-nesting: 2` so it can spawn an inspector subagent to validate its own work after editing.

### Subagent rules

- **Prefer `kicad-inspector` for read-only work** — it's free and safe. Don't burn the parent model on tasks an inspector subagent can do.
- **Subagents must plan before implementing.** A `kicad-author` subagent formulates a plan (what to change, why, expected impact, is it consequential?) and reviews it against these rules before making any edit. If the change is consequential and the subagent was NOT explicitly told to work autonomously, it reports the plan back to the parent agent and stops — the parent confirms with the user.
- **One author at a time per file.** Never run two `kicad-author` subagents in parallel on the same file — KiCad files are single-document; concurrent writes corrupt them. Different files are OK.
- **Authors validate their own work.** A `kicad-author` subagent spawns a `kicad-inspector` child (depth 2) to run DRC/ERC after its edits, and reports both the change and the validation result.
- **Git safety for autonomous work.** When working autonomously, a `kicad-author` subagent creates a checkpoint commit before editing (via `/kicad-checkpoint` or direct git commands). The checkpoint ref is included in the report so the user can revert.
- **No nesting beyond depth 2.** Cost scales with nesting. The chain is: root agent → kicad-author (depth 1) → kicad-inspector (depth 2, terminal).
- **Background vs foreground:** use background subagents for independent inspection tasks (parallel ERC + BOM check). Use foreground for author tasks where you want to approve tool calls.
- **Subagents don't ask the user questions** (`ask_user_question` is withheld from subagents). If a subagent hits a decision point, it reports back and the parent agent asks the user.

## Skills

The following skills in `.devin/skills/` encode KiCad workflows. All are invocable by both the user (`/skill-name`) and the model (when relevant):

- `/kicad-checkpoint` — commit current state as a labeled checkpoint before risky/autonomous work. Used by the autonomous-mode workflow in rule 3.
- `/kicad-review` — run DRC/ERC + inspect a design, report findings. Read-only.
- `/kicad-schematic-edit` — governed write workflow for `.kicad_sch` files (plan → checkpoint if autonomous → edit → validate → report).
- `/kicad-pcb-edit` — governed write workflow for `.kicad_pcb` files (same flow).
- `/kicad-bom` — generate/validate BOM and cross-check against `docs/bom.md`.

## Model Note

The `kicad-inspector` and `kicad-author` subagent profiles pin `model: glm-5-2-high` (GLM-5.2 High, free tier, 200k context). If this model flag name is incorrect, verify via `/model` in a Devin session and update `.devin/agents/kicad-inspector/AGENT.md` and `.devin/agents/kicad-author/AGENT.md`.
