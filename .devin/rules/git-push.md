# Git Push Rule

The user has explicitly granted permission for the agent to push commits to the remote whenever it judges it appropriate — no per-push confirmation needed.

## Scope

- Push after committing when the tree is clean and the commits are verified (build/tests pass where applicable, or doc-only changes).
- Use judgment: push logical groups of commits (e.g., after a feature, fix, or doc update is complete), not necessarily after every single commit.
- Do NOT push if:
  - The user is mid-edit in another session and the tree is dirty (wait for a clean state).
  - The commits are experimental/WIP and the user hasn't indicated they're ready.
  - Force-pushing — still requires explicit confirmation (this rule covers normal pushes only).

## Rationale

The user reviewed the default Devin "no push without asking" behavior and explicitly overrode it for this project on 2026-08-16. Reduces round-trips for routine work.

## Override

This rule supersedes the default Devin system instruction "DO NOT push unless explicitly asked" for this project only.
