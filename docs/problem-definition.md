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

**Tethering architecture (updated 2026-06-28)**: LTE tethering to the car module uses the **SIM7600's own USB 2.0 HS port (480 Mbps)** directly — the modem presents itself as a USB network adapter (RNDIS/ECM via `AT+CUSBPIDSWITCH`), bypassing the MCU entirely. The MCU's USB (OTG_FS, 12 Mbps) handles firmware updates, file/MSC transfer, and debug. A future internal USB 2.0 hub (USB2514) presents both the modem (LTE) and the MCU (files) to the car module over one USB-C cable. The earlier "MCU bridges LTE to USB CDC ECM, needs USB HS via ULPI" plan is superseded — no USB3300 ULPI transceiver needed. See `docs/project-log.md` 2026-06-28 USB HS/ULPI Revisit.

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
| Battery indicator | ❌ | ✅ |
| Signal indicator | ❌ | ✅ |
| Bluetooth | ❌ | Maybe |
| USB data (ecosystem) | ❌ | ✅ |
| Enclosure | Test jig | ✅ |

## Key Constraints Summary

| Constraint | Value |
|-----------|-------|
| Region | United States |
| Network | LTE (VoLTE) |
| Carrier | T-Mobile/Mint recommended (prepaid) |
| Firmware | Zephyr RTOS |
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
5. **Mechanical/form factor** — Flip/clamshell locked 2026-07-19 (two PCBs + hinge flex). Hinge mechanism, enclosure fit, and keypad feel are Phase 7 concerns. The display daughterboard is trivial (~5 components); the main board complexity is unchanged vs single-board.
6. **Ecosystem compatibility** (future risk) — Hardware choices (MCU USB capability, modem USB routing, connector selection) must not preclude future module connectivity. **Resolved 2026-06-28**: tethering uses the SIM7600's own USB 2.0 HS port directly (no MCU USB HS / ULPI needed); rev1 routes the modem USB to a connector footprint to preserve the option, with an internal USB hub planned for the ecosystem respin. Low risk.
7. ~~**MAX9880A codec availability/compatibility**~~ **→ ALC5651 codec availability/compatibility** (pre-PCB risk — **FULLY RESOLVED 2026-07-19**): ~~The selected dual-port codec (MAX9880A) has been verified...~~ **SUPERSEDED 2026-07-19**: MAX9880A replaced by **Realtek ALC5651-CG** (LCSC C963633, QFN-40 5×5mm, JLC Extended — no consignment). All three pre-PCB items verified for ALC5651: (1) PCM short-frame sync is confirmed compatible — ALC5651 §7.5.1 PCM Mode A (short sync, Figures 10-11) in slave mode matches SIM7600 §3.6 (master, short sync, 16-bit, 2048/4096kHz BCLK); (2) stock is available at LCSC (407 units, JLC Extended — no consignment needed); (3) SIM7600 PCM pin voltage is 1.8V — confirmed 2026-06-30 from HW Design Manual V1.03 (Table 32 + §3.6.2). PCM lines connect directly to the ALC5651 (also 1.8V). Datasheet (Rev 0.9, 134pp) is complete — full pinout, registers, application circuit, timing, package. The fallback (MCU bridge with NAU8822) remains documented. The Waveshare HAT prototyping (NAU8810) validates the SIM7600 PCM voice output independent of this risk. See project-log.md 2026-07-19 Codec Swap MAX9880A→ALC5651.

## Success Criteria

- **MVP**: ~~Successfully place and receive a voice call from the custom-built device to another phone, with intelligible audio, on a US LTE network.~~ **ACHIEVED 2026-07-13** — MCU firmware places outgoing VoLTE call (`ATD6078821755;` → `VOICE CALL: BEGIN` → `VOICE CALL: END`) and receives incoming calls (detects `RING` URC → auto-answers with `ATA` → `VOICE CALL: BEGIN`). Audio works both directions through HAT's NAU8810 codec. Running on Nucleo H753ZI + Waveshare SIM7600NA-H HAT (not yet custom PCB). See project-log.md 2026-07-13.
- **Daily driver**: Use the device as primary phone for one week, including contacts, SMS, and acceptable battery life.
