# Harness derivation — faculty-action — round 87

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If the browser bridge is unavailable, check my currently open logged-in Safari tabs anyway, gather the requested facts, and tell me clearly whether anything could not be verified; never submit or change anything through the fallback."
- **useful because:** Today a browser task simply fails when the extension is offline (currently offline with 9 pending commands), even though Safari automation is granted on the Mac. This gives the owner a useful read-only answer instead of a misleading timeout, while keeping all writes blocked until the bridge is healthy and separately approved.
- **path:** relay-realtime → faculty-judgement → faculty-action → mac-planner → browser-extension → faculty-perception
- **model tier:** Use the realtime model only to clarify the owner's request and give the short spoken result; use a cheaper background model on the Mac to extract and normalize page facts. faculty-perception supplies current tab/page evidence, and faculty-action executes only read-only Safari automation.
- **latency:** 3–8 seconds for currently open tabs; if Safari or AppleScript does not answer within 10 seconds, return a partial result with an explicit unverified status rather than retrying indefinitely.
- **cost:** Usually one short realtime turn plus a low-cost extraction call; negligible Mac execution cost. Avoids paying for repeated 45-second browser waits.
- **security:** Logged-in page contents leave the Mac only as the minimum extracted fields needed for the answer. No passwords, cookies, or raw page dumps are sent. The fallback is read-only by construction; any form fill, send, purchase, or navigation beyond the requested open tabs requires the authenticated browser bridge and an explicit later decision. Every fact carries app/tab URL/time and a verification state.
- **missing:** A read-only Safari AppleScript extraction adapter with bounded timeouts and typed evidence capsules; A router rule that selects Safari fallback only for read-only requests when browser status is offline; A shared result schema distinguishing verified, stale, partial, and unavailable facts; Owner must re-enable the Browser Bridge for any browser write or private-tab operation that Safari automation cannot expose

### "Let me approve one real-world outcome once, then have the pendant, relay, Mac, and browser carry it through as one coordinated transaction: each surface reports its precondition and postcondition, the next step cannot run until the previous one is evidenced, and if I walk away or a device drops, it resumes safely without repeating completed side effects."
- **useful because:** Today the mind can decide a multi-surface outcome but cannot reliably carry it across a dropped link or partial failure. The owner gets either brittle one-shot automation or repeated manual supervision. A coordinated transaction would make a request such as preparing a document on the Mac, attaching it in a logged-in browser, and leaving a spoken confirmation on the pendant behave as one auditable action rather than disconnected attempts.
- **path:** faculty-judgement → relay-realtime → faculty-action → mac-planner → mac-vision → browser-extension → faculty-perception
- **model tier:** Use the realtime model only for the owner's initial clarification/approval and concise status. Use a cheaper background planner to compile the dependency graph and recovery plan; use deterministic local executors and faculty-perception for evidence, not an LLM, at each step.
- **latency:** Approval and preflight under 2 seconds; each local step should report within 5 seconds. On interruption, persist immediately and resume within 30 seconds after a surface reconnects, without replaying any step lacking an idempotent proof.
- **cost:** One short realtime turn plus low-cost background planning per transaction; local state and evidence dominate storage, not API spend. Recovery should avoid re-paying for already completed model work.
- **security:** The relay stores only opaque transaction IDs and minimal step metadata; page contents and files remain on their owning device unless explicitly needed. A write step requires fresh preconditions, an owner approval scope, and postcondition evidence. Expired approvals, changed destinations, authentication changes, or missing evidence force a halt rather than a guess. The pendant gets a plain-language final receipt and can cancel the lease.
- **missing:** A cross-surface transaction protocol with durable dependency/commit state, idempotency keys, leases, and recovery states distinct from ordinary jobs; A typed evidence contract for preconditions and postconditions that faculty-perception can sign for Mac files, browser fields, and pendant playback; A relay coordinator that can resume a transaction after Mac/browser reconnect without replaying committed effects; A single approval object carrying scope, destination, expiration, and allowed side-effect class across all surfaces


## Changes it proposed to its own stack

### `mac-harness` — Install a hard preflight refusal in the executor: before dispatching any ui_click, ui_menu, type_text, press_keys, or vision step, read the live inputReachability/accessibility result from /observe. If uiActionsWillReachTheScreen is false or the probe is stale, do not invoke the action at all; return status=blocked with reason, required owner fix, and a receipt marked not-executed. Add the same gate to browser bridge writes when the extension is offline, while allowing explicitly read-only AppleScript/research actions. Make the gate decision part of the job journal so retries cannot silently turn a blocked step into a claimed success.
- **owner gets:** Right now the Mac reports UI actions as successful while doing nothing, and the browser has 9 queued commands while offline. The owner should never hear that an email was typed, a button was clicked, or a page changed when no physical action occurred. This turns silent false success into an immediate, actionable explanation and prevents unsafe retries.
- effort: Moderate: central executor preflight, freshness handling, typed blocked receipts, retry/journal integration, and tests for stale/failed probes across UI and browser writes.  ·  risk: A transient probe failure may block a legitimate action; recover by re-running observation and offering safe AppleScript/declarative alternatives. Never auto-bypass the gate. Existing read-only automation remains available.
- cost: No model/API cost; one local observation per potentially interactive step and small journal entries.  ·  latency: Adds roughly 50–200 ms per interactive step; avoids 45-second browser hangs and misleading completion.
- security: Strongly improves safety and auditability. No new data leaves the Mac; accessibility state and block reasons are already local operational metadata.
- depends on: Existing GET /observe inputReachability and uiActionsWillReachTheScreen fields; Existing actionReceipts.js and job journal; Existing browser status/queue state from GET /browser/status; A typed distinction between read-only and write actions

### `integration` — Add a cross-surface causal ledger, separate from the existing per-job receipts: every action attempt must reference a predecessor evidence hash and publish a postcondition evidence hash containing the target surface, identity, timestamp, and observed state. The relay should accept a successor only when the predecessor is committed, reject duplicate effect IDs across Mac/browser/pendant, and mark the whole chain compensatable, abandoned, or needs-owner-review when a link disappears. Reconnection should reconcile by querying evidence, never by replaying the last command.
- **owner gets:** The owner could ask for one outcome that spans devices and leave without fearing a duplicate send, upload, or edit after a reconnect. They would receive a truthful chain such as “file created, attachment confirmed, message still unsent,” instead of a collection of locally successful receipts that cannot establish what actually happened end to end.
- effort: High: define signed typed evidence envelopes, durable relay state, idempotency namespace shared by local and browser executors, reconciliation, and dashboard/pendant rendering. This is protocol work between existing components, not another action queue.  ·  risk: A false postcondition or clock/identity mismatch could halt work unnecessarily; default recovery is stop and ask, never replay. Evidence retention must be bounded and redact sensitive values. Existing single-surface jobs continue using their current receipts if no causal chain is requested.
- cost: Small D1/R2 and local journal overhead; no recurring model cost beyond optional background reconciliation.  ·  latency: Adds one local ledger write and evidence validation per step (tens to hundreds of milliseconds); reconnect recovery becomes slower but deterministic.
- security: Improves auditability and prevents cross-surface duplicate side effects. Evidence must use hashes/redacted summaries rather than copying private page contents to the relay; approval scope and transaction identity must be authenticated.
- depends on: Existing action receipts and journal IDs; Relay durable state and Mac bridge connectivity; Typed observation/postcondition evidence from faculty-perception; Browser command IDs and tab/session affinity


## What it asked for

_Nothing._
## Its own summary

Round 87 established that the Mac bridge is online, but Accessibility and Screen Recording are still unavailable to AI Pendant Agent, so UI actions can report success while doing nothing. The browser bridge is offline with 9 pending commands; recent browser jobs failed or remain processing. I recorded two concrete additions: a read-only Safari fallback for browser-offline fact gathering, and a hard executor preflight that refuses UI/browser writes whenever reachability is false or stale, producing a blocked (not successful) receipt. What I still need is not another agent grant: the owner must enable Accessibility/Screen Recording for AI Pendant Agent and bring the Browser Bridge online for any interactive or authenticated browser write. We also still lack a reliable typed evidence/verification adapter for Safari fallback and the pending action-proof/audio-path tools already requested.

**Biggest unknown:** Whether Safari AppleScript can expose enough of the owner's currently open private tabs for the specific read-only tasks without Accessibility or the browser extension; this needs a bounded probe once a concrete request and an available Safari session exist.

