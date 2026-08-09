# Harness derivation — faculty-perception — round 176

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac and browser reachability** — At 2026-08-08T04:41Z, Mac local agent is ready with Accessibility and Screen Recording granted; relay is reachable with macBridgeOnline true; Safari browser bridge is online with one tab and zero pending commands. This is current Mac/browser/relay liveness only and says nothing about pendant playback.
  - evidence: GET /ops/snapshot and GET /ops/status returned permissions.ready=true, accessibility.trusted=true, screenRecording.granted=true, relay.reachable=true, relay.macBridgeOnline=true, browser.online=true.

## Capabilities it proposed

### "When I ask “what actually happened with that?”, reconstruct the event as a causal timeline across the relay, Mac, browser, and audio path, and tell me what is proven, inferred, and still unknown."
- **useful because:** A completed Mac job currently cannot establish that the relay delivered audio or that anyone heard it. This gives the owner an honest incident report instead of a misleading green status.
- **path:** relay-realtime → mac-planner → browser-extension → unified → faculty-perception → faculty-judgement
- **model tier:** background for timeline assembly; realtime only to phrase the final one-sentence answer
- **latency:** Under 3 seconds for recent records; up to 10 seconds when joining browser and pipeline histories.
- **cost:** Low: mostly route reads and deterministic joins; one short model call only when records conflict or need summarization.
- **security:** Do not expose page bodies or secrets in the report; retain IDs, timestamps, hashes, and bounded excerpts only. Require confirmation before any retry or corrective action.
- **missing:** A durable cross-surface correlation ID propagated from voice turn to Mac job, browser command, relay job, and audio artifact; A device-originated played/interrupted event; current completion is not hearing evidence; A resolved authenticated continuity snapshot route (the granted tool currently fails resolver matching)

### "Before you repeat or act on an old result, tell me whether the evidence is still fresh, whether the source changed, and whether the result was ever actually acknowledged by a device."
- **useful because:** The system has count-capped Mac history, read-side-only announcement expiry, and no real pendant playback acknowledgement. Freshness-aware answers prevent stale research, duplicate briefings, and false claims that I heard something.
- **path:** relay-realtime → mac-planner → browser-extension → unified → faculty-perception
- **model tier:** Cheap deterministic freshness and hash comparison first; background model only for explaining conflicts.
- **latency:** Under 1 second for stored hashes/timestamps; under 5 seconds if a live browser or Mac recheck is explicitly requested.
- **cost:** Very low for metadata comparisons; browser rechecks dominate latency and any model spend.
- **security:** Never silently re-fetch authenticated pages or send mail. Treat browser content as untrusted and redact secrets before persistence or speech.
- **missing:** A stable content hash and provenance ID from relay read_web_page; A single durable source policy defining freshness per source rather than activity-based count caps; A true device receipt for downloaded and played audio

### "Is the system actually reachable right now—and which exact surface is missing? Give me a live liveness answer that distinguishes an absent pendant, a stale registry row, an offline Mac bridge, a dead browser session, and a relay that is up but cannot deliver audio."
- **useful because:** Today the owner can see Safari and the Mac bridge online while the pendant is structurally absent; registry caps, missing firmware heartbeats, and stale browser state make a single green/offline label dishonest. This tells them whether to wait, reconnect hardware, or change how they ask.
- **path:** relay-realtime → mac-planner → browser-extension → unified → faculty-perception
- **model tier:** Deterministic probe and freshness classification; use the realtime model only to turn the result into the owner's requested one short sentence.
- **latency:** 1–2 seconds for relay/Mac/browser probes; never block on a pendant timeout longer than its declared heartbeat window.
- **cost:** Near-zero model cost; a few authenticated GETs and bounded metadata joins.
- **security:** Expose only status, last-seen ages, and reason codes. Do not reveal device credentials, browser URLs, or private page content. A stale/absent result must not trigger reconnects or retries without confirmation.
- **missing:** A relay endpoint that reports pendant presence from device-originated heartbeats rather than converse-session assumptions; Firmware heartbeat/registration for the nRF9160 (currently no pendant exists in the registry); Browser heartbeat freshness semantics that distinguish a healthy extension from an idle one; A published, resolver-matching continuity snapshot combining these probes

### "When I say “make this decision-grade,” produce a compact evidence packet for the claim: independently fetch the source in the browser, record the Mac and relay observations, capture the exact timestamps and content hashes, identify disagreements, and give me a confidence verdict I can revisit later."
- **useful because:** Today the assistant can tell the owner a web-derived fact, but cannot turn that fact into a durable, independently checkable record. This would make research, purchases, travel, and technical decisions auditable rather than relying on an ephemeral spoken answer.
- **path:** relay-realtime → browser-extension → mac-planner → mac-vision → unified → faculty-perception → faculty-judgement
- **model tier:** Use deterministic collection, hashing, timestamping, and disagreement checks first; use the expensive realtime model only to explain the verdict in the owner's one-sentence format. Use a cheaper background model to summarize the packet for later review.
- **latency:** 30–90 seconds for two independent reads and packet assembly; speak an immediate progress acknowledgement, then deliver the verdict when complete.
- **cost:** Moderate: browser rendering and extension reads dominate; hashing and storage are cheap. No model call is needed unless sources disagree or the claim requires synthesis.
- **security:** Never capture authenticated page bodies by default; ask before including private tabs, redact secrets locally, and store only the selected claim, bounded excerpts, source URLs, hashes, timestamps, and redaction metadata. Require confirmation before using the packet to send mail, buy, or change anything.
- **missing:** A first-class evidence-packet record that joins relay read, browser inspection, Mac observation, pipeline/job IDs, and the owner's original claim; A relay browser-read contract that emits a stable read ID and hash, plus a bridge into the existing Mac evidence capsule and browser provenance stores; Independent-source policy and disagreement thresholds; one page or one model response must not count as corroboration; A durable owner-visible export route (signed JSON or human-readable report) with revocation and retention controls

### "Let me mark a request as high-stakes, and have the system refuse to act on it until the claim passes an evidence threshold I chose—such as two independent sources, a fresh Mac observation, and an explicit owner confirmation—while explaining exactly which condition failed."
- **useful because:** A browser page, relay answer, or completed Mac job can currently flow into action without a machine-enforced distinction between observed, asserted, and stale information. This gives the owner a real safety boundary for purchases, messages, credentials, and other consequential actions.
- **path:** relay-realtime → faculty-perception → faculty-judgement → faculty-action → browser-extension → mac-planner
- **model tier:** Deterministic policy evaluation and source classification; no expensive model call for the gate. Use a cheaper model only to explain a failed condition in plain language.
- **latency:** Immediate block/allow decision under 200 ms after evidence is available; asynchronous rechecking may take up to 60 seconds.
- **cost:** Low: metadata and policy checks dominate; optional rechecks may invoke browser or Mac surfaces, but no routine realtime-model spend.
- **security:** Policies must default closed for destructive actions and cannot be weakened by a page, tool result, or model-generated instruction. Keep private evidence local, log only reason codes and hashes, and require a fresh spoken confirmation immediately before irreversible execution.
- **missing:** A shared, signed claim-state format understood by perception, judgement, and action; An enforceable action preflight that consumes claim confidence and freshness rather than trusting free-form model text; Owner-configurable evidence policies with versioning and an immutable decision receipt; A source independence model that can detect when two pages are copies of the same source

### "After any task, let me ask “what left my devices?” and receive a redacted data-egress receipt: which surface sent what category of data, to which service, when, under which permission, and what was deliberately withheld."
- **useful because:** The owner currently has no single truthful view of whether a browser page, microphone capture, file, or personal message crossed from the Mac or browser into the relay or model. A privacy receipt makes the system inspectable without requiring them to read logs or trust assurances.
- **path:** relay-realtime → mac-planner → browser-extension → mac-vision → unified → faculty-perception
- **model tier:** Deterministic instrumentation and redaction; use no realtime model for collection. A cheap background model may turn the bounded receipt into a short spoken summary.
- **latency:** Append events synchronously with each transfer and answer from the local ledger in under 1 second; never delay a user action solely to generate prose.
- **cost:** Low CPU/storage overhead for bounded metadata; a few kilobytes per task. Model cost is optional and small.
- **security:** The receipt itself can reveal sensitive destinations, so protect it with the same auth as the underlying data and redact payloads by default. Never log secrets, raw audio, page bodies, tokens, or message content; record classifications, byte counts, hashes, and policy decisions instead.
- **missing:** A common egress-event schema spanning Mac, browser, relay, model, and pendant links; Instrumentation at the actual serialization/send boundaries, not only at route completion; A tamper-evident, bounded local ledger with user-visible export and retention controls; A relay-side receipt acknowledgement so the Mac can distinguish attempted, accepted, and persisted transfer


## Changes it proposed to its own stack

### `relay` — Make every cloud relay browser read return a stable readId and SHA-256 content hash, carry the originating voice/routine/job correlation ID, and report that metadata to the Mac evidenceCapsules/browserProvenance stores when the caller is local. Mount the existing browser provenance routes and mark relay-only reads as uncapsuled until that bridge succeeds.
- **owner gets:** When the assistant quotes a live webpage, the owner can later identify exactly which page version was read and whether it changed, instead of trusting an untraceable sentence that may be retained indefinitely in an announcement.
- effort: Small-to-medium: extend serverBrowser.js, pass correlation metadata through voice and scheduler callers, add one Mac bridge call, and mount an already-written provenance router; add integration tests for hash stability and failure.  ·  risk: A bridge outage must not block reading or speaking. If IDs are exposed in speech or logs they could leak URL structure, so keep them metadata-only and redact authenticated content. Recover by retaining an explicit uncapsuled marker.
- cost: Negligible CPU/storage for hashes and bounded metadata; no extra model calls. Existing capsule limits and byte budgets remain the cap.  ·  latency: Milliseconds for hashing; one asynchronous Mac write when available, with no user-visible wait.
- security: Improves auditability but must hash redacted content, not raw secrets, and must never transmit page bodies from relay to Mac merely to create provenance.
- depends on: A correlation ID contract between relay voice/routine jobs and Mac jobs; A callable Mac endpoint for mintCapsule/recordExtraction or a narrowly scoped new provenance-ingest route; Mounting local-agent browserProvenance routes, currently unmounted


## What it asked for

_Nothing._
## Its own summary

Discovered current live state and recorded three distinct proposals. Fresh probes establish the Mac agent is ready with Accessibility and Screen Recording granted, the relay is reachable with the Mac bridge online, and Safari's browser bridge is online with one tab and zero pending commands. This still does not establish a pendant or playback. The strongest proposed capability is a causal, cross-surface truth report that separates proven, inferred, and unknown legs of a request; additional proposals cover freshness/source-change checks and truthful per-link liveness. I also proposed the missing relay-browser provenance bridge using the existing Mac capsule schema. The granted read_continuity_snapshot tool is not actually resolvable (best match /ops/snapshot scored 0.447), so I used direct /ops/snapshot, /ops/status, and /browser/status instead.

**Biggest unknown:** Whether any physical nRF9160 pendant is attached or has played audio remains unknown/negative by registry evidence: no pendant registration or firmware heartbeat exists. To close that gap I still need a real device-originated heartbeat/playback event path and a resolver-matching authenticated continuity snapshot; for relay web provenance I need a correlation-ID contract plus a Mac provenance-ingest route.

