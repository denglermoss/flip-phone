---
status: active
updated: 2026-08-16
---
# MCU Pin Assignment — STM32H743ZIT6 (LQFP-144)

**Created**: 2026-07-22
**Status**: DRAFT — pin numbers verified against STM32H743ZI datasheet (DS12110 Rev 11, Table 9, pages 64-88)
**Purpose**: O3 gate — maps every peripheral to a specific LQFP-144 pin before schematic entry.

## Verification Source

All pin numbers in this document are verified against the STM32H743ZI datasheet Table 9 "Pin/ball definition" (DS12110 Rev 11, pages 64-88). The LQFP-144 column (3rd package column) was extracted via PDF MCP `tableextraction__extract_tables` and cross-checked.

**Key LQFP-144 constraints discovered:**
- Port I (PI0-PI11), Port J (PJ0-PJ15), Port K (PK0-PK7) are **NOT available** on LQFP-144.
- PH2-PH15 are **NOT available** — only PH0/PH1 (HSE crystal) exist on LQFP-144.
- Pin 28 is **PC2_C** (analog-coupled), NOT PC2 — it lacks SPI2/I2S2 alternate functions.
- Pin 29 is **PC3_C** (analog-coupled), NOT PC3.
- VREF- is not bonded out on LQFP-144 (internally tied to VSSA).
- Available GPIO ports: PA, PB, PC, PD, PE, PF, PG (+ PH0/PH1 for HSE).

## Architecture Decisions Affecting Pin Assignment

1. **DBVDD = 1.8V** (ALC5651 codec): I2S-1 (modem↔codec) is direct 1.8V. I2S-2 (MCU↔codec) goes through a level shifter (SN74AXC4T774, 3.3V↔1.8V). I2C bus uses 1.8V pullups (STM32H7 FT pins tolerate this; MAX17048 VIH=1.4V min works at 1.8V).
2. **LPUART1 on PB6/PB7**: Matches Nucleo-H743ZI prototype. GPIO-based RTS/CTS (hardware LPUART1_RTS/CTS on PA11/PA12 conflict with USB OTG_FS).
3. **I2S2 (not SAI)**: SPI2 in I2S mode for codec music path. Simpler, well-supported in Zephyr.
4. **SDMMC1 4-bit mode**: Full 4-bit SD interface for speed.
5. **SWD (not JTAG)**: JTAG pins (PA15, PB3, PB4) repurposed as GPIO for display control.

---

## Pin Assignment Table

### Power, Crystal, Reset, Boot (fixed by package)

| Pin # | Pin Name | Net | Notes |
|-------|----------|-----|-------|
| 6 | VBAT | +3.3V | RTC supply (tie to +3.3V) |
| 8 | PC14-OSC32_IN | LSE_IN | 32.768kHz crystal (optional — NC if RTC unused) |
| 9 | PC15-OSC32_OUT | LSE_OUT | 32.768kHz crystal (optional — NC if RTC unused) |
| 23 | PH0-OSC_IN | HSE_IN | 8MHz crystal input |
| 24 | PH1-OSC_OUT | HSE_OUT | 8MHz crystal output |
| 25 | NRST | NRST | Reset (active low, 10kΩ pullup to +3.3V) |
| 30 | VDD | +3.3V | Power |
| 31 | VSSA | GND | Analog ground |
| 32 | VREF+ | +3.3V | ADC reference (tie to +3.3V via ferrite bead) — **IMPLEMENTED 2026-07-28** (L1 ferrite + C18/C19 decoupling) |
| 33 | VDDA | +3.3V | Analog supply (via ferrite bead + 1µF) — **IMPLEMENTED 2026-07-28** (L1 ferrite + C18 1µF + C19 10nF) |
| 38 | VSS | GND | Ground |
| 39 | VDD | +3.3V | Power |
| 48 | VSS | GND | Ground |
| 49 | VDD | +3.3V | Power |
| 51 | VSS | GND | Ground |
| 52 | VDD | +3.3V | Power |
| 61 | VSS | GND | Ground |
| 62 | VDD | +3.3V | Power |
| 71 | VCAP | — | 2.2µF to GND (internal LDO output cap) |
| 72 | VDD | +3.3V | Power |
| 83 | VSS | GND | Ground |
| 84 | VDD | +3.3V | Power |
| 94 | VSS | GND | Ground |
| 95 | VDD33USB | +3.3V | USB FS PHY supply (tie to +3.3V) |
| 106 | VCAP | — | 2.2µF to GND (internal LDO output cap) |
| 107 | VSS | GND | Ground |
| 108 | VDD | +3.3V | Power |
| 120 | VSS | GND | Ground |
| 121 | VDD | +3.3V | Power |
| 130 | VSS | GND | Ground |
| 131 | VDD | +3.3V | Power |
| 138 | BOOT0 | GND | Boot from flash (tie to GND via 10kΩ) |
| 143 | PDR_ON | +3.3V | Power-down reset (tie to +3.3V via 10kΩ) |
| 144 | VDD | +3.3V | Power |

### SWD Debug (fixed by package)

| Pin # | Pin Name | AF | Net | Direction | Notes |
|-------|----------|----|-----|-----------|-------|
| 105 | PA13 | AF0 | SWDIO | I/O | SWD data |
| 109 | PA14 | AF0 | SWCLK | In | SWD clock |

### USB OTG_FS (fixed by hardware — AF10)

| Pin # | Pin Name | AF | Net | Direction | Notes |
|-------|----------|----|-----|-----------|-------|
| 103 | PA11 | AF10 | USB_DM | I/O | USB D- via USBLC6-2 (D1) |
| 104 | PA12 | AF10 | USB_DP | I/O | USB D+ via USBLC6-2 (D1) |

### VBUS Sense

| Pin # | Pin Name | AF | Net | Direction | Notes |
|-------|----------|----|-----|-----------|-------|
| 34 | PA0 | GPIO/ADC | VBUS_SENSE | In | 100kΩ/68kΩ divider from VBUS (5V→2.02V) |

### LPUART1 (Modem UART — matches Nucleo prototype)

| Pin # | Pin Name | AF | Net | Direction | Notes |
|-------|----------|----|-----|-----------|-------|
| 136 | PB6 | AF8 | MCU_UART_TX | Out | To level shifter → modem UART_RX |
| 137 | PB7 | AF8 | MCU_UART_RX | In | From level shifter ← modem UART_TX |
| 46 | PB0 | GPIO | MCU_UART_RTS | Out | GPIO-based RTS (HW RTS on PA12 conflicts with USB) |
| 47 | PB1 | GPIO | MCU_UART_CTS | In | GPIO-based CTS (HW CTS on PA11 conflicts with USB) |

### I2C1 (Codec + Fuel Gauge — shared bus, 1.8V pullups)

| Pin # | Pin Name | AF | Net | Direction | Notes |
|-------|----------|----|-----|-----------|-------|
| 139 | PB8 | AF4 | I2C_SCL | I/O | 4.7kΩ pullup to +1V8 (not +3.3V — see DBVDD decision) |
| 140 | PB9 | AF4 | I2C_SDA | I/O | 4.7kΩ pullup to +1V8 |

**Bus devices**: ALC5651 (addr 0x1A, 1.8V DBVDD), MAX17048 (addr 0x36, VIH=1.4V min — works at 1.8V). STM32H7 I2C pins are FT (5V-tolerant), open-drain mode works with 1.8V pullups.

### SPI1 (Display — direct on single board, no hinge flex)

| Pin # | Pin Name | AF | Net | Direction | Notes |
|-------|----------|----|-----|-----------|-------|
| 41 | PA5 | AF5 | DISP_SCK | Out | SPI clock (main display) |
| 135 | PB5 | AF5 | DISP_MOSI | Out | SPI data (main display) |

**Display control GPIOs** (JTAG pins repurposed — SWD only):

| Pin # | Pin Name | AF | Net | Direction | Notes |
|-------|----------|----|-----|-----------|-------|
| 134 | PB4 | GPIO | DISP_CS | Out | Main display chip select (active low) |
| 133 | PB3 | GPIO | DISP_DC | Out | Main display data/command |
| 110 | PA15 | GPIO | DISP_RST | Out | Main display reset (active low) |
| 124 | PG9 | — | *(spare)* | — | **Freed 2026-08-16** — was OUTER_CS (outer display dropped with flip form factor). Available for future use (camera DCMI, analog, etc.). |
| 125 | PG10 | — | *(spare)* | — | **Freed 2026-08-16** — was OUTER_DC (outer display dropped with flip form factor). Available for future use (camera DCMI, analog, etc.). |

### I2S2 (Codec music path — via SN74AXC4T774 level shifter)

| Pin # | Pin Name | AF | Net | Direction | Notes |
|-------|----------|----|-----|-----------|-------|
| 73 | PB12 | AF5 | I2S2_LRCK | Out | I2S WS (MCU is master) → shifter → codec LRCK2 |
| 74 | PB13 | AF5 | I2S2_BCLK | Out | I2S CK (MCU is master) → shifter → codec BCLK2 |
| 76 | PB15 | AF5 | I2S2_DACDAT | Out | I2S SDO (MCU→codec) → shifter → codec DACDAT2 |
| 75 | PB14 | AF5 | I2S2_ADCDAT | In | I2S SDI (codec→MCU) ← shifter ← codec ADCDAT2 |

**Level shifter**: SN74AXC4T774 (U12), VCCA=+1V8, VCCB=+3.3V. DIR for BCLK/LRCK/DACDAT = B→A (3.3V→1.8V, MCU→codec). DIR for ADCDAT = A→B (1.8V→3.3V, codec→MCU). Hardwire DIR pins (directions are fixed). MCLK not routed — codec uses internal PLL.

### SDMMC1 (microSD — 4-bit mode)

| Pin # | Pin Name | AF | Net | Direction | Notes |
|-------|----------|----|-----|-----------|-------|
| 98 | PC8 | AF12 | SD_D0 | I/O | Data bit 0 |
| 99 | PC9 | AF12 | SD_D1 | I/O | Data bit 1 |
| 111 | PC10 | AF12 | SD_D2 | I/O | Data bit 2 |
| 112 | PC11 | AF12 | SD_D3 | I/O | Data bit 3 |
| 113 | PC12 | AF12 | SD_CK | Out | Clock |
| 116 | PD2 | AF12 | SD_CMD | I/O | Command |

### Keypad Matrix (5×4 = 9 GPIO)

| Pin # | Pin Name | AF | Net | Direction | Notes |
|-------|----------|----|-----|-----------|-------|
| 58 | PE7 | GPIO | KEY_ROW0 | I/O | Keypad row 0 |
| 59 | PE8 | GPIO | KEY_ROW1 | I/O | Keypad row 1 |
| 60 | PE9 | GPIO | KEY_ROW2 | I/O | Keypad row 2 |
| 63 | PE10 | GPIO | KEY_ROW3 | I/O | Keypad row 3 |
| 64 | PE11 | GPIO | KEY_ROW4 | I/O | Keypad row 4 |
| 65 | PE12 | GPIO | KEY_COL0 | I/O | Keypad column 0 |
| 66 | PE13 | GPIO | KEY_COL1 | I/O | Keypad column 1 |
| 67 | PE14 | GPIO | KEY_COL2 | I/O | Keypad column 2 |
| 68 | PE15 | GPIO | KEY_COL3 | I/O | Keypad column 3 |

### Modem Control GPIOs

| Pin # | Pin Name | AF | Net | Direction | Notes |
|-------|----------|----|-----|-----------|-------|
| 141 | PE0 | GPIO/EXTI | MCU_RI_IRQ | In | Ring indicator (falling edge interrupt) |
| 142 | PE1 | GPIO | MCU_DTR | Out | Data terminal ready (sleep control) |
| 1 | PE2 | GPIO | MCU_MODEM_RST | Out | Modem reset (active low) |
| 2 | PE3 | GPIO/EXTI | MCU_MODEM_STATUS | In | WAKE# interrupt (falling edge) |
| 5 | PE6 | GPIO | MCU_MODEM_PWR_EN | Out | Load switch enable (modem +3.3V power control) |

### Power Monitoring GPIOs

| Pin # | Pin Name | AF | Net | Direction | Notes |
|-------|----------|----|-----|-----------|-------|
| 3 | PE4 | GPIO/EXTI | PWR_3V3_OK | In | TPS63021 PG (power good) interrupt |
| 4 | PE5 | GPIO/EXTI | FUEL_ALERT | In | MAX17048 ALRT interrupt |

### Backlight PWM

| Pin # | Pin Name | AF | Net | Direction | Notes |
|-------|----------|----|-----|-----------|-------|
| 100 | PA8 | AF1 (TIM1_CH1) | BL_PWM | Out | Backlight dimming PWM |

### Level Shifter DIR Control (optional — can hardwire)

If SN74AXC4T774 DIR pins are hardwired (directions fixed), no MCU GPIO needed. If software-controlled for flexibility:

| Pin # | Pin Name | AF | Net | Direction | Notes |
|-------|----------|----|-----|-----------|-------|
| 56 | PG0 | GPIO | SHIFTER_DIR | Out | Optional: level shifter direction control |

---

## Spare GPIO (unassigned)

| Pin # | Pin Name | Available For |
|-------|----------|---------------|
| 7 | PC13 | GPIO (RTC_OUT/WKUP4) |
| 10 | PF0 | GPIO / I2C2_SDA |
| 11 | PF1 | GPIO / I2C2_SCL |
| 12 | PF2 | GPIO |
| 13 | PF3 | GPIO / ADC3 |
| 14 | PF4 | GPIO / ADC3 |
| 15 | PF5 | GPIO / ADC3 |
| 18 | PF6 | GPIO / ADC3 / TIM16_CH1 |
| 19 | PF7 | GPIO / ADC3 / TIM17_CH1 |
| 20 | PF8 | GPIO / ADC3 / TIM16_CH1N |
| 21 | PF9 | GPIO / ADC3 / TIM17_CH1N |
| 22 | PF10 | GPIO / ADC3 |
| 26 | PC0 | GPIO / ADC123 |
| 27 | PC1 | GPIO / ADC123 |
| 28 | PC2_C | ADC3 only (analog-coupled, no digital AF) |
| 29 | PC3_C | ADC3 only (analog-coupled, no digital AF) |
| 35 | PA1 | GPIO / ADC1 / TIM2_CH2 |
| 36 | PA2 | GPIO / ADC12 / USART2_TX |
| 37 | PA3 | GPIO / ADC12 / USART2_RX |
| 40 | PA4 | GPIO / ADC12 / DAC1_OUT1 |
| 42 | PA6 | GPIO / ADC12 / SPI1_MISO (if display read needed) |
| 43 | PA7 | GPIO / ADC12 / TIM1_CH1N |
| 44 | PC4 | GPIO / ADC12 / I2S1_MCK |
| 45 | PC5 | GPIO / ADC12 |
| 48 | PB2 | GPIO / COMP1 |
| 49 | PF11 | GPIO / ADC1 |
| 50 | PF12 | GPIO / ADC1 |
| 53 | PF13 | GPIO / ADC2 |
| 54 | PF14 | GPIO / ADC2 |
| 55 | PF15 | GPIO |
| 57 | PG1 | GPIO |
| 69 | PB10 | GPIO / I2C2_SCL / USART3_TX |
| 70 | PB11 | GPIO / I2C2_SDA / USART3_RX |
| 77 | PD8 | GPIO / USART3_TX |
| 78 | PD9 | GPIO / USART3_RX |
| 79 | PD10 | GPIO / USART3_CK |
| 80 | PD11 | GPIO |
| 81 | PD12 | GPIO / TIM4_CH1 / I2C4_SCL |
| 82 | PD13 | GPIO / TIM4_CH2 / I2C4_SDA |
| 85 | PD14 | GPIO / TIM4_CH3 |
| 86 | PD15 | GPIO / TIM4_CH4 |
| 87 | PG2 | GPIO |
| 88 | PG3 | GPIO |
| 89 | PG4 | GPIO |
| 90 | PG5 | GPIO |
| 91 | PG6 | GPIO |
| 92 | PG7 | GPIO / USART6_CK |
| 93 | PG8 | GPIO / USART6_RTS |
| 96 | PC6 | GPIO / I2S2_MCK / TIM3_CH1 |
| 97 | PC7 | GPIO / I2S3_MCK / TIM3_CH2 |
| 101 | PA9 | GPIO / LPUART1_TX / USART1_TX |
| 102 | PA10 | GPIO / LPUART1_RX / USART1_RX |
| 114 | PD0 | GPIO / FDCAN1_RX |
| 115 | PD1 | GPIO / FDCAN1_TX |
| 117 | PD3 | GPIO / USART2_CTS |
| 118 | PD4 | GPIO / USART2_RTS |
| 119 | PD5 | GPIO / USART2_TX |
| 122 | PD6 | GPIO / USART2_RX |
| 123 | PD7 | GPIO / USART2_CK |
| 126 | PG11 | GPIO / SPI1_SCK |
| 127 | PG12 | GPIO / SPI6_MISO |
| 128 | PG13 | GPIO / SPI6_SCK / USART6_CTS |
| 129 | PG14 | GPIO / SPI6_MOSI / USART6_TX |
| 132 | PG15 | GPIO / USART6_CTS |

**Spare count**: ~60 GPIO pins available for future expansion (camera, sensors, LEDs, etc.)

---

## Summary Statistics

| Category | Pin Count |
|----------|-----------|
| Power/Ground (fixed) | 26 |
| Crystal/Reset/Boot (fixed) | 6 |
| SWD (fixed) | 2 |
| USB OTG_FS (fixed) | 2 |
| VBUS sense | 1 |
| LPUART1 (modem UART) | 4 |
| I2C1 (codec + fuel gauge) | 2 |
| SPI1 (displays) | 2 + 5 control |
| I2S2 (codec music) | 4 |
| SDMMC1 (microSD) | 6 |
| Keypad (5×4 matrix) | 9 |
| Modem control | 5 |
| Power monitoring | 2 |
| Backlight PWM | 1 |
| **Total assigned** | **73** |
| **Spare GPIO** | **~60** |
| **Total LQFP-144 pins** | **144** |

## Conflicts Resolved

1. **LPUART1 RTS/CTS vs USB OTG_FS**: LPUART1 hardware RTS (PA12) and CTS (PA11) conflict with USB D+/D-. Resolved: GPIO-based RTS/CTS on PB0/PB1.
2. **JTAG vs display control**: PA15 (JTDI), PB3 (JTDO), PB4 (NJTRST) conflict with JTAG. Resolved: SWD-only debugging, JTAG pins repurposed as GPIO for display CS/DC/RST.
3. **PC2_C vs I2S2_SDI**: LQFP-144 pin 28 is PC2_C (analog-coupled), which lacks SPI2/I2S2 alternate functions. Resolved: use PB14 for I2S2_SDI instead.
4. **I2C voltage domain**: With DBVDD=1.8V, codec I2C is 1.8V. Resolved: 1.8V pullups on I2C bus, STM32H7 FT pins tolerate this, MAX17048 VIH=1.4V min works.

## Notes for Schematic Entry

- All VDD pins: 100nF decoupling cap to nearest VSS
- VDDA: ferrite bead from +3.3V, 1µF + 10nF to VSSA — **IMPLEMENTED 2026-07-28** (L1=BLM18KG601SN1D, C18=1µF, C19=10nF)
- VCAP pins (71, 106): 2.2µF to GND each (internal LDO output caps)
- VDD33USB (pin 95): tie to +3.3V, 100nF decoupling
- BOOT0 (pin 138): 10kΩ to GND (boot from flash)
- PDR_ON (pin 143): 10kΩ to +3.3V (enable power-down reset)
- NRST (pin 25): 10kΩ pullup to +3.3V, 100nF to GND
- HSE: 8MHz crystal + 2× 22pF load caps on PH0/PH1
- LSE: 32.768kHz crystal + 2× 12pF load caps on PC14/PC15 (optional — NC if RTC unused)
- I2C pullups: 4.7kΩ to **+1V8** (not +3.3V — see DBVDD=1.8V decision)
- SDMMC: 10kΩ pullups on CMD and DAT0-DAT3
- All unused GPIO: configure as analog input (lowest power)
- Keypad GPIO: internal pull-ups enabled, columns scanned as outputs
