# Harness derivation — faculty-action — round 167

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Use what I’m looking at and handle this: save the selected text to my notes, add a reminder for tomorrow, and tell me when it is actually done.”"
- **useful because:** The pendant becomes a physical 'act on this exact thing' control instead of forcing the owner to repeat URLs, titles, or snippets. It joins wearable intent, the Mac's focused app/browser state, execution, and independent verification into one dependable action—the most useful everyday action surface.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-action → dashboard
- **model tier:** Realtime only for the short spoken intent; a cheaper background planner executes the multi-step workflow and faculty-perception verifies each postcondition.
- **latency:** Acknowledge in under 1 s; capture focused context in under 2 s; complete typical note+reminder flow in 10–30 s, with spoken progress if longer.
- **cost:** Roughly $0.01–$0.05 per workflow, dominated by planner/verifier model calls; context hashes and selected text stay on the Mac unless needed for the requested action.
- **security:** Focused text may be private or secret. The Mac must classify sensitivity, send only the minimum excerpt/hash, redact secrets, and require the existing physical approval latch before external side effects. Never transmit passwords or page contents to the pendant.
- **missing:** A Mac bridge primitive that atomically snapshots focused app, URL, selection, and sensitivity label; A typed context-handoff envelope consumed by planner/action; A resolved postcondition verifier route with operation and step correlation

### "“If I lose the Mac link while you’re doing that, keep the job safe: tell me exactly whether it ran, is waiting, or was cancelled when I reconnect.”"
- **useful because:** A dropped link currently forces the owner to guess whether a real-world action happened. This gives the pendant a truthful recovery conversation: durable intent state, no duplicate execution after reconnect, and a clear verified/unknown outcome across the wearable, relay, Mac, browser, and perception nodes.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-action → faculty-perception → dashboard
- **model tier:** Relay state machine and Mac executor are deterministic; use a cheap background model only to summarize the state in natural language.
- **latency:** Persist state before dispatch; reconnect status available within 2 s of the Mac or pendant returning, with no requirement to keep a model session alive.
- **cost:** Under $0.005 per job for durable state and a short summary; storage and receipts dominate, not inference.
- **security:** Replay protection and idempotency keys are mandatory. A lost receipt must produce UNKNOWN, never SUCCESS. Sensitive action details remain on the Mac; the pendant receives only a redacted human summary and state token.
- **missing:** Durable operation state shared by relay and Mac executor; Idempotency-key enforcement at every side-effecting executor; Reconnect status query and compact pendant status vocabulary

### "“Watch this open browser page for the condition I named, and when it becomes true, do the prepared Mac action—but ask me if the page changes or the evidence is ambiguous.”"
- **useful because:** The owner gets a durable, supervised bridge from browser state to real-world Mac action instead of repeatedly checking pages. It combines a browser session the relay cannot access, a Mac executor, perception of fresh evidence, and the pendant as an interruption/approval channel.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-vision → faculty-perception → faculty-judgement → faculty-action → dashboard
- **model tier:** Cheap scheduled/background polling and deterministic selectors first; realtime model only when the owner speaks or ambiguity needs a short clarification.
- **latency:** Polling cadence configurable from 30 s to 15 min; notify within one cadence plus 2 s; action starts only after fresh evidence and required approval.
- **cost:** Low: browser polling is local; occasional compact perception calls cost under $0.01 per check, with model use only for changed/ambiguous pages.
- **security:** Page content can include private account data. Keep observation local to the browser extension, send hashes/minimal snippets, freeze the prepared action if DOM identity or URL changes, and require physical approval for consequential side effects. Never silently act on a changed page.
- **missing:** A durable browser watch with selector/URL identity, cadence, expiry, and change detection; A cross-surface trigger event from browser-extension to relay and Mac planner; A fresh-evidence gate that binds the action to the exact observed page revision

### "“Take this as far as you can, and if you hit a login, 2FA, CAPTCHA, or approval screen, tell me exactly what I need to do; then continue the same job without starting over.”"
- **useful because:** Today an agent either stops at an authentication boundary or risks asking for secrets. This lets the browser extension retain the live session while the pendant gives the owner a precise, minimal handoff. The owner completes only the private step, and faculty-action resumes the original operation with evidence that the page did not change underneath it.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-vision → faculty-perception → faculty-action → dashboard
- **model tier:** Deterministic browser boundary detection and state machine; use realtime only for the short spoken handoff and a cheap background model to summarize non-sensitive instructions.
- **latency:** Detect a blocked boundary within 2 s; speak instructions within 1 s; resume within 3 s after the owner completes it.
- **cost:** Under $0.02 per interrupted workflow, dominated by one compact perception/summary call. Secrets and authentication codes remain entirely on the owner's browser/device.
- **security:** Never request passwords, OTPs, recovery codes, or CAPTCHA answers through the relay or pendant. Bind the continuation to the same tab, origin, and pre-boundary state; expire it after a short timeout and abort on navigation or account change. Require approval before the resumed side effect.
- **missing:** A typed auth-boundary event containing origin, tab identity, safe human instructions, and continuation token; Browser-side detection of challenge completion without exposing secret fields; Continuation validation against pre- and post-boundary page identity

### "“Handle this private form, but keep every secret field on my Mac and show me exactly which fields you filled before anything is submitted.”"
- **useful because:** The owner could delegate tedious forms without handing the AI passwords, payment numbers, or medical identifiers. The browser holds the values locally; faculty-action fills by opaque field handles, produces a redacted field-level diff, and submits only after the owner confirms the intended non-secret values.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → faculty-perception → faculty-action → dashboard
- **model tier:** Local deterministic field mapping and redaction; a small planner model interprets labels and summarizes the diff. Realtime is only for confirmation dialogue.
- **latency:** Preview in 3–8 s for ordinary forms; no submission until the owner confirms. Local secret filling should add less than 500 ms.
- **cost:** About $0.01–$0.03 per form, primarily label interpretation; no secret data leaves the browser.
- **security:** Opaque handles, origin binding, field-type allowlists, and redaction are mandatory. The relay must never receive field values. Submission requires the existing physical approval mechanism and independent postcondition verification.
- **missing:** Browser-local secret-field handles and fill operation; Redacted field-diff preview protocol; Origin- and form-version-bound submit token


## Changes it proposed to its own stack

### `interaction` — Add a 'context pin' gesture on sw1: while the owner is viewing a Mac/browser item, one deliberate press captures a short-lived, sensitivity-labeled reference (app, URL, selection hash, title) and gives it a visible LED/audio confirmation. The next spoken request explicitly binds to that pin; it expires after 10 minutes or on completion.
- **owner gets:** The owner can point at a thing without reading it aloud or remembering where it lives, then speak naturally while walking away. It prevents the common failure where an assistant acts on the wrong tab or stale document.
- effort: Medium: firmware gesture/event, Mac bridge context snapshot, relay envelope and expiry, planner binding, and perception checks.  ·  risk: A stale or sensitive pin could be misapplied. Use short expiry, sensitivity-based redaction, explicit confirmation for side effects, and show the title/domain back to the owner before execution. Recovery is simply discard and repin.
- cost: Negligible API cost; a small relay record per pin. Firmware storage is a few hundred bytes if offline buffering is needed.  ·  latency: About 1–2 s to snapshot and acknowledge; no added latency after the pin is resolved.
- security: Improves security by binding actions to a concrete context, but selection text must not reach the pendant or relay unless explicitly required; use hashes and local redaction.
- depends on: Mac bridge focused-context snapshot API; Use sw1 (sw0 has active-edge semantics and no gesture headroom); Existing physical_transaction_approval_latch for consequential actions

### `mac-harness` — Introduce a resumable action checkpoint protocol at every external boundary: persist a compact, redacted checkpoint containing tab/app identity, intended side effect, completed substeps, idempotency key, and the next safe operation. On retry, faculty-action must reconcile the checkpoint with fresh Mac/browser state before issuing any new mutation, rather than replaying the whole plan.
- **owner gets:** A browser crash, login interruption, or dropped connection would no longer force the owner to repeat a long workflow or risk duplicate purchases, messages, or submissions. The assistant can continue from the last proven safe point and explain precisely what remains.
- effort: Medium-high: executor instrumentation, relay persistence, browser identity checks, and perception integration.  ·  risk: A stale checkpoint could cause an incorrect continuation. Expire checkpoints, require fresh state reconciliation, and return UNKNOWN when reconciliation is inconclusive; recovery is manual restart from a newly prepared plan.
- cost: Small storage and hashing overhead; negligible model cost except when reconciliation is ambiguous.  ·  latency: Adds roughly 0.5–2 s at each external boundary, but avoids much longer retries and duplicate side effects.
- security: Checkpoints must contain hashes and labels, never form secrets or page contents; encrypt sensitive metadata at rest and bind records to the operation nonce.
- depends on: A resolved independent postcondition verifier; Executor-wide idempotency keys; Browser tab/origin identity exposed to the Mac harness


## What it asked for

_Nothing._
