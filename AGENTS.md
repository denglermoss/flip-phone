# AGENTS.md — Project Instructions for AI Assistants

This file provides guidance to any LLM/agent (Devin, Cascade, Claude, etc.) working on this project. It must be read and followed at the start of every session.

## Project Summary

A custom cell phone built from scratch: STM32H743ZI MCU + SIMCom SIM7600 LTE module + Zephyr RTOS + custom PCB. Target: make/receive real VoLTE calls on a US LTE network (T-Mobile/Mint). Long-term vision: the phone is the hub of a personal ecosystem of devices connected via USB. See `docs/problem-definition.md` for full context.

## Documentation Maintenance (MANDATORY)

This project is documentation-driven. The docs are the source of truth for decisions, requirements, and constraints. **Keeping them accurate and consistent is a first-class task, not an afterthought.**

### The Documents

| Doc | Purpose |
|-----|---------|
| `docs/problem-definition.md` | The problem, architecture, MVP, risks, success criteria |
| `docs/requirements.md` | Functional & non-functional requirements, resolved/open questions |
| `docs/constraints.md` | Technical, budget, regulatory, timeline constraints |
| `docs/research-notes.md` | Research findings, component analysis, open research questions |
| `docs/feature-wishlist.md` | Features rated 1-10, ecosystem implications, component selection guide |
| `docs/project-log.md` | Decision log (dated), phase breakdown, progress tracking |
| `README.md` | Project overview, documentation index, status |

### Rules

1. **Always read the relevant docs before making changes or recommendations.** Do not assume the state of the project from memory or context alone — verify against the docs.

2. **When a decision is made, update the docs:**
   - Add a dated entry to `docs/project-log.md` (Decision Log section) with rationale and tradeoffs.
   - Update `docs/requirements.md` (move items from "Open Questions" to "Resolved Questions" as appropriate).
   - Update `docs/constraints.md` if the decision adds or changes a constraint.
   - Update `docs/research-notes.md` if the decision resolves an open research question (mark it RESOLVED with the answer).
   - Update `docs/feature-wishlist.md` if the decision affects component selection implications.
   - Update `docs/problem-definition.md` if the decision changes the architecture, MVP, risks, or success criteria.
   - Update `README.md` if the decision changes the project overview or status.

3. **When a new issue, risk, or factor is discovered, document it** in the appropriate doc (constraints, research-notes, or project-log) — do not leave it only in chat.

4. **Keep docs consistent across files.** If a decision is recorded in project-log.md, ensure requirements.md and constraints.md reflect it. Stale "open questions" that have been resolved are a known failure mode — check for them.

5. **Superseded decisions**: Do not delete old decisions from project-log.md. Strike them through (`~~text~~`) and mark **SUPERSEDED <date>** with a pointer to the replacing decision. History matters.

6. **Reference docs by relative path** (e.g., `docs/requirements.md`, not absolute paths) so citations work across environments.

7. **When reviewing or auditing the project**, check for:
   - Stale "open questions" that are actually resolved
   - Decisions in project-log.md not reflected in requirements/constraints
   - Conflicts between docs (e.g., a constraint that contradicts a decision)
   - Missing factors (hardware, firmware, regulatory, power) for the current architecture

## Key Decisions (Quick Reference — verify against project-log.md for full rationale)

- **MCU**: STM32H743ZI (LQFP-144, 480MHz Cortex-M7)
- **Cellular module**: SIMCom SIM7600 series (SIM7600NA-H for prototyping on Waveshare HAT — has B71, SIM7600A-H for final PCB) — **LOCKED 2026-06-28** after two evaluation rounds. LARA-R6401 disqualified (911 not supported). EC25-AF is documented PCB fallback. Data path: CMUX+PPP (not AT+NETOPEN).
- **RTOS**: Zephyr
- **Audio codec**: TBD — WM8960 or NAU8810-class (must handle PCM voice + I2S music; open question on dual-input capability)
- **Network**: LTE with VoLTE (2G/3G dead in US)
- **Carrier**: T-Mobile/Mint (prepaid, most lenient with non-certified devices)
- **Form factor**: Deferred — single-board prototype first
- **Ecosystem interconnect**: USB (phone is USB device; car module is USB host)
- **Timekeeping**: NITZ (network time sync via SIM7600)
- **Component selection principle**: No feature rated 5+ on the wishlist may be blocked by a hardware choice

## Open Items Requiring Revisit (as of 2026-06-28)

- ~~Modem selection (standby power, B71 validation gap, simultaneous VoLTE + data, assembly method)~~ **RESOLVED & LOCKED 2026-06-28** (two rounds): SIM7600 confirmed. LARA-R6401 disqualified (911 not supported). EC25-AF evaluated as PCB fallback. PDP context conflict is AT+NETOPEN-specific (project uses CMUX+PPP). Simultaneous VoLTE+data is NOT a requirement (pause-data fallback acceptable). See project-log.md Modem Revisit (Second Round).
- Codec dual-input architecture (PCM + I2S — does it need both, or MCU bridge?)
- Display type selection (must be color-capable per "no 5+ blocked" principle)
- Zephyr USB HS via ULPI maturity on STM32H7

Discussion prompts for each revisit are in `docs/revisit-prompts/`. Paste the prompt content into a new chat to conduct the revisit. After each revisit concludes, update the relevant docs per the maintenance rules above.
