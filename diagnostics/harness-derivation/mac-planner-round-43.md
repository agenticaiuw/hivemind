# Harness derivation — mac-planner — round 43

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-readiness-2026-08-07T09:55Z** — Relay and Mac bridge are reachable, but Mac agent is not ready: Accessibility trusted=false and Screen Recording granted=false. Browser extension home-chrome is offline with 2 pending commands. FULL_CONTROL_MODE is enabled, so execution has no confirmation gate; current evidence does not establish typed per-step before/after or idempotency receipts.
  - evidence: GET /ops/status returned HTTP 200 with agent.ready=false, accessibility.trusted=false, screenRecording.granted=false, browser.online=false/pendingCommands=2, fullControlMode=true.

## Capabilities it proposed

### "When I ask from the pendant to do something across my Mac and logged-in browser, keep the task coherent if either one disconnects, never duplicate a completed step, and tell me exactly what ran, what did not, and what was verified when it is finished."
- **useful because:** Today a stale browser bridge, missing Mac permission, or dropped connection can make a queued or ineffective action sound successful. The owner needs one trustworthy completion answer—not a false success, an unexplained failure, or a duplicate form submission—when the work crosses devices.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the realtime model only for the short spoken request and completion summary; use a cheaper background model to classify idempotency, reconcile step evidence, and prepare the durable receipt.
- **latency:** A readiness/lease check should add under one second before starting. Reconnect recovery may take minutes, but the pendant should immediately say it is paused and later deliver a concise verified/unverified receipt.
- **cost:** Low API cost per task: mostly structured relay metadata and a small background reconciliation call; the dominant cost is browser/Mac execution time and any screenshots or page extraction, not language generation.
- **security:** Leases must be short-lived and bound to the specific Mac job, browser tab/session, and action plan; receipts should redact page contents and sensitive field values. The relay must not retain credentials or unsent form data longer than the job retention policy. Irreversible actions still follow the owner's existing maximum-access policy, but any action lacking after-state evidence must be reported as unverified.
- **missing:** A cross-surface capability-lease protocol with signed, expiring readiness/session leases; A shared step schema carrying idempotency keys and observed-before, attempted, observed-after, or not-observed evidence; Durable reconnect/retry orchestration that retries only idempotent steps and resumes from the last verified checkpoint; Mac and browser adapters that return typed evidence instead of generic UI success; A pendant/dashboard receipt view distinguishing verified, unverified, skipped, and never-run steps


## Changes it proposed to its own stack

### `integration` — Add a cross-surface capability lease and truth envelope for every delegated job. Before execution, relay obtains short-lived signed leases from the Mac agent and browser bridge containing reachability, permission readiness, session/tab affinity, and capability version. Each Mac/browser step must echo the lease ID and return typed observed-before, attempted, observed-after (or explicit not-observed) evidence plus an idempotency key. Relay invalidates stale leases on disconnect, retries only idempotent steps, and sends the pendant a truthful degraded result ('not run', 'ran but could not verify', or 'verified') instead of treating a queued command or UI success as completion. This is observability and routing, not an approval gate.
- **owner gets:** When the owner asks from the pendant to do something on the Mac or in a logged-in browser, they stop hearing confident lies caused by stale tabs, lost extension links, or missing Accessibility permissions. They get a concise answer about what actually happened, and long jobs can resume safely after the laptop or browser reconnects.
- effort: Medium-high: relay lease schema and verifier, Mac/browser handshake endpoints, executor adapters for typed evidence, and durable job-state migration; test disconnect/reconnect and duplicate delivery.  ·  risk: A lease expiry can leave a legitimate job paused; recovery is an explicit resume with the same idempotency key after a fresh lease. Some UI mutations cannot provide reliable after-state, so they must be reported as unverified rather than guessed. No action is blocked by owner confirmation.
- cost: Negligible API cost (small relay metadata per job); engineering/storage overhead is the main cost, with a few hundred bytes of lease/evidence per step.  ·  latency: Adds one local health/lease round trip (typically tens of milliseconds) before a delegated job; retries after reconnect become slower but safer.
- security: Signed, short-lived leases reduce stale-session and confused-deputy risk; lease payloads must omit page contents and credentials, and evidence should hash/redact sensitive values.
- depends on: Typed per-step receipt schema beyond chg-5fc73ce3; A small authenticated health/lease endpoint in the Mac agent and browser bridge; Durable job runner chg-16bc5dee or equivalent retry state


## What it asked for

_Nothing._
