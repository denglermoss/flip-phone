---
trigger: always_on
---

# Documentation Maintenance Rule

This project is documentation-driven. The docs in `docs/` are the single source of truth for decisions, requirements, constraints, and research. **Keeping them accurate, current, and internally consistent is a mandatory part of every task — not an optional cleanup step.**

## Document Structure

```
docs/
  work/         — Active planning & working docs (frequently edited)
  ref/          — Long-term reference (locked decisions, specs, history)
  datasheets/   — Vendor datasheets (PDFs gitignored, only README.md tracked)
  archive/      — Completed/superseded plans + revisit prompts (historical)
```

Each doc has YAML frontmatter: `status: active|reference|archived`, `updated: YYYY-MM-DD`.

## Single Source of Truth — No Duplication

**Each type of information has ONE source of truth.** Other docs link to it — they do not restate it. See the Source of Truth Assignments table in `AGENTS.md` for the full mapping.

Key assignments:
- Decision rationale → `docs/ref/project-log.md`
- Architecture/MVP/risks → `docs/ref/problem-definition.md`
- Requirements → `docs/ref/requirements.md`
- Constraints → `docs/ref/constraints.md`
- Component selection + pricing → `docs/ref/bom.md`
- Pin assignments → `docs/work/mcu-pin-assignment.md`
- Block wiring spec → `docs/work/block-diagram.md`
- Current plan/status → `docs/work/task-tracker.md`

## Read Before Acting

Before making any change, recommendation, or answering any question about this project:
1. Read `AGENTS.md` at the project root for project summary, doc structure, and source-of-truth assignments.
2. Read the specific source-of-truth doc(s) relevant to the task.
3. Do not rely on session context or memory alone — verify the current state against the docs.

## Update After Decisions

When a decision is made, a question is resolved, or a new factor/risk is discovered:

1. **Add a dated entry to `docs/ref/project-log.md`** (Decision Log section) with rationale and tradeoffs. This is the canonical record.
2. **Update the specific source-of-truth doc** that the decision affects:
   - New/changed constraint → `docs/ref/constraints.md`
   - Resolved open question → `docs/ref/requirements.md` (move from Open to Resolved)
   - Resolved research question → `docs/ref/research-notes.md` (mark RESOLVED)
   - Part selection change → `docs/ref/bom.md`
   - Architecture/MVP/risk change → `docs/ref/problem-definition.md`
   - Feature rating change → `docs/ref/feature-wishlist.md`
3. **Do NOT update every doc that mentions the topic.** Update only the source of truth + project-log.md. Other docs reference the source via links.
4. **Update `README.md`** only if the project overview or phase status changes (brief summary + link, not full details).

## Consistency Checks

When finishing a task, verify:
- No "open question" in any doc has been resolved elsewhere but not updated.
- No decision in `project-log.md` contradicts a source-of-truth doc.
- No superseded decision is still written as active (strike through + mark **SUPERSEDED**).
- No content is duplicated across docs that should be a link instead (Rule 2 violation).

## Superseded Decisions

Never delete old decisions from `docs/ref/project-log.md`. Strike through the text (`~~old decision~~`) and add `**SUPERSEDED <date>**: <reason and pointer to new decision>`. The decision history must remain traceable.

## Citations

When referencing docs in responses or new doc content, use root-relative paths (e.g., `docs/ref/requirements.md`), not absolute paths, so references are greppable and work across environments.
