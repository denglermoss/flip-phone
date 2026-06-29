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
| `docs/bom.md` | Bill of Materials — component list with prices, links, cost estimates |
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
- **Audio codec**: MAX9880A (Maxim/ADI, TQFN-48, ~$1.70) — dual-port codec. Primary port: PCM voice from SIM7600. Secondary port: I2S music from MCU. MCU NOT in voice path. **LOCKED 2026-06-28.** Common single-port codecs (WM8960, NAU8810, etc.) cannot do both simultaneously. Fallback: MCU bridge with NAU8822. Pre-PCB: verify PCM short-frame sync support + stock availability + 1.8V level shifting.
- **Display**: ST7789V SPI color TFT (2.0" 240×320, RGB565, ~$5–8). 6 GPIO pins, 150KB framebuffer fits internal 1MB SRAM (no external SDRAM). **LOCKED 2026-06-28.** Color-capable (satisfies "no 5+ blocked" — photo capture 6, camera preview 6, video 5). Zephyr `display_st7789v.c` is most mature SPI display driver in main tree. Five options evaluated: ST7789V TFT (selected), SSD1351 color OLED (rejected — actually higher power ~57–71mA, 3–5x cost, 128×128 too low, not in Zephyr), e-ink (DISQUALIFIED — blocks camera preview/photo/video 5+ features via refresh rate + spot-color limitation), LTDC parallel RGB (20–28 GPIO, needs external SDRAM, overkill res), ST7735 (too low res). Pre-PCB: verify ST7789v driver on STM32H7 + target Zephyr version (MIPI DBI API conversion had teething issues).
- **Network**: LTE with VoLTE (2G/3G dead in US)
- **Carrier**: T-Mobile/Mint (prepaid, most lenient with non-certified devices)
- **Form factor**: Deferred — single-board prototype first
- **Ecosystem interconnect**: USB (phone is USB device; car module is USB host)
- **Timekeeping**: NITZ (network time sync via SIM7600)
- **Power architecture**: VBAT (modem) direct from LiPo (no regulator — 3.4–4.3V matches LiPo range, separate power net from MCU). 3.3V system rail via TPS630201 buck-boost (LiPo 3.0–4.2V → 3.3V). 1.8V codec rail via LDO from 3.3V. Charger: MCP73831 (USB → LiPo). Fuel gauge: MAX17048 (I2C, coulomb counting). ESD protection on all external connectors (USBLC6-2 + ESDA6V1). Resolved 2026-06-28 documentation review.
- **Component selection principle**: No feature rated 5+ on the wishlist may be blocked by a hardware choice
- **Ecosystem tethering architecture**: SIM7600's own USB 2.0 HS port (480 Mbps) does tethering directly via RNDIS/ECM (`AT+CUSBPIDSWITCH`), bypassing the MCU. MCU USB is OTG_FS (12 Mbps) only — for firmware, files, debug. **No USB3300 ULPI transceiver** (dropped 2026-06-28 — not needed). Rev1 routes modem USB to a connector footprint; future ecosystem respin adds an internal USB 2.0 hub (USB2514) for single-cable simultaneous LTE + file access. **LOCKED 2026-06-28.** See project-log.md 2026-06-28 USB HS/ULPI Revisit.

## Open Items Requiring Revisit (as of 2026-06-28)

- ~~Modem selection (standby power, B71 validation gap, simultaneous VoLTE + data, assembly method)~~ **RESOLVED & LOCKED 2026-06-28** (two rounds): SIM7600 confirmed. LARA-R6401 disqualified (911 not supported). EC25-AF evaluated as PCB fallback. PDP context conflict is AT+NETOPEN-specific (project uses CMUX+PPP). Simultaneous VoLTE+data is NOT a requirement (pause-data fallback acceptable). See project-log.md Modem Revisit (Second Round).
- ~~Codec dual-input architecture (PCM + I2S — does it need both, or MCU bridge?)~~ **RESOLVED & LOCKED 2026-06-28**: MAX9880A dual-port codec selected. SIM7600 PCM→codec primary (voice), MCU I2S→codec secondary (music). MCU NOT in voice path. Common single-port codecs cannot do both — original "unified audio path" claim was false. Fallback: MCU bridge with NAU8822. See project-log.md 2026-06-28 Codec Selection.
- ~~Display type selection (must be color-capable per "no 5+ blocked" principle)~~ **RESOLVED & LOCKED 2026-06-28**: ST7789V SPI color TFT (2.0" 240×320, RGB565) selected. 6 GPIO pins, 150KB framebuffer fits internal SRAM (no external SDRAM). Zephyr `display_st7789v.c` most mature SPI display driver in main tree. Five options evaluated: ST7789V TFT (selected), SSD1351 color OLED (rejected — actually higher power ~57–71mA, 3–5x cost, 128×128 too low, not in Zephyr), e-ink (DISQUALIFIED — blocks camera preview/photo/video 5+ features via refresh rate + spot-color limitation), LTDC parallel RGB (20–28 GPIO, needs external SDRAM, overkill res), ST7735 (too low res). Pre-PCB: verify ST7789v driver on STM32H7 + target Zephyr version. See project-log.md 2026-06-28 Display Selection.
- ~~Zephyr USB HS via ULPI maturity on STM32H7~~ **RESOLVED & LOCKED 2026-06-28**: Zephyr STM32H7 ULPI is viable (mainline since Dec 2022, PR #52772; bugs #61464/#75179 fixed; works on STM32H747I-DISCO) but **no longer needed** — the SIM7600's own USB 2.0 HS port does tethering directly via RNDIS/ECM, bypassing the MCU. USB3300 ULPI transceiver dropped. MCU USB OTG_FS (12 Mbps) is sufficient for firmware/files/debug. Rev1 routes modem USB to connector footprint; future respin adds internal USB 2.0 hub (USB2514). See project-log.md 2026-06-28 USB HS/ULPI Revisit.

**No open revisit items remain.** All four scheduled revisits (modem, codec, display, USB HS/ULPI) are resolved. The revisit prompt files have been **archived** to `docs/revisit-prompts/archive/` (see `docs/revisit-prompts/README.md` for the archive index). The prompts are retained for historical reference only — do not re-run them.
