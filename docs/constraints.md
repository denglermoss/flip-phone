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
- Must have enough GPIO for keypad matrix, display interface, status LEDs, power control, **modem PWRKEY/STATUS control**.
- Must have I2C/SPI for display, audio codec, **battery fuel gauge (MAX17048)**.
- Must support low-power modes (deep sleep, wake on interrupt).
- **Modem control GPIO (required)**: The SIM7600 requires a PWRKEY GPIO (pulse to power on/off) and a STATUS output GPIO (module ready indicator). Optionally a RESET GPIO (hard reset, rarely needed). Allocate **2 GPIO pins minimum** (PWRKEY + STATUS) in the GPIO budget. These are not optional — the MCU cannot power-cycle the modem without them.
- **Candidates to evaluate**: STM32 family, ESP32 (has Bluetooth/Wi-Fi if needed), nRF52 series. **Selected: STM32H743ZI (LQFP-144, 480MHz Cortex-M7)** — see project-log.md and research-notes.md for selection rationale.

### PCB Design
- Single-board design initially. Multi-board split (for flip/slider/etc.) deferred until form factor is decided.
- RF trace design for cellular antenna requires impedance control (50Ω) and possibly FCC layout guidelines.
- Antenna: can use off-the-shelf cellular antenna component or PCB trace antenna (latter is harder).
- **Board size target (MPCIe variant, 2026-07-22)**: **Main board < 2×3 inches (~50×76mm, ~3800mm²).** First-pass estimate was ~100×65mm (conservative, most parts on top); revised to ~55×78mm with aggressive 2-sided placement (MCU + most ICs on bottom under keypad zone; MPCIe + keypad stacked on top sharing the 54mm width). User believes < 2×3" is achievable with a more comfortable layout. Deferred to KiCad layout for real numbers — not recalculated yet. MPCIe modem (54×32mm keepout) is the largest single block and sets the ~54mm minimum dimension. Display daughterboard ~55×42mm (unchanged). See project-log.md 2026-07-22 Board Size Estimate.
- **Cellular module assembly (LGA reality)**: All candidate LTE modules (SIM7600, EG25-G, EG912U-GL, LARA-R6401) are LGA — none are hand-solderable with an iron. No LTE/VoLTE module exists in a hand-friendly package. Realistic path: JLCPCB assembly for the modem section (~$57–72: module + $3 extended fee + ~$24 fixture + solder joints), hand-solder the rest. Alternative: M.2 socket variant (module plugs in, no reflow) at cost of larger footprint. **SIM7600NA-H (C5380303) is a JLC pre-order part** — 0 in stock, JLC sources it from SIMCom on demand ~~($31.42, lead time ≤18 days auto-proceed / >18 days email confirmation)~~ **JLC price corrected 2026-07-22: $59.00/ea, 8-day lead time**. Stored in your private JLC library until PCBA order. **SIM7600G-H (C5355477, 39 in stock, $46.95) shares the identical 119-pin LCC+LGA package** — usable as a footprint fallback if NA-H library data is incomplete (do NOT buy G-H for the board: it lacks B71). SA-H and E-H are 87-pin LCC (different package) and lack B71 — disqualified. See NFR-3 update in requirements.md and project-log.md 2026-07-19 SIM7600 Variant Selection.
- **MPCIe form factor option (under evaluation 2026-07-22, PCM confirmed 2026-07-22)**: SIM7600NA-H-PCIE (S2-109KS-Z30G9) from Techship ~$50/ea — Mini PCIe socketed card. Same B71/B66/VoLTE/GNSS/PCM specs as the LGA NA-H. **PCM CONFIRMED** from SIM7600 Series PCIE Hardware Design V1.03 §2.2 (p14) and §3.10.1 (p29): pins 45 (PCM_CLK), 47 (PCM_OUT), 49 (PCM_IN), 51 (PCM_SYNC) — master mode, short sync, 16-bit, 2048kHz, 1.8V. Exact match to ALC5651 PCM Mode A. PCIE variant = no onboard codec = PCM active; PCIEA variant = onboard NAU8810 = PCM NC (analog audio instead). Part S2-109KS-Z30G9 ends in PCIE (not PCIEA). **All MPCIe socket options are SMD** (0.8mm pitch, right-angle, surface mount — NOT through-hole as previously stated). Socket reflows with the rest of the board — no iron work needed. Socket options: Amphenol G633A0520022U (LCSC C357792, 1589 stock, ~5mm height), SOFNG PCIE-52P40H (LCSC C444926, 3039 stock, 4mm height), Hanbo PCI-E-H52-52P (LCSC C3039346), **JLC basic C9900027618** (5.2mm height, no extended fee if going JLC PCBA). Dimensions: 50.8×31×5.35mm card (vs LGA 30×30×1.5mm — adds ~21mm length, ~4mm height). **Additional findings from V1.03 manual**: (1) Onboard SIM socket on PCIE card (§3.7) — may eliminate need for SIM socket on our PCB (confirm with Techship); (2) UART is 1.8V (§3.8, same as bare LGA — level shifter needed either way); (3) Pin mapping differs from LGA: PERST# (pin 22, reset), WAKE# (pin 1, wake host), W_DISABLE# (pin 20, RF disable), LED_WWAN# (pin 42, network status) — **no PWRKEY pin** (TBD how MPCIe module powers on/off); (4) I2C at 1.8V (§3.9, pulled up in-module); (5) USB 2.0 HS on pins 36/38 (same as LGA, VBUS internal to VBAT). **Approach: try both MPCIe + bare LGA footprints in KiCad layout before locking form factor.** See project-log.md 2026-07-22 MPCIe PCM Verified.
- **DIY assembly approach (under evaluation 2026-07-22)**: User considering full DIY assembly (no JLC PCBA) to save cost and as a learning goal. Only 1 board needed (no MOQ 2 without JLC PCBA). Plan: 1 modem + 2-3 board qty of all other parts (spares for DIY mistakes). Tools needed: reflow oven (T-962 ~$150) + preheater ($50-100) + stencil ($20-40, with modem area cut out if LGA) + solder paste ($15-30) + USB microscope ($30-50) + hot-air station ($50-100). 2-sided board: top (heavy: modem/MCU/codec/connectors) + bottom (light: ~20 keypad switches + passives). DIY sequence: stencil+populate+reflow bottom → flip → stencil+populate+reflow top. If MPCIe adopted, modem socket is SMD (reflows with the rest of the board — no separate iron step) — remaining hard parts: ALC5651 QFN-40, TPS63021 VSON-14, FPC connectors 0.5mm pitch. See project-log.md 2026-07-22 assembly evaluation.
- **ESD protection (required for external connectors)**: All external-facing data lines need ESD protection diodes placed close to the connector:
  - **USB-C D+/D-**: USBLC6-2SC6 (bidirectional, SOT-23-6, ~$0.50) — protects MCU USB OTG_FS.
  - **SIM + microSD data lines**: ESDA6V1-5SC6 (5-line array, ~$0.50) — protects modem SIM interface and MCU SDMMC.
  - These are small, cheap, and standard practice for any device with external connectors. Omitting them risks ESD damage during handling.
- **Modem USB HS port (rev1 decision, 2026-07-19)**: Route the SIM7600's USB 2.0 HS port (D+/D-) to an **unpopulated connector footprint** on rev1. Reasons beyond tethering: modem firmware updates (some versions only flash over USB), USB-based AT/diagnostics (higher bandwidth than UART), GNSS NMEA over USB (alternative to UART), and the future ecosystem (car module tethering via RNDIS/ECM). The footprint preserves all options without a respin. Cost: footprint + 2 ESD diodes + short traces. The MCU's USB OTG_FS (12 Mbps) goes to the main populated USB-C connector for firmware/files/debug — the modem USB is a separate, optional connector.
- **GNSS antenna (rev1 decision, 2026-07-19)**: Include a **U.FL footprint** for the GNSS antenna on rev1. SIM7600 has built-in GNSS (validated 2026-07-12 on HAT — valid fix in ~60s cold start, works while registered on network). U.FL is a tiny SMD coaxial connector (~2mm) that connects the PCB to an off-board antenna via a short pigtail — standard for cellular/GPS modules. Low cost (~$0.50 connector + ~$2–5 antenna). User wants this board to potentially be the final version — deferring would mean a respin to add it later.
- **SIM + microSD connector strategy (rev1 decision, 2026-07-19)**: **Deferred to sourcing.** Both combo SIM+microSD sockets (saves board space, common in phones) and separate sockets (easier to source, more placement flexibility, larger footprint) are viable. Decision will be made at BOM finalization based on reliable availability from DigiKey/Mouser/LCSC. If a combo socket is reliably in stock at a reasonable price, use it; otherwise use separate sockets. Both blocks appear in the block diagram either way.
- **USB-C connector type (formally locked 2026-07-19)**: 16-pin USB-C (USB 2.0) for the main MCU USB connector. USB FS/HS only needs D+/D- — 24-pin USB 3.x is unnecessary. Micro-USB is obsolete and not considered.

### Power
- Cellular modules can draw 2A+ peaks during transmission — battery and power management must handle this.
- **Power architecture (resolved 2026-06-28)**:
  - **+BATT (modem)**: Powered **directly from the LiPo** (3.4–4.3V matches the LiPo operating range 3.4–4.2V). No buck regulator needed — the previous "dedicated high-current buck regulator" was incorrect. The key requirement is a **separate power net** from the MCU's 3.3V rail (so modem 2A bursts don't droop the MCU rail), with substantial bulk capacitance at the module VBAT pins.
  - **3.3V system rail**: Powered from the LiPo via a **buck-boost regulator** (**TPS63021DSJR**, 3.3V fixed, 4A switches / ~3A output, LCSC C202140 — LOCKED 2026-07-19). A buck-only regulator is insufficient — the LiPo drops below 3.3V at ~40% charge, and the MCU/display/SD card need a stable 3.3V. Powers: MCU, display, SD card, codec I2S side, level shifter, fuel gauge. *(Note: docs previously referenced "TPS630201" — that was a phantom part number TI never manufactured. Corrected to TPS63021DSJR 2026-07-19. See project-log.md.)*
  - **1.8V codec rail**: Powered from the 3.3V rail via an LDO (TPS7A0218, 200mA). Low current (~10–20mA for ALC5651).
  - **Charging**: USB 5V → MCP73831 charger IC → LiPo. The charger tops up the battery; the battery handles all load currents (including 2A modem peaks). The MCP73831 (500mA) does NOT need to handle modem peaks — the battery does. For production: consider a power-path charger (e.g., BQ25895, 5A) that can supply system load + charge simultaneously; for prototype, MCP73831 is sufficient.
- **+BATT rail stability (CRITICAL)**: The SIM7600 requires VBAT to remain within tolerance (typically ±100–200 mV) **during 2A transmit bursts**. If the rail droops, the module resets mid-call. This demands:
  - ~~A dedicated high-current buck regulator for the module VBAT rail (not shared with MCU rails)~~ **RESOLVED 2026-06-28**: Direct from LiPo — no regulator. The "dedicated rail" requirement is satisfied by a separate power net (+BATT net ≠ +3.3V MCU net), not a separate regulator.
  - Substantial low-ESR bulk capacitance near the module VBAT pins (typically 100–470 µF ceramic + tantalum)
  - Short, wide PDN traces to VBAT pins
  - This is a schematic review checklist item and a PCB layout constraint.
- Battery: single-cell LiPo (3.7V nominal, 3.0–4.2V range). 1200mAh candidate gives ~45h standby.
- Charging: USB-C with a battery charger IC (MCP73831 candidate). **USB-C strongly recommended** for any new design (micro-USB is obsolete).
- **Battery fuel gauge (required for FR-4.2)**: The phone must monitor and display battery level. Selected approach: **MAX17048** I2C fuel gauge (ModelGauge, coulomb counting + voltage, ~$2.50). Shares I2C bus with ALC5651. Provides state-of-charge (%) — more accurate than ADC voltage-only (which can't track coulomb count during 2A modem bursts). Alternative: ADC voltage-only (cheaper, less accurate — no coulomb counting, ~10% error vs ~1% for fuel gauge IC).
- Battery capacity vs form factor tradeoff — flip form factor locked 2026-07-19 (two PCBs + hinge flex). Final enclosure volume TBD (Phase 7 mechanical design).
- **Standby current note (verified 2026-06-28 from datasheets)**: The SIM7600's LTE idle/DRX current is **17.5 mA** (the state where the module CAN receive incoming calls). The previously cited "3 mA" figure is deep-sleep, where the module cannot receive calls. To satisfy FR-1.2 (receive calls) and FR-4.3 (idle low-power with modem standby), the module must remain in LTE idle/DRX mode. The 24h standby target (FR-4.4) requires ~420 mAh minimum (17.5 mA × 24h) — achievable with an 800+ mAh battery with comfortable margin. All modules support `AT+CEDRXS` for eDRX cycle tuning (longer cycle = lower current, higher call setup latency). The modem dominates standby power; MCU sleep (~20 µA) is negligible. See research-notes.md modem revisit findings for comparison across modules.

### Audio
- Need microphone input and speaker output.
- The SIM7600 outputs **PCM digital audio only** (fixed: master mode, short-frame sync, 16-bit linear, 2048/4096kHz clock). No I2S mode, not configurable. See research-notes.md Codec Selection section.
- **Selected codec: Realtek ALC5651-CG** (LCSC C963633, QFN-40 5×5mm, JLC Extended — no consignment) — dual I2S/PCM audio hub codec. ~~MAX9880A (Maxim/ADI, TQFN-48)~~ **SUPERSEDED 2026-07-19** (was Mouser consignment — replaced to eliminate the last consignment part). I2S-1 accepts PCM from SIM7600 (voice, slave mode, PCM Mode A short-sync), I2S-2 accepts I2S from STM32H743 (music). Both simultaneous and asynchronous (ASRC per interface). **MCU is NOT in the voice audio path during calls.** See project-log.md 2026-07-19 Codec Swap MAX9880A→ALC5651.
- **ALC5651 supply: 1.8V analog (AVDD/DACREF/CPVDD), 1.2V digital core (internal LDO), 3.3V MICVDD.** Requires a 1.8V LDO regulator and level shifting for the MCU's 3.3V I2S lines (unidirectional — SCK, FS, SD, MCLK — simple voltage divider or TXB010x). **SIM7600 PCM lines are 1.8V — confirmed 2026-06-30** from Hardware Design Manual V1.03 (Table 32: 1.8V Digital I/O characteristics; §3.6.2 reference design wires PCM directly to codec powered by VDD_1V8, no level shifter). PCM lines connect directly to ALC5651 I2S-1 with no level shifting. DBVDD (digital I/O) set to 1.8V to match codec analog supply and SIM7600 PCM voltage.
- **Pre-PCB verification — COMPLETE 2026-07-19**: (1) **PCM short-frame sync: CONFIRMED COMPATIBLE** — ALC5651 §7.5.1 PCM Mode A (short sync, Figures 10-11) in slave mode matches SIM7600's PCM master short-frame sync (HW Design Manual V1.08 §3.6: master mode, short sync, 16-bit linear, 2048/4096kHz BCLK). (2) **Stock: AVAILABLE** — LCSC C963633, 407 in stock, JLC "Extended" (JLC sources on-demand, no consignment). (3) **1.8V supply + level shifting**: documented — 1.8V LDO from 3.3V rail, unidirectional level shifter for MCU I2S lines. SIM7600 PCM pin voltage: 1.8V confirmed (Table 32 + §3.6.2 reference design — PCM lines connect directly to ALC5651, no level shifter needed on PCM). (4) **Datasheet completeness**: Rev 0.9, 134pp — full pinout, register map, application circuit, timing, package dimensions. Sufficient for PCB design. Fallback if a blocking issue emerges later: MCU bridge with NAU8822 (see research-notes.md Codec Selection Finding 3).
- **Audio output topology**: A phone typically needs two transducers — an **earpiece** (low power, for holding to ear during a call) and a **loudspeaker** (for ringtones, speakerphone — rated 3 on wishlist). The ALC5651 has stereo headphone outputs (cap-free, 20mW/ch @ 16Ω) plus stereo line outputs and PDM output for external Class-D amplifier — can drive earpiece and loudspeaker. The specific output-to-transducer mapping is a schematic design decision.
- **Loudspeaker (rev1 decision, 2026-07-19)**: **Include both earpiece and loudspeaker on rev1.** ALC5651's stereo outputs drive both at no extra codec cost. BOM §3c already lists both. Speakerphone is rated 3 on the wishlist (nice to have) but the hardware cost is just the second transducer + routing.

### Timekeeping
- The phone needs accurate time for call history timestamps (rated 7), SMS metadata, and potentially future features.
- **Selected approach: NITZ (Network Identity and Time Zone)** — the SIM7600 can sync time from the cellular network. This avoids needing a 32.768 kHz crystal on the MCU RTC and a backup battery (coin cell/supercap) to maintain time when the main battery dies. NITZ is simpler and sufficient for this use case. If time accuracy is needed when offline (no network), revisit and add an RTC crystal + backup battery.

### Display
- **Selected display: ST7789V SPI color TFT** (2.0" 240×320, 4-wire SPI, RGB565, ~$5–8). See project-log.md 2026-06-28 Display Selection and research-notes.md Display Options section.
- **Specific panel: HS HS20HS072RX** (LCSC C5329582). **LOCKED 2026-07-19.** See project-log.md 2026-07-19 Display Panel Selection.
  - Specs: 2.0" IPS TFT, 240×RGB×320, ST7789T3 (compatible variant — same Zephyr `display_st7789v.c` driver), 4-wire SPI, 262K color. Outline 51.80×36.20×2.1mm. Active area 40.80×30.6mm.
  - FPC: 12-pin, 0.5mm pitch, ZIF plug-in type. Backlight LEDs broken out as LEDA/LEDK (not logic BLK) — enables PWM dimming. FPC cable ~20mm.
  - Sourcing: LCSC C5329582, 1,786 in stock, $3.42 qty 1. JLC-assemblable (Extended pre-order). EasyEDA footprint available.
  - Pre-PCB: verify ST7789T3 works with Zephyr `display_st7789v.c` driver. Confirm exact RST pin position from mechanical drawing.
- **Color is a hard requirement** (not a preference): the "no 5+ features blocked" principle requires color capability — photo capture (rated 6), camera preview (rated 6), video recording (rated 5) all need color. A monochrome, grayscale, or spot-color display is disqualified. **E-ink is also disqualified** — even spot-color e-ink (BWR/BWRY) can't show photos (no blue/green/gradients), and the refresh rate (~0.5–3 fps mono partial, 12–22s color full) makes camera preview impossible. True full-color e-ink (ACeP) is not available at 1.5–2.4" sizes.
- **Interface: 4-wire SPI** (SCK, MOSI, CS, DC) + RESET + backlight enable = **6 GPIO pins**. This preserves the 41-spare-GPIO margin on LQFP-144 for future ecosystem peripherals (external BT = 4 pins, modem USB = 2 pins; ~~ULPI USB HS = 12 pins~~ **dropped 2026-06-28 — modem-direct USB tethering replaces MCU USB HS, see USB/Ecosystem interconnect section**). Parallel RGB via LTDC was rejected for consuming 20–28 GPIO pins.
- **Framebuffer: 240×320 RGB565 = 150KB** — fits in the H743's 1MB internal SRAM with 850KB to spare. **No external SDRAM or FMC required.** This is a key simplification vs the LTDC path (which would need external SDRAM for comfortable double-buffering at 320×480).
- **Power**: ~30–50mA with backlight on (6mA panel + 20–40mA backlight). Backlight is PWM-dimmable and **off during standby** (per FR-4.3). The display is a use-time load, not a standby load — the modem (17.5mA LTE idle/DRX) dominates standby power. Note: the SSD1351 color OLED alternative was rejected partly on power grounds — it actually draws **more** than the TFT (~57–71mA: VCI 23–29mA + Vcc 33–42mA per datasheet) because self-emissive OLED draws current per pixel.
- **Zephyr driver**: `display_st7789v.c` is in Zephyr main tree (most mature SPI display driver); LVGL has native ST7789 support. **Pre-PCB verification**: confirm the driver works on STM32H7 with the target Zephyr version — the MIPI DBI API conversion (issue #73750) had teething issues.
- **Camera preview bandwidth**: SPI at ~40MHz gives ~15–25fps partial-frame updates at 240×320 (faster at lower preview resolution). Adequate for casual photos (rated 6), not smooth video. LTDC would be smoother but is not justified for this use case (see research-notes.md Display Options).
- **Backlight PWM**: Must be on a timer-output GPIO for dimming and power management (display off during standby).
- **Backlight driver circuit (raw panel)**: ~~Most 2.0" ST7789V panels use 4 parallel white LEDs (common anode, ~3.1V Vf, 20mA each = 80mA total). For parallel-LED panels: 3.3V rail → current-limiting resistors (one per LED or grouped) → PWM-controlled N-FET → GND. No dedicated LED driver IC needed. **Verify panel backlight configuration (parallel vs series) before PCB** — series LEDs (~12V total) would need a boost LED driver (e.g., AP3031).~~ **CONFIRMED 2026-07-19**: HS20HS072RX uses 4 parallel white LEDs, Vf 3.0V, 80mA total. 3.3V rail → current-limiting resistors → PWM-controlled N-FET → GND. No boost driver needed. The Waveshare module (item 7 in BOM) has the backlight circuit onboard; the raw panel (item 7b) does not.

### Form Factor
- **Flip/clamshell form factor LOCKED 2026-07-19.** Two PCBs connected via hinge flex cable. See project-log.md 2026-07-19 Display Panel + Flip Form Factor entry. (Supersedes 2026-06-28 "form factor deferred, single-board first" decision.)
- **Board architecture**:
  - **Main board** (base): MCU, modem, codec, keypad, battery, power (charger + buck-boost + LDO + fuel gauge), USB-C, SIM, SD, cellular/GNSS antennas, microphone, loudspeaker, level shifter, ESD protection, crystals, passives.
  - **Display daughterboard** (lid): main display panel (HS20HS072RX, 2.0" ST7789T3), outer display (EastRising ER-TFT1.14-2, 1.14" ST7789V), earpiece speaker. Trivial board (~5 components + 3 ZIF connectors). Both displays are 3.3V-only TFT — no boost converters needed on the daughterboard. **Both display panels are purchased separately from the PCB (BuyDisplay/LCSC) and assembled by the user** — the ZIF connectors are JLC-assembled on the PCB; the panels plug in post-assembly. This decouples display sourcing from PCB fab.
- **Hinge flex cable**: ~13 signals on 14-pin 0.5mm FFC (1 spare):
  - Main display SPI: SDA, SCL, CS, DC, RST (5) — shared bus with outer display
  - Display power: VCC (3.3V), GND (2)
  - Backlight: LEDA, LEDK (2) — PWM dimming via FET on main board
  - Earpiece speaker: SPK+, SPK- (2) — differential audio from ALC5651
  - Outer display: CS2, DC2 (2) — shares SPI bus (SDA/SCL/RST) with main display
- **Camera**: Out of scope for rev1. Will go in the **base** (not lid) when added — DCMI parallel bus (11 pins + 1 power) stays on main board, no hinge flex signals. No camera pins reserved in hinge flex. The 41 spare GPIO on LQFP-144 already accounts for DCMI in the GPIO budget. If camera-in-lid is ever desired later, it would need a custom FPC with ground plane (signal integrity for 50MHz parallel data) — not worth the complexity for rev1.
- **Hinge mechanism**: Deferred to Phase 7 (mechanical design). Options: salvage from existing flip phone, custom 3D printed, off-the-shelf metal hinge, or CNC machined. User has FDM/SLA/CNC access.
- **Enclosure design**: Deferred to Phase 7. 3D model in CAD, fit-check with PCBs.

### Keypad
- **Selected keypad: SMD tactile switches on custom PCB traces.** LOCKED 2026-06-28. See project-log.md 2026-06-28 Keypad Selection.
- **Specific switch part: ALPS Alpine SKQGABE010** (LCSC C115351). LOCKED 2026-07-19. See project-log.md 2026-07-19 Keypad Switch Selection.
  - Specs: 5.2×5.2×1.5mm SMD, 1.57N (160gf) operating force, 0.25mm travel, 1,000,000 cycle life, SPST-NO top-actuated gull-wing, 50mA @ 12V rating. ALPS OEM.
  - Sourcing: LCSC C115351 (41,590 in stock at LCSC, 1,344 at JLC). ~$0.089 @ 50+ qty → ~$3.50 for 40 switches (2 boards × 20 + overage).
  - KiCad library: downloaded to `pcb/phone/lib/` via easyeda2kicad (symbol `SKQGABE010`, footprint `KEY-SMD_4P-L5.2-W5.2-P3.70-LS6.4`, 3D `KEY-SMD_4P-L5.2-W5.2-H1.5-LS6.4-P3.70`).
  - Footprint-compatibility note: the SKQG series has 3.1mm, 3.4mm, and 5.0mm stem-height variants on the **same 5.2×5.2mm footprint** — if the 1.5mm/0.25mm-travel build feels too snappy, swap up without respinning the PCB.
- **Switch technology**: SMD tactile switches (e.g., C&K PTS645, ALPS SKQG class). Three options evaluated: (1) SMD tactile — selected (snappy, cheap ~$1–2 for ~20 switches, easy to source, no custom tooling); (2) conductive-rubber (silicone dome) over PCB pad pairs — phone-like feel (classic feature-phone construction) but requires custom silicone dome sheet (~$50–150 mold run); (3) membrane keypad (PET/FPC stack) — sealed but flat feel, hard to source in small qty. SMD tactile chosen for simplicity, sourcing, and alignment with the custom-PCB learning goal.
- **Key count / layout**: ~17–19 keys minimum per FR-2.1/FR-2.3 — 12 numeric (0–9, *, #) + 2 call/end + 3–5 nav (up/down/select or D-pad). 5×4 matrix (20 keys) with 1 spare.
- **GPIO**: 5×4 matrix = 9 GPIO pins (5 rows + 4 cols). Non-issue with 41 spare GPIO on LQFP-144. The matrix is identical regardless of switch technology — the schematic/GPIO allocation is unaffected by the switch choice.
- **Cost**: ~20 SMD tactile switches at ~$0.05–0.10 each = ~$1–2. (SKQGABE010 actual: ~$0.089 each → ~$1.78 for 20.)
- **Sealing**: SMD tactile switches are not dust/water sealed (unlike conductive-rubber or membrane). Acceptable for a personal prototype/daily-driver. Can be revisited with a silicone overlay sheet on top of the SMD switches if sealing becomes a requirement.
- **Washability**: SKQGABE010 datasheet marks "Non washable" — investigated and confirmed non-issue for JLC PCBA. JLC's standard flow uses no-clean flux and only washes "when applicable" (residue left on board is normal/acceptable per their after-sales FAQ). The "non washable" marking is industry-standard conservative text appearing even on IP67-rated sealed switches — it's about the wash process, not ambient moisture. No special JLC order notes needed.
- **Phase 2 prototyping**: Off-the-shelf 4×4 matrix keypad module (~$2–5) + ~6–8 loose 6×6mm tactile buttons on breadboard for call/end/nav. Electrical interface (matrix rows/cols → MCU GPIO) identical to final PCB — no firmware rework when moving to custom board.
- **Keypad feel**: Deferred to Phase 7 (mechanical/enclosure). The switch technology is locked, but keycap design, actuation force tuning, and tactile feel are mechanical-design concerns.
- **Side buttons (power, volume)**: NOT in scope of the SW1–SW20 matrix selection (2026-07-19). Would use a different switch family (side-actuated). Revisit at schematic time.

### USB / Ecosystem Interconnect
- **MCU USB: OTG_FS only (12 Mbps, built-in PHY).** Sufficient for firmware updates, file/MSC transfer, and CDC ACM debug. ~~USB HS via external ULPI transceiver (USB3300) is a board-level upgrade path preserved by LQFP-144.~~ **DROPPED 2026-06-28** — see below.
- **Ecosystem tethering uses the SIM7600's own USB 2.0 HS port (480 Mbps), not the MCU.** The modem presents itself as a USB network adapter via RNDIS (`AT+CUSBPIDSWITCH=9011,1,1`) or ECM (`=9018,1,1`), simultaneously exposing AT/ttyUSB serial ports (composite device). This bypasses the MCU entirely for tethering — no MCU USB bottleneck, no USB3300 ULPI transceiver, no Zephyr USB HS stack, no 12 ULPI GPIO pins. The MCU controls the modem via UART (CMUX+PPP); the modem's USB is dedicated to tethering. See project-log.md 2026-06-28 USB HS/ULPI Revisit and research-notes.md "USB HS / ULPI Revisit" section.
- **Do NOT populate USB3300.** The ULPI footprint is wasted board space under the modem-direct tethering architecture. The 12 ULPI pins on LQFP-144 are freed for other future use.
- **PCB routing (rev1, minimal commitment)**: Route the SIM7600 USB D+/D- to a connector footprint or test points to preserve the tethering option. MCU USB OTG_FS on the main USB-C (charge + firmware + files).
- **Future ecosystem respin**: Add an internal USB 2.0 hub (e.g., USB2514, ~$1–2) so a single USB-C presents both the modem (RNDIS for LTE) and the MCU (MSC for files) to the car module — simultaneous LTE + file access over one cable. Two USB devices cannot share one host port without a hub.
- **Pre-PCB verification**: Validate `AT+CUSBPIDSWITCH=9018,1,1` (ECM) and `=9011,1,1` (RNDIS) on the Waveshare NA-H HAT connected to a Linux host (the HAT exposes the modem USB). Confirm whether the modem can run PPP-over-UART (MCU data) simultaneously with RNDIS-over-USB (car module data) on two PDP contexts.

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
