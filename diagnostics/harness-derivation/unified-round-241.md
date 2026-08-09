# Harness derivation — unified — round 241

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Watch my USPS tracking page and tell me on the pendant when the delivery status, estimated date, or exception changes—show me the exact before/after evidence, not a guessed summary.”"
- **useful because:** The browser already holds the authenticated USPS session, while the pendant can surface an alert when the Mac is unattended. This turns a private page the relay cannot log into into a durable, evidence-backed physical notification. It is useful today with the live Safari extension and 5 tabs, without requiring Accessibility.
- **path:** browser-extension → mac-planner → relay-realtime → unified → pendant
- **model tier:** background for periodic page comparison; realtime only to phrase the short pendant alert after a confirmed diff
- **latency:** Poll on a configurable schedule (default 15 minutes); alert within one polling cycle, with under 2 seconds for diff extraction and relay enqueue
- **cost:** Low: one browser inspection and compact structured diff per poll; background model only on a confirmed change, typically <$0.01/change
- **security:** Bind the watcher to an exact tab/session URL pattern and page region; store hashes and selected fields, not page HTML or credentials. Require explicit confirmation before creating the watcher. If the tab disappears or the URL changes, pause rather than follow a new login page.
- **missing:** A durable watcher record and scheduler binding to a specific browser session; A canonical field extractor/diff format for tracking status, ETA, and exception text; An integration that converts a confirmed diff into the existing pendant inbox alert with acknowledgement

### "“Fill out this authenticated web form, but do not submit until you read me the exact fields and values on the pendant and I approve that specific transaction with the pendant button.”"
- **useful because:** This is the safest way to make the browser genuinely useful for consequential work: the browser performs the private, authenticated interaction; the Mac/relay create a digestible preview; the pendant is an independent physical consent boundary. It prevents the current failure mode where an action is described as awaiting approval but is actually discarded, while keeping secrets and page contents off the pendant.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → unified
- **model tier:** planner/background to extract and summarize the form; realtime only for the short readback and approval conversation
- **latency:** Preview in 3–8 seconds; hold submission indefinitely until physical approval or a 20-minute expiry; submit and receipt within 5 seconds after approval
- **cost:** Usually <$0.03 per form, dominated by one planner call and browser round trips; no model call after an unchanged preview is approved
- **security:** Never send passwords, payment secrets, or full page HTML to the pendant or relay. Bind approval to a hash of target origin, form fields, normalized values, and expiry; invalidate it on any DOM/value/world change. Use the existing physical transaction nonce and require a fresh deliberate hold; cancellation and expiry must be explicit and auditable.
- **missing:** Wire the existing formPreview prepare/approve flow to browser actions instead of discarding awaitingApproval; Implement relay persistence and pendant delivery for the existing approval handoff contract; A browser-side submit action that accepts only the approved digest and returns a structured receipt; A distinct authorization boundary so approval is not equivalent to the Mac bearer token

### "“My pendant is silent—tell me whether the fault is the pendant, audio link, relay, Mac, or browser, run only safe repairs, and prove with a fresh end-to-end check that it is working before you say it’s fixed.”"
- **useful because:** Today a silent pendant produces a vague timeout and repeated retries. This gives the owner one diagnosis spanning the physically distinct nodes, then performs only allowlisted idempotent recovery and revalidates the audio path. It can distinguish a browser bridge outage from a codec/link failure instead of restarting the wrong component.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** background/deterministic for snapshot correlation and repair selection; realtime only to explain the result over voice
- **latency:** Initial correlated snapshot in 2 seconds; safe repair in under 15 seconds; fresh audio validation within 30 seconds. Never claim success without a post-repair receipt.
- **cost:** Low: mostly read-only health routes and one bounded validator; <$0.02 per invocation, with no large audio upload unless the owner explicitly requests artifacts
- **security:** Repairs must be restricted to the existing enum and require an idempotency key; never mutate browser content or send audio during diagnosis. Redact page URLs, tokens, and audio artifacts by default. A failed revalidation must be reported as failed or partially recovered, not converted into a conversational success.
- **missing:** A single orchestrator that correlates incident_diagnostics output with audio_pipeline_validate and fleet_health_and_repair; A device-side authenticated health/event snapshot when LTE is absent, with clear stale-data timestamps; A post-repair audio fixture trigger and receipt that verifies both downlink hearing and uplink capture; Owner-facing severity and escalation policy for repairs that remain unresolved

### "“I’m stepping away—freeze every action this system could take for me across the pendant, relay, Mac, and authenticated browser; let nothing execute or expose a page until I physically unlock it, then show me everything that was blocked.”"
- **useful because:** The current privacy latch stops local capture/playback, but it does not establish that queued Mac jobs, relay work, or browser commands are unable to proceed while the owner is away. This gives the owner a single, physical, cross-surface agency boundary: silence and privacy are coupled to prevention of delegated actions, with a resumable audit of blocked work rather than silent expiry or accidental execution.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** deterministic state machine for entering, enforcing, and clearing the freeze; background model only to summarize blocked jobs on unlock
- **latency:** Pendant-local capture/playback stop immediately; relay/Mac/browser enforcement within 1 second of the state event; unlock report within 3 seconds
- **cost:** Negligible per transition; bounded state records and receipts, with <$0.01 for an optional unlock summary
- **security:** The freeze event must be authenticated, monotonic, durable across link loss, and fail closed when stale. Existing queued commands need cancellation or a non-executable hold state; browser sessions must receive an explicit deny mode rather than relying on tab closure. Unlock must require the physical latch and a fresh state nonce. Do not claim that already-completed external actions were prevented; report their exact cut-off times.
- **missing:** A cross-surface agency-freeze state machine and durable epoch/nonce; Relay job and routine workers that honor a freeze epoch and hold or cancel queued work; Mac executor and browser bridge guards checked immediately before dispatch, not only at planning time; A pendant event and receipt protocol extending local_privacy_latch without mixing audio privacy and agency state; An unlock report joining blocked, cancelled, and completed-before-freeze receipts


## Changes it proposed to its own stack

### `integration` — Connect browser form previews to the existing action-bound approval machinery end to end: browser inspect creates a normalized preview digest, relay persists the pending record with TTL, the pendant receives only a redacted spoken summary plus nonce, its physical approval event grants exactly that digest, and browser submit is permitted only after digest/world revalidation. Return one receipt linking preview, physical decision, submit result, and undo availability.
- **owner gets:** The owner can safely delegate real authenticated web work instead of receiving promises that an approval is waiting somewhere. A single deliberate button hold becomes meaningful consent, and a changed page or expired preview fails closed.
- effort: High: browser adapter, relay approval persistence, pendant delivery/event plumbing, and receipt joins; roughly 1–2 weeks plus hardware/link tests.  ·  risk: A digest canonicalization bug could approve the wrong value; mitigate with field-by-field readback, origin binding, expiry, world fingerprint, and mandatory fail-closed tests. If delivery fails, leave the preview pending rather than submitting.
- cost: Low per use; one planner call and small D1 records. No page secrets or audio need leave the Mac.  ·  latency: Preview 3–8 s; physical approval immediate; submit receipt 1–5 s after approval.
- security: Materially improves security by separating bearer-token execution from physical consent, but requires a real authorization boundary and nonce replay protection.
- depends on: Relay implementation of shared approvalHandoff contract; Pendant delivery path for staged approval/readback and physical_transaction_approval_latch event; Browser submit action that enforces approved digest and world fingerprint; A distinct approval credential or capability token rather than reusing the Mac AGENT_TOKEN


## What it asked for

_Nothing._
## Its own summary

This round produced three new owner-facing capabilities and one implementation change: evidence-backed USPS page-change alerts to the pendant; authenticated form completion gated by a digest-bound physical pendant approval; and cross-surface silent-pendant diagnosis with safe repair plus post-repair audio validation. The highest-value item is the form approval loop, because it turns the existing physical transaction latch and browser bridge into real, fail-closed consent rather than a spoken dead end. I also proposed wiring that loop end to end.

**Biggest unknown:** I still need the relay-side implementation of the existing approvalHandoff contract, a real staged-approval delivery path to pendant firmware (including the physical approval event), and a browser submit primitive that enforces the approved digest/world fingerprint. I do not need another general discovery pass; those are the concrete blockers. The orchestrator should also decide the separate authorization boundary so approval is not equivalent to the Mac bearer token.

