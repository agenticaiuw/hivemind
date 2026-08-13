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

---

## TASK A2 (coordinator-assigned, taken ahead of B) — the boot gate

### The proximate bug, measured rather than guessed

`CONFIG_FS_FATFS_LFN` was **not set**, so FatFs enforces 8.3 short names and
returns `FR_INVALID_NAME` for anything longer. Zephyr's
`subsys/fs/fat_fs.c:translate_error()` folds that into `-ENOENT` **in the same
case arm as `FR_NO_FILE`**:

```c
case FR_NO_FILE:
case FR_NO_PATH:
case FR_INVALID_NAME:
	return -ENOENT;
```

That is why the errno looked self-contradictory: a CREATE that fails with "no
such file". It was never about the card.

**Six paths were over 8.3 and had therefore never worked:**

| path | why it fails 8.3 | what it broke |
|---|---|---|
| `power_test.bin` | base is 10 chars | **the boot gate** — halted the whole device |
| `recipes.json` | ext is 4 chars | the reflex layer's entire persistence |
| `latest.opus` | ext is 4 chars | Opus journal |
| `selftest.opus` | ext is 4 chars | selftest journal |
| `agent_reply.audio` | base 11, ext 5 | reply audio download |
| `agent_reply.pcm` | base is 11 chars | decoded reply playback |

Fix: `CONFIG_FS_FATFS_LFN=y`, `LFN_MODE_BSS`, `MAX_LFN=64` — measured **+152 B
RAM, +3.0 kB flash**. Renaming six paths was the alternative and is worse:
`recipes.json` is a name the relay, the docs and any hand-written card all
share, so 8.3 would have to be re-derived by every future author from an errno
that actively misleads.

**Proof on the board:** flashed LFN-only, no other change → the SD self-test
passed, `sd_ready` stayed true, and the boot ran through to
`Pendant LTE connection ready (attach 8 s)` / `LTE OK — ready for button`.
The device had been dead at boot; it is alive.

### The design flaw, which mattered more

`show_error()` never returns. One optional peripheral was taking down LTE, the
WebSocket, Bluetooth, every button, the status vocabulary and the whole menu
grammar. Storage now costs **only storage**:

- The gate logs what was actually lost — the offline outbox, the alert inbox,
  and the capture journal used when there is no live uplink at press time —
  and says plainly that conversation, buttons, LTE and Bluetooth are
  unaffected. With a live uplink (the normal case) recording never touches the
  card at all; that branch already existed in `record_microphone`.
- It announces on the existing local vocabulary — `PENDANT_STATUS_FAILED`,
  three red blinks and a two-part buzz — rather than inventing a signal nobody
  has been taught.
- It queues `{"type":"device_degraded","subsystem":"storage","lost":[…]}` for
  the converse socket. **Deliberately NOT drop-when-closed**, unlike every
  other frame in that group: a menu twist banked across a dead link is stale
  intent, but "your storage is gone" is still true an hour later.
- The boot's two-slow-flashes "card OK" signal is now gated on `sd_ready`. It
  was firing unconditionally, which would have made the degraded boot actively
  tell the owner something false.

**Honest limit:** this firmware plays audio only inside a started conversation,
so there is no way to speak a sentence at boot. The device half of the spoken
announcement is done; the relay half (turning that frame into
"Storage unavailable; I can still talk, but I can't upload recordings") is
ring-voice-2's and does not exist yet. Until it lands the announcement is
local-only — LED, buzz, console, bench.

**Fault injection, because reasoning about a failure path is not testing it:**
built `build-nosd` with `CONFIG_FS_FATFS_LFN=n` to reproduce the exact original
failure, and captured:

```
microSD unavailable (mount=0 write=-2) — voice upload journal, offline outbox
and alert inbox are OFF for this boot; conversation, buttons, LTE and
Bluetooth are unaffected
…
Pendant LTE connection ready (attach 6 s)
LTE OK — ready for button
```

A pendant with a broken card now boots, attaches and connects to the relay.

### A second bug the fault-injection run exposed: 34 phantom bookmarks

The degraded capture showed bursts of `Bookmark dropped: seq=57,58,59` and
`Outbox full — evicting seq=51`, with 34 marks queued that no human made.

`gpio_is_ready_dt()` checks the **port** device, never the node's status. The
DK's Button 2 node (`sw1`) is `status = "disabled"` in the overlay because its
pin went to the RGB status LED — but the macro still resolves to gpio0 pin 7,
gpio0 is ready, so the firmware happily armed an `EDGE_TO_ACTIVE` interrupt on
**P0.07, the pin `pendant_status.c` drives as the blue channel through PWM0**.

The chain: mic reads muted → muted breathes blue → every PWM edge on P0.07
fires the bookmark ISR → the device fills its own durable outbox with events
the owner never caused, evicting real ones to make room.

Fixed with `DT_NODE_HAS_STATUS(MARK_BUTTON_NODE, okay)`. Verified: **34 → 0**
phantom bookmarks, 0 evictions, and the boot now says
`Bookmark button not present on this board`.

This one only surfaced because the mic reads muted on this board. It would have
been invisible on a board whose mic sense reads high.

### show_error() audit — every remaining forever-loop

Seven call sites. One fixed; the rest listed as asked, with an assessment.

| line | trigger | verdict |
|---|---|---|
| 4893, 4898, 4904, 4909 | DK Button 1 (`sw0`) not ready / configure / callback / interrupt fails | **Low risk, wrong in principle.** `sw0` is on-board so it does not fail in practice — but the external yellow button shares this semaphore, so a dead on-board button bricks a device whose real button works. |
| 4985 | `!device_is_ready(i2s)` | **Defensible.** No I2S means no record and no play; the device's whole purpose is gone. Still silent on a screenless device. |
| 5015 | SD gate | **FIXED** — degrades and announces. |
| 5118 | boot capture self-test failure (`PENDANT_BOOT_AUDIO_CYCLE_TEST` only) | Harness-only, not a production path. |
| 5141 | `pendant_cloud_init()` — LTE attach failed | **The worst one left, and it contradicts a shipped design.** `PENDANT_OFFLINE_STORE`'s stated purpose is that the pendant "can be present and remember while the link is down". A pendant that bricks itself in a dead zone is the exact opposite. Not changed here: the idle loop assumes an initialised modem, so making it survive needs care and its own verification pass. **Recommend it as the next task.** |

### The junk runs in the owner's feed — same bug, downstream

While this was being fixed the owner watched eight "Untitled run · Didn't catch
that" rows appear in two minutes. The suspicion was my SWD button presses; it
was not. Those presses happened while the board was still parked in
`show_error()`, so the semaphore was never consumed, and all three boot
self-test auto-press flags are 0.

It was the phantom bookmarks above, plus my own SD fix. The 34 marks nobody
made were sitting in the durable outbox; the LFN fix gave the device a relay to
drain them into. A bookmark carries no audio, so the relay gets a run with no
transcript ("Untitled run") and nothing to recognise ("Didn't catch that"), one
per idle pass — which is what a drain loop looks like and what a human does not.

Contained: generator fixed, backlog empty (`pending=0 next_seq=104`), fixed
image on the board.

### Bench probe mode — testing a button must be free

Every button test was costing the owner a junk run in his own history and real
cloud spend, on a board whose mic is unpowered so the capture is silence
anyway. New SWD hook, same idiom as `pendant_remote_press`:

```
w4 <&pendant_bench_probe> 1    arm
w4 <&pendant_bench_probe> 0    disarm
```

Armed, a press is fully **observed** and fully **inert** — the ISR still
latches the edge and the BENCH line still carries the raw pad level, so the
wire question is answered exactly as well as before; only the conversation,
memo, push-to-talk and bookmark are withheld. It sits after
`clear_button_events()` so a probe press cannot be banked and replayed on
disarm. Verified live: three presses, three correct identifications, zero
conversations, zero captures, zero uploads.
