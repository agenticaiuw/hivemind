# ptt-uart-fw — blue button becomes push-to-talk, nRF gains a Bluetooth module UART

Agent: `ptt-uart-fw` (firmware). Owns `firmware/nrf9160` and
`firmware/esp32-airpods-bridge`. Did **not** touch `cloud-relay` (owned by
another agent this session) — relay-side needs are listed as TODOs below.

## Task A — blue button (P0.23) = PUSH-TO-TALK

Approve/deny is gone from the firmware entirely. The blue button now:

1. **Press** — starts a capture with the **radio off**. New latch
   `capture_radio_off` skips `pendant_cloud_stream_ensure()` inside
   `record_microphone()`, so the modem is never brought to connected mode
   while the human talks; the mic journals to the microSD card exactly as it
   does when there is no live uplink.
2. **Press again** — stops. One chunked `POST /v1/pendant/command?dispatch=1`
   with `X-Reply-Stream: opus` (the existing non-duplex shape; **no new
   transport**), fed from the SD journal through the *same* live encoder +
   FIFO + pump machinery a yellow press uses. Feed and pump interleave
   because the FIFO is ~7 KB and a 30 s question is ~60 KB.
3. **Reply** — `stream_end()` returns `PENDANT_CLOUD_REPLY_INLINE`; the new
   `ptt_reply_play()` pulls 2-byte-BE length-prefixed Opus packets off the
   same socket and plays them through the conversation's own downlink path
   (same decoder, 24 kHz jitter ring, 96/125 TX resampler, sync preamble).
   Whatever `audio_sink` currently selects (ESP32/Bluetooth or the
   MAX98357A) hears it — no new audio code.
4. Socket closes; radio back to idle. **One RRC connection per question.**

**WHY (cited in the code, `Solar_Feasibility.md` §4.3):** PTT question =
0.94 mWh vs 2.3 mWh for the same question as a short duplex exchange —
2.4× cheaper, because radio-off capture is 4.2 mA against the modem's
~65 mA connected floor, and every radio touch pays a ~0.32 mWh RRC
connection tax (which is why it is one connection, not upload-then-fetch).

Edge cases, all implemented:
- **Mic hard-muted:** same suppression as yellow/green —
  `{"type":"mic_muted"}` + triple double-blink + long buzz, no capture.
- **During an OPEN duplex conversation:** ignored with a haptic tick
  (`ptt_press_ignored_in_conversation`). No mode mixing — a conversation
  already owns the mic, the I2S transfer, both codecs and the socket.
- **Offline:** new outbox kind `PENDANT_STORE_KIND_QUESTION` = `'Q'`,
  distinct from memo's `'T'`. Redelivers with the planner **ON**. The reply
  cannot play later (its socket is gone), so both the header comment and a
  runtime log line say the answer lands in history, not in the ear.

## Task B — Bluetooth policy on the nRF + UART command link

**Pin verdict (audited against the overlay, not assumed):**

| Line | Pin | Why it is legal |
| --- | --- | --- |
| nRF UART TX | **P0.00** → ESP32 GPIO16 (RX2) | VCOM2 group, but this repo already ships `boards/nrf9160dk_nrf52840.overlay` with `vcom2_pins_routing` **disabled**, so the IMCU's analog switch is open. P0.01 has driven SD_MODE on that same basis for weeks. **Hard dependency:** stock board-controller image ⇒ IMCU drives P0.00 and fights every start bit. |
| nRF UART RX | **P0.05** ← ESP32 GPIO17 (TX2) | Highest unused DK LED pin. Verified in `nrf9160dk_nrf9160_common.dtsi`: led0=P0.02 (the firmware's only LED, via `DT_ALIAS(led0)`), led1/2/3 = P0.03/04/05, none of 03–05 driven. |

**LED tradeoff, stated:** DK **LED4 is gone**. I also disabled
`led4_pin_routing` in the board-controller overlay (it is a real analog
switch — `nrf9160dk_nrf52840.dts` line 88), which takes the LED off the net
and makes P0.05 a clean input. Left routed it still works at 115200, but
LED4 glows on the idle-high line and an unpowered ESP32 lets the LED string
pull RX low into a permanent break. P0.03/P0.04 left free for a future
second indicator. Verified in the generated DTS: `fun=0 P0.00` (TX),
`fun=1 P0.05` (RX), `current-speed = 115200`.

`CONFIG_UART_INTERRUPT_DRIVEN=y` — uarte's `poll_in` restarts a one-byte
reception per call, so bytes arriving between polls are lost; unacceptable
for a device that reports scan results unprompted. TX stays `poll_out` (no
TX buffer allocated).

**New module `src/pendant_bt.{c,h}`** (kept out of main.c, already 4.9k lines):
- 4-entry sink table (name 24 B + address 18 B), index 0 = preferred.
  Insertion at the front / eviction from the back **is** the LRU policy.
  Persisted to `/SD:/btsinks.idx` with magic + checksum — no settings
  subsystem, no NVS.
- Only a **connection** reorders the table (the only proof an entry is
  reachable); discovery just fills the menu.
- Boot and `audio_sink` → bluetooth/both command the preferred sink; nothing
  remembered ⇒ scan. 60 s backstop re-page, stops once a sink answers.
- Converse-socket frames: emits
  `{"type":"bt_devices","devices":[{index,name,address,preferred}],"connected":bool}`
  on `{"type":"bt_list"}`; accepts `{"type":"bt_select","index":N}`.
  Frames are parsed on the WS thread but only set flags — the UART, the card
  and the table are main-thread-only.
- One 128 B RX line buffer, single-slot: the ISR stops filling once a line
  is complete and discards until main takes it, so producer and consumer are
  never in the buffer together. A type-prefix filter in the ISR drops the
  module's 1 Hz health line so it cannot hold the slot against real events.

**ESP32:** UART2 (GPIO16 RX2 / GPIO17 TX2, 115200 8N1) accepts the identical
command set as USB via one shared `handleCommand()`, and every event is
mirrored to both ports through `emitLine`/`emitDocument`. Module-parity note
in the header: a BM83-class module has exactly this UART — **UART2 is the
real interface; USB is debug only**. Event field order was reordered so
`device`/`address` (and `target`) come **before** the human-readable
`message`, because the nRF truncates at a fixed line length; the nRF's parser
additionally rejects any value whose closing quote fell outside the buffer,
so a truncated address reads as absent rather than being remembered wrong.

## Builds

| Image | Result |
| --- | --- |
| nRF9160 (NCS v3.4.0, `build-ptt`, pristine) | **RAM 204,844 / 211,608 B = 96.80 %**, **FLASH 412,728 / 576 KB = 69.97 %** |
| ESP32 (`pio run`) | SUCCESS — RAM 23.7 % (77,696 B), Flash 86.1 % |

**RAM note — the stated 96.34 % baseline needed re-measuring.** `build-sensors`
is a stale artifact. I built HEAD clean in the scratchpad: HEAD = 203,860 B =
96.34 %. My first build landed at 205,996 B = 97.35 %, over the ceiling.
1,536 B of that was **not** new code: `http_stream_buffer` in
`pendant_cloud.c` had always been dead — nothing called
`pendant_cloud_reply_read`, so `--gc-sections` deleted it and the reported
figure never paid for it. Playing an inline reply makes it live. Cuts:

- `HTTP_STREAM_READ_SIZE` 1536 → 512 (−1024 B). It is a recv() batch size,
  nothing structural; costs ~40 extra offloaded-socket reads spread over a
  15 s reply.
- `BT_LINE_MAX` 256 → 128 (−128 B), paid for by the ESP32 field reordering.

Net +984 B over HEAD.

## Relay TODOs (cloud-relay is another agent's — coordinate)

1. **`bt_list` / `bt_select` sender.** The OS-menu half. Device answers
   `bt_list` with `bt_devices` and acts on `bt_select` today; nothing sends
   them. Index is 0-based, 0 = preferred, max 4 entries.
2. **PTT question labelling.** The upload is the ordinary
   `?dispatch=1` + `X-Reply-Stream: opus` shape, so the relay needs no
   change to work — but there is no `X-Pendant-Mode` on it, so the dashboard
   cannot distinguish a PTT question from a yellow-button command. If that
   distinction is wanted, say so and I will add a header.
3. **Offline `'Q'` redelivery** arrives as an ordinary
   `?dispatch=1` PCM upload with no reply socket. The relay may want to mark
   those jobs "answer not delivered to device" so history reads honestly.
4. **`approval_readback` sender** (pre-existing TODO, now more important):
   with the blue button gone, the strong haptic on that frame is the whole
   device-side cue that the next words want an answer. Approvals are
   voice-answerable and dashboard-answerable only.
5. **`audio_sink` sender** (pre-existing TODO) — selecting bluetooth/both
   now also triggers a module connect, so it is the relay-side lever for
   "reconnect my headphones".

## Files changed

- `firmware/nrf9160/src/main.c` — PTT capture/upload/playback, approval state
  machine removed, BT wiring, radio-off capture latch
- `firmware/nrf9160/src/pendant_bt.{c,h}` — **new**
- `firmware/nrf9160/src/pendant_store.{c,h}` — kind `'Q'`
- `firmware/nrf9160/src/pendant_cloud.c` — `HTTP_STREAM_READ_SIZE` 1536→512
- `firmware/nrf9160/boards/nrf9160dk_nrf9160_ns.overlay` — `ptt_button`, uart1
- `firmware/nrf9160/boards/nrf9160dk_nrf52840.overlay` — `led4_pin_routing` off
- `firmware/nrf9160/prj.conf`, `CMakeLists.txt`
- `firmware/esp32-airpods-bridge/src/main.cpp` — UART2 parity + field order
- `firmware/CONTROLS_WIRING.md`, `hardware/BREADBOARD_WIRING.md`

Not flashed (orchestrator flashes), nothing committed.
