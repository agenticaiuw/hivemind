# Harness derivation — unified — round 264

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When something was saved offline, tell me exactly what was retained, why, and when it was deleted after delivery."
- **useful because:** Offline storage is intentionally failure-only, but the owner currently cannot distinguish an audio copy held for failed delivery from ordinary retained data. A precise disclosure makes the failure path trustworthy without changing its retention rule.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** deterministic/background; no expensive realtime model needed
- **latency:** Show current spool state in under 2 seconds; emit a compact spoken notice at the next natural conversation boundary, never an unsolicited interruption.
- **cost:** Very low: metadata reads and signed receipts; no additional audio processing.
- **security:** Expose hashes, type, size, creation time, delivery state, and deletion receipt—not raw audio by default. Do not add routine SD writes. A failed or unverifiable deletion must remain visibly pending rather than being reported as complete.
- **missing:** A typed owner-facing view over pendant_store OUTBOX metadata; A relay acknowledgement that includes deletion confirmation, not just upload acceptance; A compact notification path integrated with the existing inbox and audio-delivery receipt queue; A policy field for whether the owner wants spoken notices or dashboard-only notices

### "If the pendant, relay, Mac, or browser is failing, give me one plain-language diagnosis, the safest next repair, and proof that it worked."
- **useful because:** The system has separate health, job, browser, and audio observations, but the owner should not have to interpret four partial statuses or retry blindly. A correlated diagnosis with a dry-run repair plan is the most useful cross-surface behavior this system could provide.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background planner for hypotheses and repair ordering; deterministic checks first; realtime only if asked during a live call
- **latency:** Initial snapshot under 3 seconds; repair confirmation under 15 seconds; never block an active audio turn.
- **cost:** Low-to-moderate: deterministic health probes dominate; model cost only for translating evidence into a concise explanation.
- **security:** Repairs must be least-privilege, idempotent, and separately confirmed when they change state. Never claim pendant recovery while it is offline. Include evidence timestamps and distinguish observed failure from hypothesis.
- **missing:** A single owner-facing route that joins incident_diagnostics, fleet_health_and_repair, audio pipeline validation, and browser status; A repair receipt correlated to the diagnosis ID; A pendant-specific offline/last-seen explanation and reconnect instruction; A policy deciding which repairs may auto-run versus require approval

### "Before you act, tell me what personal data will leave the pendant, Mac, browser, and relay, and give me a receipt of what actually left."
- **useful because:** The owner can approve an action, but approval does not currently provide a plain-language data-flow boundary. This lets him distinguish a local Mac action from one that sends page contents, audio, credentials, or extracted context off-machine.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic policy analysis first; background model only to summarize unfamiliar payloads
- **latency:** Preview under 2 seconds; post-action receipt within 5 seconds; never delay a local emergency stop.
- **cost:** Low: manifests, hashes, and route metadata dominate; model summarization is optional and cheap.
- **security:** Never include secrets in the preview or receipt. Classify at field level (audio, page text, credentials, identifiers, metadata), preserve immutable hashes, and report unknown fields as unknown rather than safe. This is transparency, not authorization; existing physical approval remains required where applicable.
- **missing:** A shared data-classification manifest for pendant, relay, Mac, and browser payloads; Preflight interception that records intended egress without logging secret values; A post-action egress receipt correlated to the action ledger and job receipt; Owner-configurable rules for categories that may never leave the Mac

### "Make this conversation off-record now, without muting me: do not transcribe it, remember it, send it to the Mac or browser, or use it to trigger actions, and prove when the boundary is active."
- **useful because:** The existing local privacy latch stops capture and playback, which is appropriate for physical privacy but unusable when the owner still wants to speak. The owner needs a semantic conversation boundary that preserves live dialogue while preventing retention, extraction, and cross-surface action.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic enforcement; realtime conversation may continue without transcript persistence
- **latency:** Boundary acknowledgement within one audio turn; enforcement must begin before the next utterance is accepted.
- **cost:** Low runtime cost; bounded in-memory buffering only, with no durable transcript or context-graph writes.
- **security:** Fail closed if boundary state cannot be confirmed. Block browser/Mac commands and context extraction, not merely storage. The receipt must disclose any audio already sent before activation; no claim of retroactive erasure. Require a physical or otherwise owner-authorized trigger.
- **missing:** A relay-wide no-retention/no-action session mode; A pre-transcription gate before speech-to-text; Propagation of the mode to Mac and browser command executors; An authenticated convergence receipt covering capture, relay persistence, context graph, jobs, and browser exposure

### "Tell me when the Mac, browser, relay, and pendant disagree about the same thing, show both claims and their evidence, and ask me which one to trust before changing anything."
- **useful because:** A distributed personal assistant can silently act on stale state: a browser tab may show one status while the relay job and Mac receipt say another. The owner needs conflict visibility and an explicit resolution rather than a fabricated unified answer.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic evidence comparison; background model only to explain the conflict in plain language
- **latency:** Detect on read within 3 seconds; never mutate state automatically; resolution should be resumable later.
- **cost:** Low-to-moderate: correlated reads and hashes dominate; model explanation is optional.
- **security:** Preserve source timestamps and provenance. Treat missing evidence as unknown, not disagreement. A resolution must be recorded as an owner choice and must not rewrite historical receipts.
- **missing:** A typed cross-surface claim schema with freshness and authority metadata; Correlation of browser results, Mac receipts, relay jobs, and pendant events by intent ID; An owner-resolution record that can be consumed by later plans; A dashboard and voice presentation for side-by-side claims

### "Accept commands only when they are spoken by me, and tell me when voice identity is uncertain before doing anything consequential."
- **useful because:** The current bearer-token and browser/session mechanisms authenticate software surfaces, not the person wearing the pendant. A stolen open session or another speaker near the device could still turn a conversational request into an external action.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** small local/on-device speaker-verification model for gating; expensive realtime model only after identity passes
- **latency:** Under 300 ms for routine utterance classification; uncertain identity must fail closed before planning or dispatch.
- **cost:** Moderate one-time enrollment and low per-turn inference; hardware/firmware DSP and secure model storage dominate.
- **security:** Voice is not a sole authenticator: require physical approval for high-risk actions, rate-limit failures, avoid uploading raw enrollment audio, and provide a local fallback/revocation ceremony. Never expose a confidence score as certainty.
- **missing:** An enrollment and revocation flow bound to the pendant identity; A local feature extractor and protected verifier or secure element; A relay policy that converts uncertain identity into observe-only mode; A clear owner-facing recovery path when the owner is hoarse, masked, or in noise


## What it asked for

_Nothing._
