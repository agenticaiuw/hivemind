# Harness derivation — faculty-action — round 194

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Do the whole thing: update the document, send it to the people in the browser, and put a reminder on my calendar—tell me exactly what happened, and undo only the parts that can be safely undone if anything fails.”"
- **useful because:** Today the mind can plan a multi-step goal and individual hands can act, but it cannot honestly commit or recover a partially completed cross-surface workflow. This makes consequential errands trustworthy: every step is executed, independently verified, and leaves a truthful partial-success record rather than a vague success claim.
- **path:** unified → faculty-judgement → faculty-action → mac-planner → mac-vision → browser-extension → relay-realtime → faculty-perception
- **model tier:** Use the realtime tier only to clarify the spoken goal and report the result; use a cheaper background planner for the step graph and compensation policy. faculty-perception performs read-only verification after every mutation; faculty-action executes only approved steps.
- **latency:** Plan and approval summary in under 3 seconds; execute each step as its surface becomes available. A long workflow may take minutes, but the pendant should receive a haptic/status update after every verified step and on any stall.
- **cost:** Roughly 1–3 background-model calls per workflow plus one short realtime response. Dominant cost is browser/Mac execution time and verification, not model tokens.
- **security:** Each mutation gets its own risk classification and approval requirement. Never compensate by sending, deleting, or editing a new external object without a fresh approval. Persist an append-only operation graph with step IDs, receipts, verifier provenance, and explicit states verified/failed/unknown; expose secrets only to the local hand that needs them.
- **missing:** A saga/operation coordinator that groups existing job receipts into one dependency graph and supports narrowly predeclared compensations; A verifier-aware commit rule that requires faculty-perception evidence before advancing dependent steps; A user-facing partial-success and compensation policy, defaulting to stop-and-ask rather than guessing

### "“Fill in the checkout using my saved details, but do not show or tell me any card, address, or login secret; stop at the final purchase button and ask me to approve on the pendant.”"
- **useful because:** It lets the owner complete high-friction forms while preserving the browser's private session and keeping secrets out of model context. The AI can navigate and validate non-sensitive fields, the local browser hand can inject vault values, and the pendant remains the only physical approval boundary for the irreversible purchase.
- **path:** relay-realtime → unified → faculty-judgement → browser-extension → mac-planner → mac-vision → faculty-perception → faculty-action
- **model tier:** Use a cheap background model for field mapping and validation; use realtime only for the owner's final spoken decision and concise status. Browser-local code performs secret injection; no model receives field values.
- **latency:** Populate and validate in under 5 seconds after the owner asks. Stop at the purchase boundary and wait indefinitely for the physical approval, with expiry after 5 minutes.
- **cost:** One small planning call plus browser commands; typically <$0.05 in model spend. Browser execution and local vault access dominate latency, not inference.
- **security:** The browser extension must classify fields and redact values before returning DOM evidence. The model may see only labels, validation state, and a one-line total. A digest of merchant, amount, currency, and destination is sent to the pendant; the physical approval is nonce-bound and expires. Never permit approval for a changed digest, and never put secrets in relay logs, receipts, screenshots, or audio.
- **missing:** A browser-local secret-field injection primitive backed by the browser's existing authenticated vault/session; A redaction contract that returns field labels and validity without values or screenshots containing secrets; A final-checkout digest verifier that independently re-reads merchant, amount, currency, and destination before approval

### "“Queue that browser action, but do not run it while I’m moving. Tell me when I’m still, show me the exact target, and let me approve it on the pendant then.”"
- **useful because:** A wearable is the only node that can observe the owner's immediate motion while the Mac/browser holds the authenticated session. This prevents accidental high-impact actions while walking, cycling, or handling the pendant, without pretending that a spoken 'yes' during motion is deliberate. It turns physical approval into a context-aware handoff rather than a blind button press.
- **path:** relay-realtime → faculty-judgement → relay-realtime → faculty-action → faculty-perception → browser-extension → mac-planner → mac-vision → unified
- **model tier:** Use deterministic firmware motion classification and relay policy for the gate; use a background model to summarize the staged browser action. Realtime is only for the owner's request and final status.
- **latency:** Stage immediately; motion-state updates within 250 ms when the pendant is connected. Once stillness is detected, present the approval summary within 2 seconds and expire it after a policy-defined short window.
- **cost:** Near-zero inference for motion gating; one small summary call per staged action. Main cost is firmware integration and IMU sampling/power.
- **security:** Motion is a safety signal, not proof of identity or consent. Never auto-approve on stillness. Require the existing nonce-bound physical approval after a fresh browser digest; cancel on motion resumption, digest change, timeout, or link loss. Do not infer location or record raw IMU traces by default; persist only coarse state transitions and timestamps.
- **missing:** Firmware integration for the owned LSM6DSOX on i2c2, including a bounded stillness/motion classifier and signed state transitions; A relay policy gate that binds the staged operation nonce to a recent stillness interval and cancels on motion; Browser/Mac action support for pausing before the irreversible boundary without leaving a duplicate submission

### "“After that task, show me exactly what changed everywhere, including things that look unchanged at first glance, and offer only reversals that you can prove will not damage anything else.”"
- **useful because:** The owner cannot currently obtain a trustworthy cross-surface change ledger. A receipt says an action ran, and a verifier can check a postcondition, but neither answers the practical question: what changed before versus after, what side effects were introduced, and which reversal is safe. This would make the system usable for consequential work without requiring the owner to manually inspect every app and browser tab.
- **path:** faculty-action → faculty-perception → faculty-judgement → mac-planner → mac-vision → browser-extension → mac-terminal → relay-realtime → unified
- **model tier:** Use deterministic snapshot/diff logic for files, app state, browser URLs/fields, and message drafts. Use a cheaper background model only to summarize the structured diff in owner language; realtime speaks the short result.
- **latency:** Capture pre-state before execution in under 1 second where possible; produce a first diff within 3 seconds of completion, with slower domains marked pending rather than blocking the whole report.
- **cost:** Low model cost: typically one summarization call. Storage, redaction, and independent post-state reads dominate implementation cost.
- **security:** Snapshots must be scoped to the operation and aggressively redact secrets, message bodies, tokens, and unrelated private content. Store hashes and typed metadata by default, escalating to minimal snippets only when needed to explain a discrepancy. Never call something reversible merely because an inverse API exists; require a dependency-aware impact check and fresh approval for every reversal.
- **missing:** An operation-scoped preflight snapshot service spanning Mac app state, files, browser fields/URLs, and drafts; A typed diff format that distinguishes confirmed change, confirmed no-change, inaccessible, and unknown; A reversal-impact checker that can prove scope before presenting a rollback action; Retention and redaction policy for before/after evidence

### "“Try the whole automation in a private rehearsal first. Show me what it would touch, then run that exact approved plan for real without recomputing it.”"
- **useful because:** The owner currently must choose between trusting a plan sight-unseen and executing it directly. A deterministic rehearsal would expose wrong recipients, files, URLs, and side effects before they happen, then bind execution to the reviewed plan so the system cannot silently re-plan after approval. This is a distinct safety primitive from post-hoc verification or ordinary approval.
- **path:** faculty-judgement → faculty-action → faculty-perception → mac-planner → mac-vision → browser-extension → mac-terminal → relay-realtime → unified
- **model tier:** Use a background model to construct the plan and explain the rehearsal. Use deterministic local harnesses for dry-run interception and diffing. Realtime only presents the concise preview and receives the owner's explicit decision.
- **latency:** Preview in under 5 seconds for ordinary Mac/browser workflows; long operations stream step progress. Real execution must begin only after the owner approves the immutable plan digest.
- **cost:** One planning/summarization call; local dry-run overhead is the dominant cost. Browser and app sandboxing may require additional storage or isolated profiles.
- **security:** A rehearsal must not contact external recipients, submit forms, mutate real files, or leak secrets. Use isolated browser profiles, temporary filesystem roots, intercepted network calls, and redacted fixtures. The approval binds to the exact ordered step list, parameters, target identities, and digest; any divergence forces a new rehearsal and approval.
- **missing:** A true dry-run/interception harness for Mac actions and browser commands, not merely a textual plan; Isolated temporary browser sessions and filesystem/app fixtures that preserve enough state for realistic rehearsal; An immutable plan digest and executor enforcement that rejects any post-approval deviation; A typed side-effect forecast distinguishing simulated, blocked, and unmodeled operations


## What it asked for

_Nothing._
## Its own summary

Recorded two additional non-backlog capabilities: operation-scoped cross-surface before/after forensic diffs with provably safe reversal offers, and immutable private rehearsal followed by exact-plan execution. The owner would gain explainability and a safe preview rather than trusting opaque automation.

**Biggest unknown:** Whether the existing prepare/approve routes support immutable plan digests and whether Mac/browser surfaces can provide isolated dry-run environments; both need implementation rather than further discovery this round.

