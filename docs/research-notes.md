# Research Notes

## Cellular Communication Primer

### How Phone Calls Work (Simplified)

1. **Your device** (phone) communicates with a **cell tower** (base station) over a radio link using a cellular standard (GSM, UMTS, LTE, NR).
2. The cell tower connects to the carrier's **core network**, which routes the call to the recipient's carrier network, which routes to the recipient's nearest cell tower, which radios to the recipient's phone.
3. For voice, the audio is digitized, compressed with a **voice codec** (e.g., AMR for 3G/LTE), packetized, and transmitted over the air interface.
4. Your device authenticates to the network using credentials stored on the **SIM card** (which contains your IMSI, keys, etc.).

### What a Cellular Module Does

A cellular module (e.g., Quectel EC25, SIMCom SIM7600) is essentially a self-contained modem:
- Handles the entire radio protocol stack (L1/L2/L3).
- Manages network registration, authentication (via SIM), call setup/teardown.
- Exposes a control interface to your microcontroller via **AT commands** (text-based commands over UART).
- Has an audio interface for connecting microphone/speaker directly (analog or digital PCM/I2S).
- Requires an antenna (usually external, connected via U.FL connector or PCB trace).

### AT Commands — The Interface

Your MCU sends text commands to the module over UART. Examples:
```
AT              -> Module responds "OK" (basic check)
ATD+1234567890; -> Dial a number
ATA             -> Answer incoming call
ATH             -> Hang up
AT+CSQ          -> Query signal quality
AT+CREG?        -> Query network registration status
AT+CMGS="..."   -> Send SMS
```

The module sends **unsolicited result codes (URCs)** for events:
```
RING            -> Incoming call
+CMGS: <n>      -> SMS sent successfully
+CREG: 1        -> Registered on network
```

Your firmware must parse these asynchronously — the module can send URCs at any time.

### Network Generation Comparison

| Generation | Voice Tech | Status (US) | Module Cost | Complexity |
|-----------|-----------|-------------|------------|------------|
| 2G (GSM)  | Circuit-switched | **Shut down** | $5-15 | Lowest |
| 3G (UMTS) | Circuit-switched | **Shutting down** | $10-25 | Low |
| 4G (LTE)  | VoLTE | **Active** | $15-40 | Medium-High |
| 5G (NR)   | VoNR | Active (limited) | $40+ | High |

**Key insight**: For a usable phone in the US, **LTE is the realistic choice**. 2G/3G are dead or dying. LTE voice (VoLTE) is more complex but modules like the Quectel EC25/EG25-G handle the VoLTE stack internally — you still just use AT commands for call control.

### Module Candidates (Initial List)

| Module | Network | Voice | Interface | Cost | Notes |
|--------|---------|-------|-----------|------|-------|
| SIM800L | 2G only | Yes | UART | ~$5 | Cheap but 2G is dead in US |
| SIM900 | 2G only | Yes | UART | ~$10 | Same issue |
| SIM5320 | 3G | Yes | UART | ~$20 | 3G also sunsetting |
| Quectel EG25-G | LTE Cat 4 | VoLTE | UART/USB | ~$25-35 | No B66/B71 (T-Mobile 600MHz gap). T-Mobile cert is **data-only** (not voice) — VoLTE CS fallback on T-Mobile is a carrier provisioning issue, not hardware. Proven in PinePhone. Idle/DRX: 22 mA. LGA (144 pads). |
| Quectel EC25-AF | LTE Cat 4 | VoLTE | UART/USB/PCM | ~$30-60 | **NA variant with B71 + T-Mobile voice certification** (unlike EG25-G). Optional GNSS. Multi-PDP with IMS auto-isolated. Mini PCIe EVB at DigiKey (~$60), but no breakout with codec. Idle/DRX: 23.3 mA. LCC (144 pads, reflow required). **Documented alternative if SIM7600 is ever reconsidered.** |
| SIMCom SIM7600A-H | LTE Cat 4 | VoLTE | UART/USB | ~$25-35 | **SELECTED.** B66/B71, T-Mobile certified. 911/E911 supported. Built-in GNSS. Idle/DRX: 17.5 mA. LGA/LCC. |
| SIMCom SIM7600G-H | LTE Cat 4 | VoLTE | UART/USB | ~$25-35 | Global variant (B66, no B71). Waveshare G-H HAT uses this. Idle/DRX: 17.5 mA. |
| SIMCom SIM7600NA-H | LTE Cat 4 | VoLTE | UART/USB | ~$25-35 | NA variant **with B71**. **Waveshare NA-H HAT available (~$89) with NAU8810 codec — recommended prototyping platform (replaces G-H HAT).** Resolves B71 validation gap. |
| Quectel EG912U-GL | LTE Cat 1 | VoLTE | UART/USB | ~$15-20 | Analog audio pins (no codec needed for voice), but music needs separate DAC → two audio paths. LGA only, no breakout. Lowest idle/DRX: 14 mA. |
| u-blox LARA-R6401 | LTE Cat 1 | VoLTE | UART/USB/I2S | ~$31-49 | Best carrier cert (T-Mobile/AT&T/Verizon/FirstNet), B66/B71. Best multi-PDN architecture (8 contexts, IMS auto-managed). I2S audio (codec-native, cleaner than PCM). **DISQUALIFIED: 911/E911 NOT supported** (datasheet: "The 911 and E911 services are not supported"). No built-in GNSS. Supply: Trasna transition ongoing, -00B-00 EOL but -00B-01 in mass production, available at DigiKey. Small community. |

**Selected module**: SIMCom SIM7600 series (SIM7600NA-H for prototyping, SIM7600A-H for final PCB). **Decision locked 2026-06-28** after two rounds of evaluation.
- *Why not EG25-G*: Missing B66/B71 (T-Mobile Extended Range LTE). T-Mobile certification is **data-only, not voice** — the EG25-G is not T-Mobile voice-certified. Forum reports of VoLTE CS fallback on T-Mobile are a **carrier provisioning issue** (T-Mobile does not authorize IMS/VoLTE for the EG25-G's IMEI range), not a hardware limitation. The EC25-AF (below) is T-Mobile voice-certified and is the proper Quectel alternative if needed.
- *Why not EC25-AF*: Strong candidate — T-Mobile voice certified, B71, optional GNSS, 911/eCall supported, better-documented multi-PDP (IMS auto-isolated from data). However: no breakout board with integrated codec (unlike SIM7600's Waveshare NA-H HAT), requiring Quectel EVB + external codec for prototyping. Higher idle current (23.3 mA vs 17.5 mA). The multi-PDP advantage is irrelevant for this project (simultaneous VoLTE+data is not required — see below). **Documented as the fallback for the final PCB if SIM7600 testing reveals a blocking issue.**
- *Why not EG912U-GL (analog audio)*: Eliminates codec for voice, but the music player goal requires a real DAC anyway — would result in two audio paths (module analog for voice + external DAC for music) instead of one unified codec. LGA-only with no ready breakout. Has the lowest idle/DRX current (14 mA) but the two-audio-path problem disqualifies it.
- *Why not LARA-R6401*: **DISQUALIFIED — 911/E911 not supported.** The LARA-R6401 datasheet explicitly states "The 911 and E911 services are not supported." A phone that cannot call 911 is a safety issue. This is a hard disqualifier regardless of its other strengths (best multi-PDN, I2S audio, lowest idle current ~1.1 mA). Supply risk (Trasna transition) was the initial concern but is secondary to the 911 issue. No built-in GNSS.
- *SIM7600 PDP context conflict (RESOLVED — not a blocker)*: The SIM7600 has a confirmed firmware bug in the `AT+NETOPEN` code path: when the auto-created IMS context (cid=2) is active, `AT+NETOPEN` fails or misroutes data through the IMS APN (TinyGSM #649, LilyGO #90). **However, this project uses CMUX + PPP (`ATD*99***<cid>#`), not `AT+NETOPEN`.** PPP dials a specific PDP context directly, bypassing the buggy internal TCP/IP stack. CMUX+PPP is the standard documented pattern for simultaneous data + AT commands on the SIM7600 (Linux n_gsm driver, RT-Thread, ESP-IDF). Whether data stays active *during* a VoLTE call via PPP is unverified but likely (3GPP bearers should coexist). **Fallback if data pauses during calls: acceptable — pause data while on a call, resume after.** This is not a requirement for MVP or daily driver.
- **Simultaneous VoLTE+data is NOT a requirement**: The MVP is make/receive calls. The daily driver adds SMS, contacts, menu. None require data active during a call. The future ecosystem vision (car module tethering while on a call) is the only scenario that needs it, and that's post-daily-driver scope. Even then, "pause data during call" is acceptable (navigation pauses for call duration, resumes after). This was incorrectly treated as a near-term constraint in the first modem revisit; it has been corrected.
- **Firmware version gotcha**: The SIM7600 ships with various firmware versions, and **not all support VoLTE out of the box.** A firmware update via USB may be required before VoLTE works on T-Mobile. This is a practical gotcha that could block Phase 1 validation. **Add as explicit Phase 1 step**: verify/update SIM7600 firmware to a VoLTE-capable version before VoLTE testing. Note: firmware LE20B05 has a known `AT+NETOPEN` regression (LilyGo-Modem-Series #471); LE20B04 is reported working. Since the project uses PPP not NETOPEN, this regression may not apply, but worth noting.
- **B71 validation gap (RESOLVED 2026-06-28)**: ~~The Waveshare HAT uses SIM7600G-H (no B71), so B71 can't be validated on the HAT.~~ **RESOLVED**: Waveshare makes a **SIM7600NA-H 4G HAT** (~$89) with B71 and the same NAU8810 codec. Switch the prototyping HAT from G-H to NA-H to validate B71 early. B71 is supplementary in the user's area (good T-Mobile coverage) but still worth validating — the NA-H HAT makes it cheap to test. See modem revisit findings below.

### Architecture Decision (Module Category)

Four architectures were evaluated, not just module models:

| Architecture | Example | Audio | MCU/RTOS Learning | Prototyping | Selected? |
|-------------|---------|-------|-------------------|-------------|-----------|
| A: Cat 4 + MCU + codec | SIM7600 + STM32 + WM8960 | PCM→codec (voice) + I2S→codec (music), unified | Full | Waveshare HAT ready | **Yes** |
| B: Cat 1 voice module + MCU | EG912U-GL + STM32 | Module analog (voice) + external DAC (music), two paths | Full | Needs carrier board | No |
| C: OpenCPU smart module | EG912U/EC600M + QuecPython | Built-in | None (Python on module) | EVB available | No (eliminates learning goal) |
| D: Premium certified module | LARA-R6401 + STM32 + codec | I2S→codec | Full | DigiKey available | No (**911 not supported**) |

**Key insight**: The music player goal (rated 6 on wishlist) is what makes Architecture A win over B. A single codec (e.g., WM8960) handles both voice (PCM from module) and music (I2S from MCU) through one audio path. Architecture B's built-in analog audio is voice-quality only — music still needs a separate DAC, creating two audio paths and more complexity.

### SIM Cards

- Standard SIM, Micro-SIM, or Nano-SIM — module breakout boards usually accept a specific size.
- Need an **active SIM** from a carrier. For testing, a prepaid plan (e.g., T-Mobile, Mint Mobile) is cheapest.
- Some carriers require the device's IMEI to be registered. The module has a built-in IMEI.
- **Potential gotcha**: Some carriers block non-approved devices. Usually not an issue with prepaid.

## MCU Candidates

### Initial List (Historical)

| MCU | UARTs | Low Power | Cost | USB | BT | Notes |
|-----|-------|-----------|------|-----|-----|-------|
| STM32F4 series | 4-6 | Good | $5-10 | Device + OTG | Needs external | Well-supported (HAL/LL), lots of peripherals |
| STM32L4 series | 3-5 | Excellent | $5-10 | Device (some OTG) | Needs external | Low-power optimized, good for battery device |
| STM32H743 | 4-8 | Moderate | $12-15 | **FS + HS (OTG)** | Needs external | **SELECTED.** 480MHz M7 + L1 cache, HW JPEG, DCMI, 4x SAI, 2x SDMMC, LTDC |
| ESP32-S3 | 3-4 | Moderate | $4-5 | OTG FS | BLE only | 240MHz dual-core, DVP camera, LCD_CAM, 2x I2S. Zephyr USB support only 8 months old. |
| ESP32-P4 | 5 | TBD | $8-10 (est.) | **OTG HS** | None (external) | 400MHz RISC-V dual-core, MIPI-CSI/DSI, HW H.264, HW JPEG. Too new — limited availability, BGA likely. |
| nRF52840 | 2-4 | Excellent | $5-8 | Device only | BLE only | **Eliminated** — no camera interface, I2S clock issues, no USB OTG. |
| nRF52832 | 2-3 | Excellent | $4-6 | **None** | BLE only | **Eliminated** — no USB at all. |

### Final Selection Analysis

The "no 5+ features blocked" principle and concurrent processing load requirement drove the selection:

| 5+ Feature (rating) | STM32L4R5 | STM32H743 | ESP32-S3 | ESP32-P4 | nRF52840 |
|---------------------|-----------|-----------|----------|----------|----------|
| USB device/OTG (8) | ✅ FS | ✅ **FS + HS** | ✅ FS | ✅ **HS** | ✅ device only |
| MicroSD (7) | ✅ SDMMC | ✅ **2x SDMMC** | ✅ SPI/SDIO | ✅ **SDIO 3.0** | ✅ SPI |
| BLE (6) | ❌ external | ❌ external | ✅ built-in | ❌ external | ✅ built-in |
| Classic BT/A2DP (6) | ❌ external | ❌ external | ❌ external | ❌ external | ❌ external |
| I2S/audio (6) | ✅ 2x SAI | ✅ **4x SAI** | ✅ 2x I2S | ✅ **3x I2S** | ⚠️ clock issues |
| Camera (6) | ✅ DCMI | ✅ DCMI | ✅ DVP | ✅ **MIPI-CSI** | ❌ **none** |
| Color display (5-6) | ✅ LTDC | ✅ **LTDC** | ✅ LCD_CAM | ✅ **MIPI-DSI** | ✅ SPI only |
| Video recording (5) | ⚠️ tight | ✅ **HW JPEG** | ⚠️ software | ✅ **HW H.264** | ❌ **blocked** |
| MP3 decode (6) | ⚠️ tight | ✅ comfortable | ✅ comfortable | ✅ comfortable | ⚠️ tight |
| Concurrent load | ⚠️ 120MHz no cache | ✅ **480MHz + cache** | ✅ 240MHz dual | ✅ 400MHz dual | ❌ 64MHz |
| Zephyr USB maturity | ✅ | ✅ **mature** | ⚠️ 8 months | ⚠️ very new | ✅ |
| ARM architecture | ✅ | ✅ | ❌ Xtensa | ❌ RISC-V | ✅ |
| Power (sleep) | 0.4 µA | ~20 µA | 8 µA | TBD | 0.4 µA |

**Selected: STM32H743 (LQFP-144, STM32H743ZI)**

Key reasons:
1. **480MHz Cortex-M7 with L1 cache** — handles the worst-case concurrent load (ecosystem tethering: PPP routing + USB CDC ECM + MP3 decode + LVGL + modem management). The L1 cache is critical for networking/media workloads; cacheless M4 parts struggle with packet processing.
2. **No 5+ features blocked** — every feature rated 5+ is hardware-capable. Camera (DCMI), audio (4x SAI), USB (FS + HS), SD (2x SDMMC), display (LTDC), video (hardware JPEG codec).
3. **USB High-Speed** (via ULPI on LQFP-144) — important for ecosystem tethering. USB FS (12 Mbps) would bottleneck real-world LTE (20-50 Mbps). Can start with FS (built-in PHY) for MVP, add ULPI transceiver (USB3300, ~$2) later.
4. **ARM Cortex-M7** — industry-standard, career-relevant, best-documented in Zephyr.
5. **Mature Zephyr support** — multiple H7 boards in mainline Zephyr (H7B3I, H747I, H745I). USB stack well-tested on STM32.

Eliminated candidates:
- **nRF52840**: No camera interface (blocks photo 6, video 5), I2S clock accuracy problems, no USB OTG, 64MHz too tight.
- **ESP32-S3**: BLE advantage is moot (no classic BT either way, external BT needed regardless). Zephyr USB support only 8 months old — risk for ecosystem tethering. 240MHz without cache is less capable than 480MHz with cache for concurrent networking.
- **ESP32-P4**: Most capable for multimedia but too new — limited availability, immature Zephyr, no built-in wireless, likely BGA-only. Too risky for first custom PCB.
- **STM32L4R5**: 120MHz cacheless M4 is tight for the concurrent subsystem load, especially ecosystem tethering.

### Package Selection

All three packages share identical silicon — same CPU, peripherals, memory. The only difference is how many pins are brought out from the die. More pins = more GPIO available + more peripheral pins accessible simultaneously.

| Package | Size | GPIO | USB HS (ULPI) | Hand-solderable | Selected? |
|---------|------|------|---------------|-----------------|-----------|
| LQFP-100 | 14×14mm | 82 | ❌ No (ULPI pins not exposed) | ✅ Easiest | No — loses USB HS |
| LQFP-144 | 20×20mm | 106 | ✅ Yes | ⚠️ Doable | **Yes** — keeps USB HS, sufficient GPIO |
| LQFP-176 | 24×24mm | 140 | ✅ Yes | ⚠️ Large | No — overkill for this project |

All packages are 0.5mm pitch. LQFP-144 selected to preserve USB HS option. JLCPCB assembly is the fallback (and will be needed for SIM7600 LGA module regardless).

#### USB HS / ULPI Clarification

The STM32H743 has two separate USB OTG controllers on the silicon:

| Controller | Built-in PHY | Speed | External chip needed? |
|-----------|-------------|-------|----------------------|
| USB OTG_FS | Yes (Full-Speed PHY built in) | 12 Mbps | No — just D+/D- pins |
| USB OTG_HS | **No HS PHY built in** | 480 Mbps (HS) or 12 Mbps (FS) | **Yes for HS** — external ULPI transceiver (USB3300, ~$2) via 12 dedicated pins |

**USB High-Speed always requires the external ULPI chip, on any package.** The H743 does not have a built-in HS PHY. What the package determines is whether the 12 ULPI pins are even exposed:

| Package | USB OTG_FS (built-in PHY) | USB OTG_HS ULPI pins exposed | Can do USB HS? |
|---------|--------------------------|------------------------------|----------------|
| LQFP-100 | ✅ Yes | ❌ No (not enough pins) | **No — impossible** |
| LQFP-144 | ✅ Yes | ✅ Yes (12 ULPI pins available) | ✅ Yes, **with** external USB3300 |
| LQFP-176 | ✅ Yes | ✅ Yes | ✅ Yes, **with** external USB3300 |

Practical path:
- **MVP**: Use USB OTG_FS (built-in PHY, 12 Mbps, no extra chip). Fine for contacts transfer, firmware updates, basic ecosystem data.
- **Later (ecosystem tethering)**: Populate USB3300 ULPI transceiver on PCB and switch to OTG_HS (480 Mbps). Board-level change (add chip + 12 traces), no MCU change.

The 144-pin package keeps this option open. The 100-pin closes it permanently.

#### LQFP-144 vs LQFP-176 Detailed Tradeoff Analysis

**1. GPIO count: 106 vs 140 (34 extra pins on 176)**

Worst-case GPIO budget for the phone (all peripherals populated):

| Peripheral | Pins | Notes |
|-----------|------|-------|
| UART to SIM7600 | 4 | TX, RX, RTS, CTS (hardware flow control) |
| Debug UART | 2 | TX, RX |
| SAI to audio codec | 4 | SCK, FS, SD, MCLK |
| Display (SPI) | 6 | MOSI, SCK, CS, DC, RESET, backlight |
| SD card (SDMMC, 4-bit) | 6 | CMD, CLK, D0-D3 |
| USB OTG_FS | 2 | D+, D- (built-in PHY) |
| DCMI camera (8-bit) | 11 | D0-D7, HSYNC, VSYNC, PCLK |
| I2C bus | 2 | SCL, SDA (shared: codec, fuel gauge, camera SCCB) |
| Keypad matrix | 10 | ~5 cols × 4 rows for numeric + nav keys |
| Modem control | 3 | PWRKEY, RESET, STATUS |
| Charging/battery | 2 | charge status, battery enable |
| LEDs | 3 | status, notification, backlight enable |
| Power/misc | 4 | regulator enables, buttons, spare |
| **Subtotal** | **59** | |

Future additions:

| Future peripheral | Pins | Notes |
|-------------------|------|-------|
| USB OTG_HS (ULPI) | 12 | External USB3300 transceiver, for ecosystem tethering |
| External BT module | 4 | UART + power/control |
| **Subtotal** | **16** | |

**Total worst case: 75 pins.**

| Package | GPIO available | Used (75) | Spare |
|---------|---------------|-----------|-------|
| LQFP-144 | 106 | 75 | **31 spare** |
| LQFP-176 | 140 | 75 | **65 spare** |

Even with every peripheral populated (ULPI + BT + camera + keypad + everything), the 144 has 31 spare GPIO. The only scenario where the 176 helps is LTDC parallel RGB display (RGB888 = 28 pins instead of 6 for SPI), pushing total to 97 — still fits in 106 with 9 spare.

**Verdict: 31 spare GPIO on the 144 is plenty. The extra 34 pins on the 176 are unused.**

**2. Camera bit depth: 8-bit (144) vs 14-bit (176)**

"8-bit vs 14-bit" refers to the DVP bus width, not final image quality. Most camera modules output 8-bit formatted data (RGB565, YCbCr422, JPEG) regardless of sensor native bit depth. The camera module's internal ISP converts raw sensor data to these formats before sending over the 8-bit bus.

| | 8-bit DVP (LQFP-144) | 14-bit DVP (LQFP-176) |
|---|---|---|
| RGB565 photos | ✅ Full quality | Same (camera outputs 8-bit anyway) |
| JPEG photos | ✅ Full quality (OV2640/OV5640) | Same |
| Raw sensor capture | ❌ 8-bit raw only | ✅ 14-bit raw (for post-processing) |
| Real-world phone photos | Identical | Identical |

When does 10/12/14-bit raw matter? Professional/scientific imaging (astrophotography, industrial inspection, medical) where you capture raw sensor data for post-processing. For a phone camera taking casual photos (rated 6), this is irrelevant.

**Verdict: 8-bit DVP gives identical photo quality for this use case. 14-bit raw is for applications we're not building.**

**3. FMC (external memory bus): 16-bit (144) vs 32-bit (176)**

FMC (Flexible Memory Controller) is an interface for connecting external memory chips (SDRAM, PSRAM, NOR/NAND flash) to the MCU. The MCU maps external memory into its address space so code can read/write it like internal RAM.

Main use case is display framebuffers. The H743 has 1MB internal SRAM. Display framebuffer sizes:

| Display | Resolution | Color | Framebuffer size | Fits in 1MB SRAM? |
|---------|-----------|-------|-----------------|-------------------|
| Small SPI OLED | 128×64 | Mono | 1 KB | ✅ Trivially |
| Small color SPI | 240×320 | RGB565 | 150 KB | ✅ Comfortably |
| Medium color SPI | 320×480 | RGB565 | 300 KB | ✅ But eats 30% of SRAM |
| Medium parallel | 480×800 | RGB565 | 750 KB | ❌ Doesn't fit |
| Double-buffered 320×480 | 320×480 | RGB565 | 600 KB (×2) | ⚠️ Very tight |

When you need FMC + external SDRAM:
- Large parallel RGB display (480×800+) — framebuffer exceeds internal SRAM
- Double-buffering for smooth animation (two framebuffers)
- Camera preview + display simultaneously
- LVGL with large screens and many widgets (draw buffers too)

When you don't need FMC:
- Small SPI display (240×320 RGB565) — 150KB fits easily in 1MB SRAM
- Single-buffered UI — one framebuffer is enough for a phone menu system

For this phone: A phone-sized display (1.8-2.4") is typically 240×320 or 320×480. At RGB565, these fit in internal SRAM without external memory. FMC is only needed for larger displays (4"+, tablet territory) or double-buffered parallel displays.

The 144 exposes a 16-bit FMC data bus; the 176 exposes 32-bit. For SDRAM, 16-bit is the standard configuration — most SDRAM chips use a 16-bit bus. The 32-bit bus only matters for extreme memory bandwidth (high-res video processing).

**Verdict: FMC is probably not needed at all. If needed later, the 144's 16-bit FMC is sufficient.**

#### Package Selection Conclusion

Every factor favors the 144 or is a wash:

| Factor | 144 wins | 176 wins | Neither matters |
|--------|----------|----------|----------------|
| GPIO count | ✅ 31 spare is plenty | Overkill (65 spare) | |
| Camera quality | ✅ 8-bit = same photos | 14-bit raw unused | |
| FMC/external RAM | ✅ 16-bit sufficient if needed | 32-bit overkill | ✅ Probably not needed |
| Package size | ✅ 20×20mm smaller | 24×24mm larger | |
| Soldering | ✅ Fewer pins | More pins, same pitch | |
| PCB routing | ✅ Less complex | More complex | |

The 176's advantages (34 extra GPIO, 14-bit camera, 32-bit FMC) are all capabilities not needed for this project. The 144's advantages (smaller package, easier soldering, simpler routing) are tangible.

### Bluetooth Strategy

Neither STM32H7 nor ESP32-S3 has classic Bluetooth (A2DP for audio streaming). Both would need an external BT module for classic BT. Since an external module is needed regardless of MCU choice, the STM32's lack of built-in BLE is not a disadvantage. An external BT module (e.g., BM83 for classic BT + BLE) will be added when the Bluetooth feature (rated 6) is implemented. This defers the BT component decision without blocking the feature.

### Power Note

STM32H743 sleep current (~20 µA) is higher than STM32L4 (0.4 µA) or nRF52840 (0.4 µA), but this is negligible compared to the SIM7600 cellular module.

**Important distinction on modem sleep states (verified from datasheets — see modem revisit findings):**
- **Power-off (~20 µA)**: Module is off. Cannot receive calls.
- **Deep sleep / LTE sleep (~4.6 mA SIM7600, ~3 mA EG25-G, ~1.5–1.7 mA EG912U-GL)**: Lowest-power registered state. May still receive paging depending on DRX/eDRX config, but call setup latency is high. Not the primary standby state.
- **LTE idle/DRX (17.5 mA SIM7600, 22 mA EG25-G, 14 mA EG912U-GL, ~1.1 mA LARA-R6401 unverified)**: Module remains registered on the network, listens for pages on the DRX cycle. **Can receive incoming calls.** This is the relevant state for standby. All modules support `AT+CEDRXS` for eDRX cycle tuning (longer cycle = lower average current, higher call setup latency).

Standby battery life is determined by the modem in LTE idle/DRX mode, not the MCU and not the deep-sleep figure. For the SIM7600 at 17.5 mA idle: 17.5 mA × 24h = **420 mAh** minimum for 24h standby. With an 800 mAh battery, standby is ~45 hours — the 24h target (FR-4.4) is achievable with comfortable margin. The previous docs' claim that the modem dominates standby power is correct; only the cited "3 mA" figure was wrong (that's deep-sleep, not idle/DRX). The MCU sleep current (~20 µA) is ~0.1% of the modem idle current and truly negligible.

## Camera & Video Recording Analysis

### DCMI Hardware Limits (STM32H743)

- Maximum DCMI pixel clock: **80 MHz** (per AN5020; derived from AHB2 max 200MHz / 2.5 HCLK periods minimum)
- 8-bit DVP bus: **80 MB/s raw theoretical max**
- Realistic effective bandwidth: **~55-65 MB/s** (after blanking intervals, DMA contention, memory write overhead)

### Video Resolution vs Frame Rate (8-bit DVP, RGB565/YCbCr422 = 2 bytes/pixel)

| Resolution | Pixels/frame | Bandwidth @ 30fps | Feasible? |
|-----------|-------------|-------------------|-----------|
| 320×240 (QVGA) | 76,800 | 4.6 MB/s | ✅ Trivial |
| 640×480 (VGA) | 307,200 | 18.4 MB/s | ✅ Comfortable |
| 800×600 (SVGA) | 480,000 | 28.8 MB/s | ✅ Good |
| 1024×768 (XGA) | 786,432 | 47.2 MB/s | ✅ Fits |
| 1280×720 (HD) | 921,600 | 55.3 MB/s | ⚠️ Tight, ~30fps possible |
| 1280×960 | 1,228,800 | 73.7 MB/s | ❌ ~22fps max |
| 1920×1080 (FHD) | 2,073,600 | 124 MB/s | ❌ Not at 30fps raw |

**For raw RGB565/YCbCr422: 30fps is comfortable up to 1024×768, and possible at 1280×720.** Beyond that, the 8-bit bus bandwidth runs out.

### Memory Constraint (the harder limit)

Where do video frames go? Internal SRAM is 1MB.

| Resolution | RGB565 frame size | Fits in 1MB SRAM? |
|-----------|------------------|-------------------|
| 320×240 | 150 KB | ✅ Yes (6 frames fit) |
| 640×480 | 614 KB | ⚠️ Barely (1 frame, nothing else) |
| 800×600 | 960 KB | ❌ No |
| 1024×768 | 1.5 MB | ❌ No |
| 1280×720 | 1.8 MB | ❌ No |

For video *recording* (saving to SD card), frames can be streamed through a small buffer to SD without holding full frames in RAM. For video *preview* (showing on display while recording), at least one frame buffer is needed in memory.

### JPEG Compression (the escape hatch)

Camera modules like OV2640 and OV5640 have built-in JPEG compression. They output a compressed JPEG stream instead of raw pixels:

| Format | 320×240 frame | 640×480 frame | 1280×720 frame |
|--------|--------------|--------------|---------------|
| RGB565 (raw) | 150 KB | 614 KB | 1.8 MB |
| JPEG (compressed) | 10-30 KB | 30-80 KB | 80-200 KB |

With JPEG output:
- **Bandwidth drops 5-10×**: 1280×720 JPEG at 30fps = ~3-6 MB/s (trivial for the 80 MB/s bus)
- **Memory drops 10-30×**: A 1280×720 JPEG frame = ~150 KB (fits in SRAM easily)
- **SD card storage**: A 30-second 640×480 JPEG video at 30fps = ~60-120 MB (feasible)

**With JPEG, you can record 1280×720 (HD) at 30fps, or even 1920×1080 at ~15fps.** The 8-bit bus is not the bottleneck — the camera's JPEG engine output rate is.

### H7 Hardware JPEG Codec

The STM32H743 has a hardware JPEG encoder/decoder. Two paths for video recording:
1. **Camera outputs JPEG** → stream directly to SD card (lowest bandwidth, lowest CPU)
2. **Camera outputs RGB565** → H7 JPEG-encodes → save to SD (more flexibility, uses H7 JPEG codec)

### Practical Video Recording Summary

| Scenario | Max resolution @ 30fps | Bottleneck |
|----------|----------------------|------------|
| Raw RGB565 to SD card | 1024×768 | DCMI bus bandwidth |
| Camera JPEG to SD card | 1280×720 (HD) | Camera JPEG engine |
| Raw RGB565 + H7 JPEG encode | 1024×768 | DCMI + JPEG codec throughput |
| Live preview + record simultaneously | 640×480 | Memory (framebuffer + preview buffer) |

**For a phone camera, 640×480 (VGA) at 30fps is very achievable and fine for casual video clips.** 1280×720 (HD) is possible with JPEG. The 8-bit DVP bus is not a meaningful limitation — the camera modules (OV2640, OV5640) are designed for exactly this.

### Would 10/12/14-bit (LQFP-176) help with video?

Marginally. A 10-bit bus gives 100 MB/s raw instead of 80 MB/s, pushing raw RGB565 30fps limit from ~1024×768 to ~1280×960. But:
- Camera modules still output 8-bit formatted data (RGB565/JPEG) in normal use
- Memory constraint is unchanged (framebuffers don't get smaller)
- JPEG mode already handles HD regardless of bus width

**The 14-bit bus doesn't meaningfully improve video recording for this use case.**

## Display Options

| Type | Interface | Power | Cost | Notes |
|------|-----------|-------|------|-------|
| OLED (0.96"-1.3") | I2C/SPI | Low | $3-8 | Good contrast, small, easy to drive |
| TFT LCD (1.4"-1.8") | SPI | Medium | $5-10 | Color, decent resolution |
| Monochrome LCD | SPI/I2C | Very low | $3-6 | Classic phone look, very low power |

**Consideration**: A small OLED or monochrome LCD keeps power and cost down. Color TFT may be needed if camera/photo features are implemented (rated 6 on wishlist). Display choice deferred until component selection phase.

## Open Research Questions

- [ ] **RESOLVED**: Does VoLTE "just work" via AT commands, or is there significant configuration? — SIM7600 has a known IMS PDP context quirk (cid=2 conflict with cid=1 data) **specific to the `AT+NETOPEN` code path**. The project uses CMUX+PPP (`ATD*99***<cid>#`), which bypasses `AT+NETOPEN` and is the standard documented pattern for simultaneous data + AT commands. VoLTE configuration requires firmware update + `AT+voltesetting=1` + carrier IMS authorization. To validate empirically with Waveshare NA-H HAT + Mint SIM.
- [ ] **RESOLVED**: Can we use the module's built-in audio path or do we need an external codec? — SIM7600 (LCC package) exposes PCM digital audio only, no analog pins. External codec required (e.g., WM8960, NAU8810). The EG912U-GL has analog audio but was rejected for the two-audio-path problem with music playback.
- [ ] **OPEN — revisit**: Which carriers allow VoLTE on non-certified devices with prepaid SIMs? — T-Mobile/Mint recommended (most lenient with non-certified devices on prepaid); SIM7600A-H is T-Mobile certified which helps. Not locked in — AT&T/Verizon possible but stricter IMEI whitelisting. Validate with HAT.
- [ ] What's the minimum antenna design for LTE? Can we use a small chip antenna or stamped antenna?
- [ ] **RESOLVED (2026-06-28, second round)**: Can the SIM7600 maintain simultaneous VoLTE call + data tethering? — **Not a requirement.** Simultaneous VoLTE+data is a future ecosystem feature (tethering while on a call), not needed for MVP or daily driver. The PDP context conflict is confirmed in the `AT+NETOPEN` code path only; the project uses CMUX+PPP which bypasses it. CMUX+PPP is the standard pattern for simultaneous data + AT commands (SMS, calls) on the SIM7600, proven in Linux n_gsm, RT-Thread, and ESP-IDF. Whether data stays active *during* a live VoLTE call via PPP is unverified but likely (3GPP bearers should coexist). **Fallback: pause data during calls — acceptable for all current and planned use cases.** This is no longer a modem selection factor.
- [ ] Are there any open-source cell phone projects we can reference?
- [ ] **OPEN — ecosystem impact**: Does SIM7600 GNSS work standalone or only when module is registered on network? — If GNSS requires network registration, the car module can't use phone GPS when the phone has no signal. Worth resolving early as it affects ecosystem navigation use case.
- [ ] **RESOLVED**: Which ESP32 variants have USB OTG? (ESP32-S2, ESP32-S3 have native USB; original ESP32 does not) — Moot; STM32H743 selected.
- [ ] **OPEN — revisit (HIGH PRIORITY)**: Which codec best supports both PCM (voice from SIM7600) and I2S (music from MCU) inputs? WM8960 vs NAU8810 vs others. — **Key unresolved question**: Most codecs (WM8960, NAU8810) are I2S-only with no second PCM port. Voice PCM from the SIM7600 may need to be routed through the MCU (MCU reads PCM from module, outputs I2S to codec), making the MCU a real-time audio bridge during calls. This is feasible on the H743 (4× SAI) but is a non-trivial firmware task and adds latency. The "unified audio path" claim may be partially overstated. **Resolve before committing to codec / before PCB design.** See codec revisit prompt.

## Component Checklist (BOM items not yet specified in docs)

Components that are implied by the architecture but not yet explicitly listed in any doc's BOM/component section. Add to schematic phase checklist:

| Component | Purpose | Notes |
|-----------|---------|-------|
| Nano-SIM socket | SIM card holder for SIM7600 | LGA/SMD, typically Molex 786470-3001 or similar |
| Battery fuel gauge IC | Battery level monitoring (FR-4.2) | I2C, e.g., MAX17048 or LC709203F. Listed in GPIO budget but not as a selected component. |
| 32.768 kHz crystal | Not needed (NITZ selected) | Only if RTC crystal approach is later adopted. See constraints.md timekeeping section. |
| USB-C connector | Data + charging + ecosystem interconnect | USB-C recommended over micro-USB. Connector type still TBD in requirements.md. |
| Earpiece transducer | Call audio (held to ear) | Separate from loudspeaker. See constraints.md audio topology note. |
| Loudspeaker | Ringtones, speakerphone (rated 3) | Codec has separate speaker output. |

## Modem Revisit Findings

### First Round (2026-06-28)

A revisit of the SIM7600 selection evaluated four concerns: standby power, B71 validation, simultaneous VoLTE+data, and LGA assembly. **Conclusion: stick with SIM7600, with two changes** (switch prototyping HAT to NA-H; make VoLTE+data the first HAT test). Full rationale in `docs/project-log.md` (2026-06-28 Modem Revisit).

### Second Round (2026-06-28) — Full Re-evaluation

A deeper re-evaluation examined alternative modules (LARA-R6401, EC25-AF, EG25-G carrier issue) and re-examined the PDP context conflict. **Conclusion: SIM7600 confirmed and locked.** Key findings:

#### LARA-R6401 — DISQUALIFIED (911/E911 not supported)

The LARA-R6401 was re-evaluated because its supply risk was initially overstated (Trasna transition is ongoing, -00B-01 variant is in mass production and available at DigiKey). It has excellent specs: best multi-PDN architecture (8 contexts, IMS auto-managed), I2S digital audio (codec-native, cleaner than PCM), lowest idle current (~1.1 mA), T-Mobile/AT&T/Verizon/FirstNet certified.

**However, the LARA-R6401 datasheet explicitly states: "The 911 and E911 services are not supported."** A phone that cannot call 911 is a safety issue. This is a hard disqualifier regardless of all other strengths. No built-in GNSS (would need external module). Small community (fewer hobbyist resources for troubleshooting).

Sources: u-blox LARA-R6401 datasheet (UBX-20048923); DigiKey stock verification.

#### Quectel EC25-AF — Strong alternative, but not worth switching

The EC25-AF was identified as a stronger Quectel alternative to the EG25-G:
- **T-Mobile voice certified** (unlike EG25-G which is data-only certified) — the EG25-G's VoLTE CS fallback on T-Mobile is a carrier provisioning issue, not a hardware limitation
- **B71** supported
- **Optional GNSS** (must specify when ordering)
- **911/eCall supported** (AT+QECCNUM for emergency number configuration)
- **Multi-PDP with IMS auto-isolated** — Quectel firmware keeps the IMS bearer internal and hidden from user AT commands; `AT+QIACT` only controls the data bearer. No routing conflict.
- **Available at DigiKey** (Mini PCIe ~$60, LCC module ~$30-40)

**Why not switch to EC25-AF:**
1. **No breakout board with integrated codec** — unlike SIM7600's Waveshare NA-H HAT (~$89, includes NAU8810 codec), the EC25-AF requires a Quectel EVB + separate audio codec breakout + wiring. Slower prototyping.
2. **Higher idle current** — 23.3 mA vs SIM7600's 17.5 mA (worst of all candidates).
3. **The multi-PDP advantage is irrelevant** — simultaneous VoLTE+data is not a requirement (see below). The one advantage EC25-AF had over SIM7600 addresses a need the project doesn't have.
4. **PCM audio only on Telematics version** — must order EC25-AF (not EC25-AFDL data-only).

**EC25-AF is documented as the fallback for the final PCB** if SIM7600 HAT testing reveals a blocking issue. Both are Cat 4, T-Mobile voice certified, B71-capable — switching at PCB time is low-cost.

Sources: T-Mobile certification (everythingrf.com); EC25 Series LTE Standard Spec V2.7 (quectel.com); DigiKey EC25AFA-MINIPCIE; Quectel forum (IMS registration).

#### EG25-G — T-Mobile VoLTE issue clarified

The EG25-G's VoLTE CS fallback on T-Mobile is **not a hardware limitation** — it's a carrier provisioning issue. T-Mobile certified the EG25-G for **data only, not voice**. The EG25-G's IMEI range is not authorized for IMS/VoLTE on T-Mobile's network. The EC25-AF is T-Mobile voice-certified and is the proper Quectel alternative if a Quectel module is needed.

Source: T-Mobile certifies eight Quectel LTE modules (everythingrf.com) — EG25-G listed as data-only, EC25-AF listed as data+voice.

#### SIM7600 PDP context conflict — RESOLVED (not a blocker)

**The conflict is real but confined to the `AT+NETOPEN` code path.** Detailed findings:

1. **`AT+NETOPEN` is broken with IMS active**: When VoLTE is enabled, the SIM7600 auto-creates an IMS PDP context (cid=2, APN="ims"). `AT+NETOPEN` (SIMCom's proprietary internal TCP/IP stack) then fails or misroutes data through the IMS APN. Confirmed in TinyGSM #649 (Telekom technician verified data going through "ims" APN) and LilyGO #90 (AT+NETOPEN fails with cid=2 active on Mint Mobile/T-Mobile).

2. **SIMCom provides no multi-PDP application note for SIM7600** — they have one for the older SIM5320, but nothing for SIM7600. The absence of documentation is telling.

3. **This project uses CMUX + PPP, not `AT+NETOPEN`**: PPP uses `ATD*99***<cid>#` to dial a specific PDP context directly, bypassing the internal TCP/IP stack entirely. CMUX (GSM 07.10 multiplexer) creates virtual channels over one UART — one for PPP data, one for AT commands (calls, SMS). This is the **standard documented pattern** for simultaneous data + AT commands on the SIM7600:
   - **Linux kernel n_gsm driver** (`docs.kernel.org/driver-api/tty/n_gsm.html`): explicitly describes using `ttygsm1` for SMS and `ttygsm2` for PPP data simultaneously
   - **RT-Thread CMUX package**: explicitly supports SIM7600 with "PPP + AT mode"
   - **esp_lte_modem** (ESP32/esp-idf): CMUX + PPP on SIM7600, production-proven
   - **SIM7600 AT command manual**: documents `AT+CMUX` — "Enable the multiplexer over the UART... commands while maintaining data connection"

4. **Whether data stays active *during* a live VoLTE call via PPP is unverified** — no hobbyist has specifically tested and reported this. In standard 3GPP, the bearers should coexist (QCI=5 for IMS, QCI=9 for data, QCI=1 for voice media are separate bearers). But "should" is not "confirmed."

5. **Firmware version dependency**: LE20B05 has a known `AT+NETOPEN` regression (LilyGo-Modem-Series #471); LE20B04 is reported working. Since the project uses PPP not NETOPEN, this regression may not apply.

**Conclusion**: The PDP context conflict is in a code path the project doesn't use. The path the project does use (CMUX+PPP) is the documented, production-proven approach. Even in the worst case (data pauses during a VoLTE call), this is acceptable — see below.

#### Simultaneous VoLTE+data — NOT a requirement

This was the key insight of the second round. Simultaneous VoLTE+data was being treated as a near-term constraint driving modem selection. It isn't:

- **MVP**: make/receive voice calls. No data needed during a call.
- **Daily driver**: calls + contacts + SMS + basic menu. SMS works over the signaling channel, not a data PDP context. No simultaneous voice+data needed.
- **Future ecosystem (car module tethering)**: the only scenario that needs simultaneous voice+data. But even here, "pause data during call" is acceptable — navigation pauses for the call duration and resumes after. This is a minor inconvenience, not a blocker. Many real phones did this for years.
- The wishlist rates tethering a 6 ("strong want — keep hardware options open"), not a 9 ("must have for MVP"). The ecosystem is explicitly post-daily-driver scope.

**Dropping simultaneous VoLTE+data as a selection criterion removes the SIM7600's one real weakness** (the PDP context conflict) and makes the EC25-AF's one real advantage (better multi-PDP) irrelevant. The SIM7600's advantages (Waveshare NA-H HAT with codec for fast prototyping, built-in GNSS, large community, lower idle current) are all real and immediate.

**Fallback**: If PPP+VoLTE coexistence is tested on the HAT and fails, pause data during calls. This costs nothing for MVP/daily-driver and only a minor inconvenience for the future ecosystem. No modem switch needed.

#### Final Modem Comparison Matrix

| Factor | SIM7600NA-H | LARA-R6401 | EC25-AF | EG25-G |
|--------|-------------|------------|---------|--------|
| VoLTE T-Mobile cert | ✓ | ✓ | ✓ | ✗ (data-only) |
| B71 | ✓ | ✓ | ✓ | ✗ |
| 911/E911 | **✓** | **✗ (DISQUALIFIED)** | ✓ | ✓ |
| Simultaneous VoLTE+data | Via PPP (unverified, fallback=pause) | Best (8 PDN, IMS auto) | IMS auto-isolated | Unverified |
| Audio | PCM (may need MCU bridge) | I2S (codec-native) | PCM (Telematics only) | PCM |
| GNSS | Built-in ✓ | No (external needed) | Optional ✓ | Optional ✓ |
| Idle current | 17.5 mA | ~1.1 mA (unverified) | 23.3 mA (highest) | 22 mA |
| Prototyping w/ codec | **Waveshare NA-H HAT ~$89** | EVK ~$477 | EVB ~$60, no codec | PinePhone / EVB |
| Community | Large ✓ | Small ⚠️ | Quectel/PinePhone ✓ | Quectel/PinePhone ✓ |
| Cost | ~$25-35 | ~$31-49 | ~$30-60 | ~$25-35 |

**Decision: SIM7600, locked.** The 911 disqualification of LARA-R6401 and the irrelevance of simultaneous VoLTE+data remove the only reasons to consider alternatives.

### 1. Standby Power / Idle-DRX Current (RESOLVED — lower concern than expected)

The docs previously cited "3 mA sleep" to argue the modem dominates standby power. That figure is deep-sleep, NOT the idle/DRX state required for receiving calls. Actual datasheet figures:

| Module | LTE Idle/DRX (can receive calls) | Deep-sleep | Peak TX | 24h standby battery |
|--------|----------------------------------|------------|---------|---------------------|
| SIM7600A/G/NA-H | **17.5 mA** | 4.6 mA | 2A | ~420 mAh |
| EG25-G | **22 mA** | 3 mA | 1.8A (up to 3.5A) | ~528 mAh |
| EG912U-GL | **14 mA** (USB disconnected) | 1.5–1.7 mA | 2–3A | ~336 mAh |
| LARA-R6401 | **~1.1 mA** (unverified — needs full datasheet) | not found | 630 mA+ | ~26 mAh (if figure holds) |

Sources: SIM7600E Hardware Design V1.00 Table 26; EG25-G LTE Standard Spec V1.2; EG912U-GL LTE Standard Spec V1.2; LARA-R6 Product Summary (UBX-20048923).

**Conclusion**: SIM7600's real idle current (17.5 mA) is higher than the wrong 3 mA figure, but 24h standby is still very achievable (420 mAh minimum, comfortable with an 800+ mAh battery). The modem still dominates standby power; MCU sleep (~20 µA) is negligible. All modules support `AT+CEDRXS` for eDRX tuning. This concern does not justify switching. Cat 1 modules (EG912U-GL, LARA-R6401) are more power-efficient but were eliminated for other reasons (two-audio-path problem; 911 not supported for LARA-R6401).

### 2. B71 Validation Gap (RESOLVED — NA-H HAT exists)

**Key finding**: Waveshare makes a **SIM7600NA-H 4G HAT** (~$89, Amazon/eBay/Waveshare) with:
- **B71** (T-Mobile 600 MHz Extended Range LTE) — unlike the G-H HAT
- **NAU8810 audio codec** (same as the G-H HAT)
- GNSS, SIM slot, antennas, USB-to-UART

This is the recommended replacement for the discontinued SIM7600A-H HAT. **Switch the prototyping HAT from G-H to NA-H** to validate B71 early without a custom PCB.

B71 importance: load-bearing for rural/indoor T-Mobile coverage, supplementary in urban areas. User reports good coverage in their area, so B71 is supplementary but still worth validating (the NA-H HAT makes it cheap). Check T-Mobile coverage map for areas you frequent.

Other B71-capable modules with breakouts: Quectel EC25-AF (mini PCIe, ~$160–190 with EVB kit) — more expensive than the NA-H HAT.

### 3. Simultaneous VoLTE + Data (REAL RISK — test first, affects future feature only)

**Evidence found:**
- TinyGSM #649: With Telekom SIM, PDP context cid=2 (APN "ims") is auto-created and used for data instead of cid=1, breaking data. Workaround: set cid=2 in TinyGSM, but this broke Vodafone compatibility.
- LilyGO T-SIM7600X #90: `AT+NETOPEN` fails with both cid=1 and cid=2 active. Deleting cid=2 (`AT+CGDCONT=2`) allowed data to work. Confirms IMS context interferes with data.
- No clear hobbyist-community evidence of successful simultaneous VoLTE + data on SIM7600.
- One forum report (circuitsonline.net) of SIM7600 falling back to 3G/2G for voice (CSFB) rather than true VoLTE — could be firmware/config issue, not confirmed as hardware limitation.

**Comparison:**
- EG25-G: Better-documented multi-PDP support. Quectel forum confirms multi-PDP is possible "provided modem, firmware, and network/operator all support it." Proven in PinePhone (real-world VoLTE). Carrier provisioning is critical (IMS must be authorized on SIM).
- LARA-R6401: Explicit multi-PDN support documented (LARA-R6-L6 Linux Integration App Note). Designed for LTE-only VoLTE (no CSFB). Best architecture for simultaneous voice+data.
- EG912U-GL: VoLTE supported, but simultaneous operation documentation sparse.

**Important framing**: Simultaneous VoLTE + data is a **future ecosystem feature** (tethering while on a call), NOT an MVP or daily-driver requirement. The MVP is make/receive calls. Even if SIM7600 can't do simultaneous voice+data, it's still a valid phone module — only the ecosystem tethering-while-on-a-call scenario is blocked.

**AT command test sequence (run on HAT — use PPP, not AT+NETOPEN):**
```
# Phase 1: VoLTE validation (no data)
AT+SIMCOMATI                               # Check firmware version (note LE20B04 vs LE20B05)
AT+voltesetting=1                          # Enable VoLTE
AT+cnv=/nv/item_files/modem/mmode/ue_usage_setting,1,01,1
AT+CGDCONT?                                # Check existing PDP contexts (cid=1 data, cid=2 IMS auto-created)
AT+CNSMOD?                                 # Verify registered on LTE (mode 8), not CSFB to 3G/2G
ATD<phone_number>;                         # Place VoLTE call
AT+CLCC                                    # Call status
AT+CNSMOD?                                 # Verify still on LTE during call (not CSFB)
ATH                                        # Hang up

# Phase 2: Data via PPP (bypasses AT+NETOPEN bug)
AT+CMUX=0                                  # Enable CMUX multiplexer
# On CMUX channel 1: AT commands (calls, SMS)
# On CMUX channel 2: PPP dial
ATD*99***1#                                # PPP dial cid=1 (data context, NOT cid=2 IMS)
# PPP link established — test data connectivity

# Phase 3: Simultaneous VoLTE + data (informational, not blocking)
# While PPP is active on channel 2:
ATD<phone_number>;                         # Place VoLTE call on channel 1
# Test if data still flows on PPP channel during call
# If data pauses: acceptable — resume after call ends
ATH                                        # Hang up
# If data resumes after call: simultaneous works (bonus)
# If data does not resume: reconnect PPP
```

**Fallback if PPP+VoLTE fails**: Pause data during calls. This is acceptable for all current and planned use cases (MVP, daily driver, and future ecosystem). No modem switch needed.

### 4. LGA Assembly (WASH — all candidates are LGA)

Every LTE module in the candidate set is LGA — none are hand-solderable with an iron:

| Module | Package | Dimensions | Pins |
|--------|---------|------------|------|
| SIM7600A-H | LCC/LGA | 30×30×2.9mm | 87 |
| EG25-G | LGA | 29×32×2.4mm | 144 |
| EC25-AF | LCC | 29×32×2.4mm | 144 |
| EG912U-GL | LGA | 25×29×2.4mm | 126 |
| LARA-R6401 | LGA | 24×26×2.6mm | 100 |

No LTE/VoLTE module exists in a hand-friendly (castellated/through-hole) package — this is an industry reality, not SIM7600-specific. NFR-3 ("hand-solderable for prototypes") is unachievable for ANY LTE module and must be updated.

**Realistic path**: JLCPCB assembly for the modem section (~$57–72: module + $3 extended fee + ~$24 fixture + solder joints), hand-solder the rest. Hybrid assembly is supported by JLCPCB. Alternative: M.2 socket variant (module plugs in, no reflow) at cost of larger footprint. SIM7600A-H is not directly in JLCPCB's library (would need consignment); SIM7600E and SIM7600G-H-PCIE are stocked.
