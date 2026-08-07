# Harness derivation — mac-planner — round 88

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-planner round 88 live readiness** — The newly granted mac_readonly_inspect and mac_read_sources tools are present in schema but have no implementation; every call returns that exact error. GET /ops/snapshot confirms relay and Mac bridge reachable, browser extension offline with 5 pending commands, Accessibility and Screen Recording ungranted, and computer-use loop disabled.
  - evidence: mac_readonly_inspect and mac_read_sources calls returned 'This tool was granted a schema but has no implementation yet'; GET /ops/snapshot HTTP 200 payload at 2026-08-07T12:21Z

## Capabilities it proposed

### "Pause this and let me continue later. When I say “continue,” restore the exact work context across my pendant, Mac, and logged-in browser, tell me what changed while I was away, and resume only the next safe step."
- **useful because:** Today a long task fragments across voice, files, apps, and authenticated tabs. A durable resume capsule would let the owner leave without losing the active goal, evidence, drafts, or pending decisions, then recover on whichever device is available. It is more than an async job receipt: it restores the cross-surface working set and detects drift before acting.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use the realtime model only for the short spoken pause/continue exchange; use a cheaper background model to serialize checkpoints, compare resumed state, and summarize drift. The Mac/browser executors perform restoration; the relay owns durable state and delivery.
- **latency:** Pause acknowledgment under 1 second, checkpoint commit under 3 seconds when connected; continue brief under 5 seconds, then restore reversible context in under 10 seconds. If the Mac or browser is offline, return a partial capsule and retry without losing it.
- **cost:** About $0.01–$0.05 per continue depending on evidence size; background summarization and browser extraction dominate, not the spoken acknowledgment. Storage is small JSON plus bounded snippets and optional audio pointers.
- **security:** Capsules may contain private browser URLs, mail/calendar snippets, draft text, and file paths. Encrypt at rest in relay storage, keep browser contents as hashes/snippet excerpts by default, bind restoration to the original device/tab/session, expire capsules, and never submit/send/delete/buy during restore. Owner policy still requires confirmation before sending mail, deleting files, or buying.
- **missing:** A first-class capsule schema and durable store spanning relay, Mac job records, and browser sessions; Checkpoint hooks that capture goal, pending action, evidence references, app/file context, tab IDs, and last safe step; A drift checker that re-reads current browser/Mac state before resuming and produces a human-readable diff; Pendant command and offline queue for pause/continue plus audio-pointer synchronization; The granted mac_readonly_inspect and mac_read_sources tools currently return “schema but no implementation”; browser bridge is currently offline with five pending commands; A restore coordinator that can rebind browser tabs and invoke Mac actions idempotently

### "Put this task in a private workroom. Use only the tabs, files, messages, and calendar items relevant to it; keep everything else out of context, show me what you included, and erase the workroom when I say “close it.”"
- **useful because:** The current hive can reach many surfaces, but it has no user-visible, end-to-end context compartment. A work task can accidentally inherit unrelated mail, browser tabs, notes, or secrets, and the owner cannot audit or reliably delete the assembled context. This gives the owner a concrete privacy boundary across the pendant, relay, Mac, and browser rather than relying on each agent to remember redaction rules.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use the realtime tier only to clarify the workroom name and speak the inclusion summary. Use a cheaper background model to classify candidates, select relevant evidence, and maintain the compartment manifest; deterministic services enforce inclusion, expiry, and deletion.
- **latency:** Create in under 5 seconds, with a short inclusion preview before work begins. Context updates should be incremental in under 2 seconds; close and purge should acknowledge in under 3 seconds, with asynchronous verification if a surface is offline.
- **cost:** Roughly $0.01–$0.04 per workroom creation or major context update; classification and evidence extraction dominate. Storage is bounded metadata plus selected snippets, not whole-account copies.
- **security:** The workroom itself contains sensitive cross-surface data. Encrypt it, give it an explicit TTL and device/session scope, redact bodies and secrets by default, preserve provenance for every included item, and make close a real deletion request with a verifiable tombstone. Browser mutations, mail sending, file deletion, and purchases remain separate actions and must not be implied by inclusion. If a surface cannot honor deletion, report that clearly instead of claiming success.
- **missing:** A first-class workroom/compartment manifest with allowlisted source IDs, provenance, TTL, sensitivity labels, and deletion status; A relay-side context broker that issues scoped handles rather than copying raw context into every model prompt; Mac and browser adapters that can enumerate candidate items, enforce the workroom scope, and prove which data was read; A pendant command/state protocol for create, inspect, switch, and close while offline, followed by synchronized purge; A dashboard showing included sources, access history, expiry, and any surface that failed to purge; Working implementations of the granted read-only Mac inspection/source tools; they currently return schema-only errors


## Changes it proposed to its own stack

### `integration` — Implement a signed, versioned Resume Capsule coordinator. On pause or any long-running job checkpoint, write a compact manifest containing goal/constraints, last completed action, pending action class, Mac jobId plus receipt, app/file references, browser session+tab IDs with evidence hashes, relay job state, and pendant audio/message offsets. Store immutable checkpoints with a short TTL and append-only transitions. On continue, fan out read-only probes first, compare current state to the manifest, present a concise drift report, and only then replay idempotent open/read/fill-preparation steps; mark every restored step with the capsule ID.
- **owner gets:** The owner can stop mid-task, close the lid, or lose the browser connection and later pick up without guessing what was already done or accidentally repeating a mutation. Drift warnings prevent acting on stale prices, forms, meetings, or files.
- effort: Medium-high: shared schema and relay persistence, Mac job/checkpoint hooks, browser session rebinding, pendant command/state handling, and a small drift/diff service. Start with JSON manifests and receipts before adding richer UI.  ·  risk: Stale or duplicated actions are the main risk. Mitigate with idempotency keys, read-only revalidation, explicit distinction between prepared and committed mutations, expiry, and recovery to a review-only state if any surface changed. If relay is unavailable, retain the last capsule locally and sync later.
- cost: Negligible storage; roughly $0.005–$0.03 for background drift summarization per resume, with browser extraction the dominant cost. No new per-action realtime call.  ·  latency: Adds 1–3 seconds for checkpoint writes and 2–8 seconds for parallel revalidation; avoids much longer manual recovery.
- security: Capsules are sensitive cross-surface metadata. Encrypt and minimize snippets, redact mail bodies by default, scope browser tokens to existing sessions, bind manifests to device identity, and audit reads/restores. Never encode secrets such as captured owner credentials.
- depends on: Durable browser job runner and result stream (chg-16bc5dee remains incomplete); A relay durable capsule endpoint and Mac/browser idempotency-key propagation; Implementation of the newly granted read-only Mac inspection/source tools (currently schema-only); Browser extension recovery/rebinding when Safari bridge is offline; A pendant offline pause/continue queue or equivalent local intent persistence


## What it asked for

### `t14-8v4g` (tool) — mac_resume_capsule
- why: The planner needs one controlled operation to checkpoint and later restore a cross-surface task without manually stitching Mac jobs, browser tabs, and pendant offsets. Existing mac_run_actions can execute actions but cannot atomically persist a manifest, compare state, or resume idempotently.

```json
{
  "operation": "string enum: checkpoint|inspect|resume|discard",
  "capsule_id": "string optional; required for inspect/resume/discard",
  "goal": "string optional; required for checkpoint",
  "constraints": "array of strings optional",
  "pending_action": "object optional, with kind and human_description",
  "mac_job_id": "string optional",
  "browser_session_ids": "array of strings optional",
  "evidence_refs": "array of objects optional, each with source,id,hash",
  "audio_offset": "object optional",
  "ttl_seconds": "integer optional, default 604800",
  "dry_run": "boolean default true",
  "confirmation_token": "string optional"
}
```

## Its own summary

Round 88 produced a new cross-surface Resume Capsule capability and implementation change: pause/continue should checkpoint the pendant intent/audio offset, relay state, Mac job/receipt, local context, and authenticated browser tab/evidence into an immutable manifest; continue must re-probe all surfaces, report drift, and replay only idempotent safe steps. I also queued a precise mac_resume_capsule tool request. Live verification found the Mac bridge/relay reachable, but browser extension offline with 5 pending commands; Accessibility, Screen Recording, and computer-use loop remain unavailable. The newly granted mac_readonly_inspect and mac_read_sources APIs exist only as schemas and return no implementation, so I could not inspect apps/tabs or read Calendar/Mail this round.

**Biggest unknown:** Whether the relay/browser job infrastructure has already begun implementing a durable cross-surface checkpoint schema; the backlog shows durable browser jobs are still incomplete, but no live capsule endpoint was discoverable. I still need working implementations of the granted read-only Mac tools, browser heartbeat/recovery, and a durable capsule coordinator (the queued mac_resume_capsule tool) to make the proposal executable.

