# Harness derivation — faculty-action — round 191

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Start this job, but let me stop it from the pendant if I change my mind.”"
- **useful because:** Long Mac/browser jobs currently have approval before execution but no owner-controlled interrupt once a multi-step run is underway. The owner gets a real emergency brake: a deliberate pendant gesture cancels at the next safe checkpoint, while already-completed steps remain auditable and no later irreversible step starts.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** background planner for checkpoint planning; realtime only for the pendant cancel event; no LLM in the cancellation path
- **latency:** Cancel signal reaches the relay in under 1 s when connected; executor checks before every step and within 2 s; if disconnected, the pendant queues the cancel decision for the operation expiry.
- **cost:** Low API cost after planning: one relay event and job cancellation per request; dominant cost is the existing planner and browser execution, not the cancel path.
- **security:** Cancel is fail-safe and never authorizes work. The pendant receives only an opaque operation ID, expiry, and risk summary—not page contents or secrets. A stale, replayed, or digest-mismatched cancel is refused. The executor must stop before the next side effect and return a partial receipt.
- **missing:** A cooperative checkpoint contract in Mac/browser executors that makes POST /jobs/:jobId/cancel stop before the next side effect; A relay operation stream carrying signed pendant cancel events and binding them to an operation nonce; Dashboard rendering of partial completion and the exact next step that was prevented

### "“The connection dropped—figure out whether that went through, then continue only if it is safe.”"
- **useful because:** A dropped link leaves the worst state: the owner cannot tell whether a message, purchase, or browser submission happened. This capability freezes the operation, asks the independent perception layer to inspect fresh Mac/browser state, classifies the result as verified, definitely-not-done, or unknown, and resumes only from an idempotent checkpoint when evidence proves it is safe.
- **path:** relay → mac-planner → mac-vision → browser → pendant → dashboard
- **model tier:** cheap background recovery state machine; perception model only for ambiguous visual state; realtime is not needed unless the owner is actively speaking
- **latency:** Freeze immediately; first state check within 5 s of reconnection; owner-facing result within 15 s, with unknown preserved rather than guessed.
- **cost:** Usually a few read-only route calls; visual ambiguity dominates cost and is invoked only when structured app/browser state cannot establish the postcondition.
- **security:** No automatic retry of non-idempotent steps. Each checkpoint carries an operation digest, idempotency key, and postcondition. Fresh verification provenance is retained. Unknown is a terminal state until the owner explicitly chooses a recovery branch; secrets never enter the pendant or relay event.
- **missing:** A durable operation/checkpoint state machine shared by relay, Mac, and browser; A declared idempotency/postcondition schema for every side-effecting executor step; A resume API that accepts only a verified checkpoint and emits a new receipt chain

### "“I have several things waiting—read me the pending actions and let me choose one with the wheel.”"
- **useful because:** A bounded approval queue is safe but unusable when more than one operation is pending: the owner cannot know which nonce a button gesture would affect. A rotary encoder gives the jewellery pendant a private, deterministic selector; short spoken summaries play through the existing 24 kHz downlink, and only the selected item can be approved or cancelled.
- **path:** pendant → relay → mac-planner → browser
- **model tier:** background model produces a <=12-word redacted summary at staging time; pendant firmware handles selection and gesture logic locally; no realtime model is needed
- **latency:** Wheel selection feedback under 100 ms locally; summary playback starts under 1 s when audio is available; selection and approval remain queued safely through a link drop.
- **cost:** One small summary-generation call per staged operation; negligible relay traffic and no per-tick model calls.
- **security:** The pendant receives only risk class, expiry, operation digest, and a redacted human summary—never page content, form values, or secrets. Selection changes focus but never approves. Approval requires the existing deliberate gesture on the selected digest; expired, consumed, or digest-mismatched entries are refused.
- **missing:** Rotary encoder hardware integration in the product enclosure and firmware input driver; An ordered pending-operation inbox protocol with selected-index persistence and signed summaries; A relay endpoint to acknowledge focus/selection without treating it as consent

### "“Before you change anything, show me exactly what will be different across my Mac and browser, and let me approve that diff.”"
- **useful because:** Today previews are surface-specific and an owner cannot inspect one coherent consequence set when a request spans a local file, a browser form, and an account-side effect. This gives the owner a redacted, ordered before/after diff and a single approval over the whole transaction, rather than approving an opaque plan or discovering collateral changes afterward.
- **path:** pendant → relay → mac-planner → mac-vision → browser → dashboard
- **model tier:** background planner builds a structured diff; realtime is unnecessary; perception is used only to establish before-state for visual-only browser controls
- **latency:** Diff available within 5 seconds for structured state and 15 seconds when screenshots are required; approval remains valid only for a short digest-bound lease.
- **cost:** One planning call plus read-only state collection; screenshot perception is the dominant cost and runs only for controls without structured selectors.
- **security:** Diffs are redacted by sensitivity class and never sent to the pendant in raw form. Approval binds to exact before-state hashes, target identities, and intended mutations; any drift invalidates it and forces a fresh diff. No mutation occurs during preview.
- **missing:** A cross-surface before/after diff schema with sensitivity and hash fields; Read-only snapshot adapters for Mac and browser state that expose proposed mutations without executing them; A pendant-friendly summary/audio rendering and digest-bound approval envelope

### "“Remember this rule: never submit a form or send a message unless the recipient, amount, and destination match what I said.”"
- **useful because:** A physical approval gesture proves the owner approved a staged operation, but it does not protect against a planner misunderstanding a name, amount, or destination. The owner should be able to state durable semantic invariants once; Mac and browser executors enforce them immediately before mutation and refuse with the mismatching field highlighted.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** background model compiles natural-language rules into a typed constraint; deterministic executor checks enforce it; realtime is only for reading the refusal aloud
- **latency:** Constraint checks add under 200 ms when fields are structured; visual extraction may take up to 3 seconds. Refusal is immediate and never waits for an LLM retry.
- **cost:** Small one-time model call to compile or revise a rule; deterministic checks are effectively free; visual field extraction dominates exceptional cases.
- **security:** Rules are scoped by action class and destination, versioned, and fail closed when a field is missing or ambiguous. Secrets are compared locally where possible and never copied to the pendant. A rule cannot silently broaden its scope; changing it requires explicit owner confirmation.
- **missing:** A typed invariant language covering recipients, amounts, domains, files, and account identities; Pre-mutation enforcement hooks in every Mac and browser executor; A safe rule-management UI and signed rule-version reference in operation receipts

### "“When I press the bookmark button, save what I was looking at on the Mac too, so I can find it later.”"
- **useful because:** The existing pendant bookmark can mark a moment, but a moment without the active Mac/browser context is hard to recover. A single physical press should atomically correlate the pendant event with the freshest foreground app, browser tab URL/title, and a privacy-filtered selection or file identity, then let the owner retrieve the exact moment later—even if the link was briefly down.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** deterministic host snapshot and correlation; background model optionally labels the bookmark; no realtime model required
- **latency:** Capture the pendant event locally immediately; Mac/browser correlation within 2 seconds; if unavailable, retain the event and attach context when the next fresh heartbeat arrives.
- **cost:** Negligible relay/storage cost for metadata; optional labeling is one cheap background call per bookmark.
- **security:** Never capture page bodies, passwords, or arbitrary clipboard contents. Store URL/title only under a sensitivity policy, hash private identifiers, and visibly mark when context was stale or unavailable. The bookmark is data, not permission to execute an action.
- **missing:** A signed correlation protocol joining pendant monotonic bookmark IDs to host/browser observation timestamps; Privacy-filtered active-context adapters for Safari, native apps, and Finder; A retrieval view that explains freshness and missing context instead of implying exact simultaneity


## What it asked for

_Nothing._
## Its own summary

I discovered a materially changed live system: /ops/snapshot reports Accessibility and Screen Recording granted, all required automation grants present, relay reachable, and Safari browser bridge online with a live DoorDash tab. The pendant itself is still absent from the relay device table and remains unregistered; USB remains bench-only. I recorded three non-duplicate capabilities: (1) a pendant emergency stop that cancels a running Mac/browser job at a safe checkpoint, (2) truthful recovery after a link drop that independently verifies state and resumes only from an idempotent checkpoint, and (3) a rotary-selected pending-action inbox so multiple approvals are intelligible and cannot target the wrong nonce. What I still need is not TCC access: I need a cooperative checkpoint/cancel contract in the Mac and browser executors, a durable operation/idempotency schema shared with relay and perception, and the rotary encoder driver plus signed pending-summary protocol. The highest-value missing behavior is unknown-outcome recovery; it prevents duplicate submissions when the owner cannot know whether an action already happened.

**Biggest unknown:** The pendant is physically on the bench per owner context but has no relay registration/device-table presence, so I cannot yet validate signed cancel/selection events over the real wearable link or measure their offline queue behavior.

