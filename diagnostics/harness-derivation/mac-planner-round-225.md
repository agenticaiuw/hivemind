# Harness derivation — mac-planner — round 225

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If I leave a checkout, booking, or order page unfinished, watch it and tell me later only when it is still pending or the price/details changed; never submit or buy anything."
- **useful because:** The owner can safely abandon a transaction and forget it. A bounded browser watcher can detect a stale pending state or changed total, then put a concise alert in the pendant inbox and optionally create a reminder, without taking the dangerous final action.
- **path:** browser → relay → pendant → mac-bridge
- **model tier:** background polling/extraction model; realtime is unnecessary except for speaking an alert when the owner asks
- **latency:** Check once per configured interval (for example 6 hours), finish within 10 seconds, and deliver an alert asynchronously.
- **cost:** Roughly $0.01–$0.05 per watched page check, dominated by authenticated-page extraction; cheaper DOM/state diffing should avoid model calls when unchanged.
- **security:** Authenticated page contents stay in the browser harness; send only merchant, status, amount, and change summary. Never click submit, checkout, or purchase. Watching a page requires explicit per-site enrollment and expiry.
- **missing:** A browser page-watch state machine that stores a redacted baseline and detects pending/changed transaction fields; A relay-to-offline_alert_inbox adapter with urgency and expiry; A bounded browser route for extracting transaction state from an enrolled authenticated tab

### "After you change something on my Mac, tell me what actually changed and offer to undo that exact change from the pendant—especially files moved, reminders created, or apps opened—rather than merely saying the command succeeded."
- **useful because:** A command receipt is not proof that the world changed as intended. This creates a compact spoken change report backed by before/after observations and makes the existing undo surface reachable from the pendant, reducing silent failures and forgotten mutations.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** background verifier using deterministic inspectors first; realtime only to summarize a stored receipt in one sentence
- **latency:** Verify within 3 seconds for local file/app/reminder actions; speak on the next owner request or alert only on contradiction.
- **cost:** Usually <$0.005 per action with deterministic checks; occasional model summarization <$0.01 when multiple resources changed.
- **security:** Receipts must redact file contents, secrets, and mail bodies, retaining paths/resource IDs and hashes. Undo must be scoped to the recorded job and never infer a broader deletion. Owner policy should choose which mutation classes may be undone remotely.
- **missing:** A postcondition verifier that maps each action type to a read-only before/after check; A durable spoken receipt schema containing touched resources, postcondition evidence, and an undo job ID; Pendant alert/inbox action that can request undo for a specific receipt, with a safe no-op when undo is unavailable

### "When I tell you something sensitive to remember, store it safely and confirm only that it was secured; never repeat the secret through the pendant, put it in a briefing, or expose it to browser or Mac logs."
- **useful because:** The current capture evidence shows a bike-lock code stored as a secret alongside ordinary ideas. A real owner-facing secret path must survive the relay while preventing accidental spoken repetition, routine inclusion, browser exposure, and plaintext Mac receipts.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** realtime classifier only for the short capture turn; background model is not needed for storage or policy enforcement
- **latency:** Acknowledge in under 1 second with a generic confirmation; encryption and policy commit should be synchronous before acknowledging success.
- **cost:** Under $0.005 per capture; dominated by encrypted storage and deterministic redaction, not model inference.
- **security:** The secret must be encrypted before durable relay/Mac storage, excluded from model context projections and all spoken summaries, and never written to action receipts or browser state. Access should require an explicit owner request and a separate reveal policy; failed writes must not fall back to plaintext.
- **missing:** An end-to-end secret vault route with envelope encryption and strict non-projection semantics; A capture classifier/policy that distinguishes secret, private, and ordinary notes before persistence; A pendant confirmation event and dashboard audit showing only metadata (created, updated, deleted), never value

### "When I say “take this with me,” move the active conversation and unfinished task from my Mac to the pendant so I can leave the desk, continue by voice over LTE, and return later without losing the browser or file context."
- **useful because:** Today the Mac and pendant are separate moments. The owner should be able to begin a task at the desk and continue while walking, with one session identity, preserved task state, and no need to explain the context again.
- **path:** mac-bridge → browser → relay → pendant
- **model tier:** Realtime for the live audio/session handoff; background for compact context summarization during reconnects.
- **latency:** Handoff acknowledgement under 2 seconds; audio migration under 5 seconds; reconnect recovery within 30 seconds after a link drop.
- **cost:** About $0.01–$0.05 per handoff, dominated by summarizing bounded active context; audio transport cost is separate.
- **security:** The relay must carry only the active task capsule, not the entire Mac screen or browser history. Browser credentials remain in the browser session. Leaving the Mac must revoke its live microphone/control lease, and return must not replay stale commands.
- **missing:** LTE-registered pendant transport and authenticated session migration; A session lease shared by relay, Mac bridge, browser bridge, and pendant firmware; A compact task capsule containing current intent, browser session handle, open resources, and pending action state; Explicit Mac microphone/control revocation and resume semantics

### "Fill out this repetitive web form for me, but before anything is submitted, show me a concise field-by-field diff on the Mac and read the risky fields to my pendant so I can approve exactly that draft."
- **useful because:** Authenticated browser sessions can reach forms, but today the owner cannot safely delegate repetitive entry while retaining precise control over what will be submitted. This combines browser reach with Mac visual review and pendant confirmation without granting blind submission.
- **path:** browser → mac-bridge → relay → pendant
- **model tier:** Background model to map the request to fields and detect anomalies; realtime only for the short approval exchange.
- **latency:** Draft in under 15 seconds for a normal form; diff rendering under 2 seconds; no submit until explicit approval.
- **cost:** About $0.02–$0.10 per form, dominated by field interpretation and validation; deterministic forms should be cheaper.
- **security:** Never expose passwords, payment numbers, or hidden fields in the diff or spoken summary. Draft data must remain scoped to the enrolled tab and expire. Submission requires an exact one-time approval bound to a content hash; changed fields invalidate it.
- **missing:** Typed browser form extraction and draft-fill operations; A redacted field-diff renderer on the Mac; A content-hash-bound approval handshake from pendant to browser; Browser-side submit isolation that rejects stale or altered approvals

### "Tell me which decisions I made before about this project, with the date, the evidence, and whether I later changed my mind—rather than giving me a generic memory answer."
- **useful because:** The owner repeatedly has to reconstruct decisions from conversations, notes, browser work, and Mac jobs. A decision ledger would distinguish an idea from a committed choice, preserve provenance, and surface later reversals so the system stops repeating settled debates.
- **path:** relay → mac-bridge → browser → pendant → dashboard
- **model tier:** Background model for extracting candidate decisions and contradictions; realtime only to answer a focused lookup.
- **latency:** Index new evidence asynchronously within 1 minute; answer a lookup in under 3 seconds.
- **cost:** About $0.01–$0.05 per indexed evidence bundle, dominated by extraction; lookups should be cheap retrieval plus short synthesis.
- **security:** Store provenance pointers and short redacted excerpts rather than full transcripts. Private browser pages and secrets must not enter the ledger. A proposed decision must never be treated as an instruction until explicitly confirmed.
- **missing:** A typed decision object with status (proposed, accepted, rejected, superseded), scope, timestamp, and evidence links; Cross-surface event ingestion from relay conversations, Mac journals, browser results, and pendant bookmarks; Contradiction detection and explicit owner confirmation for changing a committed decision; A dashboard and pendant query surface that cite evidence without replaying sensitive content


## What it asked for

_Nothing._
