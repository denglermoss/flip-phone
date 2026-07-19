# Revisit Prompt: PCB Parts Sourcing — Remaining Components

**Purpose**: Paste the prompt below into a new chat to work through the remaining parts selection and sourcing decisions for the phone PCB. This collects all open items that need either a part pick (search JLC) or a design decision before the schematic can be completed.

**STATUS: OPEN** — Created 2026-07-19 during the parts library build phase.

**Context**: The IC library is ~90% complete (9 of 11 ICs downloaded via `easyeda2kicad` from JLC/LCSC). What remains is mostly mechanical parts (connectors, switches, transducers) and two ICs not stocked on JLC. The KiCad project-local library is at `pcb/phone/lib/` (symbols in `easyeda2kicad.kicad_sym`, footprints in `easyeda2kicad.pretty/`, 3D models in `easyeda2kicad.3dshapes/`). Tracking doc: `pcb/PARTS_TRACKING.md`. BOM: `pcb/JLCPCB_BOM.xls`.

See `docs/project-log.md` (2026-07-19 Parts Library Build entry) and `pcb/PARTS_TRACKING.md` for current status.

---

## Prompt to paste into new chat:

I'm working on a custom cell phone project (STM32H743ZI + SIM7600NA-H + Zephyr RTOS + custom PCB, targeting US LTE with VoLTE on T-Mobile/Mint). The full project docs are in the `docs/` folder — please read them before responding. The block diagram is `docs/block-diagram.md`, constraints are `docs/constraints.md`, and the parts tracking doc is `pcb/PARTS_TRACKING.md`.

We're in the PCB design phase. I've already sourced and downloaded KiCad footprints/symbols/3D models for 9 of 11 ICs plus 3 passive/LED parts from JLC/LCSC using `easyeda2kicad`. The assembly method is locked: **JLCPCB PCBA, 2-board MOQ, LCSC-stocked parts + consignment for parts not on JLC.** The project-local KiCad library is at `pcb/phone/lib/`.

I need help completing the parts list. There are three categories of open items: (A) two ICs not on JLC, (B) mechanical parts that need JLC part selection, and (C) design decisions that block part selection. Please work through each item below.

### A. ICs not stocked on JLC (need Ultra Librarian + external distributor)

These two parts are not on LCSC. I need to download their KiCad models from Ultra Librarian (or the manufacturer's CAD library) and source them from Mouser/DigiKey for consignment to JLC.

1. **U3: MAX9880AETM+T** (Analog Devices/Maxim audio codec, TQFN-48 6×6mm)
   - Download KiCad V6+ symbol + footprint + 3D from Ultra Librarian (search ADI → MAX9880AETM+T)
   - Verify the footprint pad layout against the ADI datasheet (TQFN-48 with exposed pad)
   - Source from Mouser (check stock — BOM says 2,250 in stock)
   - Drop files into `pcb/phone/lib/` (may need to merge into the existing `easyeda2kicad.kicad_sym` or create a separate symbol lib)

2. **U4: TPS630201** (Texas Instruments buck-boost regulator, VQFN-10 / DRC package)
   - Download KiCad V6+ from Ultra Librarian (search TI → TPS630201)
   - **Critical**: verify the package is DRC (VQFN-10, 2.5×3mm with exposed pad) — not DSJ (VSON-14, which is the TPS63020 3A version)
   - Source from DigiKey or Mouser
   - Drop files into `pcb/phone/lib/`

### B. Mechanical parts — search JLC, pick a specific part, download via easyeda2kicad

For each item below, search JLC/LCSC for in-stock parts matching the specs, pick one (prefer OEM/brand-name, check stock quantity), and download the KiCad model. Record the C# in `pcb/PARTS_TRACKING.md` and `pcb/JLCPCB_BOM.xls`.

3. **J1: USB-C 16-pin receptacle** (SMD, USB 2.0, 16-pin — for charging + MCU USB)
   - Search JLC for "USB-C 16-pin" — pick a JLC-stocked part (e.g., GCT USB4081 or equivalent)
   - Verify it's 16-pin (not 24-pin) — the block diagram specifies 16-pin USB 2.0
   - Download footprint/symbol/3D

4. **J5, J6: U.FL antenna receptacles** (cellular + GNSS)
   - Option 1: Use KiCad built-in `Connector:U.FL_Molex_MCRW_73412-0110` (no download needed)
   - Option 2: Search JLC for a U.FL receptacle and download for BOM consistency
   - Recommend which approach is better for JLC assembly

5. **SW1–SW20: Tactile switches** (6×6mm SMD, for keypad matrix)
   - Search JLC for "6x6mm tactile switch SMD" — pick one part to use for all 20 switches
   - Considerations: actuation force (160gf is typical/comfortable), height (4.3mm is standard), JLC stock quantity (need 20+ with overage)
   - Download footprint/symbol/3D

6. **Y1: 8MHz crystal** (HSE for STM32H743, SMD 3225 4-pin)
   - Search JLC for "8MHz crystal 3225 4-pin" — pick a JLC-stocked part
   - Specs needed: 8MHz, load capacitance ~9-12pF (check STM32H743 datasheet for recommended CL), ±10-20ppm stability
   - Download footprint/symbol/3D

7. **L1: 1.5µH power inductor** (for TPS630201 buck-boost)
   - **Critical**: must meet TPS630201 datasheet specs. Check the datasheet (in `docs/reference/` if available, or ti.com) for:
     - Inductance: 1.5µH (datasheet recommended value)
     - Saturation current: ≥4A (TPS630201 has 4A switches — the TPS63020 3A version uses 1.5µH/4A, the TPS630201 may differ — verify)
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

13. **J7: Display FPC connector** (BLOCKED — needs specific ST7789V panel pick)
    - The display is locked as ST7789V SPI 2.0" 240×320, but the specific module/panel determines the FPC pin count and pitch
    - Decision needed: which specific ST7789V module? (e.g., a common breakout from AliExpress/eBay, or a specific manufacturer module)
    - Once the module is picked, the FPC connector (pitch, pin count, top/bottom contact) follows from its datasheet
    - Search for common ST7789V 2.0" modules and identify their FPC connectors
    - Consider: do we design for a specific module, or for a generic FPC with a standard pinout?

### Workflow

For each item:
1. Research the part (search JLC/LCSC, check datasheets in `docs/reference/` if applicable)
2. Present options with tradeoffs (for decisions) or a recommended pick (for mechanical parts)
3. Once I confirm, download the KiCad model (via `easyeda2kicad --full --lcsc_id=C####### --output "pcb/phone/lib"` for JLC parts, or Ultra Librarian for the two non-JLC ICs)
4. Update `pcb/PARTS_TRACKING.md` (check the boxes, record C#) and `pcb/JLCPCB_BOM.xls` (add the part with its C#)
5. After all parts are sourced, we'll import the library into KiCad and start the schematic

### Priority order

1. **A1, A2** (MAX9880A, TPS630201) — these are the only missing ICs; block schematic completion
2. **C13** (display panel pick) — blocks J7, which blocks layout planning
3. **B7** (inductor L1) — critical for power design, needs datasheet verification
4. **C11, C12** (J2, J3/J4 decisions) — block connector sourcing
5. **B3-B10** (remaining mechanical parts) — can proceed in parallel once decisions are made

### Notes

- All JLC parts should be OEM/brand-name where available (we already swapped TECH PUBLIC clones for ST originals on U10/U11)
- Check stock quantities — for 2-board assembly with overage, we need at least 5-10 of each part
- The SIM7600NA-H (C5380303) is a pre-order part — the footprint is downloaded but the part itself needs to be pre-ordered and lead time factored in
- Two consigned parts (MAX9880A, TPS630201) will be bought from Mouser/DigiKey and shipped to JLC — factor in shipping time
