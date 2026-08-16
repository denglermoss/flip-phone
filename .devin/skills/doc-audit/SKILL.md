---
name: doc-audit
description: Scan all project docs for stale references to dropped/changed concepts. Catches the "superseded decision still written as active" failure mode after a pivot. Read-only — reports hits, does not auto-fix.
triggers:
  - user
  - model
allowed-tools:
  - read
  - grep
  - glob
---

Scan the project documentation for stale references to concepts that have been dropped, renamed, or superseded. This catches the most common doc-rot failure mode: a decision is made in `project-log.md` but references to the old state linger in other docs as if still active.

## When to use

- After a major pivot or decision (e.g., form factor change, component drop, architecture shift). Run `/doc-audit` with the superseded terms.
- When the user asks "are there any stale references to X?"
- At the end of a phase, as a consistency check before moving to the next.
- When `AGENTS.md` rule 7 (consistency checks) is being applied.

**Do NOT run this immediately after another session has started updating docs for a pivot** — it will produce false positives on docs that are mid-edit. Wait until the pivot session is complete, or scope the audit to docs that session is NOT touching.

## Workflow

### 1. Determine the audit terms

Two modes:

**Explicit** — the user provides the terms:
```
/doc-audit flip hinge daughterboard outer display J8 J9 J10
```

**Inferred** — if no terms given, read `docs/ref/project-log.md` and find the most recent decision marked as superseding another. Extract the superseded concept(s) from the `**SUPERSEDED**` markers and the new decision's "what is lost / what changes" section. Confirm the inferred terms with the user before scanning.

### 2. Grep all docs

Search these locations:
- `docs/` (all subdirs: work/, ref/, datasheets/, archive/)
- `README.md`
- `AGENTS.md`
- `pcb/AGENTS.md`

For each term, run a case-insensitive grep and collect hits with file + line + a few lines of context.

### 3. Classify each hit

For every hit, determine which category it falls into:

| Category | Meaning | Action |
|----------|---------|--------|
| **Stale** | Describes the old state as if still active (e.g., a task-tracker checkbox "Place J8 hinge flex" not yet struck) | Report — recommend fix (strike through or update) |
| **Historical** | A project-log entry, archived doc, or already-struck-through text preserving history | Leave as-is (per supersede-don't-delete rule) |
| **Link-only** | References the source-of-truth doc by path without restating the content | Leave as-is (correct per single-source-of-truth rule) |
| **Ambiguous** | Can't tell from context whether it's stale or intentional | Report — ask user to classify |

### 4. Report

Format the report as a table grouped by term:

```
## Doc Audit — <terms scanned> — <date>

### Stale references (need fixing)
| File | Line | Term | Context | Suggested fix |
|------|------|------|---------|---------------|
| docs/work/task-tracker.md | 245 | J8 | "Place connectors (... J8 hinge flex ...)" | Strike through or remove J8 |

### Historical (OK — leave as-is)
| File | Line | Term | Note |
|------|------|------|------|
| docs/ref/project-log.md | 34 | flip | SUPERSEDED entry — history preserved |

### Ambiguous (needs user classification)
| File | Line | Term | Context |
|------|------|------|---------|

### Link-only (OK)
<summarize count only — e.g., "12 link-only references across 8 docs, all correct">
```

### 5. Offer to fix

After reporting, offer to fix the stale references. **Do not auto-fix** — present the list and let the user choose which to fix. For each fix, follow the doc-maintain rules:
- Strike through rather than delete (if historical context matters).
- Update the source-of-truth doc, not every doc that mentions it.
- Bump `updated:` in YAML frontmatter if the doc has one.

## Rules

- This skill is **read-only** — it reports, it does not modify files. Fixes are a separate step with user approval.
- Always classify hits before reporting — don't dump raw grep output and call it an audit.
- Respect the supersede-don't-delete rule: historical references in `project-log.md` and `docs/archive/` are correct and should not be flagged as stale.
- If a doc is being actively edited in another session, note that and exclude it from the audit (or flag that its hits may be transient).
