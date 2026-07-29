---
status: archived
updated: 2026-07-28
---
# Revisit Prompts

## Active

| Prompt | Status | Created | Summary |
|--------|--------|---------|---------|
| _(none — all prompts resolved and archived)_ | — | — | — |

## Archived

The following prompts have been resolved and locked. The files are in `archive/` and retained for historical reference only — do not re-run them.

| Prompt | Status | Archived | Resolution |
|--------|--------|----------|------------|
| Parts Sourcing (`parts-sourcing-revisit.md`) | RESOLVED | 2026-07-28 | 16 of 16 items resolved; 2 deferred to Phase 7 (speakers LS1/LS2 — case-mounted, not PCB-assembled). All parts sourced: J3 nano-SIM = SHOU HAN NANO SIM XG6P H1.35 (C7529386), J4 microSD = Molex 472192001 (C164170). All other parts: U1-U12 ICs (U5 codec = ALC5651-CG), USBC1 USB-C (Korean Hroparts), J2 test points, J5/J6 U.FL (Hirose), J7-J10 FPC (HDGC 0.5K-HX), SW1-SW20 (ALPS SKQGABE010), Y1 crystal (ECS AEC-Q200), L1 inductor (Coilcraft XFL4020-152MEC), MK1 mic (ZILLTEK ZTS6117). **No consignment parts remain. All parts have KiCad models.** |
| Cellular Module Selection (`modem-revisit.md`) | RESOLVED & LOCKED | 2026-06-28 | SIM7600 confirmed after two rounds. LARA-R6401 disqualified (911 not supported). EC25-AF documented as PCB fallback. |
| Codec / Audio Path (`codec-audio-path-revisit.md`) | RESOLVED & LOCKED | 2026-06-28 | ~~MAX9880A dual-port codec selected~~ → **Realtek ALC5651-CG** (2026-07-19 — JLC Extended, no consignment). MCU not in voice path. Fallback: MCU bridge with NAU8822. |
| Display Type (`display-decision.md`) | RESOLVED & LOCKED | 2026-06-28 | ST7789V SPI color TFT (2.0" 240×320, RGB565) selected. Five options evaluated. |
| USB HS / ULPI (`zephyr-usb-hs-ulpi-revisit.md`) | RESOLVED & LOCKED | 2026-06-28 | USB3300 ULPI dropped. SIM7600's own USB 2.0 HS port does tethering directly. MCU USB OTG_FS sufficient. |

See `docs/ref/project-log.md` for the full decision log and rationale.
