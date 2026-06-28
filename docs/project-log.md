# Project Log

## Decision Log

### 2026-06-28: Problem Definition Session
- **Decision**: Target US market — LTE with VoLTE is the only viable network path.
  - *Rationale*: 2G and 3G are shut down in the US. No point building for dead networks.
- **Decision**: Carrier-agnostic, but recommend T-Mobile/Mint for testing.
  - *Rationale*: T-Mobile is most lenient with non-certified devices on prepaid. Good LTE band 2/4/66 coverage.
- **Decision**: MVP = voice calls only (make/receive). Contacts, SMS, menus are post-MVP.
  - *Rationale*: Get to a working call as fast as possible to validate the hardest part (cellular + audio + firmware). Everything else is additive.
- **Decision**: Use RTOS (FreeRTOS or Zephyr) for firmware, not bare metal.
  - *Rationale*: Concurrent requirements (AT command parsing, UI, power management, call state machine) make bare metal unwieldy for a daily-driver. RTOS provides task scheduling without sacrificing control. FreeRTOS vs Zephyr TBD.
- **Decision**: Form factor/mechanical design deferred. Start with single-board design.
  - *Rationale*: The hard problems (cellular, firmware, power, RF) are form-factor independent. Locking into flip early adds constraints (flex cable, hinge, multi-board) before core electronics are validated. Decide mechanical design after the phone works on a single board.
- **Decision**: Display type deferred — will recommend based on constraints.
- **Decision**: Keypad design deferred to Phase 2 prototyping.

### 2026-06-28: Modular Ecosystem Vision
- **Decision**: Adopt a long-term vision of a personal ecosystem of targeted devices, with the phone as the connectivity hub.
  - *Rationale*: Building one perfect do-everything phone is unrealistic as a first project. Decomposing into targeted modules (car system, etc.) makes each piece achievable. The phone remains the primary project.
- **Decision**: First envisioned module is a car system (navigation + music), connecting to phone via USB.
  - *Rationale*: Car dock scenario makes USB ideal — provides data + power in one cable, higher bandwidth than Bluetooth, lower latency. Phone charges while docked. Android USB tethering is native. Car system offloads the hardest work (cellular) to the phone.
- **Decision**: USB is the primary ecosystem interconnect; Bluetooth/WiFi deferred for future wireless modules.
  - *Rationale*: USB is simpler, higher bandwidth, and provides power. Wireless is needed only for modules that can't be physically docked — that's a future problem.
- **Decision**: Ecosystem vision does not change MVP scope, but does constrain hardware selection — MCU must have USB capability.
  - *Rationale*: Selecting an MCU without USB would preclude future ecosystem integration. This is a low-cost constraint (many candidate MCUs have USB) that keeps the door open.

### 2026-06-28: Project Kickoff
- **Decision**: Use off-the-shelf cellular module + custom MCU architecture (not designing custom modem).
  - *Rationale*: Designing a custom cellular modem is impractical. Off-the-shelf modules handle the radio protocol stack while still being challenging in PCB/firmware/mechanical design.
- **Decision**: Target LTE (not 2G/3G) for network compatibility.
  - *Rationale*: 2G and 3G networks are decommissioned or sunsetting in the US. LTE with VoLTE is the only viable long-term option.
- **Decision**: Use KiCad for PCB design.
  - *Rationale*: Open-source, well-supported, no license cost.
- **Decision**: Flip/clamshell form factor with two PCBs connected via flex cable.
  - *Rationale*: Core to the project concept. Adds mechanical and routing complexity (desired challenge).
  - *Note*: **Revised 2026-06-28** — Form factor deferred. Single-board first, mechanical design after electronics proven.

## Phase Breakdown & Effort Estimate

### Phase 1: Research & Component Selection (~2-3 weeks, part-time)
- Deep-dive into cellular modules, compare datasheets
- Select MCU, display, cellular module, audio components
- Order dev boards / breakout boards for initial prototyping
- Get a prepaid SIM and test module with AT commands on a breadboard
- **Deliverable**: Component shortlist + working AT command proof-of-concept on breadboard

### Phase 2: Breadboard Prototype (~2-4 weeks, part-time)
- Wire MCU + cellular module + display + keypad on breadboard/perfboard
- Write firmware: UART driver for AT commands, call state machine, basic UI
- Make a test phone call
- **Deliverable**: Working phone call from breadboard setup

### Phase 3: Schematic Design (~2-4 weeks, part-time)
- Design full schematic in KiCad
- Power management circuit (battery charging, regulation, module power)
- Audio circuit (mic, speaker, codec or module direct)
- Display and keypad interfacing
- Flex cable connector selection and pinout
- **Deliverable**: Complete schematic, reviewed

### Phase 4: PCB Layout (~3-5 weeks, part-time)
- Main board layout (MCU, cellular module, power, keypad, SIM, mic)
- Display board layout (display, speaker, antenna)
- Flex cable design / FPC specification
- RF trace impedance control for antenna
- DRC, manufacturing prep (Gerbers, BOM, pick-and-place)
- **Deliverable**: PCB files sent to fab

### Phase 5: Assembly & Board Bring-up (~2-4 weeks)
- Receive PCBs, solder components
- Power on, verify rails, basic MCU blink
- Bring up cellular module, verify network registration
- Bring up display, keypad, audio
- **Deliverable**: Functional bare PCB phone (no enclosure)

### Phase 6: Firmware Development (~4-8 weeks, part-time)
- Full UI implementation (menus, contacts, call screen)
- Power management policies (sleep, wake, modem power states)
- Call handling robustness (error recovery, network loss)
- Contact storage (flash/EEPROM)
- **Deliverable**: Feature-complete firmware

### Phase 7: Mechanical Design & Enclosure (~3-6 weeks, part-time)
- 3D model the enclosure in CAD
- Design hinge mechanism
- Design keypad integration
- 3D print iterations, fit-check with PCBs
- **Deliverable**: Functional enclosure, assembled phone

### Phase 8: Integration & Testing (~2-4 weeks)
- Full assembly
- Test calls, battery life, durability
- Fix issues discovered during integration
- **Deliverable**: Working flip phone prototype

### Total Estimate
- **Conservative estimate**: 4-6 months working part-time (evenings/weekends)
- **Aggressive estimate**: 2-3 months with focused effort
- **Realistic estimate**: 5-8 months with natural pacing, learning curves, and iteration

### Key Risk Areas (likely to extend timeline)
1. **RF/antenna**: First PCB may have antenna issues requiring a respin.
2. **Cellular module bring-up**: Subtle AT command / VoLTE configuration issues.
3. **Mechanical hinge**: Flex cable failure, fit issues, 3D print iterations.
4. **Power management**: Battery life tuning, peak current handling.

## Progress Tracking

| Date | Milestone | Status |
|------|-----------|--------|
| 2026-06-28 | Project definition & documentation started | In Progress |
| 2026-06-28 | Modular ecosystem vision documented; USB interconnect constraint added to hardware selection | Done |
