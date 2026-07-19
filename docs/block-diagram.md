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
| `VBUS` | 5V | USB-C connector | MCP73831 charger input, MCU VBUS sense |
| `VBAT` | 3.4–4.3V (LiPo) | LiPo battery (direct, no regulator) | SIM7600 VBAT pins, TPS630201 input, MAX17048 sense |
| `+3V3` | 3.3V | TPS630201 buck-boost output | MCU, display, SD card, codec I2S side, level shifter 3.3V side, fuel gauge |
| `+1V8` | 1.8V | TPS7A0218 LDO output (from +3V3) | MAX9880A codec, level shifter 1.8V side (modem UART/PCM) |
| `GND` | 0V | Common ground | All blocks |

> **`VBAT` is separate from `+3V3`** — modem 2A bursts must not droop the MCU rail. LiPo connects directly to `VBAT` (no regulator). Bulk capacitance (100–470µF ceramic + tantalum) at modem VBAT pins, physically close to the modem.

---

## Section: MCU ↔ Modem Link

The most signal-dense interface in the design. Every phone function (dial, answer, hang up, SMS, signal, data) goes through this UART. The MCU also controls modem power (PWRKEY) and monitors modem status (STATUS). All signals cross a 1.8V↔3.3V voltage boundary and need level shifting.

### Voltage domains
| Side | Voltage | Device |
|------|---------|--------|
| MCU side | 3.3V (`+3V3`) | STM32H743ZI UART/GPIO pins |
| Modem side | 1.8V (`+1V8`) | SIM7600NA-H UART/GPIO pins (absolute max 2.1V — 3.3V would damage) |

> **Source**: SIM7600 HW Design Manual V1.03 §3.3.1 + Table 30 (absolute max 2.1V for digital pins) + Table 32 (VIH 1.17–2.1V, VOH 1.35–1.8V). Confirmed 2026-07-13 from datasheet.

### Components
| Ref | Part | Package | Notes |
|-----|------|---------|-------|
| U_MCU | STM32H743ZIT6 | LQFP-144 | 3.3V I/O. UART + control GPIOs on MCU side. |
| U_MODEM | SIM7600NA-H | LCC+LGA 30×30mm | 1.8V I/O. UART + control pins on modem side. |
| U_LVL | TXB0108D | TSSOP-20 | 8-bit bidirectional auto-direction-sensing level shifter. A side = 1.8V (modem), B side = 3.3V (MCU). **VCCA ≤ VCCB is required** — so A = 1.8V, B = 3.3V. |

> **Why TXB0108**: 8 bits covers all UART signals (7) + 1 spare (e.g. modem RESET or an extra GPIO). Auto-direction sensing works for UART (each signal is unidirectional). The project-log (2026-07-13) already calls out TXB0108 for this link. Alternative: SN74LVC8T245 (direction-controlled, more robust but needs direction pins). Stick with TXB0108 unless a signal-integrity issue emerges.

### UART signals (7)

| Signal | Direction | MCU side (3.3V) | Level shifter | Modem side (1.8V) | Modem pin # | Notes |
|--------|-----------|-----------------|---------------|---------------------|-------------|-------|
| `UART_TX` | MCU → modem | MCU UART TX | B1 → A1 | modem RXD | 68 | MCU sends AT commands |
| `UART_RX` | MCU ← modem | MCU UART RX | B2 ← A2 | modem TXD | 71 | Modem sends responses/URCs |
| `UART_RTS` | MCU → modem | MCU UART RTS | B3 → A3 | modem CTS | 67 | MCU requests to send |
| `UART_CTS` | MCU ← modem | MCU UART RX | B4 ← A4 | modem RTS | 66 | Modem clear to send |
| `UART_DTR` | MCU → modem | MCU GPIO (out) | B5 → A5 | modem DTR | 72 | Toggle for modem sleep/wake (`AT+CSCLK=1`) |
| `UART_RI` | MCU ← modem | MCU GPIO interrupt | B6 ← A6 | modem RI | 69 | Ring indicator — wakes MCU on incoming call |
| `UART_DCD` | MCU ← modem | MCU GPIO (in) | B7 ← A7 | modem DCD | 70 | Data carrier detect — optional, can leave NC if unused |

> **Modem pin numbers** from SIM7600 HW Design Manual V1.03 (confirmed 2026-07-13). TXD=71, RXD=68, RTS=66, CTS=67, RI=69, DCD=70, DTR=72.

> **TXB0108 bit 8 (spare)**: Could route modem RESET (if the SIM7600 has a RESET pin) or an extra GPIO. Or leave unused (tie input to GND with a pulldown per TXB0108 datasheet — floating auto-sense inputs can oscillate and waste power).

### Control GPIOs (not through UART — separate signals)

| Signal | Direction | MCU side | Level shifter? | Modem side | Modem pin | Notes |
|--------|-----------|----------|----------------|------------|-----------|-------|
| `PWRKEY` | MCU → modem | MCU GPIO (out) | Yes (3.3V→1.8V) | modem PWRKEY | (check manual) | Pulse low (~1s) to power on/off. **Required** — MCU cannot power-cycle modem without it. |
| `STATUS` | MCU ← modem | MCU GPIO (in) | Yes (1.8V→3.3V) | modem STATUS | (check manual) | High = modem ready. **Required** — MCU needs to know modem state. |
| `RESET` | MCU → modem | MCU GPIO (out) | Yes (3.3V→1.8V) | modem RESET | (check manual) | Hard reset — rarely needed, optional. Could use TXB0108 bit 8. |

> **PWRKEY and STATUS are mandatory** (per constraints.md). RESET is optional. These can go through the same TXB0108 (if bits are spare) or a smaller separate shifter (TXB0104 for 3-4 signals). Your call on how to group them.

### Power for the level shifter
| Pin | Net | Notes |
|-----|-----|-------|
| VCCA | `+1V8` | 1.8V supply (from TPS7A0218 LDO). Powers the modem-facing side. |
| VCCB | `+3V3` | 3.3V supply (from TPS630201). Powers the MCU-facing side. |
| OE | `+3V3` via pullup | Output enable (active high). Pull high to enable. Tie to VCCB or a GPIO for power sequencing. |
| GND | `GND` | Common ground. |

> **TXB0108 power sequencing**: VCCA must be present before OE goes high, or the outputs can glitch. Simplest: tie OE to VCCB with a pullup + a pulldown cap to GND for a slow RC ramp. Or drive OE from an MCU GPIO that starts LOW and goes HIGH after both rails are stable.

### UART selection on STM32H743

**Prototype used LPUART1** (PB6 TX, PB7 RX) — confirmed working 2026-07-13. For the PCB, two options:

1. **Keep LPUART1** — firmware already works with it. LPUART1 on H743 supports RTS/CTS (hardware flow control). Need to look up which alternate-function pins carry LPUART1_RTS / LPUART1_CTS on LQFP-144. Low-power UART is good for battery life (can wake from STOP mode on RX edge).
2. **Switch to a full USART** (USART1/2/3/6) — more features, higher max baud, but firmware would need updating. Not necessary unless LPUART1 lacks something needed.

**Recommendation**: Keep LPUART1 for firmware compatibility. Verify RTS/CTS pin availability on LQFP-144 before finalizing the pin map.

### Schematic layout (flat, one region)

```
    ┌─── MCU region ───────────────────┐         ┌─── Level shifter ─────────┐         ┌─── Modem region ──────────────┐
    │                                  │         │  TXB0108                   │         │  SIM7600NA-H                   │
    │  LPUART1_TX  ──────────────────┐ │         │  VCCA=+1V8  VCCB=+3V3      │         │  pin 68 RXD                   │
    │  LPUART1_RX  ◀────────────────┐│ │         │  OE=+3V3 (pullup)          │         │  pin 71 TXD                   │
    │  LPUART1_RTS ────────────────┐││ │         │                            │         │  pin 67 CTS                   │
    │  LPUART1_CTS ◀──────────────┐│││ │         │  B1 ── A1  (TX  →)         │───────▶│  pin 66 RTS                   │
    │  GPIO_DTR    ──────────────┐││││ │         │  B2 ── A2  (RX  ←)         │◀───────│  pin 72 DTR                   │
    │  GPIO_RI_IRQ ◀────────────┐│││││ │         │  B3 ── A3  (RTS →)         │───────▶│  pin 69 RI                    │
    │  GPIO_DCD    ◀───────────┐││││││ │         │  B4 ── A4  (CTS  ←)        │◀───────│  pin 70 DCD                   │
    │  GPIO_PWRKEY ───────────┐│││││││ │         │  B5 ── A5  (DTR  →)        │───────▶│  PWRKEY pin                   │
    │  GPIO_STATUS ◀────────┐││││││││ │         │  B6 ── A6  (RI   ←)        │◀───────│  STATUS pin                   │
    │                      │││││││││ │         │  B7 ── A7  (DCD  ←)        │◀───────│                               │
    │                      │││││││││ │         │  B8 ── A8  (spare/RESET →) │───────▶│  RESET pin (optional)         │
    └──────────────────────┼┼┼┼┼┼┼┼─┘         └────────────────────────────┘         └───────────────────────────────┘
                           ││││││││
                           ▼▼▼▼▼▼▼▼  (net labels: UART_TX, UART_RX, UART_RTS, etc. — labeled wires, not direct)
```

In practice: use **net labels** (`L`) on both sides of the level shifter rather than drawing long wires. MCU pins get labels like `UART_TX_MCU`, level shifter B1 gets `UART_TX_MCU`, A1 gets `UART_TX_MOD`, modem RXD pin gets `UART_TX_MOD`. KiCad connects same-named labels automatically.

### Pre-draw checklist
- [ ] Place STM32H743 symbol in MCU region (just the UART + control GPIO pins for now — full pin map comes later)
- [ ] Place SIM7600NA-H symbol in modem region (need to find or create the symbol — SIM7600 may not be in KiCad's default libraries; check LCSC/JLCPCB for a footprint)
- [ ] Place TXB0108D between them
- [ ] Wire UART signals (7) through the level shifter
- [ ] Wire PWRKEY + STATUS (through level shifter or separate shifter)
- [ ] Add power symbols: `+1V8` on VCCA, `+3V3` on VCCB, `GND` on GND
- [ ] Add OE pullup to `+3V3`
- [ ] Add net labels on both sides of the shifter
- [ ] Run ERC

### Open questions for this section
- [ ] **LPUART1 RTS/CTS pins on LQFP-144**: need to look up the alternate-function table in RM0433 to confirm which pins carry LPUART1_RTS and LPUART1_CTS. (Can do via the PDF MCP server against the local reference manual.)
- [ ] **SIM7600 PWRKEY and STATUS pin numbers**: confirmed in HW Design Manual but not captured in project-log — need to look up.
- [ ] **SIM7600 symbol for KiCad**: check if it exists in KiCad's default libraries, LCSC symbol library, or needs to be created from the datasheet pinout.
- [ ] **PWRKEY/STATUS through TXB0108 or separate shifter**: TXB0108 has 1 spare bit (bit 8) — could fit RESET but not both PWRKEY and STATUS. Options: (a) use TXB0108 for UART (7 bits) + RESET (1 bit), and a separate TXB0104 for PWRKEY + STATUS; (b) use two TXB0108s; (c) use simple voltage dividers for the 3 unidirectional control signals (PWRKEY is MCU→modem, STATUS is modem→MCU, RESET is MCU→modem — all unidirectional, so a resistor divider or single-gate buffer works).

---

## Section: Power — *to be specified*

## Section: MCU (full pin map) — *to be specified*

## Section: Modem (full pinout + SIM + antenna + USB) — *to be specified*

## Section: Codec (MAX9880A + PCM + I2S + transducers) — *to be specified*

## Section: Display (ST7789V + SPI + backlight) — *to be specified*

## Section: Keypad (5×4 matrix) — *to be specified*

## Section: Fuel Gauge (MAX17048) — *to be specified*

## Section: ESD Protection — *to be specified (distributed per-connector)*

## Section: SD Card — *to be specified (sourcing-deferred: combo or separate)*
