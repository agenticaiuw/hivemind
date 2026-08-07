# Harness derivation — faculty-perception — round 51

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent-perception-2026-08-07** — After the requested permission grant/restart, the live Mac agent still reports permissions.ready=false: accessibility trusted=false, screenRecording granted=false, inputReachability.status=failed, and uiActionsWillReachTheScreen=false. It explicitly says the running com.aipendant.agent binary is not the identity granted Accessibility. Browser extension is also offline with 5 pending commands. Separately, owner memory says timezone America/Chicago while /machine-context reports America/New_York; time-sensitive behavior has an unresolved timezone conflict.
  - evidence: GET /observe at 2026-08-07T11:47:21.165Z and GET /ops/status both returned these values; owner discover output says timezone America/Chicago; /machine-context reports timezone America/New_York.
- **browser-extension-perception-2026-08-07** — The home Chrome browser extension is offline at the live bridge: no tab/window identity, tabCount unknown, last seen 2026-08-07T11:34:33.146Z, and 5 commands are pending. The Mac agent reports this identically through /browser/status and /ops/status.
  - evidence: GET /browser/status and GET /ops/status at 2026-08-07T11:47Z returned online=false and pendingCommands=5.

## Capabilities it proposed

### "Before you schedule, remind me, or answer 'what time is it?', make sure every device agrees on my timezone—and tell me if they do not."
- **useful because:** Today the owner's remembered timezone is America/Chicago while the live Mac context says America/New_York. A silent mismatch can create missed meetings, wrong reminders, and misleading spoken answers. This capability turns an invisible cross-surface disagreement into an explicit, reviewable decision.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheap background classifier/normalizer for routine timezone evidence; reserve realtime only for the owner's spoken conflict resolution. No LLM is needed when sources agree.
- **latency:** Under 300 ms for cached agreement; 1–2 seconds when refreshing Mac/relay/device evidence. Never block ordinary non-time-sensitive requests.
- **cost:** Near-zero for agreement checks (typed comparisons and cached state); occasional model cost only to phrase an ambiguous conflict, dominated by realtime speech if the owner is speaking.
- **security:** Timezone/location hints are sensitive metadata. Persist only the chosen IANA zone, source, timestamp, and confidence; do not infer or store precise location. Ask before changing the owner's remembered timezone. Never schedule while confidence is unresolved.
- **missing:** A typed timezone evidence endpoint combining owner preference, Mac OS timezone, relay clock, and pendant/network timezone; A durable conflict state with acknowledgement and expiry; An explicit schedule gate that refuses to silently use a conflicting machine timezone; Repair of Mac Accessibility/Screen Recording so Mac evidence can be trusted

### "Before you rely on any device, tell me whether the whole system can actually see and complete this request—pendant, relay, Mac, and browser—and point out any stale or contradictory state."
- **useful because:** Today one surface can report success while the real action does nothing: the Mac agent's live UI probe is failing, the browser extension is offline with queued commands, and its timezone disagrees with the owner's remembered timezone. The owner needs a single trustworthy preflight answer, not scattered operational dashboards or false receipts, before relying on an automation.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic typed checks and freshness rules should do the normal work; use a cheap background model only to summarize several conflicts. Realtime is reserved for speaking the short result when the owner asks through the pendant.
- **latency:** Return cached readiness in under 300 ms; refresh live surfaces within 2 seconds. For a noncritical request, allow proceeding with an explicit degraded-state warning; for irreversible work, require an acknowledged preflight failure.
- **cost:** Negligible API cost when checks are structured and cached; occasional small summarization call, with no realtime model unless spoken interaction requires it. Main cost is implementation of the cross-surface evidence contract.
- **security:** Expose capability status, not secrets, page contents, or screen pixels. Preserve source, timestamp, and confidence so stale evidence is visible. Never claim completion from an action receipt if input reachability or browser liveness is false. Require confirmation before overriding a failed preflight for destructive or external actions.
- **missing:** A cross-surface readiness contract with per-surface capabilities, freshness, contradictions, and dependency edges; A request-specific preflight evaluator that maps an intended operation to required surfaces and refuses unsupported claims; A durable degraded-mode record so queued pendant/browser work is not mistaken for completed work; A concise pendant/dashboard rendering of evidence and unresolved conflicts


## Changes it proposed to its own stack

### `context` — Add a read-only /time-context (or equivalent relay contract) that returns typed timezone evidence from owner memory, Mac /machine-context, relay clock, and pendant network metadata: IANA zone, source, observedAt, confidence, and expiry. Add a deterministic conflict state consumed by routines/briefing/pipeline; route all time answers and schedule creation through it, with acknowledgement required to resolve disagreement.
- **owner gets:** The system will stop silently using the wrong timezone. The owner gets one short warning when Chicago and New York disagree, and future reminders and spoken time answers become dependable instead of subtly wrong.
- effort: Medium: schema plus relay persistence, adapters for existing routes, and tests for DST/conflict/unknown cases; no model training.  ·  risk: A stale or missing source could produce an unnecessary warning or delay a reminder. Recover by using the last acknowledged zone with visible stale labeling for non-critical answers, while requiring confirmation for new schedules.
- cost: Negligible storage and compute; avoids repeated model context by passing a compact typed record.  ·  latency: Cached checks under 300 ms; source refresh may add about 1–2 seconds only for time-sensitive work.
- security: Stores only IANA timezone and provenance, not precise location. Must redact timezone metadata from generic logs and require explicit confirmation before changing owner preference.
- depends on: Repair TCC identity so /observe and Mac-derived evidence are trustworthy; A durable acknowledgement/expiry record for timezone conflicts; Integration with existing /routines and /briefing scheduling paths

### `integration` — Add a cross-surface causality ledger: every pendant utterance/bookmark, relay job, Mac action, browser command, and returned result receives a shared correlation ID plus monotonic per-surface sequence and signed state transition. The ledger must distinguish accepted, queued, started, observed-at-target, completed, and expired; reject any completion claim lacking target-side observation, and reconcile late/offline events without duplicating work.
- **owner gets:** When the pendant says something happened later, the owner will know whether it was merely queued, actually reached the Mac/browser, or was verified at the target. Offline retries and stale GUI receipts will stop creating duplicate reminders or false assurances.
- effort: High: define the event schema and idempotency rules, add relay/Mac/browser/pendant adapters, persist compact transitions, and expose a human-readable receipt resolver.  ·  risk: Clock skew, lost acknowledgements, or a crashed target may leave work visibly 'unknown' rather than falsely complete. Recovery is an expiry/retry state with explicit owner review; destructive operations remain gated until target observation is present.
- cost: Small D1/local-log writes per transition and compact receipt payloads; no model cost for reconciliation. Storage retention can be bounded by correlation-ID age.  ·  latency: One lightweight ledger write per transition; target verification may add under a second for online actions, while offline work remains explicitly pending.
- security: Correlation IDs and signed transitions must avoid embedding page content or secrets. Protect the ledger from replay and cross-job confusion; expose sensitive details only to the owner session.
- depends on: A durable shared event schema across relay, Mac, browser, and pendant; Target-side observation hooks for Mac input reachability and browser extension execution; Idempotency keys and late-event reconciliation for offline queues; A receipt resolver integrated with existing jobs/pipeline history


## What it asked for

### `p4-htar` (permission) — Repair macOS TCC identity for the currently running AI Pendant Agent process: grant Accessibility and Screen Recording to both the app bundle com.aipendant.agent and its actual executable /Users/evanliu/Applications/AI Pendant Agent.app/Contents/Resources/node (or launch the agent under the exact already-granted identity), then restart it and verify /observe inputReachability.status=ready and /ops/status permissions.ready=true.
- why: The live probes show the prior grant did not affect the running child process: UI actions currently report success while doing nothing, and screen capture/computer-use cannot be trusted. This blocks reliable perception and action across Mac/browser surfaces.
- risk it sees: Granting these permissions gives the agent broad UI observation/control and screen capture. Keep it restricted to this exact app/executable, disclose that screen pixels may leave the device only when explicitly consented, and revoke if verification fails.

## Its own summary

Established and recorded two live cross-surface facts: (1) the requested macOS grant did not take effect for the running AI Pendant Agent child process—Accessibility and Screen Recording remain unavailable, input reachability fails, and GUI receipts cannot be trusted; (2) the browser extension is offline with five pending commands. Also found a new safety-critical contradiction: owner memory says America/Chicago, while live Mac context says America/New_York. Proposed and recorded a timezone-evidence/conflict gate for all time answers and scheduling, and queued a narrowly scoped permission repair for both the app bundle and actual node executable.

**Biggest unknown:** Whether the orchestrator can successfully repair TCC for the exact running executable and make /observe inputReachability.status=ready; until then, Mac GUI/browser perception remains unreliable.

