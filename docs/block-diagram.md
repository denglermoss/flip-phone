# Schematic Reference

> **Status**: Living document — updated section-by-section as the schematic is drawn in KiCad. Each section lists components, signals, power nets, and connection notes for that part of the design. Use this alongside KiCad while drawing.
>
> **Approach**: **Flat schematic with labeled regions** (not hierarchical sheets). All components on one schematic (or a few A3/A4 pages with off-sheet connectors). Each block occupies a clearly labeled rectangular region. Power nets are global power symbols. Inter-block signals use net labels (not hierarchical pins).
>
> **Why flat**: The board is ~30-40 components / ~8 ICs — on the boundary where hierarchical sheets add overhead (pin matching, connector-splitting awkwardness) without much benefit. Flat-with-regions keeps everything visible and avoids the "USB-C connector belongs to both power and MCU" problem.

## Power Nets (Global)

Defined once as power symbols, referenced everywhere. **Names are case-sensitive — pick exact names and stick with them.**

| Net name | Voltage | Source | Consumers |
|----------|---------|--------|-----------|
| `VBUS` | 5V | USB-C connector (J1) | MCP73831 charger input (U6), MCU VBUS sense (via divider — deferred to MCU section) |
| `+BATT` | 3.4–4.3V (LiPo) | LiPo via battery connector (J_BATT, JST S2B-PH-SM4-TB, C295747) | SIM7600 VBAT pins (U2), TPS63021DSJR input (U4), MAX17048 VDD (U7 — power + voltage sense) |
| `+3.3V` | 3.3V | TPS63021DSJR buck-boost output (U4) | MCU, display, SD card, codec MICVDD/DBVDD(3V3 side), level shifter VCCB |
| `+1V8` | 1.8V | TPS7A0218 LDO output (U5, from +3.3V) | ALC5651 codec analog (AVDD/DACREF/CPVDD), codec DBVDD (PCM side), level shifter VCCA |
| `GND` | 0V | Common ground (USB-C GND, LiPo −, all ICs) | All blocks |

> **`+BATT` is separate from `+3.3V`** — modem 2A bursts must not droop the MCU rail. LiPo connects directly to `+BATT` (no regulator). Bulk capacitance (100–470µF ceramic + tantalum) at modem VBAT pins, physically close to the modem. **Deferred to modem schematic section** — the power schematic has ~25µF on `+BATT` (C2/C3=10µF, C10=4.7µF); the modem section must add the 100–470µF bulk caps close to the modem's VBAT pins.

> **Why buck-boost (TPS63021DSJR) for +3.3V, not an LDO?** An LDO can only step *down*. The LiPo ranges 3.0–4.2V, and +3.3V must stay at 3.3V. Below 3.3V (~40% state of charge), an LDO drops out and the rail sags with the battery. A buck-boost buckles 4.2V→3.3V at full charge and boosts 3.0V→3.3V near empty — stable 3.3V across the whole discharge curve. Also: an LDO at 2-3A would dissipate ~1.8W as heat (Vdrop × I); the buck-boost is ~90% efficient. On a battery device, that efficiency directly determines standby/talk time.

### `VBUS` (5V) — sources and consumers

**Source:**
| Source | Pin | Notes |
|--------|-----|-------|
| USB-C connector (J1) | VBUS pins (A4, B9) | 5V from USB host/charger. USBLC6-2 ESD on D+/D- **and VBUS** (U10 — protects all three USB-C signal paths). |

**Consumers:**
| Consumer | Pin | Notes |
|----------|-----|-------|
| MCP73831 charger IC (U6) | VDD (pin 1) | Charger input — USB 5V → LiPo charge current (500mA). |
| MCU (STM32H743) | VBUS sense GPIO (TBD) | MCU reads VBUS to detect USB connection / charger attached. Not the USB OTG_FS VBUS pin (that's for USB enumeration) — a separate GPIO on any 3.3V-tolerant pin. VBUS is 5V, needs a resistor divider. **Deferred to MCU schematic section.** Note: the originally suggested 100k/47k divider gives ~1.6V, which is marginal for STM32H7 logic-high (CMOS VIH = 0.7×VDD = 2.31V at 3.3V; TTL-input VIH = 1.7V at 3.0V). Use 100k/68k → ~2.02V or 68k/47k → ~2.04V for reliable logic-high detection. |

### `+BATT` (3.4–4.3V LiPo) — sources and consumers

**Source:**
| Source | Pin | Notes |
|--------|-----|-------|
| LiPo battery via battery connector (J_BATT — JST S2B-PH-SM4-TB, C295747) | + terminal | Single-cell LiPo, 3.0–4.2V operating, 4.3V absolute max. Direct to +BATT net — no regulator, no switch. **Connector**: JST PH 2-pin SMD right-angle, 2A rated, mates with pre-crimped plugs on Adafruit/SparkFun/Amazon LiPo batteries. **Battery itself is NOT on JLC** (hazmat shipping) — buy separately with JST-PH plug attached. |

**Consumers:**
| Consumer | Pin | Notes |
|----------|-----|-------|
| SIM7600NA-H modem (U2) | VBAT pins (multiple — see HW Design Manual §3.1) | 2A TX bursts. **Bulk capacitance required here**: 100–470µF ceramic + tantalum, placed at the VBAT pins. Short, wide PDN traces. **Deferred to modem schematic section** — power schematic has ~25µF on +BATT; modem section must add the bulk caps. |
| TPS63021DSJR buck-boost (U4) | VIN (pin 1, 2, 3) | Input to the 3.3V buck-boost. Powers everything on +3.3V. |
| MAX17048 fuel gauge (U7) | CELL+ (pin 3) | Sense input — fuel gauge measures +BATT voltage. No current flows into this pin (high-Z). |

**Also flows INTO +BATT from charger:**
| Source | Pin | Notes |
|--------|-----|-------|
| MCP73831 charger IC (U6) | VBAT (pin 3) | Charger output — current INTO the battery when USB is connected. Same net as the battery (+BATT). |

### `+3.3V` (3.3V) — sources and consumers

**Source:**
| Source | Pin | Notes |
|--------|-----|-------|
| TPS63021DSJR buck-boost (U4) | VOUT (pin 10, 11, 12) | Fixed 3.3V output, ~3A max. Needs 3×22µF output caps + 0.1µF VINA bypass (datasheet §8.2.2.4). FB pin tied to VOUT directly (fixed-output variant — no divider). |

**Consumers:**
| Consumer | Pin | Notes |
|----------|-----|-------|
| MCU (STM32H743ZI) | VDD (multiple), VDDA (analog), VBAT (RTC — not used, tie to +3.3V) | Bulk + 100nF decoupling per VDD pair. VDDA via ferrite bead + 1µF (analog isolation). |
| Display (main + outer, via hinge flex J8) | IOVCC/VCC, LEDA (backlight anode) | Through hinge flex. Backlight LEDA also from +3.3V via current-limit resistors. |
| microSD socket (J4) | VDD | SD card power (3.3V). Card detects its own voltage. |
| ALC5651 codec (U3) | MICVDD, DBVDD (3.3V I/O side) | MICVDD is always 3.3V (mic bias). DBVDD on I2S-2 (MCU side) is 3.3V. **Open question**: does DBVDD split per port, or is there one DBVDD? Check ALC5651 datasheet pinout. |
| Level shifter (U8 TXB0108) | VCCB (pin 19) | 3.3V side — MCU-facing. |
| MAX17048 fuel gauge (U7) | VDD (pin 3) | Power + voltage sense input. Connect to +BATT (raw LiPo). MAX17048 senses battery voltage on VDD, not on a separate CELL pin. |
| USB-C CC1/CC2 pull-downs (J1) | 5.1kΩ to GND on each CC pin | Identifies the phone as a UFP (upstream-facing port / device). Not a rail consumer per se, but lives on the USB-C connector. |

### `+1V8` (1.8V) — sources and consumers

**Source:**
| Source | Pin | Notes |
|--------|-----|-------|
| TPS7A0218 LDO (U5) | OUT (pin 1) | 1.8V fixed, 200mA max. Input from +3.3V. Load is light (~10–20mA codec + level shifter). Needs 1µF in + 1µF out ceramic (datasheet §9.2). |

**Consumers:**
| Consumer | Pin | Notes |
|----------|-----|-------|
| ALC5651 codec (U3) | AVDD, DACREF, CPVDD (analog supply) | 1.8V analog. The codec's digital core (1.2V) comes from an internal LDO — no external 1.2V rail needed. |
| ALC5651 codec (U3) | DBVDD (for I2S-1 / PCM port — modem side) | 1.8V digital I/O for the PCM port facing the SIM7600. Matches SIM7600's 1.8V PCM lines (no level shifter needed on PCM). |
| Level shifter (U8 TXB0108) | VCCA (pin 2) | 1.8V side — modem-facing. VCCA ≤ VCCB is required (1.8V ≤ 3.3V ✓). |

**Open question — modem VDD_1V8 pin:** The SIM7600 has its own VDD_1V8 output pin (1.8V LDO, 50mA max) that the reference design (HW Design Manual §3.6.2) uses to power the codec. Do we use the modem's VDD_1V8 (saves the TPS7A0218) or our own U5 (guarantees 200mA headroom, independent of modem state)? **Tentative: use U5** — the ALC5651 may draw more than 50mA, and relying on the modem's LDO couples codec power to modem power state. Confirm at schematic time by checking ALC5651 analog supply current in the datasheet.

### `GND` (0V) — sources and consumers

**Source:** Common ground — USB-C GND pins (J1 A12, B12, B1, A1), LiPo negative terminal (J_BATT), exposed pad / ground pours on PCB.
**Consumers:** Every IC has GND pin(s). Every connector has GND. Every decoupling cap has a GND side. The PCB ground plane is a single continuous reference for all rails. No isolated grounds (no split planes) — single GND net everywhere.

### Power IC pinouts and connections

> **Source for all pinouts**: vendor datasheets, extracted via the PDF MCP server. TPS63021 from `docs/reference/tps63021.pdf` (TI SLVS916I §5 Pin Functions). TPS7A02 from TI SBVS277C §5 (DBV/SOT-23-5 variant). MCP73831 from `docs/reference/mcp73831.pdf` (Microchip DS20001984H — **DFN-8 2×3mm variant, not SOT-23-5**; see U6 correction below). MAX17048 from `docs/reference/max17048.pdf` (ADI/Maxim Rev 7, §Pin/Bump Descriptions p6 — TDFN-8 2×2mm variant). J1 USB-C pinout from the KiCad symbol `TYPE-C-31-M-12` (downloaded from LCSC C165948 via easyeda2kicad) — pinout follows the USB Type-C specification (USB-IF).

#### J1 — Korean Hroparts TYPE-C-31-M-12 (USB-C 16-pin receptacle, USB 2.0)

> Datasheet: LCSC product page C165948. Pinout follows the USB Type-C specification (USB-IF Rev 1.4+) — standard for all 16-pin USB 2.0 USB-C receptacles. The part datasheet confirms mechanical dimensions, current rating (5A/20V), and mating cycles (10K). KiCad symbol `TYPE-C-31-M-12`, footprint `USB-C_SMD-TYPE-C-31-M-12_1`. **LOCKED 2026-07-19.**

**Pinout (from KiCad symbol — paired VBUS/GND pins are combined in the symbol):**
```
Signal pins (12):
  A1B12  GND          B1A12  GND
  A4B9   VBUS         B4A9   VBUS
  A5     CC1          B5     CC2
  A6     DP1 (D+)     B6     DP2 (D+)
  A7     DN1 (D-)     B7     DN2 (D-)
  A8     SBU1         B8     SBU2

Mechanical/mounting tabs (4):
  1, 2, 3, 4  EH (shield/mounting — connect to GND)
```

| Pin(s) | Name | Net / connection | Notes |
|--------|------|------------------|-------|
| A4B9, B4A9 | VBUS | `VBUS` (5V) | Two VBUS pins in the symbol (each combines two physical pads: A4+A9 and B4+B9). Tie both to the `VBUS` net. 5V from USB host/charger when connected. |
| A1B12, B1A12 | GND | `GND` | Two GND pins (each combines two physical pads: A1+B12 and B1+A12). Tie both to `GND`. |
| A5 | CC1 | 5.1kΩ to `GND` | Configuration Channel 1. **5.1kΩ pull-down identifies the phone as a UFP (upstream-facing port / device)** — tells the charger/host to provide 5V on VBUS. Without this, the charger won't output VBUS. |
| B5 | CC2 | 5.1kΩ to `GND` | Configuration Channel 2. Same 5.1kΩ pull-down as CC1. CC1 and CC2 each get their own resistor (do NOT tie CC1 and CC2 together before the resistor — they serve different plug orientations). |
| A6, B6 | DP1, DP2 | `USB_DP` (D+) | USB 2.0 D+ differential pair. A6 and B6 are the same signal on opposite plug orientations — **tie A6 and B6 together** on the PCB. Routes through USBLC6-2 ESD protection (U10) to MCU USB OTG_FS D+ pin. |
| A7, B7 | DN1, DN2 | `USB_DN` (D-) | USB 2.0 D- differential pair. Same as D+ — **tie A7 and B7 together**. Routes through USBLC6-2 ESD to MCU USB OTG_FS D- pin. |
| A8 | SBU1 | Float or `GND` | Sideband Use 1. Not used for USB 2.0. Leave floating or tie to GND. Used in alternate modes (DisplayPort, analog audio) — not applicable here. |
| B8 | SBU2 | Float or `GND` | Sideband Use 2. Same as SBU1 — not used. |
| 1, 2, 3, 4 | EH | `GND` | Mechanical mounting tabs / shield. Connect to GND for shielding and mechanical robustness. |

**External components:**
- R_CC1 = 5.1kΩ to GND on CC1 (identifies as UFP)
- R_CC2 = 5.1kΩ to GND on CC2 (identifies as UFP)
- USBLC6-2 ESD protection on D+/D- **and VBUS** (U10 — see §ESD Protection for pinout. The USBLC6-2 is a 6-pin device that protects all three USB-C signal paths: D+, D-, and VBUS. VBUS ESD is NOT handled by the MCP73831's internal protection alone — the USBLC6-2 is the primary ESD diode for the VBUS rail entry point.)

**VBUS power path:**
```
USB-C J1 (A4B9, B4A9) → VBUS net → MCP73831 VDD (pin 1, U6)
                                       → MCU VBUS sense (via resistor divider)
```
- VBUS is 5V when a USB host/charger is connected, 0V when unplugged.
- MCP73831 takes VBUS as its charger input → charges the LiPo at 500mA (R_PROG = 2kΩ).
- MCU senses VBUS via a resistor divider (5V → ~1.6V at GPIO) to detect "USB connected / charger attached." This is a separate GPIO from the USB OTG_FS VBUS pin (which is for USB enumeration, not charger detection).

**USB data path:**
```
USB-C J1 (A6+B6, A7+B7) → USBLC6-2 ESD (U10) → MCU USB OTG_FS (D+, D-)
```
- USB 2.0 data goes through ESD protection to the MCU's USB OTG_FS peripheral.
- Used for firmware upload, debug, and file transfer (12 Mbps — sufficient for these tasks).
- NOT used for charging — charging is handled by the VBUS → MCP73831 path above.

**Notes:**
- **Why 5.1kΩ on CC pins**: USB-C uses the CC pins to determine plug orientation and device role. A UFP (device) presents 5.1kΩ to GND on its CC pins. A DFP (host/charger) presents 56kΩ to VBUS on its CC pins and outputs 5V on VBUS when it detects the 5.1kΩ. Without the 5.1kΩ, the charger thinks nothing is connected and won't provide VBUS.
- **D+ and D- pairing**: USB-C has two sets of D+/D- pins (A6/A7 and B6/B7) for plug-reversal symmetry. Tie each pair together on the PCB — the USB 2.0 spec allows this because only one set is active at a time (determined by CC orientation).
- **SBU pins**: Leave floating. SBU is only used for alternate modes (DisplayPort, analog audio accessory mode). We don't use any alt modes.

#### U6 — MCP73831-2ACI/MC (LiPo charger, DFN-8 2×3mm + exposed pad)

> Datasheet: `docs/reference/mcp73831.pdf` (Microchip DS20001984H). "-2ACI" = 4.20V regulation (LiPo standard). **Package: DFN-8 2×3mm with exposed pad** (NOT SOT-23-5 — the block diagram previously said SOT-23-5, corrected 2026-07-21 after downloading the datasheet and verifying the downloaded KiCad footprint `TDFN-8_L3.0-W2.0-P0.50-BL-EP1.6` has 9 pads). LCSC C150772. The "/MC" suffix in Microchip's naming usually means SOT-23-5, but LCSC C150772 maps to the DFN-8 variant — verify at order time.

**Pinout (DFN-8 2×3mm, top view — pin 1 marked with dot, exposed pad on bottom):**
```
       ┌──────────┐
   1 ──┤ VDD      ├── 8  PROG
   2 ──┤ VDD      ├── 7  NC
   3 ──┤ VBAT     ├── 6  VSS
   4 ──┤ VBAT     ├── 5  STAT
       └──────────┘
       (Exposed pad 9 = VSS/GND)
```

> **Pinout corrected 2026-07-22** — previous version had pins 2/3/4/6/7/8 wrong (written from memory before datasheet verification). Verified against Microchip DS20001984H Table 3-1 (p11). The KiCad symbol in the schematic was already correct — this doc fix brings the doc in line with both the datasheet and the schematic.

| Pin | Name | Net / connection | Notes |
|-----|------|------------------|-------|
| 1 | VDD | `VBUS` (5V from USB-C) | Charger input. Bypass to VSS with **≥4.7µF** ceramic cap (close to pin). |
| 2 | VDD | `VBUS` (5V from USB-C) | Second VDD pin — **tie to pin 1** on the PCB. (The DFN-8 package has two VDD pins for lower bond-wire inductance and better current handling.) |
| 3 | VBAT | `+BATT` (LiPo) | Charger output — current INTO battery. Bypass to VSS with **≥4.7µF** ceramic cap. Same net as J_BATT pin 1 and everything else on +BATT. |
| 4 | VBAT | `+BATT` (LiPo) | Second VBAT pin — **tie to pin 3** on the PCB. (Same reasoning as the dual VDD pins.) |
| 5 | STAT | LED + 470Ω to VDD (pin 1/2) | **Charge status LED — LOCKED 2026-07-21.** MCP73831 = tri-state: **LOW = charging** (preconditioning / fast charge / constant-voltage modes), **HIGH = charge complete**, **High-Z = shutdown** (no input power, or PROG floating). LED + 470Ω resistor from VDD (VBUS, 5V) to STAT: **LED on = charging** (STAT sinks current to GND), LED off = charge complete (STAT drives HIGH, no voltage across LED) or USB unplugged (VBUS=0). Visual indicator only — no MCU GPIO read. Rationale: (a) simple — one LED + one resistor, no firmware; (b) immediate user feedback ("is my phone charging?"); (c) saves an MCU GPIO for other uses; (d) the MCU can infer charge state indirectly if needed (VBUS presence + battery voltage trend from fuel gauge). If software charge-state monitoring becomes necessary later, the STAT net can be tapped to an MCU GPIO in parallel with the LED (LED stays, MCU reads the same tri-state logic). **STAT behavior corrected 2026-07-22** — previous doc said "high = charging" which is the opposite of the datasheet (DS20001984H p13 operational flowchart: STAT=LOW during all charging modes, STAT=HIGH at charge complete). |
| 6 | VSS | `GND` | Ground. |
| 7 | NC | — | No connect. (This pin exists on the DFN-8 package but has no internal connection — leave floating.) |
| 8 | PROG | R_PROG to GND | Programs charge current: I_REG = 1000V / R_PROG. **For 500mA**: R_PROG = 2kΩ. **For 100mA**: R_PROG = 10kΩ. Leave floating = shutdown (chip disabled). |
| 9 (EP) | VSS | `GND` | Exposed thermal pad — connect to GND. Primary heat dissipation path for the linear charger. |

**External components:**
- C11 = 4.7µF ceramic on VDD (input bypass — close to pins 1/2)
- C10 = 4.7µF ceramic on VBAT/+BATT (output bypass — close to pins 3/4; also counts toward +BATT bulk capacitance)
- R_PROG = 2kΩ (sets 500mA charge current — **LOCKED 2026-07-21**. 500mA = 0.42C on the target 1200mAh LiPo, well within the 0.5C standard LiPo charge rate. USB 2.0 standard port provides 500mA — exact match. ~2.5-3 hour charge time. If a larger battery is used later (2000mAh+), 500mA becomes even more conservative. If a smaller battery is used (<500mAh), R_PROG must be increased to keep charge rate ≤1C.)
- D_CHG = LED1 + 470Ω resistor (R3) from VDD (VBUS) to STAT — charge status indicator (LED on = charging, STAT=LOW)

**Note on charge current:** USB 2.0 standard port = 500mA. The MCP73831-2ACI can do up to 500mA. If we ever want fast charging from a 2A USB charger, we'd need a different charger IC (BQ25895 etc.) — but for prototype, 500mA is fine.

**Note on package correction (2026-07-21):** The block diagram previously said "SOT-23-5" with a 5-pin pinout. The actual downloaded KiCad footprint is `TDFN-8_L3.0-W2.0-P0.50-BL-EP1.6` (9 pads = 8 signal + 1 exposed pad), confirming the DFN-8 variant. The DFN-8 pinout differs from SOT-23-5: pin 4 is VBAT (not PROG), pin 6 is VSS (not STAT), and pins 7/8/9 are NC / PROG / exposed pad. Corrected after downloading `docs/reference/mcp73831.pdf` and verifying against datasheet page 1 package diagram and Table 3-1 (p11).

**Note on pinout correction (2026-07-22):** The 2026-07-21 package correction got the DFN-8 pinout wrong again (pins 2/3/4/6/7/8 were incorrect — written from the package diagram without reading Table 3-1). The correct pinout from DS20001984H Table 3-1: 1=VDD, 2=VDD, 3=VBAT, 4=VBAT, 5=STAT, 6=VSS, 7=NC, 8=PROG, 9(EP)=VSS. The KiCad symbol in the schematic was already correct — this doc fix brings the doc in line with both the datasheet and the schematic. The STAT behavior was also corrected: STAT=LOW during charging (not HIGH as previously documented).

#### U4 — TPS63021DSJR (3.3V buck-boost, VSON-14 with exposed pad)

> Datasheet: TI SLVS916I (in `docs/reference/tps63021.pdf`). "DSJ" = VSON-14 3×4mm with exposed thermal pad. LCSC C202140. Fixed 3.3V output (no feedback divider needed).

**Pinout (VSON-14, top view — pin 1 marked with dot):**
```
       1  VINA          14  PG
       2  GND           13  PS/SYNC
       3  FB            12  EN
       4  VOUT          11  VIN
       5  VOUT          10  VIN
       6  L2             9  L1
       7  L2             8  L1
       (Exposed pad = PGND, connect to GND plane)
```

| Pin | Name | Net / connection | Notes |
|-----|------|------------------|-------|
| 1 | VINA | (bypass cap only — see notes) | **Internally supplied from VIN** — do NOT wire to VBAT externally. TI removed the external VINA-to-VIN connection in datasheet Rev G (the internal connection is cleaner — an external wire picked up switching noise). **Only connection: 0.1µF ceramic cap to GND, close to pin 1.** This is the sole purpose of the external VINA pin — bypass for the internally-derived control supply. |
| 2 | GND | `GND` | Control/logic ground. |
| 3 | FB | `+3.3V` (VOUT) | **Fixed-output version: tie directly to VOUT.** No feedback divider. (On adjustable TPS63020, this would be the divider tap.) |
| 4, 5 | VOUT | `+3.3V` | Buck-boost output. Tie together (both pins on same net). |
| 6, 7 | L2 | L1 inductor (other end) | Inductor connection 2. Tie pin 6 and 7 together. |
| 8, 9 | L1 | L1 inductor (one end) | Inductor connection 1. Tie pin 8 and 9 together. |
| 10, 11 | VIN | `+BATT` | Power-stage supply input. Tie pin 10 and 11 together. |
| 12 | EN | `+BATT` via 1MΩ pullup | Enable (active high). **Must not float.** Pull up to VIN (+BATT) with 1MΩ for always-on. **Do NOT pull up to VOUT** — chicken-and-egg: at startup VOUT=0 so EN=0 and the chip never starts. +BATT is present immediately when battery connects, so pulling EN to +BATT guarantees startup. The TPS63021 quiescent current in power-save (~25µA) is negligible vs modem idle (17.5mA) — no reason to disable the rail. |
| 13 | PS/SYNC | `GND` (tie directly) | Power-save mode enable. **Low = power-save ON** (high efficiency at light load <100mA, auto-switches to PWM above 100mA). **High = PWM always** (lower ripple, worse light-load efficiency). Tie to GND to enable power-save — the chip automatically transitions to PWM when load exceeds 100mA. No need to toggle: standby load (~20-50mA) benefits from power-save; active load (>100mA) auto-switches to PWM. |
| 14 | PG | MCU GPIO (EXTI-capable) + 10kΩ pullup to +3.3V | **Power-good output — LOCKED 2026-07-21 (wire to MCU).** Open-drain, low = VOUT < ~90% of target (~2.97V). Pull up to **+3.3V** (NOT +BATT) with 10kΩ, wire to MCU GPIO (EXTI-capable, TBD pin assignment). **Why wire it (not "MCU is off when PG is low"):** the STM32H743 BOR (brown-out reset) triggers around ~1.7V, but PG goes low at ~2.97V — there's a ~1.2V window where PG is low but the MCU is still alive and can take defensive action (reduce clock, kill display backlight, pause modem TX, trigger graceful shutdown). Without PG, the MCU has no warning before the rail collapses. Net name: `3V3_OK`. **Pull-up rail corrected 2026-07-22** — the power schematic originally had R4 pulled up to +BATT (3.4–4.3V), which would overvoltage a non-5V-tolerant MCU GPIO. Fixed to +3.3V. |
| Exposed pad | PGND | `GND` | Thermal pad — connect to large GND copper pour for heat dissipation. Internally tied to PGND. |

**External components:**
- L1 = 1.5µH, Coilcraft XFL4020-152MEC (LOCKED — between pins 6/7 and 8/9)
- C_VIN = 2× 10µF ceramic (input, +BATT to GND, close to pins 10/11)
- C_VOUT = 3× 22µF ceramic (output, +3.3V to GND, close to pins 4/5)
- C_VINA = 0.1µF ceramic (VINA bypass to GND, close to pin 1 — **VINA's only connection**)
- R_EN = 1MΩ pullup to +BATT (always-on — chip runs whenever battery connected)
- PS/SYNC = direct wire to GND (enable power-save, no resistor needed)
- R_PG = 10kΩ pullup to +3.3V (NOT +BATT — PG is an MCU input, must not exceed 3.3V)

**Critical layout notes:**
- Input caps (C_VIN) must be as close to pins 10/11 as possible — this is a 2.5MHz switching regulator, trace inductance matters.
- Output caps (C_VOUT) must be close to pins 4/5.
- L1 traces short and wide (carries 2-3A).
- Exposed pad = primary heat path — vias to GND plane below.

#### U5 — TPS7A0218PDBVR (1.8V LDO, SOT-23-5)

> Datasheet: TI SBVS277C. "DBV" = SOT-23-5. "18" = 1.8V fixed output. LCSC C3748843. Input from +3.3V, output = +1V8.

**Pinout (SOT-23-5, top view):**
```
       ┌─────┐
   1 ──┤ IN  ├── 4  NC
   2 ──┤ GND ├── 5  OUT
   3 ──┤ EN  ├──
       └─────┘
```

| Pin | Name | Net / connection | Notes |
|-----|------|------------------|-------|
| 1 | IN | `+3.3V` | LDO input. Bypass with **1µF** ceramic to GND (close to pin). |
| 2 | GND | `GND` | Ground. |
| 3 | EN | `+3.3V` (tie to IN, pin 1) | Enable (active high, internal pulldown). **Tie to IN — LOCKED 2026-07-21.** +1V8 comes up whenever +3.3V is up. No MCU GPIO control. Rationale: (a) the ALC5651 datasheet §7.1 says "to prevent all power down leakage, needs keep all power supply on" — cutting 1.8V while 3.3V rails stay up *causes* leakage, doesn't save power; (b) the ALC5651 has per-block power management via I2C registers (§7.16, MX-61h through MX-66h) — standby power is handled in software, not by cutting rails; (c) the recommended power-on sequence (1.8V before 3.3V) is architecturally impossible with our 1.8V-from-3.3V topology anyway, and the codec's POR handles the ramp; (d) simpler schematic, one less net, one less GPIO, one less firmware task. |
| 4 | NC | `GND` or float | No internal connection. Tie to GND or leave floating. |
| 5 | OUT | `+1V8` | LDO output. **1µF ceramic** to GND (close to pin, required for stability). |

**External components:**
- C_IN = 1µF ceramic on IN (input)
- C_OUT = 1µF ceramic on OUT (output — required for stability, datasheet §9.2)
- (Optional) EN wire to MCU GPIO instead of IN, if we want MCU to control +1V8 sequencing

**Notes:**
- 200mA max output. Our load is ~10–20mA (codec analog + level shifter VCCA) — huge margin.
- Low-dropout (~150mV at 200mA) — but we don't need dropout performance since +3.3V is always >1.95V (1.8V + 150mV).
- Internal pulldown on EN means the chip is OFF if EN floats. Tying EN to IN guarantees it's on.

#### U7 — MAX17048G+T10 (fuel gauge, TDFN-8 2×2mm)

> Datasheet: `docs/reference/max17048.pdf` (ADI/Maxim MAX17048-MAX17049 Rev 7, 19pp). "G+T10" = TDFN-8 2×2mm package. LCSC C2682616. ModelGauge — no current-sense resistor needed, measures battery voltage on VDD + coulomb counting algorithmically. **Pinout corrected 2026-07-21** — previous version had 6 of 8 pins wrong (cited "Rev 7 datasheet" without actually downloading it; see project-log.md 2026-07-21 MAX17048 Pinout Correction).

**Pinout (TDFN-8, top view — pin 1 marked with dot, exposed pad on bottom):**
```
       1  CTG           8  SDA
       2  CELL          7  SCL
       3  VDD           6  QSTRT
       4  GND           5  ALRT
       (Exposed pad = GND)
```

| Pin | Name | Net / connection | Notes |
|-----|------|------------------|-------|
| 1 | CTG | `GND` | "Connect to Ground" per datasheet §Pin/Bump Descriptions. (Custom-configuration trigger on some Maxim fuel-gauge variants — on MAX17048 simply tie to GND.) |
| 2 | CELL | `+BATT` (or float) | **Not internally connected on MAX17048** — only the MAX17049 (2-cell) uses this as upper-cell voltage sense. Datasheet says "Connect to the Positive Battery Terminal" for package compatibility. Either tie to +BATT or leave floating — no current flows either way. |
| 3 | VDD | `+BATT` | **Power-supply input AND voltage sense input on MAX17048.** Connect to +BATT (raw LiPo 3.4–4.3V — within the 2.5–4.5V VDD range). Bypass with **0.1µF** ceramic to GND. The fuel gauge measures battery voltage on this pin (the "CELL" pin is NC on the 1-cell part). |
| 4 | GND | `GND` | Chip ground. Connect to negative battery terminal / system GND. |
| 5 | ALRT | MCU GPIO (EXTI-capable) + 10kΩ pullup to +3.3V | **Alert output — LOCKED 2026-07-21 (wire to MCU).** Open-drain, **active-low**. Fires on low-SOC threshold, 1% SOC change, battery under/overvoltage, VRESET alert. Pull up to +3.3V with 10kΩ, wire to MCU GPIO (EXTI-capable, TBD pin assignment). Net name: `FUEL_ALERT`. Rationale: (a) low-SOC alert triggers "battery low" UI warning before the phone dies; (b) battery undervoltage alert triggers graceful shutdown before LiPo damage — safety event, not just UI; (c) battery overvoltage alert catches charger runaway — defense-in-depth; (d) interrupt-driven vs polling saves power (MCU stays asleep until alert fires); (e) trivial cost — 1 GPIO + 1 resistor, and the STM32H743 has 41 spare GPIO. Alert is enabled by default — can fire immediately on power-up. If firmware decides to poll instead, the pin just sits as a spare input — no downside. |
| 6 | QSTRT | `GND` | Quick-start input. Allows hardware reset of the fuel gauge (rising edge triggers quick-start). **Connect to GND if not used** — most systems should not use quick-start (datasheet §Quick-Start: "Most systems should not use quick-start because the ICs handle most startup problems transparently"). Quick-start is also available via I2C (MODE register bit) — no need to wire QSTRT to MCU. |
| 7 | SCL | I2C clock (MCU I2C bus) | Open-drain, needs **4.7kΩ pullup to +3.3V**. **One pullup per I2C line, shared across all devices on the bus** — do NOT put a pullup at every device (3 devices × 4.7kΩ in parallel = 1.57kΩ = too strong, exceeds I2C 3mA sink spec). Internal pulldown (~0.4µA) for sensing disconnection. Logic thresholds 1.4V VIH / 0.5V VIL — independent of VDD, so +3.3V pullups work even though VDD is on +BATT. **Pullups deferred to MCU schematic section** — the power schematic has SCL/SDA as labeled nets with only the MAX17048 connected; the MCU section will add the pullup resistors when the MCU I2C peripheral is wired. |
| 8 | SDA | I2C data (MCU I2C bus) | Open-drain, needs **4.7kΩ pullup to +3.3V** (one pullup for the whole SDA line, shared with all other I2C devices — see SCL note). Internal pulldown for disconnection sensing. Same thresholds as SCL. **Pullups deferred to MCU schematic section** — see SCL note. |
| Exposed pad | GND | `GND` | Thermal/electrical pad — connect to GND. |

**External components:**
- C_VDD = 0.1µF ceramic on VDD (close to pin 3)
- R_SDA = 4.7kΩ pullup to +3.3V — **one resistor for the whole SDA line**, shared by all I2C devices (MCU, MAX17048, ALC5651). Do NOT add a pullup at each device. **Deferred to MCU schematic section.**
- R_SCL = 4.7kΩ pullup to +3.3V — **one resistor for the whole SCL line**, shared by all I2C devices. Same reasoning as R_SDA. **Deferred to MCU schematic section.**
- (Optional) R_ALRT = 10kΩ pullup to +3.3V (if using ALRT interrupt — ALRT is not on the I2C bus, it's a separate alert line, so it gets its own pullup)

**I2C address:** MAX17048 default = **0x36** (7-bit). ALC5651 = **0x1A** (7-bit, from `docs/reference/alc5651.pdf` §7.14.1 Table 14 — address byte `0011010 R/W`, 8-bit write = 0x34). **No conflict** — 0x36 ≠ 0x1A, both can share the same I2C bus. **RESOLVED 2026-07-21.**

**Notes:**
- The MAX17048 has no current-sense resistor — it infers state-of-charge from voltage curve + coulomb counting model. Less accurate than a sense-resistor fuel gauge but much simpler (no high-current shunt in the VBAT path).
- **VDD is on +BATT, not +3.3V.** This is the intended use case (datasheet "ONLY ONE EXTERNAL COMPONENT" typical application shows VDD tied directly to battery). Benefit: fuel gauge stays powered when +3.3V is off (MCU in STOP, modem asleep, system "off") — keeps tracking SOC in hibernate mode (3µA). When MCU wakes and +3.3V returns, it reads accumulated state.
- I2C pullups are on +3.3V (not +BATT) — SDA/SCL/ALRT are voltage-agnostic (abs max 5.5V, thresholds 1.4V/0.5V independent of VDD). Pulling up to +3.3V means the I2C bus only goes live when the MCU is awake, which is what we want (no point polling the fuel gauge when the MCU is asleep).
- Hibernate mode: 3µA typical, 5µA max. Active mode: 23µA typical, 40µA max. The IC automatically enters/exits hibernate based on charge/discharge rate.
- Sleep mode (<1µA) triggers if SCL and SDA are both held low for >2.5s — the MCU must poll at least every 2s to keep the fuel gauge awake, or accept sleep mode (no SOC updates while asleep).

---

## Section: MCU ↔ Modem Link

The most signal-dense interface in the design. Every phone function (dial, answer, hang up, SMS, signal, data) goes through this UART. The MCU also controls modem reset (PERST#) and monitors modem events (WAKE#). All signals cross a 1.8V↔3.3V voltage boundary and need level shifting.

> **MPCIe-specific simplification**: The MPCIe variant has no PWRKEY pin (the card likely auto-powers on VCC application — power-on method TBD with Techship) and no DCD pin (not on edge connector). This reduces the control signal count to exactly 8 (6 UART + RST + STATUS), fitting one TXB0108 with zero spare bits and no second shifter. The LGA variant needs 10+ signals (adds PWRKEY + DCD) and would need a second shifter — see the LGA pin mapping table in the Modem section for reference if pivoting.

### Voltage domains
| Side | Voltage | Device |
|------|---------|--------|
| MCU side | 3.3V (`+3.3V`) | STM32H743ZI UART/GPIO pins |
| Modem side | 1.8V (`+1V8`) | SIM7600NA-H-PCIE MPCIe edge connector pins (absolute max 2.1V — 3.3V would damage) |

> **Source**: SIM7600 PCIE HW Design Manual V1.03 §3.8 Table 11 (1.8V DC characteristics: VIH 1.17–2.1V, VOH 1.35–1.8V). Confirmed 2026-07-22.

### Components
| Ref | Part | Package | Notes |
|-----|------|---------|-------|
| U_MCU | STM32H743ZIT6 | LQFP-144 | 3.3V I/O. UART + control GPIOs on MCU side. |
| U_MODEM | SIM7600NA-H-PCIE | MPCIe card (50.8×31mm) in SOFNG PCIE-52P40H socket (C444926) | 1.8V I/O on edge connector pins. |
| U_LVL | TXB0108D | TSSOP-20 | 8-bit bidirectional auto-direction-sensing level shifter. A side = 1.8V (modem), B side = 3.3V (MCU). **VCCA ≤ VCCB required** (1.8 ≤ 3.3 ✓). All 8 bits used — no spare. |

> **Why TXB0108**: 8 bits covers all MPCIe control signals (6 UART + RST + STATUS = 8). Auto-direction sensing works for UART (each signal is unidirectional). Alternative: SN74LVC8T245 (direction-controlled, more robust but needs direction pins). Stick with TXB0108 unless a signal-integrity issue emerges.

### Signal mapping (8 signals → one TXB0108, all bits used)

| Bit | A-side (1.8V) | Global label (modem) | MPCIe pin # | Pin name | B-side (3.3V) | Global label (MCU) | MCU pin | Direction | Notes |
|-----|---------------|----------------------|-------------|----------|---------------|---------------------|---------|-----------|-------|
| 1 | A1 | `MODEM_TXD` | 19 | UART_TXD | B1 | `MCU_UART_RX` | LPUART1_RX | Modem → MCU | Modem transmits AT responses/URCs |
| 2 | A2 | `MODEM_RXD` | 17 | UART_RXD | B2 | `MCU_UART_TX` | LPUART1_TX | MCU → Modem | MCU sends AT commands |
| 3 | A3 | `MODEM_RTS` | 13 | UART_RTS | B3 | `MCU_UART_CTS` | LPUART1_CTS | Modem → MCU | Modem RTS → MCU CTS (hw flow control) |
| 4 | A4 | `MODEM_CTS` | 11 | UART_CTS | B4 | `MCU_UART_RTS` | LPUART1_RTS | MCU → Modem | MCU RTS → Modem CTS (hw flow control) |
| 5 | A5 | `MODEM_RI` | 44 | UART_RI | B5 | `MCU_RI_IRQ` | GPIO (int) | Modem → MCU | Ring indicator — wakes MCU on incoming call |
| 6 | A6 | `MODEM_DTR` | 46 | UART_DTR | B6 | `MCU_DTR` | GPIO (out) | MCU → Modem | Sleep control (`AT+CSCLK=1`) |
| 7 | A7 | `MODEM_RST` | 22 | PERST# | B7 | `MCU_MODEM_RST` | GPIO (out) | MCU → Modem | Active-low hard reset (PCIe PERST# name) |
| 8 | A8 | `MODEM_STATUS` | 1 | WAKE# | B8 | `MCU_MODEM_STATUS` | GPIO (int) | Modem → MCU | WAKE# — stays high, goes low on event (SMS/call/URC). **Interrupt, not a ready indicator** — see note below |

> **WAKE# vs LGA STATUS**: The LGA STATUS pin (pin 49) is "high = powered on + firmware ready" — a level-ready signal. The MPCIe WAKE# (pin 1) is an interrupt — "stays high, goes low on event." Different semantics. The MCU should treat WAKE# as a **falling-edge interrupt** (wake from STOP on falling edge), not a level-ready signal. To detect "modem ready," the MCU sends an AT command and checks for `OK` response (or polls `AT+CPIN?` / `AT+CREG?`).

> **No PWRKEY on MPCIe**: The LGA variant has PWRKEY (pin 3) — active-low pulse to power on/off. The MPCIe edge connector has no PWRKEY equivalent. The card likely auto-powers on when VCC is applied. Power-off would be via AT command (`AT+CPOWD=1`) or cutting +3.3V to the modem (load switch or MCU-controlled regulator). **Open item: confirm power-on/off method with Techship.**

> **No DCD on MPCIe**: The LGA variant exposes DCD (pin 70). The MPCIe edge connector does not. DCD is a legacy UART signal not needed for AT command communication — the prototype (Nucleo + HAT) didn't use it. No impact.

### Power for the level shifter
| Pin | Net | Notes |
|-----|-----|-------|
| VCCA | `+1V8` | 1.8V supply (from TPS7A0218 LDO). Powers the modem-facing side. |
| VCCB | `+3.3V` | 3.3V supply (from TPS63021DSJR). Powers the MCU-facing side. |
| OE | `+3.3V` via pullup | Output enable (active high). Pull high to enable. Tie to VCCB or a GPIO for power sequencing. |
| GND | `GND` | Common ground. |

> **TXB0108 power sequencing**: VCCA must be present before OE goes high, or the outputs can glitch. Simplest: tie OE to VCCB with a pullup + a pulldown cap to GND for a slow RC ramp. Or drive OE from an MCU GPIO that starts LOW and goes HIGH after both rails are stable.

### UART selection on STM32H743

**Prototype used LPUART1** (PB6 TX, PB7 RX) — confirmed working 2026-07-13. For the PCB, two options:

1. **Keep LPUART1** — firmware already works with it. LPUART1 on H743 supports RTS/CTS (hardware flow control). Need to look up which alternate-function pins carry LPUART1_RTS / LPUART1_CTS on LQFP-144. Low-power UART is good for battery life (can wake from STOP mode on RX edge).
2. **Switch to a full USART** (USART1/2/3/6) — more features, higher max baud, but firmware would need updating. Not necessary unless LPUART1 lacks something needed.

**Recommendation**: Keep LPUART1 for firmware compatibility. Verify RTS/CTS pin availability on LQFP-144 before finalizing the pin map.

### Schematic layout (flat, global labels)

```
    ┌─── MCU region ───────────────────┐         ┌─── Level shifter ─────────┐         ┌─── Modem region ──────────────┐
    │                                  │         │  U_LVL: TXB0108D           │         │  U_MODEM: MPCIe socket         │
    │  MCU_UART_RX  ◀──────────────────┼─────────┤ B1 ── A1  (TX  ←)         │◄────────┤  pin 19 UART_TXD  [MODEM_TXD] │
    │  MCU_UART_TX  ───────────────────┼─────────┤ B2 ── A2  (RX  →)         │────────►│  pin 17 UART_RXD  [MODEM_RXD] │
    │  MCU_UART_CTS ◀──────────────────┼─────────┤ B3 ── A3  (RTS ←)         │◄────────┤  pin 13 UART_RTS  [MODEM_RTS] │
    │  MCU_UART_RTS ───────────────────┼─────────┤ B4 ── A4  (CTS  →)        │────────►│  pin 11 UART_CTS  [MODEM_CTS] │
    │  MCU_RI_IRQ    ◀─────────────────┼─────────┤ B5 ── A5  (RI   ←)        │◄────────┤  pin 44 UART_RI   [MODEM_RI]  │
    │  MCU_DTR       ──────────────────┼─────────┤ B6 ── A6  (DTR  →)        │────────►│  pin 46 UART_DTR  [MODEM_DTR] │
    │  MCU_MODEM_RST ──────────────────┼─────────┤ B7 ── A7  (RST  →)        │────────►│  pin 22 PERST#    [MODEM_RST] │
    │  MCU_MODEM_STATUS ◀──────────────┼─────────┤ B8 ── A8  (WAKE ←)        │◄────────┤  pin 1  WAKE#     [MODEM_STATUS]│
    │                                  │         │  VCCA=+1V8  VCCB=+3.3V      │         │  VCC = +3.3V (not +BATT!)     │
    └──────────────────────────────────┘         │  OE=+3.3V (pullup)          │         │  GND = GND                    │
                                                  └────────────────────────────┘         └────────────────────────────────┘
```

In practice: use **global labels** on both sides of the level shifter. MCU pins get `MCU_*` labels, level shifter B-side gets the same `MCU_*` labels, A-side gets `MODEM_*` labels, modem MPCIe pins get the same `MODEM_*` labels. KiCad connects same-named global labels across the sheet automatically — no long wires needed. The level shifter is the boundary between the `MCU_*` and `MODEM_*` net namespaces.

### Pre-draw checklist
- [ ] Place MPCIe socket symbol (`connectors:PCIE-52P40H_C444926`) in modem region
- [ ] Place TXB0108D (`ics:TXB0108PWR`) between MCU and modem regions
- [ ] Place STM32H743 symbol in MCU region (just the UART + control GPIO pins for now — full pin map comes later)
- [ ] Wire 8 signals through the level shifter with global labels on both sides (`MODEM_*` on A-side, `MCU_*` on B-side)
- [ ] Add power symbols: `+1V8` on VCCA, `+3.3V` on VCCB, `GND` on GND
- [ ] Add OE pullup to `+3.3V`
- [ ] Wire MPCIe VCC pins (2, 24, 39, 41, 52) to `+3.3V` power symbol (NOT `+BATT` — MPCIe is 3.3V only)
- [ ] Wire MPCIe GND pins (4, 9, 15, 18, 21, 26, 27, 29, 34, 35, 37, 40, 43, 50) to `GND`
- [ ] Run ERC

### Open questions for this section
- [ ] **LPUART1 RTS/CTS pins on LQFP-144**: need to look up the alternate-function table in RM0433 to confirm which pins carry LPUART1_RTS and LPUART1_CTS. (Can do via the PDF MCP server against the local reference manual.)
- [ ] **MPCIe power-on/off method**: No PWRKEY pin on edge connector. Confirm with Techship whether the card auto-powers on VCC application, and how to power it off (`AT+CPOWD=1`? VCC removal via load switch?).
- [ ] **WAKE# vs RI usage**: Both WAKE# and RI can wake the MCU on events. WAKE# is general-purpose (any URC), RI is call-specific. Decide in firmware whether to use both or just one. Hardware wires both regardless — firmware choice.

---

## Section: Power — *to be specified*

## Section: MCU (full pin map) — *to be specified*

## Section: Modem (full pinout + SIM + antenna + USB)

> **Status**: Pin mappings verified 2026-07-22 from vendor PDFs via MCP extraction. **MPCIe is the primary form factor** being schemed (flat sheet + global labels). LGA pin mapping retained as a **fallback reference** — pivot only if MPCIe proves difficult during layout. Same global label set on both variants.
>
> **Sources**: LGA pinout from `docs/reference/SIM7600 Series Hardware Design_V1.03.pdf` §2.1-2.2 (pp 13-17). MPCIe pinout from `docs/reference/SIM7600_Series_PCIE_Hardware_Design_V1.03.pdf` §2.2 (pp 13-15). KiCad symbol pin numbers verified against `lib/ics.kicad_sym` (SIM7600NA-H, 135 pins) and `lib/connectors.kicad_sym` (PCIE-52P40H_C444926, 54 pins).

### Global labels (MPCIe primary, LGA fallback)

Most labels are shared between variants, but **3 labels are LGA-only** (`MODEM_PWRKEY`, `GNSS_ANT`, `MAIN_ANT` — not placed in MPCIe wiring) and the **power label differs** (`+3.3V` for MPCIe, `+BATT` for LGA). The SIM socket and its passives (100nF cap, ESD diode) live on the **flat sheet** — both variants expose USIM_* labels and the flat sheet wires them to a single SIM socket:

| Global label | Shape | Signal | Notes |
|--------------------|-------|--------|-------|
| `MODEM_TXD` | output | Modem UART TX → MCU | 1.8V, needs level shifter |
| `MODEM_RXD` | input | Modem UART RX ← MCU | 1.8V, needs level shifter |
| `MODEM_CTS` | input | Modem UART CTS ← MCU | 1.8V, needs level shifter |
| `MODEM_RTS` | output | Modem UART RTS → MCU | 1.8V, needs level shifter |
| `MODEM_RI` | output | Ring indicator → MCU (wake on call) | 1.8V, needs level shifter |
| `MODEM_DTR` | input | DTE ready ← MCU (sleep control) | 1.8V, needs level shifter |
| `PCM_CLK` | output | PCM bit clock → ALC5651 I2S-1 | 1.8V, direct to codec (no shifter) |
| `PCM_OUT` | output | PCM data out → ALC5651 I2S-1 | 1.8V, direct to codec |
| `PCM_IN` | input | PCM data in ← ALC5651 I2S-1 (mic) | 1.8V, direct from codec |
| `PCM_SYNC` | output | PCM frame sync → ALC5651 I2S-1 | 1.8V, direct to codec |
| `MODEM_USB_DP` | bidirectional | Modem USB 2.0 HS D+ | To optional modem USB connector. **Renamed from `USB_DP`** to avoid conflict with MCU USB global label in power schematic |
| `MODEM_USB_DN` | bidirectional | Modem USB 2.0 HS D- | To optional modem USB connector. **Renamed from `USB_DN`** to avoid conflict with MCU USB global label in power schematic |
| `MODEM_RST` | input | Reset ← MCU | 1.8V, needs level shifter |
| `MODEM_STATUS` | output | Module ready → MCU | 1.8V, needs level shifter |
| `MODEM_PWRKEY` | input | Power key ← MCU | **LGA only** — MPCIe has no PWRKEY pin. Do not place this label in MPCIe wiring |
| `NET_STATUS` | output | Network LED | Drives status LED via transistor |
| `GNSS_ANT` | passive | GNSS antenna U.FL | **LGA only** — MPCIe has onboard U.FL. Do not place this label in MPCIe wiring |
| `MAIN_ANT` | passive | Cellular antenna U.FL | **LGA only** — MPCIe has onboard U.FL. Do not place this label in MPCIe wiring |
| `+BATT` / `+3.3V` | power | Modem supply | **NOT shared** — LGA uses `+BATT` (3.4–4.3V LiPo direct), MPCIe uses `+3.3V` (3.0–3.6V regulated). See power supply note below |
| `GND` | power | Ground | Power symbol, global net |
| `USIM_VDD` | output | SIM card power (1.8V or 3.0V, modem-controlled) | → flat sheet SIM socket VCC. 100nF cap at socket |
| `USIM_DATA` | bidirectional | SIM card data | → flat sheet SIM socket DATA. Internal 10kΩ pullup to USIM_VDD in modem |
| `USIM_CLK` | output | SIM card clock | → flat sheet SIM socket CLK. Rise/fall < 40ns required |
| `USIM_RST` | output | SIM card reset | → flat sheet SIM socket RST |
| `USIM_DET` | bidirectional | SIM card detect (hot-plug) | → flat sheet SIM socket DET. Internal pullup to 1.8V in modem. Optional — leave NC if 6-pin socket |

### Pin mapping — LGA variant — *fallback reference*

**Symbol**: `ics:SIM7600NA-H` (135 pins, LCC+LGA 30×30mm). Pin numbers from SIM7600 HW Design V1.03 §2.2, verified against KiCad symbol.

| Global label | Modem pin name | Pin # | I/O | Notes |
|--------------------|---------------|-------|-----|-------|
| `MODEM_TXD` | TXD | 71 | DO | Modem transmits to MCU |
| `MODEM_RXD` | RXD | 68 | DI | Modem receives from MCU |
| `MODEM_RTS` | RTS | 66 | DOL | Modem RTS → MCU CTS |
| `MODEM_CTS` | CTS | 67 | DI | Modem CTS ← MCU RTS |
| `MODEM_RI` | RI | 69 | DOH | Ring indicator (wakes MCU) |
| `MODEM_DTR` | DTR | 72 | DI | Sleep control (`AT+CSCLK=1`) |
| `PCM_CLK` | PCM_CLK | 76 | DO | → ALC5651 I2S-1 BCLK |
| `PCM_OUT` | PCM_OUT | 73 | DO | → ALC5651 I2S-1 DACDAT (rx from modem) |
| `PCM_IN` | PCM_IN | 74 | DI | ← ALC5651 I2S-1 ADCDAT (mic to modem) |
| `PCM_SYNC` | PCM_SYNC | 75 | DO | → ALC5651 I2S-1 LRCK |
| `MODEM_USB_DP` | USB_DP | 13 | I/O | USB 2.0 HS D+ (renamed to avoid MCU USB conflict) |
| `MODEM_USB_DN` | USB_DN | 12 | I/O | USB 2.0 HS D- (renamed to avoid MCU USB conflict) |
| `MODEM_RST` | RESET | 4 | DI | Active low. Internal 40kΩ pullup to 1.8V |
| `MODEM_STATUS` | STATUS | 49 | DO | High = powered on + firmware ready |
| `MODEM_PWRKEY` | PWRKEY | 3 | DI | Active low pulse (~1s) to power on/off |
| `NET_STATUS` | NETLIGHT | 51 | DO | LED control output (network status) |
| `GNSS_ANT` | GNSS_ANT | 79 | AI | GNSS antenna soldering pad → U.FL |
| `MAIN_ANT` | MAIN_ANT | 82 | AIO | Main antenna soldering pad → U.FL |
| `+BATT` | VBAT | 38, 39, 62, 63 | PI | 4 pins — 3.4–4.3V, 2A bursts. Add 100–470µF bulk caps here |
| `GND` | GND | 1,2,5,10,14,37,40,41,43,57,58,60,61,64,65,77,78,80,81 | — | 19 GND pins + exposed pad |
| `USIM_VDD` | USIM_VDD | 20 | PO | → flat sheet SIM socket VCC |
| `USIM_DATA` | USIM_DATA | 17 | BIDI | → flat sheet SIM socket DATA (internal 10kΩ pullup to USIM_VDD) |
| `USIM_RST` | USIM_RST | 18 | DO | → flat sheet SIM socket RST |
| `USIM_CLK` | USIM_CLK | 19 | DO | → flat sheet SIM socket CLK |
| `USIM_DET` | USIM_DET | 53 | BIDI | → flat sheet SIM socket DET (optional hot-plug detect) |

**LGA-only pins (not in global labels — wire locally):**

| Pin name | Pin # | Notes |
|----------|-------|-------|
| VDD_1V8 | 15 | 1.8V LDO output (50mA max). **Tentative: leave open** — using our own TPS7A0218 (see block-diagram.md §+1V8 open question) |
| VDD_AUX | 44 | 2.85V LDO output (150mA). Leave open if unused |
| USB_VBUS | 11 | USB detection input (3.0–5.25V). Connect to VBAT or leave open (modem USB is optional) |
| USB_ID | 16 | USB ID input. Leave open |
| AUX_ANT | 59 | Auxiliary antenna pad. Leave open (diversity RX optional) |
| FLIGHTMODE | 54 | Flight mode control. Leave open (normal mode = high/open) |
| SCL | 55 | I2C clock. Leave open or pull up to 1.8V via 2.2kΩ |
| SDA | 56 | I2C data. Leave open or pull up to 1.8V via 2.2kΩ |
| DBG_TXD | 42 | Debug UART TX. Leave open or add test point |
| RXDDBG | 106 | Debug UART RX. Leave open or add test point |
| SD_CMD/DATA0-3/CLK | 21-26 | SD card interface. **Not supported on NA-H** — leave open |
| SDIO_* | 27-32 | SDIO interface. Leave open (not used) |
| SPI_* | 6-9 | SPI LCD interface. Leave open (not used) |
| GPIO3/6/41/43/77 | 33,34,52,50,87 | General GPIO. Leave open |
| ISINK | 45 | Current sink. Leave open |
| ADC1/ADC2 | 47,46 | ADC inputs. Leave open |
| SD_DET | 48 | SD detect. Leave open |
| COEX1/2/3 | 83,84,86 | RF coexistence (Wi-Fi/LTE). Leave open. **Do NOT pull up during power-up** |
| BOOT_CFG0 (USB_BOOT) | 85 | Boot config. Leave open (normal boot). **Do NOT pull up during power-up** |
| HSIC_STROBE/DATA | 35,36 | HSIC interface. Leave open |
| SGMII_* | 108-117 | SGMII interface. Leave open |
| RESERVED | 88-92,99-105,107,111 | No connection |

### Pin mapping — MPCIe variant — *primary*

**Symbol**: `connectors:PCIE-52P40H_C444926` (54 pins = 52 edge + 2 mounting). Pin numbers from SIM7600 PCIE HW Design V1.03 §2.2 (pp 13-15). The socket symbol pins are numbered 1-52 (signal) + 53-54 (mounting pads).

| Global label | MPCIe edge pin name | Pin # | I/O | Notes |
|--------------------|---------------------|-------|-----|-------|
| `MODEM_TXD` | UART_TXD | 19 | DO | Modem transmits to MCU |
| `MODEM_RXD` | UART_RXD | 17 | DI | Modem receives from MCU |
| `MODEM_RTS` | UART_RTS | 13 | DO | Modem RTS → MCU CTS |
| `MODEM_CTS` | UART_CTS | 11 | DI | Modem CTS ← MCU RTS |
| `MODEM_RI` | UART_RI | 44 | DO | Ring indicator (wakes MCU) |
| `MODEM_DTR` | UART_DTR | 46 | DI | Sleep control |
| `PCM_CLK` | PCM_CLK | 45 | DO | → ALC5651 I2S-1 BCLK |
| `PCM_OUT` | PCM_OUT | 47 | DO | → ALC5651 I2S-1 DACDAT |
| `PCM_IN` | PCM_IN | 49 | DI | ← ALC5651 I2S-1 ADCDAT (mic) |
| `PCM_SYNC` | PCM_SYNC | 51 | DO | → ALC5651 I2S-1 LRCK |
| `MODEM_USB_DP` | USB_DP | 38 | I/O | USB 2.0 HS D+ (renamed to avoid MCU USB conflict) |
| `MODEM_USB_DN` | USB_DN | 36 | I/O | USB 2.0 HS D- (renamed to avoid MCU USB conflict) |
| `MODEM_RST` | PERST# | 22 | DI | Active low reset (PCIe standard name) |
| `MODEM_STATUS` | WAKE# | 1 | I/O | Wake host interrupt (stays high, goes low on event). **Different semantics from LGA STATUS** — see note below |
| ~~`MODEM_PWRKEY`~~ | — | — | — | **Not used in MPCIe** — no PWRKEY pin on edge connector. Do not place this label. Power-on method TBD (confirm with Techship) |
| `NET_STATUS` | LED_WWAN# | 42 | DO | Network status LED (active low — drives LED cathode) |
| ~~`GNSS_ANT`~~ | — | — | — | **Not used in MPCIe** — onboard U.FL on card. Do not place this label |
| ~~`MAIN_ANT`~~ | — | — | — | **Not used in MPCIe** — onboard U.FL on card. Do not place this label |
| `+3.3V` | VCC | 2, 24, 39, 41, 52 | PI | 5 VCC pins — 3.0–3.6V (3.3V typical). **Use `+3.3V` net, NOT `+BATT`** — raw LiPo would damage the card. See power supply note below |
| `GND` | GND | 4,9,15,18,21,26,27,29,34,35,37,40,43,50 | — | 14 GND pins |
| `USIM_VDD` | USIM_VDD | 8 | PO | → flat sheet SIM socket VCC |
| `USIM_DATA` | USIM_DATA | 10 | BIDI | → flat sheet SIM socket DATA |
| `USIM_CLK` | USIM_CLK | 12 | DO | → flat sheet SIM socket CLK |
| `USIM_RST` | USIM_RST | 14 | DO | → flat sheet SIM socket RST |
| `USIM_DET` | USIM_DET | 16 | BIDI | → flat sheet SIM socket DET (optional hot-plug detect) |

**MPCIe-only pins (not in global labels — wire locally or leave open):**

| Edge pin name | Pin # | Notes |
|---------------|-------|-------|
| W_DISABLE# | 20 | RF disable control. Leave open (normal mode) |
| SCL | 30 | I2C clock (1.8V, pulled up in-module via 2.2kΩ). Leave open |
| SDA | 32 | I2C data (1.8V, pulled up in-module). Leave open |
| MICN | 3 | NC on PCIE variant (analog mic- on PCIEA only). Leave open |
| EARP | 5 | NC on PCIE variant (earpiece+ on PCIEA only). Leave open |
| EARN | 7 | NC on PCIE variant (earpiece- on PCIEA only). Leave open |
| NC | 6, 23, 25, 28, 31, 33, 48 | No connection. Leave open |

> **SIM socket (corrected 2026-07-22)**: The PCIE manual §3.7 says "SIM7600 series PCIE modules provide SIM socket on board product, so the external socket can be saved, for the detail please contact local sales." However, the Techship spec sheet lists the embedded SIM socket as `o` (optional) for all H-PCIE variants including NA-H-PCIE. The manual's own footnote says "contact local sales for details" — meaning it's not standard. The stock card does **not** have an onboard SIM socket. **Both variants need a SIM socket on our PCB.** The SIM socket and its passives (100nF cap on USIM_VDD, ESD protection) live at the **flat sheet level** — both variants expose `USIM_VDD`/`USIM_DATA`/`USIM_CLK`/`USIM_RST`/`USIM_DET` as global labels, and the flat sheet wires them to a single SIM socket. This avoids duplicating the SIM socket in both variants and means the socket survives a variant swap.

**Mounting pads (not signal):**

| Pad | Pin # | Notes |
|-----|-------|-------|
| Mounting | 53 | SMD pad (left side, 2.3×3.2mm) |
| Mounting | 54 | SMD pad (right side, 2.3×3.2mm) |

### Key differences between the two variants

| Factor | LGA (bare module) | MPCIe (socketed card) |
|--------|-------------------|----------------------|
| **Power supply** | VBAT = 3.4–4.3V (direct LiPo, `+BATT` net) | VCC = 3.0–3.6V (3.3V typical). **Cannot use raw LiPo** — needs regulated 3.3V. Use `+3.3V` net, not `+BATT` |
| **PWRKEY** | Pin 3 — active low pulse to power on/off | **No PWRKEY pin.** Power-on method TBD (likely auto-on at VCC application, or onboard button). Confirm with Techship |
| **STATUS** | Pin 49 — high = ready, low = off | WAKE# (pin 1) — high = idle, low = interrupt (SMS/call/URC). **Different semantics** — WAKE# is an interrupt, not a ready indicator |
| **RESET** | Pin 4 — RESET (active low) | PERST# (pin 22) — PCIe reset name, same active-low function |
| **Network LED** | NETLIGHT (pin 51) — active high (sources current) | LED_WWAN# (pin 42) — active low (sinks current). **LED circuit differs** — LED anode to +3.3V, cathode to pin 42 via resistor |
| **Antennas** | Soldering pads on module → PCB U.FL connectors | Onboard U.FL connectors on the MPCIe card itself. **No PCB antenna connectors needed** |
| **SIM socket** | USIM pins 17/18/19/20/53 → global labels → flat sheet SIM socket | USIM edge pins 8/10/12/14/16 → global labels → flat sheet SIM socket. **Same SIM socket** — flat sheet component, not duplicated |
| **I2C** | SCL=55, SDA=56 (external pullup needed) | SCL=30, SDA=32 (pulled up in-module via 2.2kΩ). No external pullup needed |
| **Debug UART** | DBG_TXD=42, RXDDBG=106 (add test points) | Not exposed on edge connector. **No debug UART access** |
| **GPIOs** | GPIO1/2/3/4/6/19/41/43/54/77 (10 GPIO pins) | Not exposed on edge connector. **No GPIO access** |
| **VDD_1V8 output** | Pin 15 (1.8V, 50mA) — could power codec | Not exposed on edge connector. Use our own TPS7A0218 LDO |
| **VDD_AUX output** | Pin 44 (2.85V, 150mA) — auxiliary LDO | Not exposed on edge connector |
| **ADC inputs** | ADC1=47, ADC2=46 | Not exposed on edge connector |
| **Footprint** | 30×30mm LGA (119 pads, 1.0mm pitch) | 50.8×31mm card + ~30×9mm socket keepout (52 pads, 0.8mm pitch) |
| **Assembly** | LGA reflow (hardest DIY step, ~70-85% success) | SMD socket reflow (standard SMD, no special reflow) + plug in card after |

### Power supply note (critical difference)

The LGA module's VBAT accepts **3.4–4.3V** (direct LiPo range) — the `+BATT` net works directly.

The MPCIe card's VCC requires **3.0–3.6V (3.3V typical)** — **raw LiPo (up to 4.3V) would damage the card.** The MPCIe variant must power the modem from the **`+3.3V` net** (TPS63021 buck-boost output), not `+BATT`.

**Implementation**: The MPCIe variant uses `+3.3V` (not `+BATT`) for the modem VCC pins. The LGA variant uses `+BATT` (direct LiPo). This is a fundamental difference — the two variants are NOT pin-compatible on the power pin. In the flat sheet, the MPCIe socket's VCC pins connect directly to the `+3.3V` power symbol.

**Current handling**: The TPS63021 is rated for ~3A output. The modem can draw 2A peaks during TX. The MCU + display + codec + SD card draw ~200-400mA. Total peak ~2.4A — within the TPS63021's capability but with less margin than the LGA variant (where the modem draws directly from the battery, bypassing the buck-boost). The MPCIe variant may need additional bulk capacitance on `+3.3V` near the modem socket.

### Schematic layout

```
  MPCIe variant (primary)                        LGA variant (fallback reference)
  ┌────────────────────────────────┐            ┌────────────────────────────────┐
  │  PCIE-52P40H_C444926            │            │  SIM7600NA-H (135 pins)         │
  │  (52 edge pins + 2 mounting)    │            │  (119 signal pads + GND/EP)     │
  │                                 │            │                                 │
  │  pin 19 UART_TXD ── MODEM_TXD   │            │  pin 71 TXD ────── MODEM_TXD    │
  │  pin 17 UART_RXD ── MODEM_RXD   │            │  pin 68 RXD ────── MODEM_RXD    │
  │  pin 13 UART_RTS ── MODEM_RTS   │            │  pin 66 RTS ────── MODEM_RTS    │
  │  pin 11 UART_CTS ── MODEM_CTS   │            │  pin 67 CTS ────── MODEM_CTS    │
  │  pin 44 UART_RI  ── MODEM_RI    │            │  pin 69 RI ──────── MODEM_RI    │
  │  pin 46 UART_DTR ── MODEM_DTR   │            │  pin 72 DTR ─────── MODEM_DTR   │
  │  pin 45 PCM_CLK  ── PCM_CLK     │            │  pin 76 PCM_CLK ─── PCM_CLK     │
  │  pin 47 PCM_OUT  ── PCM_OUT     │            │  pin 73 PCM_OUT ─── PCM_OUT     │
  │  pin 49 PCM_IN   ── PCM_IN      │            │  pin 74 PCM_IN ──── PCM_IN      │
  │  pin 51 PCM_SYNC ── PCM_SYNC    │            │  pin 75 PCM_SYNC ── PCM_SYNC    │
  │  pin 38 USB_DP   ── MODEM_USB_DP│            │  pin 13 USB_DP ─── MODEM_USB_DP │
  │  pin 36 USB_DN   ── MODEM_USB_DN│            │  pin 12 USB_DN ─── MODEM_USB_DN │
  │  pin 22 PERST#   ── MODEM_RST   │            │  pin 4 RESET ────── MODEM_RST   │
  │  pin 1  WAKE#    ── MODEM_STATUS│            │  pin 49 STATUS ──── MODEM_STATUS│
  │  (no PWRKEY)     ── (not placed)│            │  pin 3 PWRKEY ───── MODEM_PWRKEY│
  │  pin 42 LED_WWAN#── NET_STATUS  │            │  pin 51 NETLIGHT ── NET_STATUS  │
  │  (onboard U.FL)  ── (not placed)│            │  pin 79 GNSS_ANT ── GNSS_ANT    │
  │  (onboard U.FL)  ── (not placed)│            │  pin 82 MAIN_ANT ── MAIN_ANT    │
  │  pin 2,24,39,    ── +3.3V (NOT  │            │  pin 38,39,62,63 ── +BATT       │
  │    41,52 VCC        +BATT!)     │            │    VBAT            (direct LiPo)│
  │  pin 4,9,15,...  ── GND         │            │  pin 1,2,5,... ──── GND         │
  │                                 │            │                                 │
  │  USIM pins → USIM_* labels      │            │  USIM pins → USIM_* labels      │
  │    (SIM socket at flat sheet)   │            │    (SIM socket at flat sheet)   │
  │  Local: SCL/SDA leave open      │            │  Local: SCL/SDA leave open      │
  │         (pulled up in-module)   │            │         (pull up to 1.8V)       │
  │  Local: W_DISABLE# leave open   │            │  Local: FLIGHTMODE leave open   │
  │  Local: MICN/EARP/EARN = NC     │            │  Local: VDD_1V8 leave open      │
  │         (PCIE variant)          │            │         (using TPS7A0218)        │
  └────────────────────────────────┘            └────────────────────────────────┘
```

### Pre-wire checklist (MPCIe — primary)

- [ ] Place modem symbol (MPCIe socket — primary) in center-left of the flat sheet
- [ ] Place global labels on right edge (already done — 20 labels at x=207.01)
- [ ] Wire UART 6 signals to labels
- [ ] Wire PCM 4 signals to labels
- [ ] Wire USB 2 signals to labels (`MODEM_USB_DP`, `MODEM_USB_DN` — NOT `USB_DP`/`USB_DN`, those are the MCU USB)
- [ ] Wire control signals (RST, STATUS, NET_STATUS) to labels — no PWRKEY on MPCIe
- [ ] Antennas: MPCIe has onboard U.FL — no PCB antenna connectors needed (LGA fallback: wire GNSS_ANT/MAIN_ANT to U.FL)
- [ ] Wire power pins: VCC to `+3.3V` (NOT `+BATT` — MPCIe is 3.3V only) and GND to power symbols
- [ ] Add bulk capacitance (100–470µF) at modem power pins — **deferred to after placement**
- [ ] SIM socket + USIM passives (100nF cap, ESD diode) — **flat sheet**, wired to USIM_* labels from both variants
- [ ] Add U.FL connectors for antennas (LGA only)
- [ ] Add network status LED circuit (note: active-high on LGA, active-low on MPCIe)
- [ ] Run ERC — fix unconnected pins (mark unused as no-connect)

## Section: Codec (ALC5651 + PCM + I2S + transducers) — *to be specified*

## Section: Display (ST7789V + SPI + backlight) — *panel locked 2026-07-19*

> **Panel**: HS HS20HS072RX (LCSC C5329582) — 2.0" IPS TFT, 240×RGB×320, ST7789T3, 4-wire SPI, 12-pin 0.5mm ZIF FPC. 4 parallel white LEDs (LEDA/LEDK broken out for PWM dimming). See project-log.md 2026-07-19 Display Panel Selection.
>
> **Outer display**: EastRising ER-TFT1.14-2 (BuyDisplay) — 1.14" IPS TFT, 135×240, ST7789V (same driver family), 4-wire SPI, **8-pin 0.5mm FPC** (standard JLC-stockable ZIF connector). 3.3V only (no boost converter). Shares SPI bus with main display (+2 signals: CS2, DC2). **Both display panels purchased separately from PCB and assembled by user** (ZIF FPC plugs in post-assembly). See project-log.md 2026-07-19 Outer Display Re-Selection.
>
> **Form factor**: Flip/clamshell — both displays are on the display daughterboard (lid), connected to the main board via hinge flex cable (J8 main board → J9 daughterboard). See project-log.md 2026-07-19 Flip Form Factor.

### Board architecture (flip, two PCBs)

**Main board** (base): MCU, modem, codec, keypad, battery, power, USB-C, SIM, SD, antennas, microphone, loudspeaker, level shifter, ESD, crystals, passives. Connector J8 (14-pin 0.5mm ZIF) for hinge flex.

**Display daughterboard** (lid): main display panel (J7, 12-pin 0.5mm ZIF), outer display (J10, 8-pin 0.5mm ZIF), earpiece speaker. Connector J9 (14-pin 0.5mm ZIF) for hinge flex. ~5 components + 3 connectors — trivial board. Both displays are 3.3V-only TFT (no boost converters). **Display panels are purchased separately from the PCB and plugged into the ZIF connectors by the user post-assembly.**

### Hinge flex signals (~13 signals, 14-pin 0.5mm FFC)

| Signal | Direction | Source | Destination | Notes |
|--------|-----------|--------|-------------|-------|
| `DISP_SDA` | Main → Lid | MCU SPI MOSI | Display panel SDA | High-speed (up to 40MHz) |
| `DISP_SCL` | Main → Lid | MCU SPI SCK | Display panel SCL | High-speed (up to 40MHz) |
| `DISP_CS` | Main → Lid | MCU GPIO | Display panel CS | Active low |
| `DISP_DC` | Main → Lid | MCU GPIO | Display panel DC/RS | Data/command |
| `DISP_RST` | Main → Lid | MCU GPIO | Display panel RST | Reset |
| `+3.3V` | Main → Lid | TPS63021DSJR | Display panel IOVCC/VCI | Power |
| `GND` | — | Common | Common | Return for SPI + power |
| `LEDA` | Main → Lid | 3.3V rail | Display panel LEDA | Backlight anode (common) |
| `LEDK` | Main → Lid | PWM FET → GND | Display panel LEDK | Backlight cathode (PWM dimming) |
| `SPK+` | Main → Lid | ALC5651 earpiece out+ | Earpiece speaker + | Differential audio |
| `SPK-` | Main → Lid | ALC5651 earpiece out- | Earpiece speaker - | Differential audio |
| `OUTER_CS` | Main → Lid | MCU GPIO | Outer display CS2 | Active low (shared SPI bus with main display) |
| `OUTER_DC` | Main → Lid | MCU GPIO | Outer display DC2 | Data/command (shared SPI bus) |
| *(spare)* | — | — | — | 14th pin on FFC — unused / spare GND |

> **Camera**: Out of scope for rev1. DCMI (11 pins + 1 power) stays on main board when added. No hinge flex reservation. See project-log.md 2026-07-19 Flip Form Factor.

### Backlight PWM circuit (main board)

4 parallel white LEDs in the panel, common anode (LEDA), Vf 3.0V, 80mA total. Circuit on main board (LEDK switches to GND):
- `+3.3V` → current-limiting resistors → panel LEDA (through hinge flex)
- Panel LEDK (through hinge flex) → N-FET drain → N-FET source → GND
- N-FET gate: MCU timer-output GPIO (PWM dimmable, off during standby per FR-4.3)
- No boost LED driver needed (parallel LEDs, 3.0V Vf < 3.3V rail)

## Section: Keypad (5×4 matrix) — *to be specified*

## Section: Fuel Gauge (MAX17048) — *to be specified*

## Section: ESD Protection — *to be specified (distributed per-connector)*

### U10 — USBLC6-2SC6 (USB-C ESD protection, SOT-23-6)

> Datasheet: `docs/reference/usblc6-2.pdf` (ST DS4260 Rev 7, Dec 2021, 14pp). LCSC C7519. ST OEM. **Protects D+, D-, AND VBUS** — the block diagram previously (incorrectly) said "data, not VBUS." Corrected 2026-07-21 after downloading the datasheet. The USBLC6-2 is specifically designed for USB 2.0 ports — it has a VBUS pin (pin 5) that clamps ESD strikes on the 5V rail in addition to the two data-line pairs.

**Pinout (SOT-23-6, top view — pin 1 marked with dot/bar):**
```
       ┌─────┐
   1 ──┤ I/O1├── 6
   2 ──┤ GND ├── 5
   3 ──┤ I/O2├── 4
       └─────┘
```

| Pin | Name | Net / connection | Notes |
|-----|------|------------------|-------|
| 1 | I/O1 | `USB_DP` (D+) | USB 2.0 D+ — ties to J1 A6+B6 (combined) on one side, MCU USB OTG_FS D+ on the other. **Pin 1 and pin 6 are the same I/O1 line internally** — they're the two ends of the D+ ESD diode. |
| 2 | GND | `GND` | Ground reference for all ESD clamps. **Critical: tie directly to GND plane with short, wide trace** — ESD current needs a low-inductance path to ground or the clamp voltage rises. |
| 3 | I/O2 | `USB_DN` (D-) | USB 2.0 D- — ties to J1 A7+B7 (combined) on one side, MCU USB OTG_FS D- on the other. **Pin 3 and pin 4 are the same I/O2 line internally** — two ends of the D- ESD diode. |
| 4 | I/O2 | `USB_DN` (D-) | Second end of I/O2 — tie to pin 3 (or use as the "MCU side" of D- if pin 3 is the "connector side"). Either way, both pins are on the same net. |
| 5 | VBUS | `VBUS` (5V) | **VBUS ESD clamp.** Ties to the VBUS net — clamps ESD strikes on the 5V rail from the USB-C connector. This is the primary VBUS ESD protection; the MCP73831's internal ESD is secondary. |
| 6 | I/O1 | `USB_DP` (D+) | Second end of I/O1 — tie to pin 1 (or use as the "MCU side" of D+ if pin 1 is the "connector side"). |

**Wiring topology (recommended):**
```
J1 A6+B6 (D+) ──┬──── U10 pin 1 (I/O1, connector side)
                └──── U10 pin 6 (I/O1, MCU side) ──── MCU USB_OTG_FS D+

J1 A7+B7 (D-) ──┬──── U10 pin 3 (I/O2, connector side)
                └──── U10 pin 4 (I/O2, MCU side) ──── MCU USB_OTG_FS D-

J1 A4B9+B4A9 (VBUS) ──── U10 pin 5 (VBUS) ──── VBUS net ──── MCP73831 VDD

U10 pin 2 (GND) ──── GND plane (short wide trace)
```

The "connector side / MCU side" split on pins 1/6 and 3/4 is optional — both pins are on the same net internally, so you can tie them together at a single point if routing is easier that way. The split is useful when the USBLC6-2 sits physically between the connector and the MCU: D+ enters pin 1, exits pin 6, continues to MCU. The ESD diode is in the middle of the trace, which is the ideal placement (ESD clamped as close to the connector as possible, before the signal reaches the MCU).

**Key specs (from datasheet §1, Table 2):**
- IEC 61000-4-2 Level 4: ±15kV air discharge, ±8kV contact discharge
- Working voltage (VRWM): 5V — matches USB 2.0 VBUS and data lines
- Clamping voltage: 12V @ 1A, 17V @ 5A (8/20µs pulse)
- Capacitance I/O to GND: 2.5pF typ, 3.5pF max — low enough for USB 2.0 high-speed (480 Mbps)
- Capacitance matching ΔCi/o-GND: 0.015pF — critical for D+/D- signal balance
- Leakage: 150nA max — negligible for battery life

**Placement (layout-critical):**
- Place U10 **as close to J1 as physically possible** — ESD strikes happen at the connector, and the goal is to clamp them before they propagate into the board.
- Pin 2 (GND) trace to GND plane must be **short and wide** (<2mm, >0.3mm wide) — ESD current is high-frequency (sub-nanosecond rise time), so trace inductance matters more than resistance. A long thin GND trace turns the clamp into an antenna.
- D+/D- traces through U10 should maintain 90Ω differential impedance (USB 2.0 spec) — keep the traces short and symmetric.

### U11 — ESDA6V1-5SC6 (multi-line ESD protection, SOT-23-6)

> LCSC C6650. ST OEM. Used for SIM card and/or other connector ESD protection. Pinout and application TBD — to be documented when SIM/modem connector sections are specified. 3D model shared with U10 (same SOT-23-6 package).


## Section: SD Card — *to be specified (sourcing-deferred: combo or separate)*
