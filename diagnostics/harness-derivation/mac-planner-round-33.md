# Harness derivation — mac-planner — round 33

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-planner live readiness** — Mac agent v0.5.0 is reachable with FULL_CONTROL_MODE and relay online, but the browser bridge is offline with 2 pending commands; Accessibility and Screen Recording permissions are not granted, so computer-use/UI automation is not ready. Calendar/Mail/Safari automation grants are present in the host's cached permission report.
  - evidence: GET /ops/status at 2026-08-07T09:33Z returned fullControlMode:true, browserExtension.online:false, pendingCommands:2, accessibility.trusted:false, screenRecording.granted:false, and relay.reachable:true.

## Capabilities it proposed

### "“Why couldn't you do that, and fix whatever is preventing it if you can?”"
- **useful because:** The Mac currently reports a real blocked state—Accessibility is untrusted and Screen Recording is missing—while the browser bridge is offline. Today these failures surface as opaque automation errors. This gives the owner a spoken diagnosis, a concrete repair path, and an automatic re-test when the bridge or permissions recover.
- **path:** pendant voice request → relay routes the diagnostic to the paired Mac → Mac local agent runs read-only readiness checks and opens the exact System Settings pane when the owner asks → browser bridge heartbeat confirms extension recovery → relay sends a short completion/failure receipt back to the pendant
- **model tier:** Use a cheap background/text model for classifying the structured readiness report and composing the repair checklist; reserve realtime only for the owner's live spoken request and the final short notification.
- **latency:** Initial diagnosis in 1–2 seconds; opening a System Settings pane is immediate; recovery polling is low-cost background work and should stop after a bounded TTL.
- **cost:** Usually under $0.01 per invocation; dominated by one small structured-model call. Heartbeats and local checks are negligible.
- **security:** Permission status and app/session names leave the Mac only as minimal structured metadata. Never transmit screenshots, page contents, or credentials. Opening System Settings is reversible; changing a permission remains an OS-controlled owner action. Keep a repair log with no sensitive window text.
- **missing:** A typed readiness diagnostic endpoint that reports blocker codes and exact remediation URLs; A Mac permission-repair planner that can launch System Settings without pretending it granted permission; A relay retry/watch state that re-runs readiness checks after the owner repairs a blocker; A browser bridge self-test/heartbeat that distinguishes extension installed, polling, paired, and tab-attached


## Changes it proposed to its own stack

### `model-routing` — Add a cross-surface readiness-and-lease router. The Mac agent periodically publishes signed capability facts (bridge online/polling, accessibility, screen recording, app/session availability, network reachability, last-seen and lease expiry) to the relay. Before dispatch, the relay classifies each step as relay-public, Mac-local, or authenticated-browser work: it executes immediately where possible, routes public reads around an offline browser, and persists private-browser work as a resumable job instead of invoking the current 45-second blocking bridge wait. When the lease returns, the Mac claims the job with an idempotency key, emits progress and a typed receipt, and the relay delivers a one-sentence pendant notification; if prerequisites remain unavailable, it reports the exact missing prerequisite rather than 'failed'.
- **owner gets:** A request spoken while the owner is away will stop mysteriously timing out. Public questions still get answered when Chrome is closed, while private work waits safely for the owner's Mac/browser and resumes once it is genuinely available. The pendant can say 'queued—browser bridge offline' or 'done—draft saved' instead of making the owner guess.
- effort: Medium-high: readiness schema and signed heartbeat in the Mac bridge, D1 durable job/lease state and retry worker in relay, planner routing policy, browser command adapter changes, and end-to-end offline/online tests.  ·  risk: A stale lease could cause duplicate work or a job claimed by the wrong Mac; use owner/device pairing, short leases, idempotency keys, and receipts. A queued private request may expose metadata (not page contents) to relay; encrypt payloads or store only an opaque reference until the paired Mac claims it. Recovery is lease expiry plus retry/dead-letter with a clear pendant notice.
- cost: Small background relay/D1 and heartbeat cost; one cheap routing decision per request. Avoids wasting a 45-second browser wait and avoids spending the realtime model on repeated failure narration.  ·  latency: Immediate readiness decision (<100 ms locally); online work starts at once. Offline private work becomes asynchronous, with completion latency determined by the next bridge heartbeat rather than a false 45-second timeout.
- security: Improves security by making device/session binding explicit and never sending authenticated page content through the public fallback. Requires signed, paired-device heartbeats, encrypted queued payloads, TTL/deletion policy, and audit receipts.
- depends on: chg-14accc01 async/resumable browser polling (or an equivalent nonblocking adapter); A relay durable job/lease store and paired-device identity; Mac bridge heartbeat extended with permission and browser-session state

### `integration` — Create a federated activity ledger that joins one owner request across pendant utterance/audio ID, relay model decisions, Mac jobs, browser tab operations, and final delivery. Each node emits append-only event envelopes with a shared request ID, parent/child step links, monotonic sequence, local timestamps plus UTC, data-sensitivity class, and outcome. The relay periodically compacts these into a human-readable causal timeline and exposes a redacted export on the Mac; missing or contradictory events are shown as unknown rather than inferred. This is a cross-node ledger, not another per-job receipt or Mac action history.
- **owner gets:** The owner can ask, “What happened to the thing I asked while I was away?” and receive one honest answer: what the pendant heard, which body acted, which browser page or file was touched, what failed, and what remains. Today receipts are fragmented by surface, so a successful local step can look like an unexplained overall failure.
- effort: High: define an event envelope and correlation protocol, add emitters to pendant/relay/Mac/browser, persist a bounded encrypted event stream, implement clock-skew and retry deduplication, and build a concise spoken/timeline renderer.  ·  risk: A ledger can become a sensitive behavioral record. Encrypt at rest and in transit, minimize content to hashes/labels by default, apply short retention with owner-configurable deletion, and redact credentials/page text. If a node is offline, preserve a gap marker and reconcile later; never fabricate continuity.
- cost: Low ongoing storage and transfer if events contain metadata and hashes only; one inexpensive summarization call per requested timeline. The implementation cost is mainly schema adoption and reconciliation testing.  ·  latency: No impact on the critical action path if events are buffered asynchronously. Timeline retrieval should be sub-second locally, with a few seconds for cross-node reconciliation when a device has just reconnected.
- security: Adds a sensitive cross-device audit surface, so use paired-device authentication, per-event sensitivity labels, encrypted transport/storage, retention limits, and explicit exclusion of raw audio, page bodies, and secrets unless the owner asks for them.
- depends on: A shared paired-device identity and request-ID propagation across relay, Mac bridge, pendant, and browser extension; An encrypted bounded event store with deletion/retention controls; A compact timeline renderer available to the voice and Mac surfaces


## What it asked for

_Nothing._
## Its own summary

Round 33 produced two new proposals grounded in live state: (1) a relay/Mac/browser readiness-and-lease router that avoids false 45-second browser failures, routes public work around an offline browser, queues private work resumably, and returns truthful pendant receipts; (2) a spoken 'why couldn't you do that, and fix it' readiness repair flow that diagnoses missing Accessibility/Screen Recording/browser-bridge prerequisites, opens the exact System Settings remedy, and re-tests recovery. Live evidence: Mac/relay are online, but browser bridge is offline with 2 pending commands; Accessibility and Screen Recording are not granted.

**Biggest unknown:** The owner still needs to enable Accessibility and Screen Recording for AI Pendant Agent and bring the browser bridge online before UI/private-browser execution can be verified. Engineering dependencies are the async browser adapter, paired-device readiness heartbeat, and relay durable leases; no further tool or permission request is needed from me this round.

