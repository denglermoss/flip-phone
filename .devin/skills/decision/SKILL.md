---
name: decision
description: Record a project decision with full doc-maintain workflow — project-log entry, source-of-truth doc updates, stale-reference scan, README/AGENTS sync. Codifies the rules in AGENTS.md and .devin/rules/doc-maintain.md.
triggers:
  - user
  - model
allowed-tools:
  - read
  - edit
  - write
  - grep
  - glob
  - ask_user_question
---

Record a project decision following the documentation-driven workflow. This skill ensures every decision is captured consistently across the single-source-of-truth docs without duplication.

## When to use

- The user states a decision ("let's go with X", "drop Y", "change Z to W").
- A question raised in `docs/ref/requirements.md` or `docs/ref/research-notes.md` is resolved.
- A new constraint, risk, or factor is discovered.
- The user invokes `/decision` explicitly.

Do NOT use this skill for trivial clarifications that don't change the project state.

## Workflow

### 1. Gather the decision

If the decision and rationale aren't fully stated, ask the user (via `ask_user_question`) for:
- **What** is being decided (the new state).
- **Why** — the rationale and tradeoffs considered.
- **What it supersedes** (if replacing a prior decision — identify the prior decision by date/label).
- **What is lost / what changes** (consequences, freed/added pins, BOM deltas, scope changes).

### 2. Identify affected source-of-truth docs

Consult the Source of Truth Assignments table in `AGENTS.md`. Identify which doc(s) the decision affects:

| If the decision changes... | Update this doc |
|---------------------------|-----------------|
| Decision rationale / history | `docs/ref/project-log.md` (always — this is the canonical record) |
| Architecture / MVP / risks | `docs/ref/problem-definition.md` |
| Functional / non-functional requirements | `docs/ref/requirements.md` |
| Technical constraints | `docs/ref/constraints.md` |
| Component selection / pricing | `docs/ref/bom.md` |
| Research findings | `docs/ref/research-notes.md` |
| Feature ratings / ecosystem implications | `docs/ref/feature-wishlist.md` |
| Pin assignments | `docs/work/mcu-pin-assignment.md` |
| Block wiring spec | `docs/work/block-diagram.md` |
| Current plan / status | `docs/work/task-tracker.md` |
| Schematic fixes | `docs/work/schematic-completion-plan.md` |
| UI design | `docs/work/ui-design.md` |

Report the list of affected docs to the user before editing (transparency — they may know of others).

### 3. Write the project-log entry

Add a dated entry to the **Decision Log** section at the top of `docs/ref/project-log.md`:

```markdown
### YYYY-MM-DD: <Short decision title>

- **Decision**: <what was decided>
  - *Rationale*: <why, with tradeoffs>
  - *Consequences*: <what changes — pins freed/added, BOM deltas, scope, etc.>
  - *What is lost*: <if anything>
- **Docs updated**: This entry, <list of source-of-truth docs touched>
```

If this decision **supersedes** a prior one:
- Do NOT delete the old entry. Strike it through (`~~old text~~`) and add `**SUPERSEDED YYYY-MM-DD**: <reason + pointer to new decision>`.
- History must remain traceable.

### 4. Update each affected source-of-truth doc

For each doc identified in step 2, make the **minimal** change that reflects the decision:
- Update only the affected section/entry — do not restate the full rationale (that lives in project-log.md).
- If the doc has YAML frontmatter, bump the `updated:` date.
- If a resolved open question existed in `requirements.md` or `research-notes.md`, move it from Open → Resolved with a pointer to the project-log entry.

**Do NOT update every doc that mentions the topic.** Update only the source of truth + project-log.md. Other docs reference the source via links.

### 5. Update README.md / AGENTS.md only if needed

- `README.md`: only if the project overview or phase status changed (brief summary + link, not full details).
- `AGENTS.md` Key Decisions table: only if a locked decision value changed (MCU, modem, codec, display, form factor, power topology, etc.). Keep it to 1-2 lines pointing to project-log.md.

### 6. Scan for stale references

If the decision supersedes or drops a concept (e.g., "drop the outer display", "flip → candybar"), grep all docs for the superseded term(s):

```
grep -ril "<superseded term>" docs/ README.md AGENTS.md
```

For each hit, determine:
- **Stale** (describes the old state as if still active) → update or strike through.
- **Historical** (project-log entry, archived doc, or explicitly struck) → leave as-is.
- **Link-only reference** (points to the source-of-truth doc) → leave as-is.

Report stale hits to the user. Do not auto-fix without confirmation unless the fix is purely mechanical (e.g., striking a checkbox that's clearly moot).

### 7. Report

Summarize to the user:
- The project-log entry (date + title).
- Which source-of-truth docs were updated (list).
- Which stale references were found and which were fixed vs. flagged.
- Whether README/AGENTS were updated.
- Any open questions that should now be marked resolved but weren't in scope of this decision.

## Rules (from AGENTS.md + doc-maintain.md)

- Single source of truth — no duplication. Each fact lives in ONE doc.
- Superseded decisions are struck through, never deleted.
- Reference docs by root-relative path (e.g., `docs/ref/requirements.md`).
- Update only the source of truth + project-log.md for a given fact. Other docs link.
- If a "open question" in any doc has been resolved by this decision, mark it resolved — don't leave it stale.
