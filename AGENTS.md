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
- **Cellular module**: SIMCom SIM7600 series (SIM7600NA-H for both prototyping on Waveshare HAT and the final PCB — has B71 for T-Mobile 600MHz) — **LOCKED 2026-06-28** after two evaluation rounds. LARA-R6401 disqualified (911 not supported). EC25-AF is documented PCB fallback. Data path: CMUX+PPP (not AT+NETOPEN). **Part name corrected 2026-07-19**: "SIM7600A-H" was a misnomer — SIMCom's actual product code is `SIM7600NA-H` (North America H-series, 119-pin LCC+LGA). The old LCSC link (C2995537) pointed to the non-H `SIM7600A` (87-pin LCC, different package). NA-H is a JLC pre-order part (C5380303, $31.42); G-H (C5355477, in stock, same package) is the footprint fallback. See project-log.md 2026-07-19.
- **RTOS**: Zephyr
- **Audio codec**: Realtek ALC5651-CG (LCSC C963633, QFN-40 5×5mm, JLC Extended — no consignment) — dual I2S/PCM audio hub codec. ~~MAX9880A (Maxim/ADI, TQFN-48, ~$1.70)~~ **SUPERSEDED 2026-07-19** (was Mouser consignment — replaced to eliminate the last consignment part). Primary port (I2S-1): PCM voice from SIM7600. Secondary port (I2S-2): I2S music from MCU. MCU NOT in voice path. **LOCKED 2026-06-28** (MAX9880A), **updated 2026-07-19** (ALC5651). Common single-port codecs (WM8960, NAU8810, etc.) cannot do both simultaneously. Fallback: MCU bridge with NAU8822. PCM compatibility verified: ALC5651 §7.5.1 PCM Mode A (short sync) = SIM7600 §3.6 (master, short sync, 16-bit, 2048/4096kHz). Datasheet: `docs/reference/alc5651.pdf` (Rev 0.9, 134pp).
- **Display**: ST7789V SPI color TFT (2.0" 240×320, RGB565, ~$5–8). 6 GPIO pins, 150KB framebuffer fits internal 1MB SRAM (no external SDRAM). **LOCKED 2026-06-28.** Color-capable (satisfies "no 5+ blocked" — photo capture 6, camera preview 6, video 5). Zephyr `display_st7789v.c` is most mature SPI display driver in main tree. Five options evaluated: ST7789V TFT (selected), SSD1351 color OLED (rejected — actually higher power ~57–71mA, 3–5x cost, 128×128 too low, not in Zephyr), e-ink (DISQUALIFIED — blocks camera preview/photo/video 5+ features via refresh rate + spot-color limitation), LTDC parallel RGB (20–28 GPIO, needs external SDRAM, overkill res), ST7735 (too low res). **Specific panel LOCKED 2026-07-19**: HS HS20HS072RX (LCSC C5329582) — 2.0" IPS TFT, ST7789T3, 12-pin 0.5mm ZIF FPC, 4 parallel LEDs (PWM dimming), $3.42, 1786 in stock. Pre-PCB: verify ST7789T3 works with `display_st7789v.c` driver on STM32H7 + target Zephyr version.
- **Keypad**: SMD tactile switches on custom PCB traces. **LOCKED 2026-06-28.** 5×4 matrix = 9 GPIO for ~20 keys (12 numeric + 2 call/end + 3–5 nav + 1 spare). Three options evaluated: SMD tactile (selected — simple, cheap ~$1–2, easy to source), conductive-rubber/silicone dome (phone-like feel but custom tooling ~$50–150), membrane PET stack (sealed but flat feel, hard to source). Phase 2 prototyping: off-the-shelf 4×4 matrix module + loose tactile buttons. Specific switch part TBD at schematic time. Keypad feel deferred to Phase 7 (mechanical/enclosure).
- **Network**: LTE with VoLTE (2G/3G dead in US)
- **Carrier**: T-Mobile/Mint (prepaid, most lenient with non-certified devices)
- **Form factor**: Flip/clamshell — two PCBs (main board + display daughterboard) connected via hinge flex cable. **LOCKED 2026-07-19** (supersedes 2026-06-28 deferral). Display daughterboard is trivial (~5 components + 3 ZIF connectors). Hinge flex ~13 signals (display SPI + backlight + earpiece speaker + outer display CS2/DC2) on 14-pin 0.5mm FFC. Outer display: EastRising ER-TFT1.14-2 (BuyDisplay), 1.14" ST7789V TFT, 8-pin 0.5mm FPC, shares SPI bus with main display. **Both display panels purchased separately from PCB and assembled by user** (ZIF FPC plugs in post-assembly). Camera out of scope for rev1 (will go in base when added). Hinge mechanism + enclosure deferred to Phase 7.
- **Ecosystem interconnect**: USB (phone is USB device; car module is USB host)
- **Timekeeping**: NITZ (network time sync via SIM7600)
- **Power architecture**: +BATT (modem) direct from LiPo (no regulator — 3.4–4.3V matches LiPo range, separate power net from MCU). 3.3V system rail via TPS63021DSJR buck-boost (LiPo 3.0–4.2V → 3.3V, fixed 3.3V, 4A switches, LCSC C202140 — LOCKED 2026-07-19; docs previously said "TPS630201" which was a phantom part number, corrected). 1.8V codec rail via LDO from 3.3V. Charger: MCP73831 (USB → LiPo). Fuel gauge: MAX17048 (I2C, coulomb counting). ESD protection on all external connectors (USBLC6-2 + ESDA6V1). Resolved 2026-06-28 documentation review; U4 part corrected 2026-07-19. Net names standardized 2026-07-22: `+BATT`, `+3.3V`, `+1V8` (schematic power symbols); ref designators `J1` (USB-C), `J_BATT` (battery), `U10` (USBLC6-2).
- **Component selection principle**: No feature rated 5+ on the wishlist may be blocked by a hardware choice
- **Ecosystem tethering architecture**: SIM7600's own USB 2.0 HS port (480 Mbps) does tethering directly via RNDIS/ECM (`AT+CUSBPIDSWITCH`), bypassing the MCU. MCU USB is OTG_FS (12 Mbps) only — for firmware, files, debug. **No USB3300 ULPI transceiver** (dropped 2026-06-28 — not needed). Rev1 routes modem USB to a connector footprint; future ecosystem respin adds an internal USB 2.0 hub (USB2514) for single-cable simultaneous LTE + file access. **LOCKED 2026-06-28.** See project-log.md 2026-06-28 USB HS/ULPI Revisit.
- **Schematic / PCB**: KiCad. **Flat sheet structure + global labels** (not hierarchical sheets — board is ~30-40 parts, hierarchical overhead not worth it). **Modem form factor: MPCIe primary** (SIM7600NA-H-PCIE, Techship S2-109KS-Z30G9 — SMD socket, no LGA reflow), **LGA fallback** (pivot only if MPCIe proves difficult during layout). **Updated 2026-07-22** (supersedes 2026-07-19 hierarchical-sheets approach and the 2026-07-22 "try both in layout" framing). **Progress: power section schemed + reviewed (2026-07-22); all other sections to be specified.** See project-log.md 2026-07-22 Schematic Approach entry and `docs/block-diagram.md`.

## Open Items Requiring Revisit (as of 2026-06-28)

- ~~Modem selection (standby power, B71 validation gap, simultaneous VoLTE + data, assembly method)~~ **RESOLVED & LOCKED 2026-06-28** (two rounds): SIM7600 confirmed. LARA-R6401 disqualified (911 not supported). EC25-AF evaluated as PCB fallback. PDP context conflict is AT+NETOPEN-specific (project uses CMUX+PPP). Simultaneous VoLTE+data is NOT a requirement (pause-data fallback acceptable). See project-log.md Modem Revisit (Second Round).
- ~~Codec dual-input architecture (PCM + I2S — does it need both, or MCU bridge?)~~ **RESOLVED & LOCKED 2026-06-28, updated 2026-07-19**: ~~MAX9880A dual-port codec selected~~ → **Realtek ALC5651-CG** (dual I2S/PCM audio hub, JLC Extended — no consignment). SIM7600 PCM→codec I2S-1 (voice), MCU I2S→codec I2S-2 (music). MCU NOT in voice path. Common single-port codecs cannot do both — original "unified audio path" claim was false. Fallback: MCU bridge with NAU8822. See project-log.md 2026-07-19 Codec Swap MAX9880A→ALC5651.
- ~~Display type selection (must be color-capable per "no 5+ blocked" principle)~~ **RESOLVED & LOCKED 2026-06-28**: ST7789V SPI color TFT (2.0" 240×320, RGB565) selected. 6 GPIO pins, 150KB framebuffer fits internal SRAM (no external SDRAM). Zephyr `display_st7789v.c` most mature SPI display driver in main tree. Five options evaluated: ST7789V TFT (selected), SSD1351 color OLED (rejected — actually higher power ~57–71mA, 3–5x cost, 128×128 too low, not in Zephyr), e-ink (DISQUALIFIED — blocks camera preview/photo/video 5+ features via refresh rate + spot-color limitation), LTDC parallel RGB (20–28 GPIO, needs external SDRAM, overkill res), ST7735 (too low res). Pre-PCB: verify ST7789v driver on STM32H7 + target Zephyr version. See project-log.md 2026-06-28 Display Selection.
- ~~Zephyr USB HS via ULPI maturity on STM32H7~~ **RESOLVED & LOCKED 2026-06-28**: Zephyr STM32H7 ULPI is viable (mainline since Dec 2022, PR #52772; bugs #61464/#75179 fixed; works on STM32H747I-DISCO) but **no longer needed** — the SIM7600's own USB 2.0 HS port does tethering directly via RNDIS/ECM, bypassing the MCU. USB3300 ULPI transceiver dropped. MCU USB OTG_FS (12 Mbps) is sufficient for firmware/files/debug. Rev1 routes modem USB to connector footprint; future respin adds internal USB 2.0 hub (USB2514). See project-log.md 2026-06-28 USB HS/ULPI Revisit.

**No open revisit items remain.** All four scheduled revisits (modem, codec, display, USB HS/ULPI) are resolved. The revisit prompt files have been **archived** to `docs/revisit-prompts/archive/` (see `docs/revisit-prompts/README.md` for the archive index). The prompts are retained for historical reference only — do not re-run them.

## Workflow Preferences

- **Commit messages**: When using a temporary file for the commit message (e.g., `.git/COMMIT_MSG.txt`), always delete it after committing. Do not leave temporary files in the `.git/` directory.
- **Roles**: The user is the project lead and engineer. The agent is the assistant/intern. The user owns all decisions, architecture, and direction. The agent's job is to research, verify, implement, and explain — not to steer the project. Present findings and options with tradeoffs; the user decides. Reserve autonomous action for mechanical/verification tasks (building, installing, checking stock) where there's a clear right answer. For anything involving judgment or tradeoffs, ask first.
- **Learning is a project goal**: The user wants to understand how things work, not just get answers. Explain the concepts and tradeoffs behind decisions as you go — don't just hand over results. The project docs say "the steep learning curve is a feature, not a bug," and that applies to the collaborative process too.

## Reference Documentation & PDF MCP Server (set up 2026-06-30)

Vendor datasheets, reference manuals, and hardware design docs are stored locally in `docs/reference/` (gitignored — only `docs/reference/README.md` is tracked, which indexes every file with its exact part number and download URL). When a datasheet is cited in the project docs (e.g., "Hardware Design Manual V1.03 §3.6"), the local PDF is the source of truth.

**PDF MCP server** (`mcp-pdf`, rsp2k/mcp-pdf on PyPI) is configured in the Windsurf MCP config (`~/.codeium/windsurf/mcp_config.json`) and auto-imported by Devin at session start. It provides:
- `textextraction__extract_text` — extract text from any PDF (by page or full doc), via PyMuPDF with auto-fallback to pdfplumber/pypdf
- `tableextraction__extract_tables` — extract tables (electrical characteristics, pin tables, timing)
- `documentanalysis__get_document_structure` — TOC/outline for navigation
- Image/SVG extraction, OCR, and more (14 tool mixins total)

**How to use**: When verifying a spec, pin voltage, register address, or timing parameter, call the MCP tools against the local PDFs in `docs/reference/` rather than relying on web search snippets. The MCP server handles encrypted vendor PDFs (e.g., SIMCom manuals) that `webfetch` cannot parse. Example: `textextraction__extract_text` with `pdf_path` pointing to the SIM7600 manual, `pages="35"`, `inline=true` returns the PCM reference design page in ~0.06s.

**Tooling**: `uv`/`uvx` (Astral, installed via winget) manages the isolated Python environment for `mcp-pdf` — no manual venv maintenance. The MCP config uses the full path to `uvx.exe` (`C:\Users\dengle\AppData\Local\Microsoft\WinGet\Links\uvx.exe`).

**Mandatory — add missing datasheets before citing them**: If a datasheet you need to reference is not already in `docs/reference/`, you MUST find and download it first (vendor website, LCSC/Mouser/DigiKey product page, etc.) and add a row to `docs/reference/README.md`'s PDF index. Do not cite specs from memory, web search snippets, or session context alone — datasheet specs vary by revision and package variant, and citing from memory risks pinout/voltage/package errors that are expensive to catch after PCB fab. If a datasheet genuinely cannot be found, say so in `docs/project-log.md` and flag the spec as unverified. See `docs/reference/README.md` "Mandatory: add missing datasheets before citing them" for the full workflow.

## Zephyr Development Environment (set up 2026-06-29)

The Zephyr dev environment is installed on Windows (native, not WSL — WSL flashing is unsupported per Zephyr docs). See `docs/project-log.md` 2026-06-29 entry for full details.

- **Workspace**: `C:\Users\dengle\zephyrproject` (external to the phone repo — multi-GB tree, not version-controlled here)
- **Python venv**: `C:\Users\dengle\zephyrproject\.venv` (Python 3.12, contains west 1.5.0 + Zephyr Python deps)
- **Zephyr SDK**: `C:\Users\dengle\zephyr-sdk-1.0.1` (ARM toolchain `arm-zephyr-eabi-gcc` 14.3.0)
- **Board target**: `nucleo_h753zi` (the prototyping board — NUCLEO-H753ZI, substitute for the obsolete NUCLEO-H743ZI; STM32H753 = H743 + crypto, identical for this project)
- **Activation**: Dot-source `scripts/activate-zephyr.ps1` in a new PowerShell terminal to refresh PATH and activate the venv
- **Build a sample**: `cd ~/zephyrproject/zephyr; west build -p always -b nucleo_h753zi samples/basic/blinky`
- **Build the phone firmware**: `cd C:\Users\dengle\Documents\personal_projects\phone; . .\scripts\activate-zephyr.ps1; $env:ZEPHYR_BASE = "$env:HOMEPATH\zephyrproject\zephyr"; west build -b nucleo_h753zi firmware`
- **Known gap**: Zephyr SDK Windows host tools (QEMU, OpenOCD) are not available. Install OpenOCD separately (xpack-openocd or winget) before flashing via ST-Link. Building works now; flashing needs this extra step.
- **Firmware app**: `firmware/` directory in the phone repo — Zephyr application with `CMakeLists.txt` (build manifest), `prj.conf` (Kconfig features), `app.overlay` (devicetree hardware config), `src/main.c` (application code). Skeleton created 2026-07-05, builds successfully. See `docs/project-log.md` 2026-07-05 entry.
- **Path constraint**: The project directory must NOT contain spaces — Zephyr's devicetree preprocessor splits paths at spaces and fails. Directory renamed from `Personal Projects` to `personal_projects` on 2026-07-05 for this reason.
