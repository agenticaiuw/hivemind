# Harness derivation — faculty-perception — round 224

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac and pipeline truth** — At 2026-08-09T00:46Z the Mac agent reports Accessibility and Screen Recording granted, all required permissions ready, browser extension online with zero pending commands, relay reachable with D1 persistence and Mac bridge online. The newest pipeline run has 24 kHz PCM accepted by relay (466700 bytes) but delivery is held_by_relay, awaitsDevice=true, heard=unknown, provesPlayback=false; no device_playback event exists.
  - evidence: GET /ops/status HTTP 200 and GET /pipeline HTTP 200 live responses

## Capabilities it proposed

### "Tell me only what is definitely true right now across my Mac, browser, relay, and pendant — and label every other claim unknown."
- **useful because:** The system currently mixes Mac-derived preferences, relay socket delivery, count-capped history, and absent pendant telemetry as if they had equal authority. This gives the owner a short spoken reality report with source, age, coverage limit, and explicit contradictions instead of confident fiction.
- **path:** relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement
- **model tier:** background for the cross-surface collection and contradiction scan; realtime only to phrase the final one-sentence answer
- **latency:** 2–5 seconds for relay/Mac/browser reads; never wait on an absent pendant and report it as unknown
- **cost:** Low: one background model call over bounded structured records; dominated by context serialization, not audio
- **security:** Read-only and bearer-authenticated. Do not include page bodies, secrets, or owner memory values in the report; preserve provenance and distinguish machine-origin facts from owner-origin facts.
- **missing:** A single source-aware assertion schema with freshness and coverage fields; A browser snapshot adapter that reports session liveness without page content; A pendant status adapter; today no pendant is registered and absence is not proof of offline state; Contradiction policy that quarantines machine-origin preferences such as the stale America/Chicago value when /etc/localtime says America/New_York

### "Is my pendant physically connected and exchanging real audio right now? If it is only on USB bench power, say that; if it is relaying speech, show the last verified packet and playback evidence."
- **useful because:** Today the Mac bridge is online but no nRF9160 has ever registered, while historical pipeline audio can look live. A single answer must join physical USB observation, relay device state, and fresh audio telemetry so the owner can stop mistaking recorded history for a live wearable.
- **path:** mac-terminal → mac-planner → relay-realtime → faculty-perception → faculty-action
- **model tier:** background deterministic inspection; realtime only when the owner asks during a live voice turn
- **latency:** Under 3 seconds when USB is attached; 10 seconds maximum for a bounded audio exchange; fail closed if no fresh observation
- **cost:** Low API cost; dominated by a bounded serial probe and at most one short audio test, not model tokens
- **security:** USB serial is local and must use an allowlisted device path with strict byte/time bounds. Never upload raw microphone audio for diagnostics; send counters, hashes, and stage outcomes only. Require confirmation before generating audible test tones.
- **missing:** A production Mac action that can perform a bounded read on the known nRF9160 and ESP32 serial ports and return timestamped evidence; A freshness join between serial observations, GET /v1/devices/status, and pipeline events; A safe loopback test protocol that identifies packet receipt and physical playback without recording private speech

### "Before you act, show me the evidence that justifies this action — what was observed, when, by which surface, what is inferred, and what would make it unsafe."
- **useful because:** Judgement and action currently receive completion-like signals that can mean only 'the Mac ran' or 'the relay wrote bytes.' An evidence preflight lets the owner approve a consequential action knowing whether the target, page state, permission, and delivery path are actually observed or merely inferred.
- **path:** faculty-perception → faculty-judgement → faculty-action → browser-extension → mac-planner → relay-realtime
- **model tier:** Cheap background model for assembling and classifying evidence; realtime only for the final approval prompt
- **latency:** 1–3 seconds for cached evidence, up to 5 seconds for a fresh browser/Mac observation; block rather than guess when evidence is stale
- **cost:** Low-to-moderate: mostly structured records and hashes; model cost is dominated by evidence summarization, not raw page or audio content
- **security:** Evidence must carry redaction, source, capture time, and revocation state. Never treat a browser capsule's text or relay page read as trusted instructions. Require explicit confirmation for mail, deletion, purchases, or irreversible actions even when evidence is strong.
- **missing:** A common assertion record consumed by judgement and action, with observed/inferred/unknown status; Mount local browserProvenance routes and connect capsule links to action ledger receipts; A relay-origin correlation ID and content hash for cloud browser reads; A hard preflight rule that refuses action when the target evidence is expired, revoked, or only inferred

### "If I give a command while the pendant is offline, remember the exact intent locally, then when it reconnects reconcile it against the current Mac and browser state and ask me only about conflicts before doing anything."
- **useful because:** The owner should not lose a spoken request because LTE or the relay disappeared, nor should a delayed command blindly act on stale page or file state. This creates a safe offline-to-online handoff rather than pretending offline capture was execution.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Small local/device model or deterministic intent envelope while offline; background model for reconciling state after reconnect; realtime only for conflict questions.
- **latency:** Local capture under 300 ms; reconciliation within 10 seconds of reconnect; no action until conflicts are resolved.
- **cost:** Low-to-moderate: tiny encrypted intent envelopes and one background reconciliation call; state snapshots dominate context size.
- **security:** Persist only an encrypted, bounded intent envelope—not raw audio. Bind each envelope to an owner session, monotonic sequence, expiry, and deduplication key. Require confirmation for destructive or externally visible actions and discard expired intents.
- **missing:** An offline intent envelope and bounded nonvolatile queue on the pendant; Relay reconnect ingestion with idempotency and expiry; Fresh Mac/browser state snapshots at reconciliation time; A conflict taxonomy distinguishing stale target, changed permissions, duplicate request, and destructive consequence

### "Tell me what changed on my Mac, in my browser sessions, or in relay-held work while I was away, and separate my own actions from unexplained changes."
- **useful because:** The current continuity views show work and liveness but cannot establish whether a state change was owner-initiated, automation-initiated, or unexplained. A signed cross-surface drift report would catch missed actions, duplicate automation, and account changes before they become surprises.
- **path:** faculty-perception → relay-realtime → mac-planner → browser-extension → faculty-judgement
- **model tier:** Background deterministic diffing with a cheap classifier for change attribution; realtime only to summarize urgent drift.
- **latency:** Capture baselines continuously; answer in under 3 seconds from the latest signed checkpoints, with a clearly bounded observation interval.
- **cost:** Low ongoing storage and hashing cost; occasional background classification, with no raw page or audio sent to a model.
- **security:** Use append-only, hash-linked checkpoints with per-surface redaction. Never claim attribution merely because a Mac process ran; label actor identity as verified, delegated, or unknown. Require confirmation before remediation such as logout, undo, or deletion.
- **missing:** A common signed checkpoint format across relay, Mac, browser, and pendant; A durable actor/authorization identity attached to every mutation and automation receipt; Browser and Mac mutation feeds rather than only current snapshots; A bounded drift ledger with owner-visible retention and revocation

### "When a multi-step request partially fails, give me a precise recovery choice: resume only the uncompleted steps, undo the completed reversible steps, or stop and leave everything untouched."
- **useful because:** A Mac receipt or relay completion currently does not describe the whole distributed transaction, and a response can be held at the relay even after local work completed. The owner needs recovery choices grounded in actual side effects, not a generic failure message or a dangerous blind retry.
- **path:** faculty-perception → faculty-judgement → faculty-action → mac-planner → browser-extension → relay-realtime
- **model tier:** Deterministic transaction/recovery planner first; background model only to explain the choices; realtime for the concise spoken decision.
- **latency:** Under 2 seconds for ledger inspection; never auto-resume or undo while any step's side effect is unknown.
- **cost:** Low model cost; dominated by durable step receipts and reconciliation, not inference.
- **security:** Every step needs idempotency, reversibility, pre/post evidence, and an explicit unknown state. Never claim undo succeeded without verification. Destructive or externally visible compensations always require confirmation.
- **missing:** A cross-surface transaction envelope linking browser commands, Mac actions, relay jobs, and audio delivery; A common step state machine including committed, reversible, unknown, compensated, and unverifiable; Verified postconditions and compensation handlers for each action type; A recovery UI/voice prompt that exposes unknowns instead of collapsing them into completed


## Changes it proposed to its own stack

### `context` — Install a provenance-aware timezone guard in contextProjection and routine scheduling: machine-origin timezone preferences cannot override the authoritative Mac zone, and any contradictory pinned preference is surfaced as a quarantine warning rather than injected into the Owner context head. Keep the stored fact untouched until the owner explicitly edits or deletes it.
- **owner gets:** Routines, 'this morning,' quiet hours, and file times stop silently using America/Chicago when this Mac is actually America/New_York. The owner gets a visible warning instead of repeatedly receiving a wrong timezone in every prompt.
- effort: Small-to-medium: add a guard at projection/scheduling boundaries, record the contradiction with source and timestamps, and add regression tests for owner-origin versus machine-origin preferences.  ·  risk: A legitimate travel timezone could be suppressed if the owner intended it but never recorded that intent. Recovery is explicit confirmation or editing the preference; never delete the existing fact automatically.
- cost: Negligible API cost and no hardware cost.  ·  latency: Effectively none; one local comparison against /etc/localtime.
- security: Improves safety by preventing a high-confidence machine-derived fact from controlling reminders or actions. Do not expose unrelated memory values in the warning.
- depends on: GET /machine-context; GET /memory/projection; A provenance-preserving context projection hook; An owner-confirmation path for changing pinned preferences


## What it asked for

_Nothing._
