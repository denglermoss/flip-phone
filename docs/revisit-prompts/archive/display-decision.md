# Revisit Prompt: Display Type Selection

**STATUS: RESOLVED & LOCKED 2026-06-28** — Revisit conducted. **ST7789V SPI color TFT** (2.0" 240×320, RGB565, ~$5–8) selected.

**Outcome**: Five options evaluated: (1) SPI color TFT ST7789V 2.0" 240×320 — **SELECTED**; (2) SPI color OLED SSD1351 1.5" 128×128 — rejected (actually HIGHER power than TFT at ~57–71mA per datasheet — self-emissive OLED draws current per pixel; 3–5x cost at $15–24; 128×128 too low for phone UI/camera preview; not in Zephyr main tree, only out-of-tree driver); (3) E-ink (B/W or spot-color BWRY) — **DISQUALIFIED** by "no 5+ blocked" (blocks camera preview 6 at ~0.5–3fps refresh, photo capture 6 with spot-color only no blue/green/gradents, video 5; true color e-ink not available at 1.5–2.4"); (4) Parallel RGB TFT via LTDC 2.0" 320×480 — rejected (20–28 GPIO pins eats spare margin needed for future ULPI/BT; needs external SDRAM for comfortable double-buffering; 320×480 overkill for feature-phone UI); (5) SPI TFT ST7735 1.8" 128×160 — rejected (too low resolution). ST7789V wins on Zephyr driver maturity (`display_st7789v.c` most widely-used SPI display driver in main tree, native LVGL support), GPIO efficiency (6 pins preserves 31-spare margin), no external SDRAM (150KB framebuffer fits internal 1MB SRAM), color-capable (satisfies "no 5+ blocked" — photo capture 6, camera preview 6, video 5), lower power than the OLED alternative, and cost (~$5–8). Pre-PCB: verify ST7789v driver on STM32H7 + target Zephyr version (MIPI DBI API conversion had teething issues). See project-log.md 2026-06-28 Display Selection and research-notes.md Display Options section. **Note (2026-06-28)**: The "future ULPI" rationale for rejecting LTDC was superseded by the USB HS/ULPI Revisit (ULPI dropped; modem-direct USB tethering replaces it). The LTDC rejection still stands — it eats margin needed for BT and other future peripherals — but the spare margin is now 41 (was 31 with ULPI). See zephyr-usb-hs-ulpi-revisit.md.

---

**Purpose**: Paste the prompt below into a new chat to make a decision on the display, which has been deferred but is now blocking (it affects the "no 5+ features blocked" principle and needs to be settled before schematic design).

---

## Prompt to paste into new chat:

I'm working on a custom cell phone project (STM32H743ZI + SIMCom SIM7600 LTE module + Zephyr RTOS + custom PCB). The full project docs are in the `docs/` folder — please read them before responding, especially `research-notes.md` (Display Options section), `feature-wishlist.md` (Media and Component Selection Summary), and `requirements.md` (Open Questions).

## The situation

Display type has been deferred since the start of the project. It's now time to decide because:
1. The schematic phase is approaching, and the display interface affects PCB routing and GPIO allocation.
2. The "no 5+ features blocked" principle (see `project-log.md`) means the display must be **color-capable** — photo capture (rated 6) and camera preview need color. A monochrome display would block a 5+ feature.
3. The STM32H743 has both **SPI** peripherals and the **LTDC** (LCD TFT Controller) for parallel RGB displays, so the MCU supports either path.

## What I need from you:

1. Read the docs first for full context on the wishlist ratings, power constraints, and the ecosystem vision.
2. Lay out the realistic display options for a phone-sized device (1.8"–2.4" is typical for a feature-phone form factor):
   - Small SPI color TFT (e.g., 1.8" 128×160 or 2.0" 240×320 ST7789/ILI9341)
   - Small SPI OLED (e.g., 1.5" 128×128 SSD1327 color OLED)
   - Parallel RGB TFT via LTDC (e.g., 2.0" 320×480 — needs FMC/SDRAM for framebuffer?)
   - Any other realistic option
3. For each option, evaluate:
   - **Power consumption** (matters for the 24h standby target — see `constraints.md` power section)
   - **Cost** (target BOM < $150/unit)
   - **GPIO pin count** (see the GPIO budget in `research-notes.md` — SPI display = 6 pins, parallel RGB = 28 pins)
   - **Framebuffer memory** (does it fit in the H743's 1MB SRAM, or does it need external SDRAM via FMC? See the FMC analysis in `research-notes.md`.)
   - **Zephyr LVGL support** (how mature is the driver for this display type in Zephyr?)
   - **Suitability for camera preview** (rated 6 — can it show a live preview at reasonable framerate?)
   - **Suitability for a phone UI** (call status, contacts list, menus — readability at phone size)
4. Give me a clear recommendation: **which display should we use, and why.** Include a specific panel recommendation (controller IC, resolution, size, interface) if possible.
5. Confirm the recommendation doesn't block any 5+ feature.
6. Update the docs (`research-notes.md`, `requirements.md` open questions, `project-log.md` decision log) with the decision — follow the doc maintenance rules in `AGENTS.md`.

## Context that may help
- This is a feature-phone-like device, not a smartphone. The UI is menus, contacts, call screens, maybe a camera preview — not full-screen video or web browsing.
- The user has FDM/SLA/CNC for enclosure, so the display mounting is flexible.
- The form factor is still deferred (single-board prototype first), but the display choice should be reasonable for an eventual phone enclosure.
