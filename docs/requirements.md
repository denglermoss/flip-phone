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
- **FR-2.2**: Device shall have a display capable of showing: call status, dialed digits, contacts list, signal strength, battery level.
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

### FR-5: Form Factor (Deferred)
- **FR-5.1**: Device form factor is not yet specified. Single-board prototype first.
- **FR-5.2**: Mechanical design (enclosure, form factor, keypad integration) will be decided after electronics and firmware are proven.
- **FR-5.3**: User has access to FDM, SLA, and CNC for enclosure fabrication.

## Non-Functional Requirements

### NFR-1: Performance
- Call setup time < 10 seconds from pressing "call" to hearing ringback.
- UI response time < 200ms for keypad input.
- Boot time < 15 seconds.

### NFR-2: Reliability
- Device shall not crash during a phone call.
- Device shall recover gracefully from network disconnection.
- Device shall handle power-on/power-off cycles without data loss.

### NFR-3: Manufacturability
- PCB design shall be producible by standard PCB fab houses (e.g., JLCPCB, PCBWay).
- Components shall be sourced from available distributors (DigiKey, Mouser, LCSC).
- Assembly shall be feasible with hand soldering for prototypes (minimize BGA if possible).

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
- **Display**: To be recommended based on constraints (see research-notes.md).
- **Keypad**: Deferred to Phase 2 prototyping.
- **Enclosure/Form factor**: Deferred — single-board prototype first, mechanical design after electronics are proven. User has FDM, SLA, and CNC access.
- **Firmware**: RTOS (FreeRTOS or Zephyr) — balances concurrency needs with maintainability for a daily-driver device.

## Open Questions (Requirements)

- [ ] Display type: OLED vs TFT LCD vs monochrome LCD (recommendation needed)
- [ ] Keypad: custom PCB traces vs membrane vs mechanical switches (defer to Phase 2)
- [ ] Bluetooth support: defer to post-MVP
- [ ] MCU selection: STM32 vs nRF52 vs ESP32 (need to evaluate against RTOS choice and power requirements)
- [ ] FreeRTOS vs Zephyr (Zephyr has native nRF52 support and cellular modem integration; FreeRTOS is more portable)
