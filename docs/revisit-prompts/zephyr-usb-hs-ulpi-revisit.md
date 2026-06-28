# Revisit Prompt: Zephyr USB High-Speed via ULPI on STM32H7

**Purpose**: Paste the prompt below into a new chat to validate whether Zephyr's USB stack actually supports USB High-Speed via an external ULPI transceiver (USB3300) on the STM32H743. This is the ecosystem tethering path, and if it's not mature, the architecture needs adjustment.

---

## Prompt to paste into new chat:

I'm working on a custom cell phone project (STM32H743ZI in LQFP-144 + Zephyr RTOS + SIMCom SIM7600 LTE module + custom PCB). The full project docs are in the `docs/` folder — please read them before responding, especially `research-notes.md` (MCU selection, USB HS/ULPI clarification, and Package Selection sections) and `project-log.md` (MCU Selection decision).

## The situation

The phone is envisioned as the hub of a personal device ecosystem. The primary interconnect is USB — the phone acts as a **USB device**, and a future module (e.g., a car infotainment system) acts as USB host. The phone exposes LTE tethering to the module via USB CDC ECM (Ethernet-over-USB), which is a built-in Zephyr USB function.

The catch: real-world LTE throughput is 20–50 Mbps, but **USB Full-Speed (FS) caps at 12 Mbps** — a bottleneck. The STM32H743 has a second USB controller (OTG_HS) that can do **USB High-Speed (480 Mbps)**, but it requires an **external ULPI transceiver** (e.g., USB3300, ~$2) connected via 12 dedicated pins. The LQFP-144 package was chosen specifically to expose these ULPI pins (the LQFP-100 doesn't).

Our docs claim Zephyr has "mature" STM32H7 USB support, citing multiple H7 boards in mainline Zephyr. But I'm worried this conflates **USB OTG_FS** (which is well-tested) with **USB OTG_HS via external ULPI** (which may be much less tested or unsupported).

## What I need from you:

1. Read the docs first for full context on the ecosystem vision and the USB HS rationale.
2. **Determine the actual state of Zephyr's STM32H7 USB OTG_HS + ULPI support:**
   - Search the Zephyr source tree, Zephyr GitHub issues, Zephyr Discord/forum archives, and any blog posts.
   - Is there a `CONFIG_USB_DC_STM32` option or similar that enables HS via ULPI on the H7? Or does the STM32 USB driver only support the FS PHY?
   - Are there any mainline Zephyr boards that use USB HS via ULPI on an STM32H7? (Check `boards/` in the Zephyr repo.)
   - What's the most recent Zephyr version, and has ULPI support been added or improved recently?
3. **If Zephyr ULPI support is inadequate, what are the fallbacks?**
   - Use USB FS (12 Mbps) and accept the tethering bottleneck — how bad is this in practice for the car module use case (navigation + music streaming)?
   - Contribute upstream Zephyr support for STM32H7 ULPI — how hard is this? (Is it a Kconfig/dts change, or does it need driver code?)
   - Use a different USB approach (e.g., a USB-to-Ethernet bridge chip like the LAN7800 on the phone side — but this adds a chip and may defeat the purpose).
   - Use the SIM7600's own USB interface directly for tethering (the module has a USB port) — does this bypass the MCU entirely for the tethering path?
4. **Check whether the SIM7600's USB port can be used for tethering** instead of routing through the MCU. The SIM7600 has both UART and USB interfaces. If the module's USB can connect directly to the car module (or via a USB hub/switch), the MCU's USB speed may not matter for tethering. This could change the architecture significantly.
5. Give me a clear recommendation:
   - Is USB HS via ULPI on Zephyr/STM32H7 viable, or should I plan around USB FS?
   - Should the PCB include the USB3300 footprint (as a "populate later if needed" option), or is it wasted board space?
   - Is there a better tethering architecture that avoids the MCU USB bottleneck entirely?
6. Update the docs (`research-notes.md`, `project-log.md`) with the conclusion — follow the doc maintenance rules in `AGENTS.md`.
