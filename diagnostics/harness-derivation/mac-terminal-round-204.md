# Harness derivation — mac-terminal — round 204

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Run the pendant bench self-test and tell me exactly whether the wearable audio path is healthy.""
- **useful because:** The chips are physically attached now, but there is no owner-facing way to turn raw UART captures into a trustworthy answer. This would validate enumeration, firmware heartbeats, framing, I2S timing, resampling, and Bluetooth output in one short test, rather than making the owner interpret logs.
- **path:** pendant → relay → mac-planner → mac-terminal
- **model tier:** Use deterministic shell/parsing and a cheap background model for log interpretation; reserve realtime only for the final spoken answer if requested.
- **latency:** 15-30 seconds for a bounded 5-second capture and analysis; report partial results within 5 seconds if one chip is absent.
- **cost:** Usually <$0.01 API cost; dominated by local capture and parsing, not model tokens.
- **security:** USB logs remain on the Mac. The command must be fixed to the existing dual-chip diagnostic scripts, bounded in duration/output, and must not claim wearable LTE health from a USB bench. No confirmation needed for this read-only test.
- **missing:** A real serial diagnostic implementation (the granted schema is still unresolved) or a typed Mac action that invokes the existing dual_chip_autocapture.sh and reads its output; A parser for nRF9160/ESP32 heartbeat, framing, I2S underrun, and A2DP state; A relay/pendant result envelope that distinguishes USB bench from LTE production

### ""Keep watching that Mac or browser task until it is genuinely finished, and tell me immediately if it stalls or fails.""
- **useful because:** Today a long shell/browser action can be marked processing after a restart, cancellation cannot interrupt a running shell, and the pendant only knows a coarse last state. The owner needs a truthful watchdog that observes progress and never turns silence into success.
- **path:** pendant → relay → mac-planner → browser-extension → mac-terminal
- **model tier:** Deterministic relay watchdog and job receipts first; a cheap background model summarizes only on state changes. Realtime speaks only the concise alert.
- **latency:** Heartbeat every 2-5 seconds; alert within 10 seconds of a missed heartbeat; no need to spend a model call on every poll.
- **cost:** <$0.01 per multi-minute task if state-change summaries are batched; polling and receipt storage dominate.
- **security:** Expose only task metadata, bounded output tails, and explicit browser provenance—not environment variables or arbitrary secret-bearing stdout. The watchdog must label a restarted job as unknown/stale, never completed.
- **missing:** A durable heartbeat/progress protocol from Mac executor to relay; Boot reconciliation for pendant-jobs.json and closure/joining of action ledgers; Per-action exit code, pid, and structured progress receipts; A small relay scheduler that updates the existing truthful_action_status_beacon with age and stale state

### ""Take the result from the signed-in browser, apply it to the local project, and show me exactly what changed.""
- **useful because:** The browser can reach authenticated sessions and the Mac can edit/run local files, but the owner currently has to manually bridge those worlds. This creates a provenance-preserving handoff: read a specific browser result, validate it, make a targeted local change, run a check, and return a diff plus source URL.
- **path:** pendant → relay → browser-extension → mac-planner → mac-terminal
- **model tier:** Cheap model for extracting structured fields and generating a patch; deterministic local checks and diff; realtime only for the spoken completion summary.
- **latency:** Under 30 seconds for a small text/config artifact; stream progress after browser read and before local mutation.
- **cost:** <$0.03 for extraction plus patch review; local diff/test time dominates.
- **security:** Never copy whole pages or cookies. Transfer only selected claims/artifact bytes with host, URL, timestamp, and hash. Limit writes to the requested project and retain an undoable patch; ask before broad or destructive edits.
- **missing:** A typed browser-to-local artifact handoff carrying bounded bytes, SHA-256, URL, and provenance; A patch/apply/check action that records pre/post hashes and can undo; A relay transaction ID joining browser provenance, Mac job, and pendant spoken result

### ""I lost my place—continue the exact task I was doing before the Mac slept or the browser session dropped, and tell me what you are resuming before you touch anything.""
- **useful because:** Today the system can report individual jobs and browser state, but it cannot reconstruct a partially completed cross-surface workflow. The owner must manually remember which page, local file, command, and pending decision were part of one task. This would make sleep, link loss, and restarts survivable without silently repeating an email, purchase, form submission, or file mutation.
- **path:** pendant → relay → mac-planner → browser-extension → mac-terminal
- **model tier:** Use deterministic checkpoint collection and action-history reconciliation first; use a cheap background model to summarize the recovered workflow and identify the next safe step. Realtime is only needed to speak the short resume summary through the pendant.
- **latency:** Produce a resume candidate within 5 seconds of reconnect; do not execute until the owner confirms the proposed next step. Recovery can continue in the background while the Mac reconnects.
- **cost:** <$0.02 per recovery, dominated by summarizing a compact checkpoint rather than replaying full conversation or page contents.
- **security:** Persist only task identifiers, hashes, URLs, page titles, local paths, action receipts, and redacted intent—not cookies, full page text, or shell environment. Treat any mutation whose completion is uncertain as 'unknown', never as completed; require confirmation before replaying non-idempotent actions.
- **missing:** A durable cross-surface checkpoint schema with workflow ID, step sequence, pre/post hashes, provenance, and explicit unknown state; A reconnect reconciler joining pendant turn IDs, relay jobs, Mac job/ledger records, and browser command IDs; Idempotency keys and resume-safe replay for Mac and browser actions; A compact owner-visible resume preview delivered through the pendant before execution

### ""If this task gets blocked by a login, permission prompt, CAPTCHA, or sleeping Mac, tell me exactly what I need to do, wait, and continue from the same step when it is cleared.""
- **useful because:** Authenticated browser sessions and local Mac actions fail in ways that look like ordinary task errors. The owner currently has to notice the prompt, remember the original goal, and restart manually—often duplicating a side effect. This would turn an interruption into a guided handoff rather than a lost workflow.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → mac-terminal
- **model tier:** Deterministic detectors classify known blocked states and hold the workflow; a cheap model writes the one-sentence instruction. Realtime speaks only the request and resumed result.
- **latency:** Detect a blocked state within 2 seconds; speak the required owner action immediately; resume within 5 seconds of a verified clear signal.
- **cost:** <$0.01 per interruption; most work is local state detection and polling.
- **security:** Never ask the model to read or repeat passwords, MFA codes, cookies, or CAPTCHA contents. The owner completes sensitive prompts directly on the Mac/browser. Store only prompt type, application/host, and workflow step; expire the pending continuation.
- **missing:** Typed blocked-state events from browser and Mac surfaces; A pause/resume state machine that freezes the exact action boundary and rejects duplicate submissions; A pendant interaction for acknowledge/ready without inventing a second meaning for the existing recording button; A secure local proof that the prompt cleared, rather than trusting a model's visual guess

### ""Undo the last thing you did across my Mac and browser, and show me anything that could not be reversed.""
- **useful because:** The system can act across local files, applications, and authenticated pages, but recovery is fragmented: some Mac actions have undo handlers while browser mutations and shell effects do not share a common history. A single owner-facing undo would make experimentation safe and would explicitly identify irreversible effects instead of pretending the whole task was rolled back.
- **path:** pendant → relay → mac-planner → browser-extension → mac-terminal
- **model tier:** Deterministic receipt matching and inverse actions first; a cheap model explains the resulting partial rollback. Realtime is only for the pendant's short confirmation and outcome.
- **latency:** Identify the last completed workflow in under 2 seconds; execute reversible inverses within 10 seconds; stop and report at the first ambiguous or non-idempotent inverse.
- **cost:** <$0.02 per undo; local/browser action execution and receipt reconciliation dominate.
- **security:** Never infer an inverse from prose alone. Require signed action receipts, pre/post hashes, target identity, and an explicit reversibility flag. Deleting or sending externally must remain reported as irreversible; do not claim rollback after a partial failure.
- **missing:** A cross-surface inverse-action registry for Mac, browser, and file operations; Receipt-level pre/post state and durable workflow ordering shared by browser and Mac; A partial-rollback protocol with compensating actions and an honest irreversible-effects report; A pendant confirmation interaction that is distinct from recording and existing marker behavior


## Changes it proposed to its own stack

### `hardware` — Replace the prototype HUZZAH32 A2DP bridge with an ESP32-S3-class bridge board with external PSRAM, a real I2S codec/headphone interface, and a hardware watchdog; retain SBC/A2DP for compatibility but leave RAM and CPU headroom for jitter buffering, link diagnostics, and a second output path.
- **owner gets:** Audio would stop dropping into silence when buffering or Bluetooth scheduling spikes, and the pendant could truthfully report whether the fault is microphone, USB/LTE transport, resampling, or headphones instead of making every failure sound like 'the AI is broken'.
- effort: Medium hardware redesign plus firmware port, enclosure and power validation; bench-test against the currently attached ESP32 before changing the wearable.  ·  risk: ESP32-S3 Bluetooth profile support and existing headphone pairing may differ; recover by keeping the current SBC bridge as a fallback and gating rollout behind a hardware capability bit.
- cost: Roughly +$10-$25 BOM over the development board and modestly higher idle power, depending on codec, PSRAM, and enclosure.  ·  latency: Can reduce underrun recovery latency by 50-150 ms through larger, better-managed buffers, while preserving the current 44.1 kHz A2DP contract.
- security: No new cloud data; diagnostic frames should omit audio payload and expose only counters, clock drift, and connection state.
- depends on: audio_link_truth_and_recovery; A typed bounded USB bench diagnostic path; A product audio-bridge board specification rather than the current prototype pinout


## What it asked for

_Nothing._
