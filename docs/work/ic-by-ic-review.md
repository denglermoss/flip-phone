---
status: active
updated: 2026-08-16
---
# IC-by-IC Schematic Review

> **Created**: 2026-08-02
> **Purpose**: Track results of a full IC-by-IC schematic review against vendor datasheets. The user (project lead) reviews each IC and asks questions; the agent verifies against the datasheet (primary source) and schematic (read-only, minimal). Decisions and findings are recorded here.
> **Context**: Project is switching from PCIe to LGA modem. Review may surface items affected by that switch.
> **Source of truth for pin connections**: The **KiCad schematic** (`pcb/phone/phone.kicad_sch`) is the pin-level source of truth. `docs/work/block-diagram.md` provides design intent and historical planning reference. This doc records review findings and deferred tasks only — it does not duplicate wiring specs.

## Review Process

1. **One IC at a time.** The user drives the review — examines the schematic and asks questions about each IC.
2. **Datasheets are the primary source.** The agent verifies answers against the local datasheet in `docs/datasheets/` (via the PDF MCP server), not memory or web snippets. If a datasheet can't be read (encrypted, scanned, etc.), ask the user to read it rather than guessing.
3. **Schematic is read-only and minimal.** Only consult the schematic (`pcb/phone/*.kicad_sch`) to confirm actual net connections when needed — don't re-derive the whole design from it.
4. **Record findings here.** Each IC gets a section with the questions asked, datasheet-verified answers, assessment, and severity (Info / Action / Deferred).
5. **Deferred tasks go in the Deferred Tasks table** with an ID (DEF-NNN) so they can be tracked and picked up later.

---

## Review Status

| IC | Refdes | Sheet | Status | Date Reviewed |
|----|--------|-------|--------|---------------|
| TPS63021DSJR (3.3V buck-boost) | U8 | Power | ⚠️ Findings | 2026-08-02 |
| TPS7A0218 (1.8V LDO) | U9 | Power | ☐ Pending | |
| MCP73831 (LiPo charger) | U11 | Power | ☐ Pending | |
| MAX17048 (fuel gauge) | U10 | Power | ☐ Pending | |
| USBLC6-2 (USB ESD) | D1 | Power | ☐ Pending | |
| STM32H743ZI (MCU) | U1 | MCU | ☐ Pending | |
| SIM7600 (modem) | U2 | Modem | ☐ Pending | |
| ALC5651 (codec) | U5 | Codec | ☐ Pending | |
| SN74AXC4T774 (level shifter) | U12 | Codec | ☐ Pending | |
| TXB0108 (level shifter) | U3 | Display | ☐ Pending | |
| ST7789 (main display) | — | Display | ☐ Pending | |
| ~~ST7789 (outer display)~~ | — | ~~Display_Daughter~~ | **DROPPED 2026-08-16** | | Outer display + daughterboard sheet eliminated with candybar pivot. See project-log.md 2026-08-16 Form Factor Pivot. |

---

## U8 — TPS63021DSJR (3.3V buck-boost)

**Datasheet**: TI SLVS916I (`docs/datasheets/tps63021.pdf`), Rev. I, Oct 2019
**Reviewed**: 2026-08-02

### Q1: PS/SYNC tied to GND — datasheet typical app shows it tied to VINA and EN with 100nF cap to GND

**Finding**: User is correct. The datasheet typical application circuit (Figure 7, p13) ties **VINA, EN, and PS/SYNC together** at a common node, with C3 (100nF) from that node to GND. Verified by tracing the vector SVG extraction of page 13:

- VINA pin (path y≈922) → wire to (659.43, 922) → up to (659.43, 652) → C3 bottom plate
- PS/SYNC pin (path y≈742) → wire to junction at (659.43, 742) — this junction sits on the VINA wire (which passes through y=742 between y=922 and y=652)
- EN pin (path y≈832) → wire to junction at (659.43, 832) — same VINA wire
- C3 top plate → GND symbol

So in the TI typical application: **EN = PS/SYNC = VINA** (all tied together). Since VINA is internally derived from VIN (~VIN level), this means:
- EN = HIGH → chip always enabled
- **PS/SYNC = HIGH → power-save DISABLED (PWM mode always)**

Our schematic ties PS/SYNC to GND, which **enables power-save mode** (PS/SYNC = LOW). This is a **deliberate deviation** from the datasheet typical application.

**Assessment**: Our choice is valid and arguably better for a battery-powered device:
- **Power-save ON (our choice)**: Higher efficiency at light load (<100mA). Auto-switches to PWM above ~100mA. Standby load (~20-50mA) benefits. Cost: slightly higher output ripple in power-save mode (~3.5% above nominal vs lower in PWM).
- **PWM always (datasheet typ app)**: Lower output ripple, worse light-load efficiency. The typical app optimizes for ripple; we optimize for battery life.

The datasheet §7.4.4 (p12) explicitly supports both: "To enable power save mode, PS/SYNC must be set low... The power save mode can be disabled by programming high at the PS/SYNC."

**One consideration**: The datasheet ties PS/SYNC to VINA (not directly to VIN or VOUT). VINA is the internally-derived control supply, so it's at a stable logic level. If we ever wanted PWM-always mode, we should tie PS/SYNC to VINA (as the datasheet shows) rather than to VIN or +BATT directly, because VINA is the proper logic-level reference for this pin. But since we're tying to GND, this doesn't apply.

**Conclusion**: No change needed. Document the rationale (already in block-diagram.md line 228). The deviation is intentional and appropriate.

**Severity**: Info (no action)

### Q2: PG pullup — datasheet shows 1MΩ, we have 10kΩ

**Finding**: User is correct. The datasheet typical application (Figure 7, p13) shows **R3 = 1MΩ** from PG to VOUT. Our schematic has **10kΩ** to +3.3V (VOUT).

**Assessment**: Both values are valid. The PG pin is open-drain (§7.3.4, p10: "The output is open-drain and can be left open if not needed. By connecting a pullup resistor to the supply voltage of the externally connected logic, it is possible to adjust the voltage level within the absolute maximum ratings."). The datasheet does not specify a min/max pullup value.

Tradeoffs:
| Value | Current when PG=LOW | Rise time | Suitable for |
|-------|---------------------|-----------|--------------|
| 1MΩ (datasheet) | 3.3µA | Slow (high RC) | Static polling, minimal current |
| 10kΩ (ours) | 330µA | Fast (sharp edges) | **EXTI interrupt-driven monitoring** |

Our design wires PG to an MCU GPIO with EXTI (interrupt) for brown-out warning (block-diagram.md line 229). A 10kΩ pullup gives sharper rising edges for reliable interrupt triggering. The 330µA current only flows when PG is low (VOUT out of regulation — a fault condition, not normal operation). In normal operation, PG is high (open-drain off) and zero current flows through the pullup.

**Conclusion**: No change needed. 10kΩ is the right choice for interrupt-driven PG monitoring. The datasheet's 1MΩ optimizes for minimal current in applications where PG is polled or unused.

**Severity**: Info (no action)

### Q3: Power switch function — ~~momentary slide switch architecture (soft on/off + 5s hard off)~~ **SUPERSEDED 2026-08-17: maintained power switch in battery path + MCU sleep timer**

**Finding**: ~~Architecture decided 2026-08-02. SW21 changed from maintained slide (SSSS811101, direct EN control) to **momentary slide switch** (ALPS SSAL120100, LCSC C335996 — SPDT, spring-return, ALPS "Single-side Recoil Type"). Three functions:~~
~~1. **Short press when off** → power on (release hard-off latch → EN high → boot, or EXTI wakes MCU from STOP)~~
~~2. **Short press when on** → soft off (MCU EXTI → graceful shutdown → STOP mode)~~
~~3. **5-second hold** → hard off (RC timer → latch → EN low → 3.3V rail dies; pure hardware, works if MCU hung)~~

**SUPERSEDED 2026-08-17**: Replaced with a simple maintained power switch in the battery path + MCU inactivity timer for soft off. See project-log 2026-08-17. Key changes:
- **Hard off**: Maintained switch physically disconnects battery from +BATT net. 0 power draw. No latch circuit needed.
- **Soft off**: MCU inactivity timer → STOP mode. Firmware-driven, all firmware details deferred until after PCB ordered.
- **EN pin**: Reverts to always-on (1MΩ pullup to +BATT). No switch on EN.
- **Switch part**: Changes from SSAL120100 (signal-level momentary, 10mA@5V) to TBD maintained power-rated switch (≥3A). Specific part TBD at schematic time.
- **Charging while off**: Not supported (switch disconnects battery from charger VBAT path). Accepted.
- **DEF-002 (latch circuit)**: Moot — no latch needed.

> **The following text describes the superseded 2026-08-02 architecture and is retained for history. All of it is struck. See the SUPERSEDED note above and project-log 2026-08-17 for the current architecture.**

~~**Switch type correction (2026-08-02)**: Previously mislabeled as "momentary pushbutton." SSAL120100 is a **momentary slide switch** — SPDT, 2 positions, springs back to the rest position ("recoil"). Functionally equivalent to a momentary pushbutton for this circuit. The SPDT contact (common + NO/NC) may be useful for the latch circuit (separate SET/RESET edges). **⚠️ NRND**: ALPS marks this part "Not Recommended for New Designs." Still in stock at LCSC (C335996) for now, but an active alternative should be sourced before PCB fab. Not a blocker for the architecture decision.~~

~~**Long-press behavior (decided 2026-08-02)**: Simple for rev1 — short press = soft off, 5s hold = hard off. The MCU does **not** intercept long presses for a "Power off?" menu. The 5s hardware timer is the unconditional kill (works even if MCU is hung). Firmware does not need to distinguish press lengths. A menu-based power-off can be added post-rev1.~~

~~**Critical verification finding**: The naive "RC timer → transistor → EN" approach does NOT work because EN has a permanent 1MΩ pullup to +BATT. Releasing the switch after a 5s hold would immediately re-power the system. A **latching circuit** is required:~~
~- SET (5s hold via RC timer) → holds EN low persistently after switch release~
~- RESET (short press) → releases EN → 1MΩ pullup brings rail up → boot~
~- RESET must work in pure hardware (MCU is unpowered during hard-off)~

~~**Unified power-on**: A short press does the right thing in both states because the hardware paths are naturally exclusive — when the rail is up, the latch reset is a no-op and the EXTI fires; when the rail is dead, there's no EXTI to fire, so the latch reset does the work. Same user action, hardware picks the right path automatically.~~

~~**Firmware note — power-on race condition**: When the latch releases and the rail comes up, the MCU boots over ~tens of ms. The switch press that triggered boot is ending right around then. Firmware must **ignore switch events for the first ~500ms after boot**, otherwise the tail end of the "power on" press could be read as a "soft off" press and immediately shut the system back down. This is a firmware concern, not hardware, but must be noted in the firmware task spec.~~

~~**Latch implementation (DEF-002)**: Deferred — not yet designed. Two options on the table:~~
~- (A) SR latch from 2 transistors + RC timer (~$0.10, ~5-8 components) — cheaper, more educational, more failure modes~
~- (B) Dedicated pushbutton on/off controller IC (e.g., LTC2950, ~$2-3, single IC) — more reliable, less educational~
~- **Decision**: Resolve when drawing the power schematic section. Not a blocker for the architecture.~

~~**Schematic impact**: Current SW21 wiring (maintained switch directly on EN: ON=+BATT→R1→SW21→EN, OFF=EN→SW21→GND) must be replaced with the momentary switch + latch circuit. This is a power section change — requires explicit approval per pcb/AGENTS.md rule 9 (protected section).~~

~~**Charging while off**: Still works — MCP73831 VBUS→+BATT path is independent of TPS63021. Hard-off kills +3.3V but charging continues. ✓~~

~~**Modem during hard-off**: MPCIe modem is on +3.3V (via VCC pins), so hard-off kills the modem too. This is desirable — true power-off, not standby. For soft-off (MCU STOP), the modem stays registered on the network for incoming calls (standby, not off).~~

~~**Severity**: Architecture decided. Latch implementation = deferred design task (DEF-002, resolve at power schematic drawing time).~~

---

## Deferred Tasks

| ID | Description | Origin | Date | Status |
|----|-------------|--------|------|--------|
| DEF-001 | Power switch architecture: what does "off" mean? Does modem VBAT need a separate switch? How does LGA modem change this? SW21 placement. | U8 review Q3 | 2026-08-02 | **Resolved 2026-08-02, SUPERSEDED 2026-08-17** — replaced by maintained power switch in battery path + MCU sleep timer. See Q3 above + project-log 2026-08-17. |
| DEF-002 | ~~Latch circuit implementation for hard-off persistence: SR latch (2 transistors + RC timer) vs dedicated IC (LTC2950). Component selection, schematic wiring, RC time constant calc.~~ **MOOT 2026-08-17** — no latch circuit needed. The maintained power switch physically disconnects the battery; no latch is required to hold EN low. | U8 review Q3 | 2026-08-02 | **Moot (2026-08-17)** — eliminated by power switch simplification. |

---

## Change Log

| Date | IC | Change |
|------|----|--------|
| 2026-08-02 | U8 | Initial review: Q1 (PS/SYNC — no change, deliberate deviation), Q2 (PG pullup — no change, correct for EXTI), Q3 (power switch — deferred) |
| 2026-08-02 | U8 | Q3 updated: power switch architecture decided (momentary slide switch, soft on/off + 5s hard off). DEF-001 resolved, DEF-002 opened (latch circuit TBD). SW21 part changed SSSS811101 → SSAL120100. |
| 2026-08-02 | U8 | Q3 corrected: SSAL120100 is a momentary **slide** switch (SPDT, spring-return), not a pushbutton. Added NRND flag. Added long-press decision (simple for rev1 — no menu, 5s hardware kill only). Added unified power-on explanation + power-on race condition firmware note. DEF-002 deferred to power schematic drawing time. |
| 2026-08-17 | U8 | Q3 SUPERSEDED: Power switch architecture simplified to maintained switch in battery path + MCU inactivity timer. Latch circuit eliminated (DEF-002 moot). EN reverts to always-on. Switch part changes from SSAL120100 to TBD power-rated maintained switch. See project-log 2026-08-17. |
