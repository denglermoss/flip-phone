# Bill of Materials (BOM)

> **Status**: Preliminary — reflects component selections locked as of 2026-06-28 (MCU, modem, codec, display, keypad). Items not yet selected (power ICs, transducers) are listed as candidates with price ranges. Prices are USD, captured 2026-06-28 from publicly listed distributor pages. Verify current pricing/stock before ordering. **Updated 2026-06-28 (documentation review)**: VBAT buck regulator removed (direct-from-LiPo); 3.3V buck-boost (TPS630201) and fuel gauge (MAX17048) added; ESD protection added; MCP73831 note corrected. **Updated 2026-06-28 (keypad selection)**: Keypad locked — SMD tactile switches on custom PCB traces; prototyping keypad module added to §1. **Updated 2026-06-28 (Nucleo substitution)**: NUCLEO-H743ZI/ZI2 obsolete — NUCLEO-H753ZI is the substitute (H753 = H743 + crypto, identical for this project). DigiKey links added for all prototyping parts. Order consolidation: DigiKey (electronics) + Waveshare (HAT + display) + Mint Mobile (SIM).

## How to Read This BOM

- **LOCKED**: Component decision is final (see `docs/project-log.md`). Do not substitute without a documented revisit.
- **CANDIDATE**: Component not yet locked. Listed option(s) are recommended based on current docs; a selection revisit is pending.
- **TBD**: No candidate selected yet — deferred to a later phase per the docs.
- Prices are unit price at qty 1 unless noted. Bulk pricing reduces cost significantly for most components.

---

## 1. Prototyping Platform (Phase 2 — HAT-Based Prototype)

These items are for Phase 2 validation (VoLTE on a real carrier) before any custom PCB work. See `docs/project-log.md` Phase Breakdown.

**Order consolidation (3 sources, all free/fast shipping):**
- **DigiKey** (one order): Nucleo H753ZI, Adafruit keypad, tactile buttons, breadboard, jumper wires
- **Amazon** (free shipping): SIM7600NA-H HAT + 2" LCD (Waveshare parts — Amazon is cheaper than Waveshare direct once shipping is factored in; Waveshare ships from China with paid shipping and 1-2 week delivery)
- **Mint Mobile**: SIM + plan

| # | Component | Part Number | Status | Qty | Unit Price | Ext Price | Source / Link |
|---|-----------|-------------|--------|-----|-----------|-----------|---------------|
| 1 | LTE Cat-4 HAT (NA variant, B71, NAU8810 codec, GNSS) | Waveshare SIM7600NA-H 4G HAT (SKU 30717) | LOCKED | 1 | ~$77–89 | ~$77–89 | [Amazon — SIM7600NA-H HAT](https://www.amazon.com/SIM7600NA-H-4G-HAT-Communication-Positioning/dp/B0F24NBYKC) · [Waveshare direct](https://www.waveshare.com/sim7600na-h-4g-hat.htm) |
| 2 | Prepaid SIM (T-Mobile/Mint, most lenient with non-cert devices) | Mint Mobile Starter Kit / plan | CANDIDATE | 1 | ~$0–15 (starter) + $15–30/mo plan | ~$15–45 | [Mint Mobile](https://www.mintmobile.com) · [Amazon — Mint plans](https://www.amazon.com/Mint-Mobile-Wireless-Unlimited-3-Months/dp/B0741FV7ZV) |
| 3 | STM32H7 dev board (Nucleo-144, for MCU-side prototyping with HAT) | NUCLEO-H753ZI (substitute — see note) | CANDIDATE | 1 | $28.15 | $28.15 | [DigiKey — NUCLEO-H753ZI](https://www.digikey.com/en/products/detail/stmicroelectronics/NUCLEO-H753ZI/21348937) · [Mouser — NUCLEO-H753ZI](https://www.mouser.com/ProductDetail/STMicroelectronics/NUCLEO-H753ZI) |
| 4 | 2.0" SPI IPS TFT display (ST7789VW, for MCU prototyping) | Waveshare 2inch LCD Module (SKU 17344) | LOCKED | 1 | $14.39 | $14.39 | [Amazon — 2inch LCD Module](https://www.amazon.com/waveshare-2inch-LCD-Display-Module/dp/B081Q79X2F) · [Waveshare direct](https://www.waveshare.com/product/2inch-lcd-module.htm) |
| 5 | 4×4 matrix keypad module (membrane, for firmware prototyping) | Adafruit 4×4 Matrix Keypad (PID 3844) | CANDIDATE | 1 | $5.95 | $5.95 | [DigiKey — Adafruit 3844](https://www.digikey.com/en/products/detail/adafruit-industries-llc/3844/9561536) | 16-key membrane matrix. For Phase 2 firmware development (matrix scan + debounce). Electrical interface (rows/cols → MCU GPIO) identical to final PCB. |
| 6 | Tactile buttons, 6×6mm, for call/end/nav (breadboard) | Adafruit Tactile Button Switch 6mm, 20-pack (PID 367) | CANDIDATE | 1 | $2.50 | $2.50 | [DigiKey — Adafruit 367](https://www.digikey.com/en/products/detail/adafruit-industries-llc/367/10669771) | Loose buttons on breadboard for call/end/nav keys not on the 4×4 matrix. |
| 7 | Breadboard, 830 tie-point, solderless | Adafruit Full-size Breadboard (PID 239) | CANDIDATE | 1 | $2.95 | $2.95 | [DigiKey — Adafruit 239](https://www.digikey.com/en/products/detail/adafruit-industries-llc/239/7244929) | Standard full-size breadboard for prototyping. |
| 8 | Jumper wires, M/M, 40×3" (75mm) | Adafruit Premium M/M Jumper Wires (PID 759) | CANDIDATE | 1 | $1.95 | $1.95 | [DigiKey — Adafruit 759](https://www.digikey.com/en/products/detail/adafruit-industries-llc/759/5353615) | 40 male-to-male jumpers for breadboard connections. |
| | **Prototyping subtotal** | | | | | **~$148–180** | |

> **Nucleo board note (2026-06-28)**: Both NUCLEO-H743ZI2 and NUCLEO-H743ZI are **obsolete** on DigiKey and ST eStore. The **NUCLEO-H753ZI** is the recommended substitute — the STM32H753ZI is an STM32H743ZI with crypto peripherals (AES, HASH, TRNG) added; everything else (core, Flash, RAM, package, peripherals, pinout) is identical. The crypto peripherals are irrelevant to this project. The locked MCU decision (STM32H743ZIT6 for the final PCB) is unaffected — the Nucleo is only for prototyping. DigiKey has 387 in stock ($28.15); Mouser has 898 in stock ($27.00). DigiKey is recommended to consolidate with the Adafruit parts (Mouser does not carry the Adafruit keypad).

> **Bare chip stock (STM32H743ZIT6, for final PCB — not needed now)**: Confirmed in stock at ST eStore ($14.61), Mouser (360 units, $17.37), DigiKey (limited stock, $16.54). No supply concern for the PCB phase.

---

## 2. Core Components — LOCKED (Final PCB)

These are the locked component decisions per `docs/project-log.md`. Prices reflect the bare component for PCB assembly.

| # | Component | Part Number | Package | Status | Qty | Unit Price | Ext Price | Source / Link | Notes |
|---|-----------|-------------|---------|--------|-----|-----------|-----------|---------------|-------|
| 4 | MCU — STM32H7 Cortex-M7 480MHz, 2MB Flash, 1MB RAM | STM32H743ZIT6 | LQFP-144 20×20mm | LOCKED | 1 | $14.61 (qty 1) / $9.13 (10ku) | $14.61 | [ST eStore](https://estore.st.com/en/stm32h743zit6-cpn.html) · [DigiKey](https://www.digikey.com/en/products/detail/stmicroelectronics/STM32H743ZIT6/6371188) | Hand-solderable LQFP. USB OTG_FS built-in (12 Mbps). USB HS via ULPI **dropped** 2026-06-28 — modem-direct USB tethering replaces it. LQFP-144 retained for GPIO margin (41 spare). |
| 5 | Cellular module — LTE Cat-4, VoLTE, B66/B71, NA variant | SIM7600NA-H | LCC+LGA 30×30mm, 119-pin | LOCKED | 1 | $31.42 (JLC pre-order) | $31.42 | [JLC pre-order — SIM7600NA-H (C5380303)](https://jlcpcb.com/partdetail/SIMCom_WirelessSolutions-SIM7600NA-H/C5380303) | LGA — requires JLCPCB assembly (~$57–72 for modem section). **Part name corrected 2026-07-19**: "SIM7600A-H" was a misnomer — SIMCom's actual product code is `SIM7600NA-H` (North America H-series). The old LCSC link (C2995537) pointed to the non-H `SIM7600A`, a different/older product (87-pin LCC, not 119-pin LCC+LGA). **JLC availability**: NA-H is a **pre-order part** (C5380303, $31.42, 0 in stock — JLC sources it from SIMCom on demand). SIM7600G-H (C5355477, $46.95, 39 in stock) shares the identical 119-pin LCC+LGA package and is the **footprint fallback** if NA-H library data is incomplete. SA-H and E-H are 87-pin LCC (different package) and lack B71 — disqualified. Fallback modem: EC25-AF. See project-log.md 2026-07-19 SIM7600 Variant Selection. |
| 6 | Audio codec — dual I2S/PCM (PCM voice + I2S music) | Realtek ALC5651-CG | QFN-40 5×5mm | LOCKED | 1 | ~$1.00 (LCSC qty 1) | ~$1.00 | [LCSC — ALC5651-CG (C963633)](https://www.lcsc.com/product-detail/C963633.html) · [JLC — C963633](https://jlcpcb.com/partdetail/Realtek-ALC5651CG/C963633) | ~~MAX9880AETM+T~~ **SUPERSEDED 2026-07-19** (was Mouser consignment — replaced to eliminate last consignment part). ALC5651 is JLC Extended (no consignment). Dual I2S/PCM audio hub: I2S-1 = PCM voice from SIM7600 (slave, PCM Mode A short-sync), I2S-2 = I2S music from MCU. 100dBA DAC, 94dBA ADC, ASRC, 7-band EQ, DRC/AGC. 1.8V analog + 1.2V digital (internal LDO) + 3.3V MICVDD. QFN-40 5×5mm (smaller than MAX9880A TQFN-48 6×6mm). PCM compatibility verified (ALC5651 §7.5.1 PCM Mode A = SIM7600 §3.6 short sync). Datasheet: `docs/reference/alc5651.pdf`. KiCad model downloaded. See project-log.md 2026-07-19 Codec Swap. |
| | **Core subtotal** | | | | | **~$43–47** | | |

---

## 3. Supporting Components — Recommended/Candidate

These components are required for the phone but have not been formally locked in `docs/project-log.md` (except the display, which is locked — see §3a). Candidates are listed with prices; a selection revisit is pending for keypad and power ICs.

### 3a. Display (LOCKED — ST7789V SPI color TFT)

| # | Component | Part Number | Status | Qty | Unit Price | Ext Price | Source / Link | Notes |
|---|-----------|-------------|--------|-----|-----------|-----------|---------------|-------|
| 7 | 2.0" SPI IPS TFT color display, 240×320, ST7789VW | Waveshare 2inch LCD Module (SKU 17344) | LOCKED | 1 | $11.99 | $11.99 | [Waveshare — 2inch LCD Module](https://www.waveshare.com/product/2inch-lcd-module.htm) | IPS, 262K color, 4-wire SPI, 58×35mm module. ST7789VW driver. 150KB framebuffer fits internal 1MB SRAM. 6 GPIO pins. See project-log.md 2026-06-28 Display Selection. |
| 7b | 2.0" ST7789V raw panel (FPC, for PCB integration) | HS HS20HS072RX (LCSC C5329582) | LOCKED | 1 | $3.42 | $3.42 | [LCSC — HS20HS072RX (C5329582)](https://www.lcsc.com/product-detail/C5329582.html) · [JLC part page](https://jlcpcb.com/partdetail/HS-HS20HS072RX/C5329582) | **LOCKED 2026-07-19.** 2.0" IPS TFT, 240×RGB×320, ST7789T3 (compatible variant — same Zephyr driver), 4-wire SPI, 262K color. Outline 51.80×36.20×2.1mm. 12-pin 0.5mm ZIF FPC (backlight LEDs broken out as LEDA/LEDK — enables PWM dimming). 4 parallel white LEDs, 80mA, Vf 3.0V. LCSC: 1,786 in stock. JLC: Extended (pre-order). EasyEDA footprint available. See project-log.md 2026-07-19 Display Panel Selection. **Backlight**: 4 parallel white LEDs (common anode, ~3.0V Vf, 80mA total). Driven by 3.3V rail through current-limiting resistors + PWM-controlled N-FET on a timer-output GPIO. No dedicated LED driver IC needed. |
| 7c | 1.14" ST7789V raw panel (FPC, outer display for flip lid) | EastRising ER-TFT1.14-2 (BuyDisplay) | LOCKED | 1 | $3.27 | $3.27 | [BuyDisplay — ER-TFT1.14-2](https://www.buydisplay.com/1-14-inch-tft-lcd-display-ips-panel-screen-135x240-for-smart-watch) | **LOCKED 2026-07-19** (replaces Wisevision N114 — see note). 1.14" IPS TFT, 135×240, ST7789V (same driver family as main display — Zephyr `solomon,st7789v`), 4-wire SPI, 65K/262K color. Outline 17.6×31.0×1.6mm. Active area 14.86×24.91mm. **8-pin 0.5mm pitch FPC (top contact)** — standard JLC-stockable ZIF connector (HDGC C2919539). Backlight: 1 white LED, 3.0V, 15mA (PWM dimmable). Supply 2.5–3.3V (3.3V only — no boost converter). Brightness 400 cd/m². Contrast 500:1. Pinout: 1=LEDA, 2=GND, 3=RESET, 4=RS(DC), 5=SDA, 6=SCL, 7=VDD, 8=CS. **Purchased separately from PCB and assembled by user** (ZIF FPC plugs in post-PCB-assembly). 10-year continuity supply promise. See project-log.md 2026-07-19 Outer Display Re-Selection. **Note**: Replaces Wisevision N114-2413THBIG01-H13 (C2890618) — that panel used 0.7mm FPC pitch, which is non-standard and has no JLC-stocked connectors. |

### 3b. Power (CANDIDATE)

| # | Component | Part Number | Status | Qty | Unit Price | Ext Price | Source / Link | Notes |
|---|-----------|-------------|--------|-----|-----------|-----------|---------------|-------|
| 8 | LiPo battery, 3.7V, ~1000–1200mAh (24h standby needs ≥420mAh) | Adafruit 258 (1200mAh) | CANDIDATE | 1 | $9.95 | $9.95 | [Adafruit — 1200mAh LiPo](https://www.adafruit.com/product/258) | 34×62×5mm. 1200mAh gives ~45h standby. Currently out of stock at Adafruit — check alternatives. |
| 9 | Battery charger IC, single-cell LiPo, USB input | MCP73831-2ACI/MC | CANDIDATE | 1 | ~$1.00 | ~$1.00 | [DigiKey — MCP73831](https://www.digikey.com/en/products/detail/microchip-technology/MCP73831-2ACI-MC/1874108) · [Microchip](https://www.microchip.com/en-us/product/mcp73831) | DFN-8 2×3mm, up to 500mA charge current. Charges battery from USB; battery supplies modem peaks (2A+). For production: consider a power-path charger (e.g., BQ25895, 5A) that can supply system load + charge simultaneously. For prototype, MCP73831 is sufficient — battery handles transient peaks. |
| 10 | 3.3V buck-boost regulator (MCU/system rail from LiPo) | TPS63021DSJR (3.3V fixed, 4A switches / ~3A output) | LOCKED | 1 | ~$3.50 | ~$3.50 | [LCSC — TPS63021DSJR (C202140)](https://www.lcsc.com/product-detail/DC-DC-Converters_Texas-Instruments-TPS63021DSJR_C202140.html) | LiPo (3.0–4.2V) → 3.3V. Buck-boost needed: LiPo drops below 3.3V at ~40% charge. Powers MCU, display, SD card, codec I2S side, level shifter. **Part corrected 2026-07-19**: "TPS630201" was a phantom part number (TI never made it). TPS63021DSJR is the real fixed-3.3V part (VSON-14/DSJ, 4A switches, ~3A output — exceeds the original 2A spec). JLC-stocked (C202140) — no consignment needed. See project-log.md 2026-07-19 U4 Buck-Boost Correction. |
| 10a | Power inductor for item 10 (TPS63021DSJR) | Coilcraft XFL4020-152MEC (1.5µH, Isat 4.4A, DCR 14.4mΩ) | LOCKED | 1 | ~$1.25 | ~$1.25 | [LCSC — XFL4020-152MEC (C3033018)](https://www.lcsc.com/product-detail/C3033018.html) | **LOCKED 2026-07-19.** Datasheet-recommended part (TI SLVS916I Table 2 + Table 4 — XFL4020-152ME/ML family). 1.5µH ±20%, 4×4×2.1mm, magnetic shielded. Lowest DCR available at this size (14.4mΩ) → best efficiency on the 3.3V rail. Isat 4.4A at 20% inductance drop — adequate for actual phone load currents (2–3A peak; 4A is the switch current limit, not operating current). JLC "Extended" (757 in stock at LCSC). KiCad model downloaded. Alternative rejected: Taiyo Yuden LSDND4040WKT1R5MM (C6653414, Isat 7A but DCR 35mΩ — 2.4× higher). See project-log.md 2026-07-19 L1 Inductor Selection. |
| 11 | 1.8V LDO regulator (for ALC5651 codec supply, from 3.3V rail) | TPS7A0218PDBVR | CANDIDATE | 1 | ~$0.84 | ~$0.84 | [DigiKey — TPS7A0218PDBVR](https://www.digikey.com/en/products/detail/texas-instruments/TPS7A0218PDBVR/12165118) | 1.8V fixed, 200mA, SOT-23-5. Fed from 3.3V buck-boost (item 10). Low current (~10–20mA codec). |
| 12 | Battery fuel gauge (coulomb-counting, I2C) | MAX17048G+T10 | CANDIDATE | 1 | ~$2.50 | ~$2.50 | [DigiKey — MAX17048](https://www.digikey.com/en/products/detail/analog-devices-inc-maxim-integrated/MAX17048G-T10/5263689) | ModelGauge IC, I2C. Provides state-of-charge (%), voltage, current estimation. Required for FR-4.2 (battery level display). Shares I2C bus with ALC5651. 3.3V-compatible. Alternative: ADC voltage-only (cheaper, less accurate — no coulomb counting). |
| | **Power subtotal** | | | | | **~$9–10** | | |

### 3c. Audio Transducers (CANDIDATE)

| # | Component | Part Number | Status | Qty | Unit Price | Ext Price | Source / Link | Notes |
|---|-----------|-------------|--------|-----|-----------|-----------|---------------|-------|
| 13 | Earpiece speaker, 10mm, 8Ω | Taoglas SPKM.10.8.A | CANDIDATE | 1 | ~$1.69 | ~$1.69 | [Taoglas — SPKM.10.8.A](https://www.taoglas.com/product/10-mm-round-miniature-speaker-500mw/) · [ichome](https://www.ichome.com/product-detail/taoglas/spkm-10-8-a) | 10×4mm, 200mW RMS. For call audio (held to ear). |
| 14 | Loudspeaker (ringtones, speakerphone) | TBD — 20mm+ mylar speaker | CANDIDATE (include on rev1 — locked 2026-07-19) | 1 | ~$2–5 | ~$2–5 | — | Rated 3 on wishlist. ALC5651 has stereo outputs for both. **Rev1 decision (2026-07-19)**: include both earpiece + loudspeaker — stereo outputs drive both at no extra codec cost. Specific part TBD at schematic time. |
| 15 | Microphone (MEMS or electret) | TBD — e.g. Knowles SPQ | TBD | 1 | ~$1–3 | ~$1–3 | — | MEMS preferred for SMD. |
| | **Audio transducer subtotal** | | | | | **~$5–10** | | |

### 3d. Level Shifting (CANDIDATE — required for ALC5651 1.8V↔3.3V)

| # | Component | Part Number | Status | Qty | Unit Price | Ext Price | Source / Link | Notes |
|---|-----------|-------------|--------|-----|-----------|-----------|---------------|-------|
| 16 | 4-bit bidirectional level shifter, 1.8V↔3.3V | TXB0104D | CANDIDATE | 1 | ~$0.76 | ~$0.76 | [TI — TXB0104](https://www.ti.com/product/TXB0104) · [Digi-Key via DiGi Electronics](https://www.digi-electronics.com/en/products/detail/texas-instruments/TXB0104D/1837198.html) | SOIC-14. For MCU I2S lines (SCK, FS, SD, MCLK) to ALC5651. Unidirectional — simple divider also works. |
| | **Level shifting subtotal** | | | | | **~$1** | | |

### 3e. Connectors (CANDIDATE)

| # | Component | Part Number | Status | Qty | Unit Price | Ext Price | Source / Link | Notes |
|---|-----------|-------------|--------|-----|-----------|-----------|---------------|-------|
| 17 | USB-C receptacle, 16-pin, SMD (data + power) — main MCU USB | GCT USB4081 or similar | LOCKED (USB-C locked 2026-07-19) | 1 | ~$1–3 | ~$1–3 | [DigiKey — GCT USB-C](https://www.digikey.com/en/product-highlight/g/gct/usb-type-c) | USB-C 16-pin for USB 2.0 + power. Routes to MCU USB OTG_FS (firmware/files/debug). |
| 17b | USB-C receptacle (or micro-USB) — modem USB HS port footprint | TBD | CANDIDATE (unpopulated on rev1 — locked 2026-07-19) | 1 | ~$1–3 | ~$0 (unpopulated) | — | **Rev1 decision (2026-07-19)**: route SIM7600 USB HS D+/D- to an unpopulated connector footprint. Preserves tethering + modem FW update + diagnostics + GNSS-over-USB + ecosystem options. May be USB-C (consistent) or micro-USB (smaller footprint) — TBD at schematic time. |
| 18 | Nano SIM card socket, SMD, hinged | SHOU HAN NANO SIM XG6P H1.35 | LOCKED | 1 | $0.146 | $0.15 | [LCSC — C7529386](https://www.lcsc.com/product-detail/C7529386.html) | **LOCKED 2026-07-19.** Nano-SIM (4FF), hinged lid, 6-pin (no card detect — optional per SIM7600 manual), 1.45mm height. 38,255 in stock. Hinged chosen over push-push (top-loading, no lateral clearance). See project-log.md 2026-07-19 J3/J4 Sourcing. |
| 19 | MicroSD card socket, SMD, hinged | Molex 472192001 | LOCKED | 1 | $0.765 | $0.77 | [LCSC — C164170](https://www.lcsc.com/product-detail/C164170.html) | **LOCKED 2026-07-19.** MicroSD (TF), hinged lid, 8-pin, 1.9mm height, 1.10mm pitch. Molex OEM. 16,177 in stock. 5,000 cycles. For music/photo storage (rated 7). See project-log.md 2026-07-19 J3/J4 Sourcing. |
| 20a | FPC ZIF connector 12-pin 0.5mm (main display J7) | HDGC 0.5K-HX-12PWB | LOCKED | 1 | ~$0.11 | ~$0.11 | [JLC — C2919494](https://jlcpcb.com/partdetail/HDGC-0_5K_HX12PWB/C2919494) | **LOCKED 2026-07-19.** Hinged lid, double-sided contacts, 1mm height. Same series as J8/J9/J10. Double-sided eliminates top/bottom contact orientation risk (FPC folds under display). |
| 20b | FPC ZIF connector 8-pin 0.5mm (outer display J10) | HDGC 0.5K-HX-8PWB | LOCKED | 1 | ~$0.11 | ~$0.11 | [JLC — C2919492](https://jlcpcb.com/partdetail/HDGC-0_5K_HX8PWB/C2919492) | **LOCKED 2026-07-19.** Same series as J7/J8/J9. For ER-TFT1.14-2 outer display. |
| 20c | FPC ZIF connector 14-pin 0.5mm (hinge flex J8 + J9) | HDGC 0.5K-HX-14PWB | LOCKED | 2 | ~$0.11 | ~$0.22 | [JLC — C2919495](https://jlcpcb.com/partdetail/HDGC-0_5K_HX14PWB/C2919495) | **LOCKED 2026-07-19.** Same series as J7/J10. Two needed (one on main board, one on daughterboard). Need matching 14-pin 0.5mm FFC cable. |
| | **Connector subtotal** | | | | | **~$3–10** | | |

### 3f. Antenna (CANDIDATE)

| # | Component | Part Number | Status | Qty | Unit Price | Ext Price | Source / Link | Notes |
|---|-----------|-------------|--------|-----|-----------|-----------|---------------|-------|
| 20 | LTE cellular antenna, U.FL/IPEX, 700–2700MHz | Pulse W3907B0100 | CANDIDATE | 1 | $5.54 | $5.54 | [ArcAntenna — W3907B0100](https://www.arcantenna.com/products/antenna-for-embedded-iot-modules-lte-catm1-catnb1-egprs-like-quectel-bg96-w3907b0100-with-100mm-cable-ufl-ipex-mhf-connector) | Flexible patch, 100mm cable, U.FL. Covers B2/B4/B66/B71. |
| 21 | GNSS antenna (for SIM7600 built-in GNSS) | TBD — U.FL GPS antenna | CANDIDATE (include on rev1 — locked 2026-07-19) | 1 | ~$2–5 | ~$2–5 | — | SIM7600 has built-in GNSS (validated 2026-07-12 on HAT — valid fix in ~60s cold start). **Rev1 decision (2026-07-19)**: include U.FL footprint on rev1 — user wants this board to potentially be the final version; deferring would mean a respin. Specific antenna part TBD at schematic time. |
| | **Antenna subtotal** | | | | | **~$8–11** | | |

### 3g. Keypad (LOCKED — SMD tactile switches on custom PCB traces)

| # | Component | Part Number | Status | Qty | Unit Price | Ext Price | Source / Link | Notes |
|---|-----------|-------------|--------|-----|-----------|-----------|---------------|-------|
| 22 | SMD tactile switches, 5.2×5.2×1.5mm (keypad matrix) | ALPS Alpine SKQGABE010 (LCSC C115351) | LOCKED | ~20 | ~$0.089 | ~$1.78 | [LCSC — C115351](https://www.lcsc.com/product-detail/C115351.html) · [JLCPCB part page](https://jlcpcb.com/partdetail/ALPSALPINE-SKQGABE010/C115351) | **LOCKED 2026-07-19**: ALPS SKQGABE010 selected. Specs: 1.57N (160gf), 0.25mm travel, 1M cycle life, 1.5mm height, SPST-NO gull-wing SMD. LCSC stock 41,590; JLC stock 1,344. KiCad model downloaded to `pcb/phone/lib/`. Same 5.2×5.2mm footprint across SKQG stem-height variants (3.1/3.4/5.0mm) — swap up without respin if feel is too snappy. See project-log.md 2026-07-19 Keypad Switch Selection. |
| | **Keypad subtotal** | | | | | **~$1–2** | | |

### 3h. ESD Protection (CANDIDATE — required for external connectors)

| # | Component | Part Number | Status | Qty | Unit Price | Ext Price | Source / Link | Notes |
|---|-----------|-------------|--------|-----|-----------|-----------|---------------|-------|
| 23 | USB-C ESD protection (D+/D- lines) | USBLC6-2SC6 | CANDIDATE | 1 | ~$0.50 | ~$0.50 | [DigiKey — USBLC6-2SC6](https://www.digikey.com/en/products/detail/stmicroelectronics/USBLC6-2SC6/6035358) | SOT-23-6, bidirectional ESD for USB 2.0. Protects MCU USB OTG_FS D+/D-. |
| 24 | SIM/SD ESD protection (data lines) | ESDA6V1-5SC6 or similar | CANDIDATE | 1 | ~$0.50 | ~$0.50 | [DigiKey — ESDA6V1-5SC6](https://www.digikey.com/en/products/detail/stmicroelectronics/ESDA6V1-5SC6/6034568) | 5-line ESD array for SIM + microSD data lines. |
| | **ESD subtotal** | | | | | **~$1** | |

### 3i. Passive Components & Misc (ESTIMATE)

| # | Component | Status | Qty | Unit Price | Ext Price | Notes |
|---|-----------|--------|-----|-----------|-----------|-------|
| 25 | Bulk capacitance (100–470µF ceramic + tantalum for VBAT stability) | CANDIDATE | ~5–10 | ~$0.50–2 | ~$3–10 | CRITICAL for modem VBAT rail — direct from LiPo, separate net from 3.3V. See `docs/constraints.md`. |
| 26 | Decoupling caps, resistors, inductors (per IC) | CANDIDATE | ~30–50 | ~$0.05–0.50 | ~$5–15 | Standard SMD passives. |
| 27 | Crystals (HSE 8MHz for MCU; module has own TCXO) | CANDIDATE | 1 | ~$0.50–1 | ~$0.50–1 | MCU needs HSE crystal for USB. No 32.768kHz RTC crystal (NITZ). |
| 28 | LEDs (status, notification, backlight) | CANDIDATE | ~3 | ~$0.10–0.30 | ~$0.30–1 | Rated 2 on wishlist. |
| 29 | Test points, headers, misc hardware | CANDIDATE | — | — | ~$2–5 | For bring-up/debug. |
| | **Passive/misc subtotal** | | | | **~$11–32** | |

---

## 4. PCB Fabrication & Assembly (Not in BOM cost target — separate line item)

| # | Item | Vendor | Est Cost | Notes |
|---|------|--------|----------|-------|
| 30 | PCB fabrication (4-layer, impedance control) | JLCPCB / PCBWay | ~$5–50/board | Price scales with complexity. 4-layer recommended for RF + PDN. |
| 31 | PCB assembly — modem section only (LGA reflow) | JLCPCB | ~$57–72 | Module + $3 extended fee + ~$24 fixture + solder joints. SIM7600NA-H via JLC pre-order (C5380303) — JLC sources from SIMCom, stores in your private library until PCBA order. |
| 32 | PCB assembly — rest of board | Hand-solder | $0 (labor) | All other components hand-solderable. JLCPCB fallback if needed. |
| | **PCB total (per board, first iteration)** | | **~$62–122** | |

---

## 5. Cost Summary

### Prototype BOM (components only, per NFR-5 target: < $150/unit)

| Category | Est Cost (low) | Est Cost (high) |
|----------|---------------|-----------------|
| Core components (LOCKED: MCU + modem + codec + display panel) | $48 | $55 |
| Power (battery + charger + 3.3V buck-boost + 1.8V LDO + fuel gauge) | $18 | $18 |
| Audio transducers (earpiece + speaker + mic) | $5 | $10 |
| Level shifting | $1 | $1 |
| Connectors (USB-C, SIM, microSD) | $3 | $9 |
| ESD protection | $1 | $1 |
| Antenna (cellular + GNSS) | $8 | $11 |
| Keypad (SMD tactile switches) | $1 | $2 |
| Passive components & misc | $11 | $32 |
| **BOM total (components, per unit)** | **~$97** | **~$140** |
| PCB fab + assembly (separate) | $62 | $122 |
| **Total per unit (BOM + PCB)** | **~$159** | **~$262** |

**Assessment**: The components-only BOM target (< $150/unit, NFR-5) is achievable at the low end and tight at the high end. The dominant cost is the cellular module (~$28–32) + JLCPCB assembly (~$57–72). PCB fab/assembly is correctly excluded from the NFR-5 BOM target per `docs/requirements.md`. Note: the previous "high-current buck regulator for VBAT" (~$3–6) was removed — VBAT is powered directly from the LiPo (see constraints.md Power section). A 3.3V buck-boost (TPS630201, ~$3.50) and fuel gauge (MAX17048, ~$2.50) were added — net cost change is approximately +$2.50.

### Prototyping Phase (one-time, before custom PCB)

| Item | Source | Est Cost |
|------|--------|----------|
| Waveshare SIM7600NA-H 4G HAT | Amazon | $77–89 |
| Waveshare 2" LCD Module (ST7789VW) | Amazon | $14 |
| Mint Mobile SIM + plan (3-month) | Mint Mobile | $15–45 |
| NUCLEO-H753ZI dev board | DigiKey | $28 |
| Adafruit 4×4 matrix keypad (PID 3844) | DigiKey | $6 |
| Adafruit 6mm tactile buttons, 20-pack (PID 367) | DigiKey | $3 |
| Adafruit breadboard + jumper wires (PID 239 + 759) | DigiKey | $5 |
| **Prototyping subtotal** | | **~$148–180** |

### Total Project Budget Estimate (per `docs/constraints.md`: $200–500 realistic)

| Phase | Est Cost |
|-------|----------|
| Phase 2: HAT prototyping | $148–180 |
| Phase 4–5: First PCB (BOM + fab + assembly) | $156–267 |
| Iterations / respins / mistakes (1–2 boards) | $100–200 |
| Tools (if not already owned: hot air, solder, etc.) | $0–50 |
| **Total project estimate** | **~$404–697** |

> The high end exceeds the $500 target if multiple PCB respins are needed. The modem LGA assembly cost (~$57–72/board) is the main driver — minimizing respins by thorough schematic review is the biggest cost lever.

---

## 6. Open Items / Pre-Order Verification

Per `docs/constraints.md` and `docs/project-log.md`, these must be verified before placing the PCB order:

- [x] ~~**MAX9880A**~~: ~~Confirm PCM short-frame sync support on primary port (datasheet review). Verify stock at DigiKey/Mouser — Maxim/ADI parts can have long lead times. Confirm 1.8V supply + level shifting plan.~~ **ALL VERIFIED 2026-06-29/30**: PCM short-frame sync confirmed compatible (TDM short-sync slave mode); stock available at Mouser (2,250 units, $2.23); 1.8V supply + level shifting documented (MCU I2S lines only — SIM7600 PCM lines are 1.8V, connect directly to MAX9880A, no level shifter needed on PCM). **SUPERSEDED 2026-07-19**: MAX9880A replaced by Realtek ALC5651-CG (C963633, JLC Extended — no consignment). See project-log.md 2026-07-19 Codec Swap.
- [ ] **SIM7600NA-H**: Pre-order placed via JLC (C5380303, $31.42). JLC sources from SIMCom — lead time ≤18 days = auto-proceed, >18 days = email confirmation. Part appears in your JLC Parts Lib when it arrives at their warehouse. Can start PCB fab order in parallel; SMT assembly waits for both board + part. Verify firmware version supports VoLTE before PCB commit (HAT validated on LE20B02). |
- [ ] **ST7789V display**: Confirm ST7789v Zephyr driver works on STM32H7 with target Zephyr version (MIPI DBI API conversion had teething issues — verify on dev board before PCB). ~~Select specific raw panel module and confirm FPC/connector footprint.~~ **Panel RESOLVED 2026-07-19**: HS HS20HS072RX (C5329582), 12-pin 0.5mm ZIF FPC. Confirm panel max SPI clock (~40MHz) and STM32H7 SPI can drive it. Plan backlight PWM on timer-output GPIO. ~~Verify panel backlight LED configuration (parallel vs series)~~ **CONFIRMED 2026-07-19**: 4 parallel white LEDs, Vf 3.0V, 80mA — FET + resistors only, no boost driver. Verify ST7789T3 variant works with `display_st7789v.c` driver. Confirm exact RST pin position from mechanical drawing before finalizing ZIF pinout.
- [x] **Keypad design**: **RESOLVED 2026-06-28** — SMD tactile switches on custom PCB traces (LOCKED). 5×4 matrix = 9 GPIO for ~20 keys. **Specific switch part RESOLVED 2026-07-19** — ALPS SKQGABE010 (C115351), 5.2×5.2×1.5mm, 160gf, 0.25mm travel, 1M cycles. KiCad model downloaded. Phase 2 prototyping uses off-the-shelf 4×4 matrix module + loose tactile buttons. See project-log.md 2026-06-28 Keypad Selection and 2026-07-19 Keypad Switch Selection.
- [x] ~~**High-current buck regulator**: Select specific part for modem VBAT rail (2A+ peaks, dedicated rail).~~ **RESOLVED 2026-06-28**: No buck regulator needed — VBAT powered directly from LiPo (3.4–4.3V matches LiPo operating range). Separate power net from 3.3V MCU rail, with 100–470µF bulk capacitance. See `docs/constraints.md` Power section.
- [x] **3.3V buck-boost regulator**: ~~Verify TPS630201 stock + 2A rating sufficient for all system loads (MCU + display + SD + codec). Confirm output voltage accuracy and ripple specs meet MCU requirements.~~ **RESOLVED 2026-07-19**: "TPS630201" was a phantom part number — corrected to **TPS63021DSJR** (LCSC C202140, fixed 3.3V, 4A switches / ~3A output, VSON-14/DSJ). In stock at JLC. Exceeds the original 2A spec with headroom. KiCad model downloaded. See project-log.md 2026-07-19 U4 Buck-Boost Correction.
- [ ] **Battery fuel gauge**: Verify MAX17048 I2C address doesn't conflict with ALC5651. Confirm fuel gauge characterization for the selected LiPo (MAX17048 has a characterization table; may need custom model for non-standard cells).
- [ ] **USB-C connector**: ~~Confirm 16-pin (USB 2.0) vs 24-pin (USB 3.x) — USB FS/HS only needs 16-pin.~~ **RESOLVED 2026-07-19**: 16-pin USB-C (USB 2.0) — formally locked. USB FS/HS only needs D+/D-.
- [ ] **ESD protection**: Confirm USBLC6-2SC6 and ESDA6V1-5SC6 footprints/placement near connectors.
- [ ] **Modem USB HS connector (rev1)**: Select USB-C vs micro-USB for the unpopulated modem USB footprint (2026-07-19 decision: include footprint, type TBD at schematic time).
- [ ] **GNSS antenna part**: Select specific U.FL GNSS antenna (2026-07-19 decision: include on rev1, part TBD).
- [ ] **Loudspeaker part**: Select specific loudspeaker transducer (2026-07-19 decision: include on rev1, part TBD).
- [x] **SIM/microSD connector sourcing**: ~~Evaluate combo vs separate socket availability~~ **RESOLVED 2026-07-19** — separate sockets (J3 SHOU HAN C7529386 + J4 Molex C164170), both hinged, both JLC-sourced.

---

## Sources Index

| Distributor | Use | Notes |
|-------------|-----|-------|
| [ST eStore](https://estore.st.com/) | STM32H743ZIT6 | Direct from ST, in stock |
| [DigiKey](https://www.digikey.com/) | MCU, codec, charger, LDO, level shifter, connectors | US-authorized, fast shipping |
| [Mouser](https://www.mouser.com/) | Same parts as DigiKey | Compare price/stock |
| [LCSC](https://www.lcsc.com/) | SIM7600NA-H (via JLC pre-order), passives | China-based, cheaper for some parts |
| [JLCPCB](https://jlcpcb.com/) | PCB fab + assembly + SIM7600NA-H part (pre-order C5380303) | Use for modem LGA assembly |
| [Waveshare](https://www.waveshare.com/) | SIM7600NA-H 4G HAT | Prototyping platform |
| [Adafruit](https://www.adafruit.com/) | Battery, display breakout, misc | Hobbyist-friendly |
| [BuyDisplay / EastRising](https://www.buydisplay.com/) | Raw TFT panels | Cheapest display option |
| [Taoglas](https://www.taoglas.com/) | Speaker, antenna | RF/audio components |
| [Analog Devices](https://www.analog.com/) | ~~MAX9880A datasheet + samples~~ **SUPERSEDED** — ALC5651 now used (JLC-sourced) | ~~Codec manufacturer~~ |
