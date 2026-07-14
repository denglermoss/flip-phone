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
 * The Waveshare HAT has an onboard voltage translator (1.8V ↔ 3.3V).
 * On the final custom PCB, a TXB0108 will be needed between the
 * STM32H743 and the SIM7600A-H raw module pins.
 */

#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/uart.h>
#include <zephyr/drivers/display.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/sys/ring_buffer.h>
#include <zephyr/logging/log.h>
#include <lvgl.h>
#include <stdio.h>
#include <string.h>

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
 *   1. The B1 user button (PC13, already on the Nucleo board)
 *   2. Async URCs from the modem (RING, VOICE CALL: BEGIN/END)
 *
 * States:
 *   PHONE_IDLE     — waiting, display "Idle", button → place call
 *   PHONE_CALLING  — outgoing call in progress, display "Calling..."
 *                    button → cancel (AT+CHUP), URC BEGIN → connected
 *   PHONE_RINGING  — incoming call, display "Incoming call"
 *                    button → answer (ATA), URC BEGIN → connected
 *   PHONE_CONNECTED — call active, display "Connected"
 *                     button → hang up (AT+CHUP), URC END → idle
 *
 * The button uses a GPIO interrupt (ISR sets a flag, main loop acts).
 * The modem URCs come through the ring buffer (modem_readline).
 *
 * The main loop polls both: read a line from the modem with a short
 * timeout, check the button flag, then act based on current state.
 * lv_timer_handler() is called each iteration to keep LVGL rendering. */

#define CALL_NUMBER "6078821755"

enum phone_state {
    PHONE_IDLE,
    PHONE_CALLING,
    PHONE_RINGING,
    PHONE_CONNECTED,
};

static enum phone_state call_state = PHONE_IDLE;

/* Button (B1 user button on PC13, already in board DTS as sw0).
 * The ISR sets a flag; the main loop reads and clears it. */
static struct gpio_dt_spec button = GPIO_DT_SPEC_GET(DT_ALIAS(sw0), gpios);
static struct gpio_callback button_cb_data;
static volatile bool button_pressed;

static void button_isr(const struct device *dev, struct gpio_callback *cb,
                       uint32_t pins)
{
    ARG_UNUSED(dev);
    ARG_UNUSED(cb);
    ARG_UNUSED(pins);
    button_pressed = true;
}

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

/* LVGL UI elements */
static lv_obj_t *status_label;    /* "Idle", "Calling...", "Connected" */
static lv_obj_t *number_label;    /* Phone number being called */
static lv_obj_t *info_label;      /* Signal strength, network status */

/* Update the status text shown on screen. */
static void ui_set_status(const char *status, const char *number,
                          const char *info)
{
    if (status_label) {
        lv_label_set_text(status_label, status);
    }
    if (number_label) {
        lv_label_set_text(number_label, number ? number : "");
    }
    if (info_label) {
        lv_label_set_text(info_label, info ? info : "");
    }
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
            ui_set_status("Incoming call", CALL_NUMBER, "Press B1 to answer");
            return true;
        }
    }

    if (strstr(line, "VOICE CALL: BEGIN") != NULL) {
        if (call_state == PHONE_CALLING || call_state == PHONE_RINGING) {
            LOG_INF(">>> Call connected");
            call_state = PHONE_CONNECTED;
            ui_set_status("Connected", CALL_NUMBER, "Press B1 to hang up");
            return true;
        }
    }

    if (strstr(line, "VOICE CALL: END") != NULL) {
        if (call_state != PHONE_IDLE) {
            LOG_INF(">>> Call ended: %s", line);
            call_state = PHONE_IDLE;
            ui_set_status("Idle", "", "Press B1 to call");
            return true;
        }
    }

    return false;
}

/* Handle button press based on current call state. */
static void handle_button(void)
{
    switch (call_state) {
    case PHONE_IDLE:
        /* Place outgoing call */
        LOG_INF("=== Placing outgoing call to %s ===", CALL_NUMBER);
        call_state = PHONE_CALLING;
        ui_set_status("Calling...", CALL_NUMBER, "Press B1 to cancel");
        modem_send("ATD" CALL_NUMBER ";\r\n");
        break;

    case PHONE_CALLING:
        /* Cancel outgoing call before it connects */
        LOG_INF("=== Cancelling outgoing call ===");
        modem_send("AT+CHUP\r\n");
        call_state = PHONE_IDLE;
        ui_set_status("Idle", "", "Press B1 to call");
        break;

    case PHONE_RINGING:
        /* Answer incoming call */
        LOG_INF("=== Answering incoming call ===");
        ui_set_status("Answering...", CALL_NUMBER, "");
        modem_send("ATA\r\n");
        break;

    case PHONE_CONNECTED:
        /* Hang up — AT+CHUP is the SIM7600 voice call hangup command.
         * ATH returns OK but doesn't actually end voice calls (it's
         * for data calls). AT+CHUP sends the SIP BYE and tears down
         * the VoLTE session properly. */
        LOG_INF("=== Hanging up ===");
        modem_send("AT+CHUP\r\n");
        /* State will return to IDLE when modem sends VOICE CALL: END */
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

    /* Build the LVGL UI:
     *   status_label  — top center, large text (call state)
     *   number_label  — center, medium text (phone number)
     *   info_label    — bottom, small text (signal/network info) */
    lv_obj_t *screen = lv_screen_active();
    lv_obj_set_style_bg_color(screen, lv_color_hex(0x000000), LV_PART_MAIN);

    status_label = lv_label_create(screen);
    lv_obj_set_style_text_font(status_label, &lv_font_montserrat_28, LV_PART_MAIN);
    lv_obj_set_style_text_color(status_label, lv_color_hex(0xFFFFFF), LV_PART_MAIN);
    lv_obj_align(status_label, LV_ALIGN_TOP_MID, 0, 20);

    number_label = lv_label_create(screen);
    lv_obj_set_style_text_font(number_label, &lv_font_montserrat_28, LV_PART_MAIN);
    lv_obj_set_style_text_color(number_label, lv_color_hex(0x00FF00), LV_PART_MAIN);
    lv_obj_align(number_label, LV_ALIGN_CENTER, 0, 0);

    info_label = lv_label_create(screen);
    lv_obj_set_style_text_color(info_label, lv_color_hex(0xAAAAAA), LV_PART_MAIN);
    lv_obj_align(info_label, LV_ALIGN_BOTTOM_MID, 0, -20);

    ui_set_status("Booting...", "", "");
    lv_timer_handler();
    display_blanking_off(display_dev);
    LOG_INF("Display UI initialized");

    /* Initialize button (B1 on PC13) */
    if (!gpio_is_ready_dt(&button)) {
        LOG_ERR("Button not ready!");
        return -1;
    }
    gpio_pin_configure_dt(&button, GPIO_INPUT);
    gpio_init_callback(&button_cb_data, button_isr, BIT(button.pin));
    gpio_add_callback(button.port, &button_cb_data);
    gpio_pin_interrupt_configure_dt(&button, GPIO_INT_EDGE_TO_ACTIVE);
    LOG_INF("Button (B1/PC13) ready — press to call/answer/hangup");

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
    ui_set_status("Initializing...", "", "Waiting for modem");
    k_sleep(K_SECONDS(3));

    /* Verify modem is alive and on the network */
    LOG_INF("--- Modem checks ---");
    modem_at("AT\r\n");
    modem_at("AT+CSQ\r\n");
    modem_at("AT+CEREG?\r\n");

    call_state = PHONE_IDLE;
    ui_set_status("Idle", "", "Press B1 to call");
    LOG_INF("=== Phone ready — press B1 to place a call ===");

    /* Main loop: poll modem URCs + button, act based on call state.
     * This is a single-threaded cooperative loop — no RTOS threading
     * needed yet. modem_readline has a short timeout so we check the
     * button frequently. lv_timer_handler keeps LVGL rendering. */
    while (1) {
        char line[256];
        int len = modem_readline(line, sizeof(line), 100);
        lv_timer_handler();

        /* Process modem URC if we got a line */
        if (len > 0) {
            strip_crlf(line);
            if (strlen(line) > 0) {
                LOG_INF("URC: %s", line);
                process_urc(line);
            }
        }

        /* Process button press if ISR set the flag */
        if (button_pressed) {
            button_pressed = false;
            /* Simple debounce — wait a bit then check button is still pressed */
            k_msleep(50);
            if (gpio_pin_get_dt(&button) == 1) {
                LOG_INF("Button pressed (state=%d)", call_state);
                handle_button();
            }
        }
    }

    return 0;
}
