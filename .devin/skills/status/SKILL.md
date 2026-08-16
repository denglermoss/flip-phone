---
name: status
description: Print a "you are here" session-orientation summary — current phase, what's done, what's next, open gates, recent decisions. Reduces stale-context risk at session start.
triggers:
  - user
  - model
allowed-tools:
  - read
  - grep
  - glob
---

Print a concise orientation summary so the agent (and user) start every session grounded in the current project state, not session memory. Implements the "read the relevant docs before acting" rule from `AGENTS.md` in a structured, low-cost way.

## When to use

- At the start of a session, before any task work.
- When the user asks "where are we?" / "what's the status?" / `/status`.
- When resuming a session after a gap and context may be stale.
- Before starting a new phase or major task, to confirm gates are met.

## Workflow

### 1. Read the orientation docs

Read these in order (batch the reads):

1. `AGENTS.md` — Key Decisions table (quick reference of locked decisions).
2. `docs/work/task-tracker.md` — Current State table + Open Questions section + the current phase's task list.
3. `docs/ref/project-log.md` — the 3 most recent Decision Log entries (top of file).
4. `docs/work/schematic-completion-plan.md` — Current State table (if Phase 3 is active).

### 2. Print the summary

Format:

```
## Project Status — <today's date>

**Phase**: <current phase name + status, e.g., "Phase 3: Schematic — IN PROGRESS">
**Form factor**: <locked form factor, e.g., "Candybar / single-board (locked 2026-08-16)">

### Done
- <1-3 bullet points of completed milestones>

### In progress / next
- <current task or next uncheckboxed item in the current phase>

### Open gates (must resolve before proceeding)
- <list any unresolved O-questions from task-tracker that gate the next phase>
- If none: "No blocking gates — clear to proceed."

### Recent decisions (last 3)
- YYYY-MM-DD: <title> — <one-line summary>
- YYYY-MM-DD: <title> — <one-line summary>
- YYYY-MM-DD: <title> — <one-line summary>

### Active workflow notes
- <e.g., "User drives KiCad; agent reviews (2026-08-16 role change)">
- <any dormant skills or special constraints in effect>
```

### 3. Flag inconsistencies

While reading, if you notice:
- A "resolved" open question still listed as open.
- A decision in project-log.md not reflected in the relevant source-of-truth doc.
- A stale reference to a superseded concept.
- A phase status in task-tracker that contradicts the schematic-completion-plan or project-log.

...flag it at the end of the summary under `### Flags` with the specific file + line. Do not auto-fix — just report so the user can decide.

## Rules

- This skill is **read-only** — it never modifies files.
- Keep the summary concise — it's orientation, not a full report. Link to docs for detail.
- If a doc read fails or is missing, note it rather than guessing the state.
- Do not rely on session context or memory — always re-read the docs.
