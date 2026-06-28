# Revisit Prompt: Codec / Audio Path Architecture (PCM + I2S)

**STATUS: RESOLVED & LOCKED 2026-06-28** — Revisit conducted. **MAX9880A** dual-port codec selected.

**Outcome**: The original claim that a single common codec (WM8960, NAU8810) "unifies" PCM voice and I2S music into one audio path was **false** — all common codecs have only one digital audio port. The **MAX9880A** (Maxim/ADI, TQFN-48, ~$1.70) is the only hobbyist-accessible dual-port codec: primary port accepts PCM from SIM7600 (voice), secondary port accepts I2S from STM32H743 (music), both simultaneously. **MCU is NOT in the voice audio path during calls.** The SIM7600 outputs PCM only (fixed, no I2S mode). Fallback: MCU bridge with NAU8822 if MAX9880A unavailable. Pre-PCB verification: PCM short-frame sync support, stock availability, 1.8V level shifting. HAT prototyping unchanged. See project-log.md 2026-06-28 Codec Selection and research-notes.md Codec Selection section.

---

**Purpose**: Paste the prompt below into a new chat to revisit whether the selected codec architecture (single codec handling both PCM voice from the SIM7600 and I2S music from the MCU) is actually feasible, or whether the MCU needs to act as a real-time audio bridge.

---

## Prompt to paste into new chat:

I'm working on a custom cell phone project (STM32H743ZI + SIMCom SIM7600 LTE module + Zephyr RTOS + custom PCB). The full project docs are in the `docs/` folder — please read them before responding, especially `research-notes.md` (Architecture Decision section and the codec open question) and `feature-wishlist.md` (Media section).

## The question

Our architecture (Architecture A) selected a single audio codec (e.g., WM8960 or NAU8810) to handle **both**:
- **Voice**: PCM digital audio from the SIM7600 cellular module (during calls)
- **Music**: I2S from the STM32H743 MCU (MP3 playback, rated 6 on wishlist)

The rationale was that one codec "unifies" voice and music into a single audio path, avoiding the "two audio paths" problem that killed Architecture B (EG912U-GL with analog voice + separate DAC for music).

**The problem**: Most codecs I'm looking at (WM8960, NAU8810) appear to be **I2S-only** — they have one digital audio input interface, not two. The SIM7600 outputs **PCM** (not I2S) for voice. So the "single codec handles both" claim may not be literally true. There seem to be a few possible architectures:

1. **Codec with two digital audio inputs** (one PCM, one I2S) — does such a codec exist at hobbyist-friendly prices? (e.g., some TI TLV320 series?)
2. **MCU as audio bridge**: SIM7600 → PCM → STM32H743 (via SAI) → I2S → codec. The MCU reads PCM from the module and re-emits as I2S to the codec. Feasible on the H743 (it has 4× SAI), but it's a real-time audio bridging task with latency implications, and it means the MCU is in the voice audio path during every call.
3. **Switching/mux**: Codec has one I2S input; an analog or digital mux selects between module-PCM-converted-to-I2S and MCU-I2S. Clunky.
4. **Two codecs**: One small PCM codec for voice (module → codec → speaker), one I2S DAC for music (MCU → DAC → speaker). This is closer to the "two audio paths" we were trying to avoid — but maybe it's actually cleaner than a bridge?
5. **Module does the audio conversion**: Does the SIM7600 have any mode where it can output voice audio over I2S instead of PCM? (Check the AT command manual / datasheet.)

## What I need from you:

1. Read the docs first (`research-notes.md`, `feature-wishlist.md`, `project-log.md`) for full context on why we chose Architecture A.
2. **Determine whether WM8960, NAU8810, or any common codec actually supports two simultaneous digital audio inputs (PCM + I2S).** Check datasheets. If yes, this is easy. If no, the architecture needs adjustment.
3. **Check whether the SIM7600 can output voice over I2S** (not just PCM) — this would let us use a single I2S codec directly. Look at the SIM7600 AT command manual and hardware design manual.
4. **Evaluate the MCU-bridge option**: How hard is real-time PCM→I2S bridging on the STM32H743 under Zephyr? What's the latency? Does it interfere with the concurrent load (modem AT commands, UI, etc.)? Is there Zephyr support for this, or is it custom DMA work?
5. **Evaluate the two-codec option**: Is it actually worse than a bridge? Voice codec (e.g., a simple PCM codec like the NAU8810 on the Waveshare HAT) + music DAC (e.g., PCM5102) — how does the BOM cost, PCB complexity, and firmware complexity compare?
6. Give me a clear recommendation: which audio architecture should we use, and why. If "test first," tell me what to test on the Waveshare HAT (which has a NAU8810 wired to the SIM7600's PCM interface).
7. Update the docs (`research-notes.md`, `project-log.md`) with the conclusion — follow the doc maintenance rules in `AGENTS.md`.
