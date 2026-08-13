# hw-selftest — bench self-test of the pendant breadboard

Resumed 2026-08-13 after the first run was killed by a UI stop (not an error).
The killed run had produced `firmware/nrf9160/selftest/` and a build in
`firmware/nrf9160/build-selftest/`. Both were inspected and REUSED, not
rewritten. The app's test coverage was already right; what was missing was that
it had never actually booted on hardware.

## Files claimed

`firmware/nrf9160/selftest/**`, `firmware/nrf9160/build-selftest/**`, and the
DK's J-Link while bc-flash-2 was not holding it. Not touched:
`firmware/nrf9160/src/**`, `firmware/nrf9160/boards/**`,
`firmware/esp32-airpods-bridge/**` (read only), other `build-*`.

## Coordination

- bc-flash-2 held the J-Link; waited for its explicit RELEASED message rather
  than for idleness, as instructed. It also cancelled the board-controller
  flash: the only pins that routing frees are P0.00/P0.05 (ESP32 UART) and
  P0.03/04/07 (RGB), and NEITHER is wired, so there was nothing to unblock.
- bench-ui had a node reader on VCOM0 that was splitting the byte stream; it
  has since stood down and now checks `lsof` before opening any port.

## Board state left behind

`build-app-current/nrf9160/zephyr/tfm_merged.hex`, programmed with nrfutil
(`chip_erase_mode=ERASE_ALL`) and reset. Verified booting by clean console
capture. VCOM0 released.

## THE SELF-TEST DOES NOT BOOT YET — three real causes found and fixed, one open

Measured over SWD, not guessed. Symptom each time was a completely silent
console, which reads exactly like a dead board.

1. FIXED — SecureFault inside TF-M. The app used the board's stock ns SRAM
   split; TF-M panicked before ever branching to non-secure code (PC=0x240A,
   IPSR=7 = SecureFault, PRIMASK_S=1; a breakpoint on the NS reset handler was
   never reached). The overlay now carves secure down to 32 kB exactly as the
   application overlay does.
2. FIXED — PSA CSPRNG into a hash-less TF-M. Left alone, the app selected
   `PSA_CSPRNG_GENERATOR`, routing random requests through a non-secure call
   into a TF-M crypto partition built WITHOUT its hash module. The application
   uses the hardware entropy driver; `CONFIG_ENTROPY_GENERATOR=y` matches it.
3. FIXED — pwm0 left enabled. The board enables pwm0 by default and the
   application overlay explicitly disables it (and `pwm_led0`); the self-test
   disabled only pwm1/pwm2. So `pwm_nrfx` bound pwm0 during driver init and
   applied `pwm0_default`, claiming P0.02, before `main()` printed anything.
4. OPEN — the non-secure image still hard-faults into CPU lockup
   (PC=0xEFFFFFFE, IPSR=3) before `main()`. Confirmed not a console problem:
   the known-good application image, flashed and captured with the identical
   procedure, prints perfectly. Confirmed not reached: `pot_ready` and
   `i2c_rail_alive` in NS RAM are still zero after a 20 s run.

NEXT STEP for whoever picks this up: bisect `prj.conf`. Start from GPIO +
console only, confirm a banner, then add I2C, ADC, SPI/disk/FS, I2S in that
order. The config now differs from the working application in only
`MAIN_STACK_SIZE`, `SYSTEM_WORKQUEUE_STACK_SIZE`, `HEAP_MEM_POOL_SIZE=0` and
`I2S_NRFX_TX_BLOCK_COUNT` — `HEAP_MEM_POOL_SIZE=0` is the most suspicious of
those, since the FAT/disk stack allocates.

## A trap that cost real time, recorded so nobody repeats it

Overlapping background `sniff.py` instances. Two readers on one macOS tty SPLIT
the byte stream, so captures came back shredded ("RV205 not anwering"), and a
still-running earlier sniffer captured a LATER flash's output into a stale file
— which briefly looked like the self-test booting when it was the application.
Rule: kill every reader and check `lsof` before each capture, and never trust a
log whose window overlapped another.

## MEASURED HARDWARE RESULTS (from the application image + direct SWD probing)

The self-test never ran, so these come from the application's console and from
reading/driving the GPIO pad registers over the J-Link directly. Method for the
pad tests: apply the nRF's internal pull-down (~13k) and see whether the line
holds. A 4.7k external pull-up to 3V divides to ~2.2 V and still reads HIGH; a
floating pin collapses to LOW. Writes were verified by reading `PIN_CNF` back,
and P0.28 (unwired by design) was used as a control — it collapsed to LOW under
identical treatment, proving the method discriminates.

Resting pad levels, `GPIO_IN` = 0xE3E01061:

| Net | Pin | Reading | Verdict |
|---|---|---|---|
| I2C SDA | P0.30 | HIGH, HOLDS vs pull-down | pull-up fitted, 3V rail ALIVE |
| I2C SCL | P0.31 | HIGH, HOLDS vs pull-down | pull-up fitted, 3V rail ALIVE |
| microSD DO | P0.12 | HIGH, HOLDS vs pull-down | breakout powered |
| yellow button | P0.21 | HIGH at rest | correct for unpressed; no edge seen |
| green button | P0.22 | HIGH at rest | expected — wires off |
| blue button | P0.23 | HIGH at rest | correct for unpressed; no edge seen |
| encoder A/B | P0.24/25 | HIGH at rest | correct at rest; no turn captured |
| mic power sense | P0.26 | LOW at every app boot, drifted HIGH once | mic power CUT |
| encoder push | P0.28 | LOW under pull-down | unwired by design (control pin) |
| console TX | P0.29 | HIGH idle | working — this is the console |

- I2C: nothing ACKs. The application reports `DRV2605L not answering (-5)` on
  every boot. Because SDA/SCL both hold high, this is NOT missing pull-ups and
  NOT a dead 3V rail — chase the DEVICE end (the DRV2605L breakout's own
  VIN/GND, or its SDA/SCL leg).
- microSD: `Card error on CMD0` / `fs mount error (-5)`, five retries, every
  boot. DO holds high, so the breakout has power — points at no card / not
  seated rather than a dead rail.
- These two are on DIFFERENT buses, which had suggested a shared-rail fault.
  The pad measurements argue against that: both buses' rails are alive.
- ESP32: HEALTHY. Answered `{"command":"status"}` on its own USB port with
  `{"type":"bridge","state":"searching","target":"Bose",...}`. `emitEvent()`
  (esp32-airpods-bridge/src/main.cpp:115) writes every event to Serial2
  (GPIO17 -> nRF P0.05) too, so the chip is transmitting at the nRF constantly.
- ESP32 UART link: NOT WIRED. P0.00/P0.05 jumpers are not fitted (owner is out
  of jumper wires) and the board-controller reroute was cancelled, so the
  interface MCU still drives P0.00. Silence here is correct, not a fault.
- RGB LED: NOT WIRED AT ALL. Not tested. The firmware still drives the pads,
  which is harmless.
- Mic audio peak/RMS: NOT MEASURED. The mic is unpowered (P0.26 low), so any
  number would have been silence. Needs the red latching switch ON first.
