# Harness derivation — mac-terminal — round 127

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac and device status** — The Mac bridge and Safari extension are online, but the local agent reports ready=false because Accessibility and Screen Recording are not granted; the browser's active tab is currently a failed example.com page. The physical pendant and ESP32 are USB-attached but no serial health endpoint exists yet.
  - evidence: GET /ops/status returned fullControlMode=true, browserExtension.online=true, accessibility.trusted=false, screenRecording.granted=false, ready=false; GET /browser/status returned online=true and tabTitle='Failed to open page'; get_hardware_spec(all) identifies the two live USB serial devices.

## Capabilities it proposed

### "When I say “save this page” through the pendant, remember the exact Safari page and the part I’m looking at, then let me ask for it back later."
- **useful because:** It turns fleeting browsing into searchable memory without copy/paste: the pendant supplies intent, Safari supplies authenticated title/URL/selection, the Mac persists a compact citation, and the relay makes it retrievable from any surface. Unlike a generic voice note, the saved item is anchored to what was actually on screen.
- **path:** pendant → browser-extension → mac-planner → relay-realtime → dashboard
- **model tier:** Use realtime only to detect the short save command; use a cheaper background model to normalize page text and generate a one-line label; use the relay's normal text retrieval for later questions.
- **latency:** Acknowledge in under 500 ms; capture the page in 2 s; later retrieval under 3 s.
- **cost:** About $0.005–$0.03 per save depending on extracted text length; most cost is one background summarization, not realtime audio.
- **security:** Authenticated page content and any selection leave Safari only to the local Mac and the owner's relay account. Default to storing URL, title, selection, and a short hash/snippet rather than the whole page; require an explicit “save the whole page” phrase for more data.
- **missing:** A browser command that atomically returns active tab URL/title/selection plus a stable content fingerprint; A capture record type linking a saved item to browser tab provenance and searchable embeddings; A retrieval intent that searches these page captures and returns citations

### "During a meeting, let me tap the pendant once to bookmark what is happening; afterward give me a timeline of my bookmarks with the active meeting, the Safari page on screen, and a short note for each."
- **useful because:** The owner can mark decisions or follow-ups without interrupting the conversation. The pendant provides a physical, low-friction timestamp; the Mac adds the foreground app and browser evidence; the relay turns sparse bookmarks into a useful post-meeting timeline instead of requiring continuous recording.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Do not run a large realtime model for each tap. Store an event locally, use a cheap batch model after the meeting to label nearby transcript/page snippets, and reserve realtime for the spoken follow-up request.
- **latency:** LED/haptic acknowledgement within 150 ms; event persisted within 1 s; post-meeting timeline within 60 s of the meeting ending.
- **cost:** $0.01–$0.10 per meeting, dominated by optional transcript summarization; bookmark-only mode is nearly free.
- **security:** Default mode stores timestamps, foreground app, URL/title, and short local excerpts—not continuous audio. Authenticated page text stays scoped to the owner's Mac/relay and is deleted with the meeting record. Make recording mode visibly distinct via the pendant LED.
- **missing:** A firmware tap event distinct from start/end conversation; A local event journal that snapshots foreground app and active Safari tab at tap time; A meeting-session correlator using Calendar/meeting window identity; A post-meeting endpoint returning cited bookmark evidence

### "If the pendant stops responding, let me ask “what’s wrong?” and have the Mac inspect both USB devices, the relay pipeline, and the last audio/job receipts, then tell me the cause and recover what can be recovered."
- **useful because:** Today a dropped call, dead bridge, stale browser, and failed relay job look identical to the wearer. This gives one truthful diagnosis spanning the physically attached nRF9160 and ESP32, the Mac agent, and cloud state, with concrete recovery instead of a vague error LED.
- **path:** pendant → mac-terminal → relay-realtime → dashboard
- **model tier:** Use deterministic health probes and receipt correlation first; call a cheap text model only to explain the evidence. Use realtime only if the owner asks while a live call is active.
- **latency:** Initial diagnosis in 3 s; safe recovery attempts (reconnect serial, restart bridge process, replay unsent SD chunks) within 15 s; never claim recovery until a new heartbeat/audio packet is observed.
- **cost:** Negligible API cost for probes; under $0.01 for an optional explanation. Engineering cost is serial protocol and relay correlation, not model inference.
- **security:** USB logs can contain speech metadata and tokens; redact payload bytes and secrets before cloud upload. Recovery must be limited to the known pendant/bridge processes and produce an immutable local receipt. Never replay audio without telling the owner what interval is being replayed.
- **missing:** A Mac serial health probe for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A relay endpoint that correlates pipeline audio/events with Mac and device heartbeats; Typed recovery operations for reconnect, bridge restart, and SD failure-buffer replay; A truthful diagnosis contract with observed-at timestamps and a final verification probe

### "When I walk away from my Mac, quietly checkpoint whatever I was doing, and when I return with the pendant, restore the right Safari tabs, window layout, and unfinished draft without sending or submitting anything."
- **useful because:** The owner can move between rooms or lose connection without reconstructing their working state. The pendant supplies physical presence, the Mac captures the real UI state, and the browser preserves authenticated tabs and drafts; no single surface can provide that continuity alone.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Use deterministic presence and state capture; use a cheap background model only to name the checkpoint and identify the active task. No realtime reasoning is needed unless the owner asks for restoration by voice.
- **latency:** Checkpoint within 5 seconds of departure; restore within 10 seconds of return; never restore by submitting, sending, or navigating past an approval boundary.
- **cost:** Near-zero for state capture; under $0.02 for optional task labeling. Main cost is implementation of presence and browser/window snapshots.
- **security:** Authenticated tabs and drafts remain encrypted/local where possible. A checkpoint must expire, be bound to the owner's pendant identity, and never expose page contents in notifications. Restoration must preserve tab/session affinity and avoid replaying destructive actions.
- **missing:** A presence signal between pendant and Mac that survives relay loss; A versioned Mac window/layout checkpoint format; Browser APIs to save and restore tab groups plus draft-safe DOM state; A conflict resolver when the owner changes the same tab while away

### "Let the pendant act as my interruption filter: during a focus block, collect notifications from my Mac and authenticated browser, interrupt me only for things that meet my urgency rule, and give me a one-button way to defer the rest until I am free."
- **useful because:** The owner gets fewer context switches without losing genuinely urgent work. The relay can remain awake, the Mac and browser can see events, and the pendant provides the only interruption channel that follows the owner away from the screen.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use deterministic rules and a small classifier for urgency; reserve realtime for a concise spoken alert. Batch deferred items with a cheaper model into a digest.
- **latency:** Urgent alerts within 10 seconds; defer/dismiss acknowledgement under 1 second; digest generation under 30 seconds.
- **cost:** Typically below $0.01 per event; background summarization dominates, while rule matches are free.
- **security:** Notification text can contain sensitive work or personal data. Keep full content on the Mac/relay account, send only a redacted title and urgency rationale to the pendant, and expose a visible focus-state indicator in the dashboard. Never auto-reply or change notification settings without an explicit request.
- **missing:** A unified event intake for Mac notifications, calendar changes, and authenticated browser alerts; A durable per-owner urgency policy with quiet hours and focus sessions; Pendant alert/defer acknowledgements that work while the Mac is disconnected; A deduplicating event ledger so the same alert is not spoken twice

### "When I say “hand this off,” package the exact current browser or Mac state into a private, expiring handoff that another device or a later session can reopen at the same point, with my unsent draft and source citations intact."
- **useful because:** The owner can start research on the Mac, continue from the pendant or phone, and return later without losing the exact context. This is a stateful handoff of work—not a generic briefing or a browser watch—and it preserves what was drafted without accidentally sending it.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard → iOS
- **model tier:** Use deterministic state serialization and citation collection; a cheap model can produce a short handoff label. Realtime is only needed to interpret the short voice command.
- **latency:** Create a handoff in under 5 seconds; reopen in under 8 seconds; expired handoffs disappear immediately from all surfaces.
- **cost:** A few cents at most for optional labeling and citation compression; storage is small JSON plus selected snippets.
- **security:** Handoffs may contain authenticated URLs, drafts, and private text. Encrypt at rest, bind access to the owner's paired clients, expire by default, and redact secrets such as passwords or tokens. Reopening must never execute a draft or submit a form.
- **missing:** A cross-client handoff object with encrypted payload, expiry, and capability-scoped access; Browser serialization of tab/session/selection/form-draft state with provenance; Mac restoration of app/window/document context; A pendant and iOS command to enumerate, resume, or discard handoffs


## Changes it proposed to its own stack

### `firmware` — Add a duplex-aware audio scheduler for the nRF9160/relay pair: reserve a minimum uplink slice for mic packets whenever downlink TTS is active, adapt Opus uplink from 16 kbps toward 8 kbps under contention, and mark every dropped packet with a sequence gap. The relay should shorten or pause TTS on detected barge-in rather than allowing both streams to saturate LTE-M.
- **owner gets:** The owner can interrupt the agent and be heard instead of losing roughly eight seconds of speech during simultaneous talk. Conversations feel responsive on the real pendant, not merely healthy in telemetry.
- effort: Medium-high: firmware packet scheduler and bitrate control, relay congestion feedback, and an integration test over the USB-connected modem/bridge with induced contention.  ·  risk: Poor bitrate transitions could create artifacts or starve playback; recover by falling back to the current fixed 16/24 kbps mode when feedback is absent. Sequence numbers make loss visible rather than silently corrupting turns.
- cost: No API cost and no new hardware; slightly higher CPU during bitrate changes, within the existing ~87% single-core audio load only if transitions avoid extra transcoding.  ·  latency: Barge-in acknowledgement improves from multi-second loss to one or two packet intervals; TTS may sound briefly clipped when preempted.
- security: No new data leaves the device; congestion metadata is non-content telemetry.
- depends on: A framed packet sequence/priority field shared by pendant and relay; Relay-side barge-in detection that can stop queued TTS packets; An integration test harness for the live /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA pair

### `hardware` — Replace the prototype's single-button/LED interaction with a production pendant interaction module: add BLE presence beacons (or UWB if reliable room-level presence is required), a low-power vibration motor, and a capacitive double-tap surface while retaining the existing physical button for conversation. Expose signed presence epochs and alert acknowledgements to the nRF9160 firmware and Mac over USB/LTE.
- **owner gets:** The pendant can know when the owner has left or returned, deliver a private interruption without opening a speaker, and distinguish a context bookmark or defer gesture from starting/ending a call. That enables seamless work handoffs and attention protection rather than making the owner repeat commands.
- effort: High: enclosure and power redesign, BLE/UWB coexistence testing with LTE-M, firmware input state machine, and Mac pairing/reconnection UX.  ·  risk: False presence near the Mac or accidental taps could checkpoint or defer the wrong thing. Recover with explicit state LEDs/vibration patterns, debounce and a dashboard history; keep the existing button path as a fallback. UWB increases BOM and power, so BLE can ship first if room-level precision is unnecessary.
- cost: Roughly $8–$25 BOM increase depending on UWB versus BLE and a $1–$3 haptic motor; intermittent beaconing should add modest battery draw, while UWB ranging can materially increase it.  ·  latency: Presence changes in roughly 1–3 seconds with BLE, sub-second with UWB; local vibration acknowledgement is under 100 ms.
- security: Pairing keys and signed presence epochs must be device-bound; do not broadcast an owner-identifying static address. Presence data should remain local unless needed for a queued handoff.
- depends on: A new firmware event protocol for presence, haptic acknowledgement, and capacitive gestures; Mac and relay support for paired-device identity and presence epochs; A durable handoff/interruption state machine


## What it asked for

### `s16-hqnm` (skill) — context_bookmark_button
- does: A short double-tap while idle emits a compact context-bookmark event; the Mac immediately snapshots foreground app, active Safari tab metadata, current project/session, and timestamp. A long press still starts conversation, and a tap during a call remains end-call, preserving existing behavior.
- must be on-device because: The value is a reliable physical moment marker even when speech recognition, LTE, or the relay is unavailable. Only firmware can capture the button edge with sub-100-ms timing and queue it through a dropped-link interval.
- trigger: Button double-tap while idle; firmware event queue retries over the existing USB/LTE transport and flashes a distinct two-blink acknowledgement.
- storage: A 32-byte binary event record (sequence, timestamp, event type, CRC) in RAM ring buffer; spill only to the existing SD failure buffer if transport is unavailable. At 64 records this is ~2 kB.
- RAM budget: ~3 kB including ring metadata and retry state, well below 211,608 B application RAM; no audio buffers or Opus changes required.

