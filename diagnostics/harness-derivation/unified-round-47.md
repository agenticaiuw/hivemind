# Harness derivation — unified — round 47

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **cross_surface_diagnostics_gap** — The live pipeline already records rich but unlinked evidence (nRF9160 offline-store alerts/bookmarks, relay IDs, audio telemetry, Mac TTS metrics, and browser pending commands), while /ops/status shows browser offline with 3 pending commands and Mac readiness false due to missing Accessibility/Screen Recording. There is no incident-level correlation or repair manifest.
  - evidence: GET /pipeline and GET /ops/status on 2026-08-07 returned pipelineId/eventId plus relayJobId/audio telemetry, and browser pendingCommands=3 with accessibility.trusted=false and screenRecording.granted=false.

## Capabilities it proposed

### "When the pendant or a cross-device job starts misbehaving, say “diagnose this” and have the system reconstruct what happened, test the likely cause, and prepare the safest repair—then tell me exactly what changed or what still needs me."
- **useful because:** Today a failed voice turn, browser action, or Mac job leaves the owner guessing which node broke. This creates one evidence-backed incident timeline across the wearable's local UART/audio/link signals, relay receipts, Mac job logs, and browser command results, then turns diagnosis into a reviewable repair rather than another blind retry.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheap background model for log normalization and hypothesis ranking; use the realtime tier only for the owner's spoken diagnosis and approval. Faculty perception gathers evidence, judgement selects a reversible repair, and faculty action executes it.
- **latency:** A spoken first answer within 2 seconds from cached local/relay telemetry; complete cross-surface diagnosis in 30–90 seconds. Repairs remain staged until owner approval unless they are explicitly reversible health checks.
- **cost:** Roughly $0.01–$0.05 per incident depending on log volume; most cost is summarizing Mac/browser logs and generating the repair plan, not the short voice response.
- **security:** Logs may contain URLs, account names, snippets, and audio metadata. Keep raw UART/audio on device or short-lived relay storage, redact secrets before model use, scope browser evidence to the affected tab/session, and require confirmation before firmware changes, deleting data, sending messages, or changing system permissions.
- **missing:** A normalized incident schema linking pendant event IDs, relay request IDs, Mac job IDs, and browser command IDs; A local pendant fault/event ring buffer with upload-on-consent and SD fallback; A read-only cross-surface diagnostic collector and correlation endpoint; A repair-plan executor with preconditions, dry-run receipts, rollback, and explicit approval gates; A dashboard incident view showing timeline, confidence, evidence, and before/after verification

### "Let me give you a bounded delegation lease—‘keep this moving until Friday, up to 20 minutes and $0, draft but never send’—and have the pendant, relay, Mac, and private browser carry it out across interruptions, pause at the exact boundary I set, and return a proof of what it did."
- **useful because:** The owner currently has isolated actions, routines, and jobs, but not one durable, revocable grant of authority that survives a dropped pendant link or a sleeping Mac while still constraining every downstream action. This would make delegation trustworthy instead of requiring the owner to supervise each step.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use a low-cost background model to decompose and monitor the lease; use realtime only when the owner changes scope or an urgent decision must be spoken. The relay persists state, the Mac performs local work, and the browser handles authenticated sessions.
- **latency:** Lease creation and acknowledgement under 2 seconds. Work may continue asynchronously for minutes or days. Boundary violations must pause immediately; final receipt should be available within 5 seconds of the last action.
- **cost:** Approximately $0.01–$0.08 per lease, dominated by periodic state reconciliation and authenticated browser extraction; simple monitoring should use a cheaper model.
- **security:** A lease is authority, not merely a task description. Scope it to named accounts, tabs, folders, action classes, deadline, spend, and data destinations; make it revocable from the pendant and relay; encrypt it; expire it automatically; require confirmation for sending, purchasing, deletion, permission changes, or scope expansion. Receipts must show the exact policy evaluated before every action.
- **missing:** A signed, versioned delegation-lease object understood identically by relay, Mac, browser, and pendant; A policy decision point that evaluates every action against lease scope before execution; A pendant revoke/pause gesture that works offline and takes effect when the relay reconnects; Durable lease state with wake/resume, expiry, retry budget, and escalation rules; A cryptographic action receipt proving the lease version, policy decision, target, before/after state, and verification result; Dashboard controls for creating, editing, revoking, and auditing leases


## Changes it proposed to its own stack

### `integration` — Add a correlation ledger that assigns one incidentId at the pendant button/audio session boundary and propagates it through relay requests, D1 jobs, Mac jobs, browser commands, and receipts. Store a compact event envelope (timestamp, node, operation, status, latency, error class, evidence pointer, redaction status), expose GET /incidents/:id and a dashboard timeline, and add a dry-run repair manifest with preconditions, expected verification, rollback receipt, and approval state.
- **owner gets:** Instead of hearing “it failed,” the owner gets a plain explanation of where the failure occurred, what was tried, and a safe, verifiable next step. Repeated failures become actionable bug reports rather than lost anecdotes.
- effort: Medium: shared schema and propagation middleware first, then read-only collectors and dashboard; roughly 1–2 weeks for a useful vertical slice.  ·  risk: Correlation IDs could accidentally join unrelated private activity, and oversized evidence could leak secrets. Use per-session random IDs, strict TTLs, field redaction, opt-in raw evidence, and a fallback that reports only aggregates. If a repair fails, do not auto-chain retries; preserve the pre-repair snapshot and offer rollback.
- cost: Small D1/R2 metadata cost; approximately <$0.001 per incident excluding model summarization. Raw audio/log evidence should be capped and expire quickly.  ·  latency: Negligible on the live path if envelopes are append-only and asynchronous; diagnosis adds 30–90 seconds in the background.
- security: Improves auditability but expands sensitive telemetry. Encrypt evidence pointers, separate metadata from raw payloads, enforce node/session scoping, and require confirmation for any mutation.
- depends on: Pendant local event ring buffer and consented upload; Stable request/job/command IDs across relay, Mac, and browser; Read-only diagnostic collector; Repair executor with approval and rollback; Dashboard incident timeline

### `relay` — Introduce a signed Delegation Lease protocol. The relay issues a versioned lease containing goal, allowed surfaces/accounts, permitted action verbs, spend/time limits, data destinations, retry budget, expiry, and revocation nonce. Every Mac and browser command must present the lease version; the policy gate returns allow/deny plus reason before execution. Pendant pause/revoke packets are accepted locally while offline and applied on reconnect. Persist a hash-chained receipt for each decision and expose lease state, expiry, and revocation in the dashboard.
- **owner gets:** The owner can hand over a bounded outcome without leaving an unmonitored agent with vague authority. They can revoke it from the thing they are wearing, and later prove exactly which actions were authorized and why.
- effort: High: protocol, enforcement middleware in two executors, offline pendant command, durable state, and dashboard audit controls.  ·  risk: A policy bug could either block useful work or authorize too much. Default-deny unknown verbs, require lease-version matching, fail closed on expiry or malformed leases, canary with read-only leases, and retain rollback/audit receipts.
- cost: Low storage and request overhead; a few hundred bytes of policy metadata and receipt per action. Model cost is reduced because repeated authorization checks are deterministic, not LLM calls.  ·  latency: Adds roughly 5–20 ms for a local policy check and one relay lookup when cached; offline revocation takes effect on the next reconnect.
- security: Strengthens least privilege and auditability, but makes the relay a security-critical authority. Use signed leases, key rotation, replay protection, per-surface scope, encrypted private-account identifiers, and no raw credentials in lease payloads.
- depends on: Shared action vocabulary across Mac and browser; Durable relay job state; Pendant offline command queue; Typed before/after action receipts; Dashboard approval and revocation UI


## What it asked for

### `t10-s5iq` (tool) — incident_diagnostics
- why: The proposed cross-surface diagnosis capability cannot be implemented with the current seven tools: it needs a read-only, correlated snapshot of pendant/relay/Mac/browser evidence and a dry-run repair plan without granting mutation access.

```json
{
  "type": "object",
  "properties": {
    "incidentId": {
      "type": "string"
    },
    "since": {
      "type": "string",
      "format": "date-time"
    },
    "until": {
      "type": "string",
      "format": "date-time"
    },
    "include": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": [
          "pendant_events",
          "audio_link",
          "relay_receipts",
          "mac_jobs",
          "browser_commands",
          "system_health"
        ]
      }
    },
    "mode": {
      "type": "string",
      "enum": [
        "snapshot",
        "hypotheses",
        "repair_dry_run"
      ]
    },
    "redact": {
      "type": "boolean",
      "default": true
    }
  },
  "required": [
    "mode"
  ],
  "additionalProperties": false
}
```

