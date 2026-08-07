# Harness derivation — faculty-action — round 103

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Do the approved plan even if I leave the conversation: carry it out across my Mac and logged-in browser, but only while the facts it depends on are still true; stop safely on any mismatch and tell me exactly what happened.”"
- **useful because:** Today judgement can decide a multi-surface action, but execution is brittle when the voice session ends or a page changes. This gives the owner dependable follow-through without silently acting on stale information: the Mac can perform local work, the browser can use private sessions, the relay can keep the job alive, and the pendant can report completion or a blocked step.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → faculty-judgement → faculty-perception
- **model tier:** Use the realtime tier only to capture the approval and concise status; use a cheaper background model for plan compilation, precondition re-checks, retries, and final receipt summarization.
- **latency:** Acknowledge approval in under 1 second; begin execution within 5 seconds; individual checks under 3 seconds; long jobs continue asynchronously and may take minutes. A stale or ambiguous precondition must stop rather than wait indefinitely.
- **cost:** Roughly $0.01–$0.08 per job depending on number of browser pages and retries; most cost is background extraction and final summarization, not the short voice acknowledgement.
- **security:** Private browser content and local Mac state leave their respective devices only to the authenticated relay/context projection. Never send or submit irreversible changes without a fresh explicit approval token. Bind each step to tab/session, URL, expected evidence hash, and an expiry; redact secrets from receipts; support cancellation and idempotent retry.
- **missing:** A durable cross-surface job schema carrying preconditions, approval token, deadline, and compensation/cancellation state; A runner that can re-check evidence before every step and stop on mismatch; A single pendant/voice status and completion channel for jobs after the original conversation ends; Browser-online availability and owner-granted Accessibility/Screen Recording for GUI-only steps; AppleScript paths should remain the fallback


## Changes it proposed to its own stack

### `relay` — Add a precondition-and-lease gate between /plan and /execute. Every executable step must declare the evidence it requires (resource identity, expected state hash or typed predicate, freshness TTL, and whether the step is reversible). The relay re-reads that evidence immediately before dispatch, atomically consumes a short-lived owner approval lease, and emits one of proceed, blocked-stale, blocked-ambiguous, expired, or cancelled. A later step cannot run after an earlier mismatch; receipts must include the evidence used for the decision, not merely the action result.
- **owner gets:** The owner gets the safety of saying “yes” once without the system turning an old plan into a surprising action after a page, calendar event, or local file changes. If execution is interrupted, they can see whether it completed, stopped before mutation, or needs a fresh approval—and safely resume without duplicate actions.
- effort: Medium: typed schema and state machine in relay, adapters for Mac/browser evidence reads, and tests for expiry, duplicate delivery, cancellation, and partial completion.  ·  risk: A predicate that is too strict may block harmless work; one that is too weak could allow stale actions. Default to blocking, make the reason explicit, and retain the existing receipts/undo path for recovery. If the relay crashes, leases expire and no step proceeds until re-approved.
- cost: Negligible API cost; one lightweight evidence read per step plus occasional cheap background classification. Storage is small per job (predicates, hashes, timestamps, decision records).  ·  latency: Adds roughly 0.5–3 seconds per step for evidence checks; avoids much longer recovery from wrong actions.
- security: Improves security by limiting approval scope and lifetime, binding actions to the intended tab/resource, and keeping sensitive evidence local/redacted. Requires careful protection of approval tokens and no secrets in logs.
- depends on: Durable job runner across /execute and /jobs; Typed browser and Mac evidence results with session/tab affinity; Owner-facing cancellation and fresh approval prompt on the pendant/relay; Do not depend on Accessibility: use AppleScript and structured browser reads where available; mark GUI-only steps blocked until the owner grants TCC

### `integration` — Build a cross-surface outcome reconciler for actions whose truth is only visible after the mutation: model each approved goal as a transaction with an intended outcome, a set of independent confirmation queries, and a deadline. After Mac or browser execution, query the other relevant surface (for example, verify a locally-created calendar item appears in the authenticated calendar, or verify a submitted browser form produces the expected confirmation message), compare the observed state to the intended outcome, and classify the job as confirmed, partially completed, contradicted, or unverifiable. On contradiction, stop further dependent work and present the owner with the exact divergent fields and a suggested recovery plan; never claim success from an HTTP/UI click alone.
- **owner gets:** The owner can ask the mind to make real arrangements and trust that it will tell them whether the world actually reflects the decision—not merely that one interface accepted a click. This is especially valuable for bookings, calendar changes, and messages where a Mac action and a logged-in web service can disagree or fail after submission.
- effort: High: a typed outcome schema, per-service confirmation adapters, correlation IDs across Mac/browser/relay, delayed polling with deadline handling, and tests for duplicate confirmations, contradictory state, and partial success.  ·  risk: Some services expose delayed or inconsistent views, producing unverifiable results or false contradiction. Default to honest “unverified,” use bounded retries, preserve raw evidence and timestamps, and require owner confirmation before any compensating mutation.
- cost: Moderate background API cost: typically 2–5 cheap confirmation reads per transaction, with realtime used only to report the result. Storage is small outcome/evidence records, not page contents.  ·  latency: Adds seconds to minutes after execution depending on external propagation; the owner gets an immediate “submitted, verifying” status and a later confirmed/blocked result.
- security: Confirmation reads may touch private browser accounts. Keep data scoped to the job, redact message/page contents from shared receipts, bind every query to the originating authenticated session, and expire evidence after the configured retention period.
- depends on: A durable cross-surface correlation ID carried through /execute, Mac actions, browser actions, and job receipts; Structured confirmation adapters for Calendar/Mail and authenticated browser pages; A relay scheduler capable of delayed verification after the original voice session ends; Owner-visible status and explicit confirmation before any recovery or compensating action


## What it asked for

_Nothing._
## Its own summary

I recorded a new relay-layer precondition/approval-lease gate: before every Mac or browser step, re-check typed evidence, consume a short-lived approval lease, and stop with a structured blocked-stale/ambiguous result rather than acting on stale plans. I also recorded the cross-surface “continue after I leave” capability, explicitly noting that the missing connective runner—not the existing /plan, /execute, jobs, receipts, and undo routes—is the gap. Current reachable state remains Mac bridge online, browser offline, pendant absent.

**Biggest unknown:** I still need a live browser session and a registered pendant to verify end-to-end handoff and owner-facing completion. For action gating, I also need stable typed evidence (resource identity, freshness, and state hash/predicate) from Mac/browser adapters; Accessibility/Screen Recording remains owner-blocked for GUI-only actions, so AppleScript/structured browser reads must be used where possible.

