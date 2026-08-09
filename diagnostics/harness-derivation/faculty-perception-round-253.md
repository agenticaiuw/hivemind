# Harness derivation — faculty-perception — round 253

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live system state 2026-08-09** — The Mac agent is fully ready: Accessibility and Screen Recording are granted, all required permissions are present, browser extension and relay are online, and the relay is D1-backed. The relay registry now contains nrf9160-pendant but marks it offline; it was last seen at 2026-08-09T02:56:31.366Z. Therefore cloud/Mac/browser work is live, but pendant delivery is not currently available.
  - evidence: read_continuity_snapshot(include=['relay','pipeline'], since='2026-08-09T03:00:00Z') returned HTTP 200 with status.permissions.ready=true, browser.online=true, relay.reachable=true/store=d1, and devices discovery showed nrf9160-pendant offline last seen 2026-08-09T02:56:31.366Z.

## Capabilities it proposed

### "“Can you reach me right now, and if not, get this to me another way?”"
- **useful because:** The system should answer with a truthful current reachability verdict instead of treating a completed relay job as heard: today the Mac, relay, and browser are live while the registered nrf9160 pendant is offline. It can route a short result to the best live surface, or explicitly queue it for the pendant without claiming delivery.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime only for the spoken question; a cheap background classifier can map the snapshot to reachable/unreachable and choose fallback.
- **latency:** Under 2 seconds for the verdict; fallback routing may take 2–10 seconds.
- **cost:** Low: one small classification call plus existing snapshot and route calls; no browser model call unless browser fallback is selected.
- **security:** Read-only health metadata may be spoken. Never expose device tokens or page contents. Sending a fallback notification should require the owner's existing notification policy, and destructive actions still require confirmation.
- **missing:** A single policy engine that consumes the live device registry, Mac permissions, browser presence, and delivery acknowledgements; A pendant-aware queue state that distinguishes queued-for-offline from delivered; A Mac/browser fallback notification action with receipt joined to the same request ID

### "“What changed on the page I was looking at, and show me exactly what you’re basing that on?”"
- **useful because:** A later answer about a logged-in browser page should be change-aware and auditable: compare a fresh browser observation with the prior content hash, cite the URL/tab/region, and say when no prior observation exists. This joins the browser session nobody else can reach to the Mac evidence store instead of giving an uncited summary.
- **path:** browser → mac-bridge → relay → dashboard → pendant
- **model tier:** Cheap background text model for diff extraction; realtime only when the owner asks aloud. Deterministic hashing and redaction run locally without a model.
- **latency:** 2–5 seconds for snapshot and hash; 5–15 seconds for a concise semantic diff.
- **cost:** Low to moderate: browser snapshot plus local SHA-256/diff; one small model call only for semantic summarization.
- **security:** Keep authenticated page bodies on the Mac; send only redacted diff and provenance to relay/pendant. Respect the browser's existing read permission. Never speak secrets detected by the evidence redactor.
- **missing:** A live call site that records browser_snapshot output into the already-built evidenceCapsules and browserProvenance stores; A stable relay correlation ID/content hash for relay-originated browser reads; A dashboard diff view that displays capsule revocation/expiry rather than retaining page text indefinitely

### "“Before you tell me this again, prove whether I already heard it.”"
- **useful because:** The system currently has 'said', 'bytes written to a socket', Mac completion, and actual playback as different facts. A repeat-prevention gate would only suppress or replay an item when the device playback ledger proves the artifact was heard; otherwise it would say 'not confirmed' and offer a controlled retry, preventing both annoying duplicates and dangerous silent loss.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** No expensive model for the gate: deterministic event and artifact-ID matching. Use a small background model only to compress an unresolved-items digest; realtime can phrase the final spoken answer.
- **latency:** Under 300 ms for a gate decision; retry/replay is asynchronous with status updates.
- **cost:** Very low: local/relay state joins dominate; model cost only for optional digest wording.
- **security:** A playback proof must be device-originated and bound to an opaque artifact ID, sequence, and checksum; admin HTTP acknowledgements must never count as hearing. Replays of sensitive content require the owner's normal confirmation policy.
- **missing:** Firmware emission and relay ingestion of the already-granted audio_delivery_ack_queue events; A shared artifact identity propagated through TTS, announcement, job, Mac receipt, and browser provenance; A deterministic repeat gate wired before announcement and catch-up generation

### "“Tell me immediately if the trust boundary of my AI changed — a new device, permission, relay, browser session, firmware, or account path — and show me exactly what changed.”"
- **useful because:** The owner cannot currently tell whether an answer came through the same trusted chain as yesterday. A signed baseline across the pendant, Mac agent, browser extension, and relay would detect silent substitution, unexpected pairing, permission changes, firmware drift, or a changed relay endpoint before the system acts on private context.
- **path:** pendant → mac-bridge → browser → relay → dashboard
- **model tier:** Deterministic hashing and signature verification; use a small background model only to explain a diff in plain language. Realtime is unnecessary unless the owner asks aloud.
- **latency:** Continuous low-rate checks; alert within 30 seconds of a detected boundary change.
- **cost:** Low ongoing cost: hashes, signatures, and registry reads. Occasional small model call for an explanation.
- **security:** The baseline and signing keys must be protected from the same relay being measured. Alerts must avoid revealing private page or memory contents. Enrollment and baseline changes require explicit owner confirmation.
- **missing:** Hardware-backed identity or securely stored signing key on each node; A signed attestation record covering pendant firmware/build, Mac binary identity and permissions, browser extension identity/session, relay URL/configuration, and device pairing; A persistent owner-approved baseline with an append-only change history and a fail-closed policy for high-risk changes

### "“Prove that this private task stayed private: what data left each device, where did it go, and what was discarded?”"
- **useful because:** Today the system can perform a browser, Mac, relay, and pendant workflow but cannot give the owner an end-to-end data-egress account. A per-task privacy receipt would list captured fields, redactions, destinations, retention deadlines, and deletion confirmations, making sensitive automation auditable rather than trust-based.
- **path:** browser → mac-bridge → relay → pendant → dashboard
- **model tier:** Deterministic event/egress accounting and redaction checks; no realtime model required. A cheap background model may summarize the receipt for the owner.
- **latency:** Receipt assembled within 1–3 seconds after task completion; deletion verification may be asynchronous.
- **cost:** Low to moderate storage and hashing overhead; negligible model cost unless a natural-language summary is requested.
- **security:** The receipt itself can reveal sensitive metadata. Keep raw content local, encrypt receipts, redact URLs/claims where necessary, and require confirmation before exporting a receipt off-device.
- **missing:** A task-scoped correlation ID propagated through browser commands, Mac actions, relay calls, audio, and pendant events; Egress interceptors at each boundary that record destination, byte class, redaction result, and retention/deletion outcome; A verifiable deletion protocol rather than merely recording that a delete request was issued

### "“When something goes wrong, give me a replayable account of the exact state each body saw — not just a final success or failure.”"
- **useful because:** A failed multi-surface task is currently difficult to distinguish from a task that merely stopped reporting. The owner should receive a causal replay showing the pendant's monotonic frame and audio quality, relay receipt, Mac action pre/post-state, browser tab/session state, and permission changes in one ordered timeline, with explicit gaps instead of invented continuity.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic event ordering, clock-offset estimation, and gap detection; a small background model can produce a concise explanation. Realtime is not needed.
- **latency:** Live partial status in under 2 seconds; complete replay within 10 seconds after reconnection or task end.
- **cost:** Moderate bounded event storage and upload traffic; low model cost for optional summarization.
- **security:** Replay logs may contain page titles, commands, audio metrics, and private state. Encrypt them, minimize payloads, redact content, and enforce short retention with owner-controlled export.
- **missing:** A shared event envelope with monotonic sequence, wall-clock estimate, source identity, causation ID, and integrity hash; Clock/offset exchange between pendant, Mac, browser, and relay; A durable gap marker and replay reader that refuses to infer events across missing intervals


## What it asked for

_Nothing._
