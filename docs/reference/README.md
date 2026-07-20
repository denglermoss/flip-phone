# Reference Documentation

Local copies of vendor datasheets, reference manuals, hardware design docs, and saved wiki pages that this project relies on. These are **not** version-controlled (see `.gitignore` — everything in this directory except this README is ignored). They are large binary files that vendors update independently. This index records what belongs here, the exact part numbers, and where to download each so anyone can re-fetch the current version.

## How to populate

Download each file below into this directory (`docs/reference/`). Browser "Save Page As" creates an `.html` file plus a `_files/` subdirectory of assets — both belong here. The `.gitignore` excludes everything except this README, so the files stay local-only.

## Index

### PDFs

| File | Part / Document | Source |
|------|-----------------|--------|
| `SIM7600 Series Hardware Design_V1.03.pdf` | SIMCom SIM7600 Series Hardware Design Manual V1.03 (the version cited in project docs — §3.6 PCM interface, Table 32 1.8V Digital I/O) | https://simcom.ee/documents/SIM7600E/SIM7600%20Series%20Hardware%20Design_V1.03.pdf |
| `SIM7600_Series_Hardware_Design_V1.08.pdf` | SIMCom SIM7600 Series Hardware Design Manual V1.08 (newer, same PCM spec, may have fixes) | https://edworks.co.kr/wp-content/uploads/2022/04/SIM7600_Series_Hardware_Design_V1.08.pdf |
| `max9880a.pdf` | Analog Devices MAX9880A datasheet (Rev 2) — dual-port codec, TQFN-48. **SUPERSEDED 2026-07-19**: MAX9880A replaced by ALC5651 (see below). Retained for historical reference. | https://www.analog.com/media/en/technical-documentation/data-sheets/MAX9880A.pdf |
| `alc5651.pdf` | Realtek ALC5651 datasheet (Rev 0.9) — dual I2S/PCM audio hub codec, QFN-40 5×5mm. **Current codec (LOCKED 2026-07-19).** §7.5.1 Two I2S/PCM Interface (PCM Mode A = short sync, compatible with SIM7600). §7.4.1 PLL (2.048–40MHz input). §10 Application Circuit (Figure 36). Pinout Figure 4 (40-pin QFN). | https://www.lcsc.com/product-detail/C963633.html (datasheet link) |
| `tps63021.pdf` | Texas Instruments TPS6302x (TPS63020/TPS63021) datasheet (SLVS916I, Rev. I, Oct 2019) — 4A-switch buck-boost converter, VSON-14 (DSJ). TPS63021 = fixed 3.3V out; TPS63020 = adjustable. Covers L1 inductor selection (§8.2.1, recommended 1.5µH Coilcraft XFL4020-152ML). | https://www.ti.com/lit/ds/symlink/tps63021.pdf |
| `stm32h743zi.pdf` | STMicroelectronics STM32H743ZI datasheet (LQFP-144 electrical/mechanical/pinout) | https://www.st.com/resource/en/datasheet/stm32h743zi.pdf |
| `dm00314099-stm32h742-stm32h743753-and-stm32h750-value-line-advanced-armbased-32bit-mcus-stmicroelectronics.pdf` | STMicroelectronics RM0433 Rev 8 — STM32H742/H743/753/H750 reference manual (peripheral registers, 3353 pp) | https://www.st.com/resource/en/reference_manual/dm00314099-stm32h742-stm32h743753-and-stm32h750-value-line-advanced-armbased-32bit-mcus-stmicroelectronics.pdf |
| `dm00499160-stm32h7-nucleo144-boards-mb1364-stmicroelectronics.pdf` | STMicroelectronics UM2407 Rev 5 — STM32H7 Nucleo-144 boards (MB1364) user manual (board schematics, jumper config, ST-Link) | https://www.st.com/resource/en/user_manual/dm00499160-stm32h7-nucleo144-boards-mb1364-stmicroelectronics.pdf |
| `ST7789V.pdf` | Sitronix ST7789V LCD controller datasheet (240RGB×320, 262K color TFT controller/driver) — covers both main display (ST7789T3) and outer display (ST7789V3) | https://newhavendisplay.com/content/datasheets/ST7789V.pdf |
| `HS20HS072RX-main-display.pdf` | HS HS20HS072RX panel datasheet — 2.0" IPS TFT, 240×RGB×320, ST7789T3, 12-pin 0.5mm ZIF FPC (main display, LOCKED 2026-07-19). Pinout: 1=GND, 2=CS, 3=RS(DC), 4=SCL, 5=SDA, 6=RST, 7=NC, 8=I/O-VCC, 9=VCC, 10=LEDA, 11=LEDK, 12=GND. | https://www.lcsc.com/product-detail/C5329582.html |
| `ER-TFT1.14-2-outer-display.pdf` | EastRising ER-TFT1.14-2 panel datasheet — 1.14" IPS TFT, 135×240, ST7789V, 8-pin 0.5mm FPC top contact (outer display, LOCKED 2026-07-19). Pinout: 1=LEDA, 2=GND, 3=RESET, 4=RS(DC), 5=SDA, 6=SCL, 7=VDD, 8=CS. Purchased from BuyDisplay (not LCSC) — assembled by user post-PCB-assembly. | https://www.buydisplay.com/1-14-inch-tft-lcd-display-ips-panel-screen-135x240-for-smart-watch |
| `N114-2413THBIG01-H13-outer-display-superseded.pdf` | Wisevision N114-2413THBIG01-H13 panel datasheet — 1.14" IPS TFT, 240×135, ST7789V3, 13-pin 0.7mm FPC (**SUPERSEDED 2026-07-19**: 0.7mm pitch has no JLC-stocked connectors — replaced by ER-TFT1.14-2 with standard 0.5mm pitch). | https://lcsc.com/product-detail/C2890618.html |
| `N130-6428TSWOG01-H13-OLED-rejected.pdf` | Wisevision N130-6428TSWOG01-H13 panel datasheet — 1.3" SH1107 OLED, 128×64, 13-pin 0.7mm FPC (REJECTED 2026-07-19: requires 9V VPP external boost converter) | https://lcsc.com/product-detail/C2890613.html |

### Saved wiki pages (HTML + `_files/` subdirectory)

| File (+ assets dir) | Resource | Source URL |
|---------------------|----------|------------|
| `2inch LCD Module - Waveshare Wiki.html` (+ `2inch LCD Module - Waveshare Wiki_files/`) | Waveshare 2inch LCD Module wiki — pinout, schematic, example code (ST7789VW) | https://www.waveshare.com/wiki/2inch_LCD_Module |
| `SIM7600NA-H 4G HAT - Waveshare Wiki.html` (+ `SIM7600NA-H 4G HAT - Waveshare Wiki_files/`) | Waveshare SIM7600NA-H 4G HAT wiki — HAT pinout, audio port, AT commands, antennas | https://www.waveshare.com/wiki/SIM7600NA-H_4G_HAT |

### Non-PDF references (bookmark, don't download)

| Resource | URL |
|----------|-----|
| Waveshare 2inch LCD Module product page | https://www.waveshare.com/2inch-lcd-module.htm |
| Waveshare SIM7600NA-H 4G HAT product page | https://www.waveshare.com/product/sim7600na-h-4g-hat.htm |
| STMicroelectronics STM32H743/753 documentation hub | https://www.st.com/en/microcontrollers-microprocessors/stm32h743-753/documentation.html |
| ~~Analog Devices MAX9880A product page~~ **SUPERSEDED** | https://www.analog.com/en/products/max9880a.html |

## Exact part numbers (for cross-checking on vendor sites)

- **MCU**: STM32H743ZIT6 (LQFP-144, 2MB Flash, 1MB RAM)
- **MCU dev board**: NUCLEO-H753ZI (substitute for obsolete NUCLEO-H743ZI; H753 = H743 + crypto, identical for this project)
- **Cellular module (final PCB)**: SIM7600NA-H (JLC pre-order C5380303; "SIM7600A-H" was a misnomer — corrected 2026-07-19)
- **Cellular module (prototyping HAT)**: SIM7600NA-H (Waveshare HAT, SKU 30717)
- **Audio codec**: Realtek ALC5651-CG (QFN-40, 5×5mm) — LCSC C963633 (JLC Extended)
- **Display dev module**: Waveshare 2inch LCD Module, SKU 17344 (ST7789VW driver)
- **Display controller**: ST7789V (Sitronix; Waveshare module uses ST7789VW variant — same datasheet covers both)
- **Display raw panel (final PCB — LOCKED 2026-07-19)**: HS HS20HS072RX (LCSC C5329582) — 2.0" IPS TFT, ST7789T3, 12-pin 0.5mm ZIF FPC
- **Outer display raw panel (final PCB — LOCKED 2026-07-19)**: EastRising ER-TFT1.14-2 (BuyDisplay) — 1.14" IPS TFT, ST7789V, 8-pin 0.5mm FPC (purchased from BuyDisplay, not LCSC — user assembles post-PCB)

## Maintenance

When a vendor publishes a new revision, replace the local file and update the "Source" URL (and the version in the filename) in this index. If a document is cited by version in the project docs (e.g., "Hardware Design Manual V1.03 §3.6"), note the version change in `docs/project-log.md` so the citation trail stays accurate.
