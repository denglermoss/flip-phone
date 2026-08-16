---
name: kicad-schematic-edit
description: "DORMANT (2026-08-16 role change): Governed write workflow for .kicad_sch files. Invoke only on explicit user request — user now drives all KiCad edits, agent reviews."
status: dormant
triggers:
  - user
subagent: true
agent: kicad-author
---

> **DORMANT as of 2026-08-16** — Per the Workflow Role Change decision (project-log.md 2026-08-16), the user handles all KiCad work and the agent acts as reviewer/guide. This skill remains available but should only be invoked when the user **explicitly** asks the agent to make a KiCad edit. Do not auto-invoke. The active review path is `/kicad-review` (read-only, via kicad-inspector subagent).

Implement a change to a `.kicad_sch` file in the current KiCad project, following the governed workflow in `pcb/AGENTS.md`.

## Workflow

1. **Read** the target `.kicad_sch` file(s) and understand the current state.
2. **Formulate a plan**: what to change, why, which components/nets are affected, expected impact.
3. **Classify the change**:
   - **Consequential** (nets, net names, refdes, symbols, footprints, pin assignments, power rails, protected sections): requires confirmation unless working autonomously.
   - **Non-consequential** (annotations, labels, comments, cosmetic): proceed directly.
4. **If consequential and NOT autonomous**: report the plan back and wait for approval. Do not implement yet.
5. **If autonomous**: run `/kicad-checkpoint` to create a rollback point.
6. **Implement** the change using `kicad` MCP server tools (preferred) or direct file edits.
7. **Validate**: run ERC on the modified schematic (via MCP or `kicad-cli sch erc`).
8. **Report**: the plan, what changed (file, components/nets affected), ERC result, and checkpoint ref if autonomous.

## Rules (from pcb/AGENTS.md)

- Start from a clean git working tree.
- No silent renames — flag and confirm any net/refdes/symbol/footprint renames.
- Scope discipline — only modify what's in scope for the current task.
- Protected sections (power section as of 2026-07-22) require explicit approval.
- Never commit without user approval. Never force-push.
- Stop on uncertainty — if a tool's effect is unclear, report back rather than guessing.
