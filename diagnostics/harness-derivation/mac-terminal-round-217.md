# Harness derivation — mac-terminal — round 217

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Take whatever I’m looking at in Safari, figure out the next concrete action, and do it on my Mac—then tell me in my ear what changed and where you got the facts.”"
- **useful because:** This is the system’s strongest unique combination: the browser has authenticated context the relay cannot see, the Mac can mutate local state, and the pendant is the only interface that can report completion while the owner walks away. It turns a page into a finished outcome rather than another summary, while retaining page-level provenance.
- **path:** pendant → relay → browser → mac-planner → mac-vision → dashboard
- **model tier:** Use realtime only for the short voice turn and intent extraction; use a cheaper background model to read the page, identify the next action, and draft the execution plan. Use the Mac planner/computer-use loop only for UI steps that structured browser actions cannot perform.
- **latency:** Acknowledge from the pendant in under 1 second; page read and plan in 3–8 seconds; execution may run asynchronously with a spoken completion or failure update.
- **cost:** Typically one cheap text call plus browser/Mac actions; reserve realtime tokens for roughly 1–2 short turns. Vision is the dominant cost only when the page has canvas or inaccessible controls.
- **security:** Authenticated page text and URLs leave the browser only as extracted claims; never send whole cookies or page HTML to the relay. Local mutations remain on the Mac. Speak only a concise result; require the existing owner policy for consequential actions, but do not add a new approval gate.
- **missing:** A first-class cross-surface task object tying pendant request, browser command/provenance, Mac job, and final receipt together; A planner contract that emits a typed next-action plus provenance requirements instead of an unstructured goal; A completion payload that the relay can turn into a spoken digest and cache offline

### "“That Mac task failed—tell me exactly why, fix the command or working directory if you can, and retry only the failed step.”"
- **useful because:** Today a shell failure is flattened into a message: exit status is lost, retries are absent, and a restart can strand a job. A spoken, step-scoped repair loop would make the Mac feel dependable: the owner gets a diagnosis instead of “failed,” and successful earlier steps are not repeated.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** Use a cheap background model to classify the captured exit code/stderr and propose a repair; use realtime only to ask a short clarification when the repair is genuinely ambiguous. The planner should reuse the original job’s context and action receipts rather than resend the whole conversation.
- **latency:** Speak failure within 2 seconds of process exit; propose a repair within 5 seconds; retry starts immediately after the owner’s natural-language go-ahead or the existing unattended policy permits it.
- **cost:** One small text repair call per failure; negligible compared with a repeated full planning call. Persisted receipts reduce context retransmission and are the main savings.
- **security:** A repair must be bounded to the failed action’s touched paths and preserve the original command for audit. Never silently broaden cwd, environment, or network scope while repairing. The owner’s maximum-access policy remains intact; this is diagnosis and recovery, not a new gate.
- **missing:** Capture process exit code, signal, argv-or-command digest, and timeout reason in the receipt; Attach every execution ledger to its jobId and close it on success/failure; An idempotent retry endpoint that resumes from the failed step and refuses already-completed side effects; A relay event carrying structured failure and retry outcome to the pendant

### "“I’m handing my Mac to someone for five minutes—hide my private browser tabs and sensitive windows, keep the work state, and restore everything when I say I’m back.”"
- **useful because:** The owner’s authenticated Safari currently contains Discord, YouTube, X/Grok, Google searches, and other private context in one window. A wearable command can protect that state while the owner is away without logging out or destroying work, then restore it hands-free. No single node can do this: the pendant supplies trustworthy intent, the Mac controls windows, and the browser extension knows which tabs can be suspended and restored.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime handles the two short commands and immediate acknowledgement. A deterministic local Mac/browser routine should snapshot tab IDs, window order, URLs, focused app, and mute/lock state; use a cheap model only to classify which visible windows are private when labels are ambiguous.
- **latency:** Privacy transition under 2 seconds, with an immediate pendant tone before windows move; restore under 5 seconds. If the Mac link drops, the pendant should say the transition was not confirmed rather than claim privacy.
- **cost:** Near-zero model cost for explicit commands; the expensive part is only occasional vision/classification for an unlabelled window. Local state snapshots are tiny.
- **security:** The snapshot must stay encrypted on the Mac and must not send URLs, titles, cookies, or screenshots to the relay. Never close tabs or sign out; hide/minimize or switch to a clean workspace and record exactly what changed. Restoration must be scoped to the owner’s authenticated local session and expire stale snapshots.
- **missing:** A browser action to suspend/restore a named tab set and preserve window ordering; A Mac workspace/privacy transaction with atomic snapshot, apply, and restore operations; A local-only sensitivity classifier and an explicit verified completion signal surfaced to the pendant; A TTL and crash-recovery policy for snapshots so private tabs cannot be restored to the wrong user

### "“Handle this private task without sending its contents to the cloud: read the authenticated page on my Mac, make the needed local change, and tell me only the outcome.”"
- **useful because:** The owner should be able to use the system for genuinely sensitive work, not merely public browsing. Today the relay/model boundary makes it unclear whether authenticated page contents, URLs, and local files leave the Mac. A local execution lane would let the pendant be the voice interface while sensitive perception and action remain on-device.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime handles only the short intent and a redacted result. A local Mac model or local planner performs page reading, extraction, and action; the relay receives an intent token and a bounded outcome enum, never page text or screenshots.
- **latency:** Acknowledge intent in under 1 second; local page handling in 2–10 seconds; speak only after a verifiable local completion receipt.
- **cost:** Relay token cost is minimal. Local model inference and encrypted local storage dominate; cloud vision is avoided for sensitive tasks.
- **security:** The privacy boundary must be technically enforced, not a prompt promise: separate local-only execution mode, deny cloud uploads and telemetry for the task, redact logs and receipts, encrypt transient page data, and show a distinct pendant state while local-only mode is active. The owner should be told if the task cannot be completed locally.
- **missing:** A local-only task mode with an enforceable no-upload boundary; A local inference/extraction capability for browser pages and Mac files; Redacted result schemas that carry outcome and evidence hashes without sensitive content; A pendant-visible privacy mode and an audit record proving which surfaces received data

### "“Only act on sensitive requests while I’m physically wearing the pendant; if it’s on my desk or disconnected, pause the task and tell me why.”"
- **useful because:** A voice token or Mac session alone is not proof that the owner is present. A continuously authenticated wearable-presence signal would make unattended browser sessions and powerful Mac control safer without adding a confirmation dialog to every ordinary action. It also prevents a stale queued request from executing after the owner has left.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** No expensive model is needed for presence attestation. Use firmware and cryptographic challenge-response; use realtime only to explain a pause or resume in natural language.
- **latency:** Presence decision under 300 ms for a new action; loss of presence should pause before the next side-effecting step and report within 1 second. Reconnection must require a fresh challenge, not merely a cached heartbeat.
- **cost:** Negligible model cost. Work is firmware, pairing, and a small relay/Mac state machine.
- **security:** Do not use RSSI alone, which can be spoofed or remain strong while the owner is absent. Use rotating nonces, replay protection, explicit paired-device identity, and a short lease. Presence should authorize continuation, not reveal location. The owner must be able to disable it for trusted unattended routines.
- **missing:** A cryptographic wearable-presence attestation protocol over the available pendant link; A Mac executor hook that checks the lease before each side-effecting action; A relay rule that expires queued sensitive work when presence is lost; A clear pendant state for paused-for-presence versus host failure

### "“I was away for an hour—tell me only what materially changed on my Mac and in my open browser work, what still needs me, and let me resume any unfinished thread from the pendant.”"
- **useful because:** Today state is fragmented across browser tabs, Mac jobs, relay events, and local files. The owner can inspect each surface, but cannot receive a trustworthy causal catch-up that distinguishes completed work, incidental changes, and unresolved decisions. This would make leaving the desk safe: the owner returns to a prioritized continuation, not six unrelated status screens.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard → unified
- **model tier:** Use a cheap background model to cluster and rank durable events; realtime only speaks the short prioritized digest. Deterministic event correlation should establish timestamps and job outcomes before any model summarizes them.
- **latency:** Generate a catch-up in under 5 seconds for the last hour; under 15 seconds for a day. Resume should acknowledge immediately and run asynchronously with truthful progress.
- **cost:** Low: incremental event summaries and compact local state, rather than resending browser pages or full job logs. Model cost scales with changed items, not elapsed time.
- **security:** Keep raw browser URLs, page text, and local file contents on the Mac. Send the relay only redacted event summaries and stable identifiers. Mark uncertain or inferred changes explicitly; never present a model guess as a completed action.
- **missing:** A durable cross-surface event stream for browser, Mac, relay, and pendant state changes; A causal correlation layer linking events to a user request and unfinished continuation; A materiality/attention ranking policy with an explicit uncertainty field; A resume token that safely reopens the exact browser/Mac context without replaying side effects


## What it asked for

_Nothing._
