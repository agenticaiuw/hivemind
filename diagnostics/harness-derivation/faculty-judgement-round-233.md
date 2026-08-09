# Harness derivation — faculty-judgement — round 233

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Give me a morning brief that I can trust: tell me what you checked, deliver it once, and if I didn't hear it, recover it later without repeating everything.”"
- **useful because:** The current system can mark a routine/job completed while the calendar read was unauthorized, audio was never played, or two daily routines both spoke. This is the single most useful capability: it turns a briefing from generated text into a closed-loop promise with honest uncertainty and one recovery path.
- **path:** relay → mac → pendant → dashboard
- **model tier:** Background model assembles and ranks the brief; realtime model only handles the owner's interruption or replay request. Deterministic policy and delivery state decide whether to speak, queue, or recover.
- **latency:** Generate in under 60s at routine time; delivery acknowledgement within 5s; recovery appears on next reconnect without another expensive generation.
- **cost:** About $0.01–$0.05 per brief depending on mail/research context; most cost is source reading and synthesis, not ACK reconciliation.
- **security:** Never say 'nothing waiting' when EventKit is unreadable; include source freshness and permission provenance. Dedupe by a briefing fingerprint, keep full mail/calendar text on the Mac, send only the selected redacted speech, and require owner confirmation before any resulting mutation.
- **missing:** A durable briefing-run record joining routine ID, source-read verdicts, artifact ID, and owner-visible delivery state; A scheduler-side dedupe/lease for the two existing 07:00 routines; A relay endpoint that consumes pendant delivery ACKs and requeues an interrupted item exactly once; An owner-configurable delivery policy (speak now, queue, retry, suppress) rather than the placeholder default

### "“Forget everything you learned about [topic/person/source], and prove it won't be used again.”"
- **useful because:** Today deletion is store-local: a capture can survive in context_graph.json, a browser-derived fact has no capsule link, and evidence revocation does not reach facts or relay memory. A life assistant must be able to honor a correction or erasure as a single promise, not leave hidden copies that silently influence later judgement.
- **path:** dashboard → relay → mac → browser → pendant
- **model tier:** Deterministic index/provenance traversal performs the deletion and produces a receipt; use the expensive model only to resolve ambiguous natural-language scope and summarize residual uncertainty.
- **latency:** Scope preview under 3s; deletion under 10s locally and under 30s across relay/browser; spoken confirmation one sentence, with a detailed dashboard receipt.
- **cost:** Near-zero model cost for exact IDs; $0.01–$0.03 only when resolving an ambiguous topic or entity.
- **security:** Fail closed on ambiguous scope. Never put erased content in the confirmation or logs. Require explicit confirmation for broad or third-party erasure; retain only salted tombstone IDs, deletion time, and affected-store counts. A failed relay purge must remain visible and must block claims of completion.
- **missing:** A cross-store provenance index linking facts, context-graph entities, capsules, browser extractions, fleet events, jobs, and audio artifacts; A dry-run and commit erasure operation with cryptographic receipt and retry semantics; Relay/fleet tombstone propagation and a prompt-projection check that refuses revoked IDs; A browser extension command to delete or invalidate its local provenance/cache records

### "“Notice when I keep correcting or ignoring the same kind of help, then ask me once whether to change the rule—don't silently learn a habit.”"
- **useful because:** A useful assistant should get less annoying over time without turning repeated silence into consent. The system already has interruptions, routine outcomes, spoken delivery ACKs, and policy evaluation, but no layer that distinguishes a one-off miss from a stable owner preference and offers a reviewable policy change.
- **path:** pendant → relay → mac → dashboard → browser
- **model tier:** Cheap background statistics detect repeated patterns; the realtime model is used only when the owner answers the proposed change. Deterministic autonomy_policy_evaluate enforces the old policy until explicit acceptance.
- **latency:** Update candidate after 3–7 relevant events or one explicit correction; no extra latency in the live turn; dashboard proposal appears within a minute of the last event.
- **cost:** Usually under $0.01 per candidate using local counters; one realtime turn only when the owner reviews it.
- **security:** Silence, missed playback, and link failure are not negative preference evidence. Keep candidates local and redact summaries; never infer sensitive preferences from health, relationships, or private content without explicit opt-in. Every accepted change needs versioning, expiry/review date, and an undo path.
- **missing:** A durable event-to-policy candidate store with evidence references and confidence; A classifier separating owner correction, explicit approval, deferral, non-delivery, and mere absence; A dashboard/pendant review interaction that presents one proposed rule and accepts/rejects it physically or explicitly; Policy version propagation to relay, Mac, browser, and pendant with rollback

### "“When I use a new Mac or browser, let the pendant pair it as my device, show me exactly what that host can do, and revoke an old host from the pendant.”"
- **useful because:** The owner currently has several execution surfaces but no portable, owner-verifiable trust boundary. A stolen or stale Mac/browser session can remain useful until someone notices. The pendant should be the physical root of trust that makes host access understandable and revocable, without exposing secrets through voice.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Deterministic pairing, capability intersection, expiry, and revocation; no expensive model needed except to explain a host's permissions in the owner's one-sentence style.
- **latency:** Pairing in under 10 seconds; revocation takes effect on the next command and is reflected on all surfaces within 30 seconds.
- **cost:** Negligible API cost; cryptographic storage and relay fan-out dominate engineering, not inference.
- **security:** The pendant must never read or speak browser credentials. Pairing requires a deliberate physical action and displays only host identity, scope, and expiry. Fail closed when the relay cannot confirm revocation; retain an append-only audit of pair/revoke events with no page content.
- **missing:** A device identity and key lifecycle distinct from bearer sessions; A signed host-attestation and capability-scope exchange over LTE/relay and the current USB bench path; Relay-enforced revocation epochs checked before Mac/browser execution; A pendant-visible host list and recovery path after loss of the pendant


## Changes it proposed to its own stack

### `hardware` — Add a small secure element with a protected device key, monotonic counter, and tamper-evident pairing state to the pendant; use it to sign physical approvals, host-pairing changes, privacy-latch transitions, and delivery receipts. Keep content and transcripts out of the secure element.
- **owner gets:** The owner can know that an approval or revocation really came from the device in their hand, even if a Mac session, browser extension, or relay credential is stale or compromised. This makes the pendant a trustworthy personal key rather than merely a microphone and speaker.
- effort: Moderate hardware revision and firmware/relay protocol work; requires key provisioning, recovery design, and migration from current software-only signing.  ·  risk: Lost or damaged pendant could strand the owner's trust boundary; provide a second-device or in-person recovery ceremony, never a voice-only bypass. Counter wear and provisioning mistakes require manufacturing tests and a rollback-safe epoch scheme.
- cost: Roughly $1–$4 BOM increase and negligible steady-state power; engineering and secure provisioning are the substantial costs.  ·  latency: A few milliseconds per signature; no noticeable conversational delay if signatures are attached to existing envelopes.
- security: Strongly improves non-repudiation and revocation. It does not protect content after a legitimate host is authorized, so least-privilege scopes and relay-side expiry remain required.
- depends on: A durable device identity and host-pairing protocol; physical_transaction_approval_latch semantics; relay-side revocation epochs; A recovery ceremony that does not rely on the same Mac session being revoked


## What it asked for

_Nothing._
