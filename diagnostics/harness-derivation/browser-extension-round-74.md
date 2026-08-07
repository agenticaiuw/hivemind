# Harness derivation — browser-extension — round 74

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser bridge live readiness** — Safari is currently not reporting online; only the offline home-chrome registration appears in /browser/status. There are 5 pending browser commands, while three persisted sessions point to stale Safari tabs from earlier probes (time.is and test forms).
  - evidence: GET /browser/status returned online:false, devices=[home-chrome offline], pendingCommands:5; GET /browser/sessions returned stale tabIds 320512, 230928, 229550 with lastUsedAt 06:26–05:40.

## Capabilities it proposed

### "“I’m looking at this page—tell me what matters, and remember which page I mean while we work on it.”"
- **useful because:** Today a pendant request cannot reliably refer to the authenticated Safari tab the owner is viewing. This creates a new cross-surface handoff: Safari supplies the active tab and selected/visible content, the Mac extracts and cites it, the relay keeps a short-lived task reference, and the pendant answers follow-ups like “what’s the deadline?” without making the owner repeat a URL. It is especially useful for private dashboards, tickets, and forms that public web search cannot access.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard-ux
- **model tier:** Use the realtime model only for the short spoken answer and disambiguation; use a cheaper background text model for page extraction, normalization, and follow-up index building.
- **latency:** Initial capture and concise answer within 3–6 seconds; follow-up answers under 2 seconds while the task reference is warm.
- **cost:** Usually one small extraction call plus a short realtime turn (roughly $0.01–$0.05 depending on page size/audio); DOM text and compact citations dominate context, not screenshots.
- **security:** Only read the explicitly active Safari tab (or owner-selected tab), never all logged-in tabs by default. Keep a task-scoped reference with URL/title, tab/session ID, selected regions, source hashes, and a short TTL; do not persist raw page text or secrets. Show the source title/domain in the spoken answer and dashboard. Any follow-up form fill remains draft-only and stops before submission.
- **missing:** An extension command/result that reports active tab plus selection/viewport extraction as one atomic snapshot; A relay-to-Mac task-reference handoff keyed to the pendant conversation, with TTL and revocation; A compact citation-aware page extraction/index layer for follow-up questions; A pendant intent that resolves deictic references such as “this page,” “that button,” and “the deadline here”

### "“Save this private page for me so I can ask about exactly what it said later, even if the site changes or I’m offline.”"
- **useful because:** An authenticated page is often transient: dashboards update, tickets disappear, and browser sessions expire. The owner should be able to preserve a precise, local-only evidence snapshot from Safari and later ask the pendant or Mac questions against that snapshot, with the original URL, capture time, and quoted source regions. This is different from watching a page or producing a briefing: it preserves the owner’s exact private view as a deliberate, auditable reference.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → pendant → dashboard-ux
- **model tier:** Use a cheap background model only to build a searchable outline and entity index; use the realtime tier for short spoken retrieval answers. Never send raw authenticated content to the relay unless the owner explicitly asks for remote processing.
- **latency:** Capture in under 3 seconds for a normal page; later answers in 1–2 seconds from the local index, with slower fallback for a large snapshot.
- **cost:** Near-zero recurring API cost when indexed locally; occasional small extraction call, dominated by page size. Encrypted local storage is the main resource cost.
- **security:** Snapshots may contain credentials, financial data, or private work information. Encrypt at rest with a Mac-held key, keep them out of cloud logs and relay memory, apply per-snapshot expiration and deletion, and show domain/time before using one. Permit capture only from the explicitly active tab. Never preserve cookies, passwords, or executable page content. Answers must distinguish captured facts from current live-page facts.
- **missing:** An authenticated browser capture command that returns a stable, sanitized DOM/text-plus-source-region bundle rather than only an ephemeral read result; An encrypted local evidence vault with per-item TTL, deletion, and search/index metadata; A task resolver that lets pendant speech target a named snapshot instead of the current live tab; A dashboard review/delete view and an offline retrieval path from Mac to pendant


## Changes it proposed to its own stack

### `browser-harness` — Add a browser-command lease/recovery controller on top of the existing queue: every queued command gets an expiry, attempt counter, device affinity, and idempotency key; when a device heartbeat disappears, commands move to a visible dead-letter state instead of remaining pending indefinitely. On reconnect, read-only commands may be replayed automatically, while mutations require an explicit resume choice; reconcile late results by commandId and discard duplicates. Expose queue health (stale count, oldest age, last heartbeat, replayability) to the Mac status/dashboard and clear the five currently stranded pending commands through this state machine rather than silently retrying them.
- **owner gets:** The owner will not have browser work silently hang—or accidentally happen twice after Safari reconnects. They can see whether a private-page task is waiting, safely recover reads, and know exactly which changes did or did not occur after closing the lid or losing the extension.
- effort: Medium: browserBridge queue schema/state transitions, heartbeat-triggered sweeper, result reconciliation, dashboard/status fields, and extension reconnect tests.  ·  risk: A late extension result could arrive after expiry; commandId/idempotency reconciliation must mark it as late and never apply a duplicate mutation. A read replay may see changed page content, so retain timestamps and label it as a fresh observation. Recovery is deleting/dead-lettering only queue metadata, not page data.
- cost: Negligible API cost; one small D1/local JSON record per command plus periodic sweeper requests.  ·  latency: No added latency on healthy commands; reconnect recovery adds one heartbeat/queue reconciliation round.
- security: Preserve device/session affinity and avoid replaying mutations automatically. Queue metadata should exclude page contents and redact URLs where configured.
- depends on: Existing browser command request IDs, tab/session affinity, and typed results (chg-14accc01); A durable browser job runner or equivalent command persistence (chg-16bc5dee); Browser heartbeat/poll status


## What it asked for

_Nothing._
## Its own summary

Recorded a new capability: deliberate, encrypted local snapshots of authenticated Safari pages that remain queryable from the pendant/Mac after the site changes, session expires, or the owner goes offline. It requires a sanitized stable capture format, encrypted evidence vault with TTL/deletion, snapshot-targeted pendant resolution, and local offline retrieval.

**Biggest unknown:** The exact Safari extension APIs available for exporting a sanitized DOM/source-region bundle; no further discovery is available this round.

