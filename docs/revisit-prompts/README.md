# Revisit Prompts

## Active

| Prompt | Status | Created | Summary |
|--------|--------|---------|---------|
| Parts Sourcing (`parts-sourcing-revisit.md`) | **OPEN** (5 of 13 items resolved) | 2026-07-19 | Remaining PCB parts: 1 IC on Mouser consignment (MAX9880A — Ultra Librarian model integrated, buy from Mouser), 7 mechanical parts needing JLC part selection (connectors, transducers, crystal, inductor — **switches resolved 2026-07-19: ALPS SKQGABE010 C115351**), 2 design decisions blocking part selection (J2 USB type, J3/J4 SIM+SD combo vs separate). **U4 buck-boost resolved 2026-07-19**: "TPS630201" was a phantom part number — corrected to TPS63021DSJR (LCSC C202140, JLC-stocked, no consignment). **Display panel + flip form factor resolved 2026-07-19**: HS HS20HS072RX (C5329582) — 2.0" IPS TFT, ST7789T3, 12-pin 0.5mm ZIF FPC. Flip locked (two PCBs + hinge FFC, ~13 signals). **Outer display resolved 2026-07-19**: Wisevision N114-2413THBIG01-H13 (C2890618) — 1.14" ST7789V3 TFT, 3.3V only, shares SPI bus with main display. New connectors J8-J10 added (hinge FFC + outer display). Next priority: B7 (inductor L1), then C11/C12 (J2, J3/J4 decisions), then B3-B10 (remaining mechanical + new connectors). |

## Archived (all resolved & locked 2026-06-28)

The following prompts have been resolved and locked. The files are in `archive/` and retained for historical reference only — do not re-run them.

| Prompt | Status | Resolution |
|--------|--------|------------|
| Cellular Module Selection (`modem-revisit.md`) | RESOLVED & LOCKED | SIM7600 confirmed after two rounds. LARA-R6401 disqualified (911 not supported). EC25-AF documented as PCB fallback. |
| Codec / Audio Path (`codec-audio-path-revisit.md`) | RESOLVED & LOCKED | MAX9880A dual-port codec selected. MCU not in voice path. Fallback: MCU bridge with NAU8822. |
| Display Type (`display-decision.md`) | RESOLVED & LOCKED | ST7789V SPI color TFT (2.0" 240×320, RGB565) selected. Five options evaluated. |
| USB HS / ULPI (`zephyr-usb-hs-ulpi-revisit.md`) | RESOLVED & LOCKED | USB3300 ULPI dropped. SIM7600's own USB 2.0 HS port does tethering directly. MCU USB OTG_FS sufficient. |

See `docs/project-log.md` for the full decision log and rationale.
