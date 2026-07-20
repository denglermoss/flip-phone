# Custom Phone Project

## Overview

Designing and building a custom cell phone from scratch. The project covers hardware design (PCB, electronics), embedded firmware, cellular communication, and eventually mechanical/enclosure design.

**Form factor is not yet locked.** The initial goal is a working phone (breadboard → custom PCB). Mechanical design (flip, candybar, slider, etc.) will be decided after the electronics and firmware are proven.

**Long-term vision**: The phone is the hub of a personal ecosystem of targeted devices. Future modules (e.g. a car infotainment system for navigation + music) would connect to the phone via USB for LTE tethering, data access, and charging. **Tethering uses the SIM7600 modem's own USB 2.0 HS port directly** (RNDIS/ECM), bypassing the MCU — no USB3300 ULPI transceiver needed. The phone project is the primary focus — ecosystem modules are future scope, but hardware decisions must not prevent them.

## Goals

- **Learning / Portfolio**: Deepen hardware and embedded systems skills; build something impressive.
- **Actually Usable**: End goal is a device that can make real phone calls on a real cellular network.
- **The Challenge**: Push beyond prior experience (microcontrollers, simple PCBs) into RF, cellular comms, power management, and eventually mechanical integration.

## Scope

### In Scope
- Custom PCB design (single-board initially; multi-board/form factor decided later)
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
│        Phone Board           │
│  - MCU (RTOS)                │
│  - Cellular Module (LTE)     │
│  - SIM Card Slot             │
│  - Display                   │
│  - Keypad                    │
│  - Mic + Speaker             │
│  - Battery + Charging IC     │
│  - Power Regulation          │
│  - Antenna                   │
│  - USB (data + power) ←──┐   │ ← Ecosystem interconnect
│  - (future: BT/WiFi)     │   │
└──────────────────────────┼──┘
                           │
    ┌──────────────────────┘
    ▼
┌─────────────────────────────┐
│  Future Module (e.g. Car)    │
│  - SBC + Display + Audio     │
│  - USB host to phone         │
│  - Uses phone LTE via tether │
└─────────────────────────────┘

Form factor (flip, candybar, etc.)
and multi-board split deferred.
Ecosystem modules are future scope.
```

## Documentation Index

- [Problem Definition](docs/problem-definition.md) — The problem, architecture, MVP, risks, success criteria
- [Requirements](docs/requirements.md) — Functional & non-functional requirements
- [Constraints](docs/constraints.md) — Technical, budget, regulatory, timeline
- [Research Notes](docs/research-notes.md) — Cellular comms primer, component research
- [Feature Wishlist](docs/feature-wishlist.md) — All potential features rated 1-10, ecosystem implications, component selection guide
- [Project Log](docs/project-log.md) — Decision log and progress tracking
- [UI Design](docs/ui-design.md) — Screen map, input model, visual style (in progress)
- [Bill of Materials](docs/bom.md) — Component list with prices, links, and cost estimates (preliminary)
- [Revisit Prompts](docs/revisit-prompts/) — Prompts for open questions requiring dedicated discussion. **All resolved and archived** (2026-06-28): modem (SIM7600 locked), codec (~~MAX9880A~~ → ALC5651 selected 2026-07-19), display (ST7789V SPI TFT selected), USB HS/ULPI (dropped — SIM7600's own USB 2.0 HS port does tethering directly, bypassing the MCU; no USB3300 needed). Archived prompts in `docs/revisit-prompts/archive/`; see `docs/revisit-prompts/README.md` for the archive index.

## Status

**Phase 1 (Research & Component Selection) — Complete.** All guiding hardware decisions locked: MCU (STM32H743ZI), modem (SIM7600NA-H), codec (ALC5651-CG), display (ST7789V SPI TFT), keypad (SMD tactile switches), USB architecture (modem-direct tethering, no ULPI). **Zephyr development environment set up (2026-06-29)** — toolchain verified by building blinky for `nucleo_h753zi`.

**Phase 2 (HAT-Based Prototype) — In Progress (2026-07-18).** All prototyping hardware received. **MVP achieved (2026-07-13)**: MCU firmware places and receives VoLTE calls with audio on Mint LTE. **Keypad integrated + verified (2026-07-18)**: 4×4 matrix keypad wired to Nucleo GPIO via Zephyr's `gpio-kbd-matrix` input driver — user types arbitrary phone numbers and places calls (A=Call, B=End, C=Backspace). Functional test passed: real VoLTE call to a user-typed number, no PC involvement. Standalone-dialer milestone reached. Remaining MVP items: signal indicator (`AT+CSQ` polling — doable now), battery indicator (PCB-phase — needs MAX17048 fuel gauge). See `docs/project-log.md` Phase Breakdown.

**Phase 3 (Schematic Design) — Started (2026-07-19).** Pre-schematic decisions settled: modem USB HS port → unpopulated connector footprint on rev1; GNSS antenna → U.FL footprint included; loudspeaker → earpiece + loudspeaker both included; SIM/microSD connector → combo-vs-separate deferred to sourcing. USB-C connector type formally locked (16-pin USB 2.0). Approach: block-diagram-first → KiCad hierarchical sheets. See `docs/project-log.md` 2026-07-19 entry.
