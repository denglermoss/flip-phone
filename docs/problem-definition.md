# Problem Definition

## The Problem

Design and build a custom cell phone from scratch that can make and receive real voice calls on a live cellular network in the United States. The device must eventually become a usable daily-driver, not just a lab prototype.

**Form factor is deferred.** The initial focus is electronics and firmware. Mechanical design (flip, candybar, slider, etc.) will be decided after the core phone functionality is proven on a single-board design.

## Why This Is Hard

A cell phone is a convergence of five engineering disciplines, each non-trivial on its own:

1. **Cellular Communication** — The device must register on a real LTE network, authenticate via SIM, and establish VoLTE calls. This requires a cellular module, correct AT command sequencing, audio path configuration, and antenna integration. Get any of this wrong and there's no call.

2. **Hardware / PCB Design** — MCU, cellular module, power management, audio circuit, display, keypad, SIM, and antenna all on a custom PCB. RF trace impedance control, power rail integrity for 2A+ module peaks, and component placement all matter.

3. **Embedded Firmware** — An RTOS must concurrently manage: UART communication with the cellular module (parsing async AT responses), UI rendering on a display, keypad input handling, call state machine, and power management policies. All within tight memory and power constraints.

4. **Power Management** — Cellular modules draw 2A+ peaks during transmission. The battery, regulators, and charging circuit must handle this while fitting in a small enclosure. Standby time needs to be at least 24 hours.

5. **Mechanical Integration** (deferred) — Enclosure, keypad feel, display mounting, antenna placement, and form factor. This is a separate design phase that depends on the electronics being proven first.

## Architecture (Preliminary — Single Board)

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
└─────────────────────────────┘

Multi-board split and form factor
(flip, candybar, etc.) deferred.
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
| Form factor | Deferred — single board first, mechanical design later |
| Assembly | Hand-solderable for prototypes |
| Enclosure | 3D print (FDM/SLA) or CNC |

## Key Risks

1. **VoLTE configuration** — Getting VoLTE working via AT commands may require carrier-specific settings. Need to validate early with a breakout board before committing to PCB design.
2. **Antenna/RF** — LTE antenna design on a custom PCB may have poor performance. May need PCB respin.
3. **Power budget** — Meeting 24h standby with a small battery while powering an LTE module is tight.
4. **Carrier device whitelisting** — Some US carriers block unknown IMEIs. T-Mobile prepaid is the most lenient, but this needs validation.
5. **Mechanical/form factor** (deferred risk) — Flex cable, hinge, enclosure fit. Will become relevant once electronics are proven.

## Success Criteria

- **MVP**: Successfully place and receive a voice call from the custom-built device to another phone, with intelligible audio, on a US LTE network.
- **Daily driver**: Use the device as primary phone for one week, including contacts, SMS, and acceptable battery life.
