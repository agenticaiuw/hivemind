# Harness derivation — relay-realtime — round 219

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Use what’s open in my browser and on my Mac to finish this, and tell me exactly what changed.” The pendant should carry one request across authenticated Safari and local Mac apps, preserve the evidence that justified each step, and speak a concise outcome with links or app names."
- **useful because:** Today the owner must manually bridge the wearable, browser session, and Mac agent, and cannot reliably tell whether a result came from the page, a local file, or an inference. This would make the hive act as one trustworthy computer while the owner is away from the desk.
- **path:** pendant → relay → browser → mac-planner → mac-vision → dashboard
- **model tier:** Realtime relay for intent extraction and one-sentence dialogue; mac-planner for action planning; mac-vision only when visual state is required; a cheap background summarizer for the evidence receipt.
- **latency:** Acknowledge in under 500 ms; first useful result within 10 s; long work continues asynchronously and emits a short pendant alert.
- **cost:** Roughly $0.02–$0.10 per invocation depending on screenshots and browser page extraction; browser/Mac round trips dominate, not the relay utterance.
- **security:** Authenticated page contents and local-screen evidence leave their original devices for orchestration and may reach the model. Store only a compact, redacted receipt; never persist raw screenshots or page text by default. The owner’s existing maximum-access policy applies, but the spoken result must distinguish observed facts from inferred ones.
- **missing:** A cross-surface transaction record tying every action to its source evidence and final artifact; A Mac/browser handoff that can return citations and app/file identifiers to the relay; A receipt renderer that can speak observed-versus-inferred outcomes without dumping sensitive content

### "“I changed my mind—stop that and do this instead,” even after a long Mac or browser task has started. The pendant should interrupt the active transaction, safely supersede pending actions, and continue from the latest verified state rather than starting over or blindly completing the old request."
- **useful because:** A wearable conversation is especially vulnerable to stale commands: the owner may notice an error while walking away from the Mac. Today status and completion can be reported, but there is no owner-facing way to cancel or revise an in-flight multi-step goal with confidence about what already happened.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime relay handles the interruption and clarifying delta; a cheaper planner computes a compensating or superseding plan from the transaction journal; vision is used only to re-verify UI state.
- **latency:** Stop request acknowledged in under 700 ms; downstream cancellation or safe checkpoint within 3 s; revised plan may continue asynchronously.
- **cost:** About $0.01–$0.06 per interruption, dominated by re-planning and one state verification; trivial interruptions should use no model call beyond the relay.
- **security:** Cancellation is not proof that an external side effect was undone. The system must report committed versus merely queued actions, preserve an append-only journal, and never claim rollback without verification. Journal entries should redact secrets and expire quickly.
- **missing:** Cooperative cancellation and supersession semantics in Mac/browser workers; An idempotent action journal with committed, running, cancelled, and unknown states; A relay command that binds an interruption to the active job/session instead of treating it as a new unrelated utterance

### "“When I say ‘send that to her’ or ‘use the thing we just found,’ resolve the person, artifact, and destination from the live browser/Mac work and carry it out without making me repeat the details.”"
- **useful because:** Short wearable utterances depend on shared context. Today browser findings, Mac state, job receipts, and voice history live in separate shapes, so pronouns and deictic phrases are brittle precisely when the owner’s hands are unavailable.
- **path:** pendant → relay → browser-extension → mac-planner → mac-vision → dashboard
- **model tier:** Realtime relay resolves only the small reference; a low-cost background linker builds the candidate graph from recent receipts, browser findings, and memory. Escalate to the expensive model only when candidates conflict.
- **latency:** Resolve common references in under 800 ms; ask one focused spoken question when confidence is low; no full-context replay on every turn.
- **cost:** Usually under $0.01 per turn with cached entity embeddings/structured candidates; expensive calls occur only on ambiguity.
- **security:** References may expose private browser entities to the wrong surface. Candidate records need surface scoping, sensitivity labels, short TTLs, and an explicit distinction between “seen on page” and “owner stated.” Never silently choose between two recipients with the same name.
- **missing:** A shared, typed artifact/entity graph linking voice turns, browser findings, Mac files/apps, and job receipts; Reference-resolution state in the live voice session, with confidence and a one-question fallback; Surface-aware projection of recent artifacts, not just static facts


## Changes it proposed to its own stack

### `integration` — Add a cross-surface evidence ledger for each user-initiated transaction. Every browser, Mac, and relay step appends a compact record containing source surface, observed input, action, output artifact, timestamp, and confidence; the ledger exposes a redacted spoken receipt and a dashboard drill-down, and is linked to the existing job and session IDs. It must support partial completion and explicitly mark unknown verification rather than collapsing everything into success/failure.
- **owner gets:** The owner can ask “what did you actually do?” and receive a trustworthy answer with the exact page, app, file, or job that produced it, instead of a vague completion sentence or having to reconstruct events manually.
- effort: Medium: shared schema, append-only persistence, adapters in browser and Mac executors, and a short receipt formatter.  ·  risk: Receipts can leak sensitive page text or filenames; redact values, enforce TTLs, and retain hashes/labels by default. If an adapter fails, show an incomplete receipt rather than claiming the transaction succeeded.
- cost: Small storage cost; about $0.001–$0.02 extra model cost only when a natural-language receipt is requested.  ·  latency: Under 100 ms for appending structured records; receipt generation can be asynchronous and delivered through the existing alert path.
- security: Improves auditability but creates a new cross-surface metadata store. Encrypt it, scope records to the owner/session, expire raw evidence quickly, and keep secrets out of the ledger.
- depends on: A shared transaction ID propagated by /plan and /execute; Adapters that report browser and Mac observed outputs, not only action acknowledgements; A redaction policy for page text, screenshots, local paths, and recipient identities


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing capabilities and one integration change: cross-device evidence-backed task completion, interrupt-and-supersede for active work, deictic reference resolution across recent browser/Mac/voice context, and a cross-surface evidence ledger. The most useful is the first: one spoken request that safely spans authenticated browser and local Mac and reports exactly what changed.

**Biggest unknown:** Whether the existing Mac/browser executors can already propagate a shared transaction ID and observed outputs; that determines whether the ledger and cross-surface handoff are mostly wiring or require executor changes.

