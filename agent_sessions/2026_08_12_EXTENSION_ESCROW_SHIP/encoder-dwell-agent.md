# encoder-dwell — dwell-to-select for the menu knob (nRF9160 + cloud-relay)

Owner ruling, 2026-08-12: **"we're not going to use the button on the rotary
encoder."** Their part is the illuminated type (3 rotation pins + 5 carrying a
switch and an unused built-in LED); only the three rotation wires are
connected — A → P0.24, C → GND, B → P0.25. P0.28 is unwired and freed.

The gap that created: the whole screenless grammar was turn-to-scroll +
push-to-select + long-hold-to-escape. With no switch there was neither a select
nor an escape — the owner could browse the app ring forever and enter nothing.

## Claimed files
- firmware/nrf9160/src/main.c
- firmware/nrf9160/boards/nrf9160dk_nrf9160_ns.overlay
- software/ai-pendant-simulator/cloud-relay/menuRing.js + menuRing.test.js
- software/ai-pendant-simulator/cloud-relay/pendantConverse.js (comments, one log string)
- docs/Screenless_App_Grammar.md, firmware/CONTROLS_WIRING.md, hardware/BREADBOARD_WIRING.md

NOT touched: haptic.c, pendant_status.c, the audio path, local-agent, esp32.

## Firmware — where the dwell lives
- `MENU_DWELL_MS 1500` + `static struct k_work_delayable menu_dwell_work`.
- The encoder ISR's only new job: `k_work_reschedule(&menu_dwell_work,
  K_MSEC(MENU_DWELL_MS))` on each completed detent (±4 quadrature transitions),
  *including* a detent the backlog cap dropped — the cap is about what is worth
  sending, the dwell is about whether the hand is still moving. A reschedule is
  ISR-safe and is literally cancel+restart.
- `menu_dwell_expired()` runs on the system workqueue: `atomic_set(&menu_select_req, 1)`
  + `haptic_trigger(HAPTIC_PATTERN_TICK)`. The WS I/O thread still owns the
  socket, so the ISR → atomics → WS-thread discipline is unchanged; a timer was
  inserted in front of the atomic, not a new socket writer.
- **No repeat fire**: the work item is one-shot and only a detent arms it, so a
  resting knob commits exactly once. A pendant swinging on a lanyard cannot
  start a timer every 1.5 s.
- **Drop-when-closed**: the handler returns early if `pendant_ws_connected()` is
  false — no atomic, no tick. A buzz claiming a selection the relay never heard
  would be the device lying on the only feedback channel dwell has.
- Push handler REMOVED: `encoder_push` DT spec/callback/alias/node, the
  `ENCODER_PUSH_DEBOUNCE_MS` debounce and the init block are gone, and P0.28's
  bit left the GPIO sense-edge mask (`0x1be00000` → `0x0be00000`) so an unwired
  pin is not left armed as a wake source.

## Relay findings (speech pacing)
- Position name is spoken on a 200 ms settle; the select lands 1500 ms after the
  last detent, so the owner hears the entry **1.3 s before** it commits. Ordering
  is safe by construction and now documented as a paired constraint in both
  `MENU_NAME_SETTLE_MS` and the grammar doc.
- **The commit does not re-speak the name.** `menuSelect` emits no `name` effect
  on any commit path — one-shot apps answer with the app's own words (the time,
  "Checking your reminders."), audio picks say "Connecting X." / "Using the
  pendant speaker.", a preset says the timer-started line, and Back says nothing
  by design (falling earcon only). Verified as a test that loops every app-ring
  entry.
- Entering **Timer** is the one place that speaks on entry, and it was a lie
  about the hardware: "Press to start." → **"Turn, then pause to start."** It
  also fixes a real dwell wrinkle — the preset you land on cannot be dwelled
  into until a detent re-arms the timer, so the hint asks for the turn.
- `Back` is the last entry of APP_RING, TIMER_RING and every audioRing, so escape
  needs no new gesture. `{"type":"menu_back"}` stays handled (dashboard/tests)
  but nothing emits it; the long-hold it was written for is cancelled.
- 4 new tests: every ring ends in Back; turn-and-stop alone gets in and out with
  no other frame; no commit re-speaks its name; and no-repeat-fire is documented
  as the FIRMWARE's guarantee so nobody "fixes" it into the pure reducer.

## Results
- Build (NCS v3.4.0, `build-dwell`): **FLASH 414 368 B / 70.25 %**,
  **RAM 204 964 B / 96.86 %** (build-rgb was 96.85 % — net +21 B: the
  `k_work_delayable` minus the push callback struct and its debounce
  timestamp). Text −60 B, data −76 B, bss +28 B vs build-rgb. Not flashed.
- Tests: `node --test 'cloud-relay/*.test.js' 'shared/*.test.js'` → **703/703
  pass** (menuRing 27 → 31). The 743 figure in the brief predates commit
  041b0bc, which deleted shared/fleetMemory.test.js + shared/spokenMemory.test.js.
- eslint clean on the three touched relay files.
- Relay deployed (`npx wrangler deploy`, version 5299e9bc); `/health` → 200,
  `macBridgeOnline: true`.
