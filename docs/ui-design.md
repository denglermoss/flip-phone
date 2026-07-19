# UI Design

Phone UI specification — screen map, navigation, input model, and visual style. This is a living document: the screen map and input model are stable decisions; the visual style is explorative and evolves as we iterate on hardware.

## Screen Map

```
                    ┌──────────────┐
                    │  Idle/Dialer │ ← default screen
                    │  (digits,    │
                    │   status bar)│
                    └──────┬───────┘
                       D   │  (open menu)
                    ┌──────▼───────┐
                    │  Main Menu   │
                    │  • Contacts  │
                    │  • Messages  │
                    │  • Settings  │
                    └──┬─────┬──┬──┘
            ┌──────────┘     │  └──────────┐
            ▼                ▼             ▼
       ┌─────────┐     ┌──────────┐   ┌─────────┐
       │ Contacts│     │ Messages │   │Settings │
       │  list   │     │  list    │   │ (later) │
       └────┬────┘     └────┬─────┘   └─────────┘
            │               │
       A    │          A    │  (open conversation)
       (open)         (open)
            ▼               ▼
       ┌──────────┐   ┌─────────────┐
       │ Contact  │   │ Conversation│
       │ detail   │   │ (message    │
       │ Call/Txt/│   │  history)   │
       │ Edit/Del │   └──────┬──────┘
       └──────────┘          │
                        C (compose)
                             ▼
                       ┌──────────┐
                       │ Compose  │
                       │ SMS      │
                       └──────────┘

  ── Overlay screens (appear on top, any state) ──
  ┌──────────────┐  ┌──────────────┐
  │ Incoming call│  │ In-call      │
  │ Answer/Reject│  │ Connected    │
  └──────────────┘  │ Hang up      │
                    └──────────────┘
```

### Screen descriptions

| Screen | When | Content | Status |
|--------|------|---------|--------|
| Idle / Dialer | Default | Typed digits (large), status bar, soft-key hints | Exists (needs HUD restyle) |
| In-call | Outgoing/incoming/connected | Call state, number, timer, hang-up hint | Exists (needs HUD restyle) |
| Incoming call | RING URC | "INCOMING", caller number, answer/reject hints | Exists (needs HUD restyle) |
| Main menu | D from dialer | List: Contacts, Messages, Settings | Planned |
| Contacts list | Menu → Contacts | Scrollable list of contacts | Planned |
| Contact detail | Contacts list → A | Name, number, actions (Call/Txt/Edit/Delete) | Planned |
| Contact add/edit | Contact detail → Edit | Form: name + number entry | Planned |
| Messages list | Menu → Messages | List of conversations (contact + last message preview) | Planned |
| Conversation | Messages list → A | Message history with a contact | Planned |
| SMS compose | Conversation → C | Recipient + message text entry | Planned |
| Settings | Menu → Settings | Sub-menus (network, audio, about) — deferred | Future |

## Persistent Elements

Three zones on the 240×320 display:

### Status bar (top, ~24px)
- **Signal**: segmented bars (vector-style, not smooth) — 5 segments
- **Battery**: segmented block or percentage
- **Time**: from NITZ (network time sync via SIM7600) — for now, uptime or static
- **Network**: carrier name ("MINT") or status
- Shown on all screens except in-call (which goes full-screen for number + timer)

### Content area (middle, ~256px)
- Screen-specific content
- Dialer: typed digits, large
- Menu: scrollable list
- In-call: call state + number + timer

### Soft-key labels (bottom, ~40px)
- Context-dependent hints for A/B/C/D
- All-caps, boxed slots (HUD style)
- Example: dialer shows "A: CALL | B: END | C: BKSP | D: MENU"
- Menu shows "A: SELECT | B: BACK | 2/8: SCROLL"

## Input Model

Prototype 4×4 keypad (final PCB will have dedicated nav keys in a 5×4 matrix).

| Key | Dialer | Menu | In-call | Incoming |
|-----|--------|------|---------|----------|
| 0-9, *, # | Append digit | — | — | — |
| A | Call (if digits entered) | Select item | — | Answer |
| B | — (nothing to end) | Back | Hang up | Reject |
| C | Backspace | — | — | — |
| D | Open menu | — | — | — |
| 2 | — | Scroll up | — | — |
| 8 | — | Scroll down | — | — |

Nokia-style menu navigation (2=up, 8=down) — digits double as nav keys in menu context. A=select, B=back. This is a prototype mapping; the final PCB's dedicated nav keys will replace it.

## Visual Style — In Progress (Explorative)

**Starting point: 80s sci-fi HUD** — chosen 2026-07-18. This is an explorative starting point, not a final spec. We build the idle/dialer screen in this style, see it on hardware, and iterate.

### Direction
- **Color**: amber/orange on black (primary amber ~#FFB000, dim amber for inactive elements)
- **Typography**: all-caps labels, monospace or techy sans-serif
- **Borders**: chunky, visible — not thin dividers
- **Highlight**: high-contrast (bright amber on black for selected, dim amber for unselected)
- **Icons**: vector-style line art (signal bars, battery blocks) — no filled bitmaps
- **Accents**: warning-stripe patterns (yellow/black diagonal) at key framing edges — to be added later
- **Vibe**: Aliens, Star Wars, Soviet space program. Utilitarian, industrial, chunky.

### Not yet decided (will evolve on hardware)
- Exact amber shade (may shift toward orange or yellow after seeing it)
- Font choice (monospace vs. Montserrat all-caps)
- Warning-stripe placement and scale
- Status bar icon style (segmented blocks vs. smooth bars)
- Animation / transitions (scanline sweep, blink, etc.)
- Whether to add a second accent color (red for warnings, green for "active")

## Implementation Notes

- **Framework**: LVGL (already integrated — `CONFIG_LVGL=y` in prj.conf)
- **Display**: ST7789V 2.0" 240×320 RGB565 on SPI1
- **Fonts**: currently Montserrat 28. May switch to monospace or add additional sizes for the HUD style.
- **Contact storage**: Zephyr settings subsystem (key-value in existing 256KB `storage_partition`). Simplest for now — migrate to littlefs later when we need SMS archives / call logs / hundreds of contacts.
- **SMS**: SIM7600 has its own message store (read on demand via `AT+CMGR` after `+CMTI` URC). No MCU-side SMS storage initially.

## Decisions Log

- **2026-07-18**: UI design session. Full screen map committed (idle/dialer, menu, contacts list/detail/add-edit, messages list/conversation/compose, settings, in-call, incoming). Input model: 2/8 as up/down in menus (Nokia-style), A=select, B=back. Visual style: 80s sci-fi HUD (amber/orange on black) as explorative starting point. Contact storage: Zephyr settings subsystem (simplest for now). See `docs/project-log.md` 2026-07-18 UI Design Session.
