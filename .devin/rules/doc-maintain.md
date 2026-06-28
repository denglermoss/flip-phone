---
trigger: always_on
---

# Documentation Maintenance Rule

This project is documentation-driven. The docs in `docs/` are the single source of truth for decisions, requirements, constraints, and research. **Keeping them accurate, current, and internally consistent is a mandatory part of every task — not an optional cleanup step.**

## Read Before Acting

Before making any change, recommendation, or answering any question about this project:
1. Read `AGENTS.md` at the project root for project summary and maintenance rules.
2. Read the specific doc(s) relevant to the task (`docs/requirements.md`, `docs/constraints.md`, `docs/research-notes.md`, `docs/project-log.md`, `docs/feature-wishlist.md`, `docs/problem-definition.md`).
3. Do not rely on session context or memory alone — verify the current state against the docs.

## Update After Decisions

Whenever a decision is made, a question is resolved, or a new factor/risk is discovered during a session:

- **Decision log**: Add a dated entry to `docs/project-log.md` → "Decision Log" section, with rationale and tradeoffs. Also update the "Progress Tracking" table.
- **Requirements**: Move resolved items from "Open Questions" to "Resolved Questions" in `docs/requirements.md`. Update functional/non-functional requirements if the decision changes them.
- **Constraints**: Update `docs/constraints.md` if the decision adds, removes, or changes a technical/budget/regulatory constraint.
- **Research**: In `docs/research-notes.md`, mark resolved open questions as `**RESOLVED**` with the answer. Add new research findings under the appropriate section.
- **Wishlist**: Update `docs/feature-wishlist.md` if the decision changes component selection implications.
- **Problem definition**: Update `docs/problem-definition.md` if the architecture, MVP scope, risks, or success criteria change.
- **README**: Update `README.md` if the project overview or status changes.

If a change touches multiple docs, update all of them in the same session — do not leave docs out of sync.

## Consistency Checks

When finishing a task, verify:
- No "open question" in any doc has been resolved elsewhere but not updated.
- No decision in `project-log.md` contradicts a requirement or constraint.
- No superseded decision is still written as active (strike through + mark **SUPERSEDED**).
- Component selections referenced in one doc are consistent with all other docs.

## Superseded Decisions

Never delete old decisions from `docs/project-log.md`. Strike through the text (`~~old decision~~`) and add `**SUPERSEDED <date>**: <reason and pointer to new decision>`. The decision history must remain traceable.

## Citations

When referencing docs in responses or new doc content, use relative paths (e.g., `docs/requirements.md`), not absolute paths, so references work across environments.
