# Harness derivation — mac-planner — round 109

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If an answer starts playing on my pendant and LTE drops, resume it exactly where it stopped when the link returns—without re-rendering or repeating what I already heard."
- **useful because:** Long spoken briefs and replies become dependable on a wearable with intermittent cellular coverage. The owner hears one continuous answer instead of a truncated response or a restart, while the relay retains only the existing response object and the pendant uses its SD as a failure buffer rather than routine storage.
- **path:** relay-realtime → mac-planner → pendant → dashboard
- **model tier:** Use the realtime tier only for the live spoken response; use the relay's durable job/audio machinery and deterministic firmware protocol for checkpointing and resumption. No extra model call is needed on reconnect.
- **latency:** Initial playback unchanged. Reconnect resume should begin within one network round trip (target under 2 seconds); checkpoint acknowledgements should be piggybacked on existing chunk traffic.
- **cost:** Negligible model cost; modest D1/R2 metadata writes per response (chunk index and playback lease), with bandwidth dominated by audio already being delivered. Avoid polling and avoid duplicate TTS.
- **security:** Bind checkpoints to an authenticated job, device nonce, and content hash so an old response cannot be replayed into a new session. Encrypt any undelivered chunks in the existing transport. Respect the owner's rule that SD is written only when upload/playback fails, and expire response objects under the retention policy.
- **missing:** A versioned audio manifest containing content hash, codec, sample rate, chunk hashes, and duration; Pendant firmware playback checkpoint/ack messages with durable last-heard chunk and sample offset; Relay resume endpoint that returns only missing chunks and rejects stale leases; Mac pipeline integration that treats an existing rendered PCM object as resumable rather than invoking TTS again; End-to-end interruption/reconnect tests with duplicate, reordered, and partially buffered chunks

### "What is still pending? Give me one short status across my pendant, Mac jobs, and browser work, and tell me what will happen automatically when each connection returns."
- **useful because:** Today pending work is fragmented: the browser is offline with queued commands, Mac jobs have receipts, and the pendant can hold alerts. A single spoken inventory prevents duplicate requests and makes offline behavior legible without opening the dashboard.
- **path:** relay-realtime → pendant → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic aggregation and priority rules on the relay; use the realtime model only to phrase the final short spoken sentence when the owner asks. No background model spend for unchanged state.
- **latency:** Under 1 second from cached state; at most one parallel status refresh when a source is stale.
- **cost:** Near-zero model cost for normal status; small relay reads from D1 and existing Mac/browser status endpoints. No audio generation unless requested by voice.
- **security:** Return only job metadata (owner-visible labels, age, state, retry plan), never page contents or secrets. Bind browser items to the authenticated extension/session and mark stale or unknown rather than claiming completion. Do not auto-cancel or retry mutations from this read-only status.
- **missing:** A relay aggregator with a normalized PendingItem schema and source-specific freshness timestamps; A pendant-held-alert status route and browser queue item metadata route, not just counts; A deduplication key linking a relay intent to its Mac job/browser command/pending alert; A compact spoken formatter with explicit states: queued, running, waiting-for-device, failed, completed-but-undelivered

### "Let the pendant notify me privately about only urgent events: use distinct vibration/light patterns for a calendar deadline, a browser account change, and a completed Mac job, and let me acknowledge or snooze each with the button without opening my phone."
- **useful because:** The owner currently has to ask for status or hear every response. A private, glance-free alert channel would make the wearable useful while walking or in a meeting, while urgency filtering prevents notification fatigue. It depends on browser, Mac, relay, and pendant acting as one system rather than any one surface alone.
- **path:** relay-realtime → mac-planner → browser-extension → pendant → dashboard
- **model tier:** Deterministic event normalization and urgency rules on the relay; use a cheaper background model only when an event needs semantic classification. Realtime is unnecessary unless the owner asks for a spoken explanation.
- **latency:** Urgent event delivery within 5 seconds of source receipt; button acknowledgement should be handled locally in under 100 ms and synchronized when connectivity returns.
- **cost:** Near-zero inference for typed events; occasional low-cost classification for ambiguous page changes. Small cellular payloads; hardware change roughly $3–$8 BOM for a low-power haptic actuator, driver, and RGB/status LED upgrade.
- **security:** Transmit only redacted event title, urgency, source, and expiry—not email/page contents. Require explicit per-source subscriptions and quiet hours. Acknowledge/snooze must be idempotent and device-bound; never treat a vibration acknowledgement as approval to send, buy, delete, or submit.
- **missing:** A normalized cross-surface alert schema with urgency, expiry, deduplication key, and acknowledgement state; Relay fan-out from Calendar/Mail/Mac jobs and authenticated browser watches to the pendant, with offline queueing and expiry; Pendant firmware for local alert patterns, button actions (acknowledge, snooze, dismiss), and durable event IDs within the 211,608 B application RAM budget; A haptic actuator and richer LED on the product pendant; the current prototype's single LED/button is insufficient for reliably distinguishing alert classes; Dashboard controls for subscriptions, quiet hours, urgency thresholds, and an audit trail of delivered/acknowledged alerts

### "Keep one task synchronized wherever I continue it: if I start dictating on the pendant, edit the draft on my Mac, and then review it in a logged-in browser tab, show me one current version and exactly what changed instead of creating duplicates or overwriting edits."
- **useful because:** The owner can move naturally between voice, desktop, and authenticated web sessions without losing work or accidentally acting on an old draft. This is especially valuable when links drop or a browser tab is restarted, because the system can reconcile progress rather than silently replaying it.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use deterministic operation logs, version vectors, and field-level three-way merge first; use a cheap background model only to explain semantic conflicts. Realtime is only for the owner's spoken request or conflict summary.
- **latency:** Local edits should appear immediately; cross-surface sync within 2 seconds when online. Conflict explanation under 3 seconds and never blocks saving a new version.
- **cost:** Low API cost: mostly metadata and diffs, with occasional small-model conflict explanations. Storage grows with compact operations and periodic snapshots, not full duplicate documents.
- **security:** Keep per-field provenance and sensitivity labels; never merge secrets across accounts or browser sessions. A conflict involving a send/submit/delete operation must remain a draft and require the owner's existing confirmation policy. Encrypt drafts and expire abandoned authenticated-session bindings.
- **missing:** A shared task/draft identity and operation-log protocol spanning relay, Mac files, and browser form fields; Field-level provenance with base version, actor surface, timestamp, and source locator; Three-way merge plus explicit unresolved-conflict representation and a review UI/audio summary; Browser session rebind and Mac file watcher hooks that publish edits without scraping unrelated content; Idempotent commit tokens so reconnects cannot duplicate a browser fill or Mac write


## Changes it proposed to its own stack

### `firmware` — Add a resumable 24 kHz playback protocol: the relay sends a signed manifest and fixed-size audio chunks; the nRF9160 acknowledges the highest fully verified chunk plus sample offset; on link loss it writes only unplayed/partial chunks to the existing microSD failure buffer, and on reconnect requests a range by content hash. The Mac pipeline must publish the manifest once and never synthesize again for a resume.
- **owner gets:** A long answer remains continuous across elevator rides, dead zones, and reconnects. The owner does not hear repeats, lose the end of a briefing, or wait for a second TTS render.
- effort: Medium: protocol/schema shared by firmware and relay, state-machine changes in playback and pipeline upload, plus an interruption test harness. No new model work.  ·  risk: Power loss or a corrupt checkpoint could skip or repeat a small boundary; recover by replaying the last acknowledged chunk and validating hashes. Stale manifests must be rejected by device nonce/content hash. Existing SD failure-buffer semantics must remain unchanged.
- cost: No additional inference cost. Small D1 metadata and request overhead; SD writes only on failure. RAM impact should stay bounded by one manifest plus one/two audio chunks, not whole-response buffering.  ·  latency: No change to first-byte playback; reconnect adds one manifest/range request, target under 2 seconds.
- security: Requires authenticated device-bound manifests, per-chunk integrity hashes, and expiry/lease checks so an old response cannot be resumed by another session.
- depends on: 24 kHz audio path emits stable chunk boundaries and a content hash; Relay audio routes persist response object references long enough for a resume lease; Pendant firmware exposes playback position and durable checkpoint storage

### `hardware` — Replace the prototype's single LED-only notification path with a low-power coin/LRA haptic actuator plus a tri-color LED and a GPIO-capable button controller. Define three short patterns (urgent, informational, waiting) and a long-press local quiet toggle; expose a battery-safe driver and persist only alert ID/state, not content.
- **owner gets:** They can recognize and control important events discreetly in a meeting or outdoors, without taking out a phone or listening to unsolicited speech. Different patterns make the alert actionable even when the screen and audio are unavailable.
- effort: Small-to-medium hardware revision and firmware driver work: enclosure/PCB change, power characterization, pattern state machine, and relay event integration. Existing dev-kit firmware can prototype the protocol before a product board spin.  ·  risk: Added vibration and LED draw may reduce battery life; mitigate with duty-cycle limits, a battery threshold, and a local quiet mode. A failed actuator must degrade to LED/audio and never block normal command delivery.
- cost: Approximately $3–$8 added BOM at low volume; roughly 5–30 mA while vibrating and negligible idle current, subject to actuator choice. No model/API cost.  ·  latency: Local acknowledgement is immediate; cellular delivery remains the dominant delay.
- security: Patterns must encode only coarse urgency, never secret text. Persist opaque event IDs and timestamps; do not log sensitive alert payloads on the pendant.
- depends on: Relay normalized alert schema and subscription policy; Pendant firmware event acknowledgement and offline queue protocol; Battery/power budget validation on the final wearable enclosure


## What it asked for

_Nothing._
## Its own summary

Discovered the live system and recorded two new cross-surface proposals. The browser bridge is currently offline with 7 pending commands; the pipeline shows 24 kHz mono PCM rendering already works, but current delivery has no verified chunk manifest/checkpoint/resume semantics. Proposed (1) exact playback continuation after LTE loss using content-hashed manifests, chunk acknowledgements, and the pendant's SD only as a failure buffer; and (2) one spoken pending-work inventory aggregating Mac jobs, browser queue, pipeline state, routines, and pendant-held alerts. The first needs firmware↔relay protocol work and Mac reuse of rendered audio; the second needs a normalized relay PendingItem aggregator and missing pendant/browser metadata routes.

**Biggest unknown:** Whether the current pendant firmware can expose a durable playback sample offset and whether the relay's existing audio object IDs remain fetchable long enough to support a resume lease; these require implementation-level inspection, not more Mac discovery.

