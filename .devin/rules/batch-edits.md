---
trigger: always_on
---

# Batch Edits Rule

When a task requires multiple edits to the same file (or closely related files), perform them in a **single tool block containing multiple `edit` calls** rather than issuing several sequential, separate edit calls.

## Why

- Fewer round-trips → faster completion and lower cost.
- One review checkpoint for the whole change set → easier to verify correctness and consistency.
- Avoids intermediate states where a file is half-edited, which can break partial verification steps.

## How

- Plan all the edits first (read the file, identify every `old_string` → `new_string` pair).
- Issue all `edit` calls for that file in **one tool block** so they execute together.
- Only split into multiple tool blocks when an edit genuinely depends on the result of a prior edit (e.g., you need to re-read the file between edits because an earlier edit changed line numbers you were relying on).

## When NOT to batch

- Edits that depend on each other's output (must be sequential).
- Edits to files you have not yet read in this session — read first, then batch the edits.
- Very large change sets where batching would make the diff hard to review — split logically and say so.
