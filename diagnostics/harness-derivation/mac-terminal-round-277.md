# Harness derivation — mac-terminal — round 277

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live USB bench reachability** — The newly granted mac_usb_serial_diagnostics schema is still unresolved in the live inventory; no serial/USB capability is published. Both expected device path families therefore remain unverified through a tool, despite the physical connection being present.
  - evidence: mac_usb_serial_diagnostics call returned unresolved; best match action:get_mac_status score 0.225, and resolver reported no inventory match.

## Capabilities it proposed

### "When I say “finish this and tell me when it is truly done,” carry the request from the pendant through the relay to the Mac/browser, survive a disconnect, and come back with one spoken proof of what changed—or an exact failure and the recovery choice."
- **useful because:** Today a request can execute on the Mac yet leave the wearer unsure whether the browser action, local mutation, or relay acknowledgement actually completed. This gives the owner one dependable answer, including after walking away from the Mac or losing the pendant link.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Use the realtime model only to interpret the short spoken request and report the result; use the relay's background worker for supervision, receipts, and retry decisions.
- **latency:** Acknowledge dispatch locally in under 500 ms; normal completion under 10 s; after link loss, resume/poll in the background and speak the proof on reconnection rather than burning realtime turns.
- **cost:** One short realtime turn plus cheap background polling; roughly $0.01–$0.05 per invocation, dominated by the initial voice turn, not polling.
- **security:** The relay must never claim success from a missing heartbeat. Browser claims need URL/title provenance, and destructive actions retain the existing owner confirmation policy. Send only action metadata and bounded result excerpts to the relay; do not export page contents or shell environment.
- **missing:** A durable transaction record joining pendant turn ID, relay job, Mac job, action ledger, and browser provenance; A supervisor that closes/reconciles ledgers, distinguishes an interrupted step from a completed step, and resumes only replay-safe actions; A compact completion-proof event that the pendant can cache and read aloud offline

### "I have both boards plugged into my Mac. Let me say “test the pendant” and get a spoken pass/fail: enumerate both USB devices, run a bounded dual-UART capture, exercise an audio loopback, and tell me which chip, clock, frame counter, or cable failed."
- **useful because:** The hardware is live but the granted serial diagnostic schema still cannot resolve, so the owner currently has to know scripts and inspect logs. This turns today's bench setup into a one-sentence truth test and catches the failure before blaming LTE, the relay, or the model.
- **path:** pendant → mac-planner → relay → dashboard
- **model tier:** Use a deterministic local diagnostic runner for enumeration, UART framing, and loopback math; use the cheap background tier to summarize logs. Reserve realtime only for the final spoken sentence if the pendant is connected.
- **latency:** Return a local pass/fail in 5 s, with a 30 s ceiling for a full capture. Never leave a serial reader running after the test or open the microphone.
- **cost:** Near-zero model cost when the deterministic report is used; under $0.01 for an optional spoken summary. Mac CPU and a few MB of rotating logs dominate.
- **security:** Read-only device probes and synthetic loopback samples only. Do not upload raw UART logs or PCM by default; redact tokens and offer a local path plus hashes. The runner must use the two known device-path families and fail closed if a path changes rather than opening an arbitrary serial device.
- **missing:** A real resolved bounded USB-serial diagnostic capability (the granted schema remains unresolved); A host-side framing/parser for nRF9160 and ESP32 health counters; A synthetic 24 kHz loopback command and a report route consumable by the pendant; A cleanup watchdog for capture processes and rotation of bench logs

### "When I put the pendant back on after being away, tell me only what changed because of me or needs my decision: which browser pages changed, which Mac jobs finished or failed, and which queued requests became stale. Let me ask “why?” and hear the causal timeline, not a generic morning brief."
- **useful because:** Today the owner can inspect jobs, browser sessions, and scheduled briefs separately, but cannot recover the meaning of an absence. This gives them a trustworthy re-entry point after a commute, sleep, or link outage without replaying every notification or pretending stale work succeeded.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Use deterministic event correlation and timestamp/state comparison first; use a cheap background model to compress the resulting causal chains. Use realtime only for the owner's short spoken follow-up questions.
- **latency:** Prepare the absence delta in the background as soon as a link returns; first spoken answer within 2 seconds, with deeper “why?” explanations under 5 seconds.
- **cost:** Low: event indexing and state hashes dominate; roughly $0.005–$0.02 for an optional summary, with no model call when there are no meaningful changes.
- **security:** Store hashes, timestamps, action outcomes, and provenance pointers rather than page contents or microphone audio. Browser page text remains behind the existing session boundary. Clearly label inferred causality versus directly observed events, and never turn an expired authorization into a new action.
- **missing:** A durable cross-surface event timeline keyed by owner absence intervals and link epochs; Mac snapshots for foreground app, active browser tab, job state, and completion/failure transitions; Browser change cursors or page-watch diffs that expose meaningful changes without exporting whole pages; A relay-side causal correlator that marks stale, superseded, and externally changed work; A pendant query/result protocol for concise delta playback and follow-up why-chain retrieval

### "If a logged-in browser task reaches a choice I need to make, read me a short decision packet on the pendant—what the page says, the safe options, and what each changes. Let me answer “option two,” then apply exactly that choice and read back the resulting page state."
- **useful because:** Today browser automation can read and click, but an owner away from the screen cannot participate in a consequential multi-option decision without asking for a vague click. This preserves the owner's judgment while making the browser, pendant, relay, and Mac act as one conversational workflow.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Use the browser harness for structured extraction and page-state verification; use a cheap reasoning model to produce the bounded option packet. Realtime is reserved for the spoken choice and acknowledgement.
- **latency:** Extract and speak a packet in 3 seconds; apply the selected option within 5 seconds; if the page changed, invalidate the packet instead of acting on stale refs.
- **cost:** About $0.01–$0.04 per decision, dominated by one short reasoning turn; browser inspection and state checks are local/relay work.
- **security:** Send only the minimum fields needed to explain the choice. Bind the spoken answer to a page URL, session, snapshot hash, and short-lived nonce; reject it after navigation or content change. Preserve existing confirmation requirements for sending, purchasing, deleting, or other high-impact actions.
- **missing:** A structured browser decision extractor that returns labeled options, consequences, and required fields rather than only refs; A pendant-sized decision-packet and answer protocol with nonce and snapshot binding; Browser result verification that proves the selected state changed as described; A relay correlation record joining spoken answer, browser command, and resulting provenance

### "When I say “read the chart” on my pendant, inspect the chart or dashboard that is open in my logged-in browser, explain the important trend and any anomaly in plain speech, and let me ask for the exact values or a comparison without sending the page away from my Mac."
- **useful because:** Structured page reading is not enough for canvas charts, visual dashboards, and dense authenticated views. This lets the owner use information trapped behind the browser while preserving the browser session and keeping page contents local to the Mac.
- **path:** pendant → browser → mac-planner → relay
- **model tier:** Use a local Mac/browser capture and vision model for the chart; use a cheap summarizer for the spoken explanation. Realtime handles only the owner's follow-up question when low latency matters.
- **latency:** First spoken trend within 4 seconds; exact-value follow-up within 3 seconds; do not capture continuously—only on an explicit request.
- **cost:** Roughly $0.02–$0.08 per chart request depending on image resolution and vision inference; no cost when the page has an accessible structured table.
- **security:** The screenshot and extracted values stay on the Mac unless the owner explicitly asks for relay delivery. Redact unrelated browser regions, account identifiers, and neighboring tabs. Keep a provenance pointer to the URL and capture timestamp, not a permanent screenshot by default.
- **missing:** A browser chart-understanding action that crops the relevant canvas or chart region and returns values/trends with confidence; Mac-local vision access to the authenticated browser surface without exposing unrelated tabs; A spoken follow-up protocol for exact values and comparisons tied to the same capture hash; A retention policy that deletes chart pixels after the answer while retaining optional derived claims


## Changes it proposed to its own stack

### `firmware` — Ship a bench-first 24 kHz superwideband audio contract end to end: nRF9160 captures/frames at 24 kHz, the Mac bridge negotiates the codec and clock, ESP32 emits/receives the same format, and the relay records negotiated rate, frame loss, jitter, and a short deterministic loopback checksum. Keep a compatibility fallback to the current rate, but refuse to label a turn “superwideband” unless both chips and the relay agree.
- **owner gets:** The owner explicitly wants a 24 kHz path, and today a turn can sound merely “connected” while silently falling back or dropping frames. This makes the promised audio quality measurable on the physically connected bench before LTE is involved, then preserves the same truth when worn remotely.
- effort: Medium-high: codec/clock plumbing on both firmware images, a versioned negotiation frame, Mac bridge adapter, and a relay metric/event mapper. Start with the current USB bench scripts and golden PCM fixtures.  ·  risk: A clock mismatch can produce drift, buffer growth, or audible artifacts; old firmware may not understand negotiation. Gate activation on an explicit capability exchange and retain the old codec path. On failure, report the measured rate and fallback rather than guessing.
- cost: No per-turn model cost; modest relay storage for counters and a tiny checksum event. Hardware cost $0 for the current bench; a future production codec/clock change may be required if the present audio peripherals cannot sustain 24 kHz.  ·  latency: Adds one negotiation round at session start (target <150 ms); steady-state latency should remain within the existing frame budget, with bounded jitter telemetry.
- security: PCM stays on the existing audio path; emit only codec/rate/counter metadata by default. Loopback fixtures must be synthetic and must never upload microphone content.
- depends on: audio_link_truth_and_recovery; the existing dual-chip USB capture scripts; a versioned audio capability/negotiation message; a relay audio event schema for rate, loss, and jitter


## What it asked for

_Nothing._
