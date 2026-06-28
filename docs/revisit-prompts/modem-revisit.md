# Revisit Prompt: Cellular Module Selection

**Purpose**: Paste the prompt below into a new chat to revisit the cellular module decision. This collects several related concerns that surfaced during the 2026-06-28 documentation review.

**STATUS: RESOLVED & LOCKED 2026-06-28** (two rounds) — Revisit conducted twice. SIM7600 selection **locked**.

**First round**: SIM7600 confirmed. Two changes adopted: (1) prototyping HAT switched to SIM7600NA-H (resolves B71 validation gap); (2) simultaneous VoLTE+data designated as first HAT test. Standby power figure corrected (17.5 mA idle/DRX, not 3 mA). NFR-3 updated for LGA assembly reality.

**Second round (full re-evaluation)**: Deeper re-evaluation confirmed SIM7600 and locked the decision:
- **LARA-R6401 DISQUALIFIED** — 911/E911 not supported (datasheet: "The 911 and E911 services are not supported"). Hard safety disqualifier for a phone.
- **EC25-AF evaluated** as Quectel alternative — T-Mobile voice certified (unlike EG25-G which is data-only), B71, optional GNSS, 911/eCall supported, multi-PDP with IMS auto-isolated. But: no breakout with codec (slower prototyping), higher idle current (23.3 mA vs 17.5 mA). Documented as PCB fallback if SIM7600 HAT testing reveals a blocking issue.
- **EG25-G T-Mobile VoLTE clarified** — not a hardware limitation; T-Mobile certifies EG25-G for data only, not voice. EC25-AF is the proper Quectel alternative.
- **PDP context conflict RESOLVED** — confirmed in `AT+NETOPEN` code path only. Project uses CMUX+PPP (`ATD*99***<cid>#`), which bypasses it. CMUX+PPP is the standard documented pattern (Linux n_gsm, RT-Thread, ESP-IDF).
- **Simultaneous VoLTE+data is NOT a requirement** — not needed for MVP or daily driver. "Pause data during call" is acceptable for the future ecosystem too. Dropped as a modem selection factor.

See `docs/project-log.md` (2026-06-28 Modem Revisit Second Round) and `docs/research-notes.md` (Modem Revisit Findings, Second Round) for full details. The prompt below is retained for reference only.

---

## Prompt to paste into new chat:

I'm working on a custom cell phone project (STM32H743ZI + Zephyr RTOS + custom PCB, targeting US LTE with VoLTE on T-Mobile/Mint). The full project docs are in the `docs/` folder — please read them before responding.

We selected the **SIMCom SIM7600 series** (SIM7600G-H for prototyping on a Waveshare HAT, SIM7600A-H for the final PCB) over the Quectel EG25-G and other candidates. I want to revisit this selection because several concerns came up during a documentation review. Please help me evaluate whether the SIM7600 is still the right choice, or whether we should reconsider. The specific concerns:

### 1. Standby power / receive-call current (CRITICAL)
Our docs previously cited the SIM7600's "3 mA sleep" figure to argue that the modem dominates standby power and the MCU sleep current is negligible. But I've learned that 3 mA is the **deep-sleep** state, in which the module **cannot receive incoming calls**. To receive calls (a hard requirement — FR-1.2), the module must stay registered on the network in LTE idle/DRX mode, which typically draws **10–50 mA**.

- What is the SIM7600's actual idle/DRX current on LTE? (Check the datasheet — look for "idle mode S-RX" or similar.)
- How does this compare to the EG25-G, EG912U-GL, and LARA-R6401 in the same idle/DRX state?
- With the real idle current, what battery capacity do I need for the 24h standby target (FR-4.4)? Is 24h still realistic?
- What DRX cycle configuration options does the SIM7600 expose, and how much can power be reduced by extending the DRX cycle? What's the tradeoff (call setup latency)?

### 2. B71 validation gap
The Waveshare HAT uses the SIM7600**G-H** (no B71 — T-Mobile 600 MHz Extended Range LTE), but the final PCB will use the SIM7600**A-H** (has B71). B71 is one of the key reasons we chose SIM7600 over EG25-G. This means my Phase 1 VoLTE validation on the HAT **cannot test B71 performance**.

- How important is B71 in my area? (I'll provide my location — help me figure out whether T-Mobile 600 MHz is load-bearing for coverage here.)
- Is there a SIM7600A-H breakout board available with audio codec, equivalent to the Waveshare HAT? If not, what's the cheapest path to validate B71 before committing to a custom PCB?
- If B71 can't be validated early, how much risk does that add? Is there a fallback (e.g., external antenna tuned for B71)?

### 3. Simultaneous VoLTE + data tethering (PDP context conflict)
The SIM7600 has a documented quirk: the IMS PDP context (cid=2 for VoLTE) can conflict with data (cid=1). This is critical for the ecosystem goal (phone provides LTE tethering to a car module via USB, potentially while on a call).

- Has anyone in the hobbyist/forums community gotten simultaneous VoLTE + data working on the SIM7600? Search forums (Quectel/SIMCom forums, Reddit, hackaday, etc.).
- How does the EG25-G handle this? Does it have the same PDP context limitation?
- Is there a module that handles simultaneous voice + data more cleanly? (LARA-R6401? Others?)
- This should be the **first** thing I test on the Waveshare HAT. What AT command sequence should I use to validate it?

### 4. Assembly method (LGA soldering)
The SIM7600 is LGA (land grid array) — not hand-solderable. My plan is solder paste + stencil + reflow (bake). NFR-3 in requirements.md says "hand-solderable for prototypes," which is partially unachievable for this module.

- Is the SIM7600's LGA footprint hobbyist-reflowable with a stencil + hot plate / oven? Or is JLCPCB assembly the only realistic path?
- How does this compare to the EG25-G's package? Is any candidate module available in a more hand-friendly package without sacrificing the LTE/VoLTE requirements?
- Should I just plan for JLCPCB assembly for the modem section and hand-solder the rest? What's the cost impact?

### What I need from you:
1. Read all the docs in `docs/` first (especially `research-notes.md` and `project-log.md`) so you have full context.
2. Research the actual idle/DRX current figures for the SIM7600 vs alternatives from datasheets or reliable sources.
3. Give me a clear recommendation: stick with SIM7600, or switch, and why. If "it depends," tell me what it depends on and what I should test first.
4. Update the docs (`research-notes.md`, `project-log.md`, `constraints.md`) with whatever we conclude — follow the doc maintenance rules in `AGENTS.md`.
