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
- [Bill of Materials](docs/bom.md) — Component list with prices, links, and cost estimates (preliminary)
- [Revisit Prompts](docs/revisit-prompts/) — Prompts for open questions requiring dedicated discussion. **All resolved and archived** (2026-06-28): modem (SIM7600 locked), codec (MAX9880A selected), display (ST7789V SPI TFT selected), USB HS/ULPI (dropped — SIM7600's own USB 2.0 HS port does tethering directly, bypassing the MCU; no USB3300 needed). Archived prompts in `docs/revisit-prompts/archive/`; see `docs/revisit-prompts/README.md` for the archive index.

## Status

**Phase: Problem Definition & Requirements Gathering**
