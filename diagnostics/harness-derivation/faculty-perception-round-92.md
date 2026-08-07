# Harness derivation — faculty-perception — round 92

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac agent observability** — At 2026-08-07T13:55Z, Mac agent is reachable and relay/mac bridge are configured and reachable, but permissions.ready=false: Accessibility and Screen Recording are not granted to com.aipendant.agent; /observe explicitly says UI actions do not reach the screen and receipts for ui_click/ui_menu/type_text/press_keys cannot be trusted. Browser extension home-chrome reports online but has null tab/window metadata and 9 pending commands.
  - evidence: GET /ops/snapshot HTTP 200 and GET /observe HTTP 200
- **pipeline state consistency** — The local pipeline contains historical/stale entries whose semantics conflict with current device reality: a 2026-08-07 07:22 nrf9160 run is still status=processing with an alert_delivered event, and a 12:00 run says response waiting for the nRF9160, while live device discovery reports no registered pendant and only the Mac bridge online. These must be treated as historical records, not evidence of current delivery.
  - evidence: GET /pipeline HTTP 200 alongside discover(devices): cloudflare-contract-test mobile offline; home-macbook-bridge online; no pendant
- **browser evidence availability** — The browser extension reports 9 pending commands, yet GET /browser/inspections returns an empty inspection list. There is therefore no stored inspection evidence currently available to validate those queued commands.
  - evidence: GET /browser/status HTTP 200 and GET /browser/inspections HTTP 200 at 2026-08-07T13:55Z

## Capabilities it proposed

### "“What do you actually know about this right now—and what might be wrong?” Give me a spoken, source-linked answer that separates live observations from stale history, shows conflicts between my Mac, browser, relay, and pendant, and tells me exactly what evidence would resolve each uncertainty."
- **useful because:** Today the system can expose individual statuses and historical events, but the owner cannot ask for an honest cross-device truth assessment. This would prevent confident claims based on stale pipeline records, missing browser provenance, or untrusted GUI receipts, and would make uncertainty actionable rather than invisible.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheap background/text model to assemble and classify evidence; reserve realtime only for the short spoken rendering and follow-up conversation.
- **latency:** Under 3 seconds for cached evidence; up to 10 seconds when a fresh Mac/browser/relay observation is required.
- **cost:** Low: mostly local/relay joins and a small text-model call; realtime cost only for the final spoken response.
- **security:** Private browser URLs, account state, and Mac activity must remain local or encrypted through the relay; display redacted source labels by default and require confirmation before requesting fresh authenticated page reads. Never present an inferred fact as observed.
- **missing:** A typed cross-surface evidence record with source, observedAt, freshness TTL, confidence, and contradiction links; Authoritative relay device and delivery acknowledgements; Browser command/read provenance bound to tab, URL, and timestamp; Pendant registration and a durable spoken-response receipt path


## Changes it proposed to its own stack

### `context` — Add a perception consistency and freshness gate before any judgement/action input: join /v1 device registry, /ops snapshot, /observe, browser heartbeat metadata, and pipeline event timestamps by correlation ID; label each fact current, stale, unreachable, or contradictory. A pipeline event claiming pendant delivery must not become 'delivered' unless a currently registered pendant supplies a receipt/ack within a bounded TTL. Browser commands must be marked indeterminate when extension heartbeat lacks tab/window identity or the queue is nonzero beyond a timeout. Expose a compact evidence bundle with source, observedAt, TTL, and contradiction reasons rather than silently merging histories.
- **owner gets:** The owner will stop hearing confident claims that a pendant received audio or that a browser action succeeded when no pendant is connected, the browser has no identifiable tab, or macOS input permissions make UI receipts meaningless. It turns today's misleading status into an honest 'not verified' answer and points to the exact recovery needed.
- effort: Moderate: shared typed evidence schema, correlator, TTL worker, and changes to judgement context plus dashboard status; no hardware change.  ·  risk: Existing historical jobs may be relabeled stale and appear less successful; recover by retaining raw immutable events and making the classifier reversible. A too-short TTL could create false uncertainty, so use source-specific windows and explicit clock timestamps.
- cost: Negligible API cost; small D1/JSON storage for evidence labels and correlation metadata.  ·  latency: Adds tens of milliseconds for local joins; avoids expensive model calls on contradictory/obviously stale state.
- security: Improves safety by preventing unverified action claims; evidence bundles must redact page contents and preserve only identifiers/snippet hashes.
- depends on: authoritative relay device registry and delivery acknowledgments; relay browser-read provenance; continuity-event retention and acknowledgement semantics

### `hardware` — Add a hardware-backed identity and connection-attestation path to the pendant: each pendant ships with a per-device key in a secure element, signs boot/version/audio-receipt heartbeats with a monotonic counter, and the relay records registration, last-seen, and receipt counters separately from historical pipeline jobs. Firmware should expose a local LED/button enrollment flow and refuse to claim response playback completed until the signed audio receipt is persisted.
- **owner gets:** The owner would know whether a response truly reached their worn device, rather than seeing simulator or stale nRF9160 records described as current. Replacing or reconnecting a pendant would be explicit, and a lost or cloned device could not silently impersonate it.
- effort: High: secure-element selection and provisioning, firmware transport/protocol work, relay registry and receipt schema, manufacturing/enrollment UX, and migration for development devices.  ·  risk: Lost-device recovery and factory resets could strand an identity; provide a signed re-enrollment ceremony with a one-time recovery code and retain raw telemetry for diagnosis. Added attestation failures could temporarily suppress playback claims, but audio can still be offered as unverified fallback.
- cost: Approximately $0.50–$2 per device for a secure element plus small firmware/relay storage and negligible API cost; a few milliamps only during attestation, otherwise no meaningful power change.  ·  latency: Adds one short signed heartbeat/receipt exchange, roughly tens to a few hundred milliseconds on LTE; playback start should not wait for a final receipt, only completion status should depend on it.
- security: Strongly improves device authenticity and replay resistance. Provisioning keys and recovery codes become sensitive; never expose private keys to the Mac bridge or browser.
- depends on: A real pendant hardware revision and firmware transport; Authoritative relay device registry and delivery-acknowledgement protocol; Durable audio object IDs bound to signed playback receipts


## What it asked for

_Nothing._
