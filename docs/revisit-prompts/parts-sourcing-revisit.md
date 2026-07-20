# Revisit Prompt: PCB Parts Sourcing — Remaining Components

**Purpose**: Paste the prompt below into a new chat to work through the remaining parts selection and sourcing decisions for the phone PCB. This collects all open items that need either a part pick (search JLC) or a design decision before the schematic can be completed.

**STATUS: OPEN** — Created 2026-07-19 during the parts library build phase.

**Context**: The IC library is ~90% complete (9 of 11 ICs downloaded via `easyeda2kicad` from JLC/LCSC). What remains is mostly mechanical parts (connectors, switches, transducers) and two ICs not stocked on JLC. The KiCad project-local library is at `pcb/phone/lib/` (symbols in `easyeda2kicad.kicad_sym`, footprints in `easyeda2kicad.pretty/`, 3D models in `easyeda2kicad.3dshapes/`). Tracking doc: `pcb/PARTS_TRACKING.md` (single source of truth for C-numbers and sourcing status).

See `docs/project-log.md` (2026-07-19 Parts Library Build entry) and `pcb/PARTS_TRACKING.md` for current status.

---

## Prompt to paste into new chat:

I'm working on a custom cell phone project (STM32H743ZI + SIM7600NA-H + Zephyr RTOS + custom PCB, targeting US LTE with VoLTE on T-Mobile/Mint). The full project docs are in the `docs/` folder — please read them before responding. The block diagram is `docs/block-diagram.md`, constraints are `docs/constraints.md`, and the parts tracking doc is `pcb/PARTS_TRACKING.md`.

We're in the PCB design phase. I've already sourced and downloaded KiCad footprints/symbols/3D models for all ICs plus passive/LED parts from JLC/LCSC using `easyeda2kicad`. The assembly method is locked: **JLCPCB PCBA, 2-board MOQ, LCSC-stocked parts.** **No consignment parts remain** (MAX9880A was the last — replaced by ALC5651 2026-07-19). The project-local KiCad library is at `pcb/phone/lib/`.

I need help completing the parts list. There are three categories of open items: (A) ~~two ICs not on JLC~~ **RESOLVED** (both ICs now JLC-sourced), (B) mechanical parts that need JLC part selection, and (C) design decisions that block part selection. Please work through each item below.

### A. ICs not stocked on JLC (need Ultra Librarian + external distributor)

~~These two parts are not on LCSC. I need to download their KiCad models from Ultra Librarian (or the manufacturer's CAD library) and source them from Mouser/DigiKey for consignment to JLC.~~ **Both RESOLVED 2026-07-19 — no consignment parts remain.**

1. ~~**U3: MAX9880AETM+T** (Analog Devices/Maxim audio codec, TQFN-48 6×6mm)~~ — **SUPERSEDED 2026-07-19**
   - ~~Ultra Librarian KiCad v6 package downloaded...~~ ~~Sourcing: Mouser consignment...~~
   - **SUPERSEDED 2026-07-19**: MAX9880A replaced by **Realtek ALC5651-CG** (LCSC C963633, QFN-40 5×5mm, JLC Extended — no consignment). Dual I2S/PCM audio hub codec (same architecture: I2S-1 = PCM voice from SIM7600, I2S-2 = I2S music from MCU). Better specs (100dBA DAC vs 96dB, 94dBA ADC vs 82dB), smaller package, ASRC per interface. PCM Mode A short-sync verified compatible with SIM7600 §3.6. KiCad model downloaded via easyeda2kicad. Datasheet: `docs/reference/alc5651.pdf` (Rev 0.9, 134pp). See `docs/project-log.md` 2026-07-19 Codec Swap MAX9880A→ALC5651.
   - ~~Only remaining consignment part~~ **No consignment parts remain.**

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

3. **J1: USB-C 16-pin receptacle** (SMD, USB 2.0, 16-pin — for charging + MCU USB) — **RESOLVED 2026-07-19**
   - **Selected**: Korean Hroparts Elec TYPE-C-31-M-12 (LCSC C165948). 16-pin USB 2.0, 5A/20V, 10,000 mating cycles, 7.35mm right-angle SMD. 94,755 in stock at LCSC, $0.186 qty 5+.
   - **Why Korean Hroparts (HRO)**: Reputable Korean USB-C connector brand — higher tier than generic Shenzhen brands (HCTL, Hong Cheng, G-Switch). User preference (2026-07-19): OEM/brand-name connectors. HRO is one of the most popular USB-C connector brands on JLC/LCSC (94K+ stock, low C-number = long catalog history = well-supported for assembly).
   - **Why not GCT USB4081** (the revisit prompt's reference part): USB4081 is 24-pin USB 3.2 Gen 2 — wrong pin count. The block diagram specifies 16-pin USB 2.0. GCT does not appear to have a 16-pin USB 2.0 variant on JLC.
   - **Alternative evaluated**: JUSHUO JS16T-TYPE-C479-DWH2-FSQ (C49118447) — comparable specs (16-pin, 5A, 10K cycles, with O-ring) but Shenzhen brand (lower tier than Korean Hroparts). No reason to prefer it when HRO is in stock at 94K units.
   - **KiCad model downloaded** via easyeda2kicad: symbol `TYPE-C-31-M-12`, footprint `USB-C_SMD-TYPE-C-31-M-12_1`, 3D `USB-C_SMD-TYPE-C-31-M-12_1` (.wrl + .step).
   - See `docs/project-log.md` 2026-07-19 J1 USB-C Selection for full rationale.

4. **J5, J6: U.FL antenna receptacles** (cellular + GNSS) — **RESOLVED 2026-07-19**
   - **Selected**: Hirose U.FL-R-SMT-1(10) (LCSC C88373). The original U.FL connector from Hirose (invented the U.FL standard). 6 GHz, 50Ω, 53,805 in stock, $0.227 qty 5+.
   - **Why Hirose**: Hirose is the original manufacturer of the U.FL connector — it doesn't get more OEM than this. 53K stock ensures availability for both prototyping and production.
   - **KiCad model downloaded** via easyeda2kicad: symbol `U.FL-R-SMT-1`, footprint `ANT-SMD_UFL-R-SMT-1-10`, 3D `ANT-SMD_UFL-R-SMT-1-10` (.wrl + .step).

5. **SW1–SW20: Tactile switches** (5.2×5.2mm SMD, for keypad matrix) — **RESOLVED 2026-07-19**
   - **Selected**: ALPS Alpine SKQGABE010 (LCSC C115351). 5.2×5.2×1.5mm, 1.57N (160gf), 0.25mm travel, 1M cycle life. KiCad model downloaded to `pcb/phone/lib/`.
   - See `docs/project-log.md` 2026-07-19 Keypad Switch Selection for full rationale and tradeoffs.

6. **Y1: 8MHz crystal** (HSE for STM32H743, SMD 3225 4-pin) — **RESOLVED 2026-07-19**
   - **Selected**: ECS Inc ECS-80-12-33Q-GN-TR (LCSC C2595911). 8MHz, 12pF CL, ±30ppm, SMD3225-4P (3.2×2.5mm), AEC-Q200 automotive qualified. 150 in stock on JLC, $1.39.
   - **STM32H743 datasheet Table 34** confirms HSE characterized with 8MHz crystal at CL=10pF; Figure 20 shows "Typical application with an 8 MHz crystal." Load caps: with CL=12pF crystal and Cs≈3pF, CL1=CL2=18pF each.
   - **Why ECS over LIMING**: Both are SMD3225-4P (same 3.2×2.5mm footprint). ECS is a US brand with AEC-Q200 automotive qualification (higher tier). ±30ppm is 100x better than USB FS requires (±2500ppm). 150 stock is enough for prototyping. LIMING 3225-8.00-12-10-10/A (C518155, ±10ppm, $0.32, 1,973 stock) is the production fallback — same footprint.
   - **KiCad model downloaded** via easyeda2kicad: symbol `ECS-80-12-33Q-GN-TR`, footprint `CRYSTAL-SMD_4P-L3.2-W2.5-BL`, 3D `CRYSTAL-SMD_4P-L3.2-W2.5-BL` (.wrl + .step).

7. **L1: 1.5µH power inductor** (for TPS63021DSJR buck-boost) — *part reference corrected from TPS630201 2026-07-19* — **RESOLVED 2026-07-19**
   - **Selected**: Coilcraft XFL4020-152MEC (LCSC C3033018). 1.5µH ±20%, 4×4×2.1mm, magnetic shielded. Isat 4.4A at 20% inductance drop, DCR 14.4mΩ (lowest available at this size), Irms 9.1A. 757 in stock at LCSC, JLC "Extended".
   - **This is the exact datasheet-recommended part family** — TI SLVS916I Table 2 lists XFL4020-152ME (5.1A Isat, 15mΩ DCR); Table 4 lists XFL4020-152ML (low-DCR variant, not on LCSC). The MEC variant on LCSC has Isat 4.4A at the stricter 20%-drop definition (Coilcraft datasheet authoritative — LCSC's "4.6A" is at 30% drop; TI's "5.1A" uses a looser definition).
   - **Isat adequacy**: 4.4A vs the datasheet's "20% above calculated peak" guidance (≥4.8A). Adequate because (a) 4A is the TPS63021 switch current LIMIT (fault condition), not operating current; (b) actual phone peak currents are 2–3A (modem TX burst + display + audio + MCU); (c) calculated peak inductor current at 3A out buck mode ≈ 3.1A, at 3A out boost mode ≈ 3.7A — both well under 4.4A.
   - **Alternative rejected**: Taiyo Yuden LSDND4040WKT1R5MM (C6653414, Isat 7A but DCR 35mΩ — 2.4× higher, noticeable efficiency hit on the most critical rail in the phone).
   - **KiCad model downloaded** via easyeda2kicad: symbol `XFL4020-152MEC`, footprint `IND-SMD_L4.0-W4.0-A`, 3D `IND-SMD_L4.0-W4.0-A` (.wrl + .step).
   - **Datasheet added to `docs/reference/`**: `tps63021.pdf` (TI SLVS916I Rev. I, Oct 2019) — downloaded from https://www.ti.com/lit/ds/symlink/tps63021.pdf. Inductor selection specs verified from §8.2.2.2 + Table 2 + Table 4.
   - See `docs/project-log.md` 2026-07-19 L1 Inductor Selection for full rationale and tradeoffs.

8. **LS1: Earpiece speaker** (10mm round, 8Ω) — **DEFERRED 2026-07-19**
   - ~~The BOM references Taoglas SPKM.10.8.A — check if JLC stocks it~~ **DEFERRED**: Speakers are case-mounted mechanical parts (wire-soldered during final assembly, not PCB-assembled by JLC). No need to spec now — PCB will have wire solder pads (2× 1mm pads, ~5mm apart).
   - *Candidate*: Taoglas SPKM.10.8.A (C6297624, 10mm, 8Ω, 500mW, 100Hz-11kHz, Irish brand) — 0 stock on JLC but available from other distributors.
   - *Revisit at Phase 7* (mechanical/enclosure) when enclosure dimensions and speaker cavity design are known.

9. **LS2: Loudspeaker** (20mm+ mylar, for speakerphone/ringtones) — **DEFERRED 2026-07-19**
   - ~~Search JLC for "20mm speaker mylar SMD"~~ **DEFERRED**: Same as LS1 — case-mounted, not PCB-assembled. PCB will have wire solder pads.
   - *Candidates*: CUI CMS0201KLX (C3312002, 20×20mm, 2W, 424Hz-20kHz, 9.5mm), PUI Audio AS02708CO-WR-R (C7217683, 27×20mm, 1W, 250Hz-20kHz, 6.3mm), PUI Audio AS02008MR-5-R (C3311274, 20mm, 500mW, 500Hz-4kHz, 3.8mm).
   - *Revisit at Phase 7*.

10. **MK1: Microphone** (MEMS or electret, for phone calls) — **RESOLVED 2026-07-19**
    - **Selected**: ZILLTEK ZTS6117 (LCSC C481300). Analog output MEMS microphone, -42dB sensitivity, 59dB SNR, omnidirectional, 1.5V-3.6V, 120µA, 2.75×1.85×0.9mm. 5,129 in stock, $0.53.
    - **ALC5651 compatibility**: ALC5651 has differential analog mic inputs (IN1P/IN2P/IN2N) + adjustable MICBIAS (0.9×MICVDD or 0.75×MICVDD, MICVDD=3.3V → MICBIAS ≈ 2.97V or 2.48V). Supports both analog and digital mics — analog is simpler (no PDM clock routing). ZTS6117 analog output (1.5V–3.6V supply) pairs directly with ALC5651 differential inputs. MICBIAS at 2.97V is within the ZTS6117's 1.5V–3.6V range.
    - **Why ZILLTEK over Knowles**: Knowles SPU0410LR5H-QB (C2918083, gold standard, -38dB/63dB SNR, $0.85) has 0 stock on JLC. ZILLTEK (钰太) is a Taiwanese MEMS sensor brand (reputable) with 5,129 in stock. TDK InvenSense MMICT390200012 (C3171752) is EOL + PDM digital (more complex, and EOL = not for new designs).
    - **KiCad model downloaded** via easyeda2kicad: symbol `ZTS6117`, footprint `MIC-SMD_4P-L2.8-W1.9-P1.84-TL_ZTS6117`, 3D `MIC-SMD_4P-L2.8-W1.9-P1.84-TL_ZTS6117` (.wrl + .step).

### C. Design decisions blocking part selection

These need a decision before the corresponding part can be sourced. Present the tradeoffs and let me decide.

11. **J2: Modem USB connector type** (DNP on rev1 — footprint only) — **RESOLVED 2026-07-19**
    - The block diagram says the modem's USB 2.0 HS port routes to a connector footprint on rev1, populated on a future ecosystem respin.
    - ~~Decision: USB-C, micro-USB, or just unpopulated pads / test points?~~ **RESOLVED**: **Test points only** (VBUS, D+, D-, GND — 4 pads).
    - *Rationale*: The SIM7600 HW Design Manual V1.08 §3.4 explicitly recommends: "The USB interface is a frequently used debug port; it is suggested to reserve test points." The future ecosystem respin routes modem USB through an internal USB 2.0 hub (USB2514) to J1 (the main USB-C), so J2 will **never** be a user-facing connector in the final product. Test points give everything needed for rev1 (firmware updates, debug AT commands, tethering validation via probe clips) at minimal board cost. USB-C DNP was considered (future-proof if ecosystem plan changes) but rejected — a respin can add a connector then if the plan ever changes direction.
    - *J2 is no longer a "connector" — it's 4 test pads*. No part to source. No KiCad footprint download needed (use KiCad built-in `TestPoint:TestPoint_Pad_D1.0mm` or similar).

12. **J3/J4: SIM + microSD — combo socket vs separate sockets** — **RESOLVED 2026-07-19**
    - ~~Option A: Combo SIM+microSD socket (one part, saves space, common in phones)~~
    - ~~Option B: Separate nano-SIM socket + separate microSD socket~~
    - **RESOLVED**: **Separate sockets** (J3 = nano-SIM, J4 = microSD).
    - *Rationale*:
      - **Combo sockets are NOT on JLC/LCSC.** They exist from Molex (104239-1430), JAE, Hirose (KP15B), TXGA (FCD907) — but only via Mouser/DigiKey/RS. Would require consignment to JLC.
      - **Separate sockets are abundantly JLC-stocked** — Zhongdi, HMTCONN, GCT, JAE, ALPS, Molex, Yamaichi, etc. at ~$0.10–1.00.
      - **SIM7600 HW Design Manual V1.08 §3.5.3 recommends a standalone 6-pin nano-SIM socket** (Amphenol C707 10M006 512). §3.5.1 mentions 8-pin version for card detection (USIM_DET hot-plug).
      - **Electrical independence matches physical separation**: SIM is on the modem's USIM interface (1.8V/3.0V auto-detect, near the modem); microSD is on the MCU's SDMMC peripheral (3.3V, near the MCU). Separate sockets let us place each near its controller, minimizing trace lengths (SIM7600 manual §3.5.2: "SIM traces should keep away from RF lines, VBAT and high-speed signal lines... traces should be as short as possible").
      - The flip phone base has plenty of room — the marginal space saving of a combo socket isn't worth a consignment part.
    - *Next*: ~~source J3 (nano-SIM, 8-pin with card detect, OEM preferred) and J4 (microSD push-push, OEM preferred) from JLC~~ **RESOLVED 2026-07-19** — J3 = SHOU HAN NANO SIM XG6P H1.35 (C7529386, hinged 6-pin, 38,255 stock, $0.146). J4 = Molex 472192001 (C164170, hinged 8-pin, 16,177 stock, $0.765). Both hinged (user preference — top-loading, no lateral clearance needed). Amphenol nano-SIM (C5429441) rejected — out of stock + expensive. Molex doesn't make nano-SIM hinged. KiCad models downloaded. See project-log.md 2026-07-19 J3/J4 Sourcing.

13. **J7/J8/J9/J10: FPC ZIF connectors** ~~(BLOCKED — needs specific ST7789V panel pick)~~ — **RESOLVED 2026-07-19**
    - ~~The display is locked as ST7789V SPI 2.0" 240×320, but the specific module/panel determines the FPC pin count and pitch~~
    - ~~Decision needed: which specific ST7789V module?~~ **RESOLVED**: HS HS20HS072RX (LCSC C5329582) — 2.0" IPS TFT, ST7789T3, 12-pin 0.5mm ZIF FPC, 4 parallel LEDs, $3.42, 1786 in stock. JLC-assemblable. See project-log.md 2026-07-19 Display Panel Selection.
    - **Flip form factor also locked 2026-07-19**: two PCBs (main + display daughterboard) + hinge FFC. New connectors J8-J10 added to PARTS_TRACKING.md (hinge FFC 14-pin + outer display). See project-log.md 2026-07-19 Flip Form Factor entry.
    - **All four FPC connectors LOCKED 2026-07-19**: HDGC 0.5K-HX series (hinged lid, double-sided contacts, 1mm height — same series for all four). J7=C2919494 (12-pin), J10=C2919492 (8-pin), J8/J9=C2919495 (14-pin, 2 qty). KiCad models downloaded via easyeda2kicad (14-pin has no 3D model — acceptable). Double-sided contacts eliminate top/bottom orientation risk. See project-log.md 2026-07-19 FPC ZIF Connectors.
    - **Outer display re-selected 2026-07-19**: Wisevision N114 (0.7mm pitch — no JLC connectors) replaced by EastRising ER-TFT1.14-2 (BuyDisplay, 8-pin 0.5mm FPC, ST7789V, $3.27). Both display panels purchased separately from PCB and assembled by user (ZIF plugs in post-assembly). See project-log.md 2026-07-19 Outer Display Re-Selection.
    - **Remaining**: hinge FFC cable (14-pin 0.5mm, 0.3mm thick) — deferred to Phase 7 (length depends on hinge geometry).

### Workflow

For each item:
1. Research the part (search JLC/LCSC, check datasheets in `docs/reference/` if applicable)
2. Present options with tradeoffs (for decisions) or a recommended pick (for mechanical parts)
3. Once I confirm, download the KiCad model (via `easyeda2kicad --full --lcsc_id=C####### --output "pcb/phone/lib"` for JLC parts, or Ultra Librarian for the two non-JLC ICs)
4. Update `pcb/PARTS_TRACKING.md` (check the boxes, record C#)
5. After all parts are sourced, we'll import the library into KiCad and start the schematic

### Priority order

1. ~~**A1, A2** (MAX9880A, TPS630201) — these are the only missing ICs; block schematic completion~~ **RESOLVED 2026-07-19**: ~~A1 (MAX9880A) integrated from Ultra Librarian~~ **SUPERSEDED 2026-07-19**: MAX9880A replaced by Realtek ALC5651-CG (C963633, JLC Extended — no consignment). A2 (TPS630201→TPS63021DSJR) — phantom part number corrected, downloaded from JLC (C202140). Both ICs now have KiCad models. **No consignment parts remain.** See project-log.md 2026-07-19.
2. ~~**C13** (display panel pick) — blocks J7, which blocks layout planning~~ **RESOLVED 2026-07-19**: HS HS20HS072RX (C5329582) selected. 12-pin 0.5mm ZIF FPC. Flip form factor also locked (two boards + hinge FFC). J7 blocker cleared. All four FPC connectors (J7/J8/J9/J10) locked to HDGC 0.5K-HX series + KiCad models downloaded. Outer display re-selected to ER-TFT1.14-2 (BuyDisplay). See project-log.md 2026-07-19.
3. ~~**B7** (inductor L1) — critical for power design, needs TPS63021DSJR datasheet verification~~ **RESOLVED 2026-07-19**: Coilcraft XFL4020-152MEC (C3033018) — datasheet-recommended part (TI SLVS916I Table 2 + Table 4). 1.5µH, Isat 4.4A, DCR 14.4mΩ, 4×4×2.1mm. TPS63021 datasheet added to `docs/reference/tps63021.pdf`. KiCad model downloaded. See project-log.md 2026-07-19 L1 Inductor Selection.
4. ~~**C11, C12** (J2, J3/J4 decisions) — block connector sourcing~~ **RESOLVED 2026-07-19**: C11 J2 = test points only (no connector, per SIM7600 manual §3.4 recommendation). C12 J3/J4 = separate sockets (combo not on JLC; SIM7600 manual recommends standalone; electrical independence matches physical separation). See project-log.md 2026-07-19 J2/J3/J4 Decisions.
5. **B3, B4, B6, B8, B9, B10** (remaining mechanical: USB-C, U.FL, crystal, transducers) — can proceed in parallel. **User preference (2026-07-19): OEM/brand-name connectors, especially USB-C.** Apply the existing project principle (already swapped TECH PUBLIC clones for ST originals on U10/U11) to all connector sourcing.

### Notes

- All JLC parts should be OEM/brand-name where available (we already swapped TECH PUBLIC clones for ST originals on U10/U11)
- Check stock quantities — for 2-board assembly with overage, we need at least 5-10 of each part
- The SIM7600NA-H (C5380303) is a pre-order part — the footprint is downloaded but the part itself needs to be pre-ordered and lead time factored in
- ~~Two consigned parts (MAX9880A, TPS630201) will be bought from Mouser/DigiKey and shipped to JLC — factor in shipping time~~ **Updated 2026-07-19**: ~~Only ONE consignment part remains (MAX9880A from Mouser)~~ **NO consignment parts remain** — MAX9880A replaced by Realtek ALC5651-CG (C963633, JLC Extended). TPS630201 was a phantom part number — corrected to TPS63021DSJR (LCSC C202140, JLC-stocked). All parts now JLC-sourced.
