# Flip Phone Project

## Overview

Designing and building a custom flip phone from scratch. The project covers hardware design (PCB, mechanical), embedded firmware, cellular communication, and integration into a usable device.

## Goals

- **Learning / Portfolio**: Deepen hardware and embedded systems skills; build something impressive.
- **Actually Usable**: End goal is a device that can make real phone calls on a real cellular network.
- **The Challenge**: Push beyond prior experience (microcontrollers, simple PCBs) into multi-board design, RF, cellular comms, and mechanical integration.

## Scope

### In Scope
- Custom PCB design (mainboard + sub-board connected via flex through hinge)
- Microcontroller + off-the-shelf cellular module architecture
- Firmware: call handling, UI, contacts, power management
- Mechanical: flip hinge, enclosure, keypad
- Making real phone calls on a real network

### Out of Scope (for now)
- Custom cellular modem / baseband processor design
- FCC certification (prototype stage; revisit if moving toward production)
- App store, browser, camera, or smartphone features
- Custom OS (will use RTOS or bare metal)

## Architecture Summary (Preliminary)

```
┌─────────────────────────────────────────┐
│              Flip Phone                  │
│                                         │
│  Top Half: Display + Speaker + Antenna   │
│     │                                    │
│   Flex Cable (through hinge)             │
│     │                                    │
│  Bottom Half: MCU + Cellular Module      │
│               Battery + Keypad + Mic     │
│               SIM Card Slot              │
└─────────────────────────────────────────┘
```

## Documentation Index

- [Problem Definition](docs/problem-definition.md) — The problem, architecture, MVP, risks, success criteria
- [Requirements](docs/requirements.md) — Functional & non-functional requirements
- [Constraints](docs/constraints.md) — Technical, budget, regulatory, timeline
- [Research Notes](docs/research-notes.md) — Cellular comms primer, component research
- [Project Log](docs/project-log.md) — Decision log and progress tracking

## Status

**Phase: Problem Definition & Requirements Gathering**
