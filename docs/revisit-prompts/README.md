# Revisit Prompts

## Active

| Prompt | Status | Created | Summary |
|--------|--------|---------|---------|
| Parts Sourcing (`parts-sourcing-revisit.md`) | **OPEN** | 2026-07-19 | Remaining PCB parts: 2 ICs not on JLC (MAX9880A, TPS630201), 8 mechanical parts needing JLC part selection (connectors, switches, transducers, crystal, inductor), 3 design decisions blocking part selection (J2 USB type, J3/J4 SIM+SD combo vs separate, J7 display panel pick). |

## Archived (all resolved & locked 2026-06-28)

The following prompts have been resolved and locked. The files are in `archive/` and retained for historical reference only — do not re-run them.

| Prompt | Status | Resolution |
|--------|--------|------------|
| Cellular Module Selection (`modem-revisit.md`) | RESOLVED & LOCKED | SIM7600 confirmed after two rounds. LARA-R6401 disqualified (911 not supported). EC25-AF documented as PCB fallback. |
| Codec / Audio Path (`codec-audio-path-revisit.md`) | RESOLVED & LOCKED | MAX9880A dual-port codec selected. MCU not in voice path. Fallback: MCU bridge with NAU8822. |
| Display Type (`display-decision.md`) | RESOLVED & LOCKED | ST7789V SPI color TFT (2.0" 240×320, RGB565) selected. Five options evaluated. |
| USB HS / ULPI (`zephyr-usb-hs-ulpi-revisit.md`) | RESOLVED & LOCKED | USB3300 ULPI dropped. SIM7600's own USB 2.0 HS port does tethering directly. MCU USB OTG_FS sufficient. |

See `docs/project-log.md` for the full decision log and rationale.
