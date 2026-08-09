# Harness derivation — faculty-action — round 211

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live execution readiness** — As of 2026-08-08T23:17Z, Mac agent is ready with Accessibility, Screen Recording, and all listed automation grants; browser extension is online with Safari session bound, 3 tabs, zero pending commands, and ~1 second staleness. Relay is reachable and Mac bridge online.
  - evidence: GET /ops/status and GET /browser/status returned HTTP 200; permissions.ready=true, browser.online=true, pendingCommands=0.

## Capabilities it proposed

### "“Handle this purchase, but stop if the total, seller, shipping address, or final button differs from what I said.”"
- **useful because:** This is the highest-value trustworthy action: the browser can fill a real checkout while the pendant remains the owner’s physical veto. It combines spoken constraints, browser-held credentials, Mac execution, independent postcondition checks, and a final physical approval without exposing secrets to the pendant.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-judgement → faculty-action → faculty-perception
- **model tier:** Use the realtime model only to extract the owner’s constraints from the live utterance; use the cheaper background planner for browser steps; use faculty-perception for deterministic field and URL checks; use faculty-action for execution and commit.
- **latency:** Stage the cart in 5–15 seconds; pause at the final submit boundary until the pendant’s deliberate approval; verify within 2 seconds after submit.
- **cost:** One realtime turn plus 1–3 cheap planner/perception calls; roughly $0.02–$0.10 depending on page complexity. Browser screenshots and secret fields dominate latency, not token generation.
- **security:** The pendant receives only a redacted summary, amount, merchant, address hash, and transaction nonce—not credentials, card data, or page contents. Never submit if a constraint is unknown or changed. Require explicit approval for the irreversible step; report unknown rather than success if independent verification cannot establish the result.
- **missing:** A structured constraint object shared from judgement to browser planning (merchant, amount tolerance, destination/address identity, shipping deadline, forbidden changes).; Browser-side final-submit boundary that can pause before the irreversible click and return a stable command ID.; A post-submit verifier adapter for merchant order confirmation, with proof that does not retain payment secrets.

### "“For the next two weeks, accept routine calendar invites from my team during work hours, but ask me about anything outside those rules.”"
- **useful because:** It turns the system from a one-shot remote control into a bounded delegate without giving it an open-ended mandate. The Mac can monitor and act while the browser and calendar sessions stay private; the relay wakes for exceptions, and the pendant is used only when a rule boundary or ambiguity needs the owner.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-judgement → faculty-action → faculty-perception
- **model tier:** Background model compiles the spoken policy into a typed rule set; cheap scheduled evaluation handles routine events; realtime is reserved for an exception conversation; faculty-perception verifies the resulting calendar state.
- **latency:** Routine events handled in under 10 seconds without waking the owner; exceptions surfaced within one minute; approval response can wait for the owner and expire safely.
- **cost:** Low: event-triggered rule evaluation and occasional verification, usually under $0.01 per routine event; exception conversations are the dominant cost.
- **security:** Policies must be narrow, expiring, and inspectable: actor/domain, event type, time window in America/New_York, allowed mutations, and a hard action count/rate limit. Never infer a policy from a prior approval. Store a policy hash and emit a receipt for every automatic action. Send only redacted event summaries to the pendant; require physical approval for actions outside policy or with external messaging effects.
- **missing:** A versioned policy store and compiler with explicit deny-by-default semantics and expiry.; An event trigger for new calendar/browser items and an idempotency key per event.; A policy evaluation receipt that faculty-action can bind to execution and independent postcondition verification.

### "“The site timed out after I clicked—find out whether it went through, and fix it without creating a duplicate.”"
- **useful because:** Ambiguous completion is where automation causes real harm: retrying can double-order, double-send, or double-book. This capability makes the action agent useful after failure, using independent browser and Mac evidence to reconcile state before taking a compensating action.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-action → faculty-perception → faculty-judgement
- **model tier:** Use a cheap background recovery planner to enumerate evidence sources and safe reconciliation options; use faculty-perception for fresh read-only checks; use realtime only to explain the final options; faculty-action performs only an approved compensating step.
- **latency:** Begin investigation immediately after an unknown receipt; return a first status within 10 seconds and a bounded recovery plan within 30 seconds. Never auto-retry an irreversible operation.
- **cost:** Usually $0.01–$0.05 for several read-only inspections; browser evidence collection and page navigation dominate. A human approval is required only if compensation is needed.
- **security:** Bind every inspection to the original operation ID and idempotency key. Search only the relevant merchant/account/session, redact credentials and unrelated history, and preserve hashes plus timestamps rather than dumping pages. Distinguish confirmed-complete, confirmed-not-complete, duplicate, and unknown. Any cancellation, refund, resend, or deletion requires a fresh physical approval.
- **missing:** A recovery state machine with explicit terminal states and no-retry invariants.; Service-specific reconciliation adapters (order status, sent-mail identity, calendar event identity) that can query without mutating.; A durable operation journal linking executor receipts to verifier evidence and compensating-action approvals.

### "“Revoke every action I authorized today, everywhere, and tell me what could not be stopped.”"
- **useful because:** The owner needs a true emergency brake across the hive, not a separate cancel button per job. One spoken command should invalidate pending leases at the relay, stop queued Mac/browser work, prevent stale approvals from being reused, and return a truthful inventory of already-committed versus successfully halted actions.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-action → faculty-perception → faculty-judgement
- **model tier:** Realtime interprets the urgent command; a deterministic relay revocation service fans out cancellation; faculty-action performs only reversible stops; faculty-perception independently verifies queue, browser, and Mac state. Use a cheaper background model to summarize the final inventory.
- **latency:** Invalidate relay-side authority immediately (<1 second); fan out stop requests within 3 seconds; return a verified partial result within 10 seconds, with late surfaces marked unknown rather than claimed stopped.
- **cost:** Low per invocation, roughly $0.01–$0.05; the cost is dominated by fresh state checks across Mac and browser, not generation.
- **security:** Revocation must be authenticated to the paired pendant and monotonic, invalidate all unexpired approval nonces and policy leases, and be idempotent. It must not falsely promise cancellation after an irreversible commit. The pendant receives only action IDs, risk labels, and outcomes—not page contents or secrets. Any compensating action still requires a new explicit approval.
- **missing:** A globally ordered revocation epoch propagated by relay, Mac agent, and browser extension.; Cancellation endpoints for queued and in-flight Mac/browser commands, with race-safe acknowledgement semantics.; A cross-surface inventory that distinguishes pending, halted, committed, and unknown, independently verified after the revoke.; Firmware behavior for an offline emergency revoke that queues the signed revoke epoch until the link returns.


## What it asked for

_Nothing._
## Its own summary

Recorded three non-duplicate capabilities: (1) constraint-bound purchase execution with browser-held secrets, independent field verification, and a final pendant approval; (2) expiring, rate-limited bounded delegation for routine calendar actions with exception escalation; and (3) unknown-outcome recovery that reconciles state before retrying and prevents duplicate orders/messages/bookings. Fresh inspection shows the Mac agent and browser are genuinely ready now: Accessibility/Screen Recording and automation grants are live, Safari bridge online, zero pending commands, relay reachable.

**Biggest unknown:** The missing pieces are implementation contracts, not host readiness: a typed constraint/policy schema, browser final-submit pause plus idempotency key, service-specific read-only reconciliation adapters, and a durable journal joining executor receipts to independent verification and compensating approvals. The pendant itself remains unregistered, so physical approval cannot yet be exercised end-to-end over LTE; USB remains bench-only.

