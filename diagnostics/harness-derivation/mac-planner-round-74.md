# Harness derivation — mac-planner — round 74

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent readiness round 74** — Local agent and relay are reachable, but Mac readiness is false: Accessibility trusted=false and Screen Recording granted=false; computer-use loop is disabled because vision upload consent is false. Browser extension home-chrome is offline with 4 pending commands. Calendar/Mail automation grants are cached, but the newly granted read tools currently return an unimplemented-tool error.
  - evidence: GET /ops/status HTTP 200 and calls to mac_readonly_inspect/mac_read_sources returned 'This tool was granted a schema but has no implementation yet.'

## Capabilities it proposed

### "“If I start a task by voice and walk away or the connection gets bad, keep doing the safe parts on my Mac/browser and tell me on the pendant when it is ready for review.”"
- **useful because:** Today a spoken request is tied to one live call: LTE-M contention can lose seconds of uplink, and leaving the Mac or dropping the WebSocket strands the task. This makes the pendant a durable handoff point while preserving the Mac's private app/browser reach. It is distinct from generic background jobs because it captures the exact in-progress conversational intent, evidence, and stopping point, then resumes only bounded, reversible work.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use realtime only to capture a compact intent checkpoint during the call; use a cheaper background model on the relay to decompose and reconcile; use gpt-5.6-luna on Mac for planning and the existing Mac/browser executors for actions. No model should reprocess the full transcript after handoff.
- **latency:** Emit a handoff token within 300 ms of call loss or an explicit double-button 'continue'; Mac/browser polling resumes within 2 s. Completion notification can be delayed up to 30 s when the Mac is asleep/offline. Require explicit owner review before send/delete/purchase or any irreversible browser step.
- **cost:** About $0.01–$0.05 per handed-off task, dominated by one background decomposition and one completion summary; no repeated realtime audio tokens after the handoff. Storage is a few KB of structured intent/evidence per task plus existing receipts.
- **security:** Private browser URLs, snippets, and the task checkpoint leave the Mac only through the authenticated relay; encrypt at rest and expire checkpoints/results after 7 days. Never put secrets in the pendant token or spoken notification. The Mac should report app/tab/source and before/after evidence, and pause on destructive actions. Dashboard must show active handoffs and provide cancel/delete.
- **missing:** A pendant-local call-loss/explicit-handoff event that sends a small signed task token and queues a retry when LTE is unavailable; Relay persistence and a resumable task state machine linking one conversation turn to Mac/browser jobs, with lease, timeout, cancellation, and idempotency keys; Mac bridge support for reconnecting to a durable handoff, checkpointing completed steps, and returning typed receipts rather than only a final string; Browser bridge support for restoring the exact tab/session and pausing at irreversible steps; A low-bandwidth pendant notification protocol (completion, needs-review, failed) and dashboard controls for review/cancel/history

### "“If my Mac crashes, sleeps, or I accidentally close something, reconstruct what I was doing from my open documents, browser tabs, and recent pendant conversation, then restore a safe working set and tell me what could not be recovered.”"
- **useful because:** The owner currently loses the relationship between spoken intent, unsaved desktop work, and authenticated browser research when a machine or app disappears. This would create a recoverable personal workspace rather than merely reopening individual files: it would identify the active thread, restore only the relevant documents and tabs, and clearly separate verified recovery from inference.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the realtime model only for a compact conversation checkpoint while the task is active. Use a cheaper background model to cluster recent receipts, file metadata, and browser provenance into a recovery plan. Use gpt-5.6-luna only for ambiguous reconstruction; deterministic local code performs inventory and reopening.
- **latency:** Checkpoint incrementally with less than 1 second of local overhead. After reconnect, produce an initial recovery inventory within 5 seconds and restore the selected working set within 15 seconds. If reconstruction is ambiguous, leave everything untouched and ask one short pendant question.
- **cost:** Usually under $0.02 per recovery, dominated by one background summarization; local metadata snapshots and receipts are negligible. Do not upload file bodies or page contents unless the owner explicitly requests deeper reconstruction.
- **security:** Recent filenames, tab URLs, and conversation checkpoints are sensitive. Keep raw content on the Mac, encrypt relay checkpoints, use short TTLs, and redact secrets from the pendant. Never restore or submit browser mutations automatically; show source, timestamp, and confidence for every recovered item. Provide a one-command purge and disable switch.
- **missing:** A Mac journal of workspace checkpoints containing app/document identity, unsaved-change indicators, and recent action receipts without copying file contents; Browser bridge support for durable tab identity and restoration with authenticated-session boundaries; Relay storage for encrypted, expiring recovery manifests keyed to the Mac and pendant, plus a crash/reconnect trigger; A recovery planner that distinguishes verified state from inferred intent and emits a reviewable manifest; Dashboard and pendant controls for restore, skip, purge, and report unrecovered work

### "“Undo the last thing you did for me, across the Mac, browser, and any drafts or reminders, and show me exactly what was restored.”"
- **useful because:** The current system can leave a receipt, but receipts do not form a cross-surface restore point. A single request should reverse a completed multi-step task—restore moved files, revert edited drafts, remove created reminders, and restore browser form fields where possible—without pretending that an irreversible send or purchase can be undone.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic receipt replay and inverse operations first; use a cheaper background model only to explain conflicts. Reserve realtime for the short spoken result. Never use a model to guess an inverse when a typed inverse is absent.
- **latency:** A simple local rollback should begin within 2 seconds and finish within 10 seconds. If any step is non-reversible or has drifted, stop before that step and report a partial rollback with evidence.
- **cost:** Typically below $0.01 per rollback; cost is dominated by receipt storage, conflict inspection, and occasional background explanation rather than inference.
- **security:** Rollback itself can destroy newer owner changes. Every inverse must check the recorded before/after hash, current file version, tab URL/session, and reminder identity. Preserve a quarantine copy rather than deleting data, encrypt receipts, expire sensitive snapshots, and require the owner’s existing confirmation policy for destructive cleanup. Clearly mark sends, purchases, and external mutations as non-reversible.
- **missing:** A cross-surface transaction journal with typed inverse operations and before/after hashes; Mac file/editor adapters that create versioned quarantine snapshots for writes and moves; Browser form and draft mutation receipts with stable field identity and session affinity; Relay orchestration for dependency-ordered inverse execution, conflict detection, partial rollback, and cancellation; Dashboard and pendant language for previewing rollback scope and reporting irreversibility


## Changes it proposed to its own stack

### `integration` — Add a signed, low-bandwidth handoff envelope shared by pendant, relay, Mac bridge, and browser bridge. The envelope contains taskId, compact intent, allowed operation classes, last confirmed step, evidence hashes, expiry, cancellation nonce, and a monotonic sequence. Each surface acknowledges the sequence; the Mac and browser persist step receipts and can safely replay only idempotent steps after reconnect.
- **owner gets:** A dropped call or moving away from the Mac no longer loses the work already described. The owner can press the pendant once to continue, later hear 'ready for review,' and inspect exactly where the task stopped instead of repeating themselves.
- effort: 3–5 engineering days across firmware protocol, relay D1 schema/worker logic, local-agent bridge, and browser session restoration; add fault-injection tests for duplicate delivery, stale tabs, and mid-step disconnects.  ·  risk: Replay could duplicate a mutation or a stale browser tab could act on the wrong page. Mitigate with sequence numbers, idempotency keys, tab URL/session binding, before/after evidence, expiry, and mandatory pause at irreversible actions. Cancel and expire envelopes server-side.
- cost: A few hundred bytes per checkpoint and a few KB of D1 receipts; roughly $0.01 or less per handoff, mostly background summarization. Firmware RAM impact under 4 KB with a single queued envelope.  ·  latency: One LTE control packet and relay acknowledgement under 1 s when connected; reconnect polling adds 1–2 s on the Mac. No added latency to normal live audio.
- security: Use device-bound signing/MAC and short-lived opaque IDs; never place page text or secrets in the pendant envelope. Relay stores encrypted checkpoint metadata with 7-day TTL; dashboard exposes revoke/delete.
- depends on: Durable relay job state and cancellation; Mac/browser typed receipts and session affinity; Pendant event/retry queue and completion notification


## What it asked for

_Nothing._
