# Harness derivation — faculty-judgement — round 171

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Continue the thing I was doing before the Mac, browser, or connection died—without repeating anything or sending anything unless I approve the changed step.”"
- **useful because:** This is the highest-value trust feature: an interrupted job becomes recoverable rather than silently stuck for 24 hours or accidentally duplicated. It uses the pendant as the durable human checkpoint, the relay as the always-awake coordinator, and the Mac/browser as the only places that can inspect current state.
- **path:** pendant → relay → mac → browser
- **model tier:** A cheap background model reconstructs the last safe checkpoint and summarizes differences; realtime is used only for the owner's spoken request. Deterministic lease, idempotency, policy, and revalidation code makes the safety decision without an expensive model.
- **latency:** Initial answer under 2 seconds from relay cache; state inspection 5–15 seconds. Any external mutation pauses for a physical pendant approval and a fresh state check.
- **cost:** About $0.005–$0.03 per recovery, dominated by browser/Mac reads and a small summarization prompt; no model call for unchanged or already-completed work.
- **security:** Never replay a stale mutation. Revalidate the prepared plan and evidence, compare action identity/idempotency keys, fail closed on changed prices/recipients/permissions, and require the existing physical transaction approval latch for irreversible effects. Do not send page contents to the pendant; speak only a redacted diff.
- **missing:** relay_jobs lease_until plus expiry/requeue sweep; durable relay-job ↔ Mac-job correlation (today localJobId is only telemetry); a recovery coordinator that reads receipts/journal and emits a typed checkpoint; browser/Mac adapters that expose current state for the specific pending plan

### "“What did I actually hear, see, or miss today—not what the system generated?”"
- **useful because:** A generated briefing is not delivery. The owner needs to distinguish queued, downloaded, playback-started, finished, interrupted, checksum-failed, and never-reached-me items, especially after wearing the pendant offline or while the Mac/browser was disconnected. This turns the system from claiming completion into reporting lived reality.
- **path:** pendant → relay → mac → browser
- **model tier:** Deterministic aggregation first; a cheap background model compresses only the event set the owner asks about. Realtime speaks a short result, never inventing playback from server receipts.
- **latency:** Under 1 second for the last 24 hours if the delivery index is warm; up to 5 seconds when reconciling offline ACKs.
- **cost:** Usually under $0.005; storage/indexing dominates, not inference. Delivery events are tiny and can be deduplicated by eventId.
- **security:** Expose artifact IDs and source labels, not audio or private text by default. Require provenance lookup before revealing content. Treat a playback_started ACK as evidence of attention only to that point—not proof the owner understood it—and preserve interrupted/no_audio states.
- **missing:** durable delivery-event index and a read/query route by artifact, briefing item, and time window; a server-side join from artifactId to briefing item/source without exposing raw audio; reconciliation rules for out-of-order offline ACKs and duplicate deviceSequence values; a privacy-aware spoken formatter for sensitive item titles

### "“When I’m in a meeting, keep the world from acting on my behalf; collect only the work that can safely wait, then give me one review queue when the meeting ends.”"
- **useful because:** The dangerous failure is not merely an interruption: a browser or Mac job can submit an email, form, purchase, or reply while the owner is unavailable. This capability creates a bounded meeting transaction across calendar timing, browser sessions, Mac jobs, relay scheduling, and the pendant’s later physical review. It protects attention and prevents accidental commitments.
- **path:** mac → browser → relay → pendant
- **model tier:** Deterministic policy and calendar-window checks do the gating; a cheap background model clusters queued drafts after the meeting. Realtime only reads the review queue when the owner asks.
- **latency:** Meeting-entry decision under 1 second; queued work appears immediately in the local review queue; post-meeting digest under 3 seconds.
- **cost:** Under $0.01 per meeting, mostly one summarization call if there are queued items. Calendar and job reads are local.
- **security:** Do not infer that a calendar event means the owner is physically present; label it as a scheduled meeting window and allow a manual override. Default to read/draft only, never send or spend. Revalidate every draft against current browser/Mac state, expire it at the meeting boundary, and require the existing physical transaction approval latch for any external side effect. Sensitive titles stay off spoken output unless the owner policy explicitly allows them.
- **missing:** a typed meeting-window state source that distinguishes scheduled time from observed presence; a shared policy hook that makes POST /execute, browser commands, and relay jobs consult the same meeting state; a durable holding queue with expiry and per-item reason ('deferred by meeting window'); calendar EventKit permission/readability validation, since empty unauthorized reads currently look like a clear calendar

### "“Find the thing I’m thinking of across my Mac files and the authenticated browser, but do not upload my private corpus or read the contents aloud until I choose a result.”"
- **useful because:** Today search is fragmented: the Mac, browser session, relay memory, and pendant cannot perform one privacy-preserving query. The owner has to remember where information lived and manually move it between surfaces. A federated search would return ranked, source-linked candidates while keeping raw data at its origin.
- **path:** pendant → relay → mac → browser
- **model tier:** A small local model on the Mac/browser ranks locally produced candidate metadata. The relay coordinates query IDs and merges only redacted titles, hashes, and provenance. Realtime is used only to clarify an ambiguous spoken query.
- **latency:** First candidates in 2–4 seconds; deeper search up to 15 seconds. The pendant speaks only a short candidate list and waits for a deliberate selection before revealing content.
- **cost:** $0.002–$0.02 per query; local indexing and browser reads dominate. No cloud cost for documents that remain local.
- **security:** Raw file contents and authenticated page bodies must never be sent to the relay by default. Each surface returns a bounded, sensitivity-classified candidate envelope; secrets produce an existence-only result. Opening a candidate requires owner confirmation, provenance display, and an explicit trusted-origin policy. Search indexes need encryption, expiry, and deletion propagation.
- **missing:** a common federated-query protocol with origin-local execution and bounded result envelopes; Mac file index and browser-session search adapters that return provenance without raw bodies; a relay merge/ranking endpoint that cannot request unrestricted source content; cross-store deletion and revocation propagation for indexed candidates

### "“Where did I leave my keys/wallet/bag, and what is the last trustworthy evidence—not a guess?”"
- **useful because:** The pendant is always with the owner, but the system has no memory of physical objects or departures. A cross-surface last-seen service could combine deliberate pendant markers, Mac camera observations, browser purchase/receipt evidence, and relay-held history. It would answer a daily problem no single node can solve.
- **path:** pendant → relay → mac → browser
- **model tier:** A background vision model labels only the requested object in local Mac images; a cheap deterministic layer merges timestamps and confidence. Realtime speaks an uncertainty-qualified answer, never a fabricated location.
- **latency:** Under 3 seconds for indexed evidence; 10–30 seconds for a fresh local camera check. No camera activation without an explicit owner request.
- **cost:** $0.01–$0.10 per fresh visual check depending on model use; indexed lookups are negligible. Optional BLE/UWB tags add roughly $20–$50 per tagged object.
- **security:** Images remain on the Mac and are cropped/redacted before any relay transfer. Other people in frames must be blurred or omitted. Location history is sensitive and should have short retention, explicit deletion, and a confidence/provenance trail. The system must say “last observed” rather than “is there.”
- **missing:** a physical-object identity/tagging model and local object index; Mac-local camera observation capture with person/background redaction; optional BLE/UWB tag ingestion from the pendant or Mac; a durable, revocable last-seen evidence store and owner-facing uncertainty formatter


## Changes it proposed to its own stack

### `relay` — Add a USB-local session mode: when the nRF9160 and ESP32 are attached to the Mac, the Mac bridge becomes a mutually authenticated low-latency relay for pendant audio, control, delivery ACKs, and stop tokens, while cloud LTE remains an optional uplink. The mode should advertise its transport and trust scope, preserve the same artifact/job IDs, and hand off queued work to cloud only after the cloud session is authenticated.
- **owner gets:** The pendant is physically usable today even though it is not LTE-registered. The owner should be able to press the real device on the desk and have a conversation, stop playback, and receive replies without pretending the absent cellular path exists. When they unplug, queued state should survive rather than becoming a second, confusing product.
- effort: Medium-high: serial framing/authentication, Mac bridge transport selection, session handoff tests, and hardware soak tests over both chips.  ·  risk: A stale or spoofed USB peer could receive audio or inject controls. Bind the session to the Mac agent’s bearer identity and a device nonce, fail closed on framing/authentication errors, and keep the universal stop token and privacy latch effective locally. Recover by dropping to offline store-and-forward; never silently switch from local to cloud for sensitive audio.
- cost: No new hardware; modest engineering and test cost. No per-utterance cloud cost when the owner stays local, though model/TTS cost remains if cloud inference is used.  ·  latency: Could remove cellular round trips and make local control near-interactive; cloud inference remains the dominant delay. Handoff may add one authenticated session round trip.
- security: Expands the trusted transport surface to USB, so it needs explicit session binding, nonce replay protection, transport labeling in receipts, and no raw secrets in device envelopes.
- depends on: USB-tethered local voice feasibility context (already requested and still pending); a real serial transport implementation for the nRF9160 and ESP32 bridge; shared artifact/job correlation IDs; the accepted universal_stop_latch, audio_delivery_ack_queue, and offline_privacy_panic_wipe firmware behaviours

### `hardware` — Add a low-power UWB/BLE ranging channel and a small set of owner-configurable object tags, with the pendant recording only opaque tag sightings and coarse relative distance—not audio, images, or continuous location. The Mac bridge would fuse those sightings with explicitly requested local camera observations, while the relay stores only short-lived, provenance-linked last-seen summaries.
- **owner gets:** The owner could ask where an important object was last seen and get evidence grounded in the device they wear, instead of relying on memory or a cloud location guess. It also gives the pendant a useful offline capability when the Mac and relay are unavailable.
- effort: High: new radio/tag hardware, antenna and power testing, firmware ranging support, Mac BLE/UWB ingestion, object enrollment UX, and privacy-preserving evidence storage.  ·  risk: Tags can reveal movement patterns or be used to track the owner. Enrollment must be deliberate, tag IDs must rotate, raw ranging data must expire quickly, and a physical privacy latch must disable sightings locally. Recovery is deletion of the tag identity and all derived records; no continuous history should be reconstructable.
- cost: Approximately $20–$50 per tag and $5–$20 incremental pendant BOM depending on UWB implementation; modest battery impact from periodic ranging, with event-driven sampling preferred.  ·  latency: Local tag sightings can be near-real-time; cloud answers depend on link availability. Ranging should be opportunistic and never delay voice capture or playback.
- security: Introduces a new proximity sensor and tracking surface. Require rotating identifiers, authenticated enrollment, encrypted local storage, explicit retention limits, and owner-visible sensor state.
- depends on: a pendant board revision or external BLE/UWB accessory; Mac-local object observation and redaction pipeline; relay support for short-lived physical-evidence summaries; an owner-configurable object enrollment and deletion policy


## What it asked for

_Nothing._
