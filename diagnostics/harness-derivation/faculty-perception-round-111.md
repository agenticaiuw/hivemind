# Harness derivation — faculty-perception — round 111

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-input-reachability** — At 2026-08-07T17:30Z AI Pendant Agent is running but Accessibility=false, Screen Recording=false, input probe failed; ui_actions will report success while doing nothing. Automation grants are present and permissions.ready=false.
  - evidence: GET /observe and GET /ops/snapshot both report trusted:false, screenRecording:false, eventsPost:false, uiActionsWillReachTheScreen:false.
- **browser-session-provenance** — Safari bridge is online with 3 tabs and no pending commands, but its live device status identifies active tab 901786 as https://example.com with title 'Failed to open page', while durable default session maps tab 901786 to https://example.com/ yet title 'Inbox (14,987) - ... Gmail'. The active-tab identity/title is inconsistent and private Gmail state must not be inferred from the active status alone.
  - evidence: GET /browser/status and GET /observe at 2026-08-07T17:30Z.
- **machine-context-timezone** — Mac machine context reports timezone America/New_York; this is the currently observable timezone for scheduling interpretation.
  - evidence: GET /machine-context HTTP 200, machine.timezone=America/New_York.

## Capabilities it proposed

### ""Before you send, buy, delete, or change anything, tell me whether you can actually verify the target and what you will observe afterward; if the browser, Mac, or pendant reports conflicting state, stop and ask me.""
- **useful because:** Today the system can produce a successful-looking receipt even when Accessibility is false, and it can confuse a failed example.com tab with authenticated Gmail. A perception gate makes the assistant honest at the exact moment mistakes become costly. The pendant supplies the owner's confirmation channel, the browser supplies authenticated target/session provenance, the Mac agent supplies permission and postcondition observation, and the relay preserves the decision and evidence if one surface drops.
- **path:** pendant → browser-extension → mac-vision → mac-planner → relay-realtime → unified
- **model tier:** deterministic preflight and postflight checks; gpt-4.1-mini only to explain a mismatch; realtime model only for the owner's live clarification
- **latency:** 250 ms for local/relay evidence checks; up to 2 s for a concise mismatch explanation
- **cost:** Near-zero for typed status checks; roughly $0.001–$0.01 only when a model must summarize conflicting evidence. Browser screenshot upload dominates latency and privacy cost, so use it only on mismatch.
- **security:** Never expose page contents merely to prove identity; return origin, tab id, title hash, and session id by default. Require explicit confirmation for sends, purchases, deletes, and permission changes. Treat action receipts as claims until a postcondition observation verifies them.
- **missing:** A cross-surface preflight/postflight contract carrying target identity, expected postcondition, evidence timestamps, and confidence; Browser API that returns stable origin/session identity separate from mutable title and URL; A relay-held evidence record that the pendant can read back and acknowledge

### ""Is my pendant really connected and hearing you right now? Give me a proof, not just 'online'.""
- **useful because:** The relay currently reports a Mac bridge online while no pendant is registered; historical audio telemetry can be mistaken for live hardware. This capability would give the owner a single trustworthy answer: live device registration, recent bidirectional heartbeat, microphone/playback sequence acknowledgement, and which fallback surface is carrying the conversation. It is only possible by joining worn hardware, Mac USB bridge, relay registry, and the realtime voice session.
- **path:** pendant → relay-realtime → mac-planner → relay → unified
- **model tier:** Deterministic telemetry aggregation; no expensive model needed unless the owner asks a follow-up question
- **latency:** Under 1 s when registered; explicitly say 'not connected' rather than waiting for stale telemetry
- **cost:** Negligible API/storage cost; one small heartbeat and acknowledgement per check. Continuous telemetry should be sampled, not audio-streamed, to avoid bandwidth and battery cost.
- **security:** Do not include raw audio or device identifiers beyond a short stable label. A proof must include freshness windows and distinguish historical events from live acknowledgements; failed proof must not silently fall back to Mac microphone.
- **missing:** Authoritative relay device registry and delivery acknowledgements; A live USB serial bridge status reader for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A signed ping/echo packet covering microphone capture and speaker playback, not merely transport connectivity

### ""When you tell me something you saw, show me exactly where and when you saw it, and warn me if that source changed or became unreachable.""
- **useful because:** The system has a live browser bridge but its active-tab metadata conflicts with the durable session record. A provenance timeline would prevent stale Gmail, failed navigation, and historical pendant audio from being presented as current facts. The owner gets compact spoken citations and can ask to inspect the underlying page or event; the Mac and browser can observe, the relay can timestamp and retain continuity, and the pendant can announce freshness without exposing private content by default.
- **path:** pendant → browser-extension → mac-vision → mac-planner → relay-realtime → unified
- **model tier:** Deterministic provenance normalization and freshness checks; background gpt-4.1-mini for compressing multiple citations into speech
- **latency:** Immediate metadata citation under 300 ms; content synthesis under 2 s and only when requested
- **cost:** Low: metadata is tiny and deterministic. Background summarization costs about $0.001–$0.005 per brief; screenshots/page text are the dominant token and privacy cost.
- **security:** Use origin/session/tab IDs and cryptographic content hashes by default, not email/page contents. Redact secrets in relay retention. Mark every citation observed, inferred, or historical, and never upgrade inferred state to observed.
- **missing:** A shared observation schema with source, observedAt, validUntil, content hash, and historical/live classification; Browser heartbeat and inspection responses must carry monotonic observation sequence numbers; Relay retention and acknowledgement semantics for continuity evidence

### ""Before I submit this form or upload this file, show me the exact data and destination that will leave my devices, what the site can infer from it, and let me approve a redacted version from my pendant.""
- **useful because:** The owner cannot currently get a trustworthy, end-to-end view of what a browser form, Mac application, and relay-mediated action will transmit. This would make privacy visible at the moment of disclosure: the browser identifies the real destination and form fields, the Mac inspects the selected file and hidden metadata, the relay retains only a redacted decision record, and the pendant provides a physical approval channel.
- **path:** browser-extension → mac-vision → mac-terminal → mac-planner → relay-realtime → pendant → unified
- **model tier:** Deterministic field/file/metadata extraction first; background gpt-4.1-mini for plain-language risk explanation; realtime only for the live approval conversation
- **latency:** 2 seconds for a preview of a normal form or file; under 500 ms for approval once the preview is prepared
- **cost:** Usually near-zero with local parsers; $0.001–$0.02 when an LLM summarizes sensitive-field risks. Uploading screenshots or document text is the dominant cost and should be opt-in.
- **security:** The inspection itself must not transmit the sensitive payload to the relay or model by default. Redaction must happen locally, and approval must bind to a content hash, destination origin, and expiry. Never claim a site received only the redacted version without observing the resulting request.
- **missing:** Local browser network/form-payload inspection with origin binding; A Mac-side metadata scrubber and redaction preview for arbitrary files; Pendant confirmation bound cryptographically to the exact preview hash

### ""When a message, invite, payment request, or login prompt arrives, tell me whether it is genuinely meant for me, whether its sender and destination match, and what independent evidence supports that—without opening links automatically.""
- **useful because:** Today the owner must manually reconcile Gmail, Safari, Messages, and payment/login contexts. A cross-surface identity check could detect lookalike domains, mismatched account identities, reply-to manipulation, and context confusion before the owner clicks. The browser holds authenticated sessions, the Mac can inspect Mail/Messages/Calendar, the relay correlates evidence over time, and the pendant can deliver a concise warning while the owner is away from the screen.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → pendant → unified
- **model tier:** Deterministic URL/header/account checks first; background model for ambiguous language; realtime model only if the owner asks for an explanation
- **latency:** Under 1 second for structured checks; under 3 seconds for ambiguous content
- **cost:** Low for headers, origins, and account metadata; roughly $0.001–$0.01 for language-risk classification. No raw message content should leave the Mac unless explicitly requested.
- **security:** This is advisory, not an authenticity guarantee. Do not auto-open links or send verification requests. Keep message content local by default, redact tokens and addresses in relay records, and require confirmation before any response or payment.
- **missing:** A unified local identity/evidence graph across Mail, Messages, Calendar, browser sessions, and saved contacts; Safe link-resolution that never navigates the authenticated browser session; A calibrated uncertainty policy distinguishing verified identity from heuristic suspicion

### ""Give me a private end-of-day account of what the assistant changed, what it merely attempted, what failed silently, and what it exposed externally; let me dispute one item and permanently correct the record.""
- **useful because:** The owner currently has fragmented jobs, receipts, browser activity, pipeline events, and model-routing logs, but no human-readable accountability record that separates intention, execution, observation, and data disclosure. A daily audit would make the system governable: Mac and browser provide action logs, relay contributes remote delivery, the pendant provides spoken review and dispute, and the unified mind updates its durable memory only after the owner accepts corrections.
- **path:** relay-realtime → mac-planner → browser-extension → mac-terminal → pendant → unified
- **model tier:** Deterministic event join and status classification; background gpt-4.1-mini to compose the digest; realtime only for interactive dispute and correction
- **latency:** Digest generated asynchronously in under 30 seconds; individual dispute lookup under 2 seconds
- **cost:** Low storage and deterministic processing; approximately $0.002–$0.02 per daily digest depending on event volume. Never resend full page contents or audio merely to compose the report.
- **security:** Audit records contain sensitive behavior and destinations. Encrypt locally, minimize retention, redact secrets, and make deletion/dispute auditable. A correction must not rewrite the immutable original event; it should append a signed owner correction.
- **missing:** A cross-surface event identity and causal-link format joining Mac jobs, browser commands, relay deliveries, model calls, and device events; Immutable-but-correctable audit storage with owner-visible retention controls; A data-disclosure classifier that records what crossed the device boundary


## Changes it proposed to its own stack

### `firmware` — Add a USB-serial reality beacon spanning the nRF9160 and ESP32 bridge: every 5 seconds emit a signed monotonic device epoch, firmware build, capture-path loopback result, playback-path loopback result, and relay-delivery acknowledgement; the Mac bridge forwards only the compact status frame and records attach/detach transitions. The relay exposes the last acknowledged epoch and freshness, explicitly separate from historical pipeline audio.
- **owner gets:** When the owner asks whether the pendant is actually hearing them, the system can prove live capture, playback, and end-to-end delivery—or plainly say which link is broken—instead of relying on stale audio history or a Mac bridge 'online' flag.
- effort: Medium-high: firmware framing and watchdog-safe loopback on both chips, serial parser/forwarder, relay schema and tests for unplug/reconnect and clock rollback.  ·  risk: A noisy serial link could create false offline states; use sequence monotonicity, debounce, and a 30-second stale threshold. Loopback must never play audible test tones without an explicit diagnostic mode. Recover by falling back to transport-only status marked unverified.
- cost: No model API cost; small flash/RAM footprint and negligible serial bandwidth. Firmware development/testing cost only; battery impact is a few periodic packets and ADC/audio checks.  ·  latency: Adds at most one heartbeat interval (5 s) to freshness; on-demand proof can force an immediate frame and return in under 1 s over USB.
- security: Sign frames with a device key and rotate pairing credentials; do not send raw audio. The relay must reject frames with reused epochs or unknown device IDs.
- depends on: Authoritative relay device registry and delivery acknowledgements; A defined signed status-frame format shared by nRF9160, ESP32, Mac bridge, and relay


## What it asked for

_Nothing._
