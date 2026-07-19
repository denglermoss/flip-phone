/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * main.c — Phone firmware entry point
 *
 * VoLTE phone with display: places/receives calls via AT commands to
 * the SIM7600 modem, and shows call status on the ST7789V display.
 *
 * Architecture:
 *   - ISR (interrupt service routine): fires when the UART hardware
 *     receives a character. Reads from the hardware FIFO into a ring
 *     buffer. Runs in interrupt context — must be fast, no sleeping,
 *     no logging, no blocking.
 *   - Ring buffer: a circular queue. ISR writes to the tail, app
 *     reads from the head. Single-producer (ISR) / single-consumer
 *     (app) = no locking needed.
 *   - Application code: reads from the ring buffer with timeout.
 *     Can sleep while waiting (k_msleep) — no CPU spinning. This is
 *     the key advantage over polling: the app can do other work
 *     (render UI, process keypad) and the ISR catches every character
 *     that arrives, including async URCs like incoming-call notifications.
 *   - Display: ST7789V 2.0" 240×320 TFT on SPI1. LVGL renders text
 *     labels for call status (state, phone number, info line).
 *
 * Hardware connection (Waveshare HAT → Nucleo):
 *   HAT TXD  →  Nucleo PB7  (LPUART1_RX, Arduino D0)
 *   HAT RXD  →  Nucleo PB6  (LPUART1_TX, Arduino D1)
 *   HAT GND  →  Nucleo GND
 *
 * Display connection (Waveshare 2" LCD → Nucleo Arduino header):
 *   LCD VCC → 3.3V
 *   LCD GND → GND
 *   LCD DIN → D11 (PB5, SPI1 MOSI)
 *   LCD CLK → D13 (PA5, SPI1 SCK)
 *   LCD CS  → D10 (PD14, SPI1 CS)
 *   LCD DS  → D9  (PD15, Data/Command)
 *   LCD RST → D8  (PF3,  Reset)
 *   LCD BL  → D7  (PG12, Backlight)
 *
 * Keypad connection (Adafruit 4×4 membrane → Nucleo Arduino header):
 *   R1 → D3  (PE13, row 0)    C1 → A1  (PC0,  col 0)
 *   R2 → D4  (PE14, row 1)    C2 → A2  (PC3,  col 1)
 *   R3 → D5  (PE11, row 2)    C3 → A3  (PB1,  col 2)
 *   R4 → D6  (PE9,  row 3)    C4 → D2  (PG14, col 3)
 *
 * The Waveshare HAT has an onboard voltage translator (1.8V ↔ 3.3V).
 * On the final custom PCB, a TXB0108 will be needed between the
 * STM32H743 and the SIM7600A-H raw module pins.
 */

#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/uart.h>
#include <zephyr/drivers/display.h>
#include <zephyr/sys/ring_buffer.h>
#include <zephyr/logging/log.h>
#include <zephyr/input/input.h>
#include <zephyr/dt-bindings/input/input-event-codes.h>
#include <lvgl.h>
#include <stdio.h>
#include <string.h>

/* JetBrains Mono — custom LVGL bitmap fonts converted from the TTF
 * (see src/fonts/ and CMakeLists.txt). Three sizes:
 *   jetbrainsmono_10 — status bar (signal, time, battery)
 *   jetbrainsmono_14 — content, softkeys, menu, state labels
 *   jetbrainsmono_22 — dialer number, incall timer (hero content, bold) */
LV_FONT_DECLARE(jetbrainsmono_10);
LV_FONT_DECLARE(jetbrainsmono_14);
LV_FONT_DECLARE(jetbrainsmono_22);

LOG_MODULE_REGISTER(phone, LOG_LEVEL_INF);

/* LPUART1 is already configured in the board devicetree
 * (nucleo_h753zi.dts) at 115200 baud on PB6 (TX) / PB7 (RX). */
#define MODEM_UART_NODE DT_NODELABEL(lpuart1)

#define RX_RING_BUF_SIZE 1024
#define RESPONSE_TIMEOUT_MS 5000
#define RESPONSE_GAP_TIMEOUT_MS 500

static const struct device *modem_uart;

/* Ring buffer for received data.
 * The ISR writes incoming characters here; the application reads
 * them out. This decouples the fast ISR from the slower app code. */
RING_BUF_DECLARE(rx_ringbuf, RX_RING_BUF_SIZE);

/* UART interrupt service routine.
 * This runs in interrupt context — not a normal thread. It preempts
 * whatever the CPU was doing and must return quickly. Rules:
 *   - No sleeping (k_sleep, k_msleep — would crash)
 *   - No logging (LOG_INF — too slow, can deadlock)
 *   - No blocking calls
 *   - Just grab the data and get out
 *
 * Flow:
 *   1. uart_irq_update() — refresh the IRQ status (must call first)
 *   2. uart_irq_rx_ready() — check if RX data is available
 *   3. uart_fifo_read() — pull bytes from the hardware FIFO
 *   4. ring_buf_put() — store them in the ring buffer
 *
 * We read in chunks (up to 32 bytes at a time) because the UART FIFO
 * may have accumulated multiple characters between interrupts. */
static void modem_uart_isr(const struct device *dev, void *user_data)
{
    ARG_UNUSED(user_data);

    uart_irq_update(dev);

    if (uart_irq_rx_ready(dev)) {
        uint8_t read_buf[32];
        int len;

        /* Drain the hardware FIFO — keep reading until it's empty.
         * If we only read once, characters that arrived between
         * interrupts would be lost when the next byte overwrites
         * the FIFO. */
        while ((len = uart_fifo_read(dev, read_buf, sizeof(read_buf))) > 0) {
            ring_buf_put(&rx_ringbuf, read_buf, len);
        }
    }
}

/* Drain any pending data from the ring buffer.
 * Call this before sending a command to discard stale data. */
static void modem_drain(void)
{
    uint8_t tmp[64];
    while (ring_buf_get(&rx_ringbuf, tmp, sizeof(tmp)) > 0) {
        /* discard */
    }
}

/* Send a string to the modem.
 * uart_poll_out is fine for TX — it's synchronous (we send a command
 * then wait for the response). TX doesn't need interrupts because
 * we're never sending data asynchronously. */
static void modem_send(const char *cmd)
{
    LOG_INF("TX> %s", cmd);
    for (size_t i = 0; cmd[i] != '\0'; i++) {
        uart_poll_out(modem_uart, cmd[i]);
    }
}

/* Read modem response from the ring buffer with timeout.
 * This is application-level code — runs in a normal thread context
 * and can sleep. Returns when:
 *   - Overall timeout expires (RESPONSE_TIMEOUT_MS)
 *   - We got data but no new chars for RESPONSE_GAP_TIMEOUT_MS
 *   - Buffer is full
 *
 * The key difference from polling: we sleep with k_msleep(1) instead
 * of k_busy_wait(50). The ISR is catching characters into the ring
 * buffer in the background, so we don't need to poll frantically.
 * We can sleep peacefully and check the buffer periodically. */
static int modem_read(char *buf, size_t buf_size)
{
    size_t pos = 0;
    int64_t start = k_uptime_get();
    int64_t last_char = start;

    while (pos < buf_size - 1) {
        uint8_t ch;

        if (ring_buf_get(&rx_ringbuf, &ch, 1) == 1) {
            buf[pos++] = (char)ch;
            last_char = k_uptime_get();
            continue;
        }

        /* No data available — sleep and check timeouts.
         * k_msleep(1) is fine here because the ISR is filling the
         * ring buffer in the background. We won't miss anything. */
        k_msleep(1);
        int64_t now = k_uptime_get();
        if (now - start > RESPONSE_TIMEOUT_MS) {
            break;
        }
        if (pos > 0 && now - last_char > RESPONSE_GAP_TIMEOUT_MS) {
            break;
        }
    }

    buf[pos] = '\0';
    return pos;
}

/* Send an AT command and log the response. */
static void modem_at(const char *cmd)
{
    char rx_buf[512];

    modem_drain();
    modem_send(cmd);
    int len = modem_read(rx_buf, sizeof(rx_buf));
    if (len > 0) {
        LOG_INF("RX< %s", rx_buf);
    } else {
        LOG_WRN("No response (timeout %d ms)", RESPONSE_TIMEOUT_MS);
    }
    k_msleep(200);
}

/* Read a complete line from the ring buffer (terminated by \n).
 * Returns the line length (excluding null terminator), or 0 on timeout.
 * This is used in the URC monitor loop to process one line at a time. */
static int modem_readline(char *buf, size_t buf_size, int timeout_ms)
{
    size_t pos = 0;
    int64_t start = k_uptime_get();

    while (pos < buf_size - 1) {
        uint8_t ch;

        if (ring_buf_get(&rx_ringbuf, &ch, 1) == 1) {
            buf[pos++] = (char)ch;
            if (ch == '\n') {
                break;
            }
            continue;
        }

        k_msleep(1);
        if (k_uptime_get() - start > timeout_ms) {
            break;
        }
    }

    buf[pos] = '\0';
    return pos;
}

/* Strip trailing \r\n from a line for cleaner logging. */
static void strip_crlf(char *s)
{
    size_t len = strlen(s);
    while (len > 0 && (s[len - 1] == '\r' || s[len - 1] == '\n')) {
        s[--len] = '\0';
    }
}

/* URC (unsolicited result code) monitor loop.
 *
 * After placing a call, the modem sends async notifications:
 *   "VOICE CALL: BEGIN\r\n"   — call connected
 *   "VOICE CALL: END: xxxxxx\r\n" — call ended (6-digit reason code)
 *   "RING\r\n"                — incoming call ringing
 *
 * This loop reads lines from the ring buffer and acts on them:
 *   - RING → automatically answer with ATA
 *   - VOICE CALL: BEGIN → log call connected
 *   - VOICE CALL: END → log call ended, exit loop
 *   - Anything else → log it (echoes, OK, etc.)
 *
 * This is the first real use of the interrupt-driven UART for async
 * events — the modem sends these at any time, and the ring buffer
 * catches them while we sleep in modem_readline(). */
/* --- Call state machine ---
 *
 * The phone is a state machine driven by two inputs:
 *   1. Keypad keys (via the gpio-kbd-matrix input driver → callback →
 *      key_msgq → main loop)
 *   2. Async URCs from the modem (RING, VOICE CALL: BEGIN/END)
 *
 * States:
 *   PHONE_IDLE     — waiting, display "Idle", digits accumulate in dial
 *                    string, A → place call (ATD<string>;)
 *   PHONE_CALLING  — outgoing call in progress, display "Calling..."
 *                    B → cancel (AT+CHUP), URC BEGIN → connected
 *   PHONE_RINGING  — incoming call, display "Incoming call"
 *                    A → answer (ATA), B → reject (AT+CHUP),
 *                    URC BEGIN → connected
 *   PHONE_CONNECTED — call active, display "Connected"
 *                     B → hang up (AT+CHUP), URC END → idle
 *
 * The keypad driver runs in its own thread and emits input events to
 * our callback, which queues key characters into key_msgq. The main
 * loop drains the queue and calls handle_key(). The modem URCs come
 * through the ring buffer (modem_readline).
 *
 * The main loop polls both: drain key_msgq, read a line from the modem
 * with a short timeout, then act based on current state.
 * lv_timer_handler() is called each iteration to keep LVGL rendering. */

#define DIAL_STRING_MAX 20

enum phone_state {
    PHONE_IDLE,
    PHONE_CALLING,
    PHONE_RINGING,
    PHONE_CONNECTED,
};

static enum phone_state call_state = PHONE_IDLE;

/* UI screen state — separate from call state. Call states (CALLING,
 * RINGING, CONNECTED) override the screen regardless of ui_screen.
 * When IDLE, ui_screen determines what's shown.
 *   UI_DIALER         — idle/dialer (digits, call, menu access)
 *   UI_MENU           — main menu (Contacts, Messages, Settings)
 *   UI_CONTACTS       — contacts list (scroll, open)
 *   UI_CONTACT_DETAIL — contact name + number + actions (Call/Text/Edit/Delete)
 *   UI_MESSAGES       — conversations list (scroll, open)
 *   UI_CONVERSATION   — message thread with a contact
 *   UI_COMPOSE        — SMS text entry (mock — doesn't actually send) */
enum ui_screen {
    UI_DIALER,
    UI_MENU,
    UI_CONTACTS,
    UI_CONTACT_DETAIL,
    UI_MESSAGES,
    UI_CONVERSATION,
    UI_COMPOSE,
};

static enum ui_screen ui_screen = UI_DIALER;

/* --- Mock data (matches ui-mockup/index.html) ---
 *
 * Contacts and messages are hardcoded arrays for now. Real persistence
 * (Zephyr settings subsystem) and real SMS (SIM7600 AT+CMGS/CMGR) are
 * future features — this is the UI port with sample data. */
struct contact {
    const char *name;
    const char *number;  /* digits only, no spaces — ready for ATD */
};

static const struct contact contacts[] = {
    {"ALICE", "16075551234"},
    {"BOB",   "16075559876"},
    {"MOM",   "16075550001"},
    {"DAD",   "16075550002"},
    {"JEN",   "12125554242"},
};
#define CONTACT_COUNT (sizeof(contacts) / sizeof(contacts[0]))

struct message {
    bool from_me;       /* true = sent by us, false = received */
    const char *text;
};

struct conversation {
    const char *contact_name;
    const struct message *messages;
    int msg_count;
};

static const struct message alice_msgs[] = {
    {false, "hey, are you free tonight?"},
    {true,  "yeah, what's up?"},
    {false, "movie at 8?"},
    {true,  "sounds great"},
};
static const struct message bob_msgs[] = {
    {false, "did you finish the thing?"},
    {true,  "almost, tomorrow morning"},
};
static const struct message mom_msgs[] = {
    {false, "call me when you can"},
};

static const struct conversation conversations[] = {
    {"ALICE", alice_msgs, 4},
    {"BOB",   bob_msgs,   2},
    {"MOM",   mom_msgs,   1},
};
#define CONV_COUNT (sizeof(conversations) / sizeof(conversations[0]))

/* --- Navigation state --- */
static const char * const menu_items[] = {"CONTACTS", "MESSAGES", "SETTINGS"};
#define MENU_COUNT (sizeof(menu_items) / sizeof(menu_items[0]))
static int menu_index = 0;

static int contacts_index = 0;       /* scroll position in contacts list */
static int current_contact = 0;      /* which contact's detail we're viewing */
static int contact_action_index = 0; /* scroll position in contact detail actions */
static const char * const contact_actions[] = {"CALL", "TEXT", "EDIT", "DELETE"};
#define CONTACT_ACTION_COUNT 4

static int messages_index = 0;       /* scroll position in messages list */
static int current_conv = 0;         /* which conversation we're viewing */

/* Compose text — mock SMS entry. Digits append, C backspaces, A "sends"
 * (just adds to the conversation in RAM — no real AT+CMGS). */
static char compose_text[DIAL_STRING_MAX + 1];
static size_t compose_len;

/* --- Dial string + call timer --- */
/* Dial string — accumulated digits from the keypad. Displayed on the
 * hero label. When A is pressed, this is sent as ATD<string>;. */
static char dial_string[DIAL_STRING_MAX + 1];
static size_t dial_len;

/* Call timer — tracks elapsed seconds since call connected. Updated in
 * the main loop from k_uptime_get(). */
static int64_t call_start_time;
static int call_timer_seconds;

/* Keymap: maps (row, col) from the gpio-kbd-matrix driver to a
 * character. Layout matches the Adafruit 4×4 membrane keypad:
 *        C1  C2  C3  C4
 *   R1:  1   2   3   A
 *   R2:  4   5   6   B
 *   R3:  7   8   9   C
 *   R4:  *   0   #   D
 *
 * The driver emits INPUT_ABS_X=col, INPUT_ABS_Y=row (both 0-indexed),
 * then INPUT_BTN_TOUCH=1 (press) with sync=true. We capture col/row
 * on the ABS events and act on the BTN_TOUCH press event. */
static const char keymap[4][4] = {
    /* row 0 */ {'1', '2', '3', 'A'},
    /* row 1 */ {'4', '5', '6', 'B'},
    /* row 2 */ {'7', '8', '9', 'C'},
    /* row 3 */ {'*', '0', '#', 'D'},
};

/* Key event queue — passes key characters from the input callback
 * (runs in the input subsystem thread) to the main loop (which owns
 * LVGL and modem access). This avoids cross-thread LVGL/modem calls.
 * The callback just enqueues; the main loop drains and handles. */
K_MSGQ_DEFINE(key_msgq, sizeof(char), 16, 4);

/* Input callback — registered with INPUT_CALLBACK_DEFINE below.
 * Runs in the input subsystem thread context (not ISR, not main loop).
 * Must not touch LVGL or the modem UART directly — just queue the key. */
static void keypad_callback(struct input_event *evt, void *user_data)
{
    static int16_t last_col = -1;
    static int16_t last_row = -1;

    ARG_UNUSED(user_data);

    switch (evt->code) {
    case INPUT_ABS_X:
        last_col = evt->value;
        break;
    case INPUT_ABS_Y:
        last_row = evt->value;
        break;
    case INPUT_BTN_TOUCH:
        /* Act only on key press (value=1), not release (value=0).
         * sync=true marks the end of the (col, row, touch) triplet. */
        if (evt->value == 1 && evt->sync &&
            last_col >= 0 && last_col < 4 &&
            last_row >= 0 && last_row < 4) {
            char key = keymap[last_row][last_col];
            k_msgq_put(&key_msgq, &key, K_NO_WAIT);
        }
        break;
    default:
        break;
    }
}
INPUT_CALLBACK_DEFINE(DEVICE_DT_GET(DT_NODELABEL(kbd_matrix)),
                      keypad_callback, NULL);

/* --- LVGL UI ---
 *
 * LVGL (Light and Versatile Graphics Library) is Zephyr's standard UI
 * framework. It provides widgets (labels, buttons, images) and a
 * renderer that writes to the display via Zephyr's display API.
 *
 * lv_timer_handler() must be called every ~5-10ms for LVGL to process
 * animations and flush pixels to the display. The main loop calls it
 * every iteration (modem_readline timeout is short). */

static const struct device *display_dev;

/* UI color palette — TE-inspired industrial design with CRT surface.
 * Layered grey for depth (base + panels + raised), amber reserved for
 * content and active elements only. Grey borders separate zones without
 * amber doing double duty as both chrome and content.
 * Designed 2026-07-18 — see ui-mockup/index.html for the reference. */
#define UI_COLOR_BG            0x1A1A1A  /* base background (darkest) */
#define UI_COLOR_PANEL         0x262626  /* status bar / softkey bar panels */
#define UI_COLOR_PANEL_RAISED  0x303030  /* selected list items (future) */
#define UI_COLOR_BORDER        0x3A3A3A  /* subtle grey borders between zones */
#define UI_COLOR_BORDER_BRIGHT 0x4A4A4A  /* active/selected borders (future) */
#define UI_COLOR_AMBER         0xFFB000  /* primary amber — content only */
#define UI_COLOR_AMBER_BRIGHT  0xFFD000  /* bright amber — active content */
#define UI_COLOR_AMBER_DIM     0x8A6A00  /* dim amber — inactive content */

/* LVGL UI elements — three-zone layout with grey panels + grey borders:
 *   status_bar (top, 22px): signal | time | battery, grey panel
 *   content (middle): flexible labels shown/hidden per screen
 *   softkey_bar (bottom, 26px): A/B/C/D context hints, grey panel
 *
 * Content labels (all hidden by default, shown per screen by ui_render):
 *   title_label  — 14px, top of content (screen titles, call state labels)
 *   hero_label   — 22px bold, center of content (dial number, compose text, call number)
 *   list_label   — 14px, top-left below title (multi-line lists: menu, contacts, messages, actions)
 *   timer_label  — 22px, below hero (call timer on connected screen)
 *   cursor_label — small "_" that blinks, positioned after hero (dialer/compose only) */
static lv_obj_t *signal_label;
static lv_obj_t *time_label;
static lv_obj_t *battery_label;
static lv_obj_t *title_label;
static lv_obj_t *hero_label;
static lv_obj_t *list_label;
static lv_obj_t *timer_label;
static lv_obj_t *cursor_label;
static lv_obj_t *softkey_label;

/* --- Blinking cursor animation ---
 * Toggles cursor_label opacity between visible and transparent every 500ms.
 * Used on the dialer and compose screens to show the text entry position. */
static void cursor_anim_cb(void *obj, int32_t v)
{
    lv_obj_set_style_opa((lv_obj_t *)obj, (lv_opa_t)v, LV_PART_MAIN);
}

static void cursor_anim_start(void)
{
    lv_anim_t a;
    lv_anim_init(&a);
    lv_anim_set_var(&a, cursor_label);
    lv_anim_set_values(&a, LV_OPA_COVER, LV_OPA_TRANSP);
    lv_anim_set_time(&a, 500);
    lv_anim_set_playback_time(&a, 500);
    lv_anim_set_repeat_count(&a, LV_ANIM_REPEAT_INFINITE);
    lv_anim_set_exec_cb(&a, cursor_anim_cb);
    lv_anim_start(&a);
}

/* --- Master render function ---
 *
 * Hides all content labels, then shows + populates the ones needed for
 * the current screen (determined by call_state + ui_screen). Updates the
 * softkey bar. Called after any state change. */
static void ui_render(void)
{
    /* Hide all content labels first */
    lv_obj_add_flag(title_label, LV_OBJ_FLAG_HIDDEN);
    lv_obj_add_flag(hero_label, LV_OBJ_FLAG_HIDDEN);
    lv_obj_add_flag(list_label, LV_OBJ_FLAG_HIDDEN);
    lv_obj_add_flag(timer_label, LV_OBJ_FLAG_HIDDEN);
    lv_obj_add_flag(cursor_label, LV_OBJ_FLAG_HIDDEN);

    const char *softkeys = "";

    /* Call states override the UI screen */
    if (call_state == PHONE_CALLING) {
        lv_label_set_text(title_label, "CALLING...");
        lv_label_set_text(hero_label, dial_string);
        lv_obj_clear_flag(title_label, LV_OBJ_FLAG_HIDDEN);
        lv_obj_clear_flag(hero_label, LV_OBJ_FLAG_HIDDEN);
        softkeys = "B:CANCEL";
    } else if (call_state == PHONE_RINGING) {
        lv_label_set_text(title_label, "INCOMING");
        lv_label_set_text(hero_label, dial_string);
        lv_obj_clear_flag(title_label, LV_OBJ_FLAG_HIDDEN);
        lv_obj_clear_flag(hero_label, LV_OBJ_FLAG_HIDDEN);
        softkeys = "A:ANSWER  B:REJECT";
    } else if (call_state == PHONE_CONNECTED) {
        lv_label_set_text(title_label, "CONNECTED");
        lv_label_set_text(hero_label, dial_string);
        char timer_buf[16];
        int m = call_timer_seconds / 60;
        int s = call_timer_seconds % 60;
        snprintf(timer_buf, sizeof(timer_buf), "%02d:%02d", m, s);
        lv_label_set_text(timer_label, timer_buf);
        lv_obj_clear_flag(title_label, LV_OBJ_FLAG_HIDDEN);
        lv_obj_clear_flag(hero_label, LV_OBJ_FLAG_HIDDEN);
        lv_obj_clear_flag(timer_label, LV_OBJ_FLAG_HIDDEN);
        softkeys = "B:HANG UP";
    } else {
        /* PHONE_IDLE — render based on ui_screen */
        switch (ui_screen) {
        case UI_DIALER: {
            lv_label_set_text(hero_label, dial_string);
            lv_obj_clear_flag(hero_label, LV_OBJ_FLAG_HIDDEN);
            lv_obj_clear_flag(cursor_label, LV_OBJ_FLAG_HIDDEN);
            softkeys = "A:CALL  C:BKSP  D:MENU";
            break;
        }
        case UI_MENU: {
            lv_label_set_text(title_label, "MENU");
            char buf[64];
            char *p = buf;
            for (int i = 0; i < (int)MENU_COUNT; i++) {
                *p++ = (i == menu_index) ? '>' : ' ';
                *p++ = ' ';
                size_t len = strlen(menu_items[i]);
                memcpy(p, menu_items[i], len);
                p += len;
                *p++ = '\n';
            }
            *p = '\0';
            lv_label_set_text(list_label, buf);
            lv_obj_clear_flag(title_label, LV_OBJ_FLAG_HIDDEN);
            lv_obj_clear_flag(list_label, LV_OBJ_FLAG_HIDDEN);
            softkeys = "A:SELECT  B:BACK  2/8:SCROLL";
            break;
        }
        case UI_CONTACTS: {
            lv_label_set_text(title_label, "CONTACTS");
            char buf[128];
            char *p = buf;
            for (int i = 0; i < (int)CONTACT_COUNT; i++) {
                *p++ = (i == contacts_index) ? '>' : ' ';
                *p++ = ' ';
                size_t len = strlen(contacts[i].name);
                memcpy(p, contacts[i].name, len);
                p += len;
                *p++ = '\n';
            }
            *p = '\0';
            lv_label_set_text(list_label, buf);
            lv_obj_clear_flag(title_label, LV_OBJ_FLAG_HIDDEN);
            lv_obj_clear_flag(list_label, LV_OBJ_FLAG_HIDDEN);
            softkeys = "A:OPEN  B:BACK  2/8:SCROLL";
            break;
        }
        case UI_CONTACT_DETAIL: {
            const struct contact *c = &contacts[current_contact];
            lv_label_set_text(title_label, c->name);
            char buf[128];
            int n = snprintf(buf, sizeof(buf), "%s\n\n", c->number);
            char *p = buf + n;
            for (int i = 0; i < CONTACT_ACTION_COUNT; i++) {
                *p++ = (i == contact_action_index) ? '>' : ' ';
                *p++ = ' ';
                size_t len = strlen(contact_actions[i]);
                memcpy(p, contact_actions[i], len);
                p += len;
                *p++ = '\n';
            }
            *p = '\0';
            lv_label_set_text(list_label, buf);
            lv_obj_clear_flag(title_label, LV_OBJ_FLAG_HIDDEN);
            lv_obj_clear_flag(list_label, LV_OBJ_FLAG_HIDDEN);
            softkeys = "A:SELECT  B:BACK  2/8:SCROLL";
            break;
        }
        case UI_MESSAGES: {
            lv_label_set_text(title_label, "MESSAGES");
            char buf[256];
            char *p = buf;
            for (int i = 0; i < (int)CONV_COUNT; i++) {
                *p++ = (i == messages_index) ? '>' : ' ';
                *p++ = ' ';
                size_t len = strlen(conversations[i].contact_name);
                memcpy(p, conversations[i].contact_name, len);
                p += len;
                *p++ = '\n';
                /* Last message preview (indented) */
                const struct message *last =
                    &conversations[i].messages[conversations[i].msg_count - 1];
                *p++ = ' ';
                *p++ = ' ';
                if (last->from_me) {
                    memcpy(p, "me: ", 4);
                    p += 4;
                }
                len = strlen(last->text);
                if (len > 24) len = 24;  /* truncate preview */
                memcpy(p, last->text, len);
                p += len;
                *p++ = '\n';
            }
            *p = '\0';
            lv_label_set_text(list_label, buf);
            lv_obj_clear_flag(title_label, LV_OBJ_FLAG_HIDDEN);
            lv_obj_clear_flag(list_label, LV_OBJ_FLAG_HIDDEN);
            softkeys = "A:OPEN  B:BACK  2/8:SCROLL";
            break;
        }
        case UI_CONVERSATION: {
            const struct conversation *conv = &conversations[current_conv];
            lv_label_set_text(title_label, conv->contact_name);
            char buf[256];
            char *p = buf;
            for (int i = 0; i < conv->msg_count; i++) {
                const struct message *m = &conv->messages[i];
                /* "< " prefix for incoming, "> " for outgoing */
                *p++ = m->from_me ? '>' : '<';
                *p++ = ' ';
                size_t len = strlen(m->text);
                if (len > 30) len = 30;
                memcpy(p, m->text, len);
                p += len;
                *p++ = '\n';
            }
            *p = '\0';
            lv_label_set_text(list_label, buf);
            lv_obj_clear_flag(title_label, LV_OBJ_FLAG_HIDDEN);
            lv_obj_clear_flag(list_label, LV_OBJ_FLAG_HIDDEN);
            softkeys = "C:COMPOSE  B:BACK";
            break;
        }
        case UI_COMPOSE: {
            const struct conversation *conv = &conversations[current_conv];
            char title_buf[32];
            snprintf(title_buf, sizeof(title_buf), "TO: %s", conv->contact_name);
            lv_label_set_text(title_label, title_buf);
            lv_label_set_text(hero_label, compose_text);
            lv_obj_clear_flag(title_label, LV_OBJ_FLAG_HIDDEN);
            lv_obj_clear_flag(hero_label, LV_OBJ_FLAG_HIDDEN);
            lv_obj_clear_flag(cursor_label, LV_OBJ_FLAG_HIDDEN);
            softkeys = "A:SEND  C:BKSP  B:BACK";
            break;
        }
        }
    }

    lv_label_set_text(softkey_label, softkeys);
    lv_timer_handler();
}

/* Process a URC line and update call state accordingly.
 * Returns true if the state changed. */
static bool process_urc(const char *line)
{
    if (strcmp(line, "RING") == 0) {
        if (call_state == PHONE_IDLE) {
            LOG_INF(">>> Incoming call — ringing");
            call_state = PHONE_RINGING;
            ui_screen = UI_DIALER;  /* calls override menu */
            dial_len = 0;
            dial_string[0] = '\0';
            ui_render();
            return true;
        }
    }

    if (strstr(line, "VOICE CALL: BEGIN") != NULL) {
        if (call_state == PHONE_CALLING || call_state == PHONE_RINGING) {
            LOG_INF(">>> Call connected");
            call_state = PHONE_CONNECTED;
            call_start_time = k_uptime_get();
            call_timer_seconds = 0;
            ui_render();
            return true;
        }
    }

    if (strstr(line, "VOICE CALL: END") != NULL) {
        if (call_state != PHONE_IDLE) {
            LOG_INF(">>> Call ended: %s", line);
            call_state = PHONE_IDLE;
            ui_screen = UI_DIALER;  /* return to dialer after call */
            dial_len = 0;
            dial_string[0] = '\0';
            ui_render();
            return true;
        }
    }

    return false;
}

/* --- Scanline background draw callback ---
 *
 * Draws faint horizontal lines every 3px across the screen, giving a
 * CRT phosphor / HUD texture behind the content. Called by LVGL during
 * the screen's DRAW_MAIN phase, before children are drawn. */
static void scanline_draw_cb(lv_event_t *e)
{
    lv_layer_t *layer = lv_event_get_layer(e);
    lv_draw_line_dsc_t dsc;
    lv_draw_line_dsc_init(&dsc);
    dsc.color = lv_color_hex(UI_COLOR_AMBER);
    dsc.width = 1;
    dsc.opa = LV_OPA_10;  /* very faint — ~4% opacity */

    lv_coord_t w = lv_display_get_horizontal_resolution(lv_display_get_default());
    lv_coord_t h = lv_display_get_vertical_resolution(lv_display_get_default());

    for (lv_coord_t y = 0; y < h; y += 3) {
        dsc.p1.x = 0;
        dsc.p1.y = y;
        dsc.p2.x = w;
        dsc.p2.y = y;
        lv_draw_line(layer, &dsc);
    }
}

/* Handle a keypad key press based on the current call state and UI screen.
 *
 * Call states (CALLING/RINGING/CONNECTED) are handled first — they override
 * the UI screen. When IDLE, the ui_screen determines key behavior:
 *
 *   UI_DIALER:         0-9*# = digits, A = call, C = backspace, D = menu
 *   UI_MENU:           2/8 = scroll, A = select, B = back
 *   UI_CONTACTS:       2/8 = scroll, A = open, B = back
 *   UI_CONTACT_DETAIL: 2/8 = scroll actions, A = do action, B = back
 *   UI_MESSAGES:       2/8 = scroll, A = open, B = back
 *   UI_CONVERSATION:   C = compose, B = back
 *   UI_COMPOSE:        0-9*# = text, A = send (mock), C = backspace, B = back
 */
static void handle_key(char key)
{
    /* --- Call state handling (overrides UI screen) --- */
    switch (call_state) {
    case PHONE_CALLING:
        if (key == 'B') {
            LOG_INF("=== Cancelling outgoing call ===");
            modem_send("AT+CHUP\r\n");
            call_state = PHONE_IDLE;
            ui_screen = UI_DIALER;
            dial_len = 0;
            dial_string[0] = '\0';
            ui_render();
        }
        return;

    case PHONE_RINGING:
        if (key == 'A') {
            LOG_INF("=== Answering incoming call ===");
            modem_send("ATA\r\n");
        } else if (key == 'B') {
            LOG_INF("=== Rejecting incoming call ===");
            modem_send("AT+CHUP\r\n");
            call_state = PHONE_IDLE;
            ui_screen = UI_DIALER;
            ui_render();
        }
        return;

    case PHONE_CONNECTED:
        if (key == 'B') {
            LOG_INF("=== Hanging up ===");
            modem_send("AT+CHUP\r\n");
            call_state = PHONE_IDLE;
            ui_screen = UI_DIALER;
            dial_len = 0;
            dial_string[0] = '\0';
            ui_render();
        }
        return;

    case PHONE_IDLE:
        break;  /* fall through to UI screen handling */
    }

    /* --- UI screen handling (only when PHONE_IDLE) --- */
    switch (ui_screen) {
    case UI_DIALER:
        if ((key >= '0' && key <= '9') || key == '*' || key == '#') {
            if (dial_len < DIAL_STRING_MAX) {
                dial_string[dial_len++] = key;
                dial_string[dial_len] = '\0';
                ui_render();
            }
        } else if (key == 'A') {
            if (dial_len > 0) {
                char atd_cmd[32];
                LOG_INF("=== Placing outgoing call to %s ===", dial_string);
                call_state = PHONE_CALLING;
                snprintf(atd_cmd, sizeof(atd_cmd), "ATD%s;\r\n", dial_string);
                modem_send(atd_cmd);
                ui_render();
            }
        } else if (key == 'C') {
            if (dial_len > 0) {
                dial_string[--dial_len] = '\0';
                ui_render();
            }
        } else if (key == 'D') {
            LOG_INF("=== Opening menu ===");
            ui_screen = UI_MENU;
            menu_index = 0;
            ui_render();
        }
        break;

    case UI_MENU:
        if (key == 'B') {
            ui_screen = UI_DIALER;
            ui_render();
        } else if (key == 'A') {
            if (menu_index == 0) {
                ui_screen = UI_CONTACTS;
                contacts_index = 0;
                ui_render();
            } else if (menu_index == 1) {
                ui_screen = UI_MESSAGES;
                messages_index = 0;
                ui_render();
            } else {
                LOG_INF("Settings (not implemented)");
            }
        } else if (key == '2') {
            menu_index = (menu_index > 0) ? menu_index - 1 : MENU_COUNT - 1;
            ui_render();
        } else if (key == '8') {
            menu_index = (menu_index + 1) % MENU_COUNT;
            ui_render();
        }
        break;

    case UI_CONTACTS:
        if (key == 'B') {
            ui_screen = UI_MENU;
            menu_index = 0;
            ui_render();
        } else if (key == 'A') {
            ui_screen = UI_CONTACT_DETAIL;
            current_contact = contacts_index;
            contact_action_index = 0;
            ui_render();
        } else if (key == '2') {
            contacts_index = (contacts_index > 0) ? contacts_index - 1 : CONTACT_COUNT - 1;
            ui_render();
        } else if (key == '8') {
            contacts_index = (contacts_index + 1) % CONTACT_COUNT;
            ui_render();
        }
        break;

    case UI_CONTACT_DETAIL:
        if (key == 'B') {
            ui_screen = UI_CONTACTS;
            contacts_index = current_contact;
            ui_render();
        } else if (key == 'A') {
            if (contact_action_index == 0) {
                /* CALL — place a real outgoing call to this contact */
                char atd_cmd[32];
                LOG_INF("=== Calling %s (%s) ===", contacts[current_contact].name,
                        contacts[current_contact].number);
                dial_len = strlen(contacts[current_contact].number);
                strncpy(dial_string, contacts[current_contact].number, sizeof(dial_string) - 1);
                dial_string[dial_len] = '\0';
                call_state = PHONE_CALLING;
                snprintf(atd_cmd, sizeof(atd_cmd), "ATD%s;\r\n", dial_string);
                modem_send(atd_cmd);
                ui_render();
            } else if (contact_action_index == 1) {
                /* TEXT — open conversation with this contact */
                for (int i = 0; i < (int)CONV_COUNT; i++) {
                    if (strcmp(conversations[i].contact_name,
                               contacts[current_contact].name) == 0) {
                        current_conv = i;
                        break;
                    }
                }
                ui_screen = UI_CONVERSATION;
                ui_render();
            } else {
                LOG_INF("Contact %s (not implemented)",
                        contact_actions[contact_action_index]);
            }
        } else if (key == '2') {
            contact_action_index = (contact_action_index > 0)
                ? contact_action_index - 1 : CONTACT_ACTION_COUNT - 1;
            ui_render();
        } else if (key == '8') {
            contact_action_index = (contact_action_index + 1) % CONTACT_ACTION_COUNT;
            ui_render();
        }
        break;

    case UI_MESSAGES:
        if (key == 'B') {
            ui_screen = UI_MENU;
            menu_index = 1;
            ui_render();
        } else if (key == 'A') {
            current_conv = messages_index;
            ui_screen = UI_CONVERSATION;
            ui_render();
        } else if (key == '2') {
            messages_index = (messages_index > 0) ? messages_index - 1 : CONV_COUNT - 1;
            ui_render();
        } else if (key == '8') {
            messages_index = (messages_index + 1) % CONV_COUNT;
            ui_render();
        }
        break;

    case UI_CONVERSATION:
        if (key == 'B') {
            ui_screen = UI_MESSAGES;
            messages_index = current_conv;
            ui_render();
        } else if (key == 'C') {
            ui_screen = UI_COMPOSE;
            compose_len = 0;
            compose_text[0] = '\0';
            ui_render();
        }
        break;

    case UI_COMPOSE:
        if (key == 'B') {
            ui_screen = UI_CONVERSATION;
            compose_len = 0;
            compose_text[0] = '\0';
            ui_render();
        } else if (key == 'A') {
            /* Mock send — just log it. Real SMS uses AT+CMGS. */
            LOG_INF("=== Mock SMS send to %s: %s ===",
                    conversations[current_conv].contact_name, compose_text);
            compose_len = 0;
            compose_text[0] = '\0';
            ui_screen = UI_CONVERSATION;
            ui_render();
        } else if (key == 'C') {
            if (compose_len > 0) {
                compose_text[--compose_len] = '\0';
                ui_render();
            }
        } else if ((key >= '0' && key <= '9') || key == '*' || key == '#') {
            if (compose_len < DIAL_STRING_MAX) {
                compose_text[compose_len++] = key;
                compose_text[compose_len] = '\0';
                ui_render();
            }
        }
        break;
    }
}

int main(void)
{
    LOG_INF("Phone firmware starting...");
    LOG_INF("Board: %s", CONFIG_BOARD);

    /* Initialize display */
    display_dev = DEVICE_DT_GET(DT_CHOSEN(zephyr_display));
    if (!device_is_ready(display_dev)) {
        LOG_ERR("Display not ready!");
        return -1;
    }
    LOG_INF("Display (ST7789V) ready");

    /* Build the LVGL UI — TE-inspired industrial design with CRT surface:
     *   status_bar (top, 22px): grey panel, signal | network | time
     *   content (middle): state label (top) + number label (center)
     *   softkey_bar (bottom, 26px): grey panel, A/B/C/D context hints
     *   Grey borders separate zones. Amber reserved for content only.
     *   Scanlines drawn behind everything for CRT phosphor depth. */
    lv_obj_t *screen = lv_screen_active();
    lv_obj_set_style_bg_color(screen, lv_color_hex(UI_COLOR_BG), LV_PART_MAIN);

    /* Scanline background — faint horizontal lines every 3px for CRT depth */
    lv_obj_add_event_cb(screen, scanline_draw_cb, LV_EVENT_DRAW_MAIN, NULL);

    /* Status bar — grey panel at top, grey border below */
    lv_obj_t *status_bar = lv_obj_create(screen);
    lv_obj_set_size(status_bar, 240, 22);
    lv_obj_align(status_bar, LV_ALIGN_TOP_LEFT, 0, 0);
    lv_obj_set_style_bg_color(status_bar, lv_color_hex(UI_COLOR_PANEL), LV_PART_MAIN);
    lv_obj_set_style_bg_opa(status_bar, LV_OPA_COVER, LV_PART_MAIN);
    lv_obj_set_style_border_side(status_bar, LV_BORDER_SIDE_BOTTOM, LV_PART_MAIN);
    lv_obj_set_style_border_color(status_bar, lv_color_hex(UI_COLOR_BORDER), LV_PART_MAIN);
    lv_obj_set_style_border_width(status_bar, 1, LV_PART_MAIN);
    lv_obj_set_style_pad_all(status_bar, 2, LV_PART_MAIN);
    lv_obj_set_scrollbar_mode(status_bar, LV_SCROLLBAR_MODE_OFF);

    signal_label = lv_label_create(status_bar);
    lv_obj_set_style_text_color(signal_label, lv_color_hex(UI_COLOR_AMBER), LV_PART_MAIN);
    lv_obj_set_style_text_font(signal_label, &jetbrainsmono_10, LV_PART_MAIN);
    lv_label_set_text(signal_label, "SIG:|||");
    lv_obj_align(signal_label, LV_ALIGN_LEFT_MID, 0, 0);

    time_label = lv_label_create(status_bar);
    lv_obj_set_style_text_color(time_label, lv_color_hex(UI_COLOR_AMBER), LV_PART_MAIN);
    lv_obj_set_style_text_font(time_label, &jetbrainsmono_10, LV_PART_MAIN);
    lv_label_set_text(time_label, "--:--");
    lv_obj_align(time_label, LV_ALIGN_CENTER, 0, 0);

    battery_label = lv_label_create(status_bar);
    lv_obj_set_style_text_color(battery_label, lv_color_hex(UI_COLOR_AMBER), LV_PART_MAIN);
    lv_obj_set_style_text_font(battery_label, &jetbrainsmono_10, LV_PART_MAIN);
    lv_label_set_text(battery_label, "BAT:|||");
    lv_obj_align(battery_label, LV_ALIGN_RIGHT_MID, 0, 0);

    /* Content labels — created hidden, shown per screen by ui_render().
     *   title_label  — 14px, top of content (screen titles, call state)
     *   hero_label   — 22px bold, center (dial number, compose text, call number)
     *   list_label   — 14px, top-left below title (multi-line lists)
     *   timer_label  — 22px, below hero (call timer on connected screen)
     *   cursor_label — small "_" that blinks, after hero (dialer/compose) */
    title_label = lv_label_create(screen);
    lv_obj_set_style_text_font(title_label, &jetbrainsmono_14, LV_PART_MAIN);
    lv_obj_set_style_text_color(title_label, lv_color_hex(UI_COLOR_AMBER), LV_PART_MAIN);
    lv_obj_align(title_label, LV_ALIGN_TOP_MID, 0, 30);
    lv_obj_add_flag(title_label, LV_OBJ_FLAG_HIDDEN);

    hero_label = lv_label_create(screen);
    lv_obj_set_style_text_font(hero_label, &jetbrainsmono_22, LV_PART_MAIN);
    lv_obj_set_style_text_color(hero_label, lv_color_hex(UI_COLOR_AMBER_BRIGHT), LV_PART_MAIN);
    lv_obj_align(hero_label, LV_ALIGN_CENTER, 0, 0);
    lv_obj_add_flag(hero_label, LV_OBJ_FLAG_HIDDEN);

    list_label = lv_label_create(screen);
    lv_obj_set_style_text_font(list_label, &jetbrainsmono_14, LV_PART_MAIN);
    lv_obj_set_style_text_color(list_label, lv_color_hex(UI_COLOR_AMBER), LV_PART_MAIN);
    lv_obj_align(list_label, LV_ALIGN_TOP_LEFT, 8, 50);
    lv_obj_add_flag(list_label, LV_OBJ_FLAG_HIDDEN);

    timer_label = lv_label_create(screen);
    lv_obj_set_style_text_font(timer_label, &jetbrainsmono_22, LV_PART_MAIN);
    lv_obj_set_style_text_color(timer_label, lv_color_hex(UI_COLOR_AMBER_BRIGHT), LV_PART_MAIN);
    lv_obj_align(timer_label, LV_ALIGN_CENTER, 0, 30);
    lv_obj_add_flag(timer_label, LV_OBJ_FLAG_HIDDEN);

    cursor_label = lv_label_create(screen);
    lv_obj_set_style_text_font(cursor_label, &jetbrainsmono_22, LV_PART_MAIN);
    lv_obj_set_style_text_color(cursor_label, lv_color_hex(UI_COLOR_AMBER_BRIGHT), LV_PART_MAIN);
    lv_label_set_text(cursor_label, "_");
    lv_obj_align_to(cursor_label, hero_label, LV_ALIGN_OUT_RIGHT_MID, 2, 0);
    lv_obj_add_flag(cursor_label, LV_OBJ_FLAG_HIDDEN);

    /* Start the blinking cursor animation (cursor_label visibility is
     * controlled by ui_render via LV_OBJ_FLAG_HIDDEN; the animation
     * toggles opacity when the label is visible). */
    cursor_anim_start();

    /* Soft-key bar — grey panel at bottom, grey border above */
    lv_obj_t *softkey_bar = lv_obj_create(screen);
    lv_obj_set_size(softkey_bar, 240, 26);
    lv_obj_align(softkey_bar, LV_ALIGN_BOTTOM_LEFT, 0, 0);
    lv_obj_set_style_bg_color(softkey_bar, lv_color_hex(UI_COLOR_PANEL), LV_PART_MAIN);
    lv_obj_set_style_bg_opa(softkey_bar, LV_OPA_COVER, LV_PART_MAIN);
    lv_obj_set_style_border_side(softkey_bar, LV_BORDER_SIDE_TOP, LV_PART_MAIN);
    lv_obj_set_style_border_color(softkey_bar, lv_color_hex(UI_COLOR_BORDER), LV_PART_MAIN);
    lv_obj_set_style_border_width(softkey_bar, 1, LV_PART_MAIN);
    lv_obj_set_style_pad_all(softkey_bar, 4, LV_PART_MAIN);
    lv_obj_set_scrollbar_mode(softkey_bar, LV_SCROLLBAR_MODE_OFF);

    softkey_label = lv_label_create(softkey_bar);
    lv_obj_set_style_text_color(softkey_label, lv_color_hex(UI_COLOR_AMBER), LV_PART_MAIN);
    lv_obj_set_style_text_font(softkey_label, &jetbrainsmono_14, LV_PART_MAIN);
    lv_label_set_text(softkey_label, "");
    lv_obj_align(softkey_label, LV_ALIGN_CENTER, 0, 0);

    /* Boot screen — show "BOOTING..." as title before UI is ready */
    lv_label_set_text(title_label, "BOOTING...");
    lv_obj_clear_flag(title_label, LV_OBJ_FLAG_HIDDEN);
    lv_timer_handler();
    display_blanking_off(display_dev);
    LOG_INF("Display UI initialized (TE industrial + CRT scanlines)");

    /* The keypad matrix driver is initialized automatically by Zephyr
     * (the gpio-kbd-matrix device is ready at boot). The input callback
     * is registered at compile time via INPUT_CALLBACK_DEFINE. No
     * explicit init needed here — just verify the device is ready. */
    const struct device *keypad = DEVICE_DT_GET(DT_NODELABEL(kbd_matrix));
    if (!device_is_ready(keypad)) {
        LOG_ERR("Keypad matrix device not ready!");
        return -1;
    }
    LOG_INF("Keypad (gpio-kbd-matrix) ready — type number, A=Call, B=End, C=Backspace");

    /* Initialize modem UART */
    modem_uart = DEVICE_DT_GET(MODEM_UART_NODE);
    if (!device_is_ready(modem_uart)) {
        LOG_ERR("Modem UART (LPUART1) not ready!");
        return -1;
    }
    LOG_INF("Modem UART (LPUART1) ready");

    uart_irq_callback_user_data_set(modem_uart, modem_uart_isr, NULL);
    uart_irq_rx_enable(modem_uart);
    LOG_INF("Modem UART RX interrupts enabled");

    LOG_INF("Waiting 3s for modem to settle...");
    lv_label_set_text(title_label, "INITIALIZING...");
    lv_label_set_text(softkey_label, "WAITING FOR MODEM");
    lv_timer_handler();
    k_sleep(K_SECONDS(3));

    /* Verify modem is alive and on the network */
    LOG_INF("--- Modem checks ---");
    modem_at("AT\r\n");
    modem_at("AT+CSQ\r\n");
    modem_at("AT+CEREG?\r\n");

    call_state = PHONE_IDLE;
    dial_len = 0;
    dial_string[0] = '\0';
    ui_render();
    LOG_INF("=== Phone ready — type a number and press A to call ===");

    /* Main loop: drain keypad key queue + poll modem URCs, act based on
     * call state. The keypad driver runs in its own thread and feeds
     * key_msgq; we drain it here. modem_readline has a short timeout so
     * we check the queue frequently. lv_timer_handler keeps LVGL rendering.
     * The call timer is updated here when connected. */
    while (1) {
        char line[256];
        char key;

        /* Process any pending keypad keys (from the input callback) */
        while (k_msgq_get(&key_msgq, &key, K_NO_WAIT) == 0) {
            LOG_INF("Key: %c (state=%d)", key, call_state);
            handle_key(key);
        }

        /* Update call timer when connected (every loop iteration ~100ms) */
        if (call_state == PHONE_CONNECTED) {
            int new_seconds = (int)((k_uptime_get() - call_start_time) / 1000);
            if (new_seconds != call_timer_seconds) {
                call_timer_seconds = new_seconds;
                char timer_buf[16];
                int m = call_timer_seconds / 60;
                int s = call_timer_seconds % 60;
                snprintf(timer_buf, sizeof(timer_buf), "%02d:%02d", m, s);
                lv_label_set_text(timer_label, timer_buf);
                lv_timer_handler();
            }
        }

        /* Process modem URC line if we got one */
        int len = modem_readline(line, sizeof(line), 100);
        lv_timer_handler();

        if (len > 0) {
            strip_crlf(line);
            if (strlen(line) > 0) {
                LOG_INF("URC: %s", line);
                process_urc(line);
            }
        }
    }

    return 0;
}
