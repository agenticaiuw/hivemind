# Harness derivation — mac-planner — round 136

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac execution reachability and granted read tools** — At 2026-08-07T14:38:38Z the Mac agent is online/full-control but not ready: Accessibility and Screen Recording are false, input reachability failed, and browser extension is offline with 10 pending commands. Newly granted mac_readonly_inspect and mac_read_sources are schemas without implementations, so they cannot yet provide real read-only state.
  - evidence: GET /observe and GET /ops/status returned these values; direct calls to mac_readonly_inspect and mac_read_sources returned 'tool was granted a schema but has no implementation yet'.

## Capabilities it proposed

### "When my browser extension is disconnected, still tell me what you can verify from the Mac, and queue the private-page part to finish automatically when the browser reconnects."
- **useful because:** Today a browser request either blocks for 45 seconds or fails even though Calendar/Mail and local Mac state may still be available. This gives the owner a useful partial answer now, a clear missing-data notice, and an automatic continuation later without pretending the private page was read.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use no model for connectivity, source reads, queueing, or reconciliation; use the cheap background text tier only to merge verified snippets into a short brief. Reserve realtime for the owner's follow-up question.
- **latency:** Return local verified findings and a queued receipt within 1 second; browser continuation runs in the background after heartbeat and should not block the voice turn.
- **cost:** Usually near-zero model cost; metadata and one short background summary dominate. No page body leaves the Mac unless the owner requested that source.
- **security:** Keep authenticated page bodies on the Mac/relay boundary, redact secrets from the partial brief, bind queued work to the original tab/session, and never submit forms or send messages as part of recovery. Report stale or unverified data explicitly.
- **missing:** A durable reconnect/resume worker rather than the current single blocking browser wait; An implemented read-only Mac source/inspection tool (the newly granted schemas currently return no implementation); The reachability/truth envelope proposed this round; Browser heartbeat-triggered delivery to pendant speech and dashboard

### "If I leave my Mac halfway through a task, let me resume it from the pendant later—'continue the draft' or 'finish the research'—with the exact open tabs, files, findings, and next safe step restored."
- **useful because:** Today a long task is tied to one live Mac session; leaving the machine loses the working set or forces a restart. A portable continuation capsule would make the pendant a genuine always-present control surface for work that began on the Mac, without replaying completed actions or exposing unrelated desktop context.
- **path:** mac-bridge → browser → relay → pendant → dashboard
- **model tier:** Use a cheap background model to summarize and compact the task capsule; use realtime only to interpret the pendant's short resume command and answer immediate status questions.
- **latency:** Capture a capsule in under 2 seconds when the task pauses; restore the working set and return a spoken status in under 3 seconds when the owner resumes. Long research or browser work continues asynchronously.
- **cost:** One small background summarization call per pause/resume, typically well below a cent; storage is a few KB per capsule. The dominant cost is only if the owner asks for a fresh synthesis of the preserved sources.
- **security:** Capsules may contain authenticated URLs, draft text, filenames, and private findings. Encrypt them at rest, bind them to the owner's paired pendant and Mac session, apply per-source sensitivity and expiry, and omit page bodies/secrets unless explicitly requested. Resuming must never send, submit, delete, purchase, or overwrite without the existing owner policy for that action.
- **missing:** A portable, encrypted continuation-capsule format with source references, completed action IDs, pending steps, and expiry; A relay endpoint and pendant command for listing, selecting, expiring, and resuming capsules; Mac and browser adapters that can reattach to the saved session/tab/file identifiers and report which references are stale; A reconciliation layer that refuses to replay completed actions and explains when a saved tab or file no longer exists


## Changes it proposed to its own stack

### `relay` — Add a cross-surface reachability/truth layer for every Mac or browser job. Before dispatch, snapshot /observe, /ops/status, and /browser/status; after each action, attach the corresponding receipt plus post-state and classify the outcome as verified, completed-but-unverified, queued-offline, or failed. Relay should never speak 'done' for UI actions when uiActionsWillReachTheScreen=false, and should automatically resume queued browser work after a heartbeat/reconnect using the existing stable action IDs. Persist a compact evidence capsule (jobId, surface, timestamps, state deltas, reason) and expose it to the pendant and dashboard.
- **owner gets:** The owner currently gets false confidence: UI actions report success while Accessibility=false, and browser work can sit in a queue while the extension is offline. They would hear the truth immediately—'queued until Chrome reconnects' or 'completed and verified'—and returning to the Mac would resume without duplicate clicks.
- effort: Medium: a relay/result schema, pre/post probes in the Mac bridge, reconnect worker, and pendant phrasing tests; no new model training.  ·  risk: A stale probe could label a real action incorrectly, or reconnect could replay an action if its ID mapping is wrong. Recover with conservative 'unverified' status, content-addressed action IDs, and the existing receipts/undo history; never infer success from an executor HTTP 200 alone.
- cost: Negligible API cost; a few hundred bytes of D1/R2 metadata per action. Background reconciliation can use a cheap model or no model.  ·  latency: Adds roughly 100–300 ms for local pre/post probes; offline work returns immediately as queued instead of blocking 45 seconds.
- security: Evidence capsules must redact page text, mail contents, secrets, and shell arguments by default; retain only hashes, app/URL origin, and state labels unless the owner asks for detail.
- depends on: Accessibility or screen recording remains optional; without it the system must honestly stay in unverified mode; The existing action receipts/undo implementation; The browser command queue and heartbeat endpoint; A relay-to-pendant result delivery path


## What it asked for

_Nothing._
## Its own summary

Discovered fresh live state: Mac agent is online and full-control, but Accessibility=false, Screen Recording=false, input reachability failed, and the browser extension is offline with 10 pending commands. The newly granted mac_readonly_inspect and mac_read_sources tools are schemas only and still return no implementation. I recorded this finding, notified relay-realtime, and proposed two new pieces: a cross-surface reachability/truth envelope for verified/unverified/queued receipts, and graceful partial browser work that resumes after heartbeat without duplicate actions.

**Biggest unknown:** Whether the orchestrator will implement the granted read-only Mac tools and the browser reconnect worker; until then I cannot independently verify Calendar/Mail/UI state or complete authenticated browser tasks. The owner still must manually grant Accessibility/Screen Recording to AI Pendant Agent if trustworthy UI interaction or vision is required.

