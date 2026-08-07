# Harness derivation — faculty-action — round 122

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“If I say ‘do this when the condition is true,’ watch the relevant private page or calendar, and execute the prepared action exactly once when the condition arrives—otherwise leave it untouched.”"
- **useful because:** This turns the hive into a dependable delayed hand: the relay waits while the Mac sleeps, the browser observes authenticated state, judgement defines a precise predicate, and faculty-action executes through the correct surface only after it is met. Useful for appointment openings, price thresholds, expiring offers, and sending a prepared reply at a specified time without polling or acting early.
- **path:** relay-realtime → browser-extension → mac-planner → mac-terminal → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Cheap background model evaluates normalized observations and predicate matches; realtime model is used only if the owner asks questions or a condition is ambiguous.
- **latency:** Observation within the configured cadence; execution within 10 seconds of a match while the Mac/bridge is online. If offline, preserve the lease and retry without duplicating the action.
- **cost:** Usually <$0.02 per observation with a small model; browser/relay storage and Mac wake/retry dominate rather than inference.
- **security:** Private page content stays on the authenticated browser/Mac path; only selected fields and a predicate hash leave for scheduling. Require a one-time owner approval over the exact action payload, expiry, and destination; never auto-send money, credentials, or irreversible messages without a fresh physical or spoken confirmation.
- **missing:** durable conditional-job schema with one-shot idempotency and expiry; authenticated browser observation scheduler; predicate evaluation against typed, provenance-bearing fields; Mac wake/reconnect and exactly-once execution lease; approval record bound to action hash

### "“Emergency privacy.” (One press on the pendant should immediately protect my Mac and browser, then tell me what it did.)"
- **useful because:** A worn button is faster and more reliable than finding a menu when a sensitive screen, logged-in tab, or conversation is exposed. The pendant event reaches the Mac over today’s USB serial bridge; the Mac locks or blanks the display, mutes audio, and asks the browser extension to hide/park private tabs. Relay records a signed receipt so the owner can later restore only what was changed.
- **path:** pendant → mac-terminal → mac-planner → browser-extension → relay-realtime → faculty-action
- **model tier:** No expensive model on the emergency path: deterministic firmware event, Mac agent policy, and browser command. Use a cheap model only to summarize the receipt afterward.
- **latency:** Local serial event to display lock/mute under 500 ms; browser tab parking best-effort under 2 s. Must work with relay unavailable.
- **cost:** Negligible API cost; implementation is local serial + OS APIs. Storage is a small encrypted action receipt.
- **security:** The physical action must be fail-safe and not expose tab URLs in the spoken confirmation. Locking is safer than trying to close tabs. Require a deliberate long-press or two-press gesture to avoid accidental activation, flash a distinct LED pattern, and support a local restore timeout only after unlock.
- **missing:** pendant-to-Mac USB serial event listener (the hardware is physically connected but not registered with relay); allowlisted local privacy policy and lock/mute primitives; browser command for hide/park private tabs; offline receipt and restore-state record; firmware gesture and LED pattern

### "“Pause this and let me pick it up later.”"
- **useful because:** For a long browser or Mac task, the owner can interrupt without losing the exact tab, extracted facts, filled-but-unsent fields, and next safe step. The relay persists a checkpoint while the browser keeps the private session, and the pendant can later announce “resume the tax form” or “discard it.” This prevents half-finished work and repeated navigation, especially when the Mac sleeps or the owner changes location.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-vision → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Cheap background model serializes and validates typed checkpoints; realtime model only interprets a spoken pause/resume/discard request.
- **latency:** Pause acknowledgement under 1 s locally; checkpoint durable within 3 s. Resume should reattach to the same tab/session within 10 s, otherwise stop and explain rather than guessing.
- **cost:** <$0.01 per checkpoint/resume for compact typed state; screenshots and page snapshots dominate storage, so retain only a bounded redacted excerpt.
- **security:** Never persist passwords, payment fields, tokens, or unrestricted page HTML. Encrypt sensitive checkpoint fields, bind them to browser session/tab identity and owner account, expire them, and require confirmation before resuming any irreversible final step. Discard must invalidate the checkpoint and clear transient browser state where possible.
- **missing:** first-class paused-job state and checkpoint schema; browser session/tab reattachment with redacted form-state extraction; Mac sleep/reconnect detection and resume lease; pendant command/status surface for pause, resume, discard; checkpoint redaction and expiry enforcement

### "“Let it handle this one task in my account, but give it no more access than this task needs—and revoke it when it’s done.”"
- **useful because:** Today the browser agent inherits a broad logged-in session, so the owner must choose between doing the work manually and granting an opaque agent too much reach. A task-scoped capability would let judgement declare exact permitted origins, fields, verbs, and expiry; the browser enforces that boundary, the relay audits it, and faculty-action can execute without exposing unrelated mail, payment data, or account settings.
- **path:** faculty-judgement → relay-realtime → browser-extension → mac-planner → faculty-action → pendant
- **model tier:** A cheap model compiles the owner's goal into a typed access manifest; realtime is used only to resolve ambiguity or obtain explicit approval for an exceptional field/action.
- **latency:** Manifest issuance under 2 seconds; each browser mutation checked locally in under 50 ms. Revocation must take effect on the next command and on reconnect.
- **cost:** <$0.01 per manifest; the dominant cost is browser-extension and authenticated-session engineering, not inference.
- **security:** The extension must deny by default and enforce origin, tab, selector/field, HTTP verb, and action-count limits rather than trusting model text. Never permit password retrieval or unrestricted DOM export. Bind the capability to an owner approval, action hash, browser session, and short expiry; show the pendant a compact scope and revoke control. A compromised Mac or relay must not be able to widen the scope.
- **missing:** browser-enforced task capability manifest and policy engine; field-level redaction and mutation gates in the authenticated extension; relay-issued signed, expiring capability tokens with revocation; Mac/action executor propagation of the token; pendant display/LED confirmation for scope and revocation


## Changes it proposed to its own stack

### `integration` — Add a local pendant serial supervisor on the Mac that owns /dev/cu.usbmodem00096003658* discovery, frames button/LED/audio-control events, authenticates the device per connection, and exposes a narrow local event stream to faculty-action. Implement a deterministic `privacy_latch` action: on the configured gesture, lock the Mac and mute output immediately, enqueue browser tab parking, and write an encrypted receipt with before/after state. Do not flash firmware; initially support a host-injected test event and the existing dev-board button protocol.
- **owner gets:** The pendant becomes a real safety switch today while USB-attached, rather than a voice-only client that fails exactly when privacy matters. It remains useful with relay, LTE, and model inference all unavailable.
- effort: Medium: serial framing/discovery, reconnect handling, local auth, macOS lock/mute allowlists, browser command, tests with simulated button frames. Firmware gesture work can follow after approval.  ·  risk: A malformed or accidental event could lock the screen or mute audio; require long-press/two-press, rate-limit, and make unlock entirely owner-controlled. If serial disappears, fail closed for privacy activation but never repeatedly lock. Recover through normal macOS unlock and an auditable receipt.
- cost: No per-call model cost; a small always-on process consumes modest CPU and <10 MB RAM. No hardware purchase; the two live USB boards are already present.  ·  latency: Local event handling target <500 ms; browser parking is asynchronous and may take ~2 s.
- security: Treat the serial device as an authenticated control plane, not arbitrary USB input. Keep receipts local/encrypted, omit URLs and secrets from spoken output, and require explicit gesture configuration.
- depends on: Owner-approved local serial protocol and test event format; Allowlisted lock/mute and browser tab parking operations; Pending physical-action confirmation policy, if privacy action is expanded beyond lock/mute

### `browser-harness` — Introduce a deny-by-default, task-scoped capability broker between faculty-judgement and the authenticated browser extension. It should compile a signed manifest (allowed origins, tab/session, read selectors, writable fields, verbs, maximum mutations, expiry, and action hash), enforce it inside browser_run_actions and the extension—not merely in prompts—and emit a proof for every allowed/denied command. Revocation must propagate through the relay and invalidate queued Mac/browser work.
- **owner gets:** The owner can delegate a narrowly defined job without handing the AI an all-access logged-in browser. Unrelated private pages remain inaccessible even if the model makes a mistake or a queued task is replayed later.
- effort: High: extension enforcement, signed token format, relay revocation, typed action plumbing, redaction tests, and adversarial tests against selector/URL confusion and replay.  ·  risk: Overly narrow manifests could make legitimate tasks fail; default should be a clear deny with an edit-and-reissue flow. A bug in enforcement could create false confidence, so ship audit-only shadow mode first and visibly label it until conformance tests pass.
- cost: No meaningful per-request model cost; modest relay/extension CPU and storage for manifests and proofs.  ·  latency: Under 50 ms local policy check per browser command; a few hundred milliseconds for issuance/revocation.
- security: Substantially reduces blast radius from prompt injection, compromised tabs, and stale queued jobs. Secrets, passwords, unrestricted DOM, and capability escalation must be structurally unavailable.
- depends on: A typed action schema shared by browser_run_actions and Mac execution; Relay signing key and revocation endpoint; Extension-side enforcement hooks for navigation, extraction, click, type, and submit; Owner-visible scope/approval UI or pendant gesture


## What it asked for

_Nothing._
## Its own summary

Round 122 produced three new cross-surface capabilities and one concrete integration: one-shot conditional actions over authenticated pages; a pendant emergency privacy latch; pause/resume of browser and Mac work with redacted checkpoints; and a Mac USB-serial supervisor that makes the physically connected pendant a deterministic privacy switch without flashing it. The strongest immediate owner benefit is emergency privacy: it works offline and on the hardware that is live today.

**Biggest unknown:** The exact USB serial framing and button-event protocol in the current firmware, plus the owner's acceptable gesture and whether browser tab parking should be enabled after the immediate Mac lock/mute. I still need an approved local serial test protocol and the missing durable checkpoint/conditional-job primitives before these can be implemented safely.

