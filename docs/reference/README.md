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
| `max9880a.pdf` | Analog Devices MAX9880A datasheet (Rev 2) — dual-port codec, TQFN-48 | https://www.analog.com/media/en/technical-documentation/data-sheets/MAX9880A.pdf |
| `stm32h743zi.pdf` | STMicroelectronics STM32H743ZI datasheet (LQFP-144 electrical/mechanical/pinout) | https://www.st.com/resource/en/datasheet/stm32h743zi.pdf |
| `dm00314099-stm32h742-stm32h743753-and-stm32h750-value-line-advanced-armbased-32bit-mcus-stmicroelectronics.pdf` | STMicroelectronics RM0433 Rev 8 — STM32H742/H743/753/H750 reference manual (peripheral registers, 3353 pp) | https://www.st.com/resource/en/reference_manual/dm00314099-stm32h742-stm32h743753-and-stm32h750-value-line-advanced-armbased-32bit-mcus-stmicroelectronics.pdf |
| `dm00499160-stm32h7-nucleo144-boards-mb1364-stmicroelectronics.pdf` | STMicroelectronics UM2407 Rev 5 — STM32H7 Nucleo-144 boards (MB1364) user manual (board schematics, jumper config, ST-Link) | https://www.st.com/resource/en/user_manual/dm00499160-stm32h7-nucleo144-boards-mb1364-stmicroelectronics.pdf |
| `ST7789V.pdf` | Sitronix ST7789V LCD controller datasheet (240RGB×320, 262K color TFT controller/driver) | https://newhavendisplay.com/content/datasheets/ST7789V.pdf |

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
| Analog Devices MAX9880A product page | https://www.analog.com/en/products/max9880a.html |

## Exact part numbers (for cross-checking on vendor sites)

- **MCU**: STM32H743ZIT6 (LQFP-144, 2MB Flash, 1MB RAM)
- **MCU dev board**: NUCLEO-H753ZI (substitute for obsolete NUCLEO-H743ZI; H753 = H743 + crypto, identical for this project)
- **Cellular module (final PCB)**: SIM7600A-H
- **Cellular module (prototyping HAT)**: SIM7600NA-H (Waveshare HAT, SKU 30717)
- **Audio codec**: MAX9880AETM+T (TQFN-48, 6×6mm) — Mouser 700-MAX9880AETM+T
- **Display dev module**: Waveshare 2inch LCD Module, SKU 17344 (ST7789VW driver)
- **Display controller**: ST7789V (Sitronix; Waveshare module uses ST7789VW variant — same datasheet covers both)
- **Display raw panel (final PCB candidate)**: W200QVC016-A or equivalent 2.0" ST7789V FPC panel

## Maintenance

When a vendor publishes a new revision, replace the local file and update the "Source" URL (and the version in the filename) in this index. If a document is cited by version in the project docs (e.g., "Hardware Design Manual V1.03 §3.6"), note the version change in `docs/project-log.md` so the citation trail stays accurate.
