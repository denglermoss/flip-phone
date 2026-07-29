---
status: reference
updated: 2026-07-28
---
# Requirements

## Functional Requirements

### FR-1: Cellular Communication
- **FR-1.1**: Device shall place outgoing voice calls to any phone number.
- **FR-1.2**: Device shall receive incoming voice calls and alert the user (ring).
- **FR-1.3**: Device shall support SMS send/receive (post-MVP, required for daily-driver).
- **FR-1.4**: Device shall connect to a real cellular network via a standard SIM card.
- **FR-1.5**: Device shall operate on networks currently active in the user's region (see constraints — 2G sunset issue).

### FR-2: User Interface
- **FR-2.1**: Device shall have a numeric keypad (0-9, *, #) plus call/end buttons.
  - **Prototype status (2026-07-18)**: Implemented on the Nucleo+HAT prototype using a 4×4 matrix keypad (Adafruit PID 3844) via Zephyr's `gpio-kbd-matrix` input driver. Keys: 0-9/\*/# = digits, A = Call, B = End/Cancel/Reject, C = Backspace, D = Menu (future). Final PCB will use SMD tactile switches in a 5×4 matrix (same driver, different devicetree pins).
- **FR-2.2**: Device shall have a display capable of showing: call status, dialed digits, contacts list, signal strength, battery level.
  - **Prototype status (2026-07-18)**: Call status + dialed digits implemented (LVGL labels on ST7789V). Signal strength and battery level not yet implemented (signal indicator is next; battery indicator is PCB-phase — needs MAX17048 fuel gauge in the battery power path).
- **FR-2.3**: Device shall support navigation buttons (up/down/select or D-pad) for menu interaction.
- **FR-2.4**: Device shall provide audible feedback (ringtones, key tones, call audio).

### FR-3: Contacts & Storage
- **FR-3.1**: Device shall store contacts locally (name + phone number). (Post-MVP)
- **FR-3.2**: Device shall persist contacts across power cycles. (Post-MVP)
- **FR-3.3**: Device shall allow adding, deleting, and editing contacts. (Post-MVP)

### FR-4: Power Management
- **FR-4.1**: Device shall be battery-powered and rechargeable via USB.
- **FR-4.2**: Device shall monitor and display battery level.
- **FR-4.3**: Device shall enter low-power mode when idle (display off, modem standby).
- **FR-4.4**: Device shall support a standby time of at least 24 hours (target).

### FR-5: Form Factor (Flip/Clamshell — LOCKED 2026-07-19)
- **FR-5.1**: Device form factor is flip/clamshell — two PCBs (main board + display daughterboard) connected via a 14-pin 0.5mm hinge flex cable. Main display (ST7789V 2.0") + outer display (1.14" TFT) on the daughterboard; keypad, MCU, modem, battery, and connectors on the main board.
- **FR-5.2**: Mechanical design (enclosure, hinge mechanism, keypad feel) is deferred to Phase 7 — depends on electronics being proven first. See `docs/ref/project-log.md` 2026-07-19 Display Panel Selection + Flip Form Factor Locked.
- **FR-5.3**: User has access to FDM, SLA, and CNC for enclosure fabrication.

### FR-6: Ecosystem Connectivity (Future — Constrains Hardware Selection Now)
- **FR-6.1**: Device MCU shall have USB capability (device or OTG mode) to enable future module connectivity. This is a hardware selection constraint, not an MVP feature.
- **FR-6.2**: Device PCB shall include a USB data connector (not charge-only) routed to the MCU. Physical connector type TBD.
- **FR-6.3**: Future scope (post-daily-driver): USB tethering to expose LTE connectivity to external modules. **Architecture (2026-06-28)**: tethering uses the SIM7600's own USB 2.0 HS port directly (RNDIS/ECM via `AT+CUSBPIDSWITCH`), bypassing the MCU — the modem is the USB network adapter, not the MCU. The MCU's USB (OTG_FS) is not in the tethering path. See project-log.md 2026-06-28 USB HS/ULPI Revisit.
- **FR-6.4**: Future scope: File access (contacts, music storage) over USB for external modules.
- **FR-6.5**: Bluetooth/WiFi for wireless ecosystem modules is deferred — not a hardware selection constraint at this time.

## Non-Functional Requirements

### NFR-1: Performance
- Call setup time < 10 seconds from pressing "call" to hearing ringback.
- UI response time < 200ms for keypad input.
- Boot time (MCU firmware ready + UI displayed): < 15 seconds. Note: full LTE network registration is a separate, longer sequence (~15–30s depending on carrier and signal) and is not included in this target. The phone shall show a "searching for network" indicator during registration.

### NFR-2: Reliability
- Device shall not crash during a phone call.
- Device shall recover gracefully from network disconnection.
- Device shall handle power-on/power-off cycles without data loss.

### NFR-3: Manufacturability
- PCB design shall be producible by standard PCB fab houses (e.g., JLCPCB, PCBWay).
- Components shall be sourced from available distributors (DigiKey, Mouser, LCSC).
- Assembly shall be feasible with hand soldering for prototypes, **except the cellular module** — all LTE/VoLTE modules are LGA and require reflow or JLCPCB assembly. Realistic approach: JLCPCB assembles the modem section (~$57–72), hand-solder the rest. No LTE module exists in a hand-friendly package; this is an industry reality. (Updated 2026-06-28 per modem revisit.) **MPCIe option (primary 2026-07-22)**: the SIM7600NA-H-PCIE Mini PCIe socketed card plugs into an SMD socket that reflows with the rest of the board — no LGA reflow, no JLC PCBA required for the modem. The MPCIe card is the primary form factor; bare LGA is the fallback. See `docs/ref/constraints.md` MPCIe section and `docs/ref/project-log.md` 2026-07-22 Schematic Approach entry.

### NFR-4: Maintainability
- Firmware shall be modular and well-structured.
- Hardware design files shall be version-controlled and documented.
- Schematics and PCB layouts shall be in KiCad (open-source EDA).

### NFR-5: Cost
- Prototype BOM cost target: < $150 per unit (excluding PCB fab costs).
- Total project budget: keep relatively low; avoid gold-plating.

## Resolved Decisions

- **Region**: United States
- **Network**: LTE with VoLTE (2G/3G are shut down in the US)
- **Carrier**: No preference — will use cheapest/easiest prepaid SIM. T-Mobile/Mint recommended (most lenient with non-certified devices, good LTE band coverage).
- **MVP scope**: Voice calls only (make/receive). Contacts, SMS, menus are post-MVP.
- **Daily-driver scope**: Calls + contacts + SMS + basic menu system (feature phone experience).
- **Display**: ST7789V SPI color TFT, 2.0" 240×320, RGB565. See research-notes.md Display Options section and project-log.md 2026-06-28 Display Selection.
- **Keypad**: SMD tactile switches on custom PCB traces (LOCKED 2026-06-28). See Resolved Questions below and project-log.md 2026-06-28 Keypad Selection.
- **Enclosure/Form factor**: Flip/clamshell — two PCBs (main board + display daughterboard) connected via hinge flex cable. **LOCKED 2026-07-19** (supersedes 2026-06-28 deferral). Hinge mechanism + enclosure design deferred to Phase 7 (mechanical design). User has FDM, SLA, and CNC access.
- **Firmware**: Zephyr RTOS — balances concurrency needs with maintainability for a daily-driver device. See project-log.md 2026-06-28 RTOS Selection.

## Open Questions (Requirements)

- [ ] **MCU-to-modem UART stress test** (post-MVP, pre-PCB): Run a long-duration stress test of the LPUART1 ↔ SIM7600 UART link — send 100+ AT commands back-to-back with no delay, verify zero data loss (every response contains expected result code). Test with varied response sizes (short `AT`→`OK`, long `AT+CGMM`, multi-line `AT+COPS?`). Also test GPS NMEA streaming (continuous data into the 1KB ring buffer — verify no overflow). This validates the interrupt-driven UART + ring buffer architecture is reliable enough for the final PCB. Deferred until after the MVP call works — the current 4-command test is sufficient for MVP development. See project-log.md 2026-07-13 entries.

## Resolved Questions (moved from Open)

Full rationale for each decision is in `docs/ref/project-log.md` — entries below are one-line summaries with links.

- [x] **Bluetooth support**: Deferred to post-MVP (external module needed — no MCU has classic BT A2DP). See project-log.md 2026-06-28.
- [x] **MCU selection**: STM32H743ZI. See project-log.md 2026-06-28 MCU Selection.
- [x] **FreeRTOS vs Zephyr**: Zephyr. See project-log.md 2026-06-28 RTOS Selection.
- [x] **USB mode**: USB FS only (12 Mbps) for MCU; ULPI/USB3300 dropped — SIM7600's own USB HS does tethering. See project-log.md 2026-06-28 USB HS/ULPI Revisit.
- [x] **USB device vs OTG**: Device-only sufficient (car module is host). See project-log.md 2026-06-28 USB HS/ULPI Revisit.
- [x] **Modem selection**: SIM7600 locked after two rounds. LARA-R6401 disqualified (no 911). EC25-AF is PCB fallback. See project-log.md 2026-06-28 Modem Revisit (Second Round).
- [x] **Codec selection**: ALC5651-CG (dual I2S/PCM, MCU not in voice path). ~~MAX9880A~~ superseded. See project-log.md 2026-07-19 Codec Swap.
- [x] **Display selection**: ST7789V SPI TFT 2.0" (color-capable, no 5+ features blocked). See project-log.md 2026-06-28 Display Selection.
- [x] **Keypad selection**: SMD tactile switches, 5×4 matrix. See project-log.md 2026-06-28 Keypad Selection.
- [x] **USB-C connector type**: 16-pin USB-C (USB 2.0). See project-log.md 2026-07-19.
- [x] **Modem USB HS port on rev1**: Routed to unpopulated connector footprint. See project-log.md 2026-07-19.
- [x] **GNSS antenna on rev1**: U.FL footprint included. See project-log.md 2026-07-19.
- [x] **Loudspeaker on rev1**: Both earpiece and loudspeaker included. See project-log.md 2026-07-19.
- [x] **SIM + microSD connector strategy**: Resolved during sourcing — separate sockets. See `docs/ref/bom.md` and project-log.md 2026-07-19.
