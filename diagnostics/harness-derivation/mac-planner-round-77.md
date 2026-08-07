# Harness derivation — mac-planner — round 77

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Handle this private account task, but keep the page contents and anything I type on my Mac. Tell me only what you need me to know and ask before the final change.”"
- **useful because:** Today, coordinating the pendant, relay, Mac, and authenticated browser generally requires sensitive page text and form data to cross the server boundary. The owner should be able to use the system for banking, health, employment, and personal-account tasks without choosing between convenience and exposing private content. The Mac/browser can retain raw evidence locally while the pendant receives only a minimized status, redacted summary, and final diff.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the realtime model only for the spoken request, status questions, and final concise explanation. Run page understanding and field matching locally on the Mac/browser harness with a cheaper background model; the relay should coordinate typed intents and redacted events, not inspect page bodies.
- **latency:** Initial mode negotiation under 500 ms; local page analysis typically 1–3 seconds per step; spoken status updates can arrive immediately from local events. Final review should wait for a complete local before/after diff, not a fixed timeout.
- **cost:** Low relay/model cost: roughly one short realtime turn plus local inference per step. The dominant cost is Mac-side model execution and optional encrypted local evidence storage, not API tokens.
- **security:** Raw DOM, screenshots, clipboard contents, credentials, and typed secrets must remain on the Mac/browser. Relay events use opaque workflow and action IDs, capability labels, coarse progress, and redacted field names. Encrypt local evidence, expire it by default, prevent accidental body inclusion in logs, and require explicit owner confirmation delivered through the pendant for the final irreversible change. If local privacy mode cannot prove it is active, fail closed rather than silently falling back to cloud processing.
- **missing:** A first-class privacy-mode execution contract spanning relay, Mac executor, and browser bridge; A local planner/extractor that returns typed facts and redacted diffs instead of page bodies; Redaction and data-loss tests for receipts, thinking traces, browser results, and dashboard views; Pendant-visible mode state and a fail-closed handshake proving that sensitive steps stayed local; A confirmation protocol that lets the owner approve a locally prepared final diff without uploading the underlying content


## Changes it proposed to its own stack

### `integration` — Add a resumable action ledger shared by relay, Mac executor, and Safari browser bridge. Before dispatch, assign a durable workflowId and deterministic actionId per semantic step; persist step intent, backend, precondition fingerprint, attempt, status, and receipt. Commit the completion record atomically with the receipt. On link loss, restart, or extension sleep, the relay asks for the ledger and resumes at the first incomplete step; completed actionIds are skipped only when their postcondition/evidence still matches, otherwise the step is marked needs-reconciliation. For non-idempotent mutations, add an operation key passed to the bridge/Mac side and retain it until the workflow is terminal. Expose pause/resume/reconcile and a pendant-friendly progress event, not a blind whole-plan retry.
- **owner gets:** If the Mac sleeps, Safari disconnects, or the pendant link drops halfway through 'collect these details, fill the form, save the file, and draft the reply,' the owner gets a truthful continuation instead of duplicate clicks, duplicate drafts, or uncertainty about what happened. They can leave a long task running and hear exactly which step completed and which needs attention.
- effort: Medium-high: a D1/R2 ledger and state machine in the relay, Mac job-store integration, browser bridge acknowledgement/postcondition protocol, recovery tests for crashes between side effect and receipt, and progress fan-out to pendant/dashboard.  ·  risk: The hard failure window is a side effect occurring before its completion record is committed; recovery must classify that step as unknown and inspect evidence rather than replay it. Stale fingerprints could incorrectly skip a step, so unknown or changed postconditions stop at reconciliation. Existing one-shot jobs remain compatible and can be imported as non-resumable terminal runs.
- cost: Small persistent storage and a few relay writes per step; negligible model cost because recovery is deterministic. Additional browser polling/heartbeat traffic is minor.  ·  latency: One ledger write and acknowledgement per step adds roughly tens of milliseconds locally and one network round trip for remote browser steps; retries become much faster and safer than restarting a long plan.
- security: Ledger contains URLs, touched paths, and action metadata, so encrypt sensitive fields, minimize retention, and bind records to the owner/session. Never persist form secrets or page bodies; operation keys should be opaque.
- depends on: chg-5fc73ce3 receipt infrastructure (implemented but currently lacks checkpoints/preconditions); chg-16bc5dee durable browser job runner (router exists; runner and result stream remain missing); chg-14accc01 browser request IDs/idempotency and tab affinity (partially implemented)


## What it asked for

_Nothing._
