# Harness derivation — browser-extension — round 24

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser availability** — Safari extension is currently offline (status reports only offline home-chrome, no tab) with 2 pending browser commands; authenticated page work cannot be verified until the real Safari device heartbeats again.
  - evidence: GET /browser/status live response at 2026-08-07T09:32Z: online=false; devices=[home-chrome offline, tabCount null]; pendingCommands=2.

## Capabilities it proposed

### "“If something genuinely urgent changes on one of my logged-in web pages, tell me through the pendant when I’m not already talking; otherwise leave a sourced card on my Mac.”"
- **useful because:** This combines the browser's private authenticated reach with the always-available relay and worn audio surface. It avoids noisy polling alerts and does not force the owner to keep Safari visible; the Mac card preserves the exact evidence and lets the owner review before any action.
- **path:** browser → mac-bridge → relay → pendant → dashboard
- **model tier:** Use a cheap background extraction/fingerprint model for scheduled page checks, deterministic semantic-diff and urgency rules for most events, and realtime only to turn a confirmed urgent diff into a brief spoken interruption. No model is needed for delivery or quiet-state arbitration.
- **latency:** Page checks can run on the configured cadence (typically minutes to hourly). After a meaningful urgent diff, deliver the pendant summary within 10 seconds when the voice channel is idle; if busy, queue it and show the Mac card immediately.
- **cost:** About $0.01–$0.05 per watched page-check depending on extraction complexity; realtime audio generation is pennies or less per alert. Dominant costs are authenticated browser execution and repeated page context, so cache session/tab metadata and send only changed regions.
- **security:** Private page text leaves Safari for extraction and the relay only when the owner created the watch; minimize to selected DOM regions, redact secrets, retain diff evidence briefly, and never auto-submit. Urgency is advisory: the spoken alert can say what changed and where, while all follow-up mutations remain owner-directed. A busy-call interruption policy must be explicit and locally overrideable.
- **missing:** Durable authenticated page-watch definitions with semantic baselines and volatile-field suppression; A relay event bus plus pendant delivery/queue protocol that understands voice-idle versus active state; A compact Mac evidence card linking the alert to URL, timestamp, changed snippet, and baseline; Per-watch urgency rules, quiet hours, and a one-button 'mute this watch' action

### "“Save this private webpage for me so I can ask about it later, even after Safari is closed, but don’t upload the page’s contents to the relay.”"
- **useful because:** Today the browser is the only node that can see the owner’s logged-in page, but that knowledge disappears with the tab and cannot be safely carried into a later pendant conversation. This would create private, durable continuity without turning the relay into a repository of authenticated page data: the owner could say “what was that insurance deadline?” hours later and get an answer grounded in the saved page.
- **path:** browser → mac-bridge → dashboard → relay → pendant
- **model tier:** Use a background/cheap model on the Mac to extract a concise structured record and citations from the page; use realtime only when the owner later asks through the pendant. Deterministic local encryption, indexing, and retrieval should not consume a model.
- **latency:** Capture should complete in under 5 seconds after the owner asks. A later pendant lookup should return a short answer in under 2 seconds when the Mac is online; if it is offline, the pendant should honestly say the private archive is unavailable rather than sending page contents elsewhere.
- **cost:** A few cents or less per capture, dominated by local extraction if a model is needed; later lookups are negligible. Storage is local workspace metadata plus an encrypted page artifact, with no additional relay audio or inference requirement.
- **security:** The page snapshot and extracted text must be encrypted with a device-held key, stored under ~/AI-Pendant-Workspace, and excluded from relay logs, D1, R2, and generic context projections. The dashboard should show source URL, capture time, sensitivity, and expiry, with explicit delete/export controls. Never save passwords, tokens, payment fields, or hidden form values; redact them before persistence. The relay may carry only an opaque archive ID and query result if the Mac elects to answer.
- **missing:** A browser capture command that returns a sanitized DOM/text bundle with field-level sensitivity labels and stable citations; A Mac-local encrypted private archive with semantic indexing, TTLs, and delete receipts; A relay protocol for opaque archive-query requests and an online/offline response state; A context-projection rule that keeps private archive contents out of ordinary prompts unless the owner explicitly asks about the saved item; Pendant phrasing and dashboard UX for naming, reviewing, and deleting saved private pages


## Changes it proposed to its own stack

### `hardware` — Ship a real 24-kHz superwideband audio path as one negotiated end-to-end mode rather than only changing the relay sample-rate label: replace the fixed-15,625-Hz I2S microphone with a clockable 24/48-kHz digital mic and move to a higher-memory/DSP wearable SoC (nRF5340-class or equivalent). Firmware advertises audio capabilities at session start, captures 24-kHz mono, encodes Opus 24 kHz in 20-ms packets, and reports sequence/timing metadata; the relay preserves 24 kHz through its transcode and the ESP32 bridge requests 24-kHz decode before its unavoidable 44.1-kHz SBC output resample. Keep 16-kHz mode as a negotiated fallback for the current DK and poor radio conditions, with a single end-to-end quality indicator in the completion receipt.
- **owner gets:** The owner's voice would sound materially clearer and less telephone-like, while calls remain usable on today's prototype. Capability negotiation prevents a half-upgraded path where one node silently resamples or lies about quality, and fallback means a weak LTE-M link does not break conversations.
- effort: High: prototype a 24-kHz mic/clock on a product board, port fixed-point Opus and measure simultaneous encode/decode plus modem headroom, add relay capability negotiation and packet timing, update ESP32 buffering/resampler, and test loss/jitter over LTE-M. The current DK cannot honestly be the production endpoint because its mic is fixed at 15,625 Hz and its 211,608-B app RAM is already constrained.  ·  risk: Higher codec bitrate and CPU can increase LTE-M airtime, heat, and battery drain; packet loss may be more audible. Roll back by capability negotiation to the existing 16-kHz/16-kbps profile. Validate with A/B recordings and watchdogs before enabling it by default.
- cost: No per-call model/API cost change. Prototype hardware roughly $30–$80 for a mic and capable SoC/board, plus enclosure and battery iteration; 24-kHz Opus at roughly 24–32 kbps increases radio airtime and energy versus 16 kbps.  ·  latency: 20-ms packets can reduce algorithmic latency versus the current 60-ms playback packets, but LTE-M jitter buffering may add 20–60 ms. Target <250 ms mouth-to-ear and expose measured mode/RTT in receipts.
- security: Raw audio still traverses the existing relay and R2 retention path; do not add recordings merely for quality testing. Encrypt capability/session metadata, tag test captures with explicit short retention, and keep the existing deletion sweeper requirement.
- depends on: A product audio SoC/microphone that can sustain 24-kHz capture and Opus alongside LTE-M; Relay capability negotiation and packet-timing schema; ESP32 bridge buffer/resampler changes and end-to-end A/B test harness; Audio retention sweeper and per-job deletion controls


## What it asked for

_Nothing._
## Its own summary

I discovered the owner's active priority is the 24-kHz superwideband path. Current hardware cannot honestly deliver 24-kHz capture: the mic is fixed at 15,625 Hz, the nRF9160 has only 211,608 B app RAM, and simultaneous Opus encode/decode already consumes about 87% of a core. I proposed a negotiated end-to-end 24-kHz product mode with a clockable mic, stronger SoC, 20-ms Opus packets, relay/bridge capability negotiation, and safe 16-kHz fallback. I also proposed a new cross-node capability: urgent authenticated browser changes spoken through the pendant only when voice-idle, otherwise left as sourced Mac evidence. Live browser status is currently offline with two pending commands and no Safari tab.

**Biggest unknown:** The concrete relay codec/transcode contract and whether a product audio board capable of 24-kHz capture has been selected. For browser work, I still need the real Safari extension to heartbeat again; the enqueue path remains unusable while it is offline.

