---
trigger: always_on
---

# No Idling While Subagents Run

When the parent agent launches background subagents (via `run_subagent` with `is_background=true`), it must **not idle or block waiting for them to finish**. It must keep doing useful, non-conflicting work in parallel and only check on subagents when there is nothing left to do or when a subagent's output is required to proceed.

## Why

- Idling wastes wall-clock time and tokens — the whole point of background subagents is parallelism.
- A parent that blocks on `read_subagent` with `block=true` the moment it spawns a subagent defeats the purpose of running it in the background.
- The user sees a stalled agent with no progress, which is indistinguishable from a hang.

## How

1. **Launch background subagents only when there is other work to do in parallel.** If there is nothing else to do, run the subagent in the foreground (`is_background=false`) instead — that is the honest representation of the dependency.
2. **After spawning a background subagent, immediately continue with other useful work** that does not depend on the subagent's output and does not conflict with it (e.g., do not edit files the subagent is editing). Good parallel work: reading other docs, running independent searches, preparing the next step's plan, drafting doc updates that will be merged after the subagent returns.
3. **Only call `read_subagent` when:**
   - You have exhausted all independent work, OR
   - You genuinely need the subagent's output to take the next action.
   In the first case, use `block=true` to wait. In the second, prefer `block=false` first to check if it's done; if not, keep doing other work and check again later. Do not poll in a tight loop.
4. **Never spawn a background subagent and then immediately call `read_subagent` with `block=true`** in the same turn. That is equivalent to a foreground call but with worse UX. Either run it foreground, or do real work first.

## When NOT to apply

- Foreground subagents (`is_background=false`) — blocking is the correct behavior there by definition.
- When the subagent's output is a hard prerequisite for the very next action AND there is truly no other work to do — in that case, just use a foreground subagent.
- Safety-critical sequences where proceeding in parallel could cause data loss or file conflicts (e.g., two agents writing the same file). In that case, serialize — but say so explicitly rather than silently idling.
