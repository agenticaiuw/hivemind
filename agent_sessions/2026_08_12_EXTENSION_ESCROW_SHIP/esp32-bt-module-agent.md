# ESP32 Bluetooth-module strip — working log

Agent: esp32-bt-module-agent. Claims `firmware/esp32-airpods-bridge/**` only.
Ruling applied (owner, 2026-08-12, sharpened 2026-08-13): "the esp32 should
only do its own job of a bluetooth module." No device memory, no ranking, no
auto-reconnect, no name/address fallback, no hunting, no volume state. Every
decision moves to the nRF9160 — in the shipped product this chip is replaced
by a bare BT module that cannot make decisions.

## Starting state found

A prior pass (commit `6ab43e3`, agent `esp32-module-parity-agent`, logged in
`esp32-module-parity-agent.md`) had already stripped volume control and
bring-up instrumentation, and *was* committed (contrary to that log's own
"not committed" note — it got picked up in a later commit). Two later
commits (`33f14ae`, `5c2c71e`, both from other agents — ptt-uart-firmware and
button-grammar — who touched this file outside their claimed scope) added a
**name-keyed `connect` command** (`{"command":"connect","target":"<name>"}`)
plus a **one-entry address CACHE persisted to NVS** (`Preferences`,
`"addr"`/`"addrname"`) and a **30 s automatic re-page loop**
(`RECONNECT_INTERVAL_MS`) that ran without any command from the nRF. Both are
exactly the "second opinion" the owner's ruling forbids: memory that
survives a reboot, and a retry the nRF never asked for. This is the "prior
module-parity rebuild ... built but never flashed" the task pointed at —
except it *was* committed and (per repeated boot tests below) evidently not
reflecting the sharpened ruling. Confirmed by reading pendant_bt.c
(nrf9160, read-only — owned by nrf-bench-buttons): the nRF's `connect`
command sent `"target":"<name>"`, never an address, even though its own
4-entry LRU table stores both.

## What changed (`firmware/esp32-airpods-bridge/src/main.cpp`)

- **Removed** the NVS address cache entirely: `Preferences` object, its
  `begin()`/`getBytes()`/`getString()`/`putBytes()`/`putString()` calls, and
  the `#include <Preferences.h>`. Nothing on this chip survives a reboot now.
- **Removed** `RECONNECT_INTERVAL_MS` and the 30 s auto-page loop in
  `loop()`. A dropped/failed link is reported once; nothing pages again
  without a new `connect` command.
- **Removed** name-matching entirely. `targetMatches()` (renamed
  `reportDiscoveredDevice()`) now ALWAYS returns `false` — it only reports
  what a scan found, never selects or auto-connects to it.
- **`connect` now requires an explicit `addr`** (`"aa:bb:cc:dd:ee:ff"`,
  validated and rejected if malformed/missing/all-zero). A bare `target`
  name (the old shape) is explicitly rejected with `reason:"missing_addr"` —
  verified on the chip (see below). An optional `name` field is accepted
  purely as a cosmetic label for log messages; it is never compared against
  anything.
- **Added `disconnect`** (was missing before — only the stronger `forget`,
  which also unpairs, existed). Idempotent, closes the current A2DP link,
  clears the session-only commanded address.
- **`scan` now takes an optional `ms`** and self-terminates, reporting a
  `{"event":"scan_result","message":"...N device(s) reported."}` line
  instead of scanning forever (old behaviour never stopped on its own).
- **Every bridge event now carries `connected` (bool), `addr`, and `a2dp`**
  (the raw ESP-IDF connection-state name) in addition to the existing
  `state`/`message`. `target` is kept as an alias of `addr` for any bench
  tooling still reading it (documented: it is no longer ever a name).
- **New immediate command acks** for `connect`/`disconnect`:
  `{"type":"bridge","event":"connect","ok":bool,"addr":"...","reason":"..."}`
  — `ok` means "the command was valid and the page was issued", NOT "the
  link is up" (A2DP connect is asynchronous, sometimes several seconds). The
  definitive outcome still arrives as an ordinary unsolicited `state` event
  (`connected`/`searching`/`usb`), unchanged in spirit from before.
- Header comment rewritten to state the sharpened ruling and retire the
  rationale for the cache/retry it used to defend.

## Two real bugs found and fixed while proving this on the chip

1. **JSON line splicing.** `emitDocument()`/`Serial.println()` is called
   from two FreeRTOS tasks — Arduino's `loopTask` (commands, status,
   diagnostics) and the Bluetooth stack's own app task (straight out of the
   scan `ssid_callback`) — with no lock between them. Observed on the bench:
   `{"type":"bridge","event":"disconnect"true,"addr":...}` — a concurrent
   discovery line ate `,"ok":` out of the middle of a disconnect
   acknowledgement. This is not a truncation the nRF's parser already
   tolerates by contract; it is a splice, which can pass a naive check and
   be read wrong. **Fix:** a `SemaphoreHandle_t serialLock` mutex now guards
   every write inside `emitLine()`. Also lowered `CORE_DEBUG_LEVEL` from 3
   to 1 in `platformio.ini` — the framework's own `ESP_LOGx` output shares
   the same UART0 peripheral as `Serial` outside of any lock we control, and
   at level 3 the volume of unrelated log lines made this materially more
   likely; a module shouldn't be spewing internal library chatter on its
   own port anyway.
2. **Connect-after-restart race.** The original code paged a cached address
   500 ms after `a2dp.start()` — a margin I dropped when refactoring
   `pageCachedAddress()` into `beginConnect()`. Without it, `connect_to()`
   can run before the A2DP profile has finished registering after
   `a2dp.start()` (or before a preceding `a2dp.end()` has fully settled),
   and fails silently and immediately (`connect_to()` returns `false`,
   no HCI attempt is even made) — observed live as
   `{"event":"connect","ok":false,"reason":"page_not_issued"}` against a
   known-good, powered-on speaker. **Fix:** restored the 500 ms settle
   before `connect_to()`, and added the same 300 ms settle after
   `finishScan()`'s own `a2dp.end()` (mirroring what `resetA2dpSession()`
   already did on its own teardown path, which `finishScan()` bypassed).
3. **Scan duration floor.** The vendored ESP32-A2DP library hard-codes a
   `delay_ms(10000)` in its own stack-up handler before it ever calls
   `esp_bt_gap_start_discovery()`. A `scan` bounded shorter than ~10.5 s
   reports zero devices *every time*, regardless of what's nearby — this is
   why 6 s and 9 s scans both came back empty while a 15 s scan found the
   speaker. This is a hardware/library constraint, not a bug I could fix in
   this file; instead `SCAN_MIN_MS` is now 11000 and `SCAN_DEFAULT_MS` is
   15000 (was 8000). **The `ms:5000` example in the original task spec does
   not work on this hardware — say so plainly rather than silently keep a
   default that always fails.**

## Verified on the real chip (HUZZAH32, `/dev/cu.usbserial-0287A9CA`)

Built and flashed three times over the course of fixing the two bugs above;
final flash confirmed via `esptool` hash verification. All bytes below are
copy-pasted from the actual serial session (USB console; UART2 to the nRF
carries byte-identical JSON per `emitLine()`, not independently observed —
see caveat below).

**status (cold boot, nothing commanded):**
```
>>> {"command":"status"}
<<< {"type":"bridge","state":"usb","connected":false,"addr":"","a2dp":"disconnected","target":"","message":"USB ready; no Bluetooth activity."}
```

**legacy name-only connect correctly rejected (proves the name-matching hole is closed):**
```
>>> {"command":"connect","target":"SoundCore 2"}
<<< {"type":"bridge","event":"connect","ok":false,"addr":"","reason":"missing_addr","message":"The connect command needs a valid \"addr\" like \"aa:bb:cc:dd:ee:ff\"; a name is not enough."}
```

**scan (default, now 15000 ms) found the owner's speaker:**
```
>>> {"command":"scan"}
<<< {"type":"bridge","state":"searching","connected":false,"addr":"","a2dp":"disconnected","target":"","message":"Scanning for nearby Bluetooth audio devices for 15000 ms."}
<<< {"type":"discovery","state":"searching","device":"SoundCore 2","address":"e8:09:59:19:93:40","rssi":-41,"message":"Found \"SoundCore 2\" (-41 dBm)."}
<<< {"type":"bridge","state":"usb","event":"scan_result","connected":false,"addr":"","a2dp":"disconnected","target":"","message":"Scan finished; 22 device(s) reported."}
```
**RECORDED ADDRESS: SoundCore 2 = `e8:09:59:19:93:40`** (RSSI -38 to -48 dBm
across multiple scans — clearly the strongest/closest device, consistently
named). One other MAC (`ec:3a:56:ba:43:5b`) reported "SoundCore 2" a single
time out of ~20 sightings and "DESKTOP-9E48SIM"/"CHU" every other time —
almost certainly a nearby laptop's EIR name transiently misread, not a
second speaker. `e8:09:59:19:93:40` is the address to use.
**Per the owner's ruling this address is NOT written anywhere in this
firmware as a default/fallback/constant — it lives only in this log and
belongs on the nRF's LRU table (`firmware/nrf9160/src/pendant_bt.c`,
`/SD:/btsinks.idx`).**

**connect by address (after the settle-delay fix), and genuine A2DP up:**
```
>>> {"command":"connect","addr":"e8:09:59:19:93:40","name":"SoundCore 2"}
<<< {"type":"bridge","event":"connect","ok":true,"addr":"e8:09:59:19:93:40","message":"Paging e8:09:59:19:93:40 (\"SoundCore 2\"). Device must be on and not connected elsewhere."}
... (searching for several seconds) ...
<<< {"type":"bridge","state":"connected","connected":true,"addr":"e8:09:59:19:93:40","a2dp":"connected","target":"e8:09:59:19:93:40","message":"Bluetooth speaker connected. A2DP is streaming."}
<<< {"type":"diagnostic",...,"a2dp_state":2,...}
```
`a2dp_state:2` is the raw `ESP_A2D_CONNECTION_STATE_CONNECTED` enum read
directly off the ESP-IDF Bluetooth stack — not this file's own label.
Confirmed stable and repeated across 25+ seconds of continuous polling, not
a blip.

**disconnect (tested once, on the run BEFORE the coordinator asked me to
leave a live connection up — not re-tested afterward, deliberately, per
instruction):**
```
>>> {"command":"disconnect"}
<<< {"type":"bridge","event":"disconnect","ok":true,"addr":"e8:09:59:19:93:40","message":"Disconnecting the current Bluetooth link."}
<<< {"type":"bridge","state":"searching","connected":false,"addr":"","a2dp":"disconnected","target":"","message":"Bluetooth disconnected."}
```
(This exact sequence is what first exposed the JSON-splicing bug — the very
first disconnect attempt, pre-mutex-fix, produced
`{"type":"bridge","event":"disconnect"true,"addr":...}`. Re-run after the
mutex fix produced the clean lines above.)

**No memory across reset — proven empirically, repeatedly, not asserted
from reading the code.** Every one of the 4 reflashes in this session is a
full chip reset. Every single time, the following `status` came back:
```
<<< {"type":"bridge","state":"usb","connected":false,"addr":"","a2dp":"disconnected","target":"","message":"USB ready; no Bluetooth activity."}
```
— no address, no "was connected to X" anywhere. This is by construction
(no NVS write exists anywhere in the file any more), not by luck.

## What is proven vs. not

**Proven, on the real chip, over USB:** `status`, `scan` (bounded, with the
corrected minimum), `connect` by explicit address (both the reject-path for
a name-only command and the accept-path with a real speaker, genuine A2DP
up), `disconnect`. The radio and the new address-only protocol work.

**NOT proven: that the pendant (nRF9160) can drive this.** Per a message
relayed through the coordinator, an earlier hardware pass found the
nRF-to-ESP32 UART (P0.00 TX / P0.05 RX) is **not physically wired** — no
jumpers on the board. Everything above was driven directly from this Mac
over the USB debug port (`Serial`, UART0), which is wired and always was.
UART2 (`moduleSerial`, the wire the nRF actually uses) carries byte-identical
output from the same `emitLine()` call, so the protocol itself is proven —
but I have no second probe on UART2 to independently confirm bytes actually
land there, and if the physical link is missing, the nRF has no path to send
these commands at all regardless of firmware correctness. That gap needs two
jumper wires from the owner and is outside this chip's firmware.

**Not re-tested:** `forget` (unpairs — would have dropped the live
connection the coordinator told me to leave up; its code path is a small,
unmodified-in-logic superset of `disconnect` — unbond after disconnect —
so it is lower-risk than an untouched command, but genuinely unverified this
session). `route`/`tone` — unchanged in logic from before this task, not
re-tested.

## Bug #3: connected but silent — a2dp_frames stuck at 0 forever

Found live, at the owner's explicit request to actually hear the speaker
("so we can test"). Connecting by address (bug #2's fix) genuinely opened
the Bluetooth profile connection — `status` correctly showed
`connected:true`/`a2dp_state:2` — but `provideA2dpFrames()` was never once
invoked: `a2dp_frames` in the diagnostic line stayed at exactly 0 through a
full `{"command":"tone"}` cycle.

**Root cause:** the vendored ESP32-A2DP library's own internal state
machine (`s_a2d_state`, private to `BluetoothA2DPSource`) is what actually
drives the AVDTP media-start handshake (`ESP_A2D_MEDIA_CTRL_CHECK_SRC_RDY`
then `..._START`, in its 10 s heartbeat timer) — and that state machine only
reaches its own "connected" state via two paths: a discovery match (never
happens here — `reportDiscoveredDevice()` always returns `false`, by
design), or `set_auto_reconnect(addr, retries)` called *before* `start()`,
which makes the library's own `start()` page `addr` through the FSM path a
discovery match would have used. A bare `a2dp.connect_to(address)` — what
`beginConnect()` did — calls `esp_a2d_connect()` directly; it opens a real
profile connection (confirmed by the raw connection-state callback, which
is independent of the library's internal FSM) but is invisible to the state
machine that gates whether audio ever gets requested. This is not
documented anywhere in the library; it was found by connecting a real
speaker and watching frame counters stay at zero.

**Fix:** `beginConnect()` now calls `a2dp.set_auto_reconnect(commandedAddr,
0)` before `a2dp.start()`, instead of calling `connect_to()` itself.
Retries pinned to **0** is the load-bearing detail: the library's own
reconnect-on-drop logic (`handle_reconnect_logic()`, gated on
`reconnect_retries > 0`) can then never fire on a later disconnect — the
*first* page, at `start()` time, is unconditional and still happens (that
check does not gate it), but nothing pages again without another `connect`
command. This keeps the "no auto-reconnect, retry nothing on its own"
contract exactly as before; it just routes the one connection this chip is
allowed to make through the call the library actually requires in order to
also start streaming audio. `resetA2dpSession()` no longer calls
`a2dp.start()` itself — callers (`beginScan`/`beginConnect`) set
`set_auto_reconnect` first and start the stack themselves, since the two
commands need different values.

**A real, load-bearing side effect:** this path also makes the connection
progression visible as a proper `connecting` → `connected` transition (raw
`a2dp_state` 0 → 1 → 2), where the old direct-`connect_to()` path jumped
straight 0 → 2 with no visible `connecting` state — further evidence the
library's FSM was never engaged before.

**Verified on the chip**, reconnecting to the same recorded address after a
reflash:
```
>>> {"command":"connect","addr":"e8:09:59:19:93:40","name":"SoundCore 2"}
<<< {"type":"bridge","event":"connect","ok":true,"addr":"e8:09:59:19:93:40","message":"Connecting to e8:09:59:19:93:40 (\"SoundCore 2\"). This hardware takes roughly 10 s to begin paging after a restart; device must be on and not connected elsewhere."}
... a2dp_state: 0 for ~10s, then ...
<<< {"type":"bridge","state":"searching","connected":false,"addr":"e8:09:59:19:93:40","a2dp":"connecting","target":"e8:09:59:19:93:40","message":"Bluetooth target found; opening the A2DP link."}
<<< {"type":"bridge","state":"connected","connected":true,"addr":"e8:09:59:19:93:40","a2dp":"connected","target":"e8:09:59:19:93:40","message":"Bluetooth speaker connected. A2DP is streaming."}
```
Then, once connected, `a2dp_frames` climbed continuously on its own
(~44,000/s, matching the 44.1 kHz output rate — silence, since nothing feeds
real audio in without the nRF's I2S link):
```
<<< {"type":"diagnostic",...,"a2dp_frames":351872,...}
<<< {"type":"diagnostic",...,"a2dp_frames":881024,...}   (12s later)
```
Then, isolating the built-in test tone (bypasses I2S/the nRF entirely, a
real 440 Hz square wave at -25 dBFS for 3 s — deliberately not full-scale,
per the existing code comment, since the owner was sitting next to the
speaker):
```
BEFORE: a2dp_frames = 1,499,648
>>> {"command":"tone"}
<<< {"type":"bridge",...,"message":"Playing a three-second ESP32-direct Bluetooth test tone."}
AFTER (through the tone's window): a2dp_frames = 1,942,144, confirmed
climbing continuously throughout
```
This agent has no way to independently confirm audibility (no microphone/
ears) — the owner, at the bench, is the actual confirmation. Every
measurement available says the tone was genuinely delivered to the
Bluetooth stack during that window: real connection, real streaming state,
real frame delivery, real (if brief and quiet) signal.

**Consequence for `beginConnect()`'s ack timing:** because the page itself
now happens inside the library's own `start()` internals, connecting takes
noticeably longer than the earlier (broken) direct-`connect_to()` path felt
like — roughly 10 s of nothing (the same hard-coded `delay_ms(10000)` noted
under the scan-duration finding above) before the library even issues its
first page, then normal A2DP negotiation on top. The `connect` ack message
now says this plainly ("takes roughly 10 s to begin paging after a
restart") so nrf-bench-buttons doesn't read a long `searching` window as a
hang.

## Bug #4: `set_auto_reconnect(addr, 0)` was not actually retry-free

Found under direct challenge from the coordinator ("prove it behaves, do not
assert it") after bug #3's fix introduced `set_auto_reconnect(commandedAddr,
0)` into `beginConnect()` — a function whose name is the exact policy the
owner ordered removed. The retries=0 argument narrows one branch, but
`set_auto_reconnect`'s OWN header doc (`BluetoothA2DPSource.h`, not just the
.cpp guard I'd read before) says plainly: "If active is true, will retry up
to max_retries times before falling back to scanning." Reading
`handle_reconnect_logic()` in full confirmed it: when `reconnect_status ==
AutoReconnect` and retries are exhausted (immediately, since 0 already is),
there is a SECOND branch that does not retry the same peer, but does call
`esp_bt_gap_start_discovery()` on its own — the library keying the radio
into an unrequested scan on the first heartbeat after any disconnect,
commanded by nobody. `reportDiscoveredDevice()` always returning `false`
means this can never auto-*connect* to anything, but a scan the nRF never
asked for is still this chip acting on its own.

**Fix:** `onConnectionState()` — the raw connection-state callback, which
`process_user_state_callbacks()` invokes BEFORE the library's own FSM
switch runs for that same event — now calls `a2dp.set_auto_reconnect(false,
0)` the instant it observes `CONNECTED` (and defensively on `DISCONNECTED`
too, covering the case where `CONNECTED` is somehow never observed).
Because this runs before the library's own switch for the identical event,
`reconnect_status` is back to `NoReconnect` before `handle_reconnect_logic()`
can ever read it as `AutoReconnect` — both its branches (retry, and the
discovery fallback) require that value, so both are unreachable for the
rest of the session. `set_auto_reconnect(addr, 0)` is used for exactly one
purpose now: routing the ONE `start()` call in `beginConnect()` through the
path that also arms the library's own audio-start handshake (bug #3), and
it is disarmed within the same event cycle that job completes. A long
comment at both call sites (the arm in `beginConnect()`, the disarm in
`onConnectionState()`) names the owner's ruling, quotes the library's own
doc comment, and tells the next person not to raise retries above 0 or
leave `reconnect_status` armed any longer than that one call.

**Re-verified deliberately, not inferred from before this change:**
reflashed with this fix in place, then checked `status` on a fresh boot
before sending any command:
```
<<< {"type":"bridge","state":"usb","connected":false,"addr":"","a2dp":"disconnected","target":"","message":"USB ready; no Bluetooth activity."}
```
Reconnected to the same recorded address afterward and confirmed
`a2dp_frames` still climbs normally (the disarm does not cost the working
audio path from bug #3).

**Not yet verified: the actual uncommanded-drop case (the coordinator's
item 1).** That needs the speaker to drop for a reason this chip did not
choose — powered off, or out of range — while watching for ~30+ s (2-3 of
the library's own 10 s heartbeats) for any unrequested `{"type":"discovery"}`
line or re-page. That requires physically touching the owner's speaker
mid-session; coordinating timing with the coordinator/owner before doing it
per their explicit request, rather than causing it unilaterally.

**Flagged, not fixed (out of scope for this task):** once connected,
`a2dp_frames` climbs continuously at ~44,000/s even with nothing to send —
the A2DP stream just pushes silence forever. That is a genuine idle power
cost on a battery-wearable (a Bluetooth radio kept busy transmitting silent
frames). Whoever owns audio-source policy (the nRF, per this same ruling)
should probably suspend/stop the stream when there is nothing to say; this
chip only executes what it is told, so it is not this chip's decision to
make on its own, but it is worth someone deciding.

## Sizes

Flash 86.0% → 84.9% after the CORE_DEBUG_LEVEL drop (smaller, not just
safer). RAM 23.7%, essentially unchanged (Preferences removal, mutex, and
address-parsing code roughly offset each other).

## Files touched

- `firmware/esp32-airpods-bridge/src/main.cpp`
- `firmware/esp32-airpods-bridge/platformio.ini` (CORE_DEBUG_LEVEL 3 → 1)

Did not touch `firmware/nrf9160/**` (owned by nrf-bench-buttons) or any
other agent's claimed files.
