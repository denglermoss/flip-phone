---
name: kicad-checkpoint
description: Create a git checkpoint commit before risky or autonomous KiCad work. Ensures work is never lost and can be reverted.
triggers:
  - user
  - model
allowed-tools:
  - read
  - exec
  - grep
---

Create a git checkpoint of the current KiCad project state before risky or autonomous work. This provides a rollback point if something goes wrong.

## Steps

1. Run `git status` in the project root (`C:\Users\dengle\Documents\personal_projects\phone`).
2. **If the working tree is clean**: create a checkpoint commit with a descriptive message:
   ```
   git commit --allow-empty -m "checkpoint: <description> before <task>"
   ```
   (Use `--allow-empty` so the checkpoint exists even if there's nothing new to commit — it marks a known-good point in history.)
3. **If the working tree is dirty**: report the dirty files to the user and ask whether to:
   - Commit the current changes first (user approves the message), then create the checkpoint, or
   - Stash the changes, create the checkpoint, then pop the stash.
   Do not layer AI edits on top of uncommitted user work.
4. Report the checkpoint commit hash so the user (or a kicad-author subagent) can reference it or revert to it later.

## When to use

- Before any autonomous kicad-author workflow (per `pcb/AGENTS.md` rule 3).
- Before any consequential change to `.kicad_sch` or `.kicad_pcb` files.
- Whenever the user asks for a "checkpoint" or "save point" before KiCad work.
