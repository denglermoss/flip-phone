# Custom Phone Project

## Overview

Designing and building a custom cell phone from scratch — hardware (PCB, electronics), embedded firmware, cellular communication, and eventually mechanical/enclosure design. Flip/clamshell form factor (two PCBs + hinge flex, locked 2026-07-19). Long-term vision: the phone is the hub of a personal ecosystem of USB-connected devices. See `docs/ref/problem-definition.md` for full architecture, MVP, risks, and ecosystem vision.

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

## Documentation

Full doc index and source-of-truth assignments in `AGENTS.md`. Key docs:

- `docs/ref/problem-definition.md` — architecture, MVP, risks, ecosystem vision
- `docs/ref/requirements.md` — functional & non-functional requirements
- `docs/ref/constraints.md` — technical, budget, regulatory constraints
- `docs/ref/project-log.md` — decision log (dated), phase breakdown
- `docs/ref/bom.md` — bill of materials with prices and links
- `docs/work/` — active planning docs (block-diagram, pin assignment, task tracker, schematic completion plan, UI design)
- `docs/archive/` — completed/superseded plans + all revisit prompts

## Status

**Phase 1 (Research & Component Selection) — Complete.** All guiding hardware decisions locked: MCU (STM32H743ZI), modem (SIM7600NA-H), codec (ALC5651-CG), display (ST7789V SPI TFT), keypad (SMD tactile switches), USB architecture (modem-direct tethering, no ULPI). Zephyr development environment set up (2026-06-29).

**Phase 2 (HAT-Based Prototype) — Complete.** MVP achieved (2026-07-13): MCU firmware places and receives VoLTE calls with audio on Mint LTE. Keypad integrated + verified (2026-07-18): standalone dialer — user types phone numbers and places real calls with no PC involvement. See `docs/ref/project-log.md` Phase Breakdown.

**Phase 3 (Schematic Design) — In Progress (2026-07-28).** All parts sourced with KiCad models (no consignment). Schematic approach: flat sheet + global labels, MPCIe modem form factor (primary), LGA fallback. **Per-sheet progress** (see `docs/work/schematic-completion-plan.md` for details): Power ✅, MCU ~92%, Modem ~90%, Codec ✅ (restored), Keypad ✅, Display main ~80% (backlight FET pending), Display daughter ~70%, SIM/SD ✅. ERC: 0 errors, 15 warnings. Remaining work tracked in `docs/work/schematic-completion-plan.md`; full Phase 3-5 plan in `docs/work/task-tracker.md`.
