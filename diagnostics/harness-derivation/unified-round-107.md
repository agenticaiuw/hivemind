# Harness derivation — unified — round 107

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **cross-surface read reliability** — Live browser status is offline with 10 pending commands; latest workday briefing explicitly says calendar and mail were not read because this Mac needs Automation grants. Recent browser jobs spent ~45 seconds timing out or failing instead of returning a preflight result.
  - evidence: GET /browser/status => online:false, pendingCommands:10; GET /briefing/latest => Not read calendar/mail — needs an Automation grant; GET /jobs => browser failures with 45s durations and offline/timeout reasons.

## Capabilities it proposed

### "When I ask you to read Gmail, GitHub, my calendar, or another private account, check every reachable surface, tell me exactly which source was accessed and which was unavailable, and leave a cited review brief without pretending a failed read succeeded."
- **useful because:** The owner has repeatedly asked for Gmail, GitHub, calendar, and browser access but received opaque failures. This turns the pendant's short answer into a trustworthy cross-surface result: the relay can speak immediately, the Mac can use granted AppleScript/apps, and the browser can use an authenticated session when online; gaps and stale data are explicit.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension → dashboard
- **model tier:** Use gpt-5.6-luna for source selection, reconciliation, and citation-quality synthesis; use deterministic Mac/browser tools for reads; use gpt-realtime-2.1 only to speak the short result and ask for clarification.
- **latency:** A reachable single source should answer in 5–10 seconds; parallel source checks in 15–30 seconds. If a surface is offline, return partial results immediately and enqueue a retry rather than blocking the owner.
- **cost:** About $0.02–$0.10 per request depending on number of sources and extracted text; most cost is synthesis/context, not deterministic reads. Cached source health and unchanged-page fingerprints should keep routine checks near the low end.
- **security:** Private mail, calendar, and repository content must remain on the authenticated Mac/browser path; send only minimal extracted snippets and metadata to the relay. Never send, delete, or mutate. Show source URL/app, timestamp, freshness, and failure reason; require confirmation before any future draft submission or external action.
- **missing:** A unified read-intent coordinator that fans out to Mac AppleScript/app reads and authenticated browser tabs; Typed per-source receipts with freshness, coverage, and failure categories surfaced to the pendant and dashboard; A durable retry/brief queue for sources that are offline, without claiming completion

### "Set up my private account access once, then verify it: walk me through enabling only the Mail, Calendar, and browser permissions you choose, test each one with a harmless read, and tell me exactly what I can and cannot ask you to access afterward."
- **useful because:** Today private reads fail opaquely because browser connectivity and per-app macOS Automation grants are prerequisites but are not surfaced as a coherent setup experience. The owner should not have to understand TCC, extension polling, bearer routes, or which surface owns a login. A guided, least-privilege setup would turn inaccessible accounts into a verified everyday capability without granting broad computer control.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use the cheaper planner tier for deterministic setup sequencing and permission checks; use realtime only for the pendant's short spoken guidance. No expensive synthesis is needed except to explain an unusual failure.
- **latency:** Initial setup should take under 2 minutes plus the owner's manual permission clicks. Each verification read should complete in under 5 seconds and fail fast if a grant or extension is missing.
- **cost:** Negligible API cost after setup; mostly deterministic health checks and one short spoken response. A small persistent capability manifest avoids repeating setup context.
- **security:** Never request full Accessibility or Screen Recording as part of this flow. Ask only for narrowly scoped Mail/Calendar automation and the browser extension's existing page access. Show every requested permission, keep a signed local manifest of granted scopes, test with non-mutating reads, and require separate confirmation before any write or send. Do not transmit credentials or raw account contents to the relay.
- **missing:** A permission/setup wizard that can open the relevant macOS settings panes and browser extension page, then wait for the owner to approve manually; Per-scope capability manifest with grant state, verification timestamp, and expiry/recheck policy; Harmless read probes for Mail, Calendar, and browser connectivity with actionable error messages; A pendant-friendly setup state and dashboard checklist


## Changes it proposed to its own stack

### `integration` — Implement a privacy-preserving source-read coordinator and typed evidence receipt. Parse a read intent into Gmail/GitHub/calendar source adapters; run reachable Mac AppleScript and authenticated browser reads in parallel with per-source deadlines; normalize each result to {source, account/app, scope, observedAt, freshness, citations, status, failureClass}; reconcile duplicates and publish one brief plus a retry job for unavailable sources. Relay and pendant receive only the compact brief and receipt summary, while raw private content stays on the Mac/browser path. Dashboard exposes coverage and lets the owner retry one failed source.
- **owner gets:** Requests that currently end as an unexplained 'failed' become honest, useful answers: what was checked, what was not, when it was checked, and where to look. The owner can still get a partial spoken answer when the browser is offline or a private app is unavailable.
- effort: Medium: adapters and schema are straightforward; the hard part is source-specific extraction and stable citations, followed by integration tests for offline/timeout/duplicate cases.  ·  risk: A connector could overread private data or mislabel stale content. Enforce least-scope queries, source allowlists, per-adapter timeouts, no mutation verbs, and fail-closed citation/status validation. Recover by discarding the synthesized brief if any receipt is malformed and retrying only the failed adapter.
- cost: Low ongoing API cost: deterministic reads dominate latency, and one small synthesis call handles normalized receipts. Storage is small JSON receipts plus optional short-lived extracted snippets.  ·  latency: Parallel fan-out reduces total time; typical result 5–20 seconds. Offline browser no longer stalls the answer because its branch times out and becomes an explicit queued retry.
- security: Improves security observability: every private read has source, scope, timestamp, and retention metadata; relay gets minimized output rather than credentials or full pages. No send/delete/purchase actions are permitted.
- depends on: A durable job/receipt queue (the existing job runner and receipt/undo pieces need to be wired into this coordinator); Adapters for AppleScript-readable Mail/Calendar/Notes and authenticated browser page extraction; A compact typed context/evidence schema with TTL and redaction policy

### `integration` — Build a verified least-privilege access bootstrapper. Maintain a local capability manifest for each source (Mail, Calendar, browser extension), expose a preflight endpoint returning missing scope plus exact remediation, open the appropriate Settings or extension UI through approved Mac actions, pause for the owner's manual approval, then run a non-mutating probe and persist a signed verification receipt. Make every private-read route consult this manifest and fail immediately with the precise missing prerequisite instead of invoking a 45-second doomed job.
- **owner gets:** The owner gets a one-time setup that explains and proves access, rather than repeatedly asking for Gmail/calendar/browser reads that silently fail. They retain control over every permission and can see exactly what this system is allowed to access.
- effort: Medium. Requires macOS settings deep-link handling, extension health probing, a manifest/receipt schema, and integration tests for denied, revoked, offline, and partially granted states.  ·  risk: Settings URLs may change or a probe may produce a false positive. Treat verification as scoped and short-lived, fail closed on uncertainty, and provide a manual recheck. Never auto-click permission dialogs or broaden an existing grant.
- cost: Very low runtime API cost; a small local manifest and occasional probes. Engineering cost is concentrated in reliable macOS-version handling and test fixtures.  ·  latency: Adds milliseconds to normal reads through a local manifest check; setup takes one owner interaction plus seconds for probes. Eliminates long waits on impossible requests.
- security: Reduces privilege sprawl and makes grants auditable. Accessibility and Screen Recording remain out of scope. Raw account data stays on the Mac/browser path; only capability status and minimal receipts reach the relay.
- depends on: A local manifest storage location with revocation/expiry handling; Read-only probes for Mail, Calendar, and browser extension polling; A safe Mac action for opening permission settings; Dashboard and pendant rendering for setup state


## What it asked for

_Nothing._
