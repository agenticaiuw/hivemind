# Harness derivation — faculty-action — round 219

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Show me exactly what will happen, then let me approve it once.” For any multi-step Mac/browser task, prepare a redacted rehearsal: app changes, browser fields/URLs, files/messages affected, and reversible/irreversible steps; read the compact diff over the pendant, accept one physical approval, execute, and independently verify every checkpoint. If anything differs from the rehearsal, stop and return the discrepancy instead of improvising."
- **useful because:** This is the safest way to let the owner delegate consequential work without exposing page secrets to the pendant or requiring them to watch a screen. It turns vague trust into a concrete before/after contract and catches stale pages, changed recipients, and partial execution.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-judgement → faculty-action → faculty-perception
- **model tier:** Use the realtime tier only to clarify the owner's goal and speak the short rehearsal; use a cheaper background planner for the step graph and redaction; use deterministic Mac/browser executors and faculty-perception verification for execution and proof.
- **latency:** Rehearsal in 2–5 seconds for a short task; each checkpoint under 1 second after the local executor reports; never trade verification for latency.
- **cost:** Typically one background planning call plus a short realtime summary; roughly $0.01–$0.08 depending on task complexity. Dominant cost is planning long multi-app workflows, not verification.
- **security:** Only labels, hashes, recipient/domain summaries, and redacted diffs go to the pendant; never form secrets or page contents. Approval binds to a digest and expiry. A changed URL, field, file, or recipient invalidates the approval. Owner confirmation is required before irreversible steps.
- **missing:** A typed rehearsal/diff envelope shared by planner, pendant, browser, and verifier; Per-step before-state capture and digest binding in the action ledger; A redaction policy that can summarize browser/file changes without leaking values; A single executor contract that pauses on drift rather than retrying blindly

### "“Leave this ready, but do not send or publish it until I am back.” The system should stage a browser or Mac action as a resumable, expiring checkpoint: keep the draft and exact target, notice if the Mac/browser sleeps or the page changes, and after reconnection ask for a fresh compact diff and physical approval rather than replaying an old click sequence."
- **useful because:** The owner can safely delegate work while moving between machines or losing connectivity. Today a dropped link makes an action either disappear or resume with stale state; this makes interruption a safe pause, not an accidental send.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-action → faculty-perception
- **model tier:** Use a cheap background state machine for lease expiry, reconnection, and diff comparison; use realtime only for the owner's brief resume/cancel interaction; deterministic executors perform the final action.
- **latency:** Detect stale state within 5 seconds of a heartbeat or executor failure; present a resume summary within 2 seconds of reconnection; no action is sent merely because connectivity returned.
- **cost:** Usually <$0.01 per interruption; storage and heartbeat processing dominate, with model calls only when a human-readable resume summary is needed.
- **security:** Persist only opaque job IDs, target hashes, and redacted summaries. Never replay an approval after expiry or state drift. Drafts may contain private content on the Mac/browser and must remain there; relay stores metadata only. Irreversible actions require a new physical approval.
- **missing:** A durable cross-surface checkpoint record with expiry, target digest, and current step; A true Mac wake/unlock signal; until one exists, report unknown and remain staged; Resume reconciliation that compares fresh browser/app/file state to the checkpoint; A pendant inbox rendering for paused, expired, changed, and safely cancellable states

### "“When I tap the moment button, make a return point I can act on later.” A pendant bookmark should atomically capture a small signed context bundle—time, audio bookmark ID, focused Mac app, browser session/URL identity, active project, and nearby action/job IDs—then let the owner later say “take me back to that” or “continue that task” and reopen the exact safe draft or research context without guessing."
- **useful because:** A physical bookmark is currently just a memory marker. This would make it a reliable bridge between a fleeting thought while away from the keyboard and a resumable Mac/browser workspace, without recording continuous audio or requiring the owner to remember filenames and tabs.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-terminal → faculty-perception → faculty-action
- **model tier:** Use firmware and deterministic metadata capture for the bookmark; use a small background resolver to find the associated project/job; use realtime only to interpret “that” and speak the result. No expensive reasoning is needed for ordinary reopen/continue operations.
- **latency:** Capture acknowledgement in under 300 ms locally; relay upload opportunistically; resolve a return point in under 2 seconds when online. If identity is ambiguous, present candidates and do not act.
- **cost:** Near-zero for capture and lookup; occasional small model call for ambiguous natural-language references, typically <$0.01.
- **security:** The pendant stores only an opaque bookmark ID and checksum; private audio and page contents remain on the Mac/relay under existing retention rules. Returning to a context may reveal sensitive app state, so require owner presence and never auto-submit or publish. Expire or revoke bookmarks on request.
- **missing:** A bookmark envelope that binds pendant event, Mac observation, browser session, project, and job IDs; A relay index mapping bookmark IDs to context snapshots with retention/ revocation; Browser and Mac reopen/continue actions that accept an opaque context ID rather than guessed URLs; A disambiguation UI/haptic pattern for multiple candidate return points

### "“Do this whole job, but if it only partly succeeds, put everything back and tell me exactly what could not be restored.” For a multi-step Mac/browser operation, generate a compensation plan before execution, take private local snapshots or preserve drafts where possible, execute in dependency order, and on any failed or unverifiable step automatically run only the pre-approved compensating actions. Return a signed outcome distinguishing fully committed, compensated, partially restored, and unknown."
- **useful because:** Today approval and verification can authorize and observe a workflow, but a failed middle step can leave a half-sent, half-edited world for the owner to repair manually. Compensating execution is the difference between an assistant that merely clicks and one that can safely own a consequential job. It is the single most useful missing action capability because it bounds damage from inevitable partial failures.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-terminal → faculty-judgement → faculty-action → faculty-perception
- **model tier:** Use a background planner to derive a typed dependency and compensation graph; use deterministic Mac/browser execution for both forward and compensating steps; use faculty-perception only for independent postconditions; reserve realtime for the concise risk summary and final outcome.
- **latency:** Planning under 5 seconds for ordinary jobs; compensation starts immediately after a failed step and should begin within 500 ms of the receipt; final classification within 3 seconds, excluding external network delays.
- **cost:** Usually one planning call and no extra model call during failure; approximately $0.02–$0.10 for complex workflows. Storage and local snapshots dominate, not inference.
- **security:** Compensation must be explicitly listed and digest-bound before approval; never invent a rollback after failure. Preserve private snapshots locally on the Mac, encrypt relay metadata, and expire them. Some external sends cannot be recalled, so those steps must be classified as irreversible and require stronger confirmation. Never claim restored when a verifier returns unknown.
- **missing:** A typed forward-step/compensation graph with irreversibility and restoration guarantees; Private, bounded Mac snapshots for files, drafts, and structured app state, plus browser draft preservation; An executor that can atomically stop downstream steps and invoke only pre-approved compensations; Outcome taxonomy and pendant haptic rendering for committed, compensated, partially restored, and unknown; Ledger correlation joining forward receipts, compensation receipts, and independent verification provenance

### "“Watch for this exact condition, and only then prepare the action for me—never act on an old observation.” For a price, availability, calendar, inbox, or webpage condition, the relay should keep a bounded watch, require fresh browser/Mac evidence at trigger time, produce a diff from the rule, and deliver a physical approval request to the pendant. If evidence is stale, contradictory, or the session changes, it expires instead of acting."
- **useful because:** The owner can delegate waiting without granting an open-ended automation that might fire hours later against a changed page or wrong account. It combines the relay's always-on reach with the browser's authenticated session while keeping the irreversible side effect behind fresh evidence and a deliberate gesture.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-judgement → faculty-action → faculty-perception
- **model tier:** Use a cheap scheduled/edge evaluator for deterministic conditions and expiry; use a background model only to translate a natural-language condition into a typed predicate; use realtime for the final concise approval prompt.
- **latency:** Condition checks on a configured cadence from 1 minute to 1 hour; once triggered, fresh evidence and an approval packet within 5 seconds. Never bypass the cadence or approval to optimize latency.
- **cost:** Low: mostly relay scheduling and browser polling; typically <$0.01 per watch hour, with model cost only at setup or ambiguity.
- **security:** Watch definitions must be scoped to one account/session/domain and expire by default. Store hashes and redacted evidence, not page contents. Never submit on trigger alone. Re-authentication, account change, or changed target invalidates the watch and alerts the owner.
- **missing:** A typed condition language with explicit freshness, scope, expiry, and side-effect policy; Relay scheduler and durable watch state with deduplication and backoff; Browser/Mac evidence adapters that return provenance and session identity at trigger time; A pendant approval envelope that includes the fresh evidence digest without secrets

### "“Use the credentials and payment details already in this browser, but do not show or transmit the secrets to the assistant; tell me exactly which site, account, amount, and non-secret fields will be used, then let me approve the final submission on the pendant.” The browser extension should perform secret-bearing field fills locally, while the planner sees only field labels and redacted value types, and faculty-perception verifies the destination and submitted result."
- **useful because:** This closes the most practical gap between a voice assistant and real authenticated work: the owner can complete purchases, applications, and account forms without copying passwords or card numbers into chat. The browser remains the secret boundary while the Mac, relay, and pendant provide planning, clear intent, and physical consent.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-judgement → faculty-action → faculty-perception
- **model tier:** Use a background planner to map the request to typed non-secret fields; deterministic browser code fills secrets from the existing session; realtime speaks only the redacted review and receives the deliberate approval.
- **latency:** Prepare the review in 3–8 seconds; final local fill/submit within 2 seconds after approval; pause immediately if origin, account, amount, or required field set changes.
- **cost:** Typically <$0.03 per form, dominated by planning and verification; browser execution and redaction are local.
- **security:** Passwords, tokens, card numbers, security answers, and page contents never enter relay/model/pendant. Browser enforces origin, account, field allowlists, and no cross-origin frame escape. Payment, legal attestation, deletion, and external submission always require fresh physical approval. If the browser cannot prove the origin or postcondition, do not claim success.
- **missing:** A browser-side secret-fill primitive that returns only typed field metadata and redacted hashes; Origin/account/amount binding between browser session, approval digest, and submission; A policy language for which secret field classes may be used and which always require confirmation; Independent post-submit verification that does not expose secret values


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing capabilities: (1) rehearsal-first execution with redacted before/after diff, digest-bound physical approval, checkpoint verification, and stop-on-drift; (2) resumable expiring action checkpoints that remain staged across sleep, browser changes, or connectivity loss and require fresh approval; (3) a physical bookmark-to-return-point flow (recorded as connective work) tying a pendant bookmark to Mac/browser/project/job context for later safe reopening. The first is the highest-value capability: it makes consequential delegation trustworthy rather than merely automated.

**Biggest unknown:** The missing implementation contracts are still cross-surface: a typed rehearsal/checkpoint envelope, per-step before-state digests and redaction rules, and durable resume reconciliation. Mac wake/unlock remains genuinely unknown, so interrupted work must stay staged until the owner explicitly resumes. The bookmark idea is close to an existing backlog entry and should be merged rather than implemented as a second bookmark mechanism.

