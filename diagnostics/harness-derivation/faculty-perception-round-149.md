# Harness derivation — faculty-perception — round 149

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac/browser/relay state at 2026-08-08T02:03Z** — The exact AI Pendant Agent now has Accessibility and Screen Recording granted; /ops/status reports permissions.ready=true, all listed automation grants present, computer-use loop enabled, but visionUploadConsented=false. Safari extension is online on x.com (tab 1163292, 9 tabs, no pending commands); Mac bridge and relay are reachable. GET /v1/devices/status is not a Mac-agent route (404), so this probe cannot establish pendant registration.
  - evidence: GET /ops/status 200 and GET /browser/status 200 at 2026-08-08T02:03Z; GET /v1/devices/status 404 explicitly says no such route on this agent.
- **continuity snapshot grant resolution** — The granted read_continuity_snapshot tool is not callable in this runtime: its resolver scored below threshold and returned nearest routes GET /ops/snapshot and GET /pipeline. Therefore I cannot honestly claim a unified continuity snapshot; current evidence had to be collected from separate probes.
  - evidence: Direct call to read_continuity_snapshot returned error 'could not be resolved' with nearestRealCapabilities GET /ops/snapshot (0.447) and GET /pipeline (0.443).

## Capabilities it proposed

### "Before you send, click, change, or remind me, verify that the target state is fresh and say exactly what you observed, what may have changed, and what you cannot see."
- **useful because:** The system currently knows many states but can still act on a stale tab, stale job, or relay belief. A target-bound preflight makes every consequential action honest: it either proves the relevant surface was observed within a freshness budget or asks instead of silently guessing. This is more useful than a generic dashboard because it prevents the wrong action.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Cheap background perception for collecting and normalizing state; realtime only to explain the resulting preflight in the owner's turn.
- **latency:** Under 500 ms for Mac/browser/relay checks; pendant state may be last-known and explicitly marked stale.
- **cost:** Usually <$0.001 in API/model cost; dominated by one short explanation only when the preflight finds a conflict.
- **security:** Return capability-limited facts, not page secrets or full tab contents. Bind the preflight to an action target, session, and observation timestamp; require confirmation when freshness is exceeded or surfaces disagree.
- **missing:** A target-bound preflight object with per-field observedAt, source, freshness deadline, and unknown reason; A relay-side pendant registry/health read exposed to the perception layer; Action handlers that refuse or request confirmation when the preflight is stale

### "Don't interrupt me unless you can tell whether I'm speaking, listening, driving my attention in the browser, or away; if you do interrupt, tell me which signal made it safe."
- **useful because:** A worn assistant that speaks at the wrong moment is actively harmful. This would combine local audio/VAD quality, the Mac's current app and permission state, browser tab activity, and relay delivery conditions into an interruption decision with an explicit reason. It can defer low-priority speech without pretending the owner heard it.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → unified
- **model tier:** A small classifier/rules engine on the Mac and pendant; use the expensive realtime model only when signals conflict or the owner asks why.
- **latency:** Local signal classification under 100 ms; decision under 300 ms. Deferred announcements should be reevaluated on the next safe boundary, not polled expensively.
- **cost:** Near-zero for local signals; <$0.002 only for ambiguous conflict explanations.
- **security:** Keep raw microphone audio local and emit only quality/VAD features. Browser activity should be reduced to host/title/category unless the owner explicitly permits content. Never infer driving or physical safety as fact from an app signal; label it as unknown.
- **missing:** A shared interruption-state schema with speaking/listening/attention/deferred/unknown and confidence; A Mac observer for frontmost app and idle/focus state that does not depend on screen recording when AppleScript can answer it; Pendant-to-relay forwarding of the accepted offline-capture-integrity-sentinel verdict and playback ledger state; A scheduler/announcement policy that consumes the state and records why an item was deferred

### "When something goes wrong, tell me the first boundary that failed—my voice, the link, the relay, the Mac, the browser, or playback—and show the one piece of evidence for that diagnosis."
- **useful because:** Today a job can look completed when only the Mac ran, a browser command can be pending while the relay is healthy, and relay delivery does not prove playback. A causal failure card would stop the system from giving me a confident but false success and would tell me the shortest recovery path.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Deterministic causal rules over telemetry first; a cheap text model summarizes only the selected boundary and evidence. Realtime is reserved for speaking the explanation.
- **latency:** Attach a provisional boundary within 1 s of a failed or stalled stage; final card within 3 s after timeout or reconnection.
- **cost:** <$0.001 per incident; storage is a bounded event index, not transcripts or screenshots.
- **security:** Evidence must be redacted and content-addressed; do not include page text, audio, tokens, or private app contents by default. Mark inference versus device-originated fact, and require confirmation before automated retry if an external side effect may have happened.
- **missing:** A common stage vocabulary with monotonic sequence numbers across capture, transport, relay acceptance, Mac execution, browser result, and device playback; A durable bounded causal index that preserves the first missing/contradictory edge instead of only the final completed status; Relay access to device-originated playback acknowledgements and Mac access to relay job receipts in one joinable record; A recovery policy mapping each boundary to safe retry, ask, or stop

### "Let me say 'make this change everywhere' and have you stage the Mac, browser, and relay effects as one transaction, show me the complete diff, then commit only when every surface confirms its precondition; if one surface fails, leave the others untouched or explain the exact partial state."
- **useful because:** Today multi-surface work can produce a successful Mac receipt while a browser command is still pending or a relay side effect has already happened. The owner needs one understandable commit boundary, not several local successes that must be reconciled by hand.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Deterministic transaction coordinator and existing action ledgers do the planning, validation, commit, and compensation; use realtime only to summarize the final transaction state.
- **latency:** Stage and validate within 2 seconds for ordinary Mac/browser changes; commit may take up to 10 seconds when a browser session or relay round trip is required.
- **cost:** Usually under $0.003 per transaction; storage and latency are dominated by pre-state snapshots and compensation receipts, not model tokens.
- **security:** Never silently commit external or destructive effects. Require explicit confirmation for the final barrier, bind every mutation to an owner-approved transaction ID, redact secrets from diffs, and expire staged plans. Compensation is not presented as rollback unless the target actually confirms it.
- **missing:** A cross-surface transaction protocol with prepare, commit, abort, and compensation states; Browser mutations and relay actions that support prepare or an equivalent idempotent commit token; A durable join between Mac action-ledger entries, browser command receipts, and relay job receipts; A user-facing diff/partial-state representation that distinguishes confirmed rollback from best-effort compensation

### "Before you send a message, publish, purchase, or submit anything as me, read back the exact recipient, destination, text, amount, and attachments from the real app, then require a deliberate physical confirmation on the pendant; if the app changes afterward, cancel and ask again."
- **useful because:** A fluent assistant can be wrong at the final boundary even when its plan was right. The owner needs protection against a changed tab, wrong recipient, injected page instruction, or stale form—not merely a confirmation of the assistant's own draft.
- **path:** pendant → mac-planner → browser-extension → mac-vision → relay-realtime
- **model tier:** Deterministic extraction and destination comparison first; use a local model only to render a concise spoken summary. No cloud model is needed for the final confirmation.
- **latency:** Read-back and confirmation in under 2 seconds after the form is ready; any DOM or app mutation invalidates the confirmation immediately.
- **cost:** Near-zero model cost for local extraction; small bounded storage for the signed approval and final-state hash.
- **security:** The confirmation must be bound to the exact final payload, recipient, origin, and window/session, not a natural-language paraphrase. Never expose full secrets in logs or relay telemetry. Reject confirmation if focus, tab identity, or content hash changes; require a second confirmation for irreversible financial or public actions.
- **missing:** A cross-surface final-submission inspector that can extract the real payload from AppleScript-controlled apps and the browser extension; A pendant-local physical confirm/cancel gesture with nonce display or haptic code, usable offline; A final-state content hash and compare-before-submit hook for browser and Mac action paths; A policy registry classifying actions by reversibility, amount, audience, and required confirmation strength


## Changes it proposed to its own stack

### `hardware` — Add a low-power wearer-presence sensor to the pendant enclosure: capacitive skin contact plus a 3-axis accelerometer pattern, with a tiny local state machine that reports worn, removed, stationary, and uncertain. Include a physical privacy shutter or button that forces microphone-disabled state and emits a visible/haptic confirmation. Do not store raw biometric or motion data; expose only signed state transitions with monotonic sequence numbers.
- **owner gets:** The owner should know—and the system should know—whether the assistant is actually being worn before it speaks, records, or treats an offline event as something the owner could have heard. It also gives the owner an immediate, physical guarantee that the microphone is disabled, even when the Mac or relay is unreachable.
- effort: New enclosure flex/PCB, sensor driver, calibration, battery characterization, and relay/agent policy integration. Prototype with capacitive electrode and existing IMU first; production revision should validate false-positive rates across clothing and skin conditions.  ·  risk: False worn/removed transitions could suppress an important alert or record when nobody is wearing it. Recover by using an uncertain state, retaining the current audio-delivery acknowledgement semantics, and never treating worn as proof of hearing. A physical shutter failure must default to microphone disabled and be surfaced on reconnect.
- cost: Roughly $2–8 in added components and PCB/enclosure complexity at small volume; capacitive sensing and intermittent IMU sampling should add well under 1 mA average, with a small calibration cost in battery life.  ·  latency: Local state transition under 100 ms; shutter state should gate capture immediately in firmware. Relay visibility is eventually consistent when offline.
- security: Improves privacy by making microphone-off a local hardware-enforced fact. Avoid exporting raw touch, motion, or presence streams; sign only state transitions and firmware build identity.
- depends on: Existing offline-reality-beacon and audio-delivery acknowledgement queue; Firmware support for a local microphone gate and monotonic event sequence; Relay and Mac policies that treat unworn/uncertain as no-proof-of-hearing rather than as device failure


## What it asked for

_Nothing._
