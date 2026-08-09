# Harness derivation — mac-terminal — round 275

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I rebooted the Mac or lost the link — continue the thing you were doing, but don't repeat anything that already happened.”"
- **useful because:** This turns the current durable ledger and job history into actual continuity. Today an interrupted job stays marked processing, cancellation cannot stop a running shell, and resume actions are only returned for a human or model to repost. The owner gets a truthful spoken recovery instead of guessing whether a browser fill, file move, or shell command already ran.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Background model for reconciliation and replay planning; realtime only for the short spoken confirmation.
- **latency:** 2–5 seconds to inspect state; replay proceeds asynchronously with a pendant status beacon and a final spoken result.
- **cost:** Low: one background planning call per recovery, then ordinary Mac action calls; dominated by replay verification, not generation.
- **security:** Replaying a mutation can duplicate side effects. Require an idempotency key and postcondition check for every step; never infer success from a stale processing record. Send only job/ledger metadata and browser provenance, not page contents, to the relay unless needed.
- **missing:** Boot-time reconciliation of processing jobs; orchestrator closeLedger and a real jobId↔ledgerId join; PID-aware cancellation and exactly-once action replay; A recovery coordinator that verifies browser/file postconditions before POST /execute

### "“Finish this browser task from where I left off, and show me exactly what you changed.”"
- **useful because:** The browser can hold authenticated sessions that the relay cannot reach, while the Mac can perform local file and app actions. This capability makes a durable, inspectable handoff: recover the active tab, verify the last known page state, perform only the remaining steps, and return a source-backed change report rather than a vague success message.
- **path:** pendant → relay → browser → mac-planner → dashboard
- **model tier:** Background model for page-state comparison and change summary; realtime handles only the owner’s short request and completion.
- **latency:** 3–10 seconds for session inspection; longer browser actions stream status to the pendant and dashboard.
- **cost:** Moderate only when page interpretation is needed; structured browser snapshots and provenance keep context smaller than screenshots.
- **security:** Authenticated content stays in the browser node. Persist only URL/title, action receipts, provenance IDs, and explicit result claims; redact form values and never replay a submit without verifying the target and prior state.
- **missing:** Deterministic browser evidence read for a session; A resumable browser transaction ID linked to Mac job and ledger records; Postcondition/diff receipts for browser actions; A single handoff endpoint that joins browser provenance with Mac receipts

### "“What am I looking at, and what is the safest next click?”"
- **useful because:** The owner can ask from the pendant without touching the keyboard. The Mac supplies foreground-window and active-tab facts, the browser supplies a structured snapshot or bounded capture only when necessary, and the model explains the current state and proposes one reversible next action. It bridges the pendant's lack of a display with the Mac's screen and the browser's authenticated session.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Realtime for the short spoken explanation; use a cheaper background model for large page summarization.
- **latency:** Under 2 seconds for observe plus structured browser snapshot; under 5 seconds if a screenshot is required.
- **cost:** Low when using metadata and structured snapshots; screenshot interpretation is the dominant token and latency cost.
- **security:** Do not send raw screen or authenticated page text farther than needed. Redact passwords, payment fields, and hidden tabs; treat the next click as a suggestion until the owner says “do it.” Record the exact tab URL, snapshot timestamp, and chosen action for audit.
- **missing:** A deterministic join between GET /observe and the active browser session; A screen/tab redaction layer for snapshots; A spoken response path that can cite the snapshot timestamp and action receipt

### "“Before you act, tell me exactly what information would leave each device, then do it.”"
- **useful because:** The owner gets a plain-language data-flow explanation for a multi-surface action: which browser fields, Mac files, audio fragments, and relay metadata are involved. This is not a blocking approval gate; it is a truthful preview followed by the owner’s existing maximum-access execution policy. Today the system can execute across surfaces but cannot explain the concrete data boundary of one action.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Realtime for a short data-flow explanation; background model for inspecting large action plans and classifying fields.
- **latency:** Under 2 seconds for structured actions; up to 5 seconds when browser forms or local files require inspection.
- **cost:** Low when based on typed action metadata; dominated by exceptional page/file inspection.
- **security:** Never transmit secrets merely to explain them. Return field classes, destinations, and hashes locally where possible; redact values. Keep this informational rather than adding a confirmation gate.
- **missing:** Per-action data-flow manifests for shell, browser, file, and audio operations; Secret/PII classification at the Mac and browser boundaries; A relay endpoint that renders one cross-surface egress explanation

### "“Make my work state portable: put this exact project, browser session, audio state, and pending actions onto whichever device is available.”"
- **useful because:** The owner should not lose their working context when moving between Mac, browser, relay, and pendant. This creates a signed, minimal workspace capsule containing project identity, active tabs, pending action IDs, and audio turn position—not a giant transcript—then restores it on another available surface with explicit missing-part reporting.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Background model for capsule compression and conflict explanation; realtime only for the spoken handoff.
- **latency:** 2–5 seconds to create or inspect a capsule; restoration runs asynchronously and reports each surface as ready, unavailable, or conflicted.
- **cost:** Low: compact structured state keeps context and storage small; model cost is limited to conflict resolution.
- **security:** Capsules must be encrypted and capability-scoped. Browser credentials never leave the browser; store references and provenance IDs instead. Reject stale capsules rather than silently overwriting newer work.
- **missing:** A versioned cross-surface workspace-capsule schema; Conflict resolution using project/session timestamps; Browser session export/import of metadata without credentials; Pendant-visible restore progress and conflict summaries

### "“While I’m away, watch for the one thing that genuinely needs me and interrupt me only once, with the evidence.”"
- **useful because:** Existing monitoring can produce events, but the owner needs an interruption policy that combines Mac state, authenticated browser changes, pending jobs, and pendant availability into one ranked exception. It should suppress duplicates, attach the source evidence, and defer non-urgent items until the owner is reachable instead of generating a stream of alerts.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Cheap background model for event deduplication and priority ranking; realtime only when delivering the selected interruption.
- **latency:** Seconds for event ingestion; under 10 seconds from a high-priority change to a pendant alert when the link is live.
- **cost:** Low-to-moderate background inference, dominated by event volume; deduplicated state keeps context bounded.
- **security:** Authenticated browser contents stay local; relay receives event type, urgency, provenance reference, and a minimal evidence capsule. The owner controls quiet hours and emergency categories.
- **missing:** A unified event stream joining browser watches, Mac jobs, and pendant reachability; Cross-source deduplication and urgency policy; Evidence capsules that can be read aloud without leaking sensitive page text; A durable interruption queue with acknowledgement and expiry


## Changes it proposed to its own stack

### `relay` — Add a Mac-availability transaction coordinator: when a pendant request arrives, create one correlation ID, persist the spoken intent and required postcondition, dispatch to the browser and Mac only when their heartbeats are current, and deliver a single terminal receipt (or queued/stale state) back to the pendant. On reconnect, reconcile browser, Mac job, and ledger state before replaying any remaining step.
- **owner gets:** The owner gets one truthful answer to “did it happen?” across a sleeping Mac, an authenticated browser, and a wearable—not three disconnected statuses or a duplicated action after reconnect.
- effort: High: durable state machine, heartbeat-aware scheduling, postcondition evaluators, and adapters for existing browser and Mac job records.  ·  risk: A bad postcondition could trigger duplicate work. Default to no replay when evidence is ambiguous, surface the exact reason, and retain a manual resume path.
- cost: Low persistent storage and relay execution cost; background model only for ambiguous reconciliation.  ·  latency: Adds tens to hundreds of milliseconds when online; offline requests are immediate local queue writes and complete on reconnect.
- security: Correlation metadata can leave the device; keep page contents local to browser and send only provenance/result claims. Use capability-scoped tokens per surface.
- depends on: truthful_action_status_beacon; audio_link_truth_and_recovery; A stable job↔ledger join; Browser transaction IDs


## What it asked for

_Nothing._
