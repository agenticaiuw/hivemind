# Harness derivation — faculty-action — round 225

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live device/session state** — The live device inventory shows Safari on MacIntel online with two tabs and home-macbook-bridge online; no pendant device is listed. GET /observe currently reports foregroundApp loginwindow, so interactive-session readiness is unknown and must not be inferred as unlocked.
  - evidence: discover:devices live result plus describe GET /observe liveResponse at 2026-08-09T00:24:29.792Z

## Capabilities it proposed

### "“Do this in the page I’m looking at, but stop if the page or the value changed while you were preparing it.”"
- **useful because:** This is the missing bridge between faculty-judgement and a trustworthy hand: browser sessions can change underneath a queued job. The browser extension snapshots URL plus target-field state, Mac/browser performs the action only if those preconditions still hold, and faculty-perception independently verifies the postcondition. The pendant's existing physical transaction latch can approve the exact digest without receiving page contents or secrets. It prevents the most dangerous class of automation failure: a correct instruction applied to the wrong account, tab, or stale form.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-perception → faculty-judgement
- **model tier:** Realtime only for the short spoken intent and approval summary; deterministic relay/browser checks and a cheaper background model for ambiguous target resolution.
- **latency:** 2–5 seconds for snapshot and preflight; execution must refuse rather than wait if the snapshot expires. Verification adds under 2 seconds.
- **cost:** About $0.01–$0.05 per invocation when language is needed; most cost is browser round trips, not model tokens.
- **security:** The pendant receives only a redacted human summary and digest, never field values or page secrets. URL/account identifiers need sensitivity labels. Refuse on URL, session, target-field hash, or expiry mismatch; never silently retarget. Require the existing physical_transaction_approval_latch for risky submissions, and return unknown—not success—if postcondition verification cannot obtain fresh state.
- **missing:** A typed browser precondition snapshot containing session ID, URL, target locator, value hash, expiry, and sensitivity without exposing the value; A browser executor branch that atomically rechecks that snapshot immediately before mutation; A relay operation envelope linking snapshot digest, action receipt, and verify_operation_step provenance

### "“Queue this for my Mac, but do not run it until I’m back at the computer; tell me when it is safe to continue.”"
- **useful because:** Today the relay can know that the bridge is online, but cannot distinguish an awake interactive session from the macOS login screen. A queued action can therefore be delivered at the wrong time or sit indefinitely with no honest explanation. A lock-aware gate would let the pendant accept work while away, wake the owner with a status beacon when execution becomes possible, and preserve the conservative default when state is unknown.
- **path:** pendant → relay → mac-planner → faculty-perception → faculty-judgement
- **model tier:** No expensive model for gating: a deterministic policy reads host state. Use the low-latency model only to phrase the owner's request and the final status.
- **latency:** Host-state refresh within 5 seconds of a transition; queued work remains staged until an authenticated active-session observation is fresh.
- **cost:** Negligible model cost; one small authenticated host-state heartbeat per transition and bounded polling while a job is staged.
- **security:** Do not infer unlock from foregroundApp, browser heartbeat, or bridge liveness. The gate must return unknown on stale or contradictory observations and must not execute then. Do not transmit secrets in the pending record. Owner-configured policy decides which action classes may resume automatically; default is stage-for-approval.
- **missing:** A macOS agent source for lock/session-active state, with freshness and provenance (not a guessed boolean); A relay job gate that binds the action to a specific host-session epoch and rechecks it immediately before execution; A pendant status pattern for staged/blocked/ready, distinct from approval and outcome patterns

### "“Bookmark what I’m seeing right now.”"
- **useful because:** The physical moment bookmark already marks an instant, but by itself it cannot tell the owner which tab, document, selection, or project that instant referred to. This capability atomically joins the pendant's bookmark event with the freshest Mac foreground/app state and browser session snapshot, then returns a compact, searchable context card. If the Mac is absent, it stores the bookmark normally and explicitly marks context as unavailable rather than inventing it; when the link returns, it must not retroactively claim a state it did not observe.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-perception
- **model tier:** Deterministic capture and hashing first; use a cheap background model only to produce a short title from owner-approved, sensitivity-filtered text. Realtime is unnecessary.
- **latency:** Haptic acknowledgement immediately; context join within 3 seconds when the Mac/browser is reachable. Offline bookmark durability is immediate and context enrichment is best-effort with an explicit unavailable result.
- **cost:** Usually under $0.01; dominant cost is optional summarization. No model call is needed for a URL/title-only card.
- **security:** Never put page bodies, form values, or secrets into the pendant or relay event by default. Store sensitivity labels and hashes for private content, and require explicit owner policy before retaining snippets. The card must carry observedAt and source provenance; stale browser status cannot be represented as current context.
- **missing:** A correlation protocol joining the pendant bookmark monotonic ID to a Mac/browser observation taken within a bounded time window; A context-card store/search projection that distinguishes observed context from inferred labels; A browser snapshot mode that returns safe metadata (session, URL, title, selected-text hash) without page secrets

### "“Pause this exactly where it is; when I come back, continue from the last verified step, not from the beginning.”"
- **useful because:** A multi-step Mac/browser task can currently be cancelled or reported, but an interruption can leave the owner unsure whether restarting will duplicate a message, lose a draft, or skip a step. This capability creates a durable, resumable action checkpoint: the relay records the last verified postcondition, the browser session identity and a redacted continuation token; on return, faculty-perception checks that the world still matches before faculty-action continues. The pendant can acknowledge pause/resume without exposing page contents. This is not merely job status or undo: it preserves safe continuation through a partial execution.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-perception → faculty-judgement → mac-terminal
- **model tier:** Deterministic checkpointing and postcondition checks; use a cheaper background model only to summarize the checkpoint. Realtime is reserved for the owner's pause/resume utterance.
- **latency:** Pause acknowledgement under 1 second; checkpoint durable within 2 seconds. Resume preflight under 5 seconds, refusing on any mismatch instead of guessing.
- **cost:** Usually under $0.02 per interrupted task; storage and browser checks dominate, with no model call for structured workflows.
- **security:** Continuation tokens must be opaque, short-lived, bound to operation ID and browser session, and must not contain secrets or page text. Never resume a submission step after an unknown receipt. Require the existing physical transaction approval latch again when the resumed step is consequential; a pause must revoke any pending approval.
- **missing:** A first-class checkpoint schema with step index, verified postcondition digest, session epoch, expiry, and resume policy; Executor support for idempotent step boundaries and explicit unknown outcomes rather than treating transport success as completion; A resume orchestrator that calls fresh verify_operation_step before each continuation and emits a new outcome beacon

### "“Show me which tab you mean, and let me choose it from the pendant without reading the screen.”"
- **useful because:** When several browser tabs or accounts match an instruction, silently picking one is unsafe and asking the owner to inspect the Mac defeats a wearable assistant. A rotary encoder plus haptic patterns can present a bounded list of redacted tab labels one item at a time; the owner turns to select and presses to confirm. The browser extension then binds the action to that exact session/tab identity. This makes the pendant a genuine decision surface across Mac and browser, not merely a microphone and approval button.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-judgement → faculty-perception
- **model tier:** Cheap deterministic ranking and redaction; realtime language only for the owner's spoken request. No expensive model is needed to enumerate tabs or render haptics.
- **latency:** Candidate list within 2 seconds; haptic/rotary selection feedback under 150 ms per detent; selection expires after 30 seconds.
- **cost:** Under $0.01 per selection; costs are browser polling and a small relay event, not inference.
- **security:** The pendant must receive only owner-approved redacted labels (for example, domain plus short title hash), never page text, account identifiers, or secrets. Bind the choice to browser device, session, tab ID, URL hash, and expiry; refuse if any changes. Require the existing physical transaction latch for a consequential action, and make cancel the safe default.
- **missing:** A rotary encoder and second deliberate selection button in the jewellery enclosure, plus firmware input/debounce and compact haptic vocabulary; A browser tab enumeration route returning stable opaque tab IDs with sensitivity-filtered labels; A relay selection session that cryptographically binds the chosen tab to the subsequent operation and verification

### "“Privacy now—stop listening, stop any staged computer action, and erase the temporary page context.”"
- **useful because:** The owner needs one physical, unmistakable escape hatch when entering a sensitive setting. A pendant gesture should fan out to the relay, Mac agent, and browser extension: stop capture, cancel staged work, revoke pending approvals, and delete only ephemeral context artifacts while preserving an auditable tombstone. Today those surfaces have separate cancellation and retention semantics, so an owner cannot know that one gesture actually reached all of them.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-action → faculty-perception
- **model tier:** Fully deterministic security operation; no language model is needed. Realtime may narrate the result only after each surface reports its state.
- **latency:** Local pendant acknowledgement immediately; relay fan-out within 1 second; each surface must report stopped/cancelled/unknown within 5 seconds. Unknown must remain visible and must not be called erased.
- **cost:** Negligible inference cost; bounded control messages and deletion receipts dominate.
- **security:** The gesture must be physically distinct from approval and cancel only pending work, never execute anything. Deletion must be scoped to temporary artifacts and produce hashes/tombstones without retaining secret content. If a surface is offline, the relay queues the revocation and marks it not-yet-enforced; the pendant must not claim privacy complete. Existing physical approval envelopes must be invalidated by a revocation epoch.
- **missing:** A signed cross-surface privacy/revocation envelope with monotonic epoch and expiry; Mac and browser handlers that halt active capture, cancel staged jobs, revoke approvals, and return deletion receipts; A firmware gesture using the coming second button or rotary control, with a distinct haptic confirmation for complete versus partially enforced


## What it asked for

_Nothing._
## Its own summary

Recorded three distinct capabilities: (1) stale-context-guarded browser execution with typed preconditions, immediate recheck, and independent postcondition verification; (2) a lock/session-aware relay gate that stages work while the Mac is unavailable and never guesses unlock from bridge/browser liveness; and (3) atomic pendant bookmark-to-current-Mac/browser context joining with provenance and explicit unavailable semantics. The live inventory confirms Safari and the Mac bridge are online, but no pendant is registered; /observe currently sees loginwindow, so execution readiness is unknown. I still need a real macOS lock/session-active provenance source, a typed browser snapshot/precondition protocol, and a correlation/context-card store connecting pendant bookmark IDs to fresh Mac/browser observations. I did not request Accessibility again.

**Biggest unknown:** Whether the Mac agent can expose an authenticated active-console/lock state without Accessibility or Screen Recording; until that exists, deferred actions must remain staged rather than resume automatically.

