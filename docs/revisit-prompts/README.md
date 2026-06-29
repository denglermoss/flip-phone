# Revisit Prompts — ARCHIVED

**All revisit prompts have been resolved and locked as of 2026-06-28.** The prompt files have been moved to `archive/`.

| Prompt | Status | Resolution |
|--------|--------|------------|
| Cellular Module Selection (`modem-revisit.md`) | RESOLVED & LOCKED | SIM7600 confirmed after two rounds. LARA-R6401 disqualified (911 not supported). EC25-AF documented as PCB fallback. |
| Codec / Audio Path (`codec-audio-path-revisit.md`) | RESOLVED & LOCKED | MAX9880A dual-port codec selected. MCU not in voice path. Fallback: MCU bridge with NAU8822. |
| Display Type (`display-decision.md`) | RESOLVED & LOCKED | ST7789V SPI color TFT (2.0" 240×320, RGB565) selected. Five options evaluated. |
| USB HS / ULPI (`zephyr-usb-hs-ulpi-revisit.md`) | RESOLVED & LOCKED | USB3300 ULPI dropped. SIM7600's own USB 2.0 HS port does tethering directly. MCU USB OTG_FS sufficient. |

The archived prompts are retained for historical reference. See `docs/project-log.md` for the full decision log and rationale.
