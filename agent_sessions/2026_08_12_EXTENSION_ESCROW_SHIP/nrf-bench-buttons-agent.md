# nrf-bench-buttons-agent

Claims: `firmware/nrf9160/**` (released by hw-selftest after ba04e7d).
Must not touch: `software/dashboard-sveltekit`, `software/ai-pendant-simulator/local-agent` (bench-ui owns them).

Two tasks:
- **A** — the SHIPPING app emits `BENCH {json}` bench telemetry so bench-ui's dashboard has a signal source.
- **B** — task #26, the nRF half of context-sensitive buttons (`menu_context` → yellow=select / blue=back while a ring is open; global verbs otherwise).

---

## 2026-08-13 — orientation

### Serial port coordination (done first, on purpose)

`lsof /dev/cu.usbmodem0009600365811` → `cat` pid 45096, parent pid 39857 =
`AI Pendant Agent.app` running `local-agent/server.js`. That is bench-ui's
`BenchLink` reader (`benchLink.js` spawns one `/bin/cat` per candidate VCOM).
So the console is held by the agent, not by a human tail.

Good news from reading `benchLink.js`: it already implements the standoff I
would otherwise have had to negotiate by hand.

- `foreignHolders()` runs `lsof -t <port>` on every 2 s rescan and, if anyone
  else holds the tty, it `closeReader()`s and reports
  `another process is reading … — standing off until it lets go`.
- `reapIdle()` drops every reader 10 s after the last `/bench/stream`
  subscriber goes away.

So the protocol on this bench is: **when I need the console I take it and the
agent stands off within 2 s; when I let go it takes it back within 2 s.** I
never run two readers of my own. Recorded here so the next agent does not
re-derive it.

### The parser is the contract (`benchTelemetry.js`)

Read in full. Firmware must conform to it, not the reverse:

- Prefix `BENCH ` then one JSON object. Every key except `v` optional; lines
  MERGE into a running snapshot, so **absent ≠ zero**, absent = "not reported".
  This is exactly the honesty rule I was told to respect — omit, never fake a 0.
- `btn` keys are `p21`/`p22`/`p23` (or the bare pin number), values are **RAW
  PAD LEVELS** 1=HIGH / 0=LOW. `pressed`, `presses` and `edges` are DERIVED in
  the parser from level transitions — firmware must NOT pre-derive them
  (`noteButtonLevel`, and the comment at line 43: a firmware that pre-derives
  hides the reading that separates "unpressed" from "wire fell off").
- `enc`: `a`, `b` raw levels; `pos`, `det`, `cw`, `ccw` counters.
- `pot`: `{raw}` only — 12-bit SAADC count. percent/volts derived host-side.
- `mic`: `{sense}` raw level (+ optional peak/rms).
- `i2c`: array of 7-bit addresses **as numbers** (90 = 0x5a).
- `sd`: `{present, bytes, sectors, mounted}`. `amp`: 0/1 pad readback.
  `esp`: "ok" | "silent" | "partial". `fw`: string. `up`: `k_uptime_get()` ms.
- The text rules for the *pendant app's* existing printks still run alongside
  the JSON (`applyLine` tries the JSON prefix first, then every text rule), so
  `I2S mic capture totals: … peak= rms=` keeps feeding the mic-level tile for
  free. No need to duplicate that in JSON.

### Firmware as it stands (`firmware/nrf9160/src/main.c`, 5411 lines)

- Controls are all **edge-ISR** driven, configured in `configure_control_inputs()`
  (line 4619): yellow P0.21 → `button_press_sem` (shares button 1's ISR),
  green P0.22 → `memo_press_sem`, blue P0.23 → `ptt_press_sem`, all
  `GPIO_INT_EDGE_TO_ACTIVE` (active-low, so the ISR fires on the FALLING edge
  only — there is no release interrupt).
- Encoder P0.24/25 → `encoder_edge_isr`, `GPIO_INT_EDGE_BOTH`, Gray-code table,
  one menu step per ±4 transitions (already "one detent = one unit").
- Pot P0.15/AIN2 → `volume_poll()`, ~20 Hz one-shot SAADC, hysteresis 82 counts.
- Mic sense P0.26 → polled `gpio_pin_get_dt`, no interrupt, no pull.
- `grep -ri bench firmware/nrf9160/src` → nothing. Confirmed: the shipping app
  emits no BENCH line today. The instrument really is pointed at silence.

Consequence for the design: a 5 Hz poll (the idle loop's cadence) **cannot see
a 90 ms button tap**. So the press has to be latched in the ISR and drained by
the emitter, not sampled. Written down because it is the one non-obvious part.

---

## TASK A — done, flashed, verified on the board

### What was built

- `firmware/nrf9160/src/bench.h` / `bench.c` — the emitter. No thread, no timer,
  no buffers; it runs on loops that already turn. +1,860 B flash, +348 B RAM,
  352 B of stack in its one non-trivial function.
- `firmware/nrf9160/Kconfig` — `PENDANT_BENCH_TELEMETRY`, default y, idle-cheap.
  Every call site compiles to nothing when it is `n` (the header supplies no-op
  inlines), so `main.c` carries no `#ifdef`.
- Hooks in `main.c`: the three button ISRs, the encoder ISR, `volume_poll`,
  the haptic probe, the SD gate, and `pendant_bench_tick()` on the idle loop,
  the conversation loop and — see below — `show_error()`.
- `pendant_bt.c/h` — `pendant_bt_module_state()`, an honest ok/partial/silent
  for the ESP32's serial link, counted in the UART ISR (the only place that
  sees the bytes the line filter throws away).

Emission is change-driven with a **2 s** heartbeat and a 150 ms floor, plus a
10 s slow line for `fw`/`i2c`/`sd`/`esp`.

The 2 s figure is not taste. `benchSnapshot()` computes `stream.connected` as
"a line parsed less than 3000 ms ago", so the 5 s heartbeat I first wrote would
have rendered a healthy idle pendant as a disconnected one between changes —
the instrument reporting its own silence as the board's.

### Three things that cost real time, recorded so nobody repeats them

**1. The "shredded stream" is a macOS termios trap, not a second reader.**
My first three captures gave 0 bytes, then 54 bytes of garbage. It looks
exactly like the stream-splitting the brief warned about, and it is not:
macOS resets a `cu.*` device's termios when the FIRST reader opens it, so the
conventional `stty 115200 …` **then** `cat` order sets the speed on a port that
is about to be reset back to 9600 underneath it. Hold the fd open first, then
set the line:

```sh
exec 3</dev/cu.usbmodem0009600365811
/bin/stty -f /dev/cu.usbmodem0009600365811 115200 raw -echo cs8 -parenb -cstopb clocal
/bin/cat <&3 > capture.txt &
```

Saved as `scratchpad/capture.sh`. `lsof` during the capture confirmed only my
own `cat` held the port, so this was never contention. Worth flagging to
bench-ui: `benchLink.js:openReader` does `configurePort()` (stty) and *then*
`spawn('/bin/cat', …)`, which is the losing order — their "board has sent
nothing at all" may be this same trap rather than silent firmware.

**2. A 5 Hz poll cannot see a button.** The buttons interrupt on the ACTIVE
edge only; there is no release interrupt, and the idle loop turns every 200 ms.
A 90 ms tap falls entirely between two samples. So the ISR **latches** the edge
and the emitter drains the latch, reporting the pad at the active level rather
than re-reading a pad the finger already left. Without this the owner's press
is invisible — the exact verdict they are trying to tell apart from a dead wire.

**3. The board was parked in `show_error()`, so telemetry stopped at boot.**
`last_fast_ms` read back over SWD as 285 ms and never moved: the emitter ran
once from `pendant_bench_init()` and never again. The app halts before its idle
loop (see the blocking finding below). A pendant in a dead boot is *precisely*
when the owner is about to go poking at wires, so `show_error()`'s forever-loop
now calls `volume_poll()` + `pendant_bench_tick()`. That is what turned this
from "one boot sample that ages out" into a live instrument.

### Verified by the real parser, on real captured bytes

Not by reading code. I drove P0.21, P0.22 and P0.23 LOW in turn over SWD
(`DIRSET`/`DIRCLR` on the NS GPIO alias — driving LOW only, which is
electrically what the button itself does), captured the console, and fed the
bytes to the actual Mac parser:

```
yellow  P0.21  level=1  presses=1  edges=2  moved=true
green   P0.22  level=1  presses=1  edges=2  moved=true
blue    P0.23  level=1  presses=1  edges=2  moved=true
```

One press each, no cross-talk between pins, `source=bench-json`. This proves
the ISR → latch → emit → parse path end to end. It does **not** prove the
owner's external wiring — a pin driven by the chip and a pin pulled down by a
button look identical from inside. Only a finger settles that.

### Live values, owner's hardware as-is (2026-08-13)

| control | reading | what it means |
|---|---|---|
| yellow P0.21 | HIGH, steady | resting **or** unwired — indistinguishable by level alone |
| green P0.22 | HIGH, steady | same; wires are known to be off, and this is why the raw level is shipped instead of a `pressed` boolean |
| blue P0.23 | HIGH, steady | resting or unwired |
| encoder A/B P0.24/25 | both HIGH, 0 detents | never moved — nobody turned it |
| pot P0.15 | `raw=0`, dead steady | **suspicious.** Real reading, taken before the volume curve's snap/hysteresis |
| mic sense P0.26 | **LOW**, 0 changes | firmware believes mic power is cut — contradicts the owner's "red switch is ON" |
| haptic 0x5a | **intermittent** | one boot "attached (status=0xe4)", next boot "not answering (-116)" |
| amp P0.01 | 0 | correct: bluetooth sink is the boot default = amp in shutdown |
| ESP32 | omitted | app dies before `pendant_bt_init()`, so there is nothing honest to say |

Nothing was pressed, turned or flipped during these captures because no human
was at the bench. "Never moved" here means "never exercised", not "dead".

### BLOCKING FINDING — the shipping app halts at boot

```
I: Maximum SD clock is under 25MHz, using clock of 2000000Hz
E: file open error (-2)
E: file open error (-2)
microSD is required for Internet voice upload
```

`mount_sd_card()` succeeds — the card answers and the FAT volume mounts — but
`test_sd_persistence()`'s `fs_open("/SD:/power_test.bin", FS_O_CREATE|FS_O_WRITE|FS_O_TRUNC)`
returns `-2` (ENOENT), so `sd_ready` is forced false and `show_error()` never
returns. Reproduced on every boot. The pendant reaches its idle loop **never**:
no LTE, no WebSocket, no Bluetooth, no button actions.
