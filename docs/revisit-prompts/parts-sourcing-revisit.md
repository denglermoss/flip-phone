# Revisit Prompt: PCB Parts Sourcing — Remaining Components

**Purpose**: Paste the prompt below into a new chat to work through the remaining parts selection and sourcing decisions for the phone PCB. This collects all open items that need either a part pick (search JLC) or a design decision before the schematic can be completed.

**STATUS: OPEN** — Created 2026-07-19 during the parts library build phase.

**Context**: The IC library is ~90% complete (9 of 11 ICs downloaded via `easyeda2kicad` from JLC/LCSC). What remains is mostly mechanical parts (connectors, switches, transducers) and two ICs not stocked on JLC. The KiCad project-local library is at `pcb/phone/lib/` (symbols in `easyeda2kicad.kicad_sym`, footprints in `easyeda2kicad.pretty/`, 3D models in `easyeda2kicad.3dshapes/`). Tracking doc: `pcb/PARTS_TRACKING.md` (single source of truth for C-numbers and sourcing status).

See `docs/project-log.md` (2026-07-19 Parts Library Build entry) and `pcb/PARTS_TRACKING.md` for current status.

---

## Prompt to paste into new chat:

I'm working on a custom cell phone project (STM32H743ZI + SIM7600NA-H + Zephyr RTOS + custom PCB, targeting US LTE with VoLTE on T-Mobile/Mint). The full project docs are in the `docs/` folder — please read them before responding. The block diagram is `docs/block-diagram.md`, constraints are `docs/constraints.md`, and the parts tracking doc is `pcb/PARTS_TRACKING.md`.

We're in the PCB design phase. I've already sourced and downloaded KiCad footprints/symbols/3D models for 9 of 11 ICs plus 3 passive/LED parts from JLC/LCSC using `easyeda2kicad`. The assembly method is locked: **JLCPCB PCBA, 2-board MOQ, LCSC-stocked parts + consignment for parts not on JLC.** The project-local KiCad library is at `pcb/phone/lib/`.

I need help completing the parts list. There are three categories of open items: (A) two ICs not on JLC, (B) mechanical parts that need JLC part selection, and (C) design decisions that block part selection. Please work through each item below.

### A. ICs not stocked on JLC (need Ultra Librarian + external distributor)

These two parts are not on LCSC. I need to download their KiCad models from Ultra Librarian (or the manufacturer's CAD library) and source them from Mouser/DigiKey for consignment to JLC.

1. **U3: MAX9880AETM+T** (Analog Devices/Maxim audio codec, TQFN-48 6×6mm) — **RESOLVED 2026-07-19**
   - Ultra Librarian KiCad v6 package downloaded by user and integrated into `pcb/phone/lib/`:
     - Symbol: `lib/symbols/ultralibrarian.kicad_sym` (separate lib from easyeda2kicad)
     - Footprint: `lib/footprints.pretty/21-0141I_T4866-1_MXM.kicad_mod` (TQFN-48 + exposed pad, 49 pads verified)
     - 3D model: not available from Ultra Librarian (acceptable — footprint+symbol suffice)
   - Sourcing: Mouser consignment (2,250 in stock, $2.23 qty 1) → ship to JLC with PCB fab order
   - Only remaining consignment part (U4 was also consignment but is now JLC-stocked)
   - See `docs/project-log.md` 2026-07-19 U4 Buck-Boost Correction entry

2. **U4: TPS63021DSJR** (Texas Instruments buck-boost regulator, VSON-14 / DSJ package) — **RESOLVED & LOCKED 2026-07-19**
   - **"TPS630201" was a phantom part number** — TI never manufactured it. Carried in docs since 2026-06-28. The original prompt text below (kept for history) referenced a non-existent part and a confused package warning.
   - **Real part**: TPS63021DSJR — fixed 3.3V output, 4A switches / ~3A output, Vin 1.8–5.5V, VSON-14 (DSJ, 3×4mm) with exposed pad. TI "Active Production".
   - LCSC C202140, in stock at JLC → **no consignment needed** (downloaded via easyeda2kicad like the other JLC parts).
   - Alternative rejected: TPS63020DSJR (C15483, adjustable, same DSJ package) — would need 2 external resistors for 3.3V; TPS63021 fixed-3.3V matches BOM spec exactly and is JLC-sourced.
   - KiCad model: symbol `TPS63021DSJR`, footprint `VSON-14_L4.0-W3.0-P0.50-BL-EP_TI_DSJ`, 3D `VSON-14_L4.0-W3.0-H1.0-P0.50`.
   - ~~Download KiCad V6+ from Ultra Librarian (search TI → TPS630201)~~
   - ~~**Critical**: verify the package is DRC (VQFN-10, 2.5×3mm with exposed pad) — not DSJ (VSON-14, which is the TPS63020 3A version)~~ — **this warning was backwards**: DSJ (VSON-14) is the 4A family we want; DRC (VSON-10) is the smaller 1.8A TPS6300x family. There is no 4A part in DRC.
   - See `docs/project-log.md` 2026-07-19 U4 Buck-Boost Correction for full rationale.

### B. Mechanical parts — search JLC, pick a specific part, download via easyeda2kicad

For each item below, search JLC/LCSC for in-stock parts matching the specs, pick one (prefer OEM/brand-name, check stock quantity), and download the KiCad model. Record the C# in `pcb/PARTS_TRACKING.md`.

3. **J1: USB-C 16-pin receptacle** (SMD, USB 2.0, 16-pin — for charging + MCU USB)
   - Search JLC for "USB-C 16-pin" — pick a JLC-stocked part (e.g., GCT USB4081 or equivalent)
   - Verify it's 16-pin (not 24-pin) — the block diagram specifies 16-pin USB 2.0
   - Download footprint/symbol/3D

4. **J5, J6: U.FL antenna receptacles** (cellular + GNSS)
   - Option 1: Use KiCad built-in `Connector:U.FL_Molex_MCRW_73412-0110` (no download needed)
   - Option 2: Search JLC for a U.FL receptacle and download for BOM consistency
   - Recommend which approach is better for JLC assembly

5. **SW1–SW20: Tactile switches** (5.2×5.2mm SMD, for keypad matrix) — **RESOLVED 2026-07-19**
   - **Selected**: ALPS Alpine SKQGABE010 (LCSC C115351). 5.2×5.2×1.5mm, 1.57N (160gf), 0.25mm travel, 1M cycle life. KiCad model downloaded to `pcb/phone/lib/`.
   - See `docs/project-log.md` 2026-07-19 Keypad Switch Selection for full rationale and tradeoffs.

6. **Y1: 8MHz crystal** (HSE for STM32H743, SMD 3225 4-pin)
   - Search JLC for "8MHz crystal 3225 4-pin" — pick a JLC-stocked part
   - Specs needed: 8MHz, load capacitance ~9-12pF (check STM32H743 datasheet for recommended CL), ±10-20ppm stability
   - Download footprint/symbol/3D

7. **L1: 1.5µH power inductor** (for TPS63021DSJR buck-boost) — *part reference corrected from TPS630201 2026-07-19*
   - **Critical**: must meet TPS63021DSJR datasheet specs (TI SLVS916I). Check the datasheet (in `docs/reference/` if available, or ti.com) for:
     - Inductance: 1.5µH (datasheet recommended value for the TPS6302x family)
     - Saturation current: ≥4A (TPS63021 has 4A switches — same as the TPS63020 sibling)
     - DCR: as low as possible (efficiency)
     - Recommended part in datasheet: Coilcraft XFL4020-152ML (4×4mm) — check if JLC stocks this or an equivalent
   - Search JLC for "1.5uH inductor 4A SMD" — pick a part meeting the specs
   - Download footprint/symbol/3D

8. **LS1: Earpiece speaker** (10mm round, 8Ω)
   - The BOM references Taoglas SPKM.10.8.A — check if JLC stocks it
   - If not, search JLC for "10mm speaker 8 ohm SMD" — pick an alternative
   - Download footprint/symbol/3D

9. **LS2: Loudspeaker** (20mm+ mylar, for speakerphone/ringtones)
   - Search JLC for "20mm speaker mylar SMD" or "28mm speaker SMD" — pick a JLC-stocked part
   - Considerations: impedance (4-8Ω), power handling (≥0.5W for ringtones), mounting type (SMD vs through-hole)
   - Download footprint/symbol/3D

10. **MK1: Microphone** (MEMS or electret, for phone calls)
    - Search JLC for "MEMS microphone" — pick a JLC-stocked part (e.g., Knowles SPQ series, or generic)
    - Considerations: sensitivity, SNR, directivity (omnidirectional for phone), interface (analog or PDM/I2S — check what MAX9880A expects on its mic input)
    - Download footprint/symbol/3D

### C. Design decisions blocking part selection

These need a decision before the corresponding part can be sourced. Present the tradeoffs and let me decide.

11. **J2: Modem USB connector type** (DNP on rev1 — footprint only)
    - The block diagram says the modem's USB 2.0 HS port routes to a connector footprint on rev1, populated on a future ecosystem respin.
    - Decision: USB-C, micro-USB, or just unpopulated pads / test points?
    - Tradeoffs: USB-C is future-proof but adds complexity; micro-USB is simpler but obsolete; test points are cheapest but not user-friendly for the future ecosystem use case
    - Note: This is DNP on rev1, so the footprint choice only matters for the future respin

12. **J3/J4: SIM + microSD — combo socket vs separate sockets**
    - Option A: Combo SIM+microSD socket (one part, saves space, common in phones)
    - Option B: Separate nano-SIM socket + separate microSD socket
    - Tradeoffs: combo saves board space and is more phone-like; separate is easier to source individually and more flexible for layout
    - Search JLC for both options and compare availability/price/footprint size
    - Check if the SIM7600 HW Design Manual has a recommended socket part

13. **J7: Display FPC connector** ~~(BLOCKED — needs specific ST7789V panel pick)~~ — **RESOLVED 2026-07-19**
    - ~~The display is locked as ST7789V SPI 2.0" 240×320, but the specific module/panel determines the FPC pin count and pitch~~
    - ~~Decision needed: which specific ST7789V module?~~ **RESOLVED**: HS HS20HS072RX (LCSC C5329582) — 2.0" IPS TFT, ST7789T3, 12-pin 0.5mm ZIF FPC, 4 parallel LEDs, $3.42, 1786 in stock. JLC-assemblable. See project-log.md 2026-07-19 Display Panel Selection.
    - **Flip form factor also locked 2026-07-19**: two PCBs (main + display daughterboard) + hinge FFC. New connectors J8-J10 added to PARTS_TRACKING.md (hinge FFC 14-pin + outer OLED). See project-log.md 2026-07-19 Flip Form Factor entry.
    - **Remaining**: source the 12-pin 0.5mm ZIF receptacle for J7, 14-pin 0.5mm ZIF + FFC for J8/J9, and OLED connector for J10.

### Workflow

For each item:
1. Research the part (search JLC/LCSC, check datasheets in `docs/reference/` if applicable)
2. Present options with tradeoffs (for decisions) or a recommended pick (for mechanical parts)
3. Once I confirm, download the KiCad model (via `easyeda2kicad --full --lcsc_id=C####### --output "pcb/phone/lib"` for JLC parts, or Ultra Librarian for the two non-JLC ICs)
4. Update `pcb/PARTS_TRACKING.md` (check the boxes, record C#)
5. After all parts are sourced, we'll import the library into KiCad and start the schematic

### Priority order

1. ~~**A1, A2** (MAX9880A, TPS630201) — these are the only missing ICs; block schematic completion~~ **RESOLVED 2026-07-19**: A1 (MAX9880A) integrated from Ultra Librarian → `pcb/phone/lib/`. A2 (TPS630201→TPS63021DSJR) — phantom part number corrected, downloaded from JLC (C202140). Both ICs now have KiCad models. See project-log.md 2026-07-19.
2. ~~**C13** (display panel pick) — blocks J7, which blocks layout planning~~ **RESOLVED 2026-07-19**: HS HS20HS072RX (C5329582) selected. 12-pin 0.5mm ZIF FPC. Flip form factor also locked (two boards + hinge FFC). J7 blocker cleared. New connectors J8-J10 added (hinge FFC + outer OLED). See project-log.md 2026-07-19.
3. **B7** (inductor L1) — critical for power design, needs TPS63021DSJR datasheet verification *(part ref corrected from TPS630201)*
4. **C11, C12** (J2, J3/J4 decisions) — block connector sourcing
5. **B3-B10** (remaining mechanical parts) — can proceed in parallel once decisions are made

### Notes

- All JLC parts should be OEM/brand-name where available (we already swapped TECH PUBLIC clones for ST originals on U10/U11)
- Check stock quantities — for 2-board assembly with overage, we need at least 5-10 of each part
- The SIM7600NA-H (C5380303) is a pre-order part — the footprint is downloaded but the part itself needs to be pre-ordered and lead time factored in
- ~~Two consigned parts (MAX9880A, TPS630201) will be bought from Mouser/DigiKey and shipped to JLC — factor in shipping time~~ **Updated 2026-07-19**: Only ONE consignment part remains (MAX9880A from Mouser). TPS630201 was a phantom part number — corrected to TPS63021DSJR (LCSC C202140, JLC-stocked, no consignment needed).
