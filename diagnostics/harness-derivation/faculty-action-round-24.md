# Harness derivation — faculty-action — round 24

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **execution-readiness** — Mac bridge and relay are online, but screen-dependent actions are not trustworthy: Accessibility trusted=false for the actual AI Pendant Agent bundle, input reachability failed, Screen Recording=false, and ops ready=false. Browser extension is offline with 2 pending commands; recent browser jobs waited ~45 seconds then failed.
  - evidence: GET /observe and /ops/status at 2026-08-07T10:01Z; GET /jobs shows two failed browser_navigate jobs with offline-extension reason and ~45s durations.

## Capabilities it proposed

### "“If you can’t do that because the Mac is blocked, walk me through fixing it and retry automatically when I’m done.”"
- **useful because:** Today the mind can detect that UI automation is impossible but leaves the owner to diagnose permissions and remember to retry. This turns a dead end into a recoverable handoff: the Mac opens the relevant settings pane, the pendant explains the one missing step, the relay waits for the permission state to change, and the original action resumes exactly once.
- **path:** faculty-action detects and classifies the block → mac-planner opens the exact macOS Privacy & Security pane and polls permission state → relay-realtime keeps the pending job and sends a concise spoken instruction/retry status → pendant speaks the instruction and a button confirms the owner is ready → faculty-perception verifies input reachability and post-action evidence → browser-extension is used only if the owner must toggle a browser extension; otherwise it remains untouched
- **model tier:** Use deterministic local code for permission classification, settings deep links, polling, and retry; use the realtime model only for the spoken explanation and ambiguity. No background LLM is needed.
- **latency:** Immediate blocked response under 1 second; settings handoff under 2 seconds; poll every 2 seconds for up to 5 minutes, then leave a durable pending job and stop.
- **cost:** Near-zero API cost for local polling and Mac settings navigation; at most one short realtime turn for explanation. Dominant cost is the existing voice session, not the recovery logic.
- **security:** Never grant permissions or alter security settings automatically. The owner must perform the toggle. Do not capture screen contents while Screen Recording is missing. Persist only job ID, missing permission, host bundle identity, and timestamps; retry is idempotent and only after perception verifies reachability.
- **missing:** Mandatory UI-action preflight and typed blocked receipts; A local permission-state change watcher or short-poll endpoint; macOS deep links for the exact Accessibility and Screen Recording panes; Relay state machine for blocked->ready->single retry; Pendant button event routed to the pending job; Browser extension heartbeat/online state if browser recovery is requested

### "“If the first way fails, finish the task another way without making me start over—and tell me exactly what was completed.”"
- **useful because:** Today a task that hits an offline browser, a locked UI, or a sleeping Mac becomes a dead end or a misleading partial success. The owner should be able to hand the goal to the whole hive once; the action facet should preserve completed work, select a different reachable surface, and return one clear account of what happened rather than duplicate or abandon the task.
- **path:** pendant captures the single spoken goal and reads back the final state → relay holds the durable execution lease and receives heartbeats while devices disappear and return → faculty-judgement defines completion invariants and which substitutions are acceptable → faculty-perception verifies each claimed state transition with fresh evidence → faculty-action executes through Mac typed APIs, terminal, browser session, or relay fallback and records a shared task ledger → mac-planner and mac-terminal perform local alternatives when GUI/browser control is unavailable → browser-extension supplies authenticated-page actions when it is online, otherwise the task pauses at the exact browser-dependent boundary
- **model tier:** Use deterministic orchestration, action IDs, preconditions, and evidence matching for execution and fallback. Use the cheaper background model to translate a failed step into candidate alternatives. Use realtime only for the owner's live explanation or a genuinely ambiguous spoken goal.
- **latency:** Immediate acknowledgement under 1 second; fallback selection in under 3 seconds; asynchronous work may continue for minutes or hours with heartbeat updates. Never retry an unknown side effect until its prior outcome is reconciled.
- **cost:** Mostly local/relay orchestration with low background-model cost. The dominant cost is only the occasional reasoning turn to map an unavailable operation to an equivalent alternative; no screenshot or voice token cost is needed for silent retries.
- **security:** Fallbacks must preserve the original authorization scope and must not silently downgrade a private browser operation to a public/cloud route. Sensitive data stays on the Mac/browser session. Unknown outcomes become a stopped, inspectable state—not a blind retry. The owner sees which surface acted, what evidence supports it, and which portion remains undone.
- **missing:** A cross-surface task ledger with semantic completion invariants, dependency boundaries, and idempotent step identities; A failure taxonomy that distinguishes blocked, offline, rejected, timed out, and unknown-outcome actions; A planner that can generate and rank proof-equivalent fallback paths without widening data access; Evidence reconciliation across pendant, relay, Mac, and browser receipts; A resumable lease protocol that hands work between surfaces without replaying completed side effects; A compact spoken and dashboard receipt showing completed, substituted, blocked, and unknown steps


## Changes it proposed to its own stack

### `mac-harness` — Add a mandatory execution preflight for any screen-dependent action (ui_click, ui_menu, type_text, press_keys, vision/computer-use steps): read the live permission/input-reachability snapshot immediately before dispatch. If uiActionsWillReachTheScreen is false, do not dispatch the event; return a typed blocked result with the exact missing grant, host bundle identity, and a recovery instruction. For non-UI actions, continue normally. Include preflight state and timestamp in the action receipt so faculty-judgement can distinguish blocked, dispatched-but-unverified, and verified outcomes; re-check after dispatch when possible.
- **owner gets:** The owner will stop hearing “done” when nothing happened. A failed Mac permission setup becomes an honest, actionable response instead of a misleading success receipt, while safe shell/API actions keep working.
- effort: Moderate: central executor guard plus typed result/receipt schema, tests for UI-vs-non-UI routing and stale permission snapshots; coordinate with faculty-perception’s evidence envelope.  ·  risk: Some existing UI jobs will become blocked rather than silently ineffective; this is a deliberate safety improvement. Recovery is to grant Accessibility/Screen Recording to the exact AI Pendant Agent binary, then retry the blocked action by job/action ID. A race between preflight and OS permission changes is handled by post-action evidence marking the result unverified.
- cost: Negligible API cost; one local status read per UI action and small receipt metadata.  ·  latency: Adds roughly tens of milliseconds for local preflight; avoids long wasted vision loops.
- security: Improves safety by preventing UI input when the OS cannot accept it; exposes only permission state and bundle identity, not screen contents.
- depends on: faculty-perception’s cross-surface evidence envelope; A stable local permission/input-reachability status API


## What it asked for

_Nothing._
## Its own summary

Recorded a new cross-surface capability: the owner can give one goal and have the hive recover through a proof-equivalent execution path when a device or interface fails, while preserving progress, authorization scope, idempotency, and an evidence-backed completed/blocked/unknown receipt. This is distinct from generic routing or durable jobs because fallback is constrained by semantic completion invariants and reconciled evidence before any retry.

**Biggest unknown:** The exact owner-approved equivalence rules for substituting one execution surface or action method for another.

