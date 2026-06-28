# Project Log

## User Background

- Senior year Computer and Systems Engineering student.
- Experience level: between "some hardware experience" and "moderate hardware" — has worked with microcontrollers and designed a few simple PCBs.
- Wants this project to push beyond prior experience into RF, cellular comms, power management, and multi-discipline integration.
- Open to simplifying initial versions but wants the overall project to be challenging and time-consuming.
- Has access to FDM, SLA, and CNC for enclosure fabrication.

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

### 2026-06-28: Cellular Module Architecture & Selection
- **Decision**: Use Architecture A — LTE Cat 4 data module + external MCU + external audio codec (not OpenCPU, not analog-audio voice module, not premium carrier-certified module).
  - *Rationale*: Four architectures were evaluated:
    - A: Cat 4 module + MCU + codec (SIM7600/EG25-G class)
    - B: Cat 1 voice module with analog audio pins (Quectel EG912U-GL) — eliminates codec for voice, but music playback needs a separate DAC, creating two audio paths instead of one
    - C: OpenCPU/QuecPython smart module (module IS the MCU, Python firmware) — eliminates MCU/RTOS learning, which is a core project goal
    - D: Premium carrier-certified module (u-blox LARA-R6401, now Trasna) — best VoLTE/carrier support but **disqualified: 911/E911 not supported** (updated 2026-06-28 second round; originally eliminated for supply chain risk, but the 911 issue is the real disqualifier)
  - Architecture A chosen because: (1) music player goal requires a real audio DAC regardless of module, so the codec isn't redundant — it unifies voice (PCM from module) and music (I2S from MCU) into one audio path; (2) preserves full MCU + RTOS + embedded firmware learning; (3) lowest supply risk; (4) Cat 4 gives headroom for ecosystem tethering.
- **Decision**: Select SIMCom SIM7600 series as the cellular module (not Quectel EG25-G).
  - *Rationale*: SIM7600A-H (NA variant) has B66 and B71 (T-Mobile 600MHz Extended Range LTE); EG25-G lacks both. SIM7600A-H has explicit T-Mobile carrier certification; EG25-G does not. Forum evidence shows EG25-G VoLTE falls back to CS (which fails on T-Mobile since 3G shutdown) with carrier-provisioning dependencies that hobbyists can't resolve; SIM7600 has a documented, workable PDP context quirk instead. Waveshare SIM7600G-H 4G HAT provides a complete prototyping platform (NAU8810 codec, SIM slot, antennas, USB-to-UART) ready for immediate VoLTE validation — no equivalent EG25-G breakout with audio.
  - *Tradeoff*: SIM7600's IMS PDP context (cid=2 for VoLTE) can conflict with data on cid=1, requiring careful firmware management of multiple PDP contexts. This is relevant for the ecosystem goal of simultaneous VoLTE + data tethering. Manageable but a real firmware complexity item.
- **Decision**: ~~Prototyping path — Waveshare SIM7600G-H 4G HAT + Mint Mobile SIM for initial VoLTE/audio validation on a PC via USB-to-UART, before any MCU or PCB work.~~
  - **SUPERSEDED 2026-06-28**: Switched to Waveshare SIM7600NA-H 4G HAT (~$89) which has B71 + NAU8810 codec. See "Modem Revisit" decision below. The G-H HAT lacks B71 (T-Mobile 600 MHz), creating a validation gap. The NA-H HAT resolves this.
  - *Rationale*: De-risks the hardest part (VoLTE on a real US carrier) this week with zero custom hardware. HAT includes the NAU8810 codec so voice audio can be tested immediately.
- **Decision**: Final PCB will use SIM7600A-H (NA variant with B66/B71) + a codec capable of both PCM (voice from module) and I2S (music from MCU), e.g., WM8960 or NAU8810-class.
  - *Rationale*: Single codec handles both voice and music through one audio path. A-H variant gets full T-Mobile band coverage for the daily-driver goal.

### 2026-06-28: RTOS Selection
- **Decision**: Use Zephyr RTOS (not FreeRTOS).
  - *Rationale*: Every subsystem the phone needs is built into Zephyr: USB device stack (CDC ACM, CDC ECM for tethering, MSC for storage access), PPP networking over cellular modem, FatFs/LittleFS for SD card, LVGL for display, power management subsystem for battery policy, BLE stack. With FreeRTOS these would be 5+ separate third-party integrations (TinyUSB, lwIP, FatFs, LVGL, vendor BT stack) that don't always compose cleanly.
  - *Learning alignment*: User explicitly wants a challenging, time-consuming project that pushes beyond prior experience. Zephyr's devicetree + Kconfig + west + subsystems model teaches modern embedded industry practices (Linux-grade workflows) that transfer to Nordic, NXP, Intel, TI ecosystems. The steep learning curve is a feature, not a bug, for this project's goals.
  - *Ecosystem advantage*: CDC ECM (Ethernet-over-USB) is a built-in Zephyr USB function — the phone-as-USB-Ethernet-device for the car module tethering scenario is a config flag, not a from-scratch USB class implementation.
  - *Nordic native path*: nRF Connect SDK is Zephyr-based. If nRF52840 is selected for MCU, Zephyr is the native RTOS.
  - *Tradeoff*: Zephyr has a steep learning curve (devicetree, Kconfig, west build system). Expect 1-2 weeks of ramp-up before productive phone firmware work. Mitigation: complete the "Practical Zephyr" tutorial series (memfault) and Shawn Hymel's Zephyr guide before starting phone firmware.
  - *Cellular modem note*: Neither Zephyr nor FreeRTOS has ready-made SIM7600 support. Zephyr's modem subsystem (modem_chat + CMUX + PPP + pipelink) provides a real architecture to plug a SIM7600 port into; FreeRTOS Cellular Library would require building that infrastructure from scratch. This is a wash on effort but Zephyr provides better scaffolding.
- **Decision**: Adopt a "no feature blocking" principle for component selection — all features rated 5+ on the wishlist must remain achievable (hardware-capable, even if not implemented in MVP).
  - *Rationale*: Avoiding rework and respins. If a component choice blocks a 5+ feature, we'd need to swap the component later (MCU change = PCB respin + firmware rewrite). Selecting components with headroom for 5+ features costs little upfront and preserves all options.
  - *5+ features that constrain MCU selection*: USB device (8), SPI/SDIO for MicroSD (7), BLE (6), I2S/audio DAC (6), camera interface (6), color display interface (5-6), video recording processing headroom (5).

### 2026-06-28: Modem Revisit (SIM7600 Selection Review)
- **Decision**: **Stick with SIMCom SIM7600 series** — the four concerns raised in the modem revisit prompt do not collectively justify switching. Two changes adopted.
  - *Rationale*: Four concerns were researched against SIM7600, EG25-G, EG912U-GL, and LARA-R6401:
    1. **Standby power**: The docs' "3 mA sleep" figure was deep-sleep (cannot receive calls), not idle/DRX. Actual SIM7600 LTE idle/DRX current is **17.5 mA** (datasheet: SIM7600E Hardware Design V1.00 Table 26). 24h standby needs ~420 mAh — achievable with an 800+ mAh battery. The modem still dominates standby; MCU sleep (~20 µA) is negligible. EG25-G is worse (22 mA); EG912U-GL is better (14 mA) but eliminated for the two-audio-path problem; LARA-R6401 claims ~1.1 mA (unverified). This concern does not justify switching.
    2. **B71 validation gap (RESOLVED)**: Waveshare makes a **SIM7600NA-H 4G HAT** (~$89) with B71 and the same NAU8810 codec. Switching the prototyping HAT from G-H to NA-H closes the gap — B71 can be validated early without a custom PCB. B71 is supplementary in the user's area (good coverage) but cheap to validate.
    3. **Simultaneous VoLTE + data (real risk, future feature)**: Forum evidence (TinyGSM #649, LilyGO #90) shows SIM7600 PDP context conflicts (IMS cid=2 interferes with data cid=1). No clear hobbyist evidence of successful simultaneous VoLTE+data on SIM7600. EG25-G has better-documented multi-PDP support (PinePhone-proven); LARA-R6401 has best multi-PDN docs. **However**: this is a future ecosystem feature (tethering while on a call), NOT an MVP or daily-driver requirement. The MVP (make/receive calls) is unaffected. Make this the first HAT test; if it fails, it blocks a future feature, not the core phone. Fallback: EG25-G (loses B71) or LARA-R6401 (supply risk).
    4. **LGA assembly (wash)**: All candidate LTE modules are LGA — none are hand-solderable. No LTE/VoLTE module exists in a hand-friendly package. NFR-3 ("hand-solderable for prototypes") is unachievable for any LTE module. Realistic path: JLCPCB assembly for the modem section (~$57–72), hand-solder the rest.
- **Change 1**: Switch prototyping HAT from SIM7600G-H to **SIM7600NA-H** (~$89) — resolves B71 validation gap. Has B71 + NAU8810 codec + GNSS.
- **Change 2**: Make **simultaneous VoLTE + data the first HAT test** (AT command sequence in research-notes.md modem revisit findings). If it fails after genuine effort, revisit with EG25-G or LARA-R6401 as fallbacks — but only for the ecosystem tethering feature, not the MVP.
- **Carrier note**: T-Mobile/Mint is a recommendation, not a lock-in. T-Mobile is most lenient with non-certified devices on prepaid. AT&T/Verizon are stricter on IMEI whitelisting. SIM7600A-H supports bands for all three major US carriers — switching later is possible.
- **Tradeoff**: The SIM7600's PDP context management is a real firmware complexity item and simultaneous VoLTE+data is unproven. The EG25-G would be safer for the ecosystem feature but loses B71 (the original reason for choosing SIM7600). The decision is to validate on the HAT first rather than switch speculatively.
- **SUPERSEDED 2026-06-28 (same day, second round)**: The framing of simultaneous VoLTE+data as "the first HAT test" and as a real risk was overstated. The second-round re-evaluation (below) determined that (a) the PDP context conflict is specific to the `AT+NETOPEN` code path, not the CMUX+PPP path the project uses; (b) simultaneous VoLTE+data is not a requirement for any current phase; and (c) LARA-R6401 is disqualified entirely (911 not supported). See "Modem Revisit (Second Round)" decision below. The two changes (NA-H HAT, VoLTE+data testing) are retained but de-prioritized — VoLTE+data is now an informational HAT test, not a blocking one.

### 2026-06-28: Modem Revisit (Second Round — Full Re-evaluation)
- **Decision**: **SIM7600 confirmed and locked.** No alternative module justifies switching. The modem selection is resolved.
  - *Rationale*: A deeper re-evaluation examined LARA-R6401 supply chain, EC25-AF as a new candidate, the EG25-G T-Mobile VoLTE issue, and the true scope of the SIM7600 PDP context conflict.
    1. **LARA-R6401 — DISQUALIFIED (911/E911 not supported)**: The LARA-R6401 datasheet explicitly states "The 911 and E911 services are not supported." A phone that cannot call 911 is a safety issue. This is a hard disqualifier regardless of its strengths (best multi-PDN, I2S audio, ~1.1 mA idle, carrier certs). Supply risk (Trasna transition) was the initial concern but is secondary — the module is in mass production and available at DigiKey. No built-in GNSS. Small community.
    2. **EC25-AF — strong alternative, not worth switching**: T-Mobile voice certified (unlike EG25-G which is data-only), B71, optional GNSS, 911/eCall supported, multi-PDP with IMS auto-isolated. Available at DigiKey (Mini PCIe ~$60). However: no breakout with integrated codec (slower prototyping), higher idle current (23.3 mA vs 17.5 mA), and the multi-PDP advantage is irrelevant (simultaneous VoLTE+data not required). **Documented as fallback for final PCB if SIM7600 testing reveals a blocking issue.**
    3. **EG25-G T-Mobile VoLTE — clarified**: The EG25-G's VoLTE CS fallback on T-Mobile is a carrier provisioning issue (T-Mobile certifies EG25-G for data only, not voice), not a hardware limitation. The EC25-AF is the proper Quectel alternative (T-Mobile voice certified).
    4. **SIM7600 PDP context conflict — RESOLVED (not a blocker)**: The conflict is confirmed in the `AT+NETOPEN` code path only. This project uses CMUX+PPP (`ATD*99***<cid>#`), which bypasses `AT+NETOPEN` entirely. CMUX+PPP is the standard documented pattern for simultaneous data + AT commands on the SIM7600 (Linux n_gsm, RT-Thread, ESP-IDF). Whether data stays active *during* a live VoLTE call via PPP is unverified but likely (3GPP bearers should coexist). Fallback: pause data during calls — acceptable.
    5. **Simultaneous VoLTE+data — NOT a requirement**: MVP is make/receive calls. Daily driver adds SMS/contacts/menu. None need data during a call. The future ecosystem (car tethering while on a call) is the only scenario, and "pause data during call" is acceptable there too. This was incorrectly treated as a near-term constraint in the first revisit; corrected.
  - *Why SIM7600 wins*: Waveshare NA-H HAT with codec (fast prototyping), built-in GNSS, large community, lower idle current (17.5 mA vs EC25-AF's 23.3 mA), 911 supported. The one advantage EC25-AF had (better multi-PDP) addresses a need the project doesn't have.
  - *Fallback*: EC25-AF for the final PCB if SIM7600 HAT testing reveals a blocking issue. Both are Cat 4, T-Mobile voice certified, B71-capable — switching at PCB time is low-cost.
  - *Tradeoff*: The SIM7600's `AT+NETOPEN` bug is real but irrelevant to this project's CMUX+PPP architecture. Data-during-VoLTE-call is unverified via PPP; if it fails, pause data during calls. No modem switch needed.

### 2026-06-28: MCU Selection
- **Decision**: Select STM32H743 (Cortex-M7 @ 480MHz) as the MCU, in LQFP-144 package (STM32H743ZI).
  - *Rationale*: Four MCU candidates were evaluated against the "no 5+ features blocked" principle and the concurrent processing load requirement:
    - **nRF52840**: Eliminated — no camera interface (blocks photo capture 6, video 5), I2S clock accuracy problems, USB device only (no OTG), 64MHz is tight for MP3 decode.
    - **ESP32-S3**: Viable but with Zephyr USB support only 8 months old (risk for ecosystem tethering), and BLE advantage is moot since neither ESP32-S3 nor STM32 has classic BT (A2DP) — external BT module needed either way.
    - **ESP32-P4**: Most capable for multimedia (hardware H.264, MIPI camera/display) but too new — limited availability, immature Zephyr support, no built-in wireless, likely BGA-only. Too risky for first custom PCB.
    - **STM32L4R5**: Questionable on processing power — 120MHz cacheless M4 running Zephyr's full networking + USB + LVGL + audio stack concurrently is tight, especially for ecosystem tethering (PPP routing + USB CDC ECM + audio + display).
    - **STM32H743**: 480MHz Cortex-M7 with L1 cache (16KB I + 16KB D), hardware JPEG codec, USB OTG FS + HS, DCMI camera, 4x SAI audio, 2x SDMMC, LTDC display controller. Handles the worst-case concurrent load (tethering + music + UI + call) comfortably. ARM Cortex-M7 (career-relevant). Mature Zephyr support (multiple H7 boards in mainline). ~$12-15, within budget.
  - *Processing power analysis*: The real CPU demand isn't any single feature — it's the concurrent subsystem load. Worst case: ecosystem tethering (USB CDC ECM + PPP routing + potentially NAT), MP3 decode, LVGL rendering, and modem AT command management all running simultaneously. This is essentially a router + media player + UI + phone. The H7's 480MHz + L1 cache is built for this; cacheless M4 parts (L4) would struggle.
  - *Package choice (LQFP-144)*: The H743 comes in LQFP-100, -144, and -176 (all 0.5mm pitch). LQFP-100 loses USB HS (ULPI requires 12 dedicated pins that don't fit). LQFP-144 retains USB HS and all needed peripherals. LQFP-176 adds little for this project. LQFP-144 is hand-solderable with practice; JLCPCB assembly is the fallback (and will be needed for the SIM7600 LGA module regardless).
  - *Tradeoffs*: Higher power consumption (~20 µA sleep vs 0.4 µA for L4) — but modem dominates at 17,500 µA (17.5 mA LTE idle/DRX, verified 2026-06-28), so MCU sleep current is negligible. Larger package than L4. No built-in BLE — external BT module needed (same as any STM32 path, and same as ESP32-S3 for classic BT).
  - *USB HS note*: True USB High-Speed (480 Mbps) requires an external ULPI transceiver (e.g., USB3300, ~$2). Can start with USB FS (built-in PHY) for MVP and populate ULPI transceiver later for ecosystem tethering. LQFP-144 keeps this option open.
- **Decision**: Bluetooth will be added as an external module (not built into MCU).
  - *Rationale*: Neither STM32H7 nor ESP32-S3 has classic Bluetooth (A2DP for audio streaming). Both have BLE (ESP32-S3 built-in, STM32 via external module). Since an external BT module is needed for classic BT regardless of MCU choice, the STM32's lack of built-in BLE is not a disadvantage. An external BT module (e.g., BM83 for classic BT + BLE) can be added when the Bluetooth feature (rated 6) is implemented. This defers the BT component decision without blocking the feature.

### 2026-06-28: Project Kickoff
- **Decision**: Use off-the-shelf cellular module + custom MCU architecture (not designing custom modem).
  - *Rationale*: Designing a custom cellular modem is impractical. Off-the-shelf modules handle the radio protocol stack while still being challenging in PCB/firmware/mechanical design.
- **Decision**: Target LTE (not 2G/3G) for network compatibility.
  - *Rationale*: 2G and 3G networks are decommissioned or sunsetting in the US. LTE with VoLTE is the only viable long-term option.
- **Decision**: Use KiCad for PCB design.
  - *Rationale*: Open-source, well-supported, no license cost.
- **Decision**: ~~Flip/clamshell form factor with two PCBs connected via flex cable.~~
  - *Rationale*: ~~Core to the project concept. Adds mechanical and routing complexity (desired challenge).~~
  - **SUPERSEDED 2026-06-28**: Form factor deferred. Single-board first, mechanical design after electronics proven. See "Problem Definition Session" decision above. This entry is retained for history only — do not reference it as an active decision.

## Phase Breakdown & Effort Estimate

### Phase 1: Research & Component Selection (~2-3 weeks, part-time)
- Deep-dive into cellular modules, compare datasheets
- Select MCU, display, cellular module, audio components
- Order dev boards / breakout boards for initial prototyping
- Get a prepaid SIM and test module with AT commands on a breadboard
- **Deliverable**: Component shortlist + working AT command proof-of-concept on breadboard

### Phase 2: HAT-Based Prototype (~2-4 weeks, part-time)
- Validate SIM7600 VoLTE + audio on **Waveshare SIM7600NA-H 4G HAT** (~$89, has B71 + NAU8810 codec) via PC (USB-to-UART) before any MCU work
  - **First**: validate simultaneous VoLTE + data tethering (PDP context management) — critical for ecosystem. Use AT command sequence in research-notes.md modem revisit findings. If this fails, it blocks a future feature (not MVP) — see modem revisit fallback options.
  - Verify/update SIM7600 firmware to VoLTE-capable version
  - Test call audio path (NAU8810 codec on HAT)
  - Validate B71 performance (NA-H HAT has B71, unlike the G-H HAT)
- Then wire MCU (STM32H743 dev board) + HAT + display + keypad
- Write firmware: UART driver for AT commands, call state machine, basic UI
- Make a test phone call
- **Note**: The SIM7600 is LGA and cannot be breadboarded directly — the Waveshare HAT is the prototyping platform. The MCU and peripherals can be on breadboard/perfboard connected to the HAT.
- **Deliverable**: Working phone call from HAT + MCU setup

### Phase 3: Schematic Design (~2-4 weeks, part-time)
- Design full schematic in KiCad
- Power management circuit (battery charging, regulation, module power)
- Audio circuit (mic, speaker, codec or module direct)
- Display and keypad interfacing
- **Deliverable**: Complete schematic, reviewed

### Phase 4: PCB Layout (~3-5 weeks, part-time)
- Board layout (MCU, cellular module, power, keypad, SIM, mic, display, audio)
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
- Design form factor (flip, candybar, etc. — decision made by this phase)
- Design keypad integration
- 3D print / CNC iterations, fit-check with PCB
- **Deliverable**: Functional enclosure, assembled phone

### Phase 8: Integration & Testing (~2-4 weeks)
- Full assembly
- Test calls, battery life, durability
- Fix issues discovered during integration
- **Deliverable**: Working phone prototype

### Total Estimate
- **Conservative estimate**: 4-6 months working part-time (evenings/weekends)
- **Aggressive estimate**: 2-3 months with focused effort
- **Realistic estimate**: 5-8 months with natural pacing, learning curves, and iteration

### Key Risk Areas (likely to extend timeline)
1. **RF/antenna**: First PCB may have antenna issues requiring a respin.
2. **Cellular module bring-up**: Subtle AT command / VoLTE configuration issues.
3. **Mechanical/form factor**: Enclosure fit, keypad feel, 3D print/CNC iterations.
4. **Power management**: Battery life tuning, peak current handling.

## Progress Tracking

| Date | Milestone | Status |
|------|-----------|--------|
| 2026-06-28 | Project definition & documentation started | In Progress |
| 2026-06-28 | Modular ecosystem vision documented; USB interconnect constraint added to hardware selection | Done |
| 2026-06-28 | Cellular module selected: SIMCom SIM7600 (Architecture A: Cat 4 + MCU + codec) | Done |
| 2026-06-28 | RTOS selected: Zephyr (built-in USB/networking/FS/LVGL/PM subsystems) | Done |
| 2026-06-28 | MCU selected: STM32H743ZI (LQFP-144, 480MHz Cortex-M7) | Done |
| 2026-06-28 | "No 5+ features blocked" principle adopted for component selection | Done |
| 2026-06-28 | Package decision validated: LQFP-144 over LQFP-176 (GPIO budget, camera bit depth, FMC analysis) | Done |
| 2026-06-28 | Video recording analysis: 8-bit DVP sufficient for VGA@30fps raw, HD@30fps with JPEG | Done |
| 2026-06-28 | Documentation review: resolved stale open questions, marked flip decision superseded, added VBAT/standby-power/NITZ/SIM7600-firmware/codec-audio-path notes, added component checklist | Done |
| 2026-06-28 | Modem revisit: SIM7600 selection confirmed; switch prototyping HAT to SIM7600NA-H (B71 validation); VoLTE+data is first HAT test; standby power figure corrected (17.5 mA idle/DRX, not 3 mA); NFR-3 updated (LGA assembly reality) | Done |
| 2026-06-28 | Modem revisit (second round): SIM7600 **locked**. LARA-R6401 disqualified (911 not supported). EC25-AF evaluated as fallback (T-Mobile voice cert, B71, but no codec breakout). PDP conflict confirmed AT+NETOPEN-specific (project uses CMUX+PPP). Simultaneous VoLTE+data dropped as a requirement (not needed for MVP/daily driver; pause-data fallback acceptable). | Done |
