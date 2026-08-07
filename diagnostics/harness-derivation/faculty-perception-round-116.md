# Harness derivation — faculty-perception — round 116

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-device-registry** — As of 2026-08-07T17:47:36Z, relay registry has home-macbook-bridge online and cloudflare-contract-test mobile offline; no nRF9160 pendant or ESP32 bridge is registered.
  - evidence: discover(devices) returned exactly Safari on MacIntel, home-macbook-bridge, cloudflare-contract-test; /ops/status relay payload says macBridgeOnline=true.
- **mac-input-reachability** — AI Pendant Agent is running but cannot synthesize UI input: Accessibility trusted=false, Screen Recording granted=false, inputReachability.status=failed; automation grants are present for System Events and many apps.
  - evidence: GET /observe at 2026-08-07T17:47:53.635Z reports eventsPost=false, uiActionsWillReachTheScreen=false; GET /ops/status reports permissions.ready=false.
- **browser-live-state** — Safari browser bridge is online with 3 tabs, zero pending commands; durable sessions include logged-in Gmail inbox (tab 901464, title Inbox (14,986)) plus two test-form tabs.
  - evidence: GET /browser/status and GET /observe at 17:47Z.
- **pipeline-audio-history** — Pipeline contains historical nrf9160/offline-store and cloud-relay runs, including a 24kHz mono PCM render accepted by relay, but this is recorded history rather than evidence of a currently registered pendant.
  - evidence: GET /pipeline response shows source=nrf9160 historical event and 24,000 Hz PCM metadata; live device discovery has no nRF9160.

## Capabilities it proposed

### "“Did you actually deliver that to me, or is it still only on the Mac?”"
- **useful because:** Today the relay can report a response accepted or waiting while no pendant is registered, and pipeline history can look like live evidence. This gives the owner an honest end-to-end answer: rendered, uploaded, device received, playback started, playback completed, or not delivered—never confuse stored history with current wearable reality.
- **path:** relay-realtime → mac-planner → faculty-perception → faculty-judgement → faculty-action → pendant
- **model tier:** background for receipt reconciliation; realtime only when the owner asks during a live exchange
- **latency:** Under 2 seconds for cached status; up to 10 seconds to reconcile relay, Mac pipeline, and a newly reconnecting pendant.
- **cost:** ~$0.005–$0.02 per reconciliation; dominated by a small text model only when receipts conflict, not by audio generation.
- **security:** Expose only this owner's job IDs and coarse delivery state; audio content stays on the Mac/relay unless the owner requests it. Require confirmation before replaying sensitive queued audio to a newly paired device.
- **missing:** A durable per-artifact receipt chain with monotonic sequence numbers and device playback acknowledgements; A live nRF9160 registration and playback receipt endpoint; A UI/voice response that labels historical telemetry as historical

### "“Give me a truth snapshot: what is live, what changed recently, and what are you only inferring?”"
- **useful because:** The system spans a Mac, authenticated Safari, relay, and an absent wearable, yet currently exposes these facts through disconnected diagnostics. A cited snapshot would prevent dangerous assumptions such as treating an old nRF9160 event as present connectivity, and would let the owner decide whether to act or wait.
- **path:** faculty-perception → mac-planner → browser-extension → relay-realtime → unified → faculty-judgement
- **model tier:** Cheaper background model compiles typed observations; realtime model only turns the compact result into a spoken answer.
- **latency:** Cached facts in under 1 second; refresh live Mac/browser/relay probes in under 5 seconds.
- **cost:** ~$0.002–$0.01 per refresh; most work is deterministic probes and hashing, with a small model for conflict explanation.
- **security:** Redact page contents and tokens by default; return only app/tab titles, connectivity, timestamps, confidence, and source. Authenticated-page details require an explicit narrower question.
- **missing:** A typed observation envelope (source, observedAt, expiry, confidence, sensitivity) across relay/Mac/browser; A conflict resolver that refuses to merge historical pipeline events into live device state; A compact spoken/dashboard rendering with citations

### "“When I reconnect my wearable, recover anything I missed—but prove what was delivered and don't repeat it.”"
- **useful because:** A disconnected wearable should not silently lose alerts or replay them twice. The current pipeline shows held alerts and late forwarding in history, but there is no owner-visible, exactly-once handoff proof. Combining relay persistence, Mac-generated audio, and pendant acknowledgements makes reconnect useful rather than misleading.
- **path:** relay-realtime → mac-planner → faculty-perception → faculty-judgement → faculty-action → pendant
- **model tier:** Background model ranks and compresses missed items; realtime model is reserved for an interactive reconnect conversation.
- **latency:** On reconnect, inventory within 2 seconds; spoken queue begins within 5 seconds; each item is committed only after a device receipt.
- **cost:** ~$0.01–$0.05 per reconnect batch, dominated by summarization/TTS; deterministic dedupe and receipts are negligible.
- **security:** Encrypt queued content, expire sensitive items, and require confirmation for messages marked private or action-triggering. Pairing changes must invalidate prior delivery tokens.
- **missing:** Durable outbox with per-item idempotency and expiry; Pendant-side received/started/completed acknowledgements persisted across reboot; Reconnect protocol that exchanges last acknowledged sequence, not just online status; Owner-visible missed-item review and replay controls

### "“Pin what I’m looking at.” (I press the pendant button while a page, message, or document is open.)"
- **useful because:** A physical button press should bind the owner’s fleeting real-world moment to the exact Mac/browser context: active app, authenticated tab, selected text, URL, and timestamp. Later they can ask “what was that thing I pinned?” without reconstructing which tab or window they meant. This is a genuinely cross-body memory primitive: the pendant supplies intentional physical timing, Safari supplies private page context, the Mac supplies app state, and the relay provides durable retrieval.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → faculty-perception → faculty-action
- **model tier:** Background model extracts a short title and entities; realtime is unnecessary except when the owner immediately asks about the pin.
- **latency:** Acknowledge the button locally within 150 ms; capture and persist the context within 3 seconds.
- **cost:** <$0.01 per pin; deterministic metadata capture dominates, with optional small-model extraction.
- **security:** Never upload page body by default. Store URL/title/selection hash and a redacted excerpt unless the owner explicitly enables full capture. Private tabs and passwords must be excluded. The physical press is the consent boundary.
- **missing:** Pendant button event transport with a monotonic timestamp and local acknowledgement; Mac active-window/document context snapshot API that works without Accessibility where possible; Browser command to capture the active tab’s URL, title, selection, and content hash atomically; A durable pin object with retention, redaction, and owner deletion controls

### "“When I point at something with the pendant, tell me what it is and connect it to what I’m doing.”"
- **useful because:** The wearable should bridge physical surroundings and digital intent: a button/camera or short spoken description identifies an object, while the Mac/browser context supplies the task. For example, a photographed cable can be matched against an open repair guide, or a document on the desk can be matched to the relevant logged-in form. No single node can do this: the pendant supplies physical evidence, the Mac supplies private task context, Safari supplies authenticated pages, and the relay coordinates them.
- **path:** pendant → relay-realtime → mac-vision → browser-extension → mac-planner → faculty-perception → faculty-judgement
- **model tier:** Realtime vision/audio model for the immediate identification; cheaper background model performs cross-context matching and citation.
- **latency:** Initial spoken identification in 2–4 seconds; task linkage and sourced suggestions within 10 seconds.
- **cost:** ~$0.03–$0.15 per inspection, dominated by image/audio inference and optional private-page extraction.
- **security:** Physical images and private browser context leave the device only after an explicit button press. Faces, screens, and credentials require automatic redaction. Never infer a purchase, message, or form submission from an image without confirmation.
- **missing:** A pendant camera or a supported phone-camera handoff; current wearable hardware has no established imaging path; A secure multimodal upload with image retention limits and redaction; A context join protocol for pairing one physical inspection with the current Mac/browser task; Evidence citations linking visual claims to the captured frame and page excerpt

### "“Tell me when the world and my computer disagree about what just happened.”"
- **useful because:** The owner should receive a concise discrepancy report when, for example, a website shows a payment as submitted but the Mac job receipt says it stopped, a relay says audio was accepted but no wearable exists, or Calendar and an authenticated work portal show conflicting meeting times. This is not another watcher: it is a cross-system contradiction detector that refuses to collapse incompatible evidence into one confident story.
- **path:** faculty-perception → faculty-judgement → mac-planner → browser-extension → relay-realtime → unified
- **model tier:** Deterministic pairwise assertions and timestamps first; a cheaper background model explains the contradiction and ranks which source should be checked. Realtime only speaks an urgent discrepancy.
- **latency:** Detect within 30 seconds of an observed event; explain on demand in under 3 seconds.
- **cost:** <$0.02 per event batch; most work is normalized state comparison, with a small model only for explanation.
- **security:** Compare typed claims and hashes rather than copying private page contents. Keep source-specific access controls. A contradiction alert must never itself retry or mutate an external transaction.
- **missing:** A shared assertion schema with subject, predicate, value, observedAt, source, freshness, and authority; Event correlation IDs spanning browser mutations, Mac jobs, relay artifacts, and device receipts; Authority rules for common conflicts (for example, a fresh page confirmation outranks a stale local receipt); An owner-facing discrepancy queue with explicit resolution and dismissal semantics


## Changes it proposed to its own stack

### `relay` — Add a live-delivery contradiction gate: before any relay result is labeled “waiting for the pendant,” “delivered,” or “playable,” join the job with the authoritative device registry and receipt sequence. If no pendant is registered, label it “stored—no wearable connected”; if telemetry is older than its expiry, label it historical; never let old nrf9160 pipeline rows satisfy a current delivery claim.
- **owner gets:** The owner stops hearing confident but false assurances when a response exists only in Mac/relay storage. They can trust that “delivered” means a real device acknowledged it.
- effort: Medium: relay schema/status logic plus tests for absent, reconnecting, duplicate, and stale-device cases.  ·  risk: A registry outage may downgrade honest statuses to unknown and delay playback; recover by retaining the artifact and retrying reconciliation, never by guessing delivered.
- cost: Negligible compute/storage; no model call required.  ·  latency: Adds one D1/registry lookup, typically tens of milliseconds.
- security: Improves privacy by preventing sensitive audio from being replayed to an unverified or stale device; requires authenticated device/job joins.
- depends on: authoritative relay device registry and delivery acknowledgments; durable per-job artifact sequence and expiry


## What it asked for

_Nothing._
