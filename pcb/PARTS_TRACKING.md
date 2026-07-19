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
| U3 | MAX9880AETM+T | TQFN-48 | — | **Not on JLC** | [!] | [!] | [!] | **Needs Ultra Librarian (ADI) + buy from Mouser.** Not stocked on LCSC. |
| U4 | TPS630201 | VQFN-10 (DRC) | — | **Not on JLC** | [!] | [!] | [!] | **Needs Ultra Librarian (TI) + buy from DigiKey.** Only TPS63020DSJR (C15483, 3A version, VSON-14) is on LCSC — different part. |
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
| J7 | FPC connector 0.5mm pitch (display) | SMD FFC/FPC | TBD | JLC | [!] | [!] | [!] | **Blocker**: pin count depends on specific ST7789V panel — pick panel first |

## C. Switches (keypad matrix — ~20 switches)

| Ref | Part | Package | JLC Part # | Source | Symbol | Footprint | 3D | Notes |
|-----|------|---------|-----------|--------|--------|-----------|-----|-------|
| SW1–SW20 | Tactile switch 6x6mm (C&K PTS645 or ALPS SKQG) | 6x6x4.3mm SMD | TBD | JLC | [!] | [!] | [!] | **Decision needed**: pick specific switch (actuation force, height). JLC has many 6x6 tactiles. |

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
| L1 | 1.5µH inductor 2A+ (for TPS630201) | SMD | TBD | JLC | [ ] | [ ] | [ ] | **Critical**: must meet TPS630201 datasheet specs (inductance, saturation current, DCR). Pick from JLC. |
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
3. **Specific keypad switch** (SW1–SW20) — pick a JLC-stocked 6x6mm tactile
4. **Specific ST7789V panel** (J7) — needed to know FPC pin count
5. **Loudspeaker part** (LS2) — pick a JLC-stocked 20mm+ mylar speaker
6. **Microphone part** (MK1) — pick a JLC-stocked MEMS mic
7. **Earpiece confirmation** (LS1) — is Taoglas SPKM.10.8.A the final choice, or pick a JLC-stocked alternative?
8. **Power inductor for TPS630201** (L1) — must meet datasheet specs
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
