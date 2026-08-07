# Harness derivation — faculty-action — round 35

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **action-admission-readiness** — At 2026-08-07T10:40Z Mac bridge and relay are online, but action surface is not ready: Accessibility trusted=false, eventsPost=false, inputReachability failed, Screen Recording=false, computer-use loop disabled, browser extension offline with 3 pending commands. Therefore UI and browser receipts cannot be trusted.
  - evidence: GET /ops/status, GET /observe, GET /browser/status

## Capabilities it proposed

### "Start this task here, keep working while I move around, and come back to me only when you need a decision or can prove it is finished."
- **useful because:** Today a task begun in conversation is either tied to one surface or becomes an opaque background job. The owner should be able to leave the Mac, receive a concise interruption on the pendant when execution encounters a real fork, answer naturally, and then get a proof-oriented completion report. This is a handoff between the worn conversational surface, always-awake relay, Mac executor, and private browser—not a Mac-only automation.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the realtime model only for the short interruption and answer exchange on the pendant. Use a cheaper background model for decomposition, polling, summarization, and receipt generation; deterministic local code handles execution and state transitions.
- **latency:** Immediate acknowledgement on the pendant (<2 seconds). Normal background steps may take minutes. A decision request should surface within 5 seconds of a blocked step, and resume within 2 seconds after the owner's answer reaches the relay.
- **cost:** Approximately $0.01–$0.10 per task depending on duration and private-page extraction; realtime audio turns dominate, while polling, routing, and receipt generation should be near-zero with a background tier.
- **security:** The relay must carry only the minimum decision context, never raw private-page contents unless required. Each interruption needs task/session binding, expiry, replay protection, and a clear spoken description of the consequence. No irreversible external submission should happen merely because the owner answered an unrelated pendant conversation; the browser and Mac must enforce the task identity and effect receipt.
- **missing:** A first-class cross-surface task lease that binds pendant conversation, relay job, Mac job, browser session, and current step; A pendant-addressable decision inbox with interrupt/resume semantics and timeout behavior; Typed pause reasons and compact evidence payloads so the relay can ask one precise question rather than replaying full context; A verified effect receipt chain that distinguishes completed, awaiting-owner, expired, and abandoned states; Recovery when either the pendant link or browser extension disappears, without duplicating an already-applied step


## Changes it proposed to its own stack

### `integration` — Add an execution-admission and evidence chain in the action runner. Before each step, compile a typed preflight from live /ops/status + /observe (surface, permissions, online state, target/session, reversibility), and reject or reroute any step whose actuator is not reachable: UI clicks/typing/keys are refused when Accessibility/inputReachability is false; screenshot-dependent steps are refused when Screen Recording is absent; browser work is parked with a durable retry receipt when the extension is offline; AppleScript/shell alternatives are selected only when their declared postcondition is independently observable. Require each write step to carry the signed Evidence-to-Effect envelope (scope, expiry, idempotency key, expected postcondition, revocation reference), then append preflight, effect, independent observation, and recovery/expiry records to the existing job journal. Never report success for an unobserved UI effect.
- **owner gets:** The pendant will stop claiming that something happened when the Mac or browser could not physically receive the action. Instead it will say exactly what is blocked, preserve the work, retry when the required surface returns, and provide a verifiable before/after receipt—especially important for messages, forms, reminders, and other real-world changes.
- effort: Medium-high: action-runner admission middleware, typed envelope verifier/revocation lookup, readiness watcher, durable retry state machine, and adapters for /observe and /browser/status; add fault-injection tests for permission loss, disconnects, duplicate retries, and stale leases.  ·  risk: A conservative gate may defer legitimate actions and existing callers may lack postconditions. Recover by allowing explicitly declared non-UI actions with their own evidence provider, exposing a reason-coded blocked receipt, and replaying only idempotent steps after readiness returns. Keep the current journal and undo endpoints backward-compatible.
- cost: Negligible API cost; mostly local CPU/storage. A slower model is unnecessary—the planner supplies the envelope and deterministic middleware verifies it.  ·  latency: Adds roughly one local status/observation read per step (tens to hundreds of ms); disconnected work returns immediately as queued rather than waiting 45 seconds.
- security: Improves safety and auditability: least-scope, expiry, idempotency, and revocation are checked before writes; sensitive page data remains on the Mac/browser bridge. Must protect signing keys and avoid logging raw form/email contents in receipts.
- depends on: faculty-judgement's signed Evidence-to-Effect envelope schema and revocation/explain endpoint; a durable non-blocking browser command poller (replace the current 45-second wait); mac_readonly_inspect implementation or equivalent typed observation provider; readiness transition events from the Mac bridge and browser extension


## What it asked for

_Nothing._
## Its own summary

Fresh live checks show the central execution problem is still real: the Mac bridge/relay are online, but Accessibility and input reachability are false, Screen Recording is unavailable, computer-use is disabled, and the browser extension is offline with 3 pending commands. I recorded this as a finding and proposed a new integration change: deterministic per-step execution admission. It verifies live readiness before acting, refuses unreceivable UI effects, parks offline browser work, validates signed Evidence-to-Effect envelopes (scope/expiry/idempotency/postcondition/revocation), and requires independent observation before reporting success. This is the missing bridge between judgement's intent and truthful real-world effects.

**Biggest unknown:** I still need the authoritative Evidence-to-Effect envelope/revocation schema and verifier contract from faculty-judgement, plus implementation of a nonblocking browser poller and a typed read-only inspection provider. Without those, the action runner cannot safely distinguish queued, attempted, and verified effects.

