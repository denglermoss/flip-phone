# PCB Parts Library Tracking

> **Purpose**: Track the sourcing status of every part for the phone PCB. Update this as you download footprints/symbols/3D models from JLC, SnapEDA, Ultra Librarian, or create them from datasheets.
>
> **Library location**: `pcb/phone/lib/` — project-local KiCad library
> - `lib/passives.kicad_sym` — resistors, capacitors, inductors, ferrite beads, LEDs (16 symbols)
> - `lib/ics.kicad_sym` — ICs: MCU, modem, codec, power, level shifters, ESD, mic (12 symbols)
> - `lib/connectors.kicad_sym` — USB-C, SIM, microSD, U.FL, FPC, battery connectors (8 symbols)
> - `lib/electromech.kicad_sym` — tactile switches, crystals (2 symbols)
> - `lib/easyeda2kicad.pretty/` — footprint libraries (KiCad `.pretty` format)
> - `lib/easyeda2kicad.3dshapes/` — 3D STEP/WRL models
>
> **Library rebuild 2026-07-22**: All 38 symbols have correct pin electrical types
> (were all `unspecified`/`input` from easyeda2kicad auto-generation), `ki_description`
> properties (<20 char), and consistent property ordering. The original single
> `easyeda2kicad.kicad_sym` was split into 4 categorized libraries. Schematic
> references updated from `easyeda2kicad:SYM` to `passives:/ics:/connectors:SYM`.
> Old `easyeda2kicad.kicad_sym` and `missing_parts.kicad_sym` removed
> (superseded by the 4 split libraries).
>
> **How to use**: When you download a part from JLC/SnapEDA/etc., drop the files into the appropriate `lib/` subfolder and check the boxes below. Record the JLC part # (C-number) so the BOM can be filled in later.

## Status legend
- [ ] **Not sourced** — part not yet downloaded
- [x] **Sourced** — files downloaded and placed in `lib/`
- [~] **N/A** — part uses KiCad built-in library (no download needed)
- [!] **Blocker** — needs decision or datasheet work before sourcing

---

## A. ICs (downloaded from JLC via easyeda2kicad — 2026-07-19)

| Ref | Part | Package | JLC Part # | Source | Symbol | Footprint | 3D | Notes |
|-----|------|---------|-----------|--------|--------|-----------|-----|-------|
| U1 | STM32H743ZIT6 | LQFP-144 | C114408 | JLC (in stock) | [x] | [x] | [x] | ST OEM. 131 in stock. |
| U2 | SIM7600NA-H | LCC+LGA 119-pin | C5380303 | JLC (pre-order) | [x] | [x] | [!] | SIMCom OEM. 3D model not available (pre-order part). 135 pads in footprint — verify against HW Design Manual V1.08. |
| U3 | Realtek ALC5651-CG (dual I2S/PCM audio hub codec) | QFN-40-EP 5×5mm | C963633 | JLC (Extended, 407 in stock at LCSC) | [x] | [x] | [x] | **LOCKED 2026-07-19 (replaces MAX9880A).** Dual I2S/PCM interface audio codec — I2S-1 = PCM voice from SIM7600 (slave mode, PCM Mode A short-sync), I2S-2 = I2S music from MCU. ASRC per interface (asynchronous independent clocks). 100dBA DAC SNR, 94dBA ADC SNR. Stereo differential mic inputs + adjustable MICBIAS. Stereo cap-free headphone amp + line out + PDM output for ext Class-D. 1.8V analog (AVDD/DACREF/CPVDD), 1.2V digital core (internal LDO), 3.3V MICVDD. I2C control. QFN-40 5×5mm (smaller than MAX9880A's TQFN-48 6×6mm). **JLC Extended — no consignment needed** (eliminates the last Mouser consignment part). 407 in stock at LCSC. **PCM compatibility verified**: SIM7600 HW Design Manual V1.08 §3.6 = master mode, short sync, 16-bit linear, 2048/4096kHz BCLK; ALC5651 §7.5.1 supports PCM Mode A (short sync) in slave mode — exact match. KiCad model downloaded via easyeda2kicad: symbol `ALC5651-CG`, footprint `QFN-40_L5.0-W5.0-P0.40-BL-EP3.7`, 3D `QFN-40_L5.0-W5.0-H0.9-P0.4-BL-EP`. Datasheet: `docs/reference/alc5651.pdf` (Rev 0.9, 134pp — full pinout, registers, application circuit, timing, package dimensions). See project-log.md 2026-07-19 Codec Swap MAX9880A→ALC5651. |
| U4 | TPS63021DSJR | VSON-14 (DSJ, 3×4mm) + EP | C202140 | JLC (in stock) | [x] | [x] | [x] | **RESOLVED & LOCKED 2026-07-19.** Fixed 3.3V, 4A switches / ~3A output, Vin 1.8–5.5V. Downloaded via easyeda2kicad: symbol `TPS63021DSJR`, footprint `VSON-14_L4.0-W3.0-P0.50-BL-EP_TI_DSJ`, 3D `VSON-14_L4.0-W3.0-H1.0-P0.50`. **"TPS630201" was a phantom part number** (TI never made it) — carried in docs since 2026-06-28, corrected 2026-07-19. TPS63021 is the real fixed-3.3V part; TPS63020 (C15483) is the adjustable sibling (rejected — would need feedback divider). JLC-stocked → no consignment needed. See project-log.md 2026-07-19 U4 Buck-Boost Correction. |
| U5 | TPS7A0218PDBVR | SOT-23-5 | C3748843 | JLC | [x] | [x] | [x] | TI OEM. 1284 in stock. |
| U6 | MCP73831-2ACI/MC | TDFN-8 2×3mm | C150772 | JLC | [x] | [x] | [x] | Microchip OEM. 318 in stock. |
| U7 | MAX17048G+T10 | TDFN-8 2×2mm | C2682616 | JLC | [x] | [x] | [x] | ADI/Maxim OEM. 10228 in stock. |
| U8 | TXB0108PWR | TSSOP-20 | C53406 | JLC | [x] | [x] | [x] | TI OEM. **PWR (TSSOP-20) used instead of DGSR (VSSOP-20)** — DGSR (C44861261) failed EasyEDA API fetch. PWR matches block diagram spec, larger/easier to hand-solder. 45,922 in stock. |
| U9 | TXB0104D | SOIC-14 | C1549752 | JLC | [x] | [x] | [x] | TI OEM. 37 in stock. |
| U10 | USBLC6-2SC6 | SOT-23-6 | C7519 | JLC | [x] | [x] | [x] | ST OEM (swapped from TECH PUBLIC clone C2827654). |
| U11 | ESDA6V1-5SC6 | SOT-23-6 | C6650 | JLC | [x] | [x] | [x] | ST OEM (swapped from TECH PUBLIC clone C2827672). 3D model shared with C7519 (same SOT-23-6 package). |

## B. Connectors (download from JLC or SnapEDA)

| Ref | Part | Package | JLC Part # | Source | Symbol | Footprint | 3D | Notes |
|-----|------|---------|-----------|--------|--------|-----------|-----|-------|
| J1 | Korean Hroparts TYPE-C-31-M-12 (USB-C 16-pin, USB 2.0, 5A, 10K cycles) | SMD USB-C 7.35mm | C165948 | JLC (94,755 in stock) | [x] | [x] | [x] | **LOCKED 2026-07-19.** 16-pin USB 2.0 (matches block diagram spec — not 24-pin USB 3.x). 5A/20V (headroom for future power-path chargers; MCP73831 only needs 500mA). 10,000 mating cycles. Korean Hroparts Elec (HRO) — reputable Korean USB-C connector brand, higher tier than generic Shenzhen brands. $0.186 qty 5+. Low C-number (C165948) = long-standing JLC catalog part, well-supported for assembly. KiCad model downloaded via easyeda2kicad: symbol `TYPE-C-31-M-12`, footprint `USB-C_SMD-TYPE-C-31-M-12_1`, 3D `USB-C_SMD-TYPE-C-31-M-12_1` (.wrl + .step). See project-log.md 2026-07-19 J1 USB-C Selection. |
| J2 | Modem USB — test points only (DNP rev1) | 4 test pads (VBUS, D+, D-, GND) | N/A | KiCad built-in | [~] | [~] | [~] | **LOCKED 2026-07-19.** Test points only — no connector. Per SIM7600 HW Design Manual V1.08 §3.4: "The USB interface is a frequently used debug port; it is suggested to reserve test points." Future ecosystem respin routes modem USB through internal USB 2.0 hub (USB2514) to J1 — J2 will never be user-facing. Use KiCad built-in `TestPoint:TestPoint_Pad_D1.0mm` or similar. See project-log.md 2026-07-19 J2/J3/J4 Decisions. |
| J3 | SHOU HAN NANO SIM XG6P H1.35 (nano-SIM hinged 6-pin) | SMD hinged, 1.45mm height | C7529386 | JLC (Extended, 38,255 at LCSC / 22,052 at JLC) | [x] | [x] | [x] | **LOCKED 2026-07-19.** Nano-SIM (4FF), hinged lid, 6-pin (no card detect — SIM7600 manual §3.5.1 says optional, "keep USIM_DET open" if unused). 1.45mm height, -20°C to +85°C. $0.146 qty 5+. SHOU HAN (Shenzhen connector brand — lower tier than Amphenol/Molex but established, 38K+ stock). Amphenol G85D1160022HHR (C5429441) rejected — out of stock + expensive. Molex doesn't make nano-SIM hinged (78800 hinged = micro-SIM only; 104224 nano-SIM = push-pull only). Hinged chosen over push-push per user preference (top-loading, no lateral clearance needed). KiCad model downloaded via easyeda2kicad: symbol `NANO SIM XG6P H1.35`, footprint `SIM-SMD_NANO-SIM-XG6P-H1.35` (10 pads = 6 signal + 4 shell/mounting), 3D `.wrl` + `.step`. See project-log.md 2026-07-19 J3/J4 Sourcing. |
| J4 | Molex 472192001 (microSD hinged 8-pin) | SMD hinged, 1.9mm height | C164170 | JLC (16,177 at LCSC / 9,107 at JLC) | [x] | [x] | [x] | **LOCKED 2026-07-19.** MicroSD (TF), hinged lid, 8-pin, 1.10mm pitch. 1.9mm height, -20°C to +85°C (LCSC) / -40°C to +85°C (Molex datasheet). No card detect. 5,000 mating cycles. Gold-over-nickel contacts, stainless steel shell, shielded. Molex OEM (top-tier US connector brand). $0.765 qty 1, $0.502 qty 100+. Hinged chosen over push-push per user preference. KiCad model downloaded via easyeda2kicad: symbol `472192001`, footprint `TF-SMD_472192001` (12 pads = 8 signal + 4 shell/mounting), 3D `.wrl` + `.step`. See project-log.md 2026-07-19 J3/J4 Sourcing. |
| J5 | Hirose U.FL-R-SMT-1(10) (cellular antenna) | U.FL SMD | C88373 | JLC (53,805 in stock) | [x] | [x] | [x] | **LOCKED 2026-07-19.** Original U.FL connector from Hirose (invented the U.FL standard). 6 GHz, 50Ω, 53,805 in stock, $0.227 qty 5+. KiCad model downloaded via easyeda2kicad: symbol `U.FL-R-SMT-1`, footprint `ANT-SMD_UFL-R-SMT-1-10`, 3D `ANT-SMD_UFL-R-SMT-1-10` (.wrl + .step). See project-log.md 2026-07-19 B4/B6/B10 Sourcing. |
| J6 | Hirose U.FL-R-SMT-1(10) (GNSS antenna) | U.FL SMD | C88373 | (same as J5) | [x] | [x] | [x] | Same part as J5. |
| J7 | HDGC 0.5K-HX-12PWB (12-pin 0.5mm FPC, hinged lid, double-sided, 1mm) | SMD FFC/FPC | C2919494 | JLC | [x] | [x] | [x] | **LOCKED 2026-07-19.** For main display HS20HS072RX (C5329582), 12-pin 0.5mm ZIF. Pinout: 1=GND, 2=CS, 3=RS(DC), 4=SCL, 5=SDA, 6=RST, 7=NC, 8=I/O-VCC, 9=VCC, 10=LEDA, 11=LEDK, 12=GND. Double-sided contacts eliminate top/bottom orientation risk (FPC folds under panel — contacts face down). 1mm height — thinnest available. Same series as J8/J9/J10. **KiCad model downloaded** via easyeda2kicad: symbol `0.5K-HX-12PWB`, footprint `FPC-SMD_12P-P0.50_HDGC_0.5K-HX-12PWB` (14 pads = 12 signal + 2 mounting, verified). |
| J8 | HDGC 0.5K-HX-14PWB (14-pin 0.5mm FPC, hinged lid, double-sided, 1mm) | SMD FFC/FPC | C2919495 | JLC | [x] | [x] | [!] | **LOCKED 2026-07-19.** Hinge flex between main board and display daughterboard. ~13 signals on 14-pin FFC (1 spare). Same series as J7/J9/J10. Need matching 14-pin 0.5mm FFC cable (deferred to Phase 7 — length depends on hinge geometry). **KiCad model downloaded** via easyeda2kicad: symbol `0.5K-HX-14PWB`, footprint `FPC-SMD_14P-P0.50_HDGC_0.5K-HX-14PWB` (16 pads = 14 signal + 2 mounting, verified). **No 3D model** from JLC — 3D view will be missing for J8 (acceptable). |
| J9 | HDGC 0.5K-HX-14PWB (14-pin 0.5mm FPC, hinged lid, double-sided, 1mm) | SMD FFC/FPC | C2919495 | JLC | [x] | [x] | [!] | Same part as J8. Daughterboard side of hinge flex. No 3D model (same as J8). |
| J10 | HDGC 0.5K-HX-8PWB (8-pin 0.5mm FPC, hinged lid, double-sided, 1mm) | SMD FFC/FPC | C2919492 | JLC | [x] | [x] | [x] | **LOCKED 2026-07-19.** For outer display ER-TFT1.14-2 (BuyDisplay, $3.27), 8-pin 0.5mm FPC. Pinout: 1=LEDA, 2=GND, 3=RESET, 4=RS(DC), 5=SDA, 6=SCL, 7=VDD, 8=CS. Double-sided contacts (datasheet says top contact, but double-sided works either way). Same series as J7/J8/J9. **Panel purchased separately from PCB — user plugs into ZIF post-assembly.** **KiCad model downloaded** via easyeda2kicad: symbol `0.5K-HX-8PWB`, footprint `FPC-SMD_8P-P0.50_HDGC_0.5K-HX-8PWB` (10 pads = 8 signal + 2 mounting, verified). |
| J_BATT | JST S2B-PH-SM4-TB(LF)(SN) (battery, 2-pin PH, SMD right-angle) | SMD, P=2mm, 7.9×8.6×5.5mm | C295747 | JLC (Extended) | [x] | [x] | [x] | **LOCKED 2026-07-21.** Battery connector for single-cell LiPo. JST PH series, 2-pin, 2mm pitch, 2A rated (matches modem 2A TX bursts), SMD right-angle (chosen over through-hole C173752 — SMD goes through JLC pick-and-place, no wave soldering surcharge). Mates with standard JST-PH plugs pre-crimped on Adafruit/SparkFun/Amazon LiPo batteries. "Extended" = JLC sources on-demand. KiCad model downloaded via easyeda2kicad: symbol `S2B-PH-SM4-TB`, footprint `CONN-SMD_P2.00_S2B-PH-SM4-TB-LF-SN`, 3D `.wrl` + `.step`. **Battery itself is NOT JLC-sourced** (hazmat shipping) — buy separately from Adafruit/Amazon/AliExpress with JST-PH plug attached. See project-log.md 2026-07-21 Battery Connector. |

## C. Switches (keypad matrix — ~20 switches)

| Ref | Part | Package | JLC Part # | Source | Symbol | Footprint | 3D | Notes |
|-----|------|---------|-----------|--------|--------|-----------|-----|-------|
| SW1–SW20 | ALPS SKQGABE010 (5.2×5.2×1.5mm, 1.57N, 1M cycles) | 5.2×5.2×1.5mm SMD | C115351 | JLC (1,344 in stock; 41,590 at LCSC) | [x] | [x] | [x] | **LOCKED 2026-07-19.** Symbol+footprint+3D downloaded via easyeda2kicad. Force 160gf (in 160–180gf target), 1M cycle life (exceeds 300K min), 0.25mm travel (low end of numeric-keypad range — accepted for thinness), 1.5mm height (thinnest practical SMD tactile with push plate). Same 5.2×5.2mm footprint across SKQG stem-height variants (3.1/3.4/5.0mm) — can swap up without respin if feel is too snappy. ~$0.089 @ 50+ qty → ~$3.50 for 40 switches (2 boards × 20 + overage). See project-log.md 2026-07-19 Keypad Switch Selection. |

## D. Transducers

| Ref | Part | Package | JLC Part # | Source | Symbol | Footprint | 3D | Notes |
|-----|------|---------|-----------|--------|--------|-----------|-----|-------|
| LS1 | Earpiece speaker (10mm, 8Ω, DEFERRED) | 10mm round, wire leads | TBD | External (not JLC PCB-assembled) | [~] | [~] | [~] | **DEFERRED 2026-07-19.** Speakers are case-mounted mechanical parts (wire-soldered during final assembly, not PCB-assembled by JLC). No need to spec now — PCB will have wire solder pads (2× 1mm pads, ~5mm apart). Candidate: Taoglas SPKM.10.8.A (C6297624, 10mm, 8Ω, 500mW, 100Hz-11kHz, Irish brand) — 0 stock on JLC but available from other distributors. Revisit at Phase 7 (mechanical/enclosure). |
| LS2 | Loudspeaker (20mm+, 8Ω, DEFERRED) | 20mm+ round/square, wire leads | TBD | External (not JLC PCB-assembled) | [~] | [~] | [~] | **DEFERRED 2026-07-19.** Same as LS1 — case-mounted, not PCB-assembled. PCB will have wire solder pads. Candidates: CUI CMS0201KLX (C3312002, 20×20mm, 2W, 424Hz-20kHz, 9.5mm), PUI Audio AS02708CO-WR-R (C7217683, 27×20mm, 1W, 250Hz-20kHz, 6.3mm), PUI Audio AS02008MR-5-R (C3311274, 20mm, 500mW, 500Hz-4kHz, 3.8mm). Revisit at Phase 7. |
| MK1 | ZILLTEK ZTS6117 (MEMS analog microphone) | SMD-4P 2.75×1.85mm | C481300 | JLC (5,129 in stock) | [x] | [x] | [x] | **LOCKED 2026-07-19.** Analog output (pairs directly with ALC5651 differential mic inputs IN1P/IN2P/IN2N + adjustable MICBIAS 0.9×MICVDD ≈ 2.97V). -42dB sensitivity, 59dB SNR, omnidirectional, 1.5V-3.6V supply, 120µA current, 2.75×1.85×0.9mm. ZILLTEK (钰太) — Taiwanese MEMS sensor brand. $0.53. 5,129 in stock. Knowles SPU0410LR5H-QB (C2918083, gold standard, -38dB/63dB SNR) has 0 stock on JLC — ZILLTEK is best available. TDK InvenSense MMICT390200012 (C3171752) is EOL + PDM digital (more complex). KiCad model downloaded via easyeda2kicad: symbol `ZTS6117`, footprint `MIC-SMD_4P-L2.8-W1.9-P1.84-TL_ZTS6117`, 3D `MIC-SMD_4P-L2.8-W1.9-P1.84-TL_ZTS6117` (.wrl + .step). See project-log.md 2026-07-19 B4/B6/B10 Sourcing. |

## E. Crystal / Inductor / LEDs

| Ref | Part | Package | JLC Part # | Source | Symbol | Footprint | 3D | Notes |
|-----|------|---------|-----------|--------|--------|-----------|-----|-------|
| Y1 | ECS ECS-80-12-33Q-GN-TR (8MHz crystal HSE) | SMD 3225 4-pin (3.2×2.5mm) | C2595911 | JLC (150 in stock) | [x] | [x] | [x] | **LOCKED 2026-07-19.** 8MHz, 12pF CL, ±30ppm tolerance, ±30ppm stability, ESR 500Ω, -40 to +85°C. ECS Inc (US brand), AEC-Q200 automotive qualified. STM32H743 datasheet Table 34 confirms HSE characterized with 8MHz crystal at CL=10pF; Figure 20 shows "Typical application with an 8 MHz crystal." Load caps: with CL=12pF crystal and Cs≈3pF, CL1=CL2=18pF each. $1.39 qty 1, 150 in stock (enough for prototyping). LIMING 3225-8.00-12-10-10/A (C518155, ±10ppm, $0.32, 1,973 stock) is the production fallback — same SMD3225-4P footprint. KiCad model downloaded via easyeda2kicad: symbol `ECS-80-12-33Q-GN-TR`, footprint `CRYSTAL-SMD_4P-L3.2-W2.5-BL`, 3D `CRYSTAL-SMD_4P-L3.2-W2.5-BL` (.wrl + .step). See project-log.md 2026-07-19 B4/B6/B10 Sourcing. |
| L1 | Coilcraft XFL4020-152MEC (1.5µH, Isat 4.4A @20% drop, DCR 14.4mΩ, Irms 9.1A) | SMD 4×4×2.1mm | C3033018 | JLC (Extended, 757 in stock at LCSC) | [x] | [x] | [x] | **LOCKED 2026-07-19.** Datasheet-recommended part for TPS63021DSJR (TI SLVS916I Table 2 + Table 4 — XFL4020-152ME/ML family). 1.5µH ±20%, magnetic shielded. Isat 4.4A at 20% inductance drop (Coilcraft datasheet authoritative — LCSC's "4.6A" is at 30% drop; TI datasheet's "5.1A" uses a looser definition). DCR 14.4mΩ typ / 15.8mΩ max — lowest DCR available at this size → best efficiency on the 3.3V rail. Irms 9.1A (40°C rise) — way above any phone load. Isat 4.4A vs the datasheet's "20% above calculated peak" guidance (≥4.8A): adequate because (a) 4A is the TPS63021 switch current LIMIT (fault), not operating current; (b) actual phone peak currents are 2–3A (modem TX burst + display + audio + MCU); (c) calculated peak inductor current at 3A out buck mode ≈ 3.1A, at 3A out boost mode ≈ 3.7A — both well under 4.4A. Alternative rejected: Taiyo Yuden LSDND4040WKT1R5MM (C6653414, Isat 7A but DCR 35mΩ — 2.4× higher, noticeable efficiency hit on the most critical rail). The "ML" low-DCR variant from TI Table 4 is not on LCSC (broker-only). KiCad model downloaded via easyeda2kicad: symbol `XFL4020-152MEC`, footprint `IND-SMD_L4.0-W4.0-A`, 3D `IND-SMD_L4.0-W4.0-A` (.wrl + .step). See project-log.md 2026-07-19 L1 Inductor Selection. |
| D1–D3 | LEDs (status/notification) | 0603 | C99290 | JLC | [x] | [x] | [x] | LITEON LTST-C191TBKT blue LED 0603, 468nm. Downloaded. Pick color(s) — currently blue; may want different colors for status vs notification. |

## F. Passives (downloaded from JLC + KiCad built-in)

| Ref | Part | JLC Part # | Source | Notes |
|-----|------|-----------|--------|-------|
| 100nF decoupling caps | YAGEO CC0603KRX7R9BB104 | C14663 | JLC (downloaded) | 0603, X7R, 50V. 43M+ in stock. Use for per-IC decoupling. |
| 10uF bulk caps | muRata GRM21BR61H106KE43L | C440198 | JLC (downloaded) | 0805, X5R, 50V. 2.4M in stock. |
| 22uF bulk caps | muRata GRM21BR61A226ME51L | C77074 | JLC (downloaded 2026-07-21) | 0805, X5R, 10V, ±20%. Same GRM21BR family as 10uF bulk (C440198) — uniform 0805 bulk-cap footprint. Used for TPS63021 VOUT (3× 22µF on +3V3 to GND, per datasheet §8.2.2.4). 10V rating gives 3× margin on the 3.3V rail. KiCad symbol `GRM21BR61A226ME51L`, footprint `C0805` (shared with 10uF cap), 3D `C0805_L2.0-W1.3-H1.3`. |
| 4.7µF cap | muRata GRM188R61C475KE11D | C77045 | JLC (downloaded 2026-07-21) | 0603, X5R, 16V, ±10%. Used for MCP73831 VBUS bypass. KiCad symbol `GRM188R61C475KE11D`, footprint `C0603` (shared), 3D `C0603_L1.6-W0.8-H0.8`. |
| 1µF cap | muRata GRM188R61C105KA93D | C77404 | JLC (downloaded 2026-07-21) | 0603, X5R, 16V, ±10%. Used for TPS7A0218 input/output + MCU VDDA decoupling. KiCad symbol `GRM188R61C105KA93D`, footprint `C0603` (shared), 3D `C0603_L1.6-W0.8-H0.8`. |
| Bulk caps (VBAT) | 100–470µF ceramic + tantalum | TBD | JLC | Values TBD from schematic — VBAT rail stability |
| 1MΩ resistor | YAGEO RC0603JR-071ML | C107698 | JLC (downloaded 2026-07-21) | 0603, 1MΩ ±5%, 100mW, 75V, thick film. Used for TPS63021 EN pin pullup to VBAT (always-on). Matches our Yageo 0603 passive standard. KiCad symbol `RC0603JR-071ML`, footprint `R0603`. |
| 2kΩ resistor | YAGEO RC0603FR-072KL | C105576 | JLC (downloaded 2026-07-21) | 0603, 2kΩ ±1%, 100mW, thick film. Used for MCP73831 R_PROG (500mA charge current). 1% precision matters — sets charge current. KiCad symbol `RC0603FR-072KL`, footprint `R0603` (shared), 3D `R0603`. |
| 470Ω resistor | YAGEO RC0603JR-07470RL | C114433 | JLC (downloaded 2026-07-21) | 0603, 470Ω ±5%, 100mW, thick film. Used for LED current limiting. KiCad symbol `RC0603JR-07470RL`, footprint `R0603` (shared), 3D `R0603`. |
| 10kΩ resistor | YAGEO RC0603JR-0710KL | C99198 | JLC (downloaded 2026-07-21) | 0603, 10kΩ ±5%, 100mW, thick film. Used for STAT/PG/ALRT pullups. KiCad symbol `RC0603JR-0710KL`, footprint `R0603` (shared), 3D `R0603`. |
| 100kΩ resistor | YAGEO RC0603FR-07100KL | C14675 | JLC (downloaded 2026-07-21) | 0603, 100kΩ ±1%, 100mW, thick film. Used for VBUS voltage divider (high side). 1% precision matters for ADC reading. KiCad symbol `RC0603FR-07100KL`, footprint `R0603` (shared), 3D `R0603`. |
| 47kΩ resistor | YAGEO RC0603FR-0747KL | C105579 | JLC (downloaded 2026-07-21) | 0603, 47kΩ ±1%, 100mW, thick film. Used for VBUS voltage divider (low side). 1% precision matters for ADC reading. KiCad symbol `RC0603FR-0747KL`, footprint `R0603` (shared), 3D `R0603`. |
| 5.1kΩ resistor | YAGEO RC0603FR-075K1L | C105580 | JLC (downloaded 2026-07-21) | 0603, 5.1kΩ ±1%, 100mW, thick film. Used for USB-C CC pull-downs (Rd). 1% tolerance per USB-C spec for correct UFP identification. KiCad symbol `RC0603FR-075K1L`, footprint `R0603` (shared), 3D `R0603`. |
| 4.7kΩ resistor | YAGEO RC0603JR-074K7L | C105428 | JLC (downloaded 2026-07-21) | 0603, 4.7kΩ ±5%, 100mW, thick film. Used for I2C pullups. KiCad symbol `RC0603JR-074K7L`, footprint `R0603` (shared), 3D `R0603`. |
| Ferrite bead (VDDA) | muRata BLM18KG601SN1D | C85833 | JLC (downloaded 2026-07-21) | 0603, 600Ω ±25% @ 100MHz, 150mΩ DCR, 1.3A. Used for MCU VDDA analog rail isolation. muRata BLM18K high-current series. KiCad symbol `BLM18KG601SN1D`, footprint `L0603`, 3D `L0603_L1.6-W0.8-H0.5_BEAD`. |
| Other resistors | 0402/0603 | — | KiCad built-in `Device:R` | Pullups, dividers — values from schematic. Will download specific LCSC parts as values are finalized. |

---

## Decisions needed before all parts can be sourced

These block the parts marked [!] above:

1. **Modem USB connector type** (J2) — USB-C vs micro-USB for the unpopulated rev1 footprint
2. ~~**SIM/microSD: combo vs separate** (J3, J4) — check JLC stock for combo sockets~~ **RESOLVED 2026-07-19** — separate sockets, both sourced and KiCad models downloaded. See project-log.md 2026-07-19 J3/J4 Sourcing.
3. ~~**Specific keypad switch** (SW1–SW20)~~ **RESOLVED 2026-07-19** — ALPS SKQGABE010 (C115351). See project-log.md 2026-07-19 Keypad Switch Selection.
4. ~~**Specific ST7789V panel** (J7) — needed to know FPC pin count~~ **RESOLVED 2026-07-19** — HS HS20HS072RX (C5329582), 12-pin 0.5mm ZIF FPC. See project-log.md 2026-07-19 Display Panel Selection. J7 blocker cleared — now just need to source a 12-pin 0.5mm ZIF receptacle. New connectors J8-J10 added for flip form factor (hinge FFC + outer OLED).
5. **Loudspeaker part** (LS2) — pick a JLC-stocked 20mm+ mylar speaker
6. **Microphone part** (MK1) — pick a JLC-stocked MEMS mic
7. **Earpiece confirmation** (LS1) — is Taoglas SPKM.10.8.A the final choice, or pick a JLC-stocked alternative?
8. **Power inductor for TPS63021DSJR** (L1) — must meet datasheet specs *(part reference corrected from TPS630201 2026-07-19)*
9. **8MHz crystal** (Y1) — pick a specific JLC-stocked part

## Sourcing priority

1. **JLC parts library** (parts.jlcpcb.com) — for anything JLC will place. Get the C# for the BOM.
2. **Ultra Librarian** (manufacturer official) — for ST, TI, Microchip, ADI ICs not on JLC.
3. **SnapEDA** — fallback for anything not on Ultra Librarian.
4. **KiCad built-in** — passives, U.FL (if standard), LEDs, generic crystals.

## Workflow

1. Search JLC for each part below.
2. Download the KiCad footprint + symbol + 3D model (JLC offers these on each part page).
3. Drop files into `pcb/phone/lib/` (symbols into `.kicad_sym` libs, footprints into `easyeda2kicad.pretty/`, 3D into `easyeda2kicad.3dshapes/`).
4. Record the JLC C# in the table above.
5. Check the Symbol/Footprint/3D boxes.
6. Once all parts are sourced, import the libraries into KiCad (Preferences → Manage Libraries → add project-local `lib/` paths).
