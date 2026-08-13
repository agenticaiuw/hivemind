# bench-dashboard — a local instrument for the breadboard

Owner's ask, 2026-08-13: "create a local dashboard where i can inspect the
values for each of the controls in a ui that makes the most sense when the nrf
chip is connected." They are wiring hardware and cannot tell a working wire
from a dead one by looking at it.

Two more asks arrived mid-session and are folded in below: move the "Ask the
hive" composer to the top of the main dashboard, and let the Mac play the audio
the pendant was supposed to speak.

## Files claimed by this agent

- `software/ai-pendant-simulator/local-agent/benchTelemetry.js` (+ test)
- `software/ai-pendant-simulator/local-agent/benchLink.js` (+ test)
- `software/ai-pendant-simulator/local-agent/benchRoutes.js`
- `software/ai-pendant-simulator/local-agent/server.js` — two lines only
- `software/dashboard-sveltekit/src/routes/bench/+page.svelte` (new)
- `software/dashboard-sveltekit/src/routes/+page.svelte` — composer move
- `software/dashboard-sveltekit/src/globals.css` — the `.ask` margin, moved with it

Read but never written: `firmware/nrf9160/**` (hw-selftest-2 owns it),
`cloud-relay/**` (ring-voice-2 owns it).

## Transport: the DK's UART console, not RTT

RTT was the first choice and lost on two facts:

1. It is not free of firmware work. `selftest/prj.conf` does not set
   `CONFIG_USE_SEGGER_RTT`, so RTT needs a firmware commit exactly like a
   `printk` loop does — and this agent may not edit that app. Its "needs no
   pins" advantage is also moot on a DK: the console already runs on P0.29 over
   an on-board trace, consuming no breadboard wire.
2. RTT takes the J-Link exclusively, and `west flash` fails while a logger is
   attached. hw-selftest-2 and the owner are flashing this board every few
   minutes. An instrument that blocks flashing is an instrument that gets
   turned off.

RTT remains implemented as a deliberate second path (`BENCH_TRANSPORT=rtt`,
JLinkRTTLogger into a spool file) for the day the console is needed elsewhere.

The console needed no firmware change at all, because the parser reads the
prose that is already printed — see below.

## What made it work today rather than after someone else's commit

Neither image emits machine telemetry. Rather than wait, the Mac side parses
the two consoles that already exist, into one snapshot:

- the self-test's console (`selftest/src/main.c`) — buttons, encoder detents,
  pot sweeps, mic power flips, mic peak/RMS, I2C ACKs, SD size, amp pad, ESP32;
- the pendant application's console (`src/main.c`) — `Volume: raw=N level=X.YY`
  at ~20 Hz, mic power sense, `STATUS mic MUTED`, the haptic probe, the SD
  driver's CMD0 errors, `I2S mic capture totals`.

Every rule quotes the `printk` it reads, so drift is findable. The machine
contract (`BENCH {...}`, one line at 10 Hz) is specified in the module header
and handed to hw-selftest-2; when it lands, nothing on this side changes,
because both parsers already feed the identical snapshot.

Proof it reads real bytes: a console capture taken off VCOM0 with the
application flashed was replayed through the parser and produced mic MUTED,
haptic silent, SD absent — all true of that board at that moment.

## The outage this feature caused, and the fix

Ten minutes after the first `/bench/snapshot` call, the relay reported
`macBridgeOnline:false` while the Mac's own `/health` stayed 200.

Cause was NOT contention and NOT route registration, both of which were the
first guesses. `fs.createReadStream` on a character device issues BLOCKING
`read(2)` on libuv's four-thread pool. Probing three silent VCOMs pinned three
of the four threads. Inbound HTTP is event-loop work so it kept answering,
while every outbound `fetch` to the relay begins with `dns.lookup` — pool work
— and starved. A bench toy took down a live path and looked healthy doing it.

Fixed by class, not by instance:

- the tty is read by a child `cat` per port; this process reads only a PIPE,
  which is event-loop I/O and uses no pool thread. A wedged port is one
  `SIGKILL` away instead of an unclosable fd.
- only an open `/bench/stream` opens a port. `/bench/snapshot` deliberately
  does not, so a curl cannot seize a tty. Released 10 s after the last
  subscriber; any port silent for 20 s is handed back.
- `lsof -t` before every open, excluding our own `cat` PIDs. A port held by
  anyone else is skipped and reported as "another process is reading … —
  standing off until it lets go", retried every 2 s.
- nothing is awaited on a startup path; `stty` and `lsof` carry 2 s timeouts.
- guard test: registering the routes performs no I/O and opens no port.

Verified on the relay, not locally: `macBridgeOnline=true` with the heartbeat
advancing across 8 consecutive polls.

hw-selftest-2 independently confirmed my reader had been shredding their
capture ("*** BootiDK v3.4.0-b **"). The stand-off rule exists so neither of us
has to ask again.

## Verdicts corrected on hw-selftest-2's measurements

They probed P0.30/31 over SWD: both held high against an internal pull-down,
with unwired P0.28 collapsing to LOW as the control. So a silent DRV2605L is a
question about the DEVICE, not about the bus or its 4.7k pull-ups — the note
now says "the bus itself reads healthy". Same for the SD: DO holds high, so
CMD0 silence reads "no card, or not seated — the breakout itself has power".
Both old wordings would have sent the owner after the wrong wire.

## UI

`/bench`, following DESIGN.md: the values are the whole page, few colours, no
button rows, nothing red — unwired and unseen are amber or grey, because a
missing wire is a question and not a fault. A pin that has never moved renders
its value muted with "not seen yet", since an unwired button sits HIGH against
its pull-up exactly like an untouched one (hw-selftest-2's point about P0.22).

Every tile carries its own age and the grid stands down visibly when the stream
stops, so stale values never pass as live. The self-test's 12 s microphone
window is reported as "not being polled" rather than as frozen.

Off the Mac the hardware grid is absent entirely — eleven tiles reading "—"
forever is worse than one sentence saying where the page works.

375 px verified by measurement: no horizontal overflow, two columns, dense
packing so the double-width tiles leave no hole beside them.

## Audio: hear what it should have played

Tier 1 shipped. Recent runs with a reply capture get a play control on the
bench page, through the existing `audioHref` (agent → `/pipeline/:id/audio/
output`, hosted → `/api/history/:id/audio`, relay key server-side). Provenance
is labelled and never blurred: "relay sent it" always, "the pendant played it"
only when `stageState(run,'playback') === 'done'`, otherwise "no playback
confirmed on the device" in amber. The relay sending bytes is not proof the
pendant played them.

Tier 2 (live monitor) is specified, not faked: `benchLink.monitorState()`
reports `available:false` with a reason until `BENCH_MONITOR_URL` exists, and
the page says so in words instead of rendering a control that cannot work. The
contract is in the report and in the code comment.

## Composer to the top

`<section class="ask">` moved above the answer card, and its separating margin
moved with it (`margin-top` → `margin-bottom`) so the move left no gap behind.
Order is now header → ask → needs-you → answer → recent. Measured 18 px header
gap and 24 px to the next block at both 1280 px and 375 px; one composer, mic
and LOCAL/RELAY chip and submit intact.

## Not fixed, flagged

The hero answer card renders "Couldn't do it" in red on the main dashboard.
DESIGN.md says never red text. Left alone to avoid colliding with whoever owns
that card this session.

## Follow-up: the header was lying, and the labels were stale

The owner's screenshot of /bench asked "why does it say listening and no
numbers are showing???" Two separate defects, both mine.

**"LISTENING" over eleven grey dashes.** The reader was healthy — three `cat`
readers on three VCOMs — and the board had simply never spoken, because no
flashed image emits these values. The page rendered "ports open, nothing ever
received" identically to "connected and idle", so the owner read it as wires he
had broken. Now the situation is computed from whole-life link totals
(`link.bytes` / `link.parsed`, which survive a board reset, unlike the per-boot
counts) and says which of these is true, in plain words and never in red:

- NO DATA YET — "Serial ports are open (3) and healthy, but the board has sent
  nothing at all. The firmware that reports these values is not flashed yet —
  this is not a wiring fault."
- UNRECOGNISED OUTPUT — bytes arrived, none parseable: a format mismatch, a
  completely different fix. Requires a line's worth of bytes (>40), because an
  idle VCOM drops the odd stray byte at open and one byte is not "talking".
- BOARD IDLE — parsed before, quiet now. Normal: the app's console only prints
  when a value moves.
- PORT BUSY / STOOD DOWN / nRF NOT CONNECTED / READER OFF.

**Stale control map.** The tiles taught the map the owner overruled. Corrected
at its single source (`BUTTONS` in benchTelemetry.js): yellow P0.21 is talk AND
push-to-talk, blue P0.23 is memo, green P0.22 owns nothing — its wires are off.
Green keeps its tile, since the pin level is still worth watching, but says
"wires off — reads the same either way" rather than "not seen yet": a floating
pin reads HIGH exactly like an unpressed one, so that tile cannot answer either
way and must not imply it is testing anything. Grepped the whole dashboard
package; no other surface carried the old mapping.

**Stand-down lever** for the firmware agent that needs the console:
`touch /tmp/pendant-bench-standdown` and this reader lets go within one 2 s
scan, no HTTP call and no token; delete it and the reader returns on its own.
The lsof guard remains as the automatic fallback, but it leaves a ~2 s window
where both readers are on the tty — enough to shred the first seconds of a
first-boot capture.
