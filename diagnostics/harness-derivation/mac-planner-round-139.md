# Harness derivation — mac-planner — round 139

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac action contract** — The live Mac job queue has a recurring schema mismatch: run_shell command, run_applescript script, open_app appName, and browser navigation fields are being emitted in shapes the executor does not accept. This is a reliability defect, not an authorization issue; normalize and diagnose at the boundary without gates.
  - evidence: Fresh message from mac-terminal in Round 139: /jobs shows repeated failures, 24 journal failures, and browser navigation 10/10 failed; observed aliases are command/script/appName versus executor's expected canonical fields.

## Capabilities it proposed

### "If the pendant loses signal or I interrupt you halfway through a task, keep my place and resume it later without losing my words or repeating any Mac/browser actions."
- **useful because:** Today an LTE-M drop can lose seconds of speech while the Mac job may still be running, leaving the owner unsure whether to repeat the request and risking duplicate clicks or submissions. A resumable handoff would preserve the unsent audio locally, reconcile it with relay/job receipts, and continue only from the last acknowledged step.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the realtime model only to acknowledge the interruption and classify the handoff; use a cheaper background model to transcribe/reconcile queued audio and summarize the resume state. The Mac and browser agents execute no step twice: they consume idempotency keys and receipts.
- **latency:** Immediate local interruption marker and one short spoken acknowledgement under 1 s; reconnect upload in the background. Resume summary within 10 s of link recovery, bounded by the existing job/browser polling cadence.
- **cost:** Usually <$0.01 per interruption, dominated by background transcription/reconciliation; negligible when no interruption occurs. SD buffering and receipt reconciliation are local/server metadata, not model-heavy.
- **security:** Unsent audio temporarily resides on the pendant SD and transcript/job metadata on the relay; encrypt SD files, bind them to an authenticated session, expire them after successful acknowledgement, and expose a delete-now gesture. Never auto-resume an irreversible browser or Mac mutation without a durable pre-action receipt and explicit owner instruction; private page content stays in the authenticated browser session.
- **missing:** Pendant firmware interruption journal with encrypted sequence-numbered audio chunks and a local 'resume pending' state; Relay reconciliation service joining audio sequence ACKs to Mac/browser job receipts and issuing a resumable capsule; Mac/browser executors must persist idempotency keys and last-completed step before each action; Owner-facing resume capsule/notification and dashboard view of pending, resumed, and discarded work; A real packet-loss/half-duplex test fixture across LTE-M, relay, Mac bridge, and browser session


## Changes it proposed to its own stack

### `integration` — Add a non-blocking action-schema compatibility layer at the POST /plan and POST /execute boundary. Normalize aliases (open_app.appName→app, run_shell.command nested or top-level, run_applescript.script nested or top-level, browser_navigate.url) into one canonical internal action shape; preserve the original payload, emit a schemaVersion, and return a typed preflight diagnostic for unknown/missing fields. Record normalization and executor result in the existing receipt/journal without introducing approval gates.
- **owner gets:** The owner currently experiences silent-looking failures and may retry the same request: live jobs show run_shell, AppleScript, app launch, and browser navigation actions failing because planner and executor disagree about field names. This makes ordinary requests complete reliably instead of leaving half-finished desktop work or duplicate retries.
- effort: Small-to-medium: shared validator/normalizer, adapters for existing action types, contract tests against /plan→/execute and browser bridge, plus dashboard display of the canonical action and diagnostic.  ·  risk: An overly permissive alias could reinterpret malformed input. Mitigate by requiring exactly one canonical value after normalization, marking ambiguous payloads as invalid (diagnostic only), and retaining the original action for debugging. Recovery is straightforward: receipts preserve both forms and the adapter can be disabled by schema version.
- cost: No meaningful model cost; a few milliseconds and small journal overhead per action. Prevented retries likely reduce API and Mac-agent spend.  ·  latency: Adds roughly 1–5 ms validation/normalization before execution; no extra model round trip.
- security: No access expansion and no gates. Preserve existing bearer/session authorization; never log secrets from command text or page content, only field presence and action type.
- depends on: A single canonical action-type schema shared by planner, browser bridge, and executor; Receipt/journal storage already present in actionReceipt; Contract tests or a replay fixture for the 24 observed failures and repeated browser-navigation failures

### `integration` — Introduce a signed capability/schema handshake between the relay planner, Mac executor, and browser bridge at session start and whenever an executor reconnects. Each surface publishes its supported action types, required fields, aliases, result envelopes, and schema version; the planner compiles actions against that negotiated contract rather than assuming a hard-coded shape. Store the negotiated contract hash with every job and reject only impossible plans before execution with a repairable, machine-readable explanation. This is distinct from a static alias normalizer: it prevents future planner/executor drift and supports rolling upgrades across surfaces.
- **owner gets:** The owner should be able to ask for a desktop or browser task and have it remain reliable while the system is upgraded. Today a backend change can silently turn ordinary requests into failed or partial jobs because different components disagree about action contracts. With negotiation, the system adapts to the actual connected Mac/browser version and explains incompatibilities before the owner loses work or retries a task.
- effort: Medium: define the signed contract document, handshake endpoint/message, planner compilation step, contract-hash job metadata, and compatibility tests across relay, Mac, and browser versions. Add a dashboard view showing connected surface versions and contract health.  ·  risk: A stale or malicious contract could cause incorrect planning. Bind contracts to the authenticated device/session, sign them, apply short expirations, and use conservative compatibility rules. If negotiation fails, fall back to a read-only diagnostic rather than guessing a mutation.
- cost: Small metadata and one handshake per connection or upgrade; no recurring model cost. Reduced retries should lower overall model and Mac execution cost.  ·  latency: One cached handshake on connection; no per-action network round trip after negotiation. Initial connection may add tens of milliseconds.
- security: Improves protocol integrity without expanding device privileges. Contract documents must never contain command secrets, cookies, page contents, or arbitrary executable code; they describe schemas only.
- depends on: Authenticated Mac and browser sessions; A versioned canonical action/result schema; Receipt records that can store a contract hash; A relay-side planner compiler capable of selecting an available contract


## What it asked for

_Nothing._
