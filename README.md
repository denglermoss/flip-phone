# Custom Phone Project

## Overview

Designing and building a custom cell phone from scratch. The project covers hardware design (PCB, electronics), embedded firmware, cellular communication, and eventually mechanical/enclosure design.

**Form factor: flip/clamshell (LOCKED 2026-07-19).** Two PCBs (main board + display daughterboard) connected via a hinge flex cable. Mechanical design (enclosure, hinge, keypad feel) is deferred to Phase 7.

**Long-term vision**: The phone is the hub of a personal ecosystem of targeted devices. Future modules (e.g. a car infotainment system for navigation + music) would connect to the phone via USB for LTE tethering, data access, and charging. **Tethering uses the SIM7600 modem's own USB 2.0 HS port directly** (RNDIS/ECM), bypassing the MCU — no USB3300 ULPI transceiver needed. The phone project is the primary focus — ecosystem modules are future scope, but hardware decisions must not prevent them.

## Goals

- **Learning / Portfolio**: Deepen hardware and embedded systems skills; build something impressive.
- **Actually Usable**: End goal is a device that can make real phone calls on a real cellular network.
- **The Challenge**: Push beyond prior experience (microcontrollers, simple PCBs) into RF, cellular comms, power management, and eventually mechanical integration.

## Scope

### In Scope
- Custom PCB design (flip/clamshell: main board + display daughterboard + hinge flex)
- Microcontroller + off-the-shelf cellular module architecture
- Firmware: call handling, UI, contacts, power management
- Making real phone calls on a real network
- Mechanical/enclosure design (deferred — decided after electronics are proven)
- Hardware selection constrained to preserve USB connectivity for future ecosystem modules

### Out of Scope (for now)
- Custom cellular modem / baseband processor design
- FCC certification (prototype stage; revisit if moving toward production)
- App store, browser, camera, or smartphone features
- Custom OS (will use RTOS or bare metal)
- Ecosystem module design (car system, etc.) — future projects, not this one

## Architecture Summary (Preliminary)

```
┌─────────────────────────────┐
│        Main Board            │
│  - MCU (RTOS)                │
│  - Cellular Module (LTE)     │
│  - SIM Card Slot             │
│  - Keypad                    │
│  - Mic + Battery + Charging  │
│  - Power Regulation          │
│  - Antenna                   │
│  - USB (data + power) ←──┐   │ ← Ecosystem interconnect
│  - (future: BT/WiFi)     │   │
└──────────────────────────┼──┘
                           │
    ┌──────────────────────┘
    │ Hinge flex (14-pin FFC)
    │
┌─────────────────────────────┐
│   Display Daughterboard       │
│  - Main display (2.0" TFT)    │
│  - Outer display (1.14" TFT)  │
│  - Earpiece speaker            │
└─────────────────────────────┘

    ┌──────────────────────┐
    │  Future Module (Car)  │
    │  - SBC + Display       │
    │  - USB host to phone   │
    │  - Uses phone LTE      │
    └────────────────────────┘
Ecosystem modules are future scope.
```

## Documentation Index

- [Problem Definition](docs/ref/problem-definition.md) — The problem, architecture, MVP, risks, success criteria
- [Requirements](docs/ref/requirements.md) — Functional & non-functional requirements
- [Constraints](docs/ref/constraints.md) — Technical, budget, regulatory, timeline
- [Block Diagram](docs/work/block-diagram.md) — Per-section pin-level wiring spec (power, MCU, modem, codec, display, keypad, SIM/SD). Source of truth for schematic entry.
- [MCU Pin Assignment](docs/work/mcu-pin-assignment.md) — STM32H743ZI full pin map (73 pins assigned, ~60 spare)
- [Research Notes](docs/ref/research-notes.md) — Cellular comms primer, component research
- [Feature Wishlist](docs/ref/feature-wishlist.md) — All potential features rated 1-10, ecosystem implications, component selection guide
- [Project Log](docs/ref/project-log.md) — Decision log (dated), phase breakdown, progress tracking
- [Task Tracker](docs/work/task-tracker.md) — Comprehensive plan to assembled PCB (Phase 3-5: schematic → layout → DIY assembly). Created 2026-07-22.
- [Schematic Completion Plan](docs/work/schematic-completion-plan.md) — Per-sheet review tracker for Phase 3 schematic fixes (created 2026-07-28)
- [UI Design](docs/work/ui-design.md) — Screen map, input model, visual style (80s sci-fi HUD)
- [Bill of Materials](docs/ref/bom.md) — Component list with prices, links, and cost estimates
- [Revisit Prompts](docs/archive/revisit-prompts/) — All 5 prompts resolved and archived (modem, codec, display, USB HS/ULPI, parts sourcing). See `docs/archive/revisit-prompts/README.md` for the archive index.
- [Archived Docs](docs/archive/) — Completed/superseded working plans retained for historical reference.

## Status

**Phase 1 (Research & Component Selection) — Complete.** All guiding hardware decisions locked: MCU (STM32H743ZI), modem (SIM7600NA-H), codec (ALC5651-CG), display (ST7789V SPI TFT), keypad (SMD tactile switches), USB architecture (modem-direct tethering, no ULPI). Zephyr development environment set up (2026-06-29).

**Phase 2 (HAT-Based Prototype) — Complete.** MVP achieved (2026-07-13): MCU firmware places and receives VoLTE calls with audio on Mint LTE. Keypad integrated + verified (2026-07-18): standalone dialer — user types phone numbers and places real calls with no PC involvement. See `docs/ref/project-log.md` Phase Breakdown.

**Phase 3 (Schematic Design) — In Progress (2026-07-28).** All parts sourced with KiCad models (no consignment). Schematic approach: flat sheet + global labels, MPCIe modem form factor (primary), LGA fallback. **Per-sheet progress** (see `docs/work/schematic-completion-plan.md` for details): Power ✅, MCU ~92%, Modem ~90%, Codec ✅ (restored), Keypad ✅, Display main ~80% (backlight FET pending), Display daughter ~70%, SIM/SD ✅. ERC: 0 errors, 15 warnings. Remaining work tracked in `docs/work/schematic-completion-plan.md`; full Phase 3-5 plan in `docs/work/task-tracker.md`.
