# PCB Parts Library Tracking

> **Purpose**: Track the sourcing status of every part for the phone PCB. Update this as you download footprints/symbols/3D models from JLC, SnapEDA, Ultra Librarian, or create them from datasheets.
>
> **Library location**: `pcb/phone/lib/` — project-local KiCad library
> - `lib/symbols/` — `.kicad_sym` symbol libraries
> - `lib/footprints.pretty/` — footprint libraries (KiCad `.pretty` format)
> - `lib/3dshapes/` — 3D STEP/WRL models
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
| U3 | MAX9880AETM+T | TQFN-48 6×6mm + EP | — | **Not on JLC** (Mouser consignment) | [x] | [x] | [!] | **RESOLVED 2026-07-19.** Ultra Librarian KiCad v6 package integrated: symbol `lib/symbols/ultralibrarian.kicad_sym`, footprint `lib/footprints.pretty/21-0141I_T4866-1_MXM.kicad_mod` (49 pads = 48 pins + exposed pad, verified). 3 pad-density variants shipped (MXM nominal + MXM-L/M); symbol references nominal MXM. **No 3D model** from Ultra Librarian — 3D view will be missing for U3 (acceptable). Sourcing: Mouser (2,250 in stock, $2.23 qty 1) → consign to JLC with PCB fab order. Only remaining consignment part. |
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
| J1 | USB-C 16-pin (GCT USB4081 or equiv) | SMD USB-C | TBD | JLC | [ ] | [ ] | [ ] | Locked: 16-pin USB 2.0. Pick a specific JLC-stocked part. |
| J2 | Modem USB (USB-C or micro-USB) — DNP rev1 | TBD | TBD | JLC | [!] | [!] | [!] | **Decision needed**: USB-C vs micro-USB for unpopulated footprint |
| J3 | Nano SIM socket (GCT SIM8066 or Molex) | SMD push-push | TBD | JLC | [ ] | [ ] | [ ] | Sourcing decision: combo vs separate (see J4) |
| J4 | MicroSD socket (or combo SIM+SD) | SMD push-push | TBD | JLC | [!] | [!] | [!] | **Decision needed**: combo SIM+SD socket vs separate J3+J4 |
| J5 | U.FL receptacle (cellular antenna) | U.FL SMD | TBD | JLC or KiCad built-in | [~] | [~] | [~] | KiCad has `Connector:U.FL_Molex_MCRW_73412-0110` built-in. Confirm or download from JLC. |
| J6 | U.FL receptacle (GNSS antenna) | U.FL SMD | TBD | (same as J5) | [~] | [~] | [~] | Same part as J5 |
| J7 | HDGC 0.5K-HX-12PWB (12-pin 0.5mm FPC, hinged lid, double-sided, 1mm) | SMD FFC/FPC | C2919494 | JLC | [x] | [x] | [x] | **LOCKED 2026-07-19.** For main display HS20HS072RX (C5329582), 12-pin 0.5mm ZIF. Pinout: 1=GND, 2=CS, 3=RS(DC), 4=SCL, 5=SDA, 6=RST, 7=NC, 8=I/O-VCC, 9=VCC, 10=LEDA, 11=LEDK, 12=GND. Double-sided contacts eliminate top/bottom orientation risk (FPC folds under panel — contacts face down). 1mm height — thinnest available. Same series as J8/J9/J10. **KiCad model downloaded** via easyeda2kicad: symbol `0.5K-HX-12PWB`, footprint `FPC-SMD_12P-P0.50_HDGC_0.5K-HX-12PWB` (14 pads = 12 signal + 2 mounting, verified). |
| J8 | HDGC 0.5K-HX-14PWB (14-pin 0.5mm FPC, hinged lid, double-sided, 1mm) | SMD FFC/FPC | C2919495 | JLC | [x] | [x] | [!] | **LOCKED 2026-07-19.** Hinge flex between main board and display daughterboard. ~13 signals on 14-pin FFC (1 spare). Same series as J7/J9/J10. Need matching 14-pin 0.5mm FFC cable (deferred to Phase 7 — length depends on hinge geometry). **KiCad model downloaded** via easyeda2kicad: symbol `0.5K-HX-14PWB`, footprint `FPC-SMD_14P-P0.50_HDGC_0.5K-HX-14PWB` (16 pads = 14 signal + 2 mounting, verified). **No 3D model** from JLC — 3D view will be missing for J8 (acceptable). |
| J9 | HDGC 0.5K-HX-14PWB (14-pin 0.5mm FPC, hinged lid, double-sided, 1mm) | SMD FFC/FPC | C2919495 | JLC | [x] | [x] | [!] | Same part as J8. Daughterboard side of hinge flex. No 3D model (same as J8). |
| J10 | HDGC 0.5K-HX-8PWB (8-pin 0.5mm FPC, hinged lid, double-sided, 1mm) | SMD FFC/FPC | C2919492 | JLC | [x] | [x] | [x] | **LOCKED 2026-07-19.** For outer display ER-TFT1.14-2 (BuyDisplay, $3.27), 8-pin 0.5mm FPC. Pinout: 1=LEDA, 2=GND, 3=RESET, 4=RS(DC), 5=SDA, 6=SCL, 7=VDD, 8=CS. Double-sided contacts (datasheet says top contact, but double-sided works either way). Same series as J7/J8/J9. **Panel purchased separately from PCB — user plugs into ZIF post-assembly.** **KiCad model downloaded** via easyeda2kicad: symbol `0.5K-HX-8PWB`, footprint `FPC-SMD_8P-P0.50_HDGC_0.5K-HX-8PWB` (10 pads = 8 signal + 2 mounting, verified). |

## C. Switches (keypad matrix — ~20 switches)

| Ref | Part | Package | JLC Part # | Source | Symbol | Footprint | 3D | Notes |
|-----|------|---------|-----------|--------|--------|-----------|-----|-------|
| SW1–SW20 | ALPS SKQGABE010 (5.2×5.2×1.5mm, 1.57N, 1M cycles) | 5.2×5.2×1.5mm SMD | C115351 | JLC (1,344 in stock; 41,590 at LCSC) | [x] | [x] | [x] | **LOCKED 2026-07-19.** Symbol+footprint+3D downloaded via easyeda2kicad. Force 160gf (in 160–180gf target), 1M cycle life (exceeds 300K min), 0.25mm travel (low end of numeric-keypad range — accepted for thinness), 1.5mm height (thinnest practical SMD tactile with push plate). Same 5.2×5.2mm footprint across SKQG stem-height variants (3.1/3.4/5.0mm) — can swap up without respin if feel is too snappy. ~$0.089 @ 50+ qty → ~$3.50 for 40 switches (2 boards × 20 + overage). See project-log.md 2026-07-19 Keypad Switch Selection. |

## D. Transducers

| Ref | Part | Package | JLC Part # | Source | Symbol | Footprint | 3D | Notes |
|-----|------|---------|-----------|--------|--------|-----------|-----|-------|
| LS1 | Earpiece 10mm 8Ω (Taoglas SPKM.10.8.A) | 10mm round | TBD | SnapEDA or datasheet | [!] | [!] | [!] | **Blocker**: confirm Taoglas part is the final choice, or pick a JLC-stocked speaker |
| LS2 | Loudspeaker 20mm+ mylar | TBD | TBD | JLC | [!] | [!] | [!] | **Decision needed**: pick specific loudspeaker |
| MK1 | Microphone (MEMS or electret) | TBD | TBD | JLC | [!] | [!] | [!] | **Decision needed**: pick MEMS mic (e.g., Knowles SPQ) |

## E. Crystal / Inductor / LEDs

| Ref | Part | Package | JLC Part # | Source | Symbol | Footprint | 3D | Notes |
|-----|------|---------|-----------|--------|--------|-----------|-----|-------|
| Y1 | 8MHz crystal HSE | SMD 3225 4-pin | TBD | JLC | [ ] | [ ] | [ ] | Pick a specific 8MHz crystal on JLC |
| L1 | 1.5µH inductor 2A+ (for TPS63021DSJR) | SMD | TBD | JLC | [ ] | [ ] | [ ] | **Critical**: must meet TPS63021DSJR datasheet specs (inductance, saturation current, DCR). Pick from JLC. *(Part reference corrected from TPS630201 2026-07-19.)* |
| D1–D3 | LEDs (status/notification) | 0603 | C99290 | JLC | [x] | [x] | [x] | LITEON LTST-C191TBKT blue LED 0603, 468nm. Downloaded. Pick color(s) — currently blue; may want different colors for status vs notification. |

## F. Passives (downloaded from JLC + KiCad built-in)

| Ref | Part | JLC Part # | Source | Notes |
|-----|------|-----------|--------|-------|
| 100nF decoupling caps | YAGEO CC0603KRX7R9BB104 | C14663 | JLC (downloaded) | 0603, X7R, 50V. 43M+ in stock. Use for per-IC decoupling. |
| 10uF bulk caps | muRata GRM21BR61H106KE43L | C440198 | JLC (downloaded) | 0805, X5R, 50V. 2.4M in stock. |
| Bulk caps (VBAT) | 100–470µF ceramic + tantalum | TBD | JLC | Values TBD from schematic — VBAT rail stability |
| Resistors | 0402/0603 | — | KiCad built-in `Device:R` | Pullups, dividers — values from schematic |

---

## Decisions needed before all parts can be sourced

These block the parts marked [!] above:

1. **Modem USB connector type** (J2) — USB-C vs micro-USB for the unpopulated rev1 footprint
2. **SIM/microSD: combo vs separate** (J3, J4) — check JLC stock for combo sockets
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
3. Drop files into `pcb/phone/lib/{symbols,footprints.pretty,3dshapes}/`.
4. Record the JLC C# in the table above.
5. Check the Symbol/Footprint/3D boxes.
6. Once all parts are sourced, import the libraries into KiCad (Preferences → Manage Libraries → add project-local `lib/` paths).
