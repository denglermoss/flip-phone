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
| SIMCom SIM7600NA-H | LTE Cat 4 | VoLTE | UART/USB | ~$31 (JLC pre-order) | **SELECTED.** B66/B71, T-Mobile certified. 911/E911 supported. Built-in GNSS. Idle/DRX: 17.5 mA. LCC+LGA 119-pin. **Part name corrected 2026-07-19** — "SIM7600A-H" was a misnomer; actual product code is SIM7600NA-H (North America H-series). |
| SIMCom SIM7600G-H | LTE Cat 4 | VoLTE | UART/USB | ~$25-35 | Global variant (B66, no B71). Waveshare G-H HAT uses this. Idle/DRX: 17.5 mA. |
| SIMCom SIM7600NA-H | LTE Cat 4 | VoLTE | UART/USB | ~$25-35 | NA variant **with B71**. **Waveshare NA-H HAT available (~$89) with NAU8810 codec — recommended prototyping platform (replaces G-H HAT).** Resolves B71 validation gap. |
| Quectel EG912U-GL | LTE Cat 1 | VoLTE | UART/USB | ~$15-20 | Analog audio pins (no codec needed for voice), but music needs separate DAC → two audio paths. LGA only, no breakout. Lowest idle/DRX: 14 mA. |
| u-blox LARA-R6401 | LTE Cat 1 | VoLTE | UART/USB/I2S | ~$31-49 | Best carrier cert (T-Mobile/AT&T/Verizon/FirstNet), B66/B71. Best multi-PDN architecture (8 contexts, IMS auto-managed). I2S audio (codec-native, cleaner than PCM). **DISQUALIFIED: 911/E911 NOT supported** (datasheet: "The 911 and E911 services are not supported"). No built-in GNSS. Supply: Trasna transition ongoing, -00B-00 EOL but -00B-01 in mass production, available at DigiKey. Small community. |

**Selected module**: SIMCom SIM7600 series — **SIM7600NA-H** for both prototyping (Waveshare HAT) and the final PCB. **Decision locked 2026-06-28** after two rounds of evaluation. *(Part name corrected 2026-07-19: "SIM7600A-H" was a misnomer — SIMCom's actual product code is `SIM7600NA-H`. The old LCSC link C2995537 pointed to the non-H `SIM7600A`, a different 87-pin LCC product. See project-log.md 2026-07-19.)*
- *Why not EG25-G*: Missing B66/B71 (T-Mobile Extended Range LTE). T-Mobile certification is **data-only, not voice** — the EG25-G is not T-Mobile voice-certified. Forum reports of VoLTE CS fallback on T-Mobile are a **carrier provisioning issue** (T-Mobile does not authorize IMS/VoLTE for the EG25-G's IMEI range), not a hardware limitation. The EC25-AF (below) is T-Mobile voice-certified and is the proper Quectel alternative if needed.
- *Why not EC25-AF*: Strong candidate — T-Mobile voice certified, B71, optional GNSS, 911/eCall supported, better-documented multi-PDP (IMS auto-isolated from data). However: no breakout board with integrated codec (unlike SIM7600's Waveshare NA-H HAT), requiring Quectel EVB + external codec for prototyping. Higher idle current (23.3 mA vs 17.5 mA). The multi-PDP advantage is irrelevant for this project (simultaneous VoLTE+data is not required — see below). **Documented as the fallback for the final PCB if SIM7600 testing reveals a blocking issue.**
- *Why not EG912U-GL (analog audio)*: Eliminates codec for voice, but the music player goal requires a real DAC anyway — would result in two audio paths (module analog for voice + external DAC for music) instead of one unified codec. LGA-only with no ready breakout. Has the lowest idle/DRX current (14 mA) but the two-audio-path problem disqualifies it.
- *Why not LARA-R6401*: **DISQUALIFIED — 911/E911 not supported.** The LARA-R6401 datasheet explicitly states "The 911 and E911 services are not supported." A phone that cannot call 911 is a safety issue. This is a hard disqualifier regardless of its other strengths (best multi-PDN, I2S audio, lowest idle current ~1.1 mA). Supply risk (Trasna transition) was the initial concern but is secondary to the 911 issue. No built-in GNSS.
- *SIM7600 PDP context conflict (RESOLVED — not a blocker)*: The SIM7600 has a confirmed firmware bug in the `AT+NETOPEN` code path: when the auto-created IMS context (cid=2) is active, `AT+NETOPEN` fails or misroutes data through the IMS APN (TinyGSM #649, LilyGO #90). **However, this project uses CMUX + PPP (`ATD*99***<cid>#`), not `AT+NETOPEN`.** PPP dials a specific PDP context directly, bypassing the buggy internal TCP/IP stack. CMUX+PPP is the standard documented pattern for simultaneous data + AT commands on the SIM7600 (Linux n_gsm driver, RT-Thread, ESP-IDF). Whether data stays active *during* a VoLTE call via PPP is unverified but likely (3GPP bearers should coexist). **Fallback if data pauses during calls: acceptable — pause data while on a call, resume after.** This is not a requirement for MVP or daily driver.
- **Simultaneous VoLTE+data is NOT a requirement**: The MVP is make/receive calls. The daily driver adds SMS, contacts, menu. None require data active during a call. The future ecosystem vision (car module tethering while on a call) is the only scenario that needs it, and that's post-daily-driver scope. Even then, "pause data during call" is acceptable (navigation pauses for call duration, resumes after). This was incorrectly treated as a near-term constraint in the first modem revisit; it has been corrected.
- **Firmware version gotcha**: The SIM7600 ships with various firmware versions, and **not all support VoLTE out of the box.** A firmware update via USB may be required before VoLTE works on T-Mobile. This is a practical gotcha that could block Phase 1 validation. **Add as explicit Phase 1 step**: verify/update SIM7600 firmware to a VoLTE-capable version before VoLTE testing. Note: firmware LE20B05 has a known `AT+NETOPEN` regression (LilyGo-Modem-Series #471); LE20B04 is reported working. Since the project uses PPP not NETOPEN, this regression may not apply, but worth noting.
  - **UPDATE 2026-07-12 (HAT bring-up)**: The Waveshare SIM7600NA-H HAT received ships with firmware **LE20B02SIM7600NA** — older than both LE20B04 (reported working) and LE20B05 (known regression). VoLTE support on LE20B02 is **unverified** — needs testing with `AT+voltesetting=1`. If VoLTE fails, firmware update is needed via SIMCom's QDL tool (SIM7500_SIM7600_QDL V1.41, run as admin). Firmware upgrade video: https://www.waveshare.net/wiki/SIM7600-Firmware-upgrade-Video. The HAT has solder pads for forced boot mode (short-circuit to enter QDL mode if normal flash fails).
  - **UPDATE 2026-07-12 (VoLTE VALIDATED)**: **LE20B02 supports VoLTE — no firmware update needed.** `AT+voltesetting=1` returned OK. PDP contexts auto-created: cid=1 "fast.t-mobile.com" (data), cid=2 "ims" (VoLTE), cid=3 "sos" (911), cid=4 "tmus". `AT+CNSMOD: 0,8` confirms LTE mode (not CSFB). Test call `ATD<number>;` connected successfully — `VOICE CALL: BEGIN` → `VOICE CALL: END: 000006`. VoLTE is working on Mint/T-Mobile with the Waveshare NA-H HAT. The documented firmware version concern (LE20B04 vs LE20B05) is moot for this project — LE20B02 works and there's no reason to update (no NETOPEN regression risk since project uses CMUX+PPP; VoLTE works; `AT+CPSI?` not supported but `AT+COPS?` suffices for diagnostics).
  - **HAT connection notes (2026-07-12)**: The AT command port is the **SIM7600's own USB port** (requires SIMCom USB drivers V1.0.2), NOT the CP210x UART bridge port (which did not respond to AT commands). The SIM7600 enumerates multiple virtual COM ports — use the lowest-numbered one for AT commands. COM port numbers are dynamic per USB connection (fix via Device Manager → Port Settings → Advanced → COM Port Number). PuTTY serial at 115200 baud, CR line endings (not CR+LF). The new-version HAT auto-powers on (PWR/3V3 jumper shorted by default) — no PWRKEY button press needed. `AT+CPSI?` returns ERROR on LE20B02 (not supported on this firmware version).
- **B71 validation gap (RESOLVED 2026-06-28)**: ~~The Waveshare HAT uses SIM7600G-H (no B71), so B71 can't be validated on the HAT.~~ **RESOLVED**: Waveshare makes a **SIM7600NA-H 4G HAT** (~$89) with B71 and the same NAU8810 codec. Switch the prototyping HAT from G-H to NA-H to validate B71 early. B71 is supplementary in the user's area (good T-Mobile coverage) but still worth validating — the NA-H HAT makes it cheap to test. See modem revisit findings below.

### Architecture Decision (Module Category)

Four architectures were evaluated, not just module models:

| Architecture | Example | Audio | MCU/RTOS Learning | Prototyping | Selected? |
|-------------|---------|-------|-------------------|-------------|-----------|
| A: Cat 4 + MCU + codec | SIM7600 + STM32 + MAX9880A | PCM→codec primary (voice) + I2S→codec secondary (music), dual-port | Full | Waveshare HAT ready | **Yes** |
| B: Cat 1 voice module + MCU | EG912U-GL + STM32 | Module analog (voice) + external DAC (music), two paths | Full | Needs carrier board | No |
| C: OpenCPU smart module | EG912U/EC600M + QuecPython | Built-in | None (Python on module) | EVB available | No (eliminates learning goal) |
| D: Premium certified module | LARA-R6401 + STM32 + codec | I2S→codec | Full | DigiKey available | No (**911 not supported**) |

**Key insight**: The music player goal (rated 6 on wishlist) is what makes Architecture A win over B. The selected codec (**MAX9880A**, see Codec Selection section below) has two independent digital audio ports — voice (PCM from module on primary port) and music (I2S from MCU on secondary port) — so both run simultaneously through one codec without the MCU in the voice path. Architecture B's built-in analog audio is voice-quality only — music still needs a separate DAC, creating two audio paths and more complexity. **Note**: The original claim that common codecs like WM8960 "unify" PCM and I2S into one audio path was **incorrect** — WM8960, NAU8810, NAU8822, and all common single-port codecs can only accept one digital audio stream at a time. The MAX9880A (dual-port) is what makes the unified architecture actually work. See Codec Selection / Audio Path Architecture section.

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
1. **480MHz Cortex-M7 with L1 cache** — handles the worst-case concurrent load (~~ecosystem tethering: PPP routing + USB CDC ECM~~ [superseded 2026-06-28 — tethering now runs on the modem's USB, not the MCU; MCU load for tethering is ~zero] + MP3 decode + LVGL + modem management). The L1 cache is critical for networking/media workloads; cacheless M4 parts struggle with packet processing.
2. **No 5+ features blocked** — every feature rated 5+ is hardware-capable. Camera (DCMI), audio (4x SAI), USB (FS + HS), SD (2x SDMMC), display (LTDC), video (hardware JPEG codec).
3. ~~**USB High-Speed** (via ULPI on LQFP-144) — important for ecosystem tethering. USB FS (12 Mbps) would bottleneck real-world LTE (20-50 Mbps). Can start with FS (built-in PHY) for MVP, add ULPI transceiver (USB3300, ~$2) later.~~ **SUPERSEDED 2026-06-28**: USB HS via ULPI is no longer needed — the SIM7600's own USB 2.0 HS port (480 Mbps) does ecosystem tethering directly via RNDIS/ECM, bypassing the MCU. MCU USB OTG_FS (12 Mbps) is sufficient for firmware/files/debug. USB3300 dropped. See "USB HS / ULPI Revisit" section. (The LQFP-144 package is still retained for its GPIO margin — now 41 spare after dropping ULPI — camera bit depth, and peripheral fit.)
4. **ARM Cortex-M7** — industry-standard, career-relevant, best-documented in Zephyr.
5. **Mature Zephyr support** — multiple H7 boards in mainline Zephyr (H7B3I, H747I, H745I). USB stack well-tested on STM32.

Eliminated candidates:
- **nRF52840**: No camera interface (blocks photo 6, video 5), I2S clock accuracy problems, no USB OTG, 64MHz too tight.
- **ESP32-S3**: BLE advantage is moot (no classic BT either way, external BT needed regardless). Zephyr USB support only 8 months old — risk for ecosystem tethering. 240MHz without cache is less capable than 480MHz with cache for concurrent networking.
- **ESP32-P4**: Most capable for multimedia but too new — limited availability, immature Zephyr, no built-in wireless, likely BGA-only. Too risky for first custom PCB.
- **STM32L4R5**: 120MHz cacheless M4 is tight for the concurrent subsystem load, especially ecosystem tethering.

### Package Selection

All three packages share identical silicon — same CPU, peripherals, memory. The only difference is how many pins are brought out from the die. More pins = more GPIO available + more peripheral pins accessible simultaneously.

| Package | Size | GPIO | ~~USB HS (ULPI)~~ | Hand-solderable | Selected? |
|---------|------|------|---------------|-----------------|-----------|
| LQFP-100 | 14×14mm | 82 | ~~❌ No (ULPI pins not exposed)~~ | ✅ Easiest | No — ~~loses USB HS~~ insufficient GPIO margin |
| LQFP-144 | 20×20mm | 106 | ~~✅ Yes~~ | ⚠️ Doable | **Yes** — ~~keeps USB HS~~ 41 spare GPIO (margin for future peripherals), sufficient GPIO |
| LQFP-176 | 24×24mm | 140 | ~~✅ Yes~~ | ⚠️ Large | No — overkill for this project |

All packages are 0.5mm pitch. ~~LQFP-144 selected to preserve USB HS option.~~ **SUPERSEDED 2026-06-28**: LQFP-144 selected for its GPIO margin (41 spare after dropping ULPI), camera bit depth, and overall peripheral fit — not USB HS (ULPI dropped, see "USB HS / ULPI Revisit" section). JLCPCB assembly is the fallback (and will be needed for SIM7600 LGA module regardless).

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

Practical path (updated 2026-06-28 per USB HS/ULPI Revisit — see "USB HS / ULPI Revisit" section below):
- **MVP and daily driver**: Use the MCU's USB OTG_FS (built-in PHY, 12 Mbps, no extra chip). Fine for firmware updates, file/contacts transfer, CDC ACM debug.
- **Ecosystem tethering (future)**: **Use the SIM7600's own USB 2.0 HS port** (480 Mbps) directly to the car module via RNDIS/ECM (`AT+CUSBPIDSWITCH`). The modem becomes the USB network adapter — **no MCU bridging, no USB3300 ULPI transceiver, no Zephyr USB HS stack needed.** The MCU's USB speed is irrelevant for tethering.
- ~~Populate USB3300 ULPI transceiver on PCB and switch to OTG_HS (480 Mbps).~~ **SUPERSEDED 2026-06-28**: Dropped. The modem-direct USB tethering path (Finding 2) eliminates the need for MCU USB HS. USB3300 footprint is wasted board space; do not populate. The 12 ULPI pins are freed for other future use. Zephyr STM32H7 ULPI support is viable (mainline since Dec 2022) but no longer needed for this project. See "USB HS / ULPI Revisit" section.

The 144-pin package is retained (chosen for its GPIO margin — 41 spare after dropping ULPI — camera bit depth, and overall peripheral fit — not ULPI alone). The 100-pin closes the ULPI option permanently, but ULPI is no longer a project requirement.

#### LQFP-144 vs LQFP-176 Detailed Tradeoff Analysis

**1. GPIO count: 106 vs 140 (34 extra pins on 176)**

Worst-case GPIO budget for the phone (all peripherals populated):

| Peripheral | Pins | Notes |
|-----------|------|-------|
| UART to SIM7600 | 4 | TX, RX, RTS, CTS (hardware flow control) |
| Debug UART | 2 | TX, RX |
| SAI to audio codec (I2S) | 4 | SCK, FS, SD, MCLK — MCU→MAX9880A secondary port (music). Voice PCM goes SIM7600↔MAX9880A primary port directly, NOT through MCU. |
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
| ~~USB OTG_HS (ULPI)~~ | ~~12~~ | ~~External USB3300 transceiver, for ecosystem tethering~~ **DROPPED 2026-06-28** — modem-direct USB tethering replaces MCU USB HS (see USB HS/ULPI Revisit). 12 pins freed. |
| Modem USB (D+/D-) | 2 | SIM7600 USB 2.0 HS port routed to ecosystem connector footprint/test points (rev1); future internal USB hub for tethering |
| External BT module | 4 | UART + power/control |
| **Subtotal** | **6** | ~~16~~ (was 16 with ULPI; now 6 with modem USB + BT) |

**Total worst case: 65 pins.** (Was 75 with ULPI; dropped to 65 after USB HS/ULPI Revisit replaced 12-pin ULPI with 2-pin modem USB.)

| Package | GPIO available | Used (65) | Spare |
|---------|---------------|-----------|-------|
| LQFP-144 | 106 | 65 | **41 spare** |
| LQFP-176 | 140 | 65 | **75 spare** |

Even with every peripheral populated (modem USB + BT + camera + keypad + everything), the 144 has 41 spare GPIO. The only scenario where the 176 helps is LTDC parallel RGB display (RGB888 = 28 pins instead of 6 for SPI), pushing total to 87 — still fits in 106 with 19 spare.

**Verdict: 41 spare GPIO on the 144 is plenty. The extra 34 pins on the 176 are unused.** (Previously 31 spare with ULPI; now 41 spare after dropping ULPI.)

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
| GPIO count | ✅ 41 spare is plenty (was 31 with ULPI; +10 after dropping ULPI 2026-06-28) | Overkill (75 spare) | |
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

**Decision (2026-06-28 — LOCKED): ST7789V SPI color TFT, 2.0" 240×320, RGB565.** See project-log.md 2026-06-28 Display Selection. The display must be color-capable per the "no 5+ features blocked" principle (photo capture rated 6, camera preview rated 6, video recording rated 5 — a monochrome display would block these).

### Options Evaluated

| Option | Interface | Power (active) | Cost | GPIO | Framebuffer | Zephyr LVGL | Camera preview | Phone UI |
|--------|-----------|----------------------|------|------|-------------|-------------|----------------|----------|
| **SPI color TFT (ST7789V) — SELECTED** | 4-wire SPI | ~30–50mA (6mA panel + 20–40mA backlight; backlight off during standby) | ~$5–8 | **6** (MOSI, SCK, CS, DC, RESET, BL) | 240×320 RGB565 = 150KB → fits 1MB SRAM | **Best.** `display_st7789v.c` in Zephyr main tree; LVGL native ST7789. Widely used. | ~15–25fps partial updates @ 240×320; faster at lower res. Adequate for rated-6 casual photos. | 240×320 @ 2.0" ≈ 200 PPI. Standard feature-phone res. Readable. |
| SPI color OLED (SSD1351) | 4-wire SPI | **~57–71mA** (VCI 23–29mA + Vcc 33–42mA; self-emissive, no backlight — actually HIGHER than TFT) | **~$15–24** | 6 | 128×128 RGB565 = 32KB (trivial) | **Not in main tree.** Issue #88923 open; only out-of-tree driver (nktsb/zephyr-ssd1351-driver). SSD1327 (grayscale) is in Zephyr but NOT color. | 128×128 too low for useful preview. | 128×128 @ 1.5" ≈ 128 PPI. Cramped. Early-2000s res. |
| E-ink (B/W or spot-color BWRY) | SPI | Ultra-low (bistable: ~0mA static; ~9mW refresh) | ~$5–15 | 6 | Small (e.g. 250×122 = 30KB) | Some drivers in Zephyr (SSD16xx family). Partial refresh support varies. | **BLOCKED.** ~0.3–3fps (mono partial), 12–22s (color full). Unusable for live preview. | Good for static menus (sunlight readable, bistable). But no live UI response. |
| Parallel RGB TFT via LTDC | RGB565/RGB888 parallel | ~30–50mA + SDRAM quiescent | ~$8–15 panel + SDRAM chip | **20 (RGB565) or 28 (RGB888)** | 320×480 RGB565 = 300KB (tight single-buf); 600KB double-buf (very tight) → needs external SDRAM via FMC for comfort | `display_stm32_ltdc.c` in main tree; LTDC node in STM32H7 DTS. Works but less common in hobbyist use; complex devicetree (timings/porches/polarity). LVGL native LTDC. | Excellent — parallel bus + DMA2D, high bandwidth. Best preview. | 320×480 @ 2.0" ≈ 300 PPI. Sharp but overkill for feature-phone UI; more LVGL rendering work. |
| SPI TFT 1.8" 128×160 (ST7735) | 4-wire SPI | ~30–50mA | ~$4–7 | 6 | 128×160 RGB565 = 41KB (trivial) | `display_st7735` in Zephyr main tree. Mature. | 128×160 too low. | Too low resolution for usable phone UI. Eliminated. |

### Why ST7789V SPI TFT Was Selected

1. **Zephyr driver maturity is decisive.** `display_st7789v.c` is the most widely-used SPI display driver in Zephyr main tree (recently converted to MIPI DBI API — issue #73750, teething issues now resolved in main). LVGL has native ST7789 support. The LTDC driver exists but requires more complex devicetree configuration; the SSD1351 (color OLED) is not even in the main tree (out-of-tree driver only). For a first custom PCB, the path of least resistance matters.
2. **GPIO-efficient (6 pins vs 20–28 for LTDC).** Preserves the 41-spare-GPIO margin on LQFP-144 for future ecosystem peripherals — modem USB (2 pins, supports tethering rated 6) and external BT module (4 pins, supports Bluetooth rated 6). ~~ULPI USB HS (12 pins)~~ was dropped 2026-06-28 (modem-direct USB tethering replaces it — see USB HS/ULPI Revisit). LTDC's 28 pins (RGB888) would drop spare GPIO to 19, still fitting but eating the margin needed for BT and other future peripherals. RGB565 parallel (~20 pins) is better but still consumes 14 more pins than SPI for no real UI benefit at feature-phone scale.
3. **No external SDRAM needed.** 150KB framebuffer fits in internal 1MB SRAM with 850KB to spare. No FMC, no SDRAM chip, simpler PCB, lower cost, lower power. LTDC at 320×480 double-buffered (600KB) is very tight in internal SRAM and would need external SDRAM via FMC for comfortable operation.
4. **Power is acceptable — and lower than the color OLED alternative.** Backlight is PWM-dimmable and fully off during standby. The modem (17.5mA LTE idle/DRX) dominates standby power; the display is a use-time load, not a standby load. The SSD1351 color OLED actually draws **more** power during use (~57–71mA vs ~30–50mA) because self-emissive OLED draws current per pixel — for a phone UI with bright text/menus, the OLED is less efficient than a backlit TFT. The standby advantage is a wash (both near-zero when off: OLED sleep 1–5µA, TFT backlight off ~0).
5. **240×320 is the right resolution** for a feature phone — not cramped like 128×128 (OLED) or 128×160 (ST7735), not overkill like 320×480 (LTDC). Standard feature-phone resolution (Nokia S40 class).
6. **Cost is lowest** of the viable color options (~$5–8 vs ~$15–24 for color OLED).

### Why Not LTDC Parallel RGB

The only real advantage of LTDC is smoother camera preview (parallel bus + DMA2D bandwidth). This does not justify:
- 20–28 GPIO pins (vs 6) — eats the spare margin needed for future modem USB + BT (both support 6+ features) ~~and ULPI~~ (ULPI dropped 2026-06-28)
- External SDRAM for comfortable double-buffering — adds a chip, FMC routing, power, cost
- More complex Zephyr devicetree setup (display timings, porches, sync polarity, pixel clock config)
- 320×480 resolution is overkill for a feature-phone UI (menus, contacts, call screens) — more LVGL rendering work for no user benefit

Camera preview (rated 6) is "casual photos," not video. SPI at ~40MHz gives adequate ~15–25fps partial-frame updates. The LTDC advantage is real but not worth the GPIO/memory/complexity cost for this use case.

### Why Not E-ink

E-ink is **disqualified** by the "no 5+ features blocked" principle on two independent grounds:

1. **Refresh rate makes camera preview impossible.** Monochrome partial refresh (best case): ~0.3s = ~3 fps. Monochrome fast refresh: ~1.5s = ~0.67 fps. Color (BWR/BWRY) full refresh: **12–22 seconds** per frame. Camera preview (rated 6) needs ~15+ fps to be usable for framing a photo. Even the fastest monochrome partial refresh (~3 fps) gives a stuttering slideshow, not a live view. Color e-ink is orders of magnitude worse.

2. **"Color" e-ink at this size isn't actually color-capable for photos.** Small color e-ink (1.5–2.4") is **spot-color only** — black/white/red/yellow (BWRY) or black/white/red (BWR). 4 discrete colors, no blue, no green, no gradients. You cannot display a photo on this. True full-color e-ink (E Ink Gallery/ACeP) exists but starts at 6"+ and costs $100+. Not available at phone-display sizes.

This blocks **three** 5+ features:
- Photo capture (6) — can't show color photos (spot-color only, no blue/green/gradents)
- Camera preview (6) — can't show live preview (refresh rate ~0.5–3 fps)
- Video recording (5) — can't show live video

E-ink's real advantages (ultra-low power, bistable, sunlight readable) are genuine but don't outweigh blocking three 5+ features. If the wishlist ever downgrades camera/photo/video below 5, e-ink becomes worth revisiting — but not now.

### Why Not Color OLED (SSD1351)

- **Power is actually HIGHER than TFT, not lower.** The SSD1351 datasheet specifies VCI operating current 23–29mA + Vcc operating current 33–42mA = **~57–71mA total**. The ST7789V TFT with backlight is ~30–50mA. Self-emissive OLED draws current per pixel — for a phone UI with bright text/menus on a dark background, the OLED is less efficient than a backlit TFT where the backlight is the main draw. The standby advantage is a wash (OLED sleep 1–5µA, TFT backlight off ~0; modem dominates standby at 17.5mA either way).
- **Cost is 3–5x higher** — $15–24 vs $5–8 for the TFT. True color OLED at 1.5"+ is rare and expensive; 128×128 1.5" is the standard option.
- 128×128 is too low for a usable phone UI (contacts lists, menus feel cramped) and poor for camera preview. No larger color OLED options exist at reasonable prices.
- **Not in Zephyr main tree** — only an out-of-tree third-party driver (nktsb/zephyr-ssd1351-driver, issue #88923 open). Would require integrating an external driver. The SSD1327 IS in Zephyr but is grayscale (16-level), not color — fails the color requirement.

### Selected Panel

- **Controller IC**: ST7789V (Sitronix)
- **Resolution**: 240×320 (QVGA)
- **Size**: 2.0" (2.4" acceptable alternative — same controller/resolution, larger physical size, lower PPI ~167)
- **Interface**: 4-wire SPI (SCK, MOSI, CS, DC) + RESET + backlight enable
- **Color format**: RGB565 (16-bit, 65K colors)
- **Variant preference**: IPS (full viewing angle) over TN
- **Backlight**: 4× white LED, PWM-dimmable via timer-output GPIO

### Pre-PCB Verification Items

1. **Zephyr ST7789v driver on STM32H7**: Confirm `display_st7789v.c` works on STM32H7 with the target Zephyr version. The MIPI DBI API conversion (issue #73750) had teething issues (SPI word size, data transfer) — verify on a dev board (e.g., STM32H743 Nucleo + ST7789 breakout) before committing to PCB.
2. ~~**Panel selection**: Select a specific module with documented ST7789V + 240×320 + SPI, available from LCSC/DigiKey/Adafruit/Waveshare. Confirm FPC/connector footprint for PCB.~~ **RESOLVED 2026-07-19**: HS HS20HS072RX (LCSC C5329582) — 2.0" IPS TFT, ST7789T3 (compatible variant), 12-pin 0.5mm ZIF FPC, 4 parallel LEDs (PWM dimming confirmed), $3.42, 1786 in stock. JLC-assemblable. See project-log.md 2026-07-19 Display Panel Selection. Remaining: verify ST7789T3 works with `display_st7789v.c` driver, confirm exact RST pin position from mechanical drawing.
3. **SPI clock**: Confirm panel max SPI clock (typically 40MHz for ST7789V) and that STM32H7 SPI peripheral can drive it at the needed rate for acceptable UI/camera-preview framerate.
4. **Backlight PWM**: Plan backlight PWM control on a timer-output GPIO for dimming and power management (display off during standby per FR-4.3).

## Open Research Questions

- [x] **RESOLVED (2026-07-12)**: Does VoLTE "just work" via AT commands, or is there significant configuration? — **Yes, VoLTE works.** `AT+voltesetting=1` on LE20B02 firmware returned OK. IMS PDP context (cid=2) auto-created by the network. `AT+CNSMOD: 0,8` confirms LTE mode (not CSFB). Test call connected successfully on Mint/T-Mobile. No firmware update needed — LE20B02 supports VoLTE despite being older than the documented LE20B04/05 versions. The IMS PDP context quirk (cid=2 conflict with cid=1 data) is specific to `AT+NETOPEN` and does not affect this project (uses CMUX+PPP). Validated empirically with Waveshare NA-H HAT + Mint SIM.
- [ ] **RESOLVED**: Can we use the module's built-in audio path or do we need an external codec? — SIM7600 (LCC package) exposes PCM digital audio only, no analog pins. External codec required. **MAX9880A selected** (dual-port: PCM + I2S). See Codec Selection section. The EG912U-GL has analog audio but was rejected for the two-audio-path problem with music playback.
- [x] **RESOLVED (2026-07-12)**: Which carriers allow VoLTE on non-certified devices with prepaid SIMs? — **Mint/T-Mobile allows VoLTE on the SIM7600NA-H.** VoLTE call connected successfully with `AT+voltesetting=1` on a Mint Mobile SIM. The SIM7600NA-H's T-Mobile certification likely helps. No IMEI whitelisting issues encountered. AT&T/Verizon remain untested but are stricter — not needed since Mint works.
- [ ] What's the minimum antenna design for LTE? Can we use a small chip antenna or stamped antenna?
- [ ] **RESOLVED (2026-06-28, second round)**: Can the SIM7600 maintain simultaneous VoLTE call + data tethering? — **Not a requirement.** Simultaneous VoLTE+data is a future ecosystem feature (tethering while on a call), not needed for MVP or daily driver. The PDP context conflict is confirmed in the `AT+NETOPEN` code path only; the project uses CMUX+PPP which bypasses it. CMUX+PPP is the standard pattern for simultaneous data + AT commands (SMS, calls) on the SIM7600, proven in Linux n_gsm, RT-Thread, and ESP-IDF. Whether data stays active *during* a live VoLTE call via PPP is unverified but likely (3GPP bearers should coexist). **Fallback: pause data during calls — acceptable for all current and planned use cases.** This is no longer a modem selection factor.
- [ ] Are there any open-source cell phone projects we can reference?
- [x] **RESOLVED (2026-07-12, partial)**: Does SIM7600 GNSS work standalone or only when module is registered on network? — **GNSS works while module is registered on the network.** `AT+CGPS=1` → `AT+CGPSINFO` returned a valid fix (42.35°N, -76.43°W, Ithaca NY area) in ~60 seconds from cold start. Whether GNSS works *without* network registration was not tested (modem was registered the whole time). For the ecosystem use case (car module uses phone GPS), the phone will always have network registration when in use, so this is sufficient. GNSS antenna must be connected.
- [ ] **RESOLVED**: Which ESP32 variants have USB OTG? (ESP32-S2, ESP32-S3 have native USB; original ESP32 does not) — Moot; STM32H743 selected.
- [x] **RESOLVED (2026-06-28)**: Which display type should the phone use? — **ST7789V SPI color TFT, 2.0" 240×320, RGB565.** Five options evaluated: (1) SPI color TFT ST7789V — **SELECTED**; (2) SPI color OLED SSD1351 — rejected (actually HIGHER power than TFT at ~57–71mA, 3–5x cost at $15–24, 128×128 too low, not in Zephyr main tree); (3) E-ink — **DISQUALIFIED** (blocks three 5+ features: camera preview 6 at ~0.5–3fps refresh, photo capture 6 with spot-color only no blue/green, video 5; true color e-ink not available at 1.5–2.4"); (4) LTDC parallel RGB — rejected (20–28 GPIO, needs external SDRAM, overkill res); (5) SPI TFT ST7735 1.8" 128×160 — rejected (too low res). ST7789v driver (`display_st7789v.c`) is the most mature SPI display driver in Zephyr main tree with native LVGL support. 6 GPIO pins, 150KB framebuffer fits internal 1MB SRAM (no external SDRAM), ~$5–8, color-capable, lower power than the OLED alternative. Pre-PCB: verify ST7789v driver on STM32H7 + target Zephyr version (MIPI DBI API conversion had teething issues). See Display Options section and project-log.md 2026-06-28 Display Selection.
- [x] **RESOLVED (2026-06-28)**: Which codec best supports both PCM (voice from SIM7600) and I2S (music from MCU) inputs? — **MAX9880A selected.** Key findings: (1) All common codecs (WM8960, NAU8810, NAU8822, SGTL5000, TLV320AIC3204/3104, ES8316/8388) have only ONE digital audio input port — they cannot accept PCM and I2S simultaneously. The original "single codec unifies voice and music" claim was false for these parts. (2) The **MAX9880A** (Maxim/ADI, ~$1.70, TQFN-48) has two truly independent digital audio ports (primary for voiceband PCM/TDM, secondary for stereo I2S/TDM) that run simultaneously and asynchronously — designed exactly for smartphone voice+media. (3) The SIM7600 outputs PCM only (fixed master mode, short-frame sync, 16-bit linear, 2048/4096kHz) — no I2S mode, not configurable. (4) With the MAX9880A, the MCU is NOT in the voice audio path during calls (SIM7600→PCM→codec primary→speaker directly), matching real smartphone architecture. (5) Fallback if MAX9880A is unavailable: MCU bridge (SAI1 PCM slave + SAI2 I2S master + single-port codec like NAU8822) — feasible but adds ~8-10ms latency and depends on Zephyr H7 SAI driver maturity. See Codec Selection / Audio Path Architecture section and project-log.md 2026-06-28 Codec Selection.
- [x] **RESOLVED (2026-06-28)**: Is Zephyr's STM32H7 USB OTG_HS + ULPI support mature enough for the ecosystem tethering path? — **Yes, it is viable (mainline since Dec 2022, PR #52772; bugs #61464/#75119 fixed; works on STM32H747I-DISCO), BUT it is no longer needed.** The SIM7600's own USB 2.0 HS port (480 Mbps) does tethering directly via RNDIS/ECM (`AT+CUSBPIDSWITCH`), bypassing the MCU entirely — a better architecture that eliminates the MCU USB bottleneck, the USB3300 ULPI transceiver, the Zephyr USB HS stack risk, and the 12 ULPI GPIO pins. **Decision: drop USB3300/ULPI; use MCU USB OTG_FS (12 Mbps) for MCU-originated USB (firmware, files, debug); route the modem's USB to the ecosystem connector (via an internal USB hub on a future respin) for tethering.** The "USB HS via ULPI is a board-level upgrade path preserved by LQFP-144" claim is superseded. See "USB HS / ULPI Revisit" section and project-log.md 2026-06-28 USB HS/ULPI Revisit.

## Component Checklist (BOM items not yet specified in docs)

Components that are implied by the architecture but not yet explicitly listed in any doc's BOM/component section. Add to schematic phase checklist:

| Component | Purpose | Notes |
|-----------|---------|-------|
| Nano-SIM socket | SIM card holder for SIM7600 | LGA/SMD, typically Molex 786470-3001 or similar |
| Battery fuel gauge IC | Battery level monitoring (FR-4.2) | I2C. **Selected: MAX17048** (ModelGauge, coulomb counting, ~$2.50). Shares I2C bus with MAX9880A. See `docs/bom.md` item 12 and `docs/constraints.md` Power section. |
| 3.3V buck-boost regulator | MCU/system rail from LiPo | **Selected: TPS63021DSJR** (fixed 3.3V, 4A switches / ~3A output, VSON-14/DSJ, LCSC C202140, ~$3.50 — LOCKED 2026-07-19). LiPo 3.0–4.2V → 3.3V. *Correction: docs previously said "TPS630201" — phantom part number, corrected to TPS63021DSJR.* See `docs/bom.md` item 10 and `docs/constraints.md` Power section. |
| ESD protection diodes | USB-C, SIM, microSD data lines | **Selected: USBLC6-2SC6** (USB) + **ESDA6V1-5SC6** (SIM/SD), ~$1 total. See `docs/bom.md` items 23-24 and `docs/constraints.md` PCB Design section. |
| Modem PWRKEY/STATUS GPIO | Power-cycle SIM7600 from MCU | 2 GPIO pins (PWRKEY output + STATUS input). See `docs/constraints.md` MCU section. |
| Display backlight driver | Raw panel LED backlight (FET + resistors) | N-FET + current-limiting resistors + PWM GPIO for parallel-LED panels. Verify panel config before PCB. See `docs/constraints.md` Display section. |
| 32.768 kHz crystal | Not needed (NITZ selected) | Only if RTC crystal approach is later adopted. See constraints.md timekeeping section. |
| USB-C connector | Data + charging + ecosystem interconnect | USB-C recommended over micro-USB. Connector type still TBD in requirements.md. |
| Earpiece transducer | Call audio (held to ear) | Separate from loudspeaker. See constraints.md audio topology note. |
| Loudspeaker | Ringtones, speakerphone (rated 3) | Codec has separate speaker output. |
| Audio codec | PCM voice (from SIM7600) + I2S music (from MCU) | **MAX9880AETM+ selected** (TQFN-48, ~$1.70). Dual-port: primary PCM, secondary I2S. 1.8V supply. See Codec Selection section. |
| Color TFT display | Phone UI, camera preview, photo viewer | **ST7789V selected** (2.0" 240×320, 4-wire SPI, RGB565, ~$5–8). 6 GPIO pins. 150KB framebuffer fits internal SRAM. IPS variant preferred. See Display Options section. |
| 1.8V LDO regulator | MAX9880A supply | From 3.3V or battery rail. |
| I2S level shifter | 3.3V MCU → 1.8V MAX9880A secondary port | Unidirectional (SCK, FS, SD, MCLK). Voltage divider or TXB010x. |

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
| SIM7600G/NA-H | **17.5 mA** | 4.6 mA | 2A | ~420 mAh |
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

This is the recommended replacement for the discontinued SIM7600G-H HAT. **Switch the prototyping HAT from G-H to NA-H** to validate B71 early without a custom PCB.

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
| SIM7600NA-H | LCC+LGA | 30×30×2.9mm | 119 |
| EG25-G | LGA | 29×32×2.4mm | 144 |
| EC25-AF | LCC | 29×32×2.4mm | 144 |
| EG912U-GL | LGA | 25×29×2.4mm | 126 |
| LARA-R6401 | LGA | 24×26×2.6mm | 100 |

No LTE/VoLTE module exists in a hand-friendly (castellated/through-hole) package — this is an industry reality, not SIM7600-specific. NFR-3 ("hand-solderable for prototypes") is unachievable for ANY LTE module and must be updated.

**Realistic path**: JLCPCB assembly for the modem section (~$57–72: module + $3 extended fee + ~$24 fixture + solder joints), hand-solder the rest. Hybrid assembly is supported by JLCPCB. Alternative: M.2 socket variant (module plugs in, no reflow) at cost of larger footprint. **SIM7600NA-H (C5380303) is a JLC pre-order part** — JLC sources it from SIMCom on demand ($31.42, lead time ≤18 days auto-proceed / >18 days email confirmation). SIM7600G-H (C5355477, 39 in stock, $46.95) shares the identical 119-pin LCC+LGA package and is the footprint fallback if NA-H library data is incomplete (do NOT buy G-H for the board: it lacks B71). SA-H and E-H are 87-pin LCC (different package) and lack B71 — disqualified.

## Codec Selection / Audio Path Architecture

### The Problem

The architecture (Architecture A) assumed a single codec handles both voice (PCM from SIM7600) and music (I2S from MCU) through "one audio path." The revisit found this claim is **false for all common codecs** — they have only one digital audio input port and cannot accept PCM and I2S simultaneously.

### Finding 1: SIM7600 Audio Interface (PCM only, fixed)

Source: SIM7600 Series Hardware Design Manual V1.03, §3.6 "PCM Interface."

| Parameter | Value | Configurable? |
|-----------|-------|---------------|
| Format | Linear PCM | Fixed |
| Data length | 16-bit | Fixed |
| Clock/sync source | Master mode (module generates) | Fixed |
| PCM clock rate | 2048 kHz (2G/3G), 4096 kHz (4G) | Fixed |
| Sync format | Short frame sync | Fixed |
| Data ordering | MSB first | Fixed |

Pins: PCM_OUT (73), PCM_IN (74), PCM_SYNC (75), PCM_CLK (76). No I2S pins, no AT command to change framing (unlike Quectel modules which have `AT+QDAI`). The Waveshare HAT's NAU8810 is wired in PCM mode to match. There is a USB-audio path (`AT+CPCMREG=1`, `AT+CPCMFRM=1` for 16kHz) but it transfers raw PCM over a custom USB endpoint — not standard USB Audio Class, requires host software to process. Some SIM7600-PCIEA variants have analog audio (MICP/MICN, EARP/EARN) but the standard module does not.

**Conclusion**: The SIM7600 outputs PCM only. A PCM-compatible codec or MCU bridge is required. This cannot be changed via firmware.

### Finding 2: Codec Digital Audio Port Survey

| Codec | Digital Audio Ports | PCM + I2S Simultaneous? | Package | Price (1-qty) | Speaker Driver |
|-------|---------------------|-------------------------|---------|---------------|----------------|
| WM8960 | 1 port (configurable: I2S/PCM/DSP/LJ/RJ) | NO | QFN-32 (5×5mm) | ~$6-12 (obsolete) | Yes (1W Class D) |
| NAU8810 | 1 port (I2S or PCM) | NO | QFN-20 (4×4mm) | $1.10 | Yes (BTL) |
| NAU88C22/8822 | 1 port (I2S or PCM) | NO | QFN-32 (4×4mm) | $1.19-2.88 | Yes (1W BTL) |
| TLV320AIC3204 | 1 port | NO | QFN-32 (4×4mm) | ~$5.12 | Yes (headphone amp) |
| TLV320AIC3104 | 1 port | NO | QFN-32 (4×4mm) | ~$3.57 | Yes (headphone amp) |
| TLV320AIC3106 | 1 port (pin-muxed, not dual) | NO | QFN-48/BGA-80 | Request quote | Yes |
| SGTL5000 | 1 port | NO | QFN-20/32 | Obsolete | Yes |
| ES8316/8388 | 1 port | NO | QFN | ~$1-2 | Yes |
| **MAX9880A** | **2 independent ports** | **YES** | **TQFN-48 (6×6mm)** | **~$1.70** | **Yes (30mW diff, 10mW capless)** |
| TLV320AIC34 | 2 independent ports | YES | BGA-87 (6×6mm) | ~$10.43 | Yes (4 headphone amps) |

**Key finding**: All popular hobbyist codecs have only ONE digital audio port. The MAX9880A (Maxim/ADI) is the only hobbyist-accessible codec with two truly independent digital audio interfaces — primary for voiceband (PCM/TDM), secondary for stereo audio (I2S/TDM), running simultaneously and asynchronously. The TLV320AIC34 is also dual-port but BGA-only (not hand-solderable). The TLV320AIC3106's "alternate bus" is pin multiplexing, not a second independent port (confirmed by TI forum).

### Finding 3: MCU Bridge Feasibility (Fallback Architecture)

If a single-port codec is used, the MCU must bridge PCM↔I2S: SIM7600→PCM→STM32 SAI1 (PCM slave)→STM32 SAI2 (I2S master)→codec.

- **SAI blocks**: H743 has 4× SAI (8 sub-blocks). SAI1 and SAI2 have independent kernel clocks (D2CCIP1R register), so they can run at different sample rates. Within one SAI, A and B sub-blocks share a kernel clock (both directions must use same rate — acceptable for full-duplex voice).
- **Sample rate strategy**: Run codec at 8/16kHz during calls (no ASRC needed), reconfigure to 44.1/48kHz for music. Simpler than software ASRC (H743 has no hardware ASRC).
- **Latency**: ~8-10ms with 32-sample buffers (4ms per direction). Well within ITU G.114 (150ms one-way). Echo cancellation needed above 25ms — not triggered.
- **CPU load**: <1% for pure bridging at 8kHz (DMA-based, 125-500 interrupts/sec). Total system load ~20-40% with UI + modem + PPP — comfortable on 480MHz M7.
- **Bidirectional**: 4 streams (PCM in/out, I2S in/out) fit in 2 SAI blocks (4 sub-blocks). SAI1-A/B for PCM, SAI2-A/B for I2S.
- **Risk**: Zephyr STM32H7 SAI driver maturity. The driver (`drivers/i2s/i2s_stm32_sai.c`) supports F4/G4/L5/H5 but H7 support was in progress (PR #92887). If not merged, requires porting or direct HAL usage. This is the primary "hard" part.
- **Cache coherency**: DMA buffers need non-cached SRAM or cache clean/invalidate operations (D-cache present on H7).

**Verdict**: Feasible-but-hard. Works if Zephyr H7 SAI driver is ready or willing to port. Adds latency and firmware complexity the MAX9880A avoids.

### Decision: MAX9880A (Dual-Port Codec) — LOCKED 2026-06-28

**Selected codec: MAX9880AETM+ (Maxim/ADI, TQFN-48, ~$1.70).**

Architecture:
```
Voice path (calls):
  SIM7600 PCM_OUT/IN/SYNC/CLK → MAX9880A primary port (PCM)
  MAX9880A → earpiece/speaker (analog out)
  Mic → MAX9880A (analog in) → PCM_IN → SIM7600
  [MCU NOT in voice audio path]

Music path (MP3 playback):
  STM32H743 SAI (I2S) → MAX9880A secondary port (I2S)
  MAX9880A → loudspeaker/headphones (analog out)

Simultaneous voice + music:
  MAX9880A mixes internally (e.g., call waiting tone over music)
```

Why MAX9880A over MCU bridge:
1. **MCU not in voice path** — voice works even if MCU is loaded or rebooting. Matches real smartphone architecture (modem↔codec direct PCM, AP only for media).
2. **Lower voice latency** — no bridge latency (direct PCM→codec).
3. **Simpler firmware** — no real-time DMA bridging task, no cache coherency work, no codec rate switching.
4. **Cheaper** — $1.70 vs WM8960 ($6-12, obsolete) or NAU8822 + bridge complexity.
5. **Designed for exactly this use case** — smartphone voice (cellular PCM) + media (processor I2S).
6. **No Zephyr SAI driver risk** for the voice path (codec talks directly to module; MCU I2S for music is simpler and more tolerant).

Risks / pre-PCB verification items:
1. **PCM short-frame sync compatibility — RESOLVED 2026-06-29**: **CONFIRMED COMPATIBLE.** The MAX9880A datasheet explicitly documents "TDM Short-Sync" mode (register settings: TDM = 1, FSW = 0) with timing parameters for both master and slave modes. PCM short-frame sync is electrically identical to TDM with 1 timeslot — the FS pulse is short (1 bit clock wide), marking the start of each 16-bit sample. The MAX9880A's TDM clock frequency range is 128–2048 kHz (datasheet spec), and the SIM7600 outputs BCLK at 2048 kHz — exactly the top of the range. The SIM7600 is always PCM master (generates BCLK + FS); the MAX9880A primary port in slave mode (MAS = 0) accepts these external clocks. The primary interface is explicitly "intended for voiceband applications" (8/16kHz, 16-bit). Register configuration at schematic time: TDM = 1, FSW = 0, MAS = 0 (slave), 16-bit slot width. ~~Schematic-time check: verify SIM7600 PCM pin I/O voltage matches MAX9880A's 1.8V~~ **RESOLVED 2026-06-30: 1.8V confirmed** (see item 3 below).
2. **Stock availability — RESOLVED 2026-06-29**: **AVAILABLE.** Mouser has 2,250 in stock (part # 700-MAX9880AETM+T, $2.23 qty 1, $1.52 qty 50+). DigiKey is temporarily out of stock (normal for ADI/Maxim parts — cycles in/out). Part is **active** (not discontinued), manufacturer lead time 6–13 weeks. Chinese brokers have 4,896–64,286 pcs. No supply risk for the PCB phase — order from Mouser when ready.
3. **1.8V supply — documented, no change**: MAX9880A operates on 1.8V (1.65–1.95V range). The MCU's 3.3V I2S lines need level shifting (simple voltage divider or level shifter IC; I2S from MCU is output-only, so unidirectional shifting is easy). **SIM7600 PCM pin voltage — RESOLVED 2026-06-30: 1.8V CONFIRMED.** Verified directly from the SIM7600 Hardware Design Manual V1.03 via PDF extraction (MCP `mcp-pdf` server): (1) Table 32 "1.8V Digital I/O characteristics" (page 47) — VOH = 1.35–1.8V, VIH = 1.17–2.1V, covering all digital I/O pins including PCM_OUT (73), PCM_IN (74), PCM_SYNC (75), PCM_CLK (76); (2) §3.6.2 PCM Application Guide (page 35) — the reference design wires PCM directly to a NAU8810 codec powered by the module's own VDD_1V8 pin (1.8V LDO, max 50mA) with no level shifter on the PCM lines. **Conclusion: PCM lines connect directly to MAX9880A (also 1.8V) — no level shifter needed on PCM. Only the MCU's 3.3V I2S lines need level shifting (already planned).**
4. **Not on Waveshare HAT** — the HAT has NAU8810 (single-port PCM). The MAX9880A can't be prototyped on the HAT. The HAT validates SIM7600 PCM voice output (the riskiest unknown); the MAX9880A is committed for the final PCB.

**Fallback architecture (if MAX9880A unavailable or incompatible)**: MCU bridge with NAU8822 (single-port I2S codec, ~$1.20). SAI1 as PCM slave (SIM7600), SAI2 as I2S master (codec). Run codec at 8/16kHz during calls, 48kHz for music. ~8-10ms latency. Requires Zephyr H7 SAI driver. See Finding 3 above.

### Prototyping Impact

The Waveshare NA-H HAT prototyping step is **unchanged** — it validates the SIM7600's PCM voice output on T-Mobile VoLTE using the NAU8810. This is the riskiest unknown and is independent of the final codec choice. The codec architecture decision affects the final PCB, not the HAT prototyping phase.

### Component Checklist Update

| Component | Purpose | Notes |
|-----------|---------|-------|
| MAX9880AETM+ | Audio codec (dual-port: PCM voice + I2S music) | TQFN-48, ~$1.70–2.23. **Pre-PCB verification COMPLETE 2026-06-29**: PCM short-frame sync confirmed compatible (TDM short-sync slave mode, 128–2048 kHz matches SIM7600's 2048 kHz); Mouser has 2,250 in stock ($2.23 qty 1). 1.8V supply — add level shifter for MCU I2S. Schematic-time: verify SIM7600 PCM pin I/O voltage. |
| 1.8V regulator | MAX9880A supply | LDO from 3.3V or battery rail. |
| I2S level shifter | 3.3V MCU → 1.8V MAX9880A secondary port | Unidirectional, 3-4 lines (SCK, FS, SD, MCLK). Simple voltage divider or TXB010x. |

## USB HS / ULPI Revisit (Zephyr STM32H7 OTG_HS + ULPI Maturity)

Revisit of the open item: "Zephyr USB HS via ULPI maturity on STM32H7." The concern was that the docs claimed "mature" STM32H7 USB support but possibly conflated **USB OTG_FS** (well-tested) with **USB OTG_HS via external ULPI** (less tested). This matters because the ecosystem tethering path (car module gets LTE from phone) needs more than USB FS's 12 Mbps, and the LQFP-144 package was chosen partly to expose the 12 ULPI pins.

### Finding 1: Zephyr STM32H7 USB OTG_HS + ULPI IS in mainline and works

- **PR #52772 "stm32h7: add usb hs ulpi support"** (XenuIsWatching) — **merged Dec 15, 2022.** Adds OTG_HS + ULPI PHY support to the STM32 USB driver, with the ULPI devicetree definition example on the **STM32H747I-DISCO** board (a mainline board that has a USB3300 ULPI transceiver onboard). A follow-up PR to `hal_stm32#155` set the ULPI pinctrl slew rate to "high-speed" (a required board-level detail).
- **Issue #52420 "STM32: support external ULPI PHY with OTG_HS"** — **closed/completed 2024-05-14.** The feature request is resolved.
- **Both USB stacks have ULPI support**: the legacy `drivers/usb/device/usb_dc_stm32.c` and the new `drivers/usb/udc/udc_stm32.c` (the "device_next" / UDC stack). The new stack selects `PCD_PHY_ULPI` from the PHY devicetree `compatible` (`usb-ulpi-phy`) referenced by the USB controller's `phys` property.
- **Real-world confirmation** (TMPDIR community, cbrake, Aug–Sep 2023): HS USB on the STM32H747I-DISCO works well with the `cdc_acm` sample ("HS USB is behaving well"). A custom STM32H743 board initially failed to receive data (issue #57499), but the root cause was **hardware** — "Discovered the power to the USB Phy IO power was floating, so after we fixed that, the USB on our custom STM32H7 board is now reliable and matches dev boards." The same hardware worked under TinyUSB/FreeRTOS, proving the board wasn't the issue — it was a floating PHY IO power rail, not a Zephyr software bug.
- **Known bugs are fixed**:
  - #61464 (ECM class assertion on STM32H7, "mutexes cannot be used inside ISRs" in `udc_stm32_lock` from `HAL_PCD_SetupStageCallback`) — **fixed by PR #104825.** Was directly relevant when CDC ECM was the planned MCU tethering class; no longer relevant to the tethering path (modem-direct now) but still relevant if any MCU USB class is used.
  - #75179 (USB-HS not working on stm32h747i_disco with the new `device_next` stack) — **fixed by PR #76115.**
- **Latest Zephyr versions**: v3.7.2 LTS (Jul 2024, supported to 7/2029) and v4.1.0 (Mar 2025). ULPI support has been in mainline since Dec 2022 (over 3 years).

**Caveats (ULPI is the less-trodden path):**
- Only **one mainline board** (stm32h747i_disco) uses ULPI on an H7. Most H7 boards use OTG_FS. ULPI has far fewer users than FS.
- The new UDC stack (`device_next`) had a ULPI regression on the disco board (#75179) — fixed, but it signals the new stack's ULPI path is less battle-tested than FS.
- Clock configuration for ULPI is confusing (issue #71248 still has open TODOs about exposing sleep-clock DTS properties for F4/H7 ULPI; currently handled by `if(SERIES_xxx)`-gated driver code).
- Board-level details are easy to get wrong: ULPI pinctrl **slew rate must be "high-speed"**, and the USB3300 IO power rail must be solidly tied (the #57499 "bug" was a floating PHY IO power).

**Verdict on Finding 1**: Zephyr STM32H7 USB OTG_HS via ULPI is **viable and in mainline**, with known bugs fixed and real-world success on the disco board. It is not as mature as OTG_FS and has rough edges (clock config, slew rate, new-stack maturity), but it is a real, working path — not vaporware. Contributing upstream support is no longer needed (it already exists); the work would be board-bring-up (DTS/pinctrl/clock) on the custom PCB.

### Finding 2: The SIM7600's own USB port does tethering directly — a better architecture

This is the bigger finding and changes the architecture.

- The SIM7600 has a **USB 2.0 High-Speed (480 Mbps)** device port (confirmed: SIMCom hardware design PDF states "USB2.0 is up to 480Mbps").
- The module can present itself as a **USB network adapter** for tethering, with no MCU involvement:
  - **RNDIS mode**: `AT+CUSBPIDSWITCH=9011,1,1` (best for Windows; also works on Linux via `rndis_host`)
  - **ECM mode**: `AT+CUSBPIDSWITCH=9018,1,1` (best for Linux/macOS; standard CDC ECM)
- In RNDIS/ECM mode the module's single USB port is a **composite device** exposing **both** the network interface **and** multiple AT/ttyUSB serial ports simultaneously (diagnostic, GPS NMEA, AT port, modem port, USB audio). Confirmed via `lsusb` on Raspberry Pi. So the USB host (car module) gets LTE data **and** AT command access over one cable.
- This is the module's **native, best-supported tethering path** — it is what the SIM7600 is designed to do for USB tethering (used by Raspberry Pi, routers, Travel routers like Beryl AX). It is independent of the `AT+NETOPEN` firmware bug (which affects the AT-controlled embedded TCP/IP stack, not the USB network stack) and independent of the project's CMUX+PPP path (which is for MCU-originated data over UART).
- The MCU talks to the modem via **UART** (CMUX+PPP for MCU data, AT for calls/SMS) — completely independent of the modem's USB. The modem's USB is free to be dedicated to tethering.

**Implication**: For the ecosystem tethering use case, the modem's own HS USB can connect directly to the car module (USB host). The car module gets LTE at full USB 2.0 HS (480 Mbps) — **no MCU bridging, no ULPI transceiver, no USB3300, no Zephyr USB HS stack, no 12 GPIO pins.** The MCU's USB speed becomes irrelevant for tethering.

### Finding 3: What the MCU's USB actually needs to do (all FS-sufficient)

With modem-direct tethering, the MCU's USB (OTG_FS, 12 Mbps, built-in PHY) only needs to handle:
- **Firmware updates** (MCU firmware via USB DFU/class) — FS is fine.
- **File transfer / mass storage** (expose SD card / contacts / music to a PC or the car module) — FS is fine for occasional sync; music files are not bandwidth-critical to stream over USB (the car module would copy/store them, not stream).
- **CDC ACM console / debug** — FS is fine.

None of these need HS. The MCU USB FS bottleneck only existed when the MCU was *bridging* LTE data to USB CDC ECM. With the modem doing tethering directly, that bridge is eliminated.

### Finding 4: Topology options for the ecosystem connector

The phone has two USB device ports (MCU OTG_FS, modem USB 2.0 HS) and the car module is a USB host. To connect two USB devices to one host over one cable requires a USB hub (you cannot wire two device ports together). Options:

| Topology | What it does | Cost / complexity | Tradeoff |
|----------|--------------|-------------------|----------|
| **A. Internal USB 2.0 hub** (e.g., USB2514) | Single USB-C → hub → {MCU FS, modem HS}. Car module sees both devices: modem (RNDIS for LTE) + MCU (MSC for files). | +1 hub chip (~$1–2), modest routing | Cleanest for the ecosystem vision; simultaneous LTE + file access over one cable. When plugged into a PC, the PC sees both modem (for firmware update) and MCU — also fine. |
| **B. Two USB-C connectors** | USB-C #1 → MCU (charge + firmware + files), USB-C #2 → modem (tethering + modem firmware update). | No hub chip, but 2 connectors (board space, 2 enclosure holes) | Car module must connect to both for LTE + files simultaneously, or accept files-only-over-#1 and LTE-only-over-#2. |
| **C. One USB-C + USB switch/MUX** | MCU controls a switch routing the connector to either MCU USB or modem USB (one at a time). | +1 switch chip, MCU control | Cannot do LTE + file access simultaneously. Cheapest single-connector option but loses simultaneity. |
| **D. Minimal "keep door open"** | Lay out modem USB D+/D- to a connector footprint (or test points) + MCU USB on the main USB-C. Decide hub/switch topology in a PCB respin when the ecosystem becomes real. | Lowest commitment now | Defers the topology decision; preserves the option without committing to a hub chip on rev1. |

**Recommendation: Topology D for rev1 (minimal commitment), with Topology A (internal hub) as the planned ecosystem path.** Tethering is rated 6 (strong want, not must-have) and is explicitly post-daily-driver scope. Rev1 should preserve the modem USB routing option (footprint/test points) without committing to a hub chip. When the ecosystem module becomes a real project, respin with the USB2514 hub (Topology A) for the clean single-cable simultaneous LTE + file access.

### Recommendation Summary

1. **USB HS via ULPI on Zephyr/STM32H7 is viable** (mainline since Dec 2022, bugs fixed, works on the disco board) — but it is **no longer needed** for the tethering use case, because the SIM7600's own USB 2.0 HS port does tethering directly and better.
2. **Do NOT populate the USB3300 ULPI transceiver.** It is wasted board space given the modem-direct tethering architecture. The 12 ULPI pins are freed for other future use. The LQFP-144 package decision is retained (it was also chosen for its GPIO margin — 41 spare after dropping ULPI — camera, and overall peripheral fit — not ULPI alone).
3. **Use the MCU's USB OTG_FS (12 Mbps, built-in PHY)** for all MCU-originated USB needs (firmware, files, debug). FS is sufficient for all of them.
4. **Route the SIM7600's USB D+/D- to a connector footprint or test points** on rev1 (preserve the tethering option). Plan for an internal USB 2.0 hub (Topology A) on a future respin when the ecosystem module becomes real — this gives the car module simultaneous LTE (modem RNDIS, 480 Mbps) + file access (MCU MSC) over one USB-C cable, with no MCU USB bottleneck and no ULPI.
5. **Update the "USB mode" resolved question**: USB FS for the MCU is the committed path; USB HS via ULPI is dropped (not needed — modem handles tethering at HS directly). The phone remains a USB **device** in all ecosystem scenarios; the modem is also a USB device, and a future internal hub presents both to the host.

### Pre-PCB / Prototype Verification Items (new)

- Validate `AT+CUSBPIDSWITCH=9018,1,1` (ECM) and `=9011,1,1` (RNDIS) on the Waveshare NA-H HAT connected to a Linux host — confirm the module enumerates as a network adapter and LTE data flows. This is cheap to test on the HAT (the HAT exposes the modem USB).
- Confirm whether the modem can run **PPP-over-UART (MCU data) simultaneously with RNDIS-over-USB (car module data)** — two independent data sessions on two PDP contexts. Likely yes (SIM7600 supports multiple PDP contexts) but unverified. If not, the MCU can use the RNDIS network via the hub, or accept MCU data pause while tethering (acceptable — future scope).
- If the ULPI path is ever revisited (e.g., a future use case needs the MCU itself to do HS USB, not tethering): verify on a STM32H743 Nucleo + USB3300 breakout that the Zephyr `udc_stm32.c` ULPI path works on the target Zephyr version, with ULPI pinctrl slew rate set to "high-speed" and solid USB3300 IO power.

Sources: Zephyr PR #52772 (merged), issues #52420/#57499/#61464/#75179/#71248, PRs #76115/#104825; TMPDIR community thread "Zephyr on STM32H743" (cbrake); SIMCom SIM7600 hardware design PDF ("USB2.0 is up to 480Mbps"); Waveshare RNDIS/ECM dial-up wikis; SIMCom Linux NDIS driver doc (composite interface table).
