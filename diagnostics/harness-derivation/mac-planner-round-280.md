# Harness derivation — mac-planner — round 280

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac accessibility and screen capture** — As of 2026-08-09, AI Pendant Agent is trusted for Accessibility and Screen Recording; synthesized input successfully posts, secure input is false, and UI actions should reach the screen.
  - evidence: mac_readonly_inspect(operation=running_apps) invoked GET /observe and returned accessibility.trusted=true, screenRecording=true, eventsPost=true, inputReachability.status=verified.

## Capabilities it proposed

### "Finish the thing I’m looking at: turn the current page or document into the next concrete action, and do it."
- **useful because:** The owner can speak once from the pendant instead of explaining which tab, file, or app they mean. The relay binds the request to the Mac’s live foreground context, the browser session, and the exact UI target; the Mac performs the smallest useful action and returns evidence. This is the system’s highest-value everyday loop: wearable intent plus machine reach, without forcing the owner to narrate context.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime for the short spoken disambiguation only; a cheaper background planner resolves the current UI/page into a bounded action, then the Mac executes and posts a receipt.
- **latency:** Acknowledge on pendant within 500 ms; inspect context in 2 s; complete a simple action in 5 s. If ambiguity remains, ask one spoken choice rather than guessing.
- **cost:** About $0.01–$0.04 per invocation, dominated by one vision/context interpretation; simple text pages should use the cheaper planner and avoid vision.
- **security:** The current screen can contain secrets and the action can mutate external state. Send only redacted role/title/selected text by default, never screenshots unless the owner has enabled them. Require an explicit spoken confirmation for sending, deleting, purchasing, or publishing; return postcondition evidence rather than claiming success from a click.
- **missing:** A semantic current-target reader that returns app/document/selection and stable UI identity as real JSON Schema (the pending mac_semantic_context_read request).; A planner-to-executor contract carrying target identity plus postconditions, not just coordinates or free-form text.; A durable spoken confirmation and result receipt path from Mac back to the pendant.

### "Before anything on my Mac or in my browser sends data out, give me a one-line warning on the pendant with what would leave and where, and let me cancel it."
- **useful because:** The owner gets a practical privacy boundary at the moment it matters, rather than trusting that an agent, browser tab, or automation will remember every sensitive field. It covers email sends, web uploads, form submissions, and sharing from apps—places a wearable can interrupt even when the Mac is unattended or the owner is not watching the screen.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** A deterministic local classifier first (destination, file paths, MIME, text labels); use the background model only to summarize uncertain payloads. Realtime is reserved for the brief spoken alert and cancel/allow exchange.
- **latency:** The classifier must run before dispatch with under 150 ms added latency; pendant alert within 700 ms. If inspection cannot finish, fail closed for configured sensitive destinations and leave the operation staged, not partially sent.
- **cost:** Near-zero for deterministic metadata; $0.002–$0.01 only when a payload needs semantic redaction/summarization. The main cost is implementing interception at both browser and Mac dispatch boundaries.
- **security:** The inspector itself must not upload the very secret it is protecting. Keep raw payload local, send the pendant only a redacted category, destination, and byte count, and make policy owner-configurable. It must distinguish a preview from a completed send and log an immutable decision receipt.
- **missing:** A pre-dispatch interception hook in browser and Mac actions; POST /execute currently can run FULL_CONTROL actions without a policy gate.; A local redaction/classification service that can inspect files, form bodies, and outgoing mail without exposing contents to the relay.; A pendant alert action with local cancel semantics and a receipt that proves whether dispatch was prevented.

### "If a Mac or browser job gets stuck or fails while I’m away, wake me on the pendant with the reason and give me a button choice to retry safely, pause it, or leave it for later."
- **useful because:** Long jobs currently fail silently or require the owner to return to the Mac and reconstruct what happened. This turns the pendant into an operational control surface: the always-awake relay receives a structured failure, the Mac preserves the partial work, and the owner can make a bounded decision without opening the laptop.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background/cheap model classifies the failure and writes a short explanation; realtime is used only if the owner asks a follow-up question. Retry eligibility is deterministic, not model-decided.
- **latency:** Failure notification within 10 seconds of a receipt timeout; button response acknowledged locally in under 300 ms and queued if the link is down. A retry should resume from an idempotent checkpoint rather than repeat completed mutations.
- **cost:** Under $0.01 per failure, mostly receipt summarization; routine heartbeat and retry classification should be rules-only. Engineering cost is in checkpointing and durable command correlation, not inference.
- **security:** Never retry sends, purchases, deletions, or external mutations automatically. The pendant button should select only a precomputed safe action; high-impact choices require spoken confirmation. Persist opaque job IDs and redacted causes, not page contents or mail bodies, and show a receipt proving whether retry began.
- **missing:** A relay-to-pendant alert/command channel that supports action choices, not only queued informational alerts.; A job checkpoint protocol with idempotency keys, retry budgets, and an atomic handoff receipt across Mac and browser.; A postcondition-aware result schema distinguishing queued, started, completed, and partially completed; existing receipts are not sufficient for this control loop.

### "Give me a two-hour autonomy lease: handle routine work within the limits I say, and stop exactly when the lease expires or I revoke it from the pendant."
- **useful because:** The owner gets useful unattended work without granting an agent permanent authority. A single spoken lease can cover a browser session, Mac files, and relay-scheduled jobs; the pendant remains a physical revocation point even when the laptop is closed. Today these surfaces have separate commands and no shared, expiring authority.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** A cheap deterministic policy engine evaluates every proposed action against the lease; use a background model only to classify ambiguous tasks. Realtime handles creation and revocation of the lease, not routine execution.
- **latency:** Lease creation and revocation acknowledged in under 1 second. Every action must be policy-checked before dispatch without adding more than 100 ms; expiry must take effect within 1 second across queued work.
- **cost:** Under $0.005 per action for rules and audit records; occasional ambiguous classification may cost $0.01. The dominant cost is implementing one authority token understood by Mac, browser, relay jobs, and pendant firmware.
- **security:** The lease must be scoped by operation, destination, amount, and time—not a broad 'do anything' flag. Store a signed, append-only action log; do not send raw page or mail content to the relay unnecessarily. Revocation must be local on the pendant and fail closed on link loss for actions not already committed.
- **missing:** A shared capability token with expiry, scope, nonce, and revocation state accepted by every executor.; A pendant-local revoke latch that invalidates the token even while offline, with replay protection when the link returns.; Mac and browser dispatch hooks that check the lease before each action and report committed versus merely queued work.

### "For a risky action, read me the exact destination and payload summary on the pendant, then let the physical button approve that one action—and prove afterward what I approved."
- **useful because:** A spoken 'yes' can be misheard and a Mac dialog can be hidden behind another window. The pendant gives the owner a separate, unmistakable approval surface for sending money, publishing, deleting, or submitting sensitive forms, with a cryptographic binding between the approval and the exact action rather than a vague approval of a plan.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic digest and risk classification do the security work; realtime voices a short redacted summary and listens for an optional correction. No model may alter the approved payload after the button event.
- **latency:** Prepare a challenge in under 500 ms, speak the summary within 2 s, and accept the button only for a 30-second challenge. Execution receipt should arrive within 5 s or state clearly that it did not happen.
- **cost:** Less than $0.005 per challenge for hashing, signing, and receipts; semantic summarization may add $0.005–$0.02 when needed. Hardware-side storage is a few hundred bytes for a pending challenge and last nonce.
- **security:** Never voice secrets or full message bodies; use destination, item count, amount, and a short redacted digest. Bind a one-time nonce to the exact serialized action, account, and expiry; reject replay and any post-approval mutation. If the link drops, the local button must not imply remote execution—the owner gets a pending result instead.
- **missing:** A signed challenge/approval protocol terminating in the pendant button, with nonce replay protection and offline-safe pending state.; A Mac/browser executor that accepts only the exact approved action digest and returns a committed postcondition receipt.; A relay route that can deliver redacted challenge summaries and distinguish approved, rejected, expired, and executed states.

### "Lock me down now: from the pendant, close active browser sessions, pause Mac automations, revoke temporary agent authority, and show me a receipt that the lock took effect everywhere it could."
- **useful because:** If the owner loses the laptop, notices a suspicious session, or simply wants an immediate privacy reset, today they must reach each surface separately. A physical command that propagates through the relay to the Mac and browser is valuable precisely when the Mac is unattended or untrusted, and it can report partial failure honestly instead of pretending one local action protected everything.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Rules-only for revocation and session closure; realtime is unnecessary except to confirm the owner’s spoken intent if they ask for a reason or scope. The relay should fan out commands and aggregate receipts.
- **latency:** Pendant enters a local locked state immediately; relay fan-out starts within 1 second. Each reachable surface reports closed, paused, or unreachable within 10 seconds, with retries that cannot reopen anything.
- **cost:** Near-zero inference cost; roughly $0.001 per fan-out for durable events and receipts. The main work is revocation semantics and testing failure modes, not model calls.
- **security:** The pendant must be able to enter lockdown offline and keep microphone/playback disabled locally. Remote commands must be authenticated, idempotent, and monotonic: retries may close more sessions but can never restore authority. Do not claim browser cookies or third-party sessions are revoked unless the browser reports that specific postcondition; distinguish local closure from server-side logout.
- **missing:** A pendant-originated emergency event with a local persistent lock bit and authenticated monotonic sequence number.; Relay fan-out to Mac and browser that can cancel queued jobs, invalidate authority leases, close sessions, and aggregate per-surface receipts.; Explicit browser and Mac postconditions for session closure, authority revocation, and unreachable state, plus a recovery procedure that requires a fresh local unlock.


## What it asked for

_Nothing._
## Its own summary

Discovered the granted surface and live Mac state, then recorded three non-duplicate cross-node capabilities: spoken current-target completion, pre-dispatch privacy interruption, and pendant-controlled recovery for failed Mac/browser jobs. The Mac now has verified Accessibility, Screen Recording, and working synthesized input; Safari is foreground and iPhone Mirroring is running. I also informed faculty-action that no truthful iOS delivery receipt is exposed through my current tools.

**Biggest unknown:** The missing semantic current-target reader and durable pendant command/receipt path remain the key blockers. Browser inspection is currently ambiguous between action:browser_inspect and POST /browser/inspect, and there is still no verified pre-dispatch interception hook for outbound data.

