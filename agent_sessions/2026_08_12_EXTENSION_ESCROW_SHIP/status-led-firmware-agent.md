# status-led-fw — unified RGB + haptic status subsystem (nRF9160)

Owner ask: a plain 4-leg RGB LED that "works with the haptic driver" — ONE
feedback system, not two features.

## Claimed files
- firmware/nrf9160/src/pendant_status.{c,h}  (new)
- firmware/nrf9160/src/main.c                (state-transition call sites only)
- firmware/nrf9160/CMakeLists.txt            (one target_sources line)
- firmware/nrf9160/Kconfig                   (polarity flag)
- firmware/nrf9160/boards/*.overlay          (pin claims)
- firmware/CONTROLS_WIRING.md
- hardware/BREADBOARD_WIRING.md

NOT touched: haptic.c/haptic.h (reuse only), audio path, cloud-relay,
local-agent, esp32 project.

## Findings before writing code
- CONFIG_PWM, CONFIG_LED, CONFIG_INPUT are all OFF in this build: PWM0 has no
  Zephyr driver bound, and the board's led1/led2/button1 DT nodes are inert.
  PWM1/PWM2 are driven by raw nrfx HAL from main.c (mic BCLK/LRCLK) — PWM0 is
  free, and raw-HAL-on-a-DT-disabled-instance is the established house pattern.
- P0.03 = DK silkscreen LED2, P0.04 = LED3, P0.07 = Button 2. All three are
  routed through the nRF52840 board controller's analog switches, so the
  board-controller overlay must open them (same move the UART made for LED4).
- PWM duty word bit 15: SET = output HIGH for `compare` ticks (Zephyr's
  PWM_POLARITY_NORMAL), CLEAR = LOW for `compare` ticks. So common-anode vs
  common-cathode is exactly one bit.

## Log
(appended as work proceeds)

## What shipped

**New: `src/pendant_status.{c,h}`** — one enum, one setter, both channels.

State machine shape:
- `status_sticky` (IDLE / RECORDING / THINKING) — the last state set is what
  the device is.
- `status_approval` — a LATCH, not a slot. That is what makes the precedence
  table real rather than decorative: the relay can announce an approval while
  a recording is live, and the amber blink has to outrank the red. Cleared by
  any terminal transition (idle / done / failed).
- `status_muted` — latched from a `bool (*)(void)` probe (`mic_power_is_cut`)
  polled by the work item, so the mute indicator is continuously true rather
  than true only at press time.
- `status_transient` (DONE / FAILED) + start timestamp — plays its flash and
  falls back to the sticky state.
- Resolver reads the precedence list literally, top to bottom:
  `muted > approval > recording > thinking > transient > idle`.
- Entry/exit haptics fire ONLY from `status_enter()` / `status_event()`,
  which run inside the work item. Callers write an atomic (state+1, so 0 can
  mean "nothing requested" without swallowing IDLE) and reschedule.

Verified numerically (host harness, `scratchpad/env.c`): thinking breath =
2 breaths / 3 s; muted breath = 2 breaths / 6 s; approval blink = 520 ms on
per second, ~4 Hz; failed = 120 on / 120 off x3 over 720 ms; full level maps
to 25.0 % duty.

**PWM**: PWM0, channels 0/1/2, raw nrfx HAL, `NRF_PWM_LOAD_INDIVIDUAL`,
125 kHz / countertop 256 = 488 Hz. PWM1/PWM2 untouched (audio clocks).
`&pwm0` disabled in devicetree so no `pwm_nrfx` can bind and apply
`pwm0_default` (which would put PWM_OUT0 on P0.02, the on-board LED).

**Polarity**: `CONFIG_PENDANT_RGB_COMMON_ANODE`, default n. It selects bit 15
of the duty word (SET = pin HIGH for `compare` ticks) plus the parked-dark
GPIO level. Both variants compile clean; the anode branch was compile-checked
separately by re-running its compile_commands entry with the macro forced.

**Two behaviours deliberately changed in main.c:**
1. The capture-stop buzz used to be tick-for-memo / click-for-command, fired
   directly. It is now `pendant_status_set(THINKING)` on the same button
   edge, so the red light drops and the exit tick fires as ONE transition,
   and every capture closes the same way.
2. The `approval_readback` handler's bare `haptic_trigger(STRONG)` became
   `pendant_status_set(APPROVAL)` — amber 4 Hz blink + strong x2.

**Left alone on purpose**: the press-acknowledgement haptics (yellow/green/
blue press, encoder push, muted press, conversation-end press). Those are
press acks, not status; they fire on the edge before any radio work, which
is a stated house value. A conversation ended by button therefore gives
click (heard you) then, after teardown, tick (mic closed) — two real events,
not a double-fire.

**Measurements** (build-ptt at 15:52 = pre-change baseline, same method):
- RAM  204,834 -> 204,925 B = **+91 B** (96.80% -> 96.84%), 6,683 B free.
  The +91 is exactly the sum of pendant_status.o's .bss, so nothing else
  drifted.
- FLASH 409,836 -> 411,612 B = **+1,776 B** (69.48% -> 69.79%).
- Linker's own report for build-rgb: FLASH 414,524 B (70.28%), RAM
  204,940 B (96.85%). Under the 97% ceiling.

Not flashed, not committed (per instructions). Note the working tree also
carries another agent's concurrent edits under
`software/ai-pendant-simulator/local-agent/` — not mine, not touched.
