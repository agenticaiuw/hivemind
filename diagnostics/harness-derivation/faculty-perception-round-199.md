# Harness derivation — faculty-perception — round 199

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac perception and access state** — At 2026-08-08T23:01Z the Mac bridge and Safari browser extension are online; Mac permissions report Accessibility and Screen Recording granted, all listed automation permissions granted, and ready=true. Relay is reachable and macBridgeOnline=true. No pendant appears in the device inventory; only home-macbook-bridge is online and cloudflare-contract-test is offline.
  - evidence: read_continuity_snapshot(include=['relay','pipeline'], since='2026-08-08T22:50:00Z', maxItems=20) resolved to GET /ops/snapshot HTTP 200; discover:devices independently listed Safari on MacIntel online, home-macbook-bridge online, cloudflare-contract-test offline.

## Capabilities it proposed

### "Before you act, tell me whether the world is in a state where this request is safe and knowable — for example, “Can you verify the page I’m about to send is the one I mean?”"
- **useful because:** The system currently can act with live browser and Mac access, but perception cannot produce a compact pre-action reality fence. This would show the current tab/app, permissions, freshness, and any unresolved identity mismatch, then explicitly separate observed facts from assumptions before faculty-action proceeds.
- **path:** relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use the realtime model only to interpret the spoken request; use deterministic Mac/browser collectors and a cheap text model (or no model) to assemble the evidence card.
- **latency:** Under 2 seconds when the browser extension and Mac bridge are online; 5 seconds if a fresh screenshot or browser inspection is required.
- **cost:** Negligible model cost for deterministic checks; at most one short text-model call. Dominant cost is an optional screenshot/inspection round trip.
- **security:** Never include page bodies or secrets in the relay summary by default. The card must name the exact tab/app and freshness, mark login/permission uncertainty, and require owner confirmation before any irreversible action.
- **missing:** A perception endpoint that joins GET /ops/snapshot, GET /browser/status or POST /browser/inspect, and the current Mac input-reachability state into one signed, time-stamped evidence card.; A policy hook in faculty-action that blocks execution when the card is stale or contains unresolved target identity.

### "Is the wearable actually present and healthy right now, or am I only talking to the Mac? Give me a proof, not an inference."
- **useful because:** Today the registry can say the pendant is absent, but that is structurally ambiguous because the firmware does not heartbeat and converse does not register it. A bench-aware answer would distinguish no USB device, USB device with no firmware response, relay-connected pendant, and Mac-only audio history — preventing the hive from treating old pipeline records as live wearable state.
- **path:** relay-realtime → mac-terminal → mac-planner → faculty-perception → faculty-judgement
- **model tier:** Deterministic protocol parsing and freshness calculation; no realtime or background LLM call is needed.
- **latency:** 1 second for cached status; up to 3 seconds for bounded serial probes on the two known ports.
- **cost:** No model cost. Small implementation cost for a read-only serial probe and a relay registry join.
- **security:** Read-only, bounded byte/time budgets, no firmware flashing and no SD writes. Redact serial payloads and expose only build/session IDs, monotonic freshness, and link state. Treat a cable as bench evidence, never as owner location.
- **missing:** The accepted mac_usb_serial_diagnostics grant needs a live implementation with explicit nRF9160 and ESP32 port selectors, read_ms, and max_bytes.; A relay-side device identity handshake that associates a firmware health frame with a registered device without using the admin API key.; A single perception route that joins serial proof, GET /v1/devices/status, and GET /pipeline while labeling historical audio separately.

### "Do two independent surfaces agree about what I’m looking at? If not, stop and tell me exactly which observation disagrees."
- **useful because:** A single live observation can be stale or mis-targeted. A perception quorum would compare the browser extension's tab identity and URL, the Mac's frontmost-app/window observation, and (when available) a screenshot/OCR or relay browser read. It would catch the dangerous case where the voice model names one page while the action surface is on another, instead of silently choosing one.
- **path:** relay-realtime → browser-extension → mac-vision → mac-planner → faculty-perception → faculty-judgement
- **model tier:** Deterministic field comparison first; a cheap text model only summarizes a disagreement. Realtime is not needed except to understand the spoken target.
- **latency:** 1–2 seconds for metadata-only quorum; up to 4 seconds if a fresh screenshot/OCR is requested.
- **cost:** Usually zero model cost; screenshot/OCR bandwidth and one local vision pass dominate exceptional cases.
- **security:** Do not upload screenshots to the relay unless explicitly needed. Hash and retain metadata by default, redact page text, and make disagreement a hard stop for destructive actions. A matching URL is not proof of matching content, so expose content freshness separately.
- **missing:** A common observation envelope with source, capturedAt, target identity, content hash where permitted, and confidence; current surfaces report these facts in incompatible shapes.; A perception quorum route that reads browser state and Mac observation atomically enough to detect races, then emits a monotonic observation ID consumed by faculty-judgement.; A browser-extension result contract that includes the active tab's stable session/window identity rather than only a transient command result.

### "Watch this page, file, or device state and tell me only when a verified change occurs — not when the browser reconnects, the relay retries, or the observation merely gets refreshed."
- **useful because:** The owner cannot currently ask the hive to maintain a trustworthy observation over time. A browser tab can change while the Mac sleeps, a relay read can be stale, and reconnect noise can look like an event. This gives them a quiet, evidence-backed change detector rather than a stream of false alarms.
- **path:** browser-extension → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Deterministic polling, content hashing, and field-level diffs; use a cheap background model only to summarize a confirmed delta. Realtime is used only when speaking the notification.
- **latency:** User-configurable, from 5 seconds for an active tab to 15 minutes for low-power monitoring; notification within one polling interval after a confirmed change.
- **cost:** Near-zero model cost for metadata/hash changes; occasional short summarization call dominates when human-readable explanation is requested.
- **security:** Monitoring must be explicit, scoped to one tab/file/device, and revocable. Keep hashes and minimal changed regions by default; never persist full page contents or secrets. Expire watches automatically and require confirmation before any follow-up action.
- **missing:** A durable watch record with target identity, observation source, polling interval, last content hash, and owner-selected change predicate.; A browser-side read or event subscription that can survive extension reconnects without treating reconnect as a change.; A relay scheduler/notification path that deduplicates confirmed deltas and records whether the owner was actually notified.

### "For this kind of question, use my evidence rule: do not answer from one source; require two independent live observations, and tell me when that rule cannot be satisfied."
- **useful because:** The owner cannot currently set a durable standard for what counts as enough evidence. Some questions are harmless with one observation, while identity, money, privacy, and physical-presence claims need corroboration. This lets the owner choose the threshold instead of inheriting hidden model confidence.
- **path:** relay-realtime → faculty-perception → faculty-judgement → mac-planner → browser-extension
- **model tier:** Policy evaluation and source counting should be deterministic. A cheap text model may translate the rule into a human explanation, but must not override it.
- **latency:** Under 1 second for policy lookup and source availability; up to 3 seconds for the second observation.
- **cost:** Negligible recurring model cost; storage is a small set of owner-authored predicates and audit records.
- **security:** Rules are owner preferences and must be versioned, reviewable, and scoped by task type. A source must not count as independent if it is merely a relay copy of the same Mac observation. Failure to meet the rule must block or qualify the answer, never silently lower the threshold.
- **missing:** A policy language for evidence requirements such as source classes, freshness windows, independence, and minimum confidence.; A provenance graph that can distinguish independent browser, Mac, relay, and future device observations from duplicated exports.; A judgement gate that refuses to proceed when the configured evidence rule is unmet, with an explicit one-turn override requiring confirmation.

### "Show me where your perception has been wrong lately: which surface made a claim, what later contradicted it, and how often each kind of observation fails."
- **useful because:** The owner has no way to tell whether the hive's confidence is deserved. A device can appear online while its audio is unusable, a browser read can be stale, and a completed job can precede playback. A continuously measured calibration report would turn isolated surprises into visible reliability numbers and guide when the system must abstain.
- **path:** faculty-perception → faculty-judgement → relay-realtime → mac-planner → browser-extension → mac-vision
- **model tier:** Deterministic event matching and outcome scoring; use a background inexpensive model only to cluster failure explanations. Never use the realtime tier for bookkeeping.
- **latency:** No foreground latency; update after matched outcomes or at most hourly. An on-demand report should return in under 3 seconds.
- **cost:** Low storage and compute cost. The dominant cost is optional background clustering of disagreement descriptions.
- **security:** Retain only compact event IDs, source classes, hashes, and outcome labels; do not build a surveillance history of page contents or speech. Let the owner delete the calibration ledger and distinguish genuine contradiction from an unobserved outcome.
- **missing:** A durable prediction/observation/outcome ledger with explicit match windows and source independence.; Outcome emitters for browser mutations, Mac action receipts, relay delivery, and eventual device playback, so lack of confirmation is not scored as failure.; A dashboard and voice query that report coverage separately from accuracy; unknown outcomes must not become false successes.


## Changes it proposed to its own stack

### `context` — Make every cross-surface observation carry a typed reality label: observed_live, observed_historical, inferred, or unknown, plus capturedAt, source, and freshness deadline. Teach /ops/snapshot and pipeline exports to preserve those labels instead of flattening old audio traces and current liveness into one status field.
- **owner gets:** When the owner asks “did it hear me?” or “is the pendant connected?”, the answer will not quietly promote a completed Mac run or recorded pipeline event into live wearable evidence. They get an honest answer with the exact boundary of what is known.
- effort: Moderate: define the envelope, adapt snapshot/pipeline serializers, and update faculty-perception and faculty-judgement consumers; no new model required.  ·  risk: Older records lack labels and could be misclassified. Mark them historical/unknown during migration rather than guessing. Increased payload size could affect snapshot truncation; cap evidence metadata and keep bodies out.
- cost: No recurring model cost; a small increase in relay/Mac storage and snapshot bytes.  ·  latency: Negligible for cached metadata; a few milliseconds of serialization.
- security: Improves privacy by keeping source metadata while excluding raw audio/page bodies. Ensure device IDs and URLs remain redacted according to existing sanitization.
- depends on: The existing GET /ops/snapshot and GET /pipeline serializers; The accepted offline-reality-beacon and offline-capture-integrity-sentinel firmware outputs when a pendant exists; A defined device_playback/played event if playback claims are to become observed_live


## What it asked for

_Nothing._
