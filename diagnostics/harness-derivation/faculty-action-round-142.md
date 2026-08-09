# Harness derivation — faculty-action — round 142

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Do it, check that it actually happened, and if it didn’t, undo it and tell me exactly what remains.”"
- **useful because:** This is the single most useful trust primitive: the owner gets a completed action rather than an optimistic receipt. A failed postcondition triggers a bounded compensating action, while an unverified result is surfaced as unknown instead of claimed success.
- **path:** faculty-judgement → faculty-action → faculty-perception → mac-planner → browser-extension → relay-realtime
- **model tier:** Realtime only for the spoken request; background/local planner for execution and verification.
- **latency:** 5–20 s for normal Mac/browser actions; up to 60 s for a compensating action. Speak an immediate staged/working acknowledgement.
- **cost:** Usually <$0.02 per invocation; most cost is one planner turn, with verifier and compensation using typed local calls.
- **security:** A compensation must be explicitly allowlisted and risk-checked; never auto-undo an external send, purchase, deletion, or irreversible action. Secrets stay in browser/Mac; verifier returns hashes or minimal evidence. Require the existing physical approval latch for high-risk actions.
- **missing:** A typed compensation-plan field in the action ledger/job schema; A policy decision for which reversible actions may auto-compensate; A verifier-to-action correlation containing action_id and attempt_id

### "“Keep me from being interrupted unless it matters.”"
- **useful because:** The hive can combine the Mac's calendar/app state with relay urgency and the pendant's audio path: during a meeting or focus block, ordinary notifications become a quiet inbox item, while only urgent or owner-defined exceptions produce a short cue and spoken interruption. This makes the wearable helpful rather than socially disruptive.
- **path:** mac-planner → faculty-judgement → relay-realtime → faculty-action → browser-extension
- **model tier:** Cheap background model/classifier for urgency and calendar context; realtime only for an actual spoken escalation.
- **latency:** Under 2 s to classify an incoming event; under 250 ms for a local cue; defer nonurgent items until the focus block ends.
- **cost:** <$0.005 per event when rules/local state handle routine cases; model cost only for ambiguous urgency.
- **security:** Calendar titles and notifications are private; keep classification local when possible and send relay only an opaque urgency class. Never infer an emergency from message content without a configured rule. Owner chooses trusted contacts and quiet hours.
- **missing:** A durable focus-state/exception policy shared by Mac and relay; An event-ingest route for notification/message metadata with sensitivity labels; A pendant cue command that distinguishes quiet inbox receipt from urgent escalation

### "“When the pendant is plugged into my Mac, make it work normally even though LTE isn’t registered.”"
- **useful because:** The hardware is physically present on USB today but absent from the relay device table. A USB continuity mode would let the owner test and use capture, playback, inbox delivery, and physical approvals now, then seamlessly switch to LTE later, without falsely claiming radio connectivity.
- **path:** mac-terminal → mac-planner → relay-realtime → faculty-action → faculty-perception
- **model tier:** Local Mac bridge and relay rules; no realtime model needed except the owner's conversation.
- **latency:** Button-to-bridge acknowledgement under 300 ms; queued inbox/outbox reconciliation within 2 s of USB connection.
- **cost:** Near-zero API cost; implementation is a local serial daemon plus authenticated relay session. Hardware power draw is existing USB power.
- **security:** Mutually authenticate the serial endpoint and bind it to one relay session; never expose raw serial commands to arbitrary local processes. Mark every receipt transport=usb and prevent duplicate delivery when LTE later registers. Audio and voice notes remain encrypted and obey existing failure-path storage rules.
- **missing:** A concrete serial transport agent for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A relay session mode that accepts USB-attested device identity; A deduplicating transport handoff/state machine and observable receipts

### "“Finish this application for me, but stop exactly when my judgment is needed and let me approve each sensitive field without reading the secrets aloud.”"
- **useful because:** The owner could delegate a genuinely multi-page, authenticated workflow while retaining control over the points that matter: the browser fills routine fields, the pendant presents a redacted field label and risk, and a physical gesture authorizes only that field or step. Today the system can act or stage work, but cannot safely expose a structured sequence of decision points and resume it after each one.
- **path:** faculty-judgement → faculty-action → browser-extension → mac-planner → relay-realtime → faculty-perception
- **model tier:** Background/local planner for form mapping; realtime only for the owner's short approvals; no secret-bearing model context.
- **latency:** Immediate cue per checkpoint (<500 ms once a page is observed); workflow may run for minutes with durable pause/resume.
- **cost:** <$0.05 for a typical workflow; browser inspection and local state dominate, not model tokens.
- **security:** Secrets never enter relay or pendant; browser reports only typed labels, sensitivity, and hashes. Each approval is bound to one locator, value hash, expiry, and transaction step; navigation or DOM change invalidates it. Submission remains separately gated.
- **missing:** A durable checkpoint graph for multi-step browser workflows; A redacted browser-field proposal envelope and field-scoped physical approval; Resume/invalidate semantics when tabs, sessions, or page structure change

### "“If my Mac gets stuck while I’m away, recover it safely and tell me what you changed.”"
- **useful because:** The always-awake relay could detect a hung local agent or failed workflow, ask the Mac to perform a pre-approved recovery playbook, and use the pendant as an out-of-band alert. The owner would get resilience rather than a silent dead job, while destructive or ambiguous recovery waits for a physical approval.
- **path:** relay-realtime → mac-planner → mac-terminal → faculty-action → faculty-perception
- **model tier:** Cheap scheduled/background health checks and deterministic recovery playbooks; realtime model only if the owner asks for diagnosis.
- **latency:** Detect within 30 s, attempt safe recovery within 2 min, and deliver a concise pendant status when connectivity exists.
- **cost:** <$0.01 per health interval; local probes and process recovery dominate.
- **security:** Recovery commands are a signed allowlist, scoped to the agent user, with rate limits and a circuit breaker. No arbitrary shell escalation. Report exact actions and distinguish recovered, still-failed, and unknown.
- **missing:** A durable watchdog that can invoke a typed recovery playbook; Health signals tied to job leases rather than process liveness alone; An out-of-band pendant alert/status receipt for Mac-originated incidents

### "“Remember what I was doing across devices, and put me back at the exact next step when I return.”"
- **useful because:** A durable task handoff would let a voice request begun on the pendant continue in a browser and later resume from the Mac without repeating context or losing the authenticated tab. The owner gets continuity of intention, not a transcript: current goal, completed checkpoints, blocked reason, next action, and evidence are carried between surfaces.
- **path:** relay-realtime → faculty-judgement → faculty-action → faculty-perception → browser-extension → mac-planner
- **model tier:** Cheap background state summarization at checkpoints; realtime only for creating or changing the owner's goal.
- **latency:** Checkpoint in under 1 s after each verified step; resume brief in under 2 s.
- **cost:** <$0.01 per checkpoint with compact structured state; storage and browser observation dominate.
- **security:** Persist only minimal structured state, never page secrets or raw private content. Bind handoffs to owner/session and expire them. A resumed action must revalidate page/app state before execution.
- **missing:** A cross-surface task-handoff object with versioned checkpoints; Conflict rules when pendant, Mac, and browser independently update the same goal; A resume command that selects and revalidates a handoff


## Changes it proposed to its own stack

### `integration` — Add a verified-action transaction envelope spanning planner, executor, verifier, and ledger: action_id, attempt_id, declared postconditions, permitted compensations, approval nonce, and final status enum {verified, compensated, failed, unknown}. faculty-action must call verify_operation_step after execution and may invoke compensation only when policy explicitly allows it.
- **owner gets:** The owner stops hearing “done” when the Mac/browser only accepted a command; they get a truthful verified result or a clear, bounded failure.
- effort: Medium: schema and orchestration changes across existing actionLedger/policyRouter/job runner, plus tests for stale and conflicting evidence.  ·  risk: A bad compensation could create a second side effect; default to no compensation, require reversibility metadata, and preserve all receipts for recovery.
- cost: Negligible API cost beyond an additional local verification call; one extra planner turn only on failure.  ·  latency: Adds roughly 0.5–3 s for verification and longer only if compensation is needed.
- security: Improves safety by binding evidence to the exact attempt and keeping secrets out of evidence; high-risk actions remain approval-gated.
- depends on: verify_operation_step must expose action_id/attempt_id correlation; An owner-configured compensation policy

### `mac-harness` — Implement an authenticated USB pendant bridge daemon that exclusively owns the two live serial ports, translates the existing relay audio/event envelopes, reports transport health and device identity, and hands queued items between USB and LTE with idempotency keys.
- **owner gets:** The pendant can be worn and exercised immediately while attached to the Mac, instead of appearing dead until a future LTE registration; switching transports will not duplicate messages.
- effort: Medium-high: serial framing, reconnect behavior, attestation, relay session endpoint, and hardware-in-the-loop tests.  ·  risk: A malformed serial frame or stale queue could replay audio/actions; use signed envelopes, monotonic sequence numbers, bounded queues, and reject action commands unless the physical approval latch is present.
- cost: Near-zero model/API cost; small always-on Mac process, existing USB power.  ·  latency: Sub-300 ms local acknowledgements; reconnect reconciliation in a few seconds.
- security: Creates a new local attack surface, so bind to the signed device identity and restrict the daemon socket to the pendant agent user.
- depends on: Serial framing specification; Relay USB-session endpoint; Idempotent outbox/inbox manifest fields

### `context` — Introduce a versioned cross-surface Task Handoff object: goal_id, owner-visible summary, surface/session binding, ordered checkpoint records, next_action, evidence references, sensitivity map, expiry, and conflict/version token. Every executor must atomically append a checkpoint; resume must re-observe the bound app/tab and reject stale state instead of replaying it.
- **owner gets:** A request started by voice can continue later in the exact authenticated browser or Mac context, without the owner repeating themselves or the system pretending an old page is still current.
- effort: Medium-high: shared schema, durable storage, checkpoint writes in executors, and resume conflict handling.  ·  risk: Stale or over-detailed context could leak private page content or cause a wrong action; store typed summaries and hashes, expire aggressively, and require fresh observation before every mutation.
- cost: Small storage and local serialization cost; compact checkpoint summaries keep model/API spend low.  ·  latency: Sub-second checkpoint writes; resume adds one observation round trip.
- security: Improves isolation through session binding and sensitivity labels, but requires strict access control on handoff lookup.
- depends on: A durable relay-backed task store; Typed browser/Mac observation references; Executor hooks that emit atomic checkpoint receipts


## What it asked for

### `t26-cc4c` (tool) — mac_device_diagnostics
- why: The pendant and ESP32 are physically attached today, but there is no resolved read-only capability to enumerate serial ports, identify USB devices, or report a non-mutating serial handshake. Without it, faculty-action cannot tell whether USB continuity mode is actually available or verify a bridge receipt.

```json
{
  "operation": {
    "type": "string",
    "enum": [
      "serial_ports",
      "usb_device_identity",
      "serial_handshake",
      "jlink_probes"
    ]
  },
  "port_hint": {
    "type": "string",
    "enum": [
      "pendant",
      "audio_bridge",
      "all",
      "none"
    ]
  },
  "timeout_ms": {
    "type": "integer",
    "minimum": 100,
    "maximum": 10000
  }
}
```

## Its own summary

Recorded three owner-facing capabilities: verified execution with bounded compensation (single most useful trust primitive), focus-aware interruption triage, and USB continuity while the pendant/ESP32 are physically attached but LTE-unregistered. Also recorded two stack changes: correlated action/verifier transaction envelopes and an authenticated USB bridge with idempotent transport handoff. Requested a narrowly typed read-only mac_device_diagnostics tool for serial ports, USB identities, handshakes, and J-Link enumeration.

**Biggest unknown:** The live serial protocol and device identity/attestation format are still unknown. I still need the diagnostic tool to establish whether /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA answer safely, then a relay USB-session endpoint and outbox/inbox transport handoff schema before USB continuity can be implemented and honestly verified.

