# Harness derivation — mac-planner — round 56

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-planner round 56 live readiness** — Mac agent is reachable and FULL_CONTROL_MODE is on, but not ready: Accessibility trusted=false and Screen Recording granted=false. Browser extension is offline with 3 pending commands. Newly granted mac_readonly_inspect and mac_read_sources return 'schema but has no implementation yet', so they cannot currently provide inspections or Calendar/Mail reads.
  - evidence: GET /ops/status HTTP 200 at 2026-08-07T10:36Z; GET /browser/status HTTP 200; direct calls to mac_readonly_inspect and mac_read_sources returned implementation-missing errors.

## Capabilities it proposed

### "“Even when my browser is closed or offline, answer questions about the private pages I previously chose to make available—tell me exactly when the information was captured, show the source link and evidence, and tell me when it may be stale.”"
- **useful because:** Today authenticated browser knowledge disappears when the extension is offline, while sending whole page contents to a cloud relay would be an unacceptable privacy tradeoff. An owner-selected, freshness-limited private cache would let the pendant answer continuity questions during travel or a bridge outage without pretending that old information is current.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Use deterministic extraction and freshness checks for capture, lookup, and staleness. Use a background small model only to normalize a page into explicitly selected fields; use realtime only when the owner asks by voice. Never spend the expensive tier on synchronization.
- **latency:** Capture should finish within 2–5 seconds after a selected page is stable; an offline lookup should return a cited answer in under 3 seconds, with a clear stale/ unavailable result if evidence is insufficient.
- **cost:** Usually near-zero model cost for structured fields and local search; occasional gpt-4.1-mini normalization, roughly fractions of a cent per page. Storage and relay sync are the dominant costs, but retain only compact encrypted records rather than HTML.
- **security:** The owner must explicitly select pages/fields and retention windows. Store page evidence and credentials only on the Mac in an encrypted local vault; relay receives encrypted blobs or opaque hashes, not plaintext private content. Bind each record to account, URL, tab/session, capture time, and expiry; redact secrets and form values. Pendant speech should quote only the minimum matching evidence. Require confirmation before refreshing or taking any action based on cached data.
- **missing:** An owner-controlled capture API in the browser extension that emits selected structured fields plus source/evidence hashes; An encrypted Mac-local private-cache service with field-level TTL, deletion, export, and provenance; A relay sync protocol for ciphertext and revocation, with no plaintext page contents; A pendant query/receipt path that distinguishes live browser evidence from cached evidence; Dashboard controls for selecting fields, retention, and immediate purge


## Changes it proposed to its own stack

### `integration` — Add a cross-surface degraded-mode coordinator for Mac/browser jobs. Before any browser-dependent plan runs, it checks the bridge heartbeat and queue age; if the browser is offline it immediately (a) cancels/coalesces stranded duplicate commands, (b) marks authenticated steps as queued rather than retrying for 45 seconds, (c) executes any independent Mac-native/public steps through the Mac or relay, and (d) sends the pendant a compact status receipt with what completed, what is waiting for the browser, and a retry/cancel handle. When heartbeat returns, it resumes only idempotent steps using the existing request/session affinity and emits one final receipt. This is planner-level fallback, not another browser watcher.
- **owner gets:** The owner gets a useful partial result in seconds instead of a silent 45-second failure, and can leave the Mac without losing work. A spoken 'browser is offline; calendar draft is ready, portal lookup is queued' is materially better than repeated dead retries. It uses the pendant for immediate awareness, the always-on relay for queueing/notification, the Mac for independent work, and the browser bridge only when authenticated access is actually available.
- effort: Medium: coordinator state machine in relay/local-agent, health/heartbeat timestamps, idempotent queue coalescing, planner route annotations, and pendant receipt event. Add integration tests for offline, reconnect, duplicate, and cancellation paths.  ·  risk: A stale heartbeat could cause a false offline decision or resume against a changed tab. Mitigate with short heartbeat TTL, explicit session/tab identity, idempotency keys, and never auto-resume irreversible submit/send steps. Queue metadata may reveal private task names to the relay; encrypt or minimize payloads. Recovery is cancel-and-replan from the last receipt.
- cost: Low background compute and D1/local storage; one small relay notification per state transition. No realtime-model call needed for health decisions; use a cheap classifier only to summarize mixed receipts if necessary.  ·  latency: Offline detection and user receipt under 1–2 seconds instead of ~45 seconds. Reconnect adds one heartbeat interval before resumption; independent Mac steps proceed immediately.
- security: Keep authenticated page contents local to the browser/Mac; relay stores opaque job IDs, step classes, and redacted status only. Require fresh browser session proof before resuming private steps; do not weaken the owner's existing maximum-access policy for Mac actions.
- depends on: A real browser heartbeat/poll implementation and a bounded cleanup endpoint for the 3 currently stranded commands; Implementation of mac_readonly_inspect and mac_read_sources (schemas are granted but currently unimplemented); A shared job receipt/undo identity across relay, Mac, and pendant; Existing browser request IDs, tab/session affinity, and idempotency work

### `dashboard-ux` — Add a permission-repair walkthrough driven by live readiness state. When Accessibility or Screen Recording is missing, the Mac agent exposes exact actionable remediation (open the relevant System Settings pane, identify AI Pendant Agent, wait for the owner to toggle it), then re-probes and records which capability became available. The relay sends a short pendant prompt and the Mac dashboard shows a single 'verify again' action; it must not claim ready merely because requiredMissing is empty.
- **owner gets:** Today the agent reports ready=false while the owner has no clear path from failure to fix, and browser jobs time out. A guided repair takes the owner directly to the right setting and confirms success, turning a one-time setup problem into a few understandable clicks.
- effort: Small to medium: readiness reason codes, deep links to macOS Privacy & Security panes, a verify endpoint/UI, and redacted state receipts to relay/pendant.  ·  risk: System Settings URLs can change across macOS versions and the owner may grant more access than intended. Show the exact permission and why it is needed, never toggle it automatically, and fall back to a manual instruction. If verification is stale, retain ready=false.
- cost: Negligible API cost; no model call required. A few local probes and one relay status event.  ·  latency: Minutes saved during setup; verification should complete within a few seconds after the toggle.
- security: Improves transparency without expanding authority. Screen Recording and Accessibility remain explicitly owner-granted; relay receives only booleans/reason codes, never screenshots or UI contents.
- depends on: A working local readiness probe implementation; mac_readonly_inspect implementation is useful but not strictly required if /ops/status exposes stable reason codes; A small Mac dashboard/pendant status event route


## What it asked for

_Nothing._
## Its own summary

Round 56 established that the Mac agent is reachable and fully privileged by policy, but operationally not ready because Accessibility and Screen Recording are ungranted. Browser transport is offline with 3 pending commands; two recent browser jobs each spent ~45 seconds before failing. The newly granted mac_readonly_inspect and mac_read_sources schemas exist but have no implementation, so live UI/app inspection and Calendar/Mail reads still cannot run. I recorded these findings and proposed two changes: a cross-surface degraded-mode coordinator that fast-fails/queues browser steps while completing independent Mac work, and a guided permission-repair walkthrough that accurately explains and verifies missing macOS permissions.

**Biggest unknown:** Whether the browser bridge can be made to heartbeat/poll and clean its 3 stranded commands without a new implementation; and when the granted read-only Mac inspection/source tools will actually be wired up.

