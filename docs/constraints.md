# Constraints

## Technical Constraints

### Cellular Network Compatibility
- **2G (GSM) sunset**: Many regions have decommissioned or are decommissioning 2G networks. This is a CRITICAL constraint.
  - USA: AT&T shut down 2G in 2017, Verizon in 2019, T-Mobile targeted 2022-2024.
  - Europe: Varying timelines, some countries still have 2G through ~2025-2027.
  - **Implication**: A 2G-only module may not work on real networks depending on location. Need 3G (also being sunset) or LTE (4G) for longevity.
  - **LTE complication**: LTE voice (VoLTE) is more complex than legacy circuit-switched voice. Some LTE modules support it, but firmware integration is harder.
- **Module interface**: Most cellular modules communicate via UART (AT commands) or USB. This is well-documented but requires careful protocol handling.

### Microcontroller / SoC
- Must have sufficient UART interfaces (at least 2: one for cellular module, one for debugging).
- Must have enough GPIO for keypad matrix, display interface, status LEDs, power control.
- Must have I2C/SPI for display, audio codec, and possibly battery fuel gauge.
- Must support low-power modes (deep sleep, wake on interrupt).
- **Candidates to evaluate**: STM32 family, ESP32 (has Bluetooth/Wi-Fi if needed), nRF52 series.

### PCB Design
- Multi-board design: main board + display board connected via flex cable through hinge.
- Flex cable routing through hinge is mechanically challenging — limited bend cycles.
- RF trace design for cellular antenna requires impedance control (50Ω) and possibly FCC layout guidelines.
- Antenna: can use off-the-shelf cellular antenna component or PCB trace antenna (latter is harder).

### Power
- Cellular modules can draw 2A+ peaks during transmission — battery and power management must handle this.
- Battery: likely a single-cell LiPo (3.7V nominal). Need boost/buck converters for module power rails.
- Charging: USB (Type-C or Micro-USB) with a battery management IC.
- Battery capacity vs form factor tradeoff — flip phones have limited internal volume.

### Audio
- Need microphone input and speaker output.
- Cellular modules typically have analog audio interfaces (PCM/I2S or analog).
- Need audio codec or use module's built-in audio path if available.

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
  - Flex cable / FPC: $5-20
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
- User needs to learn (or deepen): RF PCB layout, flex cable design, cellular AT command protocols, audio circuits, power management for RF loads, mechanical/cad for enclosure.
- **Tools needed**:
  - KiCad (free, open-source PCB EDA)
  - 3D CAD for enclosure (FreeCAD, Fusion 360)
  - Oscilloscope (helpful for debugging audio/UART)
  - Soldering iron (have), possibly hot air station for SMD
  - Multimeter (have, presumably)
  - Logic analyzer (cheap USB ones work fine for UART/SPI debugging)
