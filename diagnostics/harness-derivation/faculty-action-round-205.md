# Harness derivation — faculty-action — round 205

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Carry out this multi-step request as one transaction. After every step, verify the result; if a later reversible step fails, automatically undo the earlier reversible changes, then tell me exactly what was completed, undone, or left for me."
- **useful because:** Today an executor can run several actions and a verifier can inspect one step, but the owner still bears the burden of reconciling partial failure. A saga-style runner makes complex requests trustworthy: it stops cascading damage, compensates what it safely can, and reports the irreducible remainder rather than claiming success.
- **path:** faculty-judgement → faculty-action → mac-planner → mac-vision → browser-extension → relay-realtime
- **model tier:** background for plan compilation; realtime only for the owner's conversational updates; deterministic Mac/browser executors for actions and faculty-perception for postcondition checks
- **latency:** Under 2 seconds per short step; up to 30 seconds for a 10-step workflow, with immediate progress events
- **cost:** Low-to-moderate: one planning call plus verification calls per step; dominated by perception evidence, not execution
- **security:** Each step needs an explicit reversibility classification and bounded compensation. Never compensate an irreversible external side effect automatically. Redact secrets from receipts; require the existing physical transaction approval latch before risky steps. If verification is unknown, pause rather than guessing.
- **missing:** A first-class saga/compensation record linking plan step, executor receipt, verifier provenance, and compensation receipt; A policy field saying which reversible action classes may be auto-undone; A user-facing partial-commit summary

### "Resume the action I started earlier when the Mac or browser comes back, but only if the exact app, browser session, URL, and relevant fields are still the same; otherwise stop and ask me what changed."
- **useful because:** A dropped link or sleeping Mac currently turns a safe continuation into either a lost task or a dangerous blind retry. Binding a continuation to a state fingerprint prevents duplicate purchases, duplicate messages, and stale-form submissions while still letting long tasks finish unattended.
- **path:** relay-realtime → faculty-judgement → faculty-action → mac-planner → mac-vision → browser-extension
- **model tier:** Background orchestration with deterministic hashing; realtime only to explain a mismatch to the owner
- **latency:** Resume within 5 seconds of fresh host/browser presence; mismatch decision under 1 second
- **cost:** Low: one lightweight presence read and one targeted verification per resume; no model call when fingerprints match
- **security:** Fingerprints must be salted hashes of only the minimum state, never page contents or credentials. Browser session IDs and continuation tokens must expire. A mismatch is a hard stop, not an invitation to infer. Physical approval must be reacquired if any risk-bearing field changed.
- **missing:** A durable continuation token carrying expected state hashes, expiry, and step cursor; A resume gate that composes /observe and /browser/status freshness with verifier evidence; A safe distinction between transient host absence and state mismatch

### "After you do something on my Mac or in my browser, give me a compact proof packet: what changed, which exact app/session it changed in, what was verified afterward, and what remains unknown—without exposing private page text."
- **useful because:** A green 'done' is not enough for actions that matter. The owner needs an auditable, privacy-preserving answer that distinguishes executor intent from observed reality, especially when a browser command times out or a remote app changes underneath it.
- **path:** faculty-action → faculty-perception → mac-planner → mac-vision → browser-extension → relay-realtime
- **model tier:** Deterministic receipt assembly with a cheap summarizer; realtime only when the owner asks for explanation
- **latency:** Under 2 seconds after each completed action; incremental packet updates for long jobs
- **cost:** Low: hashes and structured metadata dominate; optional summarization is a small background call
- **security:** Default to hashes, app/session identifiers, timestamps, and bounded redacted snippets. Never include passwords, tokens, full message bodies, or page text unless the owner explicitly requests it. Sign the packet and bind it to the executor receipt and verifier evidence so it cannot be mistaken for proof from intent alone.
- **missing:** A signed provenance-envelope schema joining executor receipt, verifier result, state freshness, and unknowns; A redaction and sensitivity policy shared by Mac, browser, and relay; A compact pendant-safe rendering for success/partial/unknown

### "Only make the changes I named. Before and during execution, detect any additional file, browser field, message recipient, or app state that would be touched; abort before the first unexpected side effect and show me the attempted scope."
- **useful because:** Verification after an action is too late when an automation has a broader blast radius than intended. A declarative side-effect boundary would let the owner safely delegate sensitive workflows: the system must prove that each write is inside the requested scope, not merely report that something happened afterward.
- **path:** faculty-judgement → faculty-action → faculty-perception → mac-planner → mac-vision → browser-extension → relay-realtime
- **model tier:** Deterministic policy and diffing at execution time; use a cheap model only to translate the owner's natural-language scope into typed selectors
- **latency:** Scope compilation under 1 second; preflight and each write check under 300 ms; abort synchronously on a violation
- **cost:** Low-to-moderate: structured preflight plus per-write observation; dominated by browser/app state capture for complex workflows
- **security:** Default-deny on unknown selectors, stale state, hidden redirects, new recipients, or unclassified writes. Do not capture full secrets or page contents; represent sensitive targets by salted hashes and sensitivity labels. A scope violation must prevent the write, not merely create an alert. Risky in-place edits still require the existing physical approval latch.
- **missing:** A typed side-effect scope language for files, browser fields/URLs, recipients, and app state; A preflight/diff hook in every executor that can veto a write before dispatch; An enforcement receipt recording allowed, observed, and blocked effects

### "Never let two parts of you act on the same app, browser session, file, or recipient at once. If a voice request and a scheduled job collide, serialize them, show me the conflict, and release the lock automatically when the work ends or expires."
- **useful because:** The Mac, browser, relay, and routines can independently originate work. Without a shared resource lock, two valid intentions can race into duplicate sends, interleaved edits, or a stale browser submission. The owner should get one ordered action rather than debugging an accidental merge.
- **path:** relay-realtime → faculty-judgement → faculty-action → mac-planner → mac-vision → browser-extension
- **model tier:** Deterministic relay lease service; no expensive model call except to explain an unusual conflict
- **latency:** Acquire or reject a lease in under 100 ms; queue ordinary conflicts transparently; expire abandoned leases within a configured TTL
- **cost:** Very low API cost; a small durable lease table and event stream dominate
- **security:** Lease keys must be scoped to the narrowest resource and tenant, cryptographically bound to the job and risk class, and impossible for a stale worker to renew after expiry. Never lock by broad app name when a session/file/recipient identifier is available. A forced release of a risky lease requires owner confirmation.
- **missing:** A relay-wide resource lease and fencing-token service; Executor support that presents and checks fencing tokens before every mutation; Conflict UI/haptic status and an owner policy for queue versus cancel

### "Try this change in a private sandbox first. Show me the exact diff and resulting preview, then commit it to the real app only if I approve; if the app cannot provide a sandbox, do not simulate one—tell me it is unavailable."
- **useful because:** Many requested actions are easy to preview but hard to trust: editing a document, changing settings, composing a form, or rearranging files can have side effects before the owner sees the result. A genuine shadow execution gives the owner a safe way to inspect outcomes without sending, publishing, or overwriting anything.
- **path:** faculty-judgement → faculty-action → mac-planner → mac-vision → browser-extension → relay-realtime
- **model tier:** Deterministic app/browser sandbox adapters; background model only to summarize a diff; realtime for the final owner decision
- **latency:** Create a sandbox in under 3 seconds where supported; preview within 10 seconds for a multi-app task; never block the live conversation while rendering
- **cost:** Moderate engineering cost and modest storage for copy-on-write snapshots; low per-use model cost
- **security:** A sandbox must be technically isolated, not a naming convention. Block network sends, external recipients, credential access, destructive system calls, and hidden app automations. Never claim isolation for an app without an adapter that can enforce it. Commit must be a new, explicit transaction bound to the reviewed diff and physical approval where required.
- **missing:** Per-app/browser copy-on-write or draft-session adapters; A capability declaration that says which side effects are actually isolated; Diff/provenance transport from sandbox to commit and an explicit commit gate


## What it asked for

_Nothing._
## Its own summary

This round produced three non-duplicate execution capabilities. The highest-value one is transactional multi-step execution with postcondition verification and compensating rollback: it turns partial failures into bounded, truthful outcomes. I also proposed state-fingerprinted continuation across Mac/browser outages, and privacy-preserving signed proof packets that separate executor receipts from independently verified reality. I still need three concrete primitives from the stack: a saga record with compensation links, a durable state-bound continuation token/resume gate, and a signed redacted provenance-envelope schema. The existing routes and granted verifier are enough to prototype all three; no new hardware is required.

**Biggest unknown:** Whether the current job/ledger schema already has a hidden compensation or provenance envelope that can be extended rather than adding these as new records; the route inventory summaries did not expose those fields.

