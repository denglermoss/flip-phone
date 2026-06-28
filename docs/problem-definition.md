# Problem Definition

## The Problem

Design and build a custom cell phone from scratch that can make and receive real voice calls on a live cellular network in the United States. The device must eventually become a usable daily-driver, not just a lab prototype.

**Form factor is deferred.** The initial focus is electronics and firmware. Mechanical design (flip, candybar, slider, etc.) will be decided after the core phone functionality is proven on a single-board design.

## Modular Ecosystem Vision (Future — Does Not Affect MVP)

The phone is the first and primary project. However, the long-term vision is a **personal ecosystem of targeted devices** that can connect to the phone (or each other) for connectivity and shared data. The phone acts as the hub — providing LTE, contacts, music storage — while satellite modules handle specific tasks with their own UIs.

**First envisioned module: Car System**
- Display navigation (Google Maps alternatives — Organic Maps, OsmAnd, Mapbox)
- Play music (local files, phone storage, Spotify via librespot)
- Connect to phone via **USB** for tethered LTE + data + charging (primary), or Bluetooth/WiFi (future wireless modules)
- This is essentially a custom head unit / infotainment system

**Design principle**: The phone's hardware and firmware decisions must not prevent ecosystem integration. Specifically, the phone must expose connectivity interfaces (USB at minimum) that allow a future module to access LTE tethering, file storage, and potentially audio. This does not change the MVP scope — it only constrains hardware choices to leave the door open.

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
│  - USB (data + power) ←──┐   │ ← Ecosystem interconnect
│  - (future: BT/WiFi)     │   │
└──────────────────────────┼──┘
                           │
    ┌──────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│  Future Module (e.g. Car)    │
│  - SBC (Linux)               │
│  - Display (5-7" TFT)        │
│  - Audio out                 │
│  - USB host to phone         │
│  - Uses phone LTE via tether │
└─────────────────────────────┘

Multi-board split and form factor
(flip, candybar, etc.) deferred.
Ecosystem modules are future scope.
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
| USB data (ecosystem) | ❌ | ✅ |
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
| Ecosystem interconnect | USB (data + power); BT/WiFi deferred |

## Key Risks

1. **VoLTE configuration** — Getting VoLTE working via AT commands may require carrier-specific settings. Need to validate early with a breakout board before committing to PCB design.
2. **Antenna/RF** — LTE antenna design on a custom PCB may have poor performance. May need PCB respin.
3. **Power budget** — Meeting 24h standby with a small battery while powering an LTE module is tight.
4. **Carrier device whitelisting** — Some US carriers block unknown IMEIs. T-Mobile prepaid is the most lenient, but this needs validation.
5. **Mechanical/form factor** (deferred risk) — Flex cable, hinge, enclosure fit. Will become relevant once electronics are proven.
6. **Ecosystem compatibility** (future risk) — Hardware choices (MCU USB capability, connector selection, firmware USB stack) must not preclude future module connectivity. Low risk if USB-capable MCU is selected.
7. **MAX9880A codec availability/compatibility** (pre-PCB risk) — The selected dual-port codec (MAX9880A) must be verified for PCM short-frame sync support on its primary port and in-stock availability at distributors before committing to PCB. Fallback (MCU bridge with NAU8822) exists but adds firmware complexity. The Waveshare HAT prototyping (NAU8810) validates the SIM7600 PCM voice output independent of this risk.

## Success Criteria

- **MVP**: Successfully place and receive a voice call from the custom-built device to another phone, with intelligible audio, on a US LTE network.
- **Daily driver**: Use the device as primary phone for one week, including contacts, SMS, and acceptable battery life.
