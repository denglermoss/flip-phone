# Constraints

## Technical Constraints

### Cellular Network Compatibility
- **2G (GSM) sunset**: Many regions have decommissioned or are decommissioning 2G networks. This is a CRITICAL constraint.
  - USA: AT&T shut down 2G in 2017, Verizon in 2019, T-Mobile targeted 2022-2024.
  - Europe: Varying timelines, some countries still have 2G through ~2025-2027.
  - **Implication**: A 2G-only module may not work on real networks depending on location. Need 3G (also being sunset) or LTE (4G) for longevity.
  - **LTE complication**: LTE voice (VoLTE) is more complex than legacy circuit-switched voice. Some LTE modules support it, but firmware integration is harder.
- **Module interface**: Most cellular modules communicate via UART (AT commands) or USB. This is well-documented but requires careful protocol handling.
- **911/E911 support (HARD CONSTRAINT)**: The cellular module MUST support emergency calls (911/E911). This is a safety requirement for any device used as a phone. **LARA-R6401 is disqualified** because its datasheet explicitly states "The 911 and E911 services are not supported." SIM7600 and EC25-AF both support emergency calls.
- **Data path: CMUX+PPP, not AT+NETOPEN**: The SIM7600 has a confirmed firmware bug in the `AT+NETOPEN` code path (IMS PDP context cid=2 interferes with data routing). This project uses **CMUX (GSM 07.10 multiplexer) + PPP (`ATD*99***<cid>#`)** instead, which bypasses `AT+NETOPEN` and is the standard documented pattern for simultaneous data + AT commands on the SIM7600 (Linux n_gsm, RT-Thread, ESP-IDF). Do not use `AT+NETOPEN` for data in this project.
- **Simultaneous VoLTE+data is NOT a constraint**: The project does not require data to be active during a VoLTE call. MVP is make/receive calls; daily driver adds SMS/contacts/menu. The future ecosystem (car tethering while on a call) is the only scenario that would need it, and "pause data during call" is an acceptable fallback. This is not a modem selection factor.

### Microcontroller / SoC
- Must have sufficient UART interfaces (at least 2: one for cellular module, one for debugging).
- Must have enough GPIO for keypad matrix, display interface, status LEDs, power control.
- Must have I2C/SPI for display, audio codec, and possibly battery fuel gauge.
- Must support low-power modes (deep sleep, wake on interrupt).
- **Candidates to evaluate**: STM32 family, ESP32 (has Bluetooth/Wi-Fi if needed), nRF52 series. **Selected: STM32H743ZI (LQFP-144, 480MHz Cortex-M7)** — see project-log.md and research-notes.md for selection rationale.

### PCB Design
- Single-board design initially. Multi-board split (for flip/slider/etc.) deferred until form factor is decided.
- RF trace design for cellular antenna requires impedance control (50Ω) and possibly FCC layout guidelines.
- Antenna: can use off-the-shelf cellular antenna component or PCB trace antenna (latter is harder).
- **Cellular module assembly (LGA reality)**: All candidate LTE modules (SIM7600, EG25-G, EG912U-GL, LARA-R6401) are LGA — none are hand-solderable with an iron. No LTE/VoLTE module exists in a hand-friendly package. Realistic path: JLCPCB assembly for the modem section (~$57–72: module + $3 extended fee + ~$24 fixture + solder joints), hand-solder the rest. Alternative: M.2 socket variant (module plugs in, no reflow) at cost of larger footprint. SIM7600A-H requires consignment to JLCPCB (not in their stock library); SIM7600E and SIM7600G-H-PCIE are stocked. See NFR-3 update in requirements.md.

### Power
- Cellular modules can draw 2A+ peaks during transmission — battery and power management must handle this.
- **VBAT rail stability (CRITICAL)**: The SIM7600 (and most LTE modules) require VBAT to remain within tolerance (typically ±100–200 mV) **during 2A transmit bursts**. If the rail droops, the module resets mid-call. This demands:
  - A dedicated high-current buck regulator for the module VBAT rail (not shared with MCU rails)
  - Substantial low-ESR bulk capacitance near the module VBAT pins (typically 100–470 µF ceramic + tantalum)
  - Short, wide PDN traces to VBAT pins
  - This is a schematic review checklist item and a PCB layout constraint.
- Battery: likely a single-cell LiPo (3.7V nominal). Need boost/buck converters for module power rails.
- Charging: USB (Type-C or Micro-USB) with a battery management IC. **USB-C strongly recommended** for any new design (micro-USB is obsolete).
- Battery capacity vs form factor tradeoff — final enclosure volume TBD (form factor deferred).
- **Standby current note (verified 2026-06-28 from datasheets)**: The SIM7600's LTE idle/DRX current is **17.5 mA** (the state where the module CAN receive incoming calls). The previously cited "3 mA" figure is deep-sleep, where the module cannot receive calls. To satisfy FR-1.2 (receive calls) and FR-4.3 (idle low-power with modem standby), the module must remain in LTE idle/DRX mode. The 24h standby target (FR-4.4) requires ~420 mAh minimum (17.5 mA × 24h) — achievable with an 800+ mAh battery with comfortable margin. All modules support `AT+CEDRXS` for eDRX cycle tuning (longer cycle = lower current, higher call setup latency). The modem dominates standby power; MCU sleep (~20 µA) is negligible. See research-notes.md modem revisit findings for comparison across modules.

### Audio
- Need microphone input and speaker output.
- Cellular modules typically have analog audio interfaces (PCM/I2S or analog).
- Need audio codec or use module's built-in audio path if available.
- **Audio output topology**: A phone typically needs two transducers — an **earpiece** (low power, for holding to ear during a call) and a **loudspeaker** (for ringtones, speakerphone — rated 3 on wishlist). The selected codec (e.g., WM8960) has separate speaker and headphone outputs, so this is hardware-feasible. The specific output-to-transducer mapping is a schematic design decision. Minor concern, but worth noting before schematic phase.

### Timekeeping
- The phone needs accurate time for call history timestamps (rated 7), SMS metadata, and potentially future features.
- **Selected approach: NITZ (Network Identity and Time Zone)** — the SIM7600 can sync time from the cellular network. This avoids needing a 32.768 kHz crystal on the MCU RTC and a backup battery (coin cell/supercap) to maintain time when the main battery dies. NITZ is simpler and sufficient for this use case. If time accuracy is needed when offline (no network), revisit and add an RTC crystal + backup battery.

## Budget Constraints

- **Target**: Keep relatively low; flexible but avoid unnecessary spending.
- **Major cost categories**:
  - Cellular module: $10-40 depending on generation (2G cheapest, LTE more expensive)
  - Microcontroller: $3-15
  - Display: $3-15
  - PCB fabrication: $5-50 per board (JLCPCB/PCBWay, price scales with complexity)
  - PCB assembly (if not hand-soldering): $20-80 per board
  - Battery: $5-15
  - Miscellaneous components (connectors, switches, audio, power ICs): $20-50
  - Flex cable / FPC: $5-20 (only if multi-board form factor chosen later)
  - Enclosure materials: $10-30 (3D printing)
- **Prototype BOM target**: < $150/unit
- **Total project budget** (including multiple iterations, tools, mistakes): $200-500 realistic

## Regulatory Constraints

- **FCC (USA)**: Any device transmitting RF requires FCC certification for legal sale/distribution.
  - For personal use/prototype: technically still required for intentional radiators, but enforcement is minimal for one-off personal devices.
  - Using a pre-certified cellular module can leverage the module's certification (simpler path).
  - **Decision needed**: Are we okay with prototype-only (no FCC cert) for now?
- **Carrier activation**: Some carriers are picky about which devices/IMEIs they'll activate on their network. Using a module with a valid IMEI is important.
- **SIM card**: Need a valid SIM from a carrier. Prepaid plans are easiest for testing.

## Timeline Constraints

- No hard deadline, but user wants a "decent amount of time" project — not a weekend build.
- **Estimated total effort**: See project-log.md for phase breakdown.
- **Key risk**: Cellular network compatibility testing requires getting a SIM and module early to validate before building everything else.

## Skill / Tooling Constraints

- User has: microcontroller experience, simple PCB design, soldering.
- User needs to learn (or deepen): RF PCB layout, cellular AT command protocols, audio circuits, power management for RF loads. Mechanical/CAD for enclosure deferred.
- **Tools needed**:
  - KiCad (free, open-source PCB EDA)
  - 3D CAD for enclosure (FreeCAD, Fusion 360)
  - Oscilloscope (helpful for debugging audio/UART)
  - Soldering iron (have), possibly hot air station for SMD
  - Multimeter (have, presumably)
  - Logic analyzer (cheap USB ones work fine for UART/SPI debugging)
