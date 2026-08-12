# sensors-firmware agent — DRV2605L events + LSM6DSOX tap + MAX98357A + volume-on-nRF

Session: 2026_08_12_EXTENSION_ESCROW_SHIP. Scope: three hardware modules into
`firmware/nrf9160` on top of the controls commit 6963fe9, plus the mid-task
owner ruling that the volume knob moves from the ESP32 to the nRF9160.
Commit: none (per task instructions).

## What landed

- **Haptics (DRV2605L, 0x5A on I2C2)** — extended the existing proven
  open-loop RTP module instead of switching to the ROM effect library
  (the bench-measured VLV101040A calibration is the calibration; open-loop
  needs no auto-cal at all). Three new presets (`tick`/`click`/`strong`)
  plus a non-blocking `haptic_trigger()` work-queue engine so events can
  fire from ISRs and mid-conversation without eating the I2S TX runway.
  Event map: press-ack=click, approval-decision-sent=double, memo
  start/stop=tick, incoming approval readback=strong, muted-press=long.
- **Accelerometer** — identified as **LSM6DSOX** (Adafruit invoice
  2026-07-02, hardware/purchases/innovoice.webarchive), NOT LIS2DH12.
  New `src/accel_tap.c`: raw-I2C double-tap-only config at 104 Hz
  low-power (~26 µA), gyro off, INT1 → P0.27 via PORT SENSE (no GPIOTE),
  ISR gives the yellow-button semaphore — all press semantics inherited.
  Register block isolated for a future part swap.
- **MAX98357A speaker amp** — taps the existing I2S TX wires; firmware
  owns only SD_MODE on **P0.01** (P0.29 was NOT free — it is the console
  TX). High = left-slot playback (datasheet Table 5), low = shutdown;
  boot default bluetooth/off; `{"type":"audio_sink"}` frame parsed from
  the converse WS (mid-conversation and idle).
- **Volume on the nRF (owner ruling)** — pot wiper → P0.15/AIN2 (the only
  free AIN in silicon), SAADC ratiometric VDD/4, ~20 Hz poll with the
  ESP32's exact tuning (2 % hysteresis, end-stop snap, squared curve),
  gain applied once in the downlink fill (`tx_apply_volume`) so the wire
  carries pre-scaled PCM; sync preamble deliberately unscaled. Reports
  `{"type":"volume"}` on the converse WS.
- **uart0 repin** — console went TX-only on P0.29; the board default
  pinctrl had been claiming P0.26 (with a pull-up on the no-pull
  mic-sense net!), P0.27 and P0.28.
- CONTROLS_WIRING.md: I2C section (4.7 k externals on P0.30/31), effect
  map, amp/speaker/pot rows, VCOM2 caveats, contract-table additions.

## Deferred / TODO (cloud-relay mid-churn by relay-voice agents)

1. Relay sender for `{"type":"audio_sink"}` downlink frames.
2. Relay `{"type":"approval_readback"}` announce before speaking an
   approval (device parses it already).
3. Optional: relay log line for uplinked `volume` frames (currently
   silently ignored — safe).
4. ESP32 pot-code strip (another agent's task); until then jumper ESP32
   GPIO34 → 3V3 so its now-orphaned gain path reads unity.

## Build — GREEN (build-sensors, NCS v3.4.0, nrf9160dk/nrf9160/ns + secrets.conf)

- App image: **RAM 203,860 B / 211,608 B = 96.34 %** (7,748 B free),
  FLASH 406,596 B / 576 KB = 68.94 %. TF-M unchanged (64,912 B / 6,952 B).
- Deltas vs build-controls (same section-sum method):
  **RAM +347 B**, FLASH +7,952 B.
- Devicetree verified in the built zephyr.dts: uart0 TX-only on P0.29
  (disable-rx), sense-edge-mask 0x1be00000, amp_sd_mode P0.01,
  accel_int1 P0.27 pull-down, adc okay.
- Not flashed (DK off USB, per instructions). Nothing committed.
