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
- Assembly shall be feasible with hand soldering for prototypes, **except the cellular module** — all LTE/VoLTE modules are LGA and require reflow or JLCPCB assembly. Realistic approach: JLCPCB assembles the modem section (~$57–72), hand-solder the rest. No LTE module exists in a hand-friendly package; this is an industry reality. (Updated 2026-06-28 per modem revisit.)

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
- **Enclosure/Form factor**: Deferred — single-board prototype first, mechanical design after electronics are proven. User has FDM, SLA, and CNC access.
- **Firmware**: Zephyr RTOS — balances concurrency needs with maintainability for a daily-driver device. See project-log.md 2026-06-28 RTOS Selection.

## Open Questions (Requirements)

- [ ] USB connector type for ecosystem interconnect: USB-C vs micro-USB (data-capable, not charge-only). USB-C strongly recommended for any new design — effectively decided (USB-C), pending formal lock.

## Resolved Questions (moved from Open)

- [x] **Bluetooth support**: Deferred to post-MVP. Will be added as an external module (e.g., BM83 for classic BT + BLE) when the Bluetooth feature (rated 6) is implemented. Neither STM32H7 nor ESP32-S3 has classic BT (A2DP), so an external module is needed regardless of MCU choice.
- [x] **MCU selection**: STM32H743ZI (LQFP-144, 480MHz Cortex-M7). See project-log.md 2026-06-28 MCU Selection.
- [x] **FreeRTOS vs Zephyr**: Zephyr RTOS. See project-log.md 2026-06-28 RTOS Selection.
- [x] **USB mode (partial)**: ~~USB FS (built-in PHY) for MVP; USB HS via external ULPI transceiver (USB3300) is a board-level upgrade path preserved by the LQFP-144 package.~~ **SUPERSEDED 2026-06-28**: USB FS (built-in PHY, 12 Mbps) is the committed MCU USB path for all MCU-originated USB (firmware, files/MSC, CDC ACM debug). USB HS via ULPI is **dropped** — no longer needed: the SIM7600's own USB 2.0 HS port (480 Mbps) does ecosystem tethering directly via RNDIS/ECM (`AT+CUSBPIDSWITCH`), bypassing the MCU. Do NOT populate USB3300. The phone (MCU) and the modem are both USB **devices** in ecosystem scenarios (car module is host); a future internal USB 2.0 hub (USB2514) presents both to the host over one cable. OTG host capability is a bonus, not a requirement. See project-log.md 2026-06-28 USB HS/ULPI Revisit.
- [x] **USB mode (device-only vs OTG)**: The phone (MCU) and modem are both USB **devices** in ecosystem scenarios — the car module is the USB host. OTG host capability on the MCU is a bonus, not a requirement. The STM32H743's OTG_FS supports device mode (sufficient for firmware, files, debug). No scenario currently requires the phone to be a USB host. See FR-6.1 and project-log.md 2026-06-28 USB HS/ULPI Revisit.
- [x] **Modem revisit (2026-06-28, first round)**: SIM7600 selection confirmed after reviewing standby power, B71 validation, simultaneous VoLTE+data, and LGA assembly. Two changes: (1) switch prototyping HAT to SIM7600NA-H (~$89, has B71 + NAU8810 codec) — resolves B71 validation gap; (2) make simultaneous VoLTE+data the first HAT test — if it fails, it blocks a future ecosystem feature (not the MVP). Standby power figure corrected: 17.5 mA idle/DRX (not 3 mA deep-sleep). NFR-3 updated to acknowledge LGA assembly reality. See project-log.md 2026-06-28 Modem Revisit.
- [x] **Modem revisit (2026-06-28, second round — LOCKED)**: SIM7600 selection **locked** after full re-evaluation. Key findings: (1) **LARA-R6401 disqualified** — 911/E911 not supported (safety disqualifier); (2) **EC25-AF evaluated** as fallback — T-Mobile voice certified, B71, but no codec breakout and higher idle current (23.3 mA); (3) **PDP context conflict is AT+NETOPEN-specific** — the project uses CMUX+PPP which bypasses it (standard pattern: Linux n_gsm, RT-Thread, ESP-IDF); (4) **simultaneous VoLTE+data is NOT a requirement** — not needed for MVP or daily driver; "pause data during call" is acceptable for the future ecosystem too. EC25-AF documented as PCB fallback if SIM7600 HAT testing reveals a blocking issue. See project-log.md 2026-06-28 Modem Revisit (Second Round).
- [x] **Codec selection (2026-06-28 — LOCKED)**: **MAX9880A** selected as audio codec (Maxim/ADI, TQFN-48, ~$1.70). Dual-port architecture: SIM7600 PCM → codec primary port (voice), STM32H743 I2S → codec secondary port (music). **MCU is NOT in the voice audio path during calls.** Key findings: (1) all common codecs (WM8960, NAU8810, NAU8822, SGTL5000, TLV320AIC3204/3104, ES8316/8388) have only ONE digital audio port — cannot accept PCM and I2S simultaneously (the original "single codec unifies voice and music" claim was false); (2) the SIM7600 outputs PCM only (fixed master mode, short-frame sync, 16-bit linear — no I2S mode); (3) the MAX9880A is the only hobbyist-accessible dual-port codec (two independent digital audio interfaces, designed for smartphones). Fallback: MCU bridge with NAU8822 if MAX9880A unavailable. Pre-PCB verification: confirm PCM short-frame sync support, stock availability, 1.8V supply level shifting. **All pre-PCB verification COMPLETE (PCM sync 2026-06-29, stock 2026-06-29, SIM7600 PCM voltage 1.8V 2026-06-30)** — no blockers found. HAT prototyping unchanged. See project-log.md 2026-06-28 Codec Selection and research-notes.md Codec Selection section.
- [x] **Display selection (2026-06-28 — LOCKED)**: **ST7789V SPI color TFT** (2.0" 240×320, 4-wire SPI, RGB565, ~$5–8). Five options evaluated: (1) ST7789V TFT — selected; (2) SSD1351 color OLED — rejected (actually higher power ~57–71mA vs TFT ~30–50mA, 3–5x cost at $15–24, 128×128 too low, not in Zephyr main tree); (3) E-ink — **DISQUALIFIED** (blocks three 5+ features: camera preview 6 at ~0.5–3fps refresh, photo capture 6 with spot-color only, video 5; true color e-ink not available at 1.5–2.4"); (4) LTDC parallel RGB — rejected (20–28 GPIO, needs external SDRAM, overkill res); (5) ST7735 1.8" — rejected (too low res). ST7789v driver (`display_st7789v.c`) is the most mature SPI display driver in Zephyr main tree with native LVGL support. 6 GPIO pins, 150KB framebuffer fits internal 1MB SRAM (no external SDRAM), color-capable (satisfies "no 5+ blocked"), lower power than the OLED alternative. Backlight PWM-dimmable/off during standby (modem dominates standby power). Pre-PCB: verify ST7789v driver on STM32H7 + target Zephyr version (MIPI DBI API conversion had teething issues). See project-log.md 2026-06-28 Display Selection and research-notes.md Display Options section.
- [x] **Keypad selection (2026-06-28 — LOCKED)**: **SMD tactile switches on custom PCB traces** for the final PCB. Three options evaluated: (1) SMD tactile switches — selected (snappy, cheap ~$1–2, easy to source, no custom tooling); (2) conductive-rubber (silicone dome) over PCB pads — phone-like feel but requires custom silicone sheet (~$50–150 mold run); (3) membrane keypad (PET stack) — sealed but flat feel, hard to source in small qty. 5×4 matrix = 9 GPIO for ~20 keys (12 numeric + 2 call/end + 3–5 nav + 1 spare). Matrix/GPIO allocation identical regardless of switch technology. Phase 2 prototyping: off-the-shelf 4×4 matrix module + loose tactile buttons (identical electrical interface, no firmware rework). Keypad feel is a Phase 7 (mechanical/enclosure) concern. See project-log.md 2026-06-28 Keypad Selection.
