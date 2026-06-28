# Research Notes

## Cellular Communication Primer

### How Phone Calls Work (Simplified)

1. **Your device** (phone) communicates with a **cell tower** (base station) over a radio link using a cellular standard (GSM, UMTS, LTE, NR).
2. The cell tower connects to the carrier's **core network**, which routes the call to the recipient's carrier network, which routes to the recipient's nearest cell tower, which radios to the recipient's phone.
3. For voice, the audio is digitized, compressed with a **voice codec** (e.g., AMR for 3G/LTE), packetized, and transmitted over the air interface.
4. Your device authenticates to the network using credentials stored on the **SIM card** (which contains your IMSI, keys, etc.).

### What a Cellular Module Does

A cellular module (e.g., Quectel EC25, SIMCom SIM7600) is essentially a self-contained modem:
- Handles the entire radio protocol stack (L1/L2/L3).
- Manages network registration, authentication (via SIM), call setup/teardown.
- Exposes a control interface to your microcontroller via **AT commands** (text-based commands over UART).
- Has an audio interface for connecting microphone/speaker directly (analog or digital PCM/I2S).
- Requires an antenna (usually external, connected via U.FL connector or PCB trace).

### AT Commands — The Interface

Your MCU sends text commands to the module over UART. Examples:
```
AT              -> Module responds "OK" (basic check)
ATD+1234567890; -> Dial a number
ATA             -> Answer incoming call
ATH             -> Hang up
AT+CSQ          -> Query signal quality
AT+CREG?        -> Query network registration status
AT+CMGS="..."   -> Send SMS
```

The module sends **unsolicited result codes (URCs)** for events:
```
RING            -> Incoming call
+CMGS: <n>      -> SMS sent successfully
+CREG: 1        -> Registered on network
```

Your firmware must parse these asynchronously — the module can send URCs at any time.

### Network Generation Comparison

| Generation | Voice Tech | Status (US) | Module Cost | Complexity |
|-----------|-----------|-------------|------------|------------|
| 2G (GSM)  | Circuit-switched | **Shut down** | $5-15 | Lowest |
| 3G (UMTS) | Circuit-switched | **Shutting down** | $10-25 | Low |
| 4G (LTE)  | VoLTE | **Active** | $15-40 | Medium-High |
| 5G (NR)   | VoNR | Active (limited) | $40+ | High |

**Key insight**: For a usable phone in the US, **LTE is the realistic choice**. 2G/3G are dead or dying. LTE voice (VoLTE) is more complex but modules like the Quectel EC25/EG25-G handle the VoLTE stack internally — you still just use AT commands for call control.

### Module Candidates (Initial List)

| Module | Network | Voice | Interface | Cost | Notes |
|--------|---------|-------|-----------|------|-------|
| SIM800L | 2G only | Yes | UART | ~$5 | Cheap but 2G is dead in US |
| SIM900 | 2G only | Yes | UART | ~$10 | Same issue |
| SIM5320 | 3G | Yes | UART | ~$20 | 3G also sunsetting |
| Quectel EG25-G | LTE Cat 4 | VoLTE | UART/USB | ~$25-35 | Good balance, well-documented |
| Quectel EC25 | LTE Cat 4 | VoLTE | UART/USB | ~$30-40 | Similar to EG25, more variants |
| SIMCom SIM7600 | LTE | VoLTE | UART/USB | ~$25-35 | Popular, good community support |

**Recommendation to investigate**: Quectel EG25-G or SIMCom SIM7600 — both are LTE, support VoLTE, well-documented, and have good community/hobbyist support.

### SIM Cards

- Standard SIM, Micro-SIM, or Nano-SIM — module breakout boards usually accept a specific size.
- Need an **active SIM** from a carrier. For testing, a prepaid plan (e.g., T-Mobile, Mint Mobile) is cheapest.
- Some carriers require the device's IMEI to be registered. The module has a built-in IMEI.
- **Potential gotcha**: Some carriers block non-approved devices. Usually not an issue with prepaid.

## MCU Candidates

| MCU | UARTs | Low Power | Cost | Notes |
|-----|-------|-----------|------|-------|
| STM32F4 series | 4-6 | Good | $5-10 | Well-supported (HAL/LL), lots of peripherals |
| STM32L4 series | 3-5 | Excellent | $5-10 | Low-power optimized, good for battery device |
| ESP32 | 3 | Moderate | $3-5 | Has Wi-Fi/BT (overkill?), lots of community support |
| nRF52840 | 2-4 | Excellent | $5-8 | Great low-power, BLE if needed, Zephyr RTOS support |

**Consideration**: ESP32 is tempting (cheap, huge community) but power management is weaker than STM32L4. For a battery device, STM32L4 or nRF52 might be better. Need to evaluate peripheral count vs needs.

## Display Options

| Type | Interface | Power | Cost | Notes |
|------|-----------|-------|------|-------|
| OLED (0.96"-1.3") | I2C/SPI | Low | $3-8 | Good contrast, small, easy to drive |
| TFT LCD (1.4"-1.8") | SPI | Medium | $5-10 | Color, decent resolution |
| Monochrome LCD | SPI/I2C | Very low | $3-6 | Classic phone look, very low power |

**Consideration**: A small OLED or monochrome LCD fits the flip phone aesthetic and keeps power/cost down.

## Open Research Questions

- [ ] Does VoLTE "just work" via AT commands on Quectel/SIMCom modules, or is there significant configuration?
- [ ] Which carriers allow VoLTE on non-certified devices with prepaid SIMs?
- [ ] Can we use the module's built-in audio path (analog mic/speaker pins) or do we need an external codec?
- [ ] What's the minimum antenna design for LTE? Can we use a small chip antenna or stamped antenna?
- [ ] Flex cable: standard FPC connectors and ribbon types that survive hinge bending?
- [ ] Are there any open-source flip phone projects we can reference?
