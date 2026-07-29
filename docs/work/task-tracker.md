---
status: active
updated: 2026-07-28
---
# Task Tracker — Path to Assembled PCB

> **Created**: 2026-07-22
> **Goal**: Physically assembled custom cell phone PCB in hand (soldered, parts on board — no power-on/bring-up in this scope).
> **Assembly path**: Full DIY assembly (no JLC PCBA). Learning goal, not just cost savings.
> **Scope**: Hardware-only (schematic → layout → fab → assembly). Firmware port to custom PCB is a separate later effort.
> **Form factor**: MPCIe primary (SIM7600NA-H-PCIE, Techship S2-109KS-Z30G9), LGA fallback.
>
> **How to use**: Work top-to-bottom. Each phase has tasks with checkboxes. Update status as you go. Open questions/decisions are called out inline — resolve them before proceeding past their gate. When a phase completes, update `docs/ref/project-log.md` and the Progress Tracking table at the bottom of this doc.

---

## Current State (verified 2026-07-22)

| Area | Status |
|------|--------|
| Phase 1 (Component selection) | **DONE** — all major components locked (MCU, modem, codec, display, keypad, power) |
| Phase 2 (HAT prototyping) | **DONE** — MVP achieved 2026-07-13 (VoLTE calls, audio, SMS, GNSS, display, keypad, LVGL UI on Nucleo+HAT) |
| Phase 3 (Schematic) | **IN PROGRESS** — power section schemed + reviewed (2026-07-22); all other sections not started |
| Phase 4 (PCB layout) | **NOT STARTED** |
| Phase 5 (Assembly) | **NOT STARTED** |
| Parts library | **DONE** — all 38 parts have KiCad symbols/footprints/3D models (no consignment parts) |
| MPCIe PCM verification | **CONFIRMED (high confidence ~90%)** — see Open Question O1 below |

---

## Open Questions / Decisions Requiring User Input

These are gates — resolve before proceeding past the indicated phase. Numbered O1–O13 for reference.

### Gates before schematic completion (Phase 3)

- **O1 — MPCIe PCM confirmation with Techship** *(gate: before buying modem, not before schematic)*
  - **Status**: Verified from V1.03 manual + Techship spec sheet (high confidence ~90%). Part S2-109KS-Z30G9 ends in "PCIE" (not "PCIEA"), Techship lists PCM as "o" (supported), manual confirms PCIE variant = PCM active on pins 45/47/49/51, PCIEA = PCM NC.
  - **Action**: Optional email to Techship for 100% certainty before purchasing. Draft email in `docs/ref/research-notes.md` (add if not there). Not a blocker for schematic — proceed with MPCIe PCM wiring.
  - **Resolved by**: Subagent verification 2026-07-22 (this session).

- **O2 — MPCIe power-on method** *(gate: before modem schematic section finalized)*
  - **Status**: RESOLVED 2026-07-22, **UPDATED 2026-07-24**. SIM7600 MPCIe auto-powers on when 3.3V is applied — no PWRKEY pin. ~~Load switch on +3.3V to modem, controlled by MCU GPIO `MCU_MODEM_PWR_EN` (PE6, pin 5), recommended for power control and graceful shutdown.~~ **SUPERSEDED 2026-07-24**: No load switch — SIM7600 has robust sleep mode (<5mA, maintains call/SMS reception) + dedicated PWRKEY pin. Load switch is redundant. MCU_MODEM_PWR_EN (PE6) is now no_connect. System on/off is controlled by a slide switch (SW21) on the TPS63021 EN pin instead.
  - **Blocks**: ~~Modem section power wiring, MCU GPIO allocation~~ — unblocked.

- **O3 — MCU peripheral-to-pin mapping** *(gate: before any non-power schematic section)*
  - **Status**: RESOLVED 2026-07-22. Full pin assignment in `docs/work/mcu-pin-assignment.md` (73 pins assigned, ~60 spare). All pin numbers verified against STM32H743ZI datasheet DS12110 Rev 11 Table 9.
  - **Blocks**: ~~All schematic sections except power~~ — unblocked.

- **O4 — ALC5651 DBVDD pinout** *(gate: before codec schematic section)*
  - **Status**: RESOLVED 2026-07-22. DBVDD is a SINGLE shared pin (pin 39) — both I2S ports share one voltage domain. Decision: DBVDD=1.8V. I2S-1 direct to modem, I2S-2 via SN74AXC4T774 level shifter (U12). I2C uses 1.8V pullups.
  - **Blocks**: ~~Codec power wiring~~ — unblocked.

- **O5 — ALC5651 analog supply current** *(gate: before codec schematic section)*
  - **Status**: RESOLVED 2026-07-22. Power consumption ≤13mW (~7mA at 1.8V) — well under 50mA. U9 (TPS7A0218) retained (MPCIe doesn't expose VDD_1V8, and decoupling codec from modem power state is desirable).
  - **Blocks**: ~~Codec power wiring~~ — unblocked.

### Gates before PCB layout (Phase 4)

- **O6 — Layer stackup: 2-layer vs 4-layer** *(gate: before layout starts)*
  - **Status**: CONFIRMED 2026-07-22. 4-layer (RF impedance control for 50Ω antenna traces, power distribution for 2A modem bursts, solid ground reference for high-speed USB/SPI, fine-pitch fanout).
  - **4-layer stackup**: L1 Top (signals/components) / L2 Inner1 (solid GND plane) / L3 Inner2 (+3.3V power plane, +BATT polygon) / L4 Bottom (signals/components).
  - **Blocks**: All layout tasks.

- **O7 — Board outline dimensions** *(gate: before placement)*
  - **Status**: OVERRIDDEN 2026-07-22. Target 60×85mm (55×78mm was too aggressive for DIY assembly — need room for hand-soldering iron access, rework, connector clearance). Final dimensions set during KiCad placement.
  - **Blocks**: Board outline definition, placement.

- **O8 — Hinge flex connector position** *(gate: before placement, may use placeholder)*
  - **Status**: CONFIRMED 2026-07-22. Placeholder position for rev1 — mechanical constraints (enclosure hinge point, Phase 7) dominate. 14-pin 0.5mm FFC connector on main board edge.
  - **Blocks**: Connector placement, daughterboard layout.

- **O9 — Daughterboard layout scope** *(gate: before layout)*
  - **Status**: CONFIRMED 2026-07-22. Same KiCad project, separate board. Daughterboard is trivial (~5 components + 3 ZIF connectors, ~55×42mm). Efficient, shares design rules.
  - **Blocks**: Layout project setup.

### Gates before ordering (Phase 5 prep)

- **O10 — Modem source** *(gate: before parts ordering)*
  - **Recommendation**: Techship MPCIe (S2-109KS-Z30G9, ~$50) — eliminates LGA reflow (hardest DIY step). Socket is standard SMD.
  - **Fallback**: Worldway broker LGA ($41) if Techship stock/shipping fails — accept higher DIY reflow risk.
  - **Blocks**: Parts ordering.

- **O11 — Solder paste: leaded vs lead-free** *(gate: before tool ordering)*
  - **Status**: CONFIRMED 2026-07-22. Leaded 63/37 for first DIY attempt (183°C melt, more forgiving). Switch to lead-free (SAC305, 217°C) for production if needed.
  - **Blocks**: Tool procurement, assembly process.

- **O12 — PCB quantity** *(gate: before fab ordering)*
  - **Status**: CONFIRMED 2026-07-22. Order 5 boards (JLCPCB MOQ, marginal cost minimal, cheap insurance for DIY errors).
  - **Blocks**: Fab ordering.

- **O13 — Surface finish: ENIG vs HASL** *(gate: before fab ordering)*
  - **Status**: CONFIRMED 2026-07-22. ENIG (flat surface, critical for fine-pitch 0.5mm FPC + QFN-40). HASL is cheaper but uneven surface risks tombstoning.
  - **Blocks**: Fab ordering.

---

## Phase 3: Schematic Completion

> **Status**: IN PROGRESS (power section done, 7 sections remaining)
> **Approach**: Flat sheet + global labels (not hierarchical sheets). Block-diagram-first.
> **Reference**: `docs/work/block-diagram.md` is the source of truth for each section.

### 3.1 Resolve schematic-blocking open questions

- [x] **O2**: Confirm MPCIe power-on method — RESOLVED (auto-on at 3.3V, load switch + MCU_MODEM_PWR_EN)
- [x] **O3**: Create MCU pin assignment spreadsheet — RESOLVED (`docs/work/mcu-pin-assignment.md`, 73 pins assigned)
- [x] **O4**: Verify ALC5651 DBVDD pinout — RESOLVED (single shared pin 39, DBVDD=1.8V, I2S-2 via SN74AXC4T774)
- [x] **O5**: Verify ALC5651 analog supply current — RESOLVED (≤13mW, U9 retained)
- [ ] **O1** (optional): Email Techship for 100% PCM confirmation (not a blocker)

### 3.2 MCU section (STM32H743ZI full pin map) — CRITICAL PATH, do first

**Complexity**: Large (~6-8 hours). Unblocks all other sections.

- [ ] Place U1 (STM32H743ZIT6, LQFP-144) symbol
- [ ] Wire power: VDD (multiple pins) → +3.3V with 100nF decoupling per pair + 4.7µF bulk; VDDA via ferrite bead + 1µF; VBAT → +3.3V (RTC not used); all GND pins
- [ ] Wire HSE crystal (Y1, 8MHz) with load caps (2×18pF for CL=12pF crystal)
- [ ] Wire LSE crystal (32.768kHz) if RTC used — or mark NC if not
- [ ] Wire USB OTG_FS: D+, D- → USBLC6-2 → USB-C; VBUS sense via divider (100k/68k → ~2.02V)
- [ ] Wire LPUART1: TX, RX, RTS, CTS → level shifter B-side (to modem)
- [ ] Wire I2C: SCL, SDA → MAX17048 + ALC5651 (shared bus, address 0x36 + 0x1A)
- [ ] Wire SPI: MOSI, SCK → displays (via hinge flex); CS, DC, RST → main display; CS2, DC2 → outer display
- [ ] Wire I2S: BCLK, LRCK, DACDAT, ADCDAT → ALC5651 I2S-2 (music, 3.3V)
- [ ] Wire SDMMC: CMD, DAT0-3, CLK → microSD (decide 1-bit vs 4-bit — see O-schematic)
- [ ] Wire keypad GPIO: 5 rows + 4 columns (9 pins)
- [ ] Wire modem control GPIO: RI_IRQ, DTR, MODEM_RST (PERST#), MODEM_STATUS (WAKE#)
- [ ] Wire power monitoring GPIO: 3V3_OK (TPS63021 PG), FUEL_ALERT (MAX17048 ALRT)
- [ ] Wire backlight PWM GPIO → FET gate
- [ ] Mark unused GPIOs as NC (analog in firmware)
- [ ] ERC: no floating inputs, all VDD decoupled, crystal load caps correct

### 3.3 Modem section (SIM7600NA-H-PCIE) + level shifter — do second

**Complexity**: Large (~4-6 hours). Depends on MCU section (UART pin assignments).

- [ ] Place MPCIe socket symbol (SOFNG PCIE-52P40H or selected socket)
- [ ] Wire power: VCC pins (2, 24, 39, 41, 52) → **+3.3V** (NOT +BATT — MPCIe is 3.3V only)
- [ ] Wire GND pins (14 pins) → GND
- [x] Add bulk capacitance (470µF tantalum polymer C40 + 2× 10µF ceramic C41/C42) at VCC pins — DONE 2026-07-24
- [ ] Wire UART: TXD, RXD, RTS, CTS, RI, DTR → level shifter A-side (1.8V)
- [ ] Wire PCM: CLK, OUT, IN, SYNC → ALC5651 I2S-1 (direct, 1.8V, no shifter)
- [ ] Wire USB: DP, DN → test points (J2, DNP rev1)
- [ ] Wire control: PERST# (reset) → MCU GPIO via level shifter; WAKE# (status/interrupt) → MCU GPIO via level shifter
- [ ] Wire LED: LED_WWAN# (pin 42, active-low) → network status LED circuit (+3.3V → resistor → LED → pin 42)
- [ ] Wire SIM: USIM_VDD, USIM_DATA, USIM_CLK, USIM_RST → flat sheet SIM socket (global labels)
- [ ] Mark unused MPCIe pins NC (W_DISABLE#, SCL, SDA, MICN, EARP, EARN)
- [ ] Place U3 (TXB0108PWR level shifter): VCCA → +1V8, VCCB → +3.3V, OE → +3.3V pullup; wire 8 bits (UART + control signals)
- [ ] ERC: VCC on +3.3V not +BATT, bulk caps present, level shifter VCCA ≤ VCCB, OE pulled high

### 3.4 Codec section (ALC5651-CG) + transducers — do third

**Complexity**: Large (~4-6 hours). Depends on MCU (I2S, I2C) and modem (PCM) sections.

- [ ] Resolve O4 (DBVDD pinout) and O5 (analog current) first
- [ ] Place U5 (ALC5651-CG, QFN-40) symbol
- [ ] Wire power: AVDD, DACREF, CPVDD → +1V8; MICVDD → +3.3V; DBVDD per O4 resolution
- [ ] Wire I2S-1 (PCM from modem): BCLK, LRCK, DACDAT, ADCDAT → modem PCM pins (1.8V direct)
- [ ] Wire I2S-2 (I2S from MCU): BCLK, LRCK, DACDAT, ADCDAT → MCU I2S pins (3.3V)
- [ ] Wire I2C: SCL, SDA → shared MCU I2C bus (address 0x1A)
- [ ] Wire mic input: MIC1P/MIC1N (differential) → MEMS mic (MK1, ZTS6117) with bias circuit
- [ ] Wire earpiece output: HPOUTL/HPOUTR → earpiece speaker via hinge flex
- [ ] Wire loudspeaker output: SPKOUTP/SPKOUTM → loudspeaker wire pads
- [ ] Add coupling caps on audio outputs (AC-coupled)
- [ ] ERC: power pins correct, I2C pullups present, PCM at 1.8V, I2S-2 at 3.3V, no floating inputs

### 3.5 Display + hinge flex + daughterboard — do fourth

**Complexity**: Medium (~3-4 hours). Depends on MCU (SPI, GPIO) and codec (earpiece) sections.

- [ ] Verify main display exact pinout (HS20HS072RX, 12-pin 0.5mm FPC) from mechanical drawing
- [ ] Place J7 (main display ZIF, 12-pin), J10 (outer display ZIF, 8-pin), J8/J9 (hinge flex ZIF, 14-pin each)
- [ ] Wire main board side (J8): SPI (SDA, SCL, CS, DC, RST), outer display (CS2, DC2), +3.3V, GND, backlight (LEDA, LEDK), earpiece (SPK+, SPK-)
- [ ] Wire daughterboard side (J9): route 14 signals to J7 (main display) and J10 (outer display)
- [ ] Wire backlight PWM circuit: +3.3V → current-limit resistors → LEDA; LEDK → N-FET drain → GND; FET gate → MCU PWM GPIO
- [ ] Select backlight PWM FET (N-channel logic-level MOSFET) — add to BOM
- [ ] Calculate backlight resistor value (4 parallel LEDs, ~80mA total: (3.3V-3.0V)/20mA = 15Ω)
- [ ] ERC: connector pin counts correct, display power from +3.3V, no floating pins

### 3.6 SIM socket + ESD protection — do fifth

**Complexity**: Medium (~2-3 hours). Depends on modem section (USIM signals).

- [ ] Download ESDA6V1-5SC6 datasheet if not in `docs/datasheets/` — add to index
- [ ] Place J3 (nano-SIM hinged, SHOU HAN NANO SIM XG6P H1.35)
- [ ] Place U6 (ESDA6V1-5SC6) near J3
- [ ] Wire USIM_VDD, USIM_DATA, USIM_CLK, USIM_RST from modem global labels → SIM socket
- [ ] Wire ESD protection on all SIM data lines
- [ ] Add 100nF cap on USIM_VDD at socket
- [ ] USIM_DET: leave NC (6-pin socket, no card detect — per SIM7600 manual §3.5.1)
- [ ] ERC: SIM pinout correct, ESD on all lines, no floating pins

### 3.7 SD card + ESD protection — do sixth

**Complexity**: Medium (~2-3 hours). Depends on MCU section (SDMMC).

- [ ] Decide SD bus width: 1-bit (DAT0 only) or 4-bit (DAT0-3) — 4-bit faster, more GPIO
- [ ] Place J4 (microSD hinged, Molex 472192001)
- [ ] Place ESD protection (ESDA6V1-5SC6 or similar) near J4
- [ ] Wire CMD, DAT0-3, CLK from MCU SDMMC → SD socket
- [ ] Wire VDD → +3.3V
- [ ] Wire ESD protection on all data lines
- [ ] Add pullup resistors on CMD, DAT0-3 (10kΩ external or rely on STM32 internal)
- [ ] ERC: SD pinout correct, ESD on all lines, pullups present

### 3.8 Keypad matrix (5×4) — do seventh

**Complexity**: Small (~1-2 hours). Depends on MCU section (GPIO).

- [ ] Place 20× ALPS SKQGABE010 tactile switches in 5×4 grid
- [ ] Wire 5 row lines → MCU GPIO (global labels)
- [ ] Wire 4 column lines → MCU GPIO (global labels)
- [ ] No diodes (software scanning handles ghosting)
- [ ] ERC: 20 switches placed, row/column nets labeled, no shorts

### 3.9 Final schematic review

**Complexity**: Medium (~2-3 hours).

- [ ] Run KiCad ERC — fix all violations
- [ ] Cross-check schematic vs `docs/work/block-diagram.md` (every component, signal, power net)
- [ ] Verify all global labels match between sections
- [ ] Verify power nets use correct symbols (+BATT, +3.3V, +1V8, GND)
- [ ] Add PWR_FLAG symbols where needed (no "power pin not driven" errors)
- [ ] Mark all unconnected pins with NC flag
- [ ] Generate netlist — verify no unconnected nets
- [ ] Update `docs/work/block-diagram.md` with completed sections
- [ ] Update `docs/ref/project-log.md` with schematic completion entry
- [ ] **Phase 3 gate**: Schematic ERC-clean and reviewed → proceed to Phase 4

---

## Phase 4: PCB Layout

> **Status**: NOT STARTED
> **Prerequisite**: Phase 3 complete (ERC-clean schematic)
> **Tool**: KiCad
> **Estimated effort**: 36-55 hours (first complex RF + 2-sided board)

### 4.1 Pre-layout setup

- [ ] **Resolve O6**: Confirm 4-layer stackup (recommended) or 2-layer
- [ ] **Resolve O7**: Confirm board outline target dimensions
- [ ] **Resolve O8**: Confirm hinge flex connector placeholder approach
- [ ] **Resolve O9**: Confirm daughterboard in same KiCad project
- [ ] Configure layer stackup in KiCad (L1 Top / L2 GND plane / L3 +3.3V plane / L4 Bottom)
- [ ] Define board outline (main board + daughterboard as separate boards in project)
- [ ] Configure design rules:
  - Track widths: power 0.3-0.5mm (0.8mm for modem VBAT), signal 0.15mm (6mil), RF per impedance calc
  - Clearances: 0.15mm default, 0.2mm power-to-ground, 1.5mm RF keepout
  - Vias: 0.3mm drill / 0.6mm pad (signal), 0.5mm drill / 0.8mm pad (power)
- [ ] Define net classes: `power`, `signal`, `rf`, `high_speed` (USB diff pair), `audio`
- [ ] Verify all footprints against datasheets (MPCIe socket, QFN-40, VSON-14, FPC 0.5mm, LQFP-144)

### 4.2 Placement (most constrained first)

- [ ] Place MPCIe socket (top layer, largest part, sets board min dimension ~54mm)
- [ ] Define board outline around MPCIe + corner radii + mounting holes (4× M2/M2.5)
- [ ] Place MCU (bottom layer, under keypad zone, thermal vias to GND plane)
- [ ] Place power ICs (U8 TPS63021, U9 TPS7A0218, U11 MCP73831) near battery connector
- [ ] Place connectors (USBC1 USB-C, CN1, J4 SD, J8 hinge flex, J5/J6 U.FL) on board edges
- [ ] Place codec (U5 ALC5651) on bottom layer, near MCU I2S and MPCIe PCM pins
- [ ] Place fuel gauge (U10 MAX17048) near battery connector
- [ ] Place ESD protection (D1 USBLC6-2 near USB-C, U6/U7 ESDA6V1 near SIM/SD)
- [ ] Place level shifter (U3 TXB0108) between MCU and modem
- [ ] Place keypad switches (20× on top layer, grid matching enclosure)
- [ ] Place decoupling caps (100nF close to IC power pins, bulk caps near modem VCC)
- [ ] Place LEDs, test points, pull-up resistors
- [ ] 3D view check: no component interference, height clearance for keypad switches
- [ ] **Daughterboard placement**: 3 ZIF connectors + earpiece pad + passives (~55×42mm)

### 4.3 Routing (critical first)

- [ ] **Power distribution** (Priority 1):
  - +BATT → modem VCC (MPCIe uses +3.3V, not +BATT — wide traces/polygon, multiple vias)
  - +3.3V → MCU VDD (star topology), display, SD, codec MICVDD, level shifter VCCB, MAX17048
  - +1V8 → codec AVDD/DACREF/CPVDD, codec DBVDD (PCM side), level shifter VCCA
  - VBUS → MCP73831 input, MCU VBUS sense (divider)
  - Bulk caps (100-470µF) at modem VCC pins; decoupling within 2mm of IC power pins
- [ ] **RF traces** (Priority 2, 50Ω impedance):
  - Cellular antenna: MPCIe antenna pin → U.FL (short, <20mm, solid GND reference, 1.5mm keepout)
  - GNSS antenna: MPCIe GNSS pin → U.FL (same requirements)
  - Calculate trace width from stackup (KiCad calculator, typically 0.3-0.4mm on 1.6mm 4-layer)
- [ ] **High-speed differential** (Priority 3):
  - USB D+/D- (MCU → USB-C): 90Ω differential, length-matched (<5mil mismatch), no plane splits
  - Modem USB D+/D- → test points (same requirements, unpopulated rev1)
- [ ] **Display SPI** (Priority 4, through hinge flex):
  - MCU → hinge flex → daughterboard → displays; keep total <150mm (capacitance)
  - Include GND in flex (14-pin FFC: ~13 signals + GND)
- [ ] **PCM audio** (Priority 5, modem ↔ codec):
  - Short traces (<25mm), CLK/SYNC length-matched, OUT/IN matched (±5mil), GND reference
- [ ] **I2S audio** (Priority 6, MCU ↔ codec):
  - Short traces (<30mm), BCLK/LRCLK/DACDAT matched (±5mil), separate from PCM
- [ ] **UART** (Priority 7, MCU ↔ modem via level shifter): standard routing, add test points
- [ ] **I2C** (Priority 8, MCU ↔ codec + fuel gauge): pullups near MCU, standard routing
- [ ] **Keypad matrix** (Priority 9): 5 rows + 4 columns, 0.15mm traces, avoid crossing high-speed
- [ ] **GPIO/control** (Priority 10): modem RST/STATUS, display control, backlight PWM, LEDs, USB-C CC pull-downs
- [ ] **Remaining passives** (Priority 11): short traces, ground return vias

### 4.4 Fanout (fine-pitch parts)

- [ ] MPCIe socket (0.8mm pitch): vias between pins, 0.3mm drill, alternate top/bottom escape
- [ ] FPC connectors (0.5mm pitch): top layer traces, 0.25mm drill vias if needed
- [ ] ALC5651 QFN-40 (0.4mm pitch): center pad → 4-6 thermal vias to GND; side pins fanout
- [ ] TPS63021 VSON-14 (0.5mm pitch): thermal pad → 4 thermal vias; power pins → multiple vias

### 4.5 Plane/pour

- [ ] Layer 2: solid GND plane (no splits, no slots under high-speed signals)
- [ ] Layer 3: +3.3V power plane (split from GND); +BATT polygon if space
- [ ] Bottom: GND pour around signals/components
- [ ] Stitching vias around board edge + near high-speed signals
- [ ] Thermal relief on ground pads (for soldering)
- [ ] **Daughterboard**: GND pour, simple routing (no complex planes needed)

### 4.6 DRC + manufacturing prep

- [ ] Run KiCad DRC — fix all errors (clearance, unconnected, track width, via size)
- [ ] Verify against JLCPCB capabilities (6mil/6mil, 0.3mm drill, 0.15mm annular ring)
- [ ] Generate Gerbers (RS-274X): all copper layers, solder mask, silkscreen, paste, outline, drill
- [ ] Export BOM (refdes, value, footprint, LCSC C-number, qty)
- [ ] Generate pick-and-place file (for DIY placement verification, not for JLC PCBA)
- [ ] Verify board outline + drill files
- [ ] Order spec: 4-layer, 1.6mm, ENIG, green mask, white silk, 6mil/6mil rules

### 4.7 Review

- [ ] Self-review checklist:
  - Mechanical: dimensions < 2×3", connectors accessible, mounting holes, no interference (3D)
  - Electrical: all nets connected, power trace widths adequate, decoupling placed, RF impedance-controlled, high-speed length-matched, GND plane continuous
  - Manufacturing: design rules met, no acute angles, silkscreen readable, fiducials present
  - DIY: top/bottom separation clear, fine-pitch accessible, test points accessible, thermal relief
- [ ] Optional: peer/expert review (EEVblog, r/PrintedCircuitBoard, makerspace, university lab)
- [ ] **Phase 4 gate**: DRC-clean, Gerbers generated, reviewed → proceed to Phase 5

---

## Phase 5: Ordering + DIY Assembly

> **Status**: NOT STARTED
> **Prerequisite**: Phase 4 complete (fab-ready Gerbers)
> **Assembly path**: Full DIY (reflow oven + stencil + paste)
> **Endpoint**: Assembled PCB in hand (no power-on)

### 5.1 Tool procurement (order in parallel with layout)

- [ ] Reflow oven: T-962 (~$150) — order early, practice tuning profile
- [ ] USB microscope: 5MP (~$30-50) — essential for QFN/0.5mm inspection
- [ ] Hot-air station: Quick 861DW or Yihua 8786D (~$50-100) — for rework
- [ ] Tweezers: ESD-safe fine-tip, curved + straight (~$15-25)
- [ ] Flux: MG Chemicals 8341 paste flux + Kester 951 liquid flux pen (~$18-27)
- [ ] Desoldering braid: Chemtronics Soder-Wick (~$5-10)
- [ ] **Resolve O11**: Solder paste — leaded 63/37 (recommended for first DIY) or lead-free SAC305
  - Order: Kester 331 (63/37 no-clean) syringe (~$15-25), refrigerate at 2-8°C
- [ ] Optional: preheater (~$50-100) — assess after first reflow attempt
- [ ] Optional: fume extractor (~$30-60)

### 5.2 Parts ordering

**Order first (long lead times):**
- [ ] **Resolve O10**: Confirm modem source — Techship MPCIe (S2-109KS-Z30G9, ~$50, recommended) or fallback
- [ ] Order Techship MPCIe modem (1 qty) — verify US shipping, stock (4 units)
- [ ] Order main display from LCSC (HS20HS072RX, C5329582, $3.42, 1 qty)
- [ ] Order outer display from BuyDisplay (ER-TFT1.14-2, $3.27, 1 qty)

**Order after layout frozen (PCB-dependent):**
- [ ] Build LCSC cart from `pcb/PARTS_TRACKING.md` C-numbers (2-3 qty spares):
  - ICs: C114408, C963633, C202140, C3748843, C150772, C2682616, C53406, C1549752, C7519, C6650 (×3 each)
  - Connectors: C165948, C7529386, C164170, C88373 (×6), C2919494, C2919495 (×6), C2919492, C295747 (×3 each)
  - MPCIe socket: C357792 or C444926 or C9900027618 (×3) — **resolve socket selection**
  - Switches: C115351 (×60, 20 per board × 3)
  - Mic: C481300 (×3)
  - Crystal: C2595911 (×3), Inductor: C3033018 (×3), LEDs: C99290 (×9)
  - Passives: 100nF (×60), 10µF (×30), various resistors (×100)
- [ ] Order battery (Adafruit 258 1200mAh or equivalent, JST-PH plug, ~$10)
- [ ] Order speakers (earpiece ~$2, loudspeaker ~$3) — case-mounted, wire-soldered
- [ ] Order antennas (cellular U.FL pigtail + antenna ~$5, GNSS ~$5)

### 5.3 PCB fab ordering (JLCPCB)

- [ ] **Resolve O12**: Board quantity — 5 boards (JLCPCB MOQ, recommended for DIY spares)
- [ ] **Resolve O13**: Surface finish — ENIG (recommended for fine-pitch)
- [ ] Upload Gerbers to JLCPCB
- [ ] Spec: 4-layer, 1.6mm, ENIG, green mask, white silk, 6mil/6mil, 0.3mm drill
- [ ] Order top + bottom stencils (frameless, 0.12mm thickness, no modem cutout for MPCIe)
- [ ] Estimated cost: PCB ~$20-30 (5 boards) + stencils ~$20-40 + shipping ~$5-10 = **$45-80**

### 5.4 Pre-assembly prep

- [ ] Inspect bare PCBs (manufacturing defects, silkscreen, dimensions)
- [ ] Clean PCB with IPA
- [ ] Print BOM with refdes + C-numbers
- [ ] Print 1:1 placement guide from KiCad (front + back assembly plots)
- [ ] Sort parts into labeled tray/compartment box by refdes
- [ ] Verify part counts against BOM
- [ ] Set up workspace: clean, well-lit, microscope, hot-air station, tweezers, flux, braid
- [ ] Practice reflow profile on a cheap test board (tune T-962 temp curve)

### 5.5 Bottom side assembly (dense side: MCU + ICs + passives)

- [ ] Secure PCB face-down
- [ ] Align + secure bottom stencil
- [ ] Apply solder paste (even squeegee pressure)
- [ ] Inspect paste under microscope (all pads covered, no bridges on QFN-40/0.5mm FPC)
- [ ] Place components: MCU (LQFP-144) first, then ICs (U5-U11), then passives, then mic
- [ ] **Critical**: Verify paste on exposed pads (TPS63021, MCU, ALC5651 thermal pads)
- [ ] Reflow (leaded profile: preheat 150→180°C 60-90s, reflow 210-220°C 30-45s, cool)
- [ ] Inspect under microscope: tombstoning, bridges, insufficient paste, misalignment
- [ ] Rework as needed (hot-air + flux + braid)

### 5.6 Top side assembly (MPCIe socket + connectors + keypad)

- [ ] Flip PCB face-up (risk: bottom components may shift — use higher-tack paste or preheater)
- [ ] Align + secure top stencil
- [ ] Apply solder paste
- [ ] Inspect paste (MPCIe 0.8mm pads, FPC 0.5mm pads)
- [ ] Place: MPCIe socket first, then connectors (USBC1, J3, J4, J5/J6, J7-J10, CN1), then keypad switches (20×), LEDs, crystal, remaining passives
- [ ] Reflow (same profile — watch for bottom-side shifting)
- [ ] Inspect: MPCIe socket (52 pins), FPC bridges, keypad alignment, LED polarity
- [ ] Rework as needed

### 5.7 Through-hole / hand-solder (if any)

- [ ] Battery connector CN1 (if through-hole variant — verify, C295747 is SMD)
- [ ] Test points (modem USB J2, any debug points)
- [ ] Speaker wire pads (clean + tin, no soldering yet — speakers are Phase 7)

### 5.8 Post-assembly inspection

- [ ] Clean flux residue with IPA
- [ ] Systematic microscope inspection: MCU (144 pins), QFN-40, VSON-14, MPCIe (52 pins), FPC (0.5mm), keypad
- [ ] Continuity check (multimeter, NO POWER):
  - +BATT to GND: >100Ω (not 0Ω)
  - +3.3V to GND: >100Ω
  - +1V8 to GND: >100Ω
  - If any rail is 0Ω → find short before power-on
- [ ] Verify all parts placed against BOM placement guide

### 5.9 Daughterboard assembly

- [ ] Stencil → paste → place (3 ZIF connectors + passives) → reflow
- [ ] Inspect FPC connectors (0.5mm pitch)
- [ ] Continuity check on hinge flex signals

### 5.10 What NOT to do (out of scope)

- [ ] Do NOT power on (bring-up is Phase 6, separate effort)
- [ ] Do NOT install MPCIe modem card (plug in after visual inspection passes)
- [ ] Do NOT install display panels (ZIF plugs in post-assembly)
- [ ] Do NOT solder speakers (case-mounted, Phase 7)

### 5.11 Known DIY failure modes

| Failure | Mitigation |
|---------|------------|
| QFN tombstoning | Even paste, proper reflow profile, solder mask dam if respin |
| 0.5mm FPC bridges | 0.12mm stencil, inspect paste before placing, braid for fixes |
| Insufficient paste on exposed pads | Verify stencil apertures, add paste manually, inspect before reflow |
| Reflow profile too hot/cold | Practice on test board, thermocouple measurement |
| 2-sided: bottom parts falling off | Higher-tack paste (leaded), higher bottom reflow temp, or preheater |
| Cold joints on ground planes | Preheater, extend reflow time |
| Solder wicking under QFN | Reduced aperture stencil, inspect fillet on all sides |

---

## Cost Summary

| Category | Cost Range |
|----------|------------|
| LCSC/JLC components (2-3 qty spares) | $115–130 |
| Techship MPCIe modem (1 qty) | $50 |
| Displays (LCSC main + BuyDisplay outer) | $6.69 |
| Battery, speakers, antennas | $25–30 |
| PCB fab (5 boards, 4-layer) + stencils | $45–80 |
| DIY tools (reflow oven, microscope, etc.) | $303–477 |
| **TOTAL** | **$545–774** |

*If you already have soldering iron + multimeter, subtract $50-80. Tools amortize over future projects.*

---

## Progress Tracking

| Date | Milestone | Status |
|------|-----------|--------|
| 2026-07-22 | Task tracker created — comprehensive plan to assembled PCB | Done |
| 2026-07-22 | MPCIe PCM verified (high confidence, subagent research) | Done |
| 2026-07-22 | Phase 3: Resolve open questions O2-O5 | Done |
| 2026-07-23 | Phase 3: Power schematic section | Done |
| 2026-07-23 | Phase 3: MCU schematic section | Done |
| 2026-07-23 | Phase 3: Modem schematic section | Done |
| 2026-07-23 | Phase 3: Codec schematic section | Done |
| 2026-07-23 | Phase 3: Display + daughterboard schematic section | Done |
| 2026-07-23 | Phase 3: SIM/SD schematic section | Done |
| 2026-07-23 | Phase 3: Keypad schematic section | Done |
| 2026-07-23 | Phase 3: Power section moved to power.kicad_sch sub-sheet | Done |
| 2026-07-23 | Phase 3: J_HINGE2 added to display daughterboard | Done |
| 2026-07-23 | Phase 3: ERC cleanup — 196→3 warnings (0 errors) | Done |
| 2026-07-24 | Phase 3: Add deferred components — VBUS divider (R12/R13), MCU_MODEM_PWR_EN pull-down (R11), SWD header (J3), NET_STATUS LED (R12+LED1) | Done |
| 2026-07-24 | Phase 3: Power switch (SW21 ALPS SSSS811101) added to power sheet — controls TPS63021 EN pin | Done |
| 2026-07-24 | Phase 3: Modem bulk caps (C40 470µF + C41/C42 10µF) added near MPCIe VCC pins | Done |
| 2026-07-24 | Phase 3: Load switch reversed — R11 removed, no_connect on PE6, temp libraries registered | Done |
| | Phase 3: Final schematic review + ERC fully clean | Pending |
| | Phase 4: Pre-layout setup (stackup, rules, outline) | Pending |
| | Phase 4: Placement | Pending |
| | Phase 4: Routing | Pending |
| | Phase 4: DRC + manufacturing prep | Pending |
| | Phase 4: Review | Pending |
| | Phase 5: Tool procurement | Pending |
| | Phase 5: Parts ordering | Pending |
| | Phase 5: PCB fab ordering | Pending |
| | Phase 5: Bottom side assembly | Pending |
| | Phase 5: Top side assembly | Pending |
| | Phase 5: Post-assembly inspection | Pending |
| | Phase 5: Daughterboard assembly | Pending |
| | **GOAL: Assembled PCB in hand** | Pending |
