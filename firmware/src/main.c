/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * main.c — Phone firmware entry point
 *
 * This is the application code. It uses Zephyr APIs (consistent across
 * hardware) to interact with peripherals described in app.overlay and
 * features enabled in prj.conf.
 *
 * Currently this is a skeleton that proves the build pipeline works
 * end-to-end. As we add peripherals, main.c will initialize each
 * subsystem and spawn the RTOS threads that run the phone:
 *   - Modem thread: AT command communication with SIM7600
 *   - UI thread: display rendering + keypad input
 *   - Power thread: battery monitoring + sleep policies
 *   - Call state machine: call lifecycle management
 */

#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>

/* Register this module with the logging system.
 * LOG_MODULE_REGISTER creates a log context named "phone" —
 * log messages from this file will be tagged [PHONE] and can
 * be filtered independently from other modules. */
LOG_MODULE_REGISTER(phone, LOG_LEVEL_INF);

int main(void)
{
    LOG_INF("Phone firmware starting...");
    LOG_INF("Board: %s", CONFIG_BOARD);

    /* TODO: Initialize subsystems as we build them:
     *   - modem_init()   — UART + AT command parser + URC handler
     *   - keypad_init()  — GPIO matrix scanner
     *   - display_init() — SPI + ST7789V driver
     *   - audio_init()   — I2C + MAX9880A codec config
     *   - power_init()   — I2C + MAX17048 fuel gauge
     */

    while (1) {
        /* Main loop — will eventually be the UI event loop.
         * For now, just sleep to prove the thread scheduler works. */
        k_sleep(K_SECONDS(5));
        LOG_INF("alive");
    }

    return 0;
}
