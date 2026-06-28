# Problem Definition

## The Problem

Design and build a custom flip phone from scratch that can make and receive real voice calls on a live cellular network in the United States. The device must eventually become a usable daily-driver, not just a lab prototype.

## Why This Is Hard

A flip phone is a convergence of five engineering disciplines, each non-trivial on its own:

1. **Cellular Communication** — The device must register on a real LTE network, authenticate via SIM, and establish VoLTE calls. This requires a cellular module, correct AT command sequencing, audio path configuration, and antenna integration. Get any of this wrong and there's no call.

2. **Multi-Board Hardware** — A flip phone has two halves connected through a hinge. This means two PCBs linked by a flex cable that must survive thousands of bend cycles. Power, audio, display, and control signals all route through this hinge.

3. **Embedded Firmware** — An RTOS must concurrently manage: UART communication with the cellular module (parsing async AT responses), UI rendering on a display, keypad input handling, call state machine, and power management policies. All within tight memory and power constraints.

4. **Power Management** — Cellular modules draw 2A+ peaks during transmission. The battery, regulators, and charging circuit must handle this while fitting in a small enclosure. Standby time needs to be at least 24 hours.

5. **Mechanical Integration** — The hinge mechanism, enclosure, keypad, display mounting, and antenna placement must all fit together in a pocketable form factor. The flex cable routing through the hinge is a known failure point.

## Architecture (Preliminary)

```
┌──────────────────────────────┐
│         TOP HALF              │
│  - Display (SPI/I2C)          │
│  - Earpiece Speaker           │
│  - Cellular Antenna           │
│  - Status LED                 │
└──────────┬───────────────────┘
           │ Flex Cable (FPC)
           │ - Display bus
           │ - Speaker audio
           │ - Antenna feed (50Ω)
           │ - GPIO (status LED)
┌──────────┴───────────────────┐
│       BOTTOM HALF             │
│  - MCU (STM32/nRF52, RTOS)    │
│  - Cellular Module (LTE/VoLTE)│
│  - SIM Card Slot              │
│  - Battery + Charging IC      │
│  - Keypad (matrix)            │
│  - Microphone                 │
│  - Power Regulation           │
└──────────────────────────────┘
```

## MVP Definition

**Minimum Viable Phone**: A device that can make and receive voice calls on a US LTE network.

| Feature | MVP | Daily Driver |
|---------|-----|-------------|
| Make calls | ✅ | ✅ |
| Receive calls | ✅ | ✅ |
| Contacts | ❌ | ✅ |
| SMS | ❌ | ✅ |
| Menu system | ❌ | ✅ |
| Battery indicator | ✅ | ✅ |
| Signal indicator | ✅ | ✅ |
| Bluetooth | ❌ | Maybe |
| Enclosure | Test jig | ✅ |

## Key Constraints Summary

| Constraint | Value |
|-----------|-------|
| Region | United States |
| Network | LTE (VoLTE) |
| Carrier | T-Mobile/Mint recommended (prepaid) |
| Firmware | RTOS (FreeRTOS or Zephyr) |
| PCB EDA | KiCad |
| Budget | Keep low; flexible |
| Prototype BOM | < $150/unit |
| Form factor | Flip/clamshell, two PCBs + flex |
| Assembly | Hand-solderable for prototypes |
| Enclosure | 3D print (FDM/SLA) or CNC |

## Key Risks

1. **VoLTE configuration** — Getting VoLTE working via AT commands may require carrier-specific settings. Need to validate early with a breakout board before committing to PCB design.
2. **Antenna/RF** — LTE antenna in a small flip form factor may have poor performance. May need PCB respin.
3. **Flex cable through hinge** — Routing display + audio + RF through a bending flex cable is mechanically and electrically challenging.
4. **Power budget** — Meeting 24h standby with a small battery while powering an LTE module is tight.
5. **Carrier device whitelisting** — Some US carriers block unknown IMEIs. T-Mobile prepaid is the most lenient, but this needs validation.

## Success Criteria

- **MVP**: Successfully place and receive a voice call from the custom-built device to another phone, with intelligible audio, on a US LTE network.
- **Daily driver**: Use the device as primary phone for one week, including contacts, SMS, and acceptable battery life.
