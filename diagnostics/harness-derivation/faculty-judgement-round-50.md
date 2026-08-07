# Harness derivation — faculty-judgement — round 50

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“When you tell me something is done, make sure it really happened; if a device is offline or permission is missing, tell me plainly and keep the task resumable.”"
- **useful because:** The owner has already experienced failed Gmail/GitHub/calendar/browser requests and currently has an online Mac bridge but no trusted GUI reachability. This prevents a dangerous false sense of completion while preserving work instead of making them repeat instructions. It needs the pendant for immediate, concise disclosure; relay for durable job state; Mac and browser for independent receipts; and judgement to reconcile contradictory evidence.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use a cheap background model to normalize receipts and classify state (confirmed, prepared, blocked, unknown); reserve realtime only for the one-sentence pendant response and follow-up question. No expensive reasoning is needed unless receipts conflict.
- **latency:** Speak an initial truthful status within 1 second from local/relay state; reconcile late Mac/browser receipts in the background and notify only when the state changes. A resumed job may take minutes, but must expose an ETA and checkpoint.
- **cost:** Low: roughly one background model call per completed/failed job, dominated by receipt normalization rather than generation; realtime cost only when the owner is actively asking.
- **security:** Receipts may contain private URLs, email subjects, or screen data and must stay in the authenticated relay/Mac store with short retention. Never infer success from an intention, queued command, or untrusted GUI observation. Sending mail, deletion, purchases, and form submission still require confirmation; a blocked task may be resumed only from its saved checkpoint.
- **missing:** A durable cross-surface outcome schema with correlation ID, precondition result, action attempt, independent verification, timestamp, and expiry; A strict spoken-state policy that distinguishes confirmed, prepared, blocked, and unknown in one short sentence; Receipt reconciliation when Mac accessibility/screen-recording or browser extension is offline, plus resumable checkpoints and owner-visible history; A pendant notification path for a late transition (for example, 'still blocked' to 'confirmed') without interrupting focus

### "“Fix the connection so you can act on my Mac again, and tell me exactly what I need to approve.”"
- **useful because:** Today the Mac bridge is online but Accessibility and Screen Recording are false, so a confident-looking GUI action cannot reach the screen; the browser extension is also offline with pending commands. The owner should get a guided, bounded recovery rather than repeated failed requests or a technical error.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-action
- **model tier:** Deterministic diagnostics and a cheap classifier should identify the missing permission/bridge step. Realtime is used only to explain the next single approval in the owner's preferred short sentence; no background large-model call is needed.
- **latency:** Diagnose within 2 seconds, open the relevant macOS Settings or extension reconnect page only after owner approval, and poll for readiness every 2 seconds for at most 2 minutes. Stop and leave a resumable recovery state if the owner walks away.
- **cost:** Near-zero model cost; mostly local status polling and one spoken response. A small background call is optional only to translate raw diagnostics into owner language.
- **security:** Never grant permissions, upload screenshots, or bypass macOS consent. Opening Settings is reversible; reconnecting the browser bridge must show the requested scopes and preserve pending commands without executing them. Sensitive diagnostics stay local/relay and expire quickly.
- **missing:** A typed readiness diagnostic with per-permission remediation instructions and verified post-change state; A safe Mac action for opening the exact Privacy & Security pane and a browser-extension reconnect handshake; A pending-command quarantine that prevents old browser commands from running until the owner reviews them; A concise pendant recovery flow with timeout, cancellation, and a final verified test action

### "“If I say yes to this, what else does it affect—and what is the least disruptive alternative?”"
- **useful because:** The owner can currently inspect individual calendars, messages, files, and logged-in pages, but cannot ask the hive to reason across them before making a commitment. This would expose hidden collisions, preparation work, travel/time costs, and downstream obligations before the owner agrees to something.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-terminal → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use a cheaper background reasoning model to build a bounded impact graph from current calendar, mail, notes, files, and authenticated pages; use realtime only to answer the owner’s spoken question and summarize the top two consequences.
- **latency:** Give a preliminary answer in under 5 seconds from cached state, then refine within 30 seconds if private browser or Mac sources need to be read. Never silently change a calendar, send a reply, or accept an invitation.
- **cost:** Moderate background cost, dominated by retrieving and deduplicating private sources; one compact graph-analysis call per question. Reuse a short-lived impact graph for follow-up questions to avoid resending context.
- **security:** This crosses highly private sources and may infer sensitive relationships or commitments. Keep source excerpts local or in encrypted relay storage, show citations and freshness, exclude secrets by default, and require explicit confirmation before any proposed change is applied.
- **missing:** A temporal obligation-and-dependency graph that links people, commitments, places, documents, and deadlines across Mac and authenticated browser sources; A counterfactual evaluator that can compare proposed choices without mutating real calendars or accounts; A source-cited impact packet with confidence, freshness, and explicit unknowns; A compact pendant interaction for choosing among alternatives or asking one clarification question

### "“Before you use another device or service, show me the smallest amount of my information you need to share, and let me approve or redact it.”"
- **useful because:** The hive can reach private browser sessions, the Mac, a relay, and a wearable, but today the owner cannot see or control the boundary between those surfaces. This gives them useful cross-device assistance without requiring blanket trust or sending full pages, screenshots, transcripts, or credentials.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → mac-terminal → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use deterministic field-level classification and redaction first; use a cheap background model only to summarize why each field is needed. Realtime reads a compact approval card, not the sensitive payload.
- **latency:** Generate a data-minimization preview in under 2 seconds for known workflows and under 10 seconds for an unfamiliar task. Once approved, execution proceeds without repeating the entire sensitive context to the realtime model.
- **cost:** Low to moderate: classification and redaction are primarily local; one small model call for an unfamiliar data-flow explanation. Savings come from transmitting fewer tokens and avoiding screenshots.
- **security:** The preview itself must not reveal redacted secrets. Store approvals as narrowly scoped, expiring grants tied to a job, destination, fields, and purpose; never permit credentials or secret values to cross surfaces. Destructive actions retain their separate confirmation requirement.
- **missing:** A typed data-flow manifest for every tool and surface, including destination, purpose, fields, retention, and model visibility; Local secret/PII detection and reversible redaction before relay or browser transfer; A pendant-sized approval/redaction UI with deny, approve-once, and approve-for-this-job choices; Audit records proving exactly what crossed each boundary and automatic expiry of the grant


## Changes it proposed to its own stack

### `integration` — Add a cross-surface Truth Contract to every job and action: before execution record required preconditions; during execution attach correlation IDs to relay, Mac, browser, and pendant events; after execution require an independent verification event from the target surface. Normalize outcomes to confirmed, prepared, blocked, expired, or unknown. A queued command, HTTP 200, screenshot, or model narrative alone can never become confirmed. Persist a resumable checkpoint and emit a late status transition when an offline surface reconnects.
- **owner gets:** They will stop hearing 'done' when nothing reached the screen, and they will not lose a half-finished task when the bridge or browser returns. This is especially valuable during the current accessibility=false and browser-extension-offline state.
- effort: Medium-high: shared event schema and idempotency across relay, Mac bridge, browser bridge, job runner, and spoken response policy; migration adapters for existing receipts.  ·  risk: Some legitimate actions will be reported unknown until a verifier is added, which feels slower. Recover by showing the exact blocker and allowing explicit retry; never auto-retry irreversible actions.
- cost: Negligible storage and one cheap normalization pass per job; no extra realtime call unless the owner asks for explanation.  ·  latency: Initial acknowledgement unchanged; final confirmation may wait for target-surface verification or reconnect. Background reconciliation avoids blocking conversation.
- security: Improves safety by preventing unverified claims; receipts need redaction, TTL, and access control because they can expose private page content and action parameters.
- depends on: durable job/event persistence; Mac and browser correlation IDs; target-surface verification hooks; a spoken four/five-state outcome policy


## What it asked for

_Nothing._
