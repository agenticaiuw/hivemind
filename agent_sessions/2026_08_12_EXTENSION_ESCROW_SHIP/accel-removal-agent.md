# Accelerometer removal agent — working log

Owner ruling: "we're not using the accelerometer anymore." Task: surgically
delete the LSM6DSOX double-tap integration from the nRF9160 firmware.

## Claimed files (per delegation, exclusive)

- firmware/nrf9160/src/accel_tap.c (deleted)
- firmware/nrf9160/src/accel_tap.h (deleted)
- firmware/nrf9160/src/main.c
- firmware/nrf9160/CMakeLists.txt
- firmware/nrf9160/boards/nrf9160dk_nrf9160_ns.overlay
- firmware/CONTROLS_WIRING.md
- hardware/BREADBOARD_WIRING.md

Did NOT touch: firmware/nrf9160/src/pendant_status.c, src/haptic.c/.h,
boards/nrf9160dk_nrf52840.overlay, prj.conf, or anything under software/.
Grepped `accel_tap` repo-wide (excluding build-*/ artifact dirs, which
another agent regenerates on next build) — the only hit outside owned/
build-artifact paths is this session's own sensors-firmware-agent.md log,
which is historical and untouched.

## What was removed

1. `git rm firmware/nrf9160/src/accel_tap.c firmware/nrf9160/src/accel_tap.h`.

2. `firmware/nrf9160/CMakeLists.txt`: dropped `src/accel_tap.c` from
   `target_sources(app PRIVATE ...)`.

3. `firmware/nrf9160/src/main.c`:
   - Removed `#include "accel_tap.h"`.
   - Removed the P0.27 row from the pin-map comment block (the
     "---- Sensor/audio additions ----" header now lists only the volume
     pot and amp SD entries).
   - Removed `accel_double_tap_isr()` and its preceding explanatory
     comment (was lines ~1014-1024). Confirmed `button_press_sem` (the
     semaphore it gave) is still used extensively elsewhere — line 971
     (ptt path uses a different sem; button 1's own ISR), 1634, 2512,
     3993, 5011, 5020, 5029, 5142 — so no dangling/unused semaphore was
     left behind, and the yellow-button / button-1 path is fully intact.
   - Removed `(void)accel_tap_init(accel_double_tap_isr);` and rewrote
     the adjacent comment from "Volume knob (SAADC) and double-tap wake
     (I2C2): both probe-once, both degrade..." to a single-feature
     version describing only the volume knob.
   - Grepped main.c for `accel|lsm6|double.tap|double_tap|tap` after
     edits. Remaining `tap` hits are all false positives unrelated to the
     accelerometer: `tx_resample_taps.h`, `TX_FIR_TAPS`/`tx_fir_*` (the TX
     FIR resampler's filter taps), and the LED-blink phrase "three fast
     double-taps" in `report_mic_muted_press()`'s comment (describes the
     mic-muted LED pattern, not the removed gesture). None reference the
     deleted symbols.

4. `firmware/nrf9160/boards/nrf9160dk_nrf9160_ns.overlay`:
   - Removed the `accel_int1` node (and its preceding comment) from
     `pendant_controls`.
   - Removed the `accel-int1 = &accel_int1;` alias.
   - **Sense-edge-mask bit arithmetic** (verified with a Python one-liner
     doing bit decomposition, not just editing the hex by eye):
     - **Before:** `0x0be00000` — bits set: 21, 22, 23, 24, 25, 27.
     - **After:** `0x03e00000` — bits set: 21, 22, 23, 24, 25.
     - Only bit 27 (P0.27) was cleared; bits 21-25 (buttons/encoder)
       untouched. Updated both the constant and the prose above it
       ("Bits: P0.21-25.") and added a new paragraph mirroring the
       existing P0.28 paragraph's style/tone: "P0.27's bit is GONE too
       (0x0be00000 -> 0x03e00000) with the accelerometer: ..."
   - Updated the uart0-pinctrl comment (~line 197-213) that listed P0.27
     as "now the accelerometer's INT1" — now reads "held the
     accelerometer's INT1, now unclaimed by anything," matching how the
     same paragraph already treated P0.28.
   - Updated the RX-pin-choice historical comment (~line 390-401,
     "RX = P0.05 ... Every other candidate was taken when this was
     chosen") which listed "P0.26/27 = mic sense / accelerometer INT1" —
     split so P0.27 reads "held the accelerometer's INT1 then and is free
     now," mirroring the existing P0.28 clause right next to it.
   - Updated the I2C2 comment block (~line 479-499): "Two breakouts share
     the bus" -> "One breakout lives on the bus"; removed the `0x6A
     LSM6DSOX accelerometer` row from the address list; removed
     "double-tap wake -> buttons only" from the degrade-mode sentence.
     Kept the I2C2 bus itself and the DRV2605L haptic entry at 0x5A
     exactly as instructed.

5. `firmware/CONTROLS_WIRING.md` — more references existed than the
   three call-outs in the brief, so all were fixed for internal
   consistency (this file is mine to edit in full):
   - Main wiring table: haptic row now says "Sole device on I2C2"
     (was "Shares I2C2 with the accelerometer"). The `Accelerometer` and
     `Accelerometer INT1` rows were replaced with a single strikethrough
     row, following the same pattern the doc already uses for the
     retired encoder-push row: `| ~~Accelerometer~~ | *not used* | — |
     — | **Removed 2026-08-13 by owner ruling** (...). **P0.27 is FREE**
     ... |`.
   - "The Bluetooth module UART" paragraph (~line 163-169): split the
     "P0.26/27 are the mic sense and the accelerometer INT1" clause so
     P0.27 gets its own "held ... then and is free now" note, matching
     the P0.28 clause beside it.
   - "Interrupt budget" paragraph: dropped P0.27 from the edge-interrupt
     pin list and reworded to explain both P0.27 and P0.28 leaving the
     mask; dropped the "(and a double-tap, slower still)" aside.
   - "Console is TX-only now" paragraph: now says freeing P0.26/27/28
     "keeps P0.27 and P0.28 genuinely claimable" (was only P0.28).
   - I2C bus table (`## I2C bus` section): removed the LSM6DSOX row.
   - Pull-ups paragraph: reworded from "two breakouts"/"both breakouts"
     to describe the single remaining haptic breakout; removed the
     "double-tap wake simply disappears" clause from the probe-once
     summary.
   - Haptic effect map table: "Press acknowledged (yellow/tap-tap, ...)"
     -> "Press acknowledged (yellow, ...)" — dropped the tap-tap alias
     (caught by a broader `tap` grep beyond the task's named hit list;
     `double.tap`-style patterns don't match "tap-tap").
   - Firmware/relay contract table: removed the "Accelerometer
     double-tap | identical to a yellow press ..." row entirely.
   - Left untouched (false positive, unrelated): "three fast
     double-taps" in the mic-muted paragraph — describes the LED blink
     pattern, same as in main.c.

6. `hardware/BREADBOARD_WIRING.md`:
   - Removed the `ACC["motion sensor: accelerometer\nLSM6DSOX"] -- "I2C
     0x6A · INT1 → P0.27" --> DK` mermaid line (node + edge were declared
     inline on one line, so removing the line removes both).
   - I2C bus table: replaced the Accelerometer row with a strikethrough
     "REMOVED" row noting P0.27 is free, in the same style as the
     Encoder-push row already in the Controls table.
   - Removed the entire "**motion sensor · LSM6DSOX accelerometer**"
     per-component pinout block (VIN/GND/SCL/SDA/INT1/DO,CS,INT2,I1 rows).

## Grep sweep — hits found outside owned files (reported, not edited)

Ran `grep -rniE "accel|lsm6dsox|lsm6|double[_-]tap|0x6A"` across the whole
repo (excluding .git, build dirs, node_modules, agent_sessions). Outside
the seven owned files, the true (non-"acceleration"/"accelerator"
false-positive) hits are:

- `docs/Breadboard_Wiring_Guide.html:120,123,124` — an HTML wiring guide
  with its own "4. LSM6DSOX IMU (I²C, optional)" section, calling out
  address 0x6A and noting "the DK already has an accelerometer." This is
  the closest cousin to the two docs I edited and is the one most likely
  to want the same treatment.
- `docs/Prototyping_Shopping_List.html:40,44,100` — shopping-list mentions
  of "an accelerometer" (dev-board feature) and a "6-axis IMU — LSM6DSOX"
  line item.
- `docs/Component_Datasheets.html:185-201` — reference links to the
  LSM6DSO and LIS2DH12 datasheets, labeled "optional accelerometer + gyro."
- `hardware/design/Design_Package_v1.md:54,55,61,83` — production-PCB
  design notes for a *different* component: the Actinius Icarus SoM's
  **onboard** accelerometer (I2C addr 0x19, INT on P0.28/P0.29 in that
  board's own numbering) plus the DRV2605L. Not the breadboard LSM6DSOX
  breakout at 0x6A — likely out of scope, but grep caught it.
- `hardware/design/Concepts_Primer.md:60` — I2C primer example using
  "onboard accel = 0x19" (same Icarus onboard part) as a teaching example.
- `hardware/design/Watch_Variant_Study.md:218` and
  `hardware/design/Solar_Feasibility.md:141` — power-budget entries for a
  **different** part, LIS2DH12, in speculative watch-variant / solar
  studies, not the breadboard build.
- `hardware/datasheets/IcarusSoM_datasheet_Actinius.md:6,12,64,65` —
  reference copy of the Icarus SoM datasheet describing its built-in
  LIS2DH12 and P0.28/P0.29 INT pins (that SoM's own pin numbering, not
  this repo's DK overlay pins).
- `docs/hardware/respin-speaker-mute-secure-element.md:402,518,800,801` —
  a hardware-respin planning doc discussing the SoM's onboard
  accelerometer at 0x19 and something at address 0x6A "alongside the
  DRV2605L (0x5A) and the accelerometer (0x19)" — worth a second look by
  whoever owns that doc, since 0x6A is exactly the breadboard LSM6DSOX
  address, but I did not investigate further since it's not an owned
  file.
- `docs/hardware/pendant-v2.md:335,465,823` — a forward-looking v2
  hardware doc proposing a **different** IMU (BMI270) for a planned
  "IMU double-tap on the shell" gesture in a future revision. Reads as
  intentionally separate from today's breadboard removal, not a stale
  reference to the deleted code.

False positives (not accelerometer-related, left alone): 
`firmware/nrf9160/README.txt:153` ("optional acceleration" = encoder
speed, not the sensor); `docs/iCloud_Access.md` (two "accelerator" hits,
unrelated); `software/ai-pendant-simulator/...` (`X-Accel-Buffering` HTTP
header, and an unrelated "accelerator" code comment).

## Verification (no build run, per instructions)

- `git status --short` on the seven owned paths shows exactly: 2 deletions
  (accel_tap.c/.h) and 5 modifications (main.c, CMakeLists.txt, the
  overlay, and the two markdown docs). No other files touched.
- `git diff` reviewed in full for all five modified files — confirmed
  brace/structure integrity of the devicetree (`pendant_controls` node
  still closes cleanly after removing `accel_int1`), and confirmed no
  half-edited comment blocks.
- Repo-wide `grep -rln "accel_tap"` restricted to real source/doc file
  extensions (excluding `build*/` artifact directories, which another
  agent regenerates) returns nothing except this log file itself.
- `main.c` has zero references to the deleted `accel_tap_init`,
  `accel_tap_available`, or `accel_double_tap_isr` symbols.
- Confirmed `button_press_sem` (the semaphore `accel_double_tap_isr` used
  to give) remains fully wired through the real button-1/yellow-button
  path — nothing there depended on the accelerometer's ISR.

## Sense-edge-mask summary (for the report)

- Before: `0x0be00000` (bits 21, 22, 23, 24, 25, 27 armed)
- After: `0x03e00000` (bits 21, 22, 23, 24, 25 armed — P0.27 cleared)
