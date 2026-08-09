# Harness derivation — unified — round 166

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac/browser readiness** — The AI Pendant Agent is healthy and fully ready now: Accessibility and Screen Recording are both granted for com.aipendant.agent, all required automation grants are present, relay is reachable, and Safari browser bridge is online with 9 tabs and zero pending commands. The pendant itself remains absent from live device inventory; only Mac bridge and browser are online.
  - evidence: GET /ops/status returned ready:true, accessibility.trusted:true, screenRecording.granted:true, relay.reachable:true, browser.online:true, pendingCommands:0; discover:devices listed Safari on MacIntel and home-macbook-bridge but no pendant.

## Capabilities it proposed

### "“Do the thing I asked for, but stop at the final irreversible step and ask me on the pendant.” Then, when I hold the approval button, finish it and tell me exactly what changed."
- **useful because:** This closes the system's most dangerous current lie: blocked plans say they are waiting for approval, but today nothing can approve or resume them. It lets the owner delegate a multi-surface browser/Mac task without surrendering the final purchase/send/delete decision, and makes the physical pendant the consent boundary.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime only for the spoken readback and concise approval prompt; deterministic local policy for staging, digest/world checks, replaySafety, expiry, and execution; background model only to summarize receipts after completion.
- **latency:** Stage within 2 s of the request; approval prompt on the next conversation turn; physical approval acknowledged within 500 ms; execute within 3 s after approval, excluding website latency.
- **cost:** Low per invocation: one realtime turn plus ordinary Mac/browser calls; deterministic digest and receipt work dominates neither tokens nor latency.
- **security:** Never send page secrets to the pendant. Bind the staged action to plan digest, world fingerprint, expiry, replaySafety, and an opaque nonce; require physical approval for irreversible-write/off-machine/uncontained steps; refuse if the page or files changed. The owner must see a truthful refusal rather than an implied completion.
- **missing:** Call closeLedger for ordinary completed orchestrator plans so resume discovery is not all historical jobs; Implement the relay half of approvalHandoff's existing APPROVAL_STORE_CONTRACT and deliver the readback on the next conversation; Add a real relay job lease/requeue sweep for Mac outages; Wire the accepted physical_transaction_approval_latch event into approval evaluation and expose one owner-facing approve/resume route; Add a distinct authorization boundary if approval must be stronger than the existing AGENT_TOKEN

### "“What did I miss while the pendant was offline?” or “Replay only the answers I never heard, in order.”"
- **useful because:** A dropped link currently leaves a confusing mix of processing, waiting, and delivered states. This would turn the relay, Mac job history, browser receipts, and the pendant's delivery acknowledgements into a trustworthy spoken catch-up: no duplicate answer, no claim that queued audio was heard, and an explicit list of anything that expired or failed.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic event join and deduplication first; a cheap background summarizer for multiple missed answers; Realtime only to speak the short catch-up or accept a replay command.
- **latency:** Return the first missed-item count in under 1 s; produce a 20–40 s spoken digest in under 5 s; replay begins within 1 s per item.
- **cost:** Low: mostly indexed receipt/event reads; one small background summarization call only when there are several items. Audio retransmission dominates bandwidth, not model cost.
- **security:** Only expose jobs bound to this pendant/session and redact browser page contents unless the owner explicitly asks for them. Treat relay acceptance, device download, playback start, and playback finish as separate facts. Never replay an item whose delivery nonce was already acknowledged; require a fresh confirmation for sensitive queued speech.
- **missing:** A durable relay query that joins job, pipeline, and audio-delivery-ack records by opaque artifact ID; A compact spoken catch-up protocol over the existing pendant inbox, with expiry and per-item replay nonce; An owner-configurable retention/redaction policy for missed transcripts and audio; A transport-aware replay endpoint that can target USB today and LTE later

### "“For the next ten minutes, let you use the logged-in browser tab only to look up my order and tell me the status; do not click, type, or send anything.”"
- **useful because:** The browser is where the owner's private sessions live, but the current bearer-token bridge does not give the owner a small, visible, revocable permission they can grant from the thing they are wearing. This creates a least-privilege, time-boxed browser capability: read-only or action-scoped, tied to one tab, auditable, and automatically dead afterward.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic policy and token enforcement; Realtime only for the owner's spoken scope and confirmation; background model optional for summarizing retrieved page data.
- **latency:** Show the scope and pending state within 1 s; physical confirmation within 500 ms; first read result within 3 s; revocation takes effect on the next browser command, under 200 ms.
- **cost:** Very low model cost; the dominant cost is browser command execution and optional screenshot/OCR. No model call is needed to enforce scope.
- **security:** Issue a short-lived, audience-bound capability token containing tab/session ID, allowed verbs, URL pattern, expiry, nonce, and redaction policy. Reject navigation or verb escalation, log every command and result, revoke on privacy latch, and never place cookies, page secrets, or token material in pendant audio. Screen recording is now reported granted, but screenshots still require explicit owner policy.
- **missing:** A capability-token issuer/verifier shared by relay and browser extension, rather than the single AGENT_TOKEN; Extension enforcement for per-tab URL, verb, field, and expiry constraints; A pendant-visible scope readback and physical approval event for granting/revoking the token; A revocation push/poll path that does not wait for the 45-second browser command lease; Owner-configurable defaults for screenshot/OCR and sensitive-domain redaction

### "“For this task, keep everything local to my Mac and browser, send the model only the minimum extracted facts, and erase the task material when you’re done.”"
- **useful because:** The owner should be able to use logged-in browser sessions and local files without making raw page contents, screenshots, audio, or intermediate transcripts durable relay data. This is a data-residency contract for one task, not merely a global privacy latch: it limits what crosses surfaces and proves cleanup afterward.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic policy engine for residency, redaction, retention, and cleanup; a cheap model may extract requested facts locally; Realtime only for concise spoken confirmation.
- **latency:** Declare the residency mode in under 1 s; local extraction within the underlying task's normal latency; cleanup receipt within 2 s of completion.
- **cost:** Usually cheaper than today because less content reaches the expensive model; local OCR/extraction and secure deletion verification dominate.
- **security:** Default-deny raw screenshot, microphone, browser HTML, cookies, and secrets at the relay boundary. Keep only a task digest and typed result. Treat deletion as incomplete if any spool, pipeline artifact, browser command result, or Mac temporary file remains; require explicit confirmation before relaxing residency.
- **missing:** A per-task data-residency contract carried through plan, browser commands, pipeline events, and receipts; Local structured extraction/redaction before relay upload; Retention tags and deletion receipts across Mac, relay, browser spool, and audio artifacts; A dashboard/pendant readback that states exactly what data crossed the boundary

### "“Only let this agent act while the pendant is physically with me. If it disappears, pause every queued action and tell me what was prevented.”"
- **useful because:** A stolen or unattended Mac session should not retain the ability to act merely because its bearer token is valid. A live, device-bound presence signal would turn the worn pendant into a physical boundary for browser and Mac authority, while still allowing read-only diagnostics when it is absent.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic heartbeat, nonce, lease, and policy checks; no model call for authorization; Realtime only to explain a pause or recovery.
- **latency:** Presence loss pauses new mutating commands within 1 s; already-running commands are cancelled at their next safe checkpoint; restoration is acknowledged within 2 s.
- **cost:** Negligible model cost; small authenticated heartbeat traffic and a bounded lease record.
- **security:** Use a device-bound key and monotonic nonce, not a replayable Bluetooth/USB identifier or spoken phrase. Fail closed for off-machine, irreversible, and browser-mutating actions; permit explicitly allowlisted local read-only work. Do not infer physical presence from the Mac's network reachability.
- **missing:** A cryptographic pendant identity/attestation channel over USB now and LTE later; Relay and Mac presence leases with fail-closed command admission; Browser-extension enforcement of the same presence lease; A policy separating read-only, reversible, and irreversible actions by presence requirement; A durable prevented-action receipt so absence is explainable rather than silent

### "“Why did you do that, and what exact evidence made you choose it?”"
- **useful because:** Today receipts can say that an action ran, but not give the owner a compact, trustworthy causal story spanning the spoken request, browser state, Mac observations, policy decision, and resulting change. This would make the agent inspectable after surprising behavior without exposing unrelated tabs or private data.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic provenance graph and redaction first; a background model compresses it into plain language; Realtime only answers the owner's follow-up question.
- **latency:** A terse spoken explanation in under 2 s; dashboard evidence expansion in under 1 s from indexed records.
- **cost:** Low: indexed receipt reads dominate; summarization is optional and can use the cheap background tier.
- **security:** Each claim must link to an immutable observation or policy rule, with timestamps and source surface. Redact unrelated tabs, credentials, and raw audio. Clearly label inference versus observed fact; never let a model-generated explanation substitute for a receipt.
- **missing:** A cross-surface provenance schema linking request, observation, policy, plan digest, action, and post-state; Immutable observation hashes and source-scoped redaction; A read-only owner query and spoken explanation formatter; Retention rules for provenance separate from raw page contents and audio; Coverage checks that refuse to claim provenance when a step lacks evidence


## What it asked for

_Nothing._
