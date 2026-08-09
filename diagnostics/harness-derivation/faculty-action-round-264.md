# Harness derivation — faculty-action — round 264

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live surfaces round 264** — Mac bridge and Safari browser are online; nrf9160 pendant is offline (last seen 2026-08-09T02:56:31.366Z). Therefore cross-surface capabilities can be exercised on Mac/browser now, but pendant-trigger and physical cancel validation still need the pendant link.
  - evidence: discover(devices) live result in round 264

## Capabilities it proposed

### ""Do this for me" — carry one approved request from my pendant through the right Mac/browser surface, and tell me only when the requested result is independently verified."
- **useful because:** This is the system's defining benefit: the owner can delegate a real-world task while wearing the pendant instead of manually coordinating relay, Mac, browser, and approval. It prevents the dangerous current failure mode where an executor receipt is mistaken for success.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Realtime only for clarifying the request and speaking the result; background/local agents perform the plan, execution, and verification.
- **latency:** Preflight under 2 seconds; ordinary tasks 5–30 seconds; long tasks become a relay job with pendant progress beacons and no repeated model turns.
- **cost:** About $0.01–$0.08 per task depending on planning/clarification; most execution and verification are local route calls, not model tokens.
- **security:** Never send page contents or secrets to the pendant. Risk-classify the plan, require the existing physical transaction approval latch for consequential actions, bind approval to a hash and expiry, and refuse commit on stale browser/session state. Report verified, failed, or unknown—not success from an executor receipt.
- **missing:** A first-class orchestrator that binds plan ID, action/attempt IDs, approval nonce, executor receipts, and verifier provenance into one commit record.; A policy-data editor for the owner's per-action-class approve/stage choices.

### "When I press the bookmark button, save a private, replayable moment that joins what I just said, the active Safari page, and the Mac's visible app context; later let me ask "what was that?" and jump back to the exact source."
- **useful because:** A physical bookmark is currently a detached event. Joining wearable speech with the browser session and host context turns fleeting thoughts and discoveries into something recoverable without requiring the owner to remember an exact URL or phrase.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Cheap background model for transcription, redaction, and compact indexing; realtime model only when the owner asks a follow-up question.
- **latency:** Acknowledge the press locally in under 100 ms; capture metadata in under 2 seconds; searchable capsule within 10 seconds. Never block recording on Mac/browser availability.
- **cost:** Roughly $0.005–$0.03 per bookmark, dominated by transcription and optional summarization; URL/app metadata and hashes are local and nearly free.
- **security:** Capture only the active tab URL/title and explicitly permitted host metadata, not arbitrary page content. Mark capsules private by default, encrypt audio/transcript at rest, redact secrets and form fields, and show a pendant status when browser context was unavailable. Retention must be bounded and deletion must remove audio, transcript, and index together.
- **missing:** A cross-surface moment-capsule schema with monotonic event ID, audio range/checksum, browser session ID, URL/title hash, host-context timestamp, and independent availability flags.; A query route that resolves a natural-language follow-up to capsules and can reopen the recorded browser session without replaying an action.

### ""Stop that now" — cancel the currently running Mac/browser job from my pendant, even if the voice link is degraded, and report whether it stopped before making any further changes."
- **useful because:** A delegated action can outlive the conversation or behave unexpectedly. The pendant is the one surface physically with the owner; an immediate stop path is a practical safety control, especially for browser navigation, repeated sends, or long-running jobs.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** No model for the emergency signal; firmware emits a signed cancel token and the relay routes it deterministically. A cheap background model may summarize the resulting state afterward.
- **latency:** Pendant acknowledgement under 100 ms; relay dispatch under 500 ms; Mac/browser cancellation attempted within 1 second. If cancellation races with a commit, expose unknown and require fresh verification rather than claiming stopped.
- **cost:** Negligible model cost; one compact relay event and one local cancellation/verification cycle per invocation.
- **security:** The cancel token must be scoped to the active operation, monotonic and replay-resistant, and must not authorize any new action. Cancellation is best-effort and cannot undo already committed external effects; the owner must see cancelled, stopped-after-step, or unknown. Keep secrets and page contents off the pendant. The physical gesture should be distinct from ordinary bookmark/record presses (future second button or encoder chord).
- **missing:** A relay-wide active-operation registry with cancellation propagation and deadlines.; Cancellation handlers in browser and Mac executors that stop queued and in-flight work and emit a final receipt.; Firmware mapping for a distinct emergency gesture, ideally the planned second button or rotary-encoder press.

### ""This needs another pair of eyes" — for a high-risk action, send a redacted approval request to a trusted person, let them approve or reject from their own device, and execute only when both my pendant gesture and their decision are present."
- **useful because:** Some actions are too consequential for one-person confirmation: sending a legal message, publishing publicly, moving money, or deleting shared material. This gives the owner a practical second-check without exposing browser passwords or the full private page.
- **path:** pendant → relay → mac-planner → browser → dashboard → iOS
- **model tier:** Cheap background model for redaction and concise summaries; no realtime model is needed unless the owner asks questions.
- **latency:** Create the redacted request in under 3 seconds; wait asynchronously for the trusted person's decision; expire requests at an owner-selected deadline.
- **cost:** Usually under $0.02 per request for summarization and notification; delivery and storage dominate, not inference.
- **security:** The second party receives only a canonical human-readable summary and risk metadata, never secrets, credentials, raw page contents, or audio. Bind both decisions to the same operation hash, enforce expiry and one-time use, log identity and provenance, and make rejection terminal. The owner must explicitly configure trusted contacts and action classes.
- **missing:** A relay-held multi-party approval protocol and identity/authentication for trusted contacts.; A redaction verifier that proves the approval summary covers the exact operation hash.; Owner-facing configuration for contact, quorum, expiry, and action-risk policy.

### ""Why did you do that, and what exactly did you see?" — give me a plain-language, replayable explanation of a completed or refused action, with the source facts, decisions, approvals, and verification evidence separated from the model's interpretation."
- **useful because:** Receipts tell machinery that something ran, but the owner needs to audit the mind: which observation led to the plan, what was withheld, who approved it, and why the result was classified as verified, failed, or unknown. This makes mistakes debuggable and trust recoverable.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Background model generates the explanation from structured provenance; realtime model only answers a follow-up question. Hashes and evidence selection are deterministic.
- **latency:** A compact pendant summary within 2 seconds; detailed audit view within 5 seconds; historical explanations remain available asynchronously.
- **cost:** About $0.005–$0.04 per explanation, depending on evidence volume; structured event storage is the main non-model cost.
- **security:** Separate immutable raw provenance from generated prose. Redact secrets and private page content, expose evidence at sensitivity levels, preserve hashes and timestamps, and clearly label inference versus observed fact. Never allow the explanation generator to alter the audit record.
- **missing:** A tamper-evident cross-surface provenance graph linking observations, plan revisions, approvals, action attempts, verifier results, and user-visible outcomes.; A redaction/evidence projection service with sensitivity-aware owner views.; A stable audit identifier that can be spoken and retrieved from the pendant.

### ""Keep this task private to my devices" or "you may use the relay" — choose where each piece of my request, audio, page data, and result is allowed to travel, enforce that boundary during planning and execution, and refuse a plan that would violate it."
- **useful because:** The owner should control not only whether an action happens, but where personal data goes. A local-only request must not silently fall back to cloud processing when the Mac or browser is unavailable, while a relay-allowed request can remain useful remotely.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Small policy classifier or deterministic rules for routing; use the expensive model only for ambiguous natural-language policy interpretation.
- **latency:** Policy decision under 100 ms before any content leaves a surface; refusal or confirmation must happen before planning sends data elsewhere.
- **cost:** Negligible inference cost for explicit policies; occasional clarification costs under $0.01.
- **security:** Default to the most restrictive interpretation. Attach a residency label to every artifact and operation, enforce it at relay, Mac, browser, and storage boundaries, and make fallback impossible without a new owner confirmation. Do not claim local-only if telemetry, logs, or backups violate the boundary.
- **missing:** A data-flow policy engine understood by every executor and storage path.; Artifact-level residency labels and enforcement at pipeline, browser, journal, and model boundaries.; Owner controls for named policies such as device-only, relay-allowed, browser-session-only, and delete-after-result.


## Changes it proposed to its own stack

### `firmware` — Add a signed emergency-cancel channel to the pendant protocol and firmware: a distinct future second-button/rotary gesture emits only an operation-scoped cancel token, queues it crash-safely while offline, and renders cancellation dispatch/result using the existing tactile outcome beacon. Do not overload sw0 recording or sw1 bookmarking on today's bench firmware.
- **owner gets:** The owner gets a physical panic stop for delegated actions without hunting for the Mac or reopening the voice conversation. It makes delegation trustworthy because stopping is always available at the hand.
- effort: Medium: protocol envelope, relay routing, Mac/browser cancellation hooks, and firmware input integration; test races against commit and link loss. Requires the planned extra button or rotary encoder for a safe distinct gesture.  ·  risk: A cancel may race after an irreversible external commit; surface unknown rather than pretending success. Replay and stale tokens must be rejected. Existing recording/bookmark behavior remains unchanged; recover by ignoring malformed tokens and using normal job cancellation.
- cost: Negligible API cost; firmware flash/build work only. Existing hardware can support the protocol, but a product-grade distinct input needs the owner's planned rotary encoder/second button (low single-digit component cost).  ·  latency: Local haptic acknowledgement under 100 ms; relay dispatch target under 500 ms; cancellation result depends on Mac/browser round trip.
- security: Reduces action risk. Cancel tokens are scoped, signed, monotonic, expiring, and contain no page content or secrets.
- depends on: relay active-operation registry; Mac/browser cancellation handlers; physical transaction approval latch semantics; planned rotary encoder or second button

### `context` — Introduce a first-class, machine-enforced data-residency label on every audio, transcript, browser observation, plan, receipt, and journal artifact. Labels such as device_only, mac_only, browser_session_only, relay_allowed, and delete_after_result must be checked before routing, persistence, model invocation, and fallback; an unlabeled artifact defaults to the strictest policy and a violation becomes a refusal, not a warning.
- **owner gets:** The owner can say where private information is allowed to go and trust that an unavailable device will not silently cause cloud or relay disclosure. Privacy becomes an enforceable choice rather than a promise in a model response.
- effort: High integration effort across relay, pipeline, Mac executor, browser bridge, storage, and model-routing; requires migration of existing journal and audio metadata.  ·  risk: Overly strict labels may cause a task to refuse unexpectedly; show the blocked hop and offer an explicit policy change. Old unlabeled records must be treated conservatively and never retroactively exposed.
- cost: Low runtime cost; moderate engineering and storage-metadata migration cost. Explicit local-only routing may increase local compute usage.  ·  latency: Sub-millisecond policy checks when labels are present; refusals can be immediate. Local-only tasks may be slower than relay-backed inference.
- security: Substantially reduces accidental data exfiltration and makes fallback behavior auditable. Labels are not encryption, so transport and storage encryption remain required.
- depends on: cross-surface provenance graph; owner-configurable policy store; artifact metadata migration; executor enforcement hooks


## What it asked for

_Nothing._
