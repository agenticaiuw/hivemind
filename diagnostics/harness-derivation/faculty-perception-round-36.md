# Harness derivation — faculty-perception — round 36

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-ui-reachability** — As of 2026-08-07T10:50:41Z, Mac local agent is reachable and relay/mac bridge online, but UI control is not actually reachable: accessibility trusted=false, screenRecording=false, inputReachability status=failed, uiActionsWillReachTheScreen=false, and /ops/status ready=false. Browser extension home-chrome is offline with 3 pending commands. Do not treat action receipts as evidence of visible UI changes.
  - evidence: GET /observe HTTP 200 at 2026-08-07T10:50:41.962Z and GET /ops/status HTTP 200: accessibility.trusted=false; inputReachability.status=failed; uiActionsWillReachTheScreen=false; browser.online=false; pendingCommands=3; permissions.ready=false.
- **mac-relay-connectivity** — At 2026-08-07T10:50:41Z, local Mac agent and Cloudflare relay are reachable; relay reports macBridgeOnline=true and capabilities pendantPipelineTelemetry, pendantSpeech, persistentAgentState, durableAudio. This does not establish pendant physical reachability.
  - evidence: GET /ops/status HTTP 200 payload: agent.ok=true; relay.reachable=true; relay.payload.macBridgeOnline=true; relay capabilities listed.

## Capabilities it proposed

### "“Where did we leave off?” Give me a trustworthy handoff of the last unfinished thread across my pendant, Mac, and browser: what I asked, what each surface actually observed, what changed, what is still pending, and the one safe next step I can approve or take."
- **useful because:** Today work can be split across a spoken pendant exchange, a Mac job, and private browser tabs without the owner knowing whether it completed, stalled, or merely produced a receipt. A cross-device causal handoff would let the owner resume in seconds instead of reconstructing state or repeating an action.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the cheaper background model to assemble a typed event timeline and identify gaps; use realtime only when the owner asks by voice and needs the short spoken handoff. The model must quote machine evidence and label inference rather than improvise completion.
- **latency:** Background event indexing under 1 minute after each event; spoken answer under 2 seconds from a cached projection, with a slower refresh only if the owner asks for current verification.
- **cost:** Low: mostly local event normalization and compact cached summaries; roughly one small background-model call per thread transition, with realtime tokens only for the voice reply. Storage and dashboard indexing dominate rather than inference.
- **security:** Private browser URLs, page snippets, messages, and audio-derived text must remain scoped to the owner's authenticated account and be minimized in the projection. Never expose secrets in spoken output or cross-device logs. The handoff may propose a next step but must require confirmation for sending, purchasing, deleting, or other irreversible actions.
- **missing:** A shared append-only event envelope with correlation IDs spanning pendant utterance, relay job, Mac plan/action, browser command, and receipt; A causal state reducer that distinguishes observed completion, queued, failed, expired, and unknown instead of treating HTTP success as task success; A privacy-filtered cross-surface handoff projection with evidence links and redaction rules; Browser and Mac agents must emit durable observation events, including negative evidence and permission/readiness state; A dashboard and pendant-readable handoff view that can identify the active thread without resending the full history


## Changes it proposed to its own stack

### `context` — Add a read-only Reachability Ledger emitted by Mac agent/relay and consumed by realtime, judgement, and action. Each node record is typed {node, transportState, actionState, observedAt, expiresAt, ttlMs, source, confidence, evidenceId}; probes are node-specific (Mac bridge /ops/status, UI input /observe, browser heartbeat/status, pendant telemetry). Merge newest unexpired records, downgrade to unknown on expiry, and explicitly distinguish transport online from action reachable. Attach the ledger version/evidenceId to every plan and receipt; when actionState is unknown or false, action must not claim success and realtime should explain the limitation. Refresh only on TTL expiry or link events to avoid repeated expensive probes.
- **owner gets:** The owner stops hearing confident confirmations for actions that never reached the screen, and gets an honest explanation of whether the pendant, Mac, or browser is currently usable. It also prevents an offline browser queue or stale Mac permission state from silently losing work.
- effort: Medium: shared schema + merge library, 3 probe adapters, relay propagation, and receipt/planner integration; add tests for expiry, conflicting observations, and transport/action divergence.  ·  risk: A stale or incorrectly merged record could unnecessarily refuse a valid action; recover by short TTLs, visible source/evidence, manual refresh, and allowing a fresh preflight. Never use this ledger to authorize destructive actions.
- cost: Negligible API cost; small D1/JSON metadata writes. Probe frequency is bounded by TTL and link events.  ·  latency: Usually none; realtime reads cached ledger. A preflight adds ~100–300 ms only when a record is expired or action-critical.
- security: Read-only operational metadata only; do not include URLs, page contents, tokens, or audio. Evidence IDs must not expose secrets.
- depends on: A pendant telemetry endpoint or relay heartbeat for authoritative pendant state; Mac agent fixes/permission refresh so /observe can report actual UI reachability; A shared typed context transport between relay and Mac agent


## What it asked for

_Nothing._
## Its own summary

Established fresh operational truth: Mac bridge and relay are reachable, but Mac UI control is not actionable (Accessibility=false, Screen Recording=false, input probe failed, ready=false); browser extension is offline with 3 pending commands; pendant physical reachability remains unobserved. Sent relay-realtime a typed reachability schema with TTL/expiry and transport-vs-action distinction, recorded these findings, and proposed a shared Reachability Ledger so plans and receipts cannot claim success from unreachable UI.

**Biggest unknown:** Why the orchestrator's claimed permission grants have not taken effect for the running com.aipendant.agent binary, and there is still no authoritative pendant heartbeat/telemetry snapshot.

