# ESP32 module-parity strip — working log

Agent: esp32 firmware strip subagent. Owned file: `firmware/esp32-airpods-bridge/src/main.cpp`.
Ruling applied (owner, 2026-08-12): the ESP32 does only what a Bluetooth audio module could do; volume is the nRF9160's job.

## Removed
- Entire potentiometer volume feature: GPIO34/ADC1 config, median-of-5 reader,
  ~20 Hz poll with hysteresis + snap bands, squared perceptual curve, Q12 gain
  multiply in the A2DP callback, boot-time `analogSetPinAttenuation`/seed poll,
  `{"type":"volume",...}` serial event, `volume_gain_q12` diagnostic field.
- Bring-up diagnostic serial commands and all code existing only for them:
  `capture` (raw 32-bit slot capture, 64x2 int32 buffer, await-audio arming,
  `raw_i2s_capture` emission), `dump` (`i2s_dump` ring dump), `probe`
  (`pin_probe`, bit-banged GPIO slot reader), `timing` (`clock_timing`,
  CCOUNT frequency counter). Also the auto clock_timing emission on resync,
  the `max_clock_test` boot line, the I2S RX-overflow IRAM hook, the
  read-gap profiler, and the A2DP CallTimer profiling struct.
- Bring-up-only counters (write-only after the diagnostic slimming):
  read errors, raw peak, resyncs, sync locks, nonzero frames, ring
  under/overrun counts, resampler starts/slips, rx overflows, max read gap,
  call timing. Behavior at each site (drop/fade/hold/resync) is unchanged.
- Unused after the above: `ringMux`, includes `soc/gpio_struct.h`,
  `xtensa/core-macros.h`; a pre-existing dead store of `buffered`.

## Kept (module parity)
I2S slave input with resync + sync-word lock (incl. one-bit-shift repair),
polyphase 625/882 resampler, SPSC ring, A2DP source + pairing over serial
JSON (scan/connect/forget/status), route gate, auto-reconnect paging, state
events, test tone. 1 s diagnostic slimmed to link health: state, target,
known_addr, a2dp_state, i2s_frames, i2s_peak, a2dp_frames, slim message.
Header comment now carries the owner's verbatim ruling + audio-path rules
(SPSC/no locks, no DRAM-for-observability, IRAM ISR rule).

## Volume curve constants for the nRF port
raw 0..4095 -> level = (raw/4095)^2; gain = round(level*4096) Q12, unity 4096,
attenuator only; hysteresis 82 counts (~2%); snap: <=40 -> 0, >=4055 -> 4095;
median-of-5 reads; poll 50 ms; apply as one coherent (sample*gain)>>12 before
final saturation.

## Sizes
Before: RAM 78344 (23.9%), Flash 1145740 (87.4%).
After:  RAM 77672 (23.7%), Flash 1128380 (86.1%). Build SUCCESS, not flashed,
not committed (per task).
