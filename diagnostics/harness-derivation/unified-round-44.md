# Harness derivation — unified — round 44

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “mark this,” save where I am and let me resume later from the pendant with the right apps, browser tabs, and a short spoken recap."
- **useful because:** Interruptions currently destroy context. This creates a durable, privacy-aware handoff: the pendant captures the intent and timing, the Mac snapshots reversible workspace state, the browser records only the authenticated tabs actually involved, and the relay stores a compact checkpoint. Later the owner can say “resume my last thread” and get back to work rather than reconstructing it.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the realtime tier only for the two short spoken turns (mark/resume). Use a cheaper background model to summarize the checkpoint and rank the minimal tabs/apps to restore.
- **latency:** Acknowledge the mark locally in under 300 ms; persist the checkpoint within 2 s. Resume should speak a one-sentence recap within 3 s, then restore reversible state asynchronously with progress receipts.
- **cost:** Roughly $0.01–$0.05 per checkpoint/resume, dominated by summarization; most captures should be deterministic metadata and need no model call.
- **security:** Authenticated URLs, titles, and snippets may be sensitive. Store encrypted, apply a short default TTL, redact secrets/forms/password fields, and bind checkpoints to the owner and originating Mac/browser session. Never auto-submit or send anything on restore; require confirmation for destructive or external actions. The owner should be able to delete a checkpoint from the pendant.
- **missing:** A durable checkpoint schema spanning pendant event, relay job, Mac workspace snapshot, and browser tab/session IDs; A local 'mark this' button/gesture and offline spool so the capture survives a dropped link; Mac APIs to snapshot and restore only the opened apps/windows without stealing focus; Browser support for authenticated tab snapshot with redaction and session reattachment; An end-to-end resume receipt that reports what was restored and what could not be restored

### "If my Mac crashes, loses power, or is replaced, reconstruct my unfinished work on the next available machine and tell me exactly what was recovered, what was missing, and what I need to redo."
- **useful because:** A crash currently turns active work into forensic recovery. This would make the relay and pendant a durable continuity layer: preserve task intent and safe local artifacts before failure, reconnect browser sessions where permitted, and give the owner a trustworthy recovery brief instead of silently losing progress.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic manifests, hashes, and job receipts for most recovery. Use a cheaper background model only to summarize gaps and generate the spoken recovery brief; reserve realtime for the owner's short recovery conversation.
- **latency:** On detecting loss of the Mac, persist the last known manifest within seconds and notify the pendant only after confidence that the outage is real. On reconnection, produce a recovery inventory in under 10 seconds; large files and workspace restoration may continue asynchronously.
- **cost:** Usually under $0.02 per incident, dominated by one short background summary. Storage and hashing dominate operational cost, not model tokens.
- **security:** Workspace paths, document metadata, browser session identifiers, and possibly unsaved content are sensitive. Encrypt manifests, keep content opt-in and locally scoped, never copy credentials or cookies to the relay, bind recovery to an authenticated replacement device, use explicit per-folder policies, and require confirmation before reopening or syncing anything externally visible.
- **missing:** A crash-tolerant, encrypted workspace manifest and artifact journal on the relay; Mac bridge support for incremental local snapshots, unsaved-document detection, and hash-based recovery receipts; A browser recovery protocol that reattaches permitted sessions without exporting cookies or secrets; Device enrollment and replacement authentication for a new Mac; A pendant-visible recovery state machine that works when the Mac is offline; A dashboard showing recovered, unverifiable, and irrecoverably missing items with exact reasons


## Changes it proposed to its own stack

### `integration` — Add a signed, append-only Context Checkpoint protocol. A pendant mark event carries checkpointId, monotonic sequence, local timestamp, link state, and optional 5-second pre/post audio hash (not raw audio by default). The relay accepts it idempotently, asks the Mac bridge for a workspace manifest (app/window IDs and document paths) and the browser bridge for redacted metadata of only the active task tabs, then writes a compact checkpoint with per-item provenance, TTL, and restore safety class. Resume returns a typed plan: safe-to-restore items execute automatically; focus-changing or external actions remain staged. Emit a completion receipt with restored/skipped/expired items and reason codes.
- **owner gets:** The owner can stop mid-task with one gesture and reliably return later, even after a dropped connection or machine restart, without the assistant guessing which tabs and files mattered.
- effort: Medium-high: protocol and durable storage, Mac/browser bridge adapters, redaction tests, and pendant event plumbing.  ·  risk: Stale paths, closed sessions, or sensitive tab leakage could restore the wrong context. Mitigate with TTLs, owner-visible manifests, session binding, idempotency, and a dry-run resume preview; recover by leaving the current workspace untouched when any required item is ambiguous.
- cost: Low storage and API cost; one small background summarization call per checkpoint at most. No new hardware required.  ·  latency: Mark acknowledgement remains local; checkpoint commit is asynchronous. Resume preview under 3 seconds on an online Mac, with restoration continuing in the background.
- security: High-value metadata is encrypted in transit and at rest, secrets/forms are excluded, raw audio is opt-in and short-lived, and all cross-surface records carry sensitivity labels and deletion timestamps.
- depends on: A durable relay job/receipt store with idempotency; Mac workspace snapshot/restore endpoint; Browser authenticated-tab metadata endpoint with redaction; Pendant offline event spool or durable mark gesture

### `memory` — Introduce a crash-recovery journal separate from ordinary conversational memory. The Mac bridge emits encrypted append-only checkpoints for active jobs, unsaved document hashes, browser task identifiers, and last acknowledged action receipts; the relay stores only policy-approved metadata and encrypted artifact fragments with per-item TTLs. On reconnect, a replacement Mac presents a device-bound challenge, downloads a signed recovery manifest, verifies hashes locally, and reports recovered/unverifiable/missing items without copying browser cookies or credentials.
- **owner gets:** After a crash or replacement, the owner gets an honest, actionable reconstruction of unfinished work instead of a vague claim that the assistant remembers it.
- effort: High: filesystem journaling, unsaved-document adapters, secure replacement-device enrollment, browser session-safe reattachment, and failure-injection testing.  ·  risk: Journaling could leak sensitive work or restore stale files. Mitigate with folder-level opt-in, encryption, short TTLs, content hashes by default, signed manifests, and a non-destructive dry-run before restoration.
- cost: Moderate relay storage and hashing bandwidth; negligible model cost. Artifact fragments should be capped and garbage-collected aggressively.  ·  latency: Small ongoing local I/O overhead; crash detection and manifest generation should be near-real-time, while full recovery is asynchronous.
- security: Adds sensitive recovery metadata to the relay, so encryption, device binding, revocation, audit logs, and explicit data-retention controls are mandatory. Cookies, tokens, passwords, and raw browser credentials must never leave the originating device.
- depends on: Durable relay storage with encryption and per-item retention; Mac bridge filesystem and application snapshot APIs; Replacement-device enrollment and revocation; Browser session reattachment that does not export credentials; Pendant offline status and recovery notification support


## What it asked for

_Nothing._
