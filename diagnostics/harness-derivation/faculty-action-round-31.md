# Harness derivation — faculty-action — round 31

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-readiness** — The Mac bridge is online but not ready: Accessibility trusted=false, Screen Recording granted=false, browser extension offline with 3 pending commands, while requiredMissing is empty. Therefore GUI/browser completion cannot honestly be claimed; action routing needs a typed readiness gate and reconciliation path.
  - evidence: GET /ops/status at 2026-08-07T10:29Z returned agent.ready=false, permissions.accessibility.trusted=false, permissions.screenRecording.granted=false, browser.online=false, pendingCommands=3.

## Capabilities it proposed

### "“For this project, make the routine decisions yourself: you may carry out changes that satisfy my standing rules, but stop and ask me whenever the actual result would violate one of them.”"
- **useful because:** Today the owner must re-authorize a stream of individually safe actions, or risk giving a broad instruction that cannot express nuanced limits. This would let the pendant, relay, Mac, and browser act as one bounded delegate: ordinary work proceeds while exceptions, ambiguity, and policy violations reach the owner with the exact evidence needed to decide.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** A cheaper background planner compiles the owner's natural-language rules into a typed policy; local Mac/browser executors enforce the deterministic checks; faculty-judgement handles ambiguous exceptions; realtime is used only to ask the owner a short clarification or approval through the pendant.
- **latency:** No added latency for actions that match a cached local policy (milliseconds). An exception should produce a pendant prompt within a few seconds; background policy compilation can take seconds to minutes.
- **cost:** Low per action after compilation: deterministic local checks dominate, with an inexpensive model call only when a new rule or ambiguous exception needs interpretation. Realtime cost is limited to exception conversations.
- **security:** Policies can grant meaningful autonomy, so scope them by project, surface, data class, action type, amount, and expiry; never infer permission from silence. Private browser data should remain on the Mac bridge except for minimized evidence. Every automatic action needs a human-readable reason and an immediate pause/revoke control from the pendant or dashboard.
- **missing:** A versioned policy language with explicit allow/deny/escalate predicates and conservative defaults; A policy compiler that turns owner rules into deterministic checks and tests them against proposed action bundles; Enforcement hooks shared by Mac, browser, relay jobs, and pendant prompts; A durable policy version/decision record attached to each action receipt; A fast owner-facing pause and revoke channel that works while a delegated job is running


## Changes it proposed to its own stack

### `integration` — Add a cross-surface Action Commit Protocol between faculty-judgement, faculty-action, faculty-perception, relay, Mac, and browser: every delegated intent becomes a versioned action bundle with (1) required capabilities and live readiness snapshot, (2) explicit preconditions/evidence fingerprints, (3) an idempotency key and short execution lease, (4) a prepare phase that gathers reversible edits/drafts without committing, (5) a commit phase routed to the physically appropriate hand, and (6) mandatory postcondition verification by perception before reporting success. If readiness changes or evidence is stale, action pauses and returns a typed 'needs replan' packet rather than attempting blind GUI work. Relay persists bundles/checkpoints while the Mac is asleep or disconnected; the pendant receives only concise approval/blocked/completed prompts. This is not another receipt/undo log: it closes the judgement-to-action-to-perception loop and gives each side a shared contract.
- **owner gets:** The owner can say 'do it' and trust that the system either completes the real-world change or clearly says what blocked it. They will stop hearing success for work that merely queued, hit an offline browser, or lacked Accessibility/Screen Recording; drafts and reversible preparation can survive leaving the Mac, and a changed page or stale calendar entry triggers re-check instead of a wrong submission.
- effort: High: shared JSON schema and state machine in relay/local-agent, capability/readiness adapters for Mac and browser, durable D1 checkpoints, perception verification hooks, pendant push states, and migration of existing execute/jobs/routines. Start with reminders and browser form drafts before irreversible transactions.  ·  risk: A stuck lease could leave an action paused; recover with lease expiry, explicit cancel, and idempotent replay. Verification can fail after a successful external side effect, so report 'committed but unverified' and retain evidence rather than retrying automatically. Do not expose page contents or secrets to the relay unless required; browser private data stays on the Mac bridge. Require fresh owner confirmation at commit for sending, purchasing, deleting, or publishing.
- cost: Small per-action D1 writes and Mac/relay network traffic; background verification uses a cheap text model, with realtime used only for the spoken clarification/approval. No new hardware required.  ·  latency: Adds roughly 0.5–2 seconds for readiness and postcondition checks on local actions; browser tasks may add one page read. Long jobs remain asynchronous with pendant push updates.
- security: Improves safety through capability declarations, freshness bounds, least-privilege routing, commit gating, and auditable evidence. Treat action bundles as sensitive; encrypt or minimize private page fields and never put auth cookies in relay state.
- depends on: A typed readiness/reconciliation contract for Mac Accessibility, Screen Recording, and browser bridge health; Shared provenance/evidence capsule IDs usable by perception and action; Durable delegated-job checkpoints and pendant push notifications; A confirmation policy for irreversible commits


## What it asked for

_Nothing._
## Its own summary

Discovered the live stack and proposed a new integration change: a cross-surface Action Commit Protocol. It gives judgement/action/perception one durable contract with readiness checks, preconditions, evidence fingerprints, idempotency leases, prepare/commit separation, and mandatory postcondition verification. This addresses the concrete live failure mode where the Mac bridge is online but not ready and the browser is offline, yet an action could otherwise be reported as completed. Current status confirms Accessibility=false, Screen Recording=false, browser offline with 3 pending commands, and ready=false despite requiredMissing=[]; I recorded this as a finding and informed relay-realtime.

**Biggest unknown:** Whether the orchestrator will implement the typed readiness/reconciliation contract and permission recovery path; until then, GUI/browser actions must remain explicitly blocked or unverified rather than claimed complete.

