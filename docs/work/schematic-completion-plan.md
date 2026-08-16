---
status: active
updated: 2026-08-16
---
# Schematic Completion Plan

> **Created**: 2026-07-28
> **Purpose**: Track remaining work to complete the PCB schematic (Phase 3) based on a full per-sheet review.
> **Source**: Per-sheet subagent reviews (9 sheets) + KiCad MCP ERC run + git history investigation.

---

## Current State (verified 2026-07-28)

| Sheet | Status | Notes |
|-------|--------|-------|
| Power | ✅ Complete | Functionally done; refdes mismatches with docs (see §A) |
| MCU | ✅ ~92% | VDDA ferrite + caps DONE 2026-07-28. Still missing bulk cap, footprint fixes (see §B) |
| Modem | ✅ ~90% | C20 footprint assigned (2026-07-28). USB not routed, socket part doc discrepancy (see §C) |
| Codec | ✅ Restored from git HEAD 2026-07-28 | Was accidentally wiped in working tree by `add_headphone_jack.py` script. Restored via `git checkout HEAD -- pcb/phone/codec.kicad_sch`. ERC now clean (0 violations on codec sheet). HP_DET still dangling (headphone jack not yet added). (see §D) |
| Keypad | ✅ Complete | Footprint overrides blanked; no key labels (see §E) |
| Display (main) | ⚠️ ~85% | Missing backlight FET (see §F). **2026-08-16**: Form factor pivoted to candybar — display now mounts directly on single board via J7 ZIF, no hinge flex. Outer display + daughterboard sheet dropped (see §G). |
| ~~Display daughter~~ | **DROPPED 2026-08-16** | Sheet removed from scope — candybar form factor eliminates the daughterboard. J8/J9 hinge connectors and J10 outer display removed. See §G. |
| SIM/SD | ✅ Complete | **Initially flagged as broken by subagent — RE-VERIFIED via ERC: no errors, no shorts.** Subagent's coordinate-based analysis was wrong. Sheet is fine. |

**ERC result (2026-07-28, after VDDA ferrite + caps)**: 0 errors, 15 warnings (lib_symbol_mismatch ×9 including 3 new for VDDA parts, endpoint_off_grid ×4, isolated_pin_label ×1 for HP_DET, unconnected_wire_endpoint ×1). All 8 sub-sheets individually clean.

---

## Action Items

### §A — Power Sheet: Reference Designator Mismatches

**Status**: DONE 2026-07-28 (docs updated to match schematic — no schematic changes needed)

**DONE 2026-07-28**: Docs updated to match schematic refdes (not the other way around). The schematic refdes are canonical. 12 refdes were updated across 11 doc files:

| Component | Doc (old) | Schematic (canonical) |
|-----------|-----------|----------------------|
| ALC5651 codec | U3 | U5 |
| TPS63021 buck-boost | U4 | U8 |
| TPS7A0218 LDO | U5 | U9 |
| MCP73831 charger | U6 | U11 |
| MAX17048 fuel gauge | U7 | U10 |
| TXB0108 level shifter | U8 | U3 |
| SN74AXC4T774 level shifter | U9 | U12 |
| USBLC6-2 ESD | U10 | D1 |
| ESDA6V1 ESD (SIM) | U11 | U6 |
| ESDA6V1 ESD (SD) | U11 | U7 |
| USB-C connector | J1 | USBC1 |
| Battery connector | J_BATT | CN1 |
| Slide switch | SW1 | SW21 | *(2026-08-17: switch moves from EN pin to battery path — power-rated maintained switch, not signal-level. See project-log 2026-08-17.)* |

Note: ESDA6V1 was a single U11 in docs but is two separate chips in the schematic (U6 for SIM, U7 for SD). U1 (MCU) and U2 (modem/MPCIe socket) were already consistent.

- [x] Get user approval for refdes direction (docs match schematic)
- [x] Update all 11 doc files via automated script (update_refdes.py)
- [x] Fix historical project-log.md entries that described the old schematic→doc rename
- [x] Handle ESDA6V1 (U11→U6/U7) manually — one doc refdes maps to two schematic refdes
- [ ] Run ERC to verify no breakage (N/A — no schematic changes, docs only)

### §B — MCU Sheet: Missing Components & Footprint Fixes

**Required for Phase 3 gate:**

- [x] **Add VDDA ferrite bead + 1µF + 10nF caps** — **DONE 2026-07-28.** Added BLM18KG601SN1D ferrite bead (L1) between +3.3V and VDDA/VREF+, with 1µF (C18, GRM188R61C105KA93D) and 10nF (C19, CC0603KRX7R9BB103) decoupling caps to GND. Added PWR_FLAG on VDDA net for ERC. Also added CC0603KRX7R9BB103 to passives.kicad_sym library. ERC: 0 errors, 15 warnings (3 new lib_symbol_mismatch for new parts, rest pre-existing).
- [ ] **Add 4.7µF bulk cap** on +3.3V near MCU (docs say "100nF per pair + 4.7µF bulk")
- [ ] **Fix C4/C13 part-number mismatch** — lib_id is 4.7µF (GRM188R61C475KE11D) but value overridden to "2.2µF". Either use correct 2.2µF part or update value to match.
- [ ] **Fix R1/R2/R3 footprints** — have `C0603` instead of `R0603`
- [ ] **Assign USBC1 (SWD header) footprint** — Conn_01x04 with empty footprint
- [ ] **Update `docs/work/mcu-pin-assignment.md`** — add HP_DET on PA2; correct VDD/VSS pin numbers

**Optional / defer:**

- [ ] **Add NRST to SWD header** — expand to 5-pin for debug reset
- [ ] **Add UART debug header** — for Zephyr console
- [ ] **Add test points** — SWDIO, SWCLK, NRST, USB_DP/DN, VBUS
- [ ] **Add hardware reset button** — tactile switch on NRST to GND

### §C — Modem Sheet: Missing Footprint & USB Routing

**Required for Phase 3 gate:**

- [x] **Assign C20 footprint** (470µF tantalum) — **DONE 2026-07-28.** Temp library `temp_470uf` already had both symbol (`6TPF470MAH`) and footprint (`CAP-SMD_L7.3-W4.3`, Case E 7.3×4.3mm). The schematic instance had an empty Footprint property override blanking the library-level value. Set instance Footprint to `temp_470uf:CAP-SMD_L7.3-W4.3`. ERC verified: 0 errors, 11 warnings (all pre-existing), Modem sheet 0 violations.
- [ ] **Route modem USB or document deferral** — pins 36/38 (USB_DN/DP) marked NC. AGENTS.md says "Rev1 routes modem USB to a connector footprint." Either route + ESD, or document deferral in project-log.
- [ ] **Resolve socket part discrepancy** — AGENTS.md says Techship S2-109KS-Z30G9; schematic uses SOFNG PCIE-52P40H (C444926). Reconcile docs.
- [ ] **Add PWR_FLAG symbols** on +3.3V and +1V8 (if needed for ERC)

**Optional / defer:**

- [ ] **Add OE RC ramp cap** — on TXB0108 OE pin for power sequencing
- [ ] **Add test points**

### §D — Codec Sheet: RESTORED FROM GIT (DONE)

**The codec sheet was complete at git HEAD but accidentally wiped in the working tree by the `add_headphone_jack.py` script (untracked, deleted 4856 lines, leaving only lib_symbols).**

**RESTORED 2026-07-28** via `git checkout HEAD -- pcb/phone/codec.kicad_sch`. ERC verified: 0 violations on codec sheet, I2S2/PCM isolated-pin warnings resolved.

HEAD version contains: U5 (ALC5651), U12 (SN74AXC4T774 level shifter), C23-C26/C41-C45 (caps), R10/R11 (resistors), J_MIC1 (mic connector), J_SPK1 (speaker connector), CN (connector), 37 power symbols, wires, and global labels.

- [x] **Restore codec sheet from HEAD** — DONE 2026-07-28
- [x] **Verify restored content** — ERC clean (0 violations on codec sheet)
- [ ] **Re-review restored codec sheet** for completeness against `docs/work/block-diagram.md` §Codec
- [ ] **Open questions to verify after restore**:
  - Does ALC5651 symbol have a RESETB pin? (subagent flagged it missing — verify against `docs/datasheets/alc5651.pdf`)
  - DCVDD (pin 40) pin type — `power_in` but docs say internal LDO (needs datasheet check)
  - MCLK level-shifting — 5th channel beyond U12's 4 bits (design decision needed)
  - Loudspeaker amp — ALC5651 has no integrated speaker driver; is an external amp in the design?
  - Headphone jack — the `add_headphone_jack.py` script was attempting to add one; HP_DET still dangling. Decide whether to re-attempt carefully.
- [ ] **Clean up**: delete or fix `pcb/phone/scripts/add_headphone_jack.py`
- [ ] **Update `docs/work/task-tracker.md`** — codec "Done" entry is now correct again

### §E — Keypad Sheet: Footprint Fixes & Labels

- [ ] **Fix 9 resistor footprint overrides** — R8-R18 have instance Footprint = `""` (blanked), should inherit `easyeda2kicad:R0603`
- [ ] **Add key-function text labels** — SW1-SW20 need silkscreen labels (1, 2, ..., CALL, END, UP, DOWN, OK, SPARE)
- [ ] **Add scan-algorithm note** — document the mixed pull-up/pull-down topology (active-low column drive, read rows)
- [ ] **Update `docs/work/block-diagram.md` §Keypad** — remove "to be specified", add keypad topology + matrix design intent (pin-level detail lives in the schematic)
- [ ] **Add project-log entry** for SKQGABE010 selection and pull topology

### §F — Display (Single Board): Backlight FET

> **2026-08-16 update**: The backlight FET architecture conflict is **resolved** by the candybar pivot. The FET lives on the single board, directly switching LEDK — no hinge flex, no daughterboard, no "which board does the FET live on?" question. The old conflict (docs said FET on main board with LEDA/LEDK through hinge; schematic used BL_PWM through hinge with R19 on daughterboard) no longer applies.

**Required for Phase 3 gate:**

- [ ] **Add N-channel logic-level MOSFET** for backlight PWM switching (CRITICAL — without it, MCU GPIO would need to sink ~64-80mA, exceeding 20mA max)
  - Recommended: AO3400A (LCSC C20917), SI2302 (C66355), or BSS138 (C85568)
  - Drain → LEDK, Source → GND, Gate → MCU PWM GPIO (BL_PWM)
- [ ] **Add gate resistor** (100Ω-1kΩ) on FET gate
- [ ] **Add gate pull-down** (10kΩ-100kΩ) to ensure backlight OFF during MCU reset
- [ ] **Remove hinge flex connectors (J8/J9)** from the display sheet — no longer needed (candybar, single board)
- [ ] **Remove outer display connector (J10)** and its signals (OUTER_CS, OUTER_DC) from the display sheet — outer display dropped
- [ ] **Wire display directly** — J7 (12-pin ZIF) connects directly to MCU SPI + GPIO + power + backlight, no hinge flex intermediary
- [ ] **Reconcile net names** — DISP_MOSI/SCK vs docs' DISP_SDA/SCL; EARPIECE+/- vs docs' SPK+/SPK-

**Optional / defer:**

- [ ] **Add ESD protection on EARPIECE+/-** — user's ear is ESD source

### §G — ~~Display Daughterboard~~ **DROPPED 2026-08-16** (candybar pivot)

> **2026-08-16**: The display daughterboard sheet is **removed from scope**. The candybar form factor (single PCB) eliminates the daughterboard, hinge flex connectors (J8/J9), and outer display (J10). All display components now live on the single board (see §F). The daughterboard `.kicad_sch` sheet can be deleted from the project or left as an empty placeholder — user's call during KiCad cleanup.
>
> The following items were previously tracked here and are now **moot**:
> - ~~Fix J_HINGE2 footprint~~ — J_HINGE2 (J9) removed, no hinge flex
> - ~~Add backlight FET on daughterboard~~ — FET lives on single board (§F)
> - ~~Add second decoupling cap for outer display~~ — outer display dropped
> - ~~Address outer display backlight~~ — outer display dropped
> - ~~Verify earpiece coupling caps~~ — earpiece now on single board, verify there
> - ~~Verify connector shell pins tied to GND~~ — only J7 (12-pin) remains, verify there

### §H — SIM/SD Sheet: NO ACTION NEEDED

**Initially flagged as broken by subagent (labels shifted by one pin pitch). Re-verified via KiCad MCP ERC: 0 errors, no shorts.** The subagent's coordinate-based net connectivity inference was incorrect — it miscalculated the socket symbol's geometric transform. The sheet is electrically correct.

- [x] ~~Re-align SIM socket labels~~ — NOT NEEDED (ERC clean)
- [x] ~~Re-align SD socket labels~~ — NOT NEEDED (ERC clean)
- [ ] (Optional) Add test points on USIM_VDD, USIM_DATA, SD_CMD, SD_CK
- [ ] (Optional) Document SD card-detect choice (pins tied to GND = polling-only)

### §I — Structural / Cross-Sheet Issues

- [ ] **Page number conflict** — Codec and Keypad both assigned page 4 in root sheet
- [ ] **Delete orphan `main.kicad_sch`** — not referenced by project, empty skeleton
- [ ] **Reconcile flat-vs-hierarchical structure** — docs say "flat sheet + global labels"; actual implementation uses hierarchical sheets (with no sheet pins, global labels only). Functionally equivalent but contradicts documented decision. Either update docs or restructure.
- [ ] **Add title blocks** to all sheets (no title/date/rev metadata currently)

### §J — Documentation Sync

- [ ] **`docs/work/task-tracker.md`**: Update §3.2-3.8 checkboxes to reflect actual completion; fix cap refdes (C40/C41/C42 → C18-C22); codec entry correct for HEAD but note working-tree issue
- [ ] **`docs/work/block-diagram.md`**: Update design intent for sections marked "to be specified" that are actually drawn (MCU, modem, keypad, display, SIM/SD). Reconcile net names (DISP_SDA/SCL vs DISP_MOSI/SCK, SPK+/SPK- vs EARPIECE+/-) — net names are design intent and must match the schematic. Pin-level detail is no longer maintained here (schematic is authoritative).
- [ ] **`docs/ref/project-log.md`**: Add entries for SKQGABE010 keypad switch selection, SOFNG socket selection, backlight architecture change, codec sheet restore
- [ ] **`AGENTS.md`**: Reconcile refdes (USBC1, CN1, U8-U10, D1) and socket part (Techship vs SOFNG) with schematic

---

## Priority Order

1. **§D: Restore codec sheet from git HEAD** ✅ DONE 2026-07-28
2. **§F: Add backlight FET + remove hinge/outer display** (critical — without FET, MCU GPIO will be damaged; candybar pivot requires removing J8/J9/J10 from display sheet)
3. **§B: Fix MCU footprints** (C4/C13, R1-R3, USBC1) + add VDDA ferrite + bulk cap
4. **§C: Assign C20 footprint** (blocks PCB layout)
5. ~~**§G: Fix J_HINGE2 footprint**~~ **DROPPED 2026-08-16** (candybar pivot — no daughterboard)
6. **§E: Fix keypad resistor footprints** (blocks PCB layout)
7. **§A: Reconcile power refdes** (needs user approval — locked section)
8. **§I: Structural fixes** (page numbers, orphan file, remove daughterboard sheet from project)
9. **§J: Documentation sync** (after all schematic fixes are done)
