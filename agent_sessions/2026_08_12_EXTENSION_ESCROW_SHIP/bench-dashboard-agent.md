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

## Follow-up: real firmware telemetry, and a bug the firmware agent found in me

nrf-bench-buttons shipped the `BENCH` emitter and the pipeline ran end to end
against real hardware: `link.state: streaming` on /dev/cu.usbmodem...811,
`source: bench-json`, 1307 bytes, 9 parsed lines, uptime 331381 ms, every
control populated from raw pad levels. Their two captured lines are now a test,
pasted byte for byte.

**Their bug report was correct and was mine.** `openReader` ran `stty` and then
spawned `cat`. On macOS a `cu.*` device's termios is reset when the FIRST
reader opens it, so the `stty` was undone by the open that followed it and
`cat` read a port that had quietly reverted to 9600 — nothing, or a few dozen
bytes of garbage. They lost three captures to it and ruled out contention with
lsof. The reader is now one `sh -c` that holds the fd open first (`exec 3<port`),
sets the line discipline second, and `exec cat <&3` third, so the setting
survives. Device paths are validated against a strict pattern before they go
near a shell.

That also means my "the board has sent nothing at all" empty state was partly
self-inflicted: some of that silence was this bug, not silent firmware.

Three wording corrections from what they measured:

- an empty `i2c` list is never a verdict on the bus. It now reads "nothing
  answered — the bus itself reads healthy, so this is about the part", and
  "intermittent — it answered earlier on this board, then stopped" once an
  address has ever ACKed. That one fact deliberately survives a reboot reset,
  because the DRV2605L attached on one boot (0xe4) and refused on the next
  (-116), and intermittent is a different diagnosis from absent.
- `sd.mounted:false` is the firmware's own write test failing, not a missing
  card: "the card answers — the firmware's own write test is what did not pass".
- an absent `esp` means the app halts in `show_error()` before
  `pendant_bt_init()`, so the tile says "not probed yet" in amber rather than
  rendering as a failure.

A test caught a flake of its own making: it read the real
/tmp/pendant-bench-standdown while the firmware agent was holding the console,
so the stand-down path is now per-instance. Fixing that surfaced a genuine gap
— with the open attempted optimistically, a link whose readers all exit was
still reporting "probing" forever; it now falls back to "no port would open —
the DK is unplugged".

Watch item for the owner: mic sense reads LOW on every boot, which says the
red switch is cutting the mic — the owner believes it is ON. One flip of that
switch while /bench is open settles it, and the tile is live for exactly that.

## Owner ruling: the bench is local-only, so it is not built for the Worker

"remember that the bench should only be available locally."

The self-describing hosted page did not satisfy that. It still shipped the
whole instrument to a public URL — tiles, SSE client, and the literal device
paths (`/dev/cu.usbmodem0009600365811`) baked into its empty-state copy. Hidden
is not absent, and publishing the port names on the owner's desk is a leak
nobody asked for.

The route is now excluded at build time rather than at render time. A Vite
plugin (`benchIsAgentOnly` in vite.config.ts) replaces the page component with
an empty one for every target except `DASHBOARD_TARGET=agent`, so Rollup has
nothing to bundle; `src/routes/bench/+page.ts` redirects the hosted URL home so
nothing renders bench chrome either. Both gate on the same compile-time flag
`hooks.server.ts` already uses, so the agent build folds them away.

Measured, per build:

| | hosted node 3 | agent node 3 |
| --- | --- | --- |
| size | 264 B (redirect + empty component) | 15,515 B (the instrument) |
| `usbmodem` | 0 files | 1 |
| `bench/stream` | 0 | 1 |
| `bn-tile` | 0 | 2 |

**Stated plainly, because it is checkable:** SvelteKit builds its route table
from the filesystem and has no supported per-build route exclusion, so the
hosted manifest still carries an empty `/bench` entry and the URL redirects
rather than 404s. The code behind it is gone, which is the part that mattered.

Leak audit of the hosted surface: no nav link anywhere points at /bench, there
are no `/bench/*` API routes under src/routes/api, and no prerender entry. The
only `bench` match elsewhere in src/ is the word "Benchmark" in hiveFeed.js,
unrelated. **The Mac agent's own routes are the only backend the bench has ever
had** — /bench/snapshot and /bench/stream exist solely on the local agent, and
nothing relay-side proxies them.

Live verification of Worker 985ab1fb, against the deployed bytes rather than
the build config: all 15 client chunks fetched and byte-identical to the local
build, none containing `usbmodem`, `bn-tile`, `bench/stream` or `NO DATA YET`;
the publicly served /bench node is the 264-byte redirect stub; GET /bench
returns 302 to /login with a zero-byte body and no bench chrome. The
authenticated path 307s home per the deployed module's own source, which I read
from the served chunk — I did not sign in to exercise it.

Agent build re-verified working at http://127.0.0.1:8000/dashboard/bench: 11
tiles, and correctly showing STOOD DOWN while the firmware agent holds the
console.

## The links: "is this thing talking to anything"

Owner: "add the debugs to the bench on the status of the mics and connections
to the remote agents and also lte connection, etc."

### Where it went, and why

Below the controls grid, not above it. The controls are the main feature and
DESIGN.md says the main feature holds the most visual field: the owner reads
them while looking up from a breadboard with a wire in his hand, several times
a minute. Connectivity gets checked when something is already wrong, which is
far rarer, so putting a wall of status text above the tiles would invert the
hierarchy for the sake of the less-used answer. Smaller type and a tighter tile
say the same thing a second way — the row reads as one glance, not as eleven
readings.

Measured at 1280x800: controls grid 536 px, links strip starts at y=702 in one
row of six, so its top is visible without scrolling and the controls still own
the screen. At 375 px it is three rows of two, no overflow, nothing clipped.

The mic is deliberately NOT repeated in this row. It already owns two of the
largest tiles above — the sense pin and the level — and DESIGN.md is explicit
about not repeating what adds no value. What it needed was honesty, not a
second home: the level tile now reads "level not reported yet" instead of a
bare dash, because "muted" and "powered but hearing nothing" are different
problems with different fixes and the page could only answer the first.

### The contract (mine; firmware conforms)

Slow line only — this is status, not pads:

    "lte":{"reg":"home","op":"AT&T","rsrp":-95,"rsrq":-9.5,"band":12,
           "mode":"ltem","cell":"01A2B3C4"}
    "sock":{"up":true,"idle":1450}
    "bt":{"conn":true,"name":"SoundCore 2","addr":"AA:BB:CC:DD:EE:FF"}
    "mic":{"sense":1,"peak":91234,"rms":560}

`lte.reg` is a string mapping 1:1 onto +CEREG <stat> so the firmware translates
the modem's number rather than inventing wording. `rsrp`/`rsrq` are sent
already converted to dBm/dB — the index arithmetic is a modem detail and must
not live in two places. `sock.idle` is ms since the socket last carried
anything either way, because "up but silent for 40 s" is the state most worth
seeing and `up` alone cannot express it. Sent to nrf-bench-buttons.

### Absent is not zero, enforced in the shape

Every link carries `reported`. A key the firmware has never sampled is omitted,
lands as null, and renders "not reported yet" in grey — never as a measured
failure. `sock:{"up":false}` is a claim; omitting `sock` says nothing has
measured it, and those must not look alike. Nothing here is red: a radio that
has not registered yet is not a fault, and `searching` / `denied` /
`not-registered` are kept apart because they have different causes.

### Working on day one, without waiting for firmware

pendant_cloud.c already prints the modem's raw AT answers, so LTE and Bluetooth
partly work now: `+CEREG` gives registration and cell id, `+CESQ` gives both
signal figures with 255 correctly staying unknown rather than becoming a very
bad reading, and the BT lines give the sink's name and address. "BT sink
remembered" is parsed as remembered and NOT as connected — it is the pendant
writing a speaker into its list, which it does whether or not the speaker is
powered on. The tile says "remembered, not reached" for exactly that state.

### Remote agents: the existing source, not a new one

The Mac bridge, relay and browser extension come from `fetchSnapshot()` — the
same /ops/snapshot the rest of the dashboard reads. Two probes of the same
three things drift, and then the bench and the home page disagree about whether
the bridge is up, which makes both untrustworthy rather than one of them wrong.
Live: all three UP, with "claiming work", "reachable" and "1 device".

## The 811 bug: a latch, not a flake

The owner pressed a button, saw nothing, and said so. The bench held 813 and
815, had never opened 811 — the only port the board prints to — and reported
"streaming" over the silence.

One line in `scanSerial`:

    if (this.winner && this.readers.has(this.winner)) return

The instant any port produced a parseable line, all scanning stopped forever.
811 was held by the firmware agent at that moment, so it was skipped once; a
stray byte on 813 then elected 813 the winner and closed the rest; and 811 was
never retried — not when they released it, not when the stand-down file went
away, not until a restart. "6 attempts" were six opens of the two ports that
had never been busy.

Fixed as a class: every closed port is retried on every scan; `consolePortOf()`
identifies VCOM0 as the lowest-numbered cu.usbmodem instead of treating three
ports as equals; the console outranks whoever spoke first, and the others are
released only once the console itself is the winner; a new `console-missing`
state makes "streaming with the console unread" unrepresentable, with the
`live` branch gated on `consoleOpen` too; and the console is never reaped for
being quiet, which was a second way to lose it.

Verified on the page, not on a field: nRF CONNECTED, winner ...811, pot moving
171-190, LTE ROAMING / AT&T / -82 dBm / b12 — independently matching the
firmware agent's own SWD measurement.

## The raw line tap replaces the stand-down file

The stand-down dance blanked the owner's bench twice in fifteen minutes, and it
was never necessary: a flash and every JLinkExe measurement go over SWD through
the J-Link's own USB interface, a different channel from the console. Reading
text was the only thing that ever needed the tty, and this process already does
that continuously. So the bench owns the ports permanently and everyone else
subscribes:

    GET /bench/lines               SSE, one raw console line per message,
                                   in arrival order, tagged with its port
    GET /bench/lines?after=N       backlog since sequence N, as JSON
    GET /bench/lines?format=text   backlog as newline-delimited text, to grep

Raw rather than parsed, because consumers grep for printk text this parser has
no rule for ("Injected frame:", "microSD unavailable (mount=0 write=-2)"). The
500-line backlog is replayed before any live line, so an agent attaching a
second after a reset still catches the boot banner. A plain GET returns the
backlog and ends — only `stream=1` holds the connection open, so a one-shot
curl cannot hang.

**The one exception, and it is an exception rather than a second path:** if this
agent process is not running there is no tap, and an agent that needs the
console must open the tty directly — otherwise a broken dashboard would mean no
firmware diagnosis at all. Check `curl -sf localhost:8000/health` first; if it
answers, use the tap and do not touch the port.

The first fragment after attaching is dropped. A reader opens mid-transmission,
so its first bytes are the tail of a line that began before we were listening;
publishing it produced exactly the corruption the first live capture showed
(`..."pot":{"raw":166` glued to `STATUS mic MUTED`). One truncated line at
attach is a known cost of tailing a live stream; a fabricated one is not.
