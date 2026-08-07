# Harness derivation — faculty-action — round 34

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“If a website needs me to sign in, approve a device, or solve a CAPTCHA while you’re doing the task, pause there, tell me exactly what to do, and continue automatically when I’m back in.”"
- **useful because:** Today an otherwise correct cross-device job fails or risks exposing credentials when a private site presents 2FA, passkey approval, CAPTCHA, or a re-auth screen. The browser is the only surface with the session; the pendant is the only surface guaranteed to reach the owner. A bounded handoff lets the owner satisfy the challenge without dictating secrets, then resumes the exact task with evidence and no duplicate submission.
- **path:** relay-realtime detects a typed auth-challenge event and gives a short pendant prompt with a one-time task code → browser-extension pauses the bound tab/session before mutation, records challenge type and URL/origin, and waits for completion → mac-planner owns the durable job/checkpoint and resumes only when the same tab/session reports authenticated continuity → faculty-action executes the remaining typed steps and emits a receipt; pendant button can cancel and trigger cleanup → dashboard shows challenge history, expiry, and whether the job resumed or was abandoned
- **model tier:** Cheap background planner/state machine for detection, checkpointing, and resume; realtime only for the concise pendant prompt and owner reply. No model should be given passwords, OTPs, or page secrets.
- **latency:** Challenge detection under 1 second; pendant prompt under 2 seconds; after owner completes the challenge, resume within 3 seconds. Challenge leases expire after 5 minutes by default and require a new prompt.
- **cost:** About $0.001–$0.01 per job, usually zero extra model calls; cost is dominated by durable browser polling and receipt storage, not inference.
- **security:** Never transmit credentials, OTP values, passkeys, or CAPTCHA contents to the relay/model. Verify origin, tab/session binding, and a nonce; reject unexpected navigation and stale completion signals. Require explicit owner button press to resume, and require a fresh approval at the final irreversible step. On timeout/cancel, clear sensitive form fields where possible and leave an auditable receipt.
- **missing:** Typed browser auth_challenge and auth_resolved events with origin, tab/session id, nonce, and expiry; Durable checkpoint/resume state machine with idempotency keys and duplicate-submit protection; Browser extension UI to show a local-only challenge banner and report completion without contents; Pendant prompt/button protocol for challenge handoff and cancel; Planner/action adapters for passkey/device approval, OTP entered locally, CAPTCHA, and re-auth flows

### "“When you reach a login checkpoint during a task, hand it to me privately, then continue from exactly where you stopped without asking me to reveal the code or start over.”"
- **useful because:** A private-site task should not fail merely because the site requires a passkey, 2FA, CAPTCHA, or re-authentication. The browser is the only place holding the session, while the pendant is the only surface guaranteed to reach the owner. This gives the owner a secure local handoff and preserves the task's progress without leaking credentials to the model.
- **path:** browser-extension detects and freezes at an authentication challenge, bound to the exact origin, tab, and session → relay-realtime sends a redacted challenge prompt to the pendant only → pendant displays the challenge kind and offers signed continue/cancel button actions; secrets remain local to the browser → mac-planner persists the checkpoint and resumes the same job only after matching nonce/origin/session resolution → faculty-action executes the remaining steps and writes a receipt; dashboard shows expiry, resume, abort, and cleanup state
- **model tier:** A cheap deterministic state machine handles challenge detection, checkpointing, nonce validation, and resume. Realtime is used only for the short pendant prompt; no model receives the secret or challenge contents.
- **latency:** Detect and notify within 2 seconds; resume within 3 seconds after the owner completes the local challenge. Expire the handoff after 5 minutes or any unexpected navigation.
- **cost:** Roughly $0.001–$0.01 per task, generally no additional inference; durable browser polling and event/receipt storage dominate.
- **security:** OTP, passkey, password, and CAPTCHA contents must never leave the browser or be placed in model context. Bind the handoff to origin, tab/session, job, nonce, and expiry; require an explicit pendant action to continue; use idempotency keys to prevent duplicate submission; cancel and clear sensitive fields on timeout where possible; require separate approval for the final irreversible step.
- **missing:** A typed auth_challenge/auth_resolved protocol across browser bridge, relay, Mac runner, and pendant; Durable checkpoint/resume state machine with idempotent continuation and cleanup; Browser-local challenge banner and completion signal that carries no secret contents; Pendant signed continue/cancel interaction and local challenge status display; End-to-end tests for passkey, 2FA, CAPTCHA, re-auth, timeout, navigation, and duplicate-submit cases


## Changes it proposed to its own stack

### `integration` — Add a challenge-aware execution protocol shared by browser bridge, Mac job runner, relay, and pendant: jobs become checkpointed state machines; the browser emits auth_challenge {jobId, tabId, sessionId, origin, kind, nonce, expiresAt} before any mutation, relay presents only a redacted prompt, the pendant returns signed approve/cancel for that nonce, and browser emits auth_resolved without secret contents. Resume requires same tab/session/origin, a fresh idempotency key, and a final receipt; timeout or navigation invalidates the lease and invokes cleanup.
- **owner gets:** A long task can survive the exact moment a private website asks the owner to prove identity, instead of failing, looping, or asking them to paste a secret into the AI. The owner handles the sensitive step locally and gets the finished result with a trustworthy record.
- effort: Medium-high: protocol types and persistence, extension event/UI, relay prompt plumbing, pendant interaction, and integration tests for 2FA/passkey/CAPTCHA/timeout/duplicate submission.  ·  risk: A stale or forged completion could resume the wrong tab or submit twice. Mitigate with origin+session binding, nonce expiry, signed pendant response, idempotency keys, and mandatory final receipt. If any check fails, abort rather than continue; recovery is an explicit retry from the last checkpoint.
- cost: Negligible inference cost; modest durable event/receipt storage and browser polling. No credential data leaves the browser.  ·  latency: Adds less than 1 second for challenge detection and roughly 1–3 seconds after local completion to resume.
- security: Improves security by keeping OTPs, passkeys, and CAPTCHA contents local. Adds a new signed control path that must be nonce-bound and origin-bound; redact challenge screenshots/text by default.
- depends on: Durable browser job runner and authenticated tab/session affinity; Typed action receipts and idempotency/undo ledger; Pendant local button/prompt protocol; Browser extension heartbeat and command/result queue


## What it asked for

_Nothing._
## Its own summary

Discovered the current tool/route surface and backlog, then added a new cross-surface capability: challenge-aware execution handoff. When a private site requires 2FA, passkey approval, CAPTCHA, or re-authentication, the browser pauses at a durable checkpoint, the pendant asks the owner without exposing secrets, and the Mac/browser resume the same tab/session with nonce, origin, expiry, idempotency, and final receipt checks. I also proposed the integration protocol and sent it to faculty-judgement.

**Biggest unknown:** The implementation still needs typed auth_challenge/auth_resolved events, durable checkpoint/resume and duplicate-submit protection, browser-local challenge UI, and a pendant signed approve/cancel interaction. I still lack the granted firmware/build and verification primitives needed to implement or test the pendant half; until those arrive this remains a recorded proposal rather than a shipped action.

