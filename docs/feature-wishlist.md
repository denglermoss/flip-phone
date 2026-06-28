# Feature Wishlist

Features are rated 1-10 based on user priority:
- **9-10**: Must have for MVP
- **7-8**: Required for daily driver
- **5-6**: Strong want — keep hardware options open
- **3-4**: Nice to have — don't compromise design for these
- **1-2**: Don't care / don't want

These ratings inform **component selection** — we should ensure the MCU, cellular module, and PCB have enough headroom for 5+ rated features without over-engineering for 1-2 rated ones.

## Communication

| Feature | Rating | Notes |
|---------|--------|-------|
| SMS | 9 | Near-MVP. Most LTE modules support SMS via AT commands natively. |
| Call history (missed/received/dialed) | 7 | Daily driver. Firmware-only feature, needs flash storage. |
| Speed dial / contacts | 7 | Daily driver. Needs persistent storage (flash/EEPROM). |
| MMS (picture messages) | 6 | Requires data connection + camera. Module-dependent. |
| Voicemail | 3 | Carrier-side feature. Phone just needs to dial voicemail number. Minimal hardware impact. |
| Speakerphone | 3 | Firmware + audio routing. Needs speaker capable of louder output. |
| Call recording | 1 | Not wanted. |

## Connectivity

| Feature | Rating | Notes |
|---------|--------|-------|
| USB data transfer | 8 | Daily driver. Also critical for **ecosystem interconnect** (car module tethering). MCU must have USB device/peripheral capability. |
| Bluetooth (headset, audio, file transfer) | 6 | Strong want. MCU selection should support BT (nRF52 has built-in BLE; STM32 would need external BT module). Note: BLE != classic BT — A2DP audio needs classic BT. |
| Hotspot / tethering | 6 | Strong want. Ties into ecosystem concept — phone provides LTE to car module via USB. Cellular module must support data + tethering. Most LTE modules do. **Note (2026-06-28)**: Simultaneous VoLTE+data (tethering while on a call) is NOT required — "pause data during call" is acceptable. SIM7600 supports data via CMUX+PPP. See project-log.md Modem Revisit (Second Round). |
| Wi-Fi (OTA updates, basic internet) | 4 | Nice to have. ESP32 has built-in; STM32/nRF52 would need external module. Could use for firmware OTA updates. |
| NFC | 1.5 | Not wanted. |

## Media

| Feature | Rating | Notes |
|---------|--------|-------|
| MP3 / music playback | 6 | Strong want. Needs: audio DAC or I2S output, storage (SD card), MP3 decoder (software or hardware). MCU must have enough processing power for decode. |
| Photo capture | 6 | Strong want. Needs camera module (SPI/MIPI). Display should be color for preview. |
| Video recording | 5 | Nice to have. More demanding — higher data rate, storage, processing. |
| FM radio | 4 | Nice to have. Some cellular modules (e.g., Quectel) have built-in FM. Headphone jack acts as antenna. |
| Custom ringtones | 2 | Don't care. |
| Voice recorder | 1 | Not wanted. |

## Camera

| Feature | Rating | Notes |
|---------|--------|-------|
| Photo capture | 6 | See Media section. Camera module selection affects PCB layout and display choice (color preferred). |
| Video recording | 5 | See Media section. |
| Flash / torch | 2 | Don't care. |

## Utility / Apps

| Feature | Rating | Notes |
|---------|--------|-------|
| Calculator | 2 | Don't care. Firmware-only, trivial. |
| Calendar / reminders | 1 | Not wanted. |
| Alarm clock | 1 | Not wanted. |
| Stopwatch / timer | 1 | Not wanted. |
| Notes | 1 | Not wanted. |
| Flashlight | 2 | Don't care. |

## Hardware Features (Component Selection Impact)

| Feature | Rating | Component Impact |
|---------|--------|-----------------|
| MicroSD card slot | 7 | Daily driver. MCU needs SPI or SDIO interface. PCB space for connector. Critical for music + photo storage. |
| 3.5mm headphone jack | 4 | Nice to have. PCB space + audio routing. Could use BT headphones instead. |
| Vibration motor | 2 | Don't care. GPIO + driver circuit, minimal impact. |
| LED notification light | 2 | Don't care. Single GPIO, trivial. |
| GPS / GNSS | (see ecosystem) | Some LTE modules have built-in GNSS (e.g., Quectel EG25-G has GPS/GLONASS). Important for ecosystem (car navigation). Select module with GNSS if possible. |
| Proximity / ambient light sensor | 1 | Not wanted. |
| Hardware power button | — | No preference. |

## Ecosystem Implications (Future — Does Not Affect MVP)

The phone is envisioned as the **hub** in a multi-device ecosystem. Key hardware implications to keep options open:

1. **USB with data capability** (rating 8) — MCU must support USB device mode. This is the primary interconnect for future modules (e.g., car infotainment). **Affects MCU selection.**
2. **GPS/GNSS** — Select a cellular module with built-in GNSS if available (SIM7600 has built-in GNSS). Costs nothing extra and enables ecosystem navigation use cases. **Affects module selection.**
3. **Bluetooth** (rating 6) — May be used for wireless ecosystem connectivity later. nRF52 has BLE built-in; classic BT (A2DP for audio) would need a separate module or different MCU. **Affects MCU selection.**
4. **Tethering / data mode** — Cellular module must support data connections (not just voice). SIM7600 supports data via CMUX+PPP (not AT+NETOPEN, which has a firmware bug with IMS context). Simultaneous VoLTE+data is not required — pause-data-during-call is acceptable. **Affects module selection.**
5. **Storage access via USB** — Phone should expose SD card or internal storage to connected modules. MCU USB stack must support mass storage class. **Affects firmware architecture.**

## Component Selection Summary (Informed by Wishlist)

When selecting components, ensure these capabilities are available (even if not used in MVP):

| Capability | Needed For | Priority |
|-----------|-----------|----------|
| USB device mode on MCU | Data transfer, ecosystem | 8 — must have |
| SPI or SDIO on MCU | MicroSD card slot | 7 — must have |
| Module with built-in GNSS | GPS, ecosystem (car nav) | 6 — strong want |
| BLE on MCU (or external BT module) | Bluetooth, ecosystem wireless | 6 — strong want |
| I2S or audio DAC on MCU | MP3 playback, audio output | 6 — strong want |
| Camera interface (SPI/parallel) | Photo capture | 6 — strong want |
| Module supports data + tethering | Hotspot, ecosystem | 6 — strong want (simultaneous VoLTE+data NOT required — pause-data acceptable) |
| Color display | Camera preview, photos | 5-6 — **SELECTED: ST7789V SPI TFT, 2.0" 240×320, RGB565** (satisfies "no 5+ blocked"; see research-notes.md Display Options) |
| FM radio in module | FM radio | 4 — nice to have |
| Wi-Fi capability | OTA updates | 4 — nice to have |
