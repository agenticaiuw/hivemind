# Harness derivation — faculty-judgement — round 71

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When a request involving my private accounts fails, tell me exactly why, give me the shortest repair step on the right device, and retry the original request automatically once access is restored—without repeating work or exposing account contents."
- **useful because:** The owner's repeated Gmail/GitHub/Calendar requests currently fail as opaque failures. This turns a dead end into a recoverable handoff: the pendant explains the blockage, the Mac or browser repairs only the missing link, and the relay resumes the original intent with an evidence trail.
- **path:** relay-realtime → browser-extension → mac-planner → mac-terminal → faculty-perception → faculty-action → pendant
- **model tier:** Use a cheap background classifier for failure taxonomy and repair-card generation; use realtime only to explain the current blockage and collect a concise owner confirmation when a browser reconnect or account sign-in is required.
- **latency:** Under 2 seconds to classify and speak the failure; repair can run asynchronously. Resume within 5 seconds of a successful bridge/session health signal, otherwise leave a durable pending card.
- **cost:** Usually one small classification call plus one short spoken response (well under a normal realtime turn); retries should be tool-only. Dominant cost is private-page extraction only after access is restored.
- **security:** Never include page contents, tokens, cookies, or account identifiers in the repair card. Distinguish bridge-offline, tab-missing, session-expired, permission-denied, and site error. Require explicit owner confirmation before opening a sign-in page or changing credentials; preserve the original request encrypted/delimited with expiry and redact it from logs.
- **missing:** A typed auth/bridge failure taxonomy with remediation recipes and safe redaction; A durable resume record that binds the original intent to a browser session and expires it; A local browser-bridge health event or Mac-side repair launcher; A pendant-visible repair card with one-tap/spoken retry and owner-presence confirmation

### "When I say “not now” or get interrupted, remember exactly what I was doing across the pendant, Mac, and browser, wait for a sensible boundary, and offer one short resume prompt—not a generic reminder."
- **useful because:** A reminder preserves a sentence; it does not preserve the half-completed browser form, the Mac document, or why the decision mattered. This would let the owner safely defer without rebuilding context, while avoiding noisy interruptions.
- **path:** relay-realtime → pendant → mac-planner → browser-extension → faculty-perception → faculty-action
- **model tier:** Use a small background model to summarize and choose a boundary from structured task state; realtime is used only for the owner's brief defer/resume exchange.
- **latency:** Capture in under 1 second after “not now.” Boundary detection may take minutes or hours; resume prompt should be one sentence and cancellable.
- **cost:** One short summary call per deferral and no model cost while waiting if events are structured; audio playback is the main device-side cost.
- **security:** Store a redacted task capsule, not page text or credentials. Do not snapshot sensitive browser pages unless the owner explicitly allows it. Resume must re-check session validity and show the target app/page before any action; never submit or send without confirmation.
- **missing:** A cross-surface task capsule with redaction and TTL; Boundary signals such as document save, browser navigation completion, meeting end, or Mac idle/active transitions; A quiet-hours and interruption policy evaluator; A resume action that reattaches browser tab and Mac app safely

### "Before you use a private page, document, or message to answer me, show me a one-line privacy preview—what source is being used, what sensitive fields will leave the device, and whether the answer can stay local—then proceed with the safest route."
- **useful because:** Today the owner can authorize browser reading, but cannot see or control the boundary between a logged-in page, the Mac, the relay, and the realtime model. This gives them useful answers without requiring blind trust, and makes sensitive work possible even when cloud transmission should be avoided.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action → pendant
- **model tier:** Run field detection and redaction locally with a small deterministic/cheap model; use realtime only to speak the compact preview. Escalate to the expensive model only after the selected privacy route is explicit.
- **latency:** Privacy preview in under 500 ms for cached/local content and under 2 seconds for a newly inspected page. Proceed asynchronously after approval; no repeated preview for the same unchanged source within its TTL.
- **cost:** Near-zero API cost when local redaction succeeds; occasional small-model classification for unknown fields. The expensive model receives only the approved, minimized excerpt.
- **security:** Treat credentials, health, financial, location, and secrets as sensitive by default. The preview itself must not quote sensitive values. Keep raw page/document content on the originating device unless the owner chooses relay processing; record only a redaction manifest and policy decision. Require confirmation for any irreversible action regardless of route.
- **missing:** A device-local sensitive-field detector and redaction engine shared by browser and Mac; A typed data-flow manifest identifying source, fields, destination model, retention, and purpose; A pendant-sized privacy preview/approval interaction with deny, redact, local-only, and proceed choices; Model-routing enforcement that cannot accidentally bypass an owner-selected local-only policy; Auditable deletion of temporary excerpts and manifests


## Changes it proposed to its own stack

### `integration` — Add an expiring Resume Contract spanning relay, browser bridge, and Mac agent. On any private-account failure, persist only {intent hash, requested data class, originating surface, session/tab hint, failure class, remediation, expiry}; emit a repair card. A bridge-health or successful sign-in event atomically revalidates the contract, resumes at the failed step with idempotency, and attaches a receipt. Expire and delete contracts by default after 24 hours or on owner cancellation.
- **owner gets:** Saying “read Gmail” once would no longer lose the request when the browser is disconnected or a session expires. The owner gets one clear repair instruction and then the original answer, rather than having to remember and repeat the task.
- effort: Medium: shared schema, event wiring, redaction tests, and failure-injection tests across relay/browser/Mac; no model training required.  ·  risk: A stale contract could resume against the wrong account or perform an unintended mutation. Restrict first release to read-only extraction and drafts, bind to an explicit session identity, require re-approval for send/delete/purchase, and provide cancellation plus receipt/undo where supported.
- cost: Negligible storage and tool overhead; one small classifier call only on failure. No extra realtime call on successful resume.  ·  latency: Immediate failure explanation; resume adds one event round trip, typically under 1–2 seconds once the bridge is healthy.
- security: Improves security by keeping secrets out of durable state, expiring intent, and making account/session binding explicit; requires encrypted contract storage and redacted telemetry.
- depends on: Typed browser/Mac failure taxonomy; A browser-bridge health/reconnect event; Durable idempotency and receipt linkage; Owner confirmation policy for authentication and irreversible actions


## What it asked for

_Nothing._
## Its own summary

This round identified two owner-facing gaps that are not another generic brief, watcher, receipt, or undo: (1) private-account failure recovery, where an opaque Gmail/GitHub/Calendar failure becomes a redacted repair card and automatically resumes the original read-only intent after the bridge/session is fixed; and (2) interruption-safe resume, where “not now” preserves a short, redacted cross-surface task capsule and offers one boundary-aware resume prompt. I recorded a concrete integration change: an expiring Resume Contract bound to intent hash, account/session, remediation, idempotency, and receipt, with revalidation before resuming. Existing tools/routes can carry much of this, but the missing connective primitives are a typed failure taxonomy, bridge-health event, durable redacted capsule, boundary signals, and policy-driven revalidation. I do not need to re-request the denied macOS grants; the first version should use the already-granted AppleScript/browser read paths and remain read-only.

**Biggest unknown:** Whether the browser bridge can emit a trustworthy reconnect/session-restored event and stable account/session identity. Without that, repair cards can explain the problem but cannot safely trigger automatic resumption; the owner would still need to say “retry.”

