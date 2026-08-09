# Harness derivation — mac-planner — round 242

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“If a website reaches an OTP, payment, or security-confirmation step, tell me on the pendant exactly what kind of approval is needed, pause there, and continue only when I say ‘approve’.”"
- **useful because:** This turns risky authenticated browser work from a silent failure into a hands-free, bounded interaction. The browser keeps the secret and the Mac performs the click; the pendant carries only a redacted request such as ‘approve login to Acme, code required’ and the owner can reject without exposing a code to the model.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Realtime only for classifying the visible challenge and conducting the short voice exchange; deterministic browser rules and the Mac executor do the pause/resume. No background expensive model call.
- **latency:** Challenge detection under 2 seconds; spoken approval-to-resume under 1 second after the next browser poll.
- **cost:** Usually <$0.01 per challenge; browser polling and relay events dominate, with a short realtime turn only when the page needs disambiguation.
- **security:** Never transmit OTP values, payment numbers, or page body by default. Browser-side detector emits challenge type, origin, and a redacted label; approval must be bound to the exact tab/session and expire after 60 seconds. Reject on navigation, origin change, or stale command. Owner policy must explicitly authorize which challenge classes may be continued unattended; empty policy stops.
- **missing:** A browser challenge classifier that emits a typed, redacted approval-needed event; An approval token bound to browser session, tab URL/origin, and command hash; Pendant speech approval routing into the browser command queue

### "“Privacy now.” Then mute both sides of the pendant and immediately hide or freeze sensitive Mac and browser surfaces until I say “privacy off.”"
- **useful because:** The existing pendant privacy latch protects the wearer locally; this makes it protect the whole conversation. A spoken or button-triggered latch would stop Mac screen/UI observation, cancel queued browser inspections and prevent accidental text/audio leakage while the owner is beside another person.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Realtime for the short command only; enforcement is a deterministic latch propagated to Mac and browser, not an LLM decision.
- **latency:** Local pendant mute is immediate; Mac/browser suppression within 250 ms when connected, with the pendant remaining safe offline.
- **cost:** Negligible model cost; one state event per transition and cancellation of in-flight observation commands.
- **security:** The latch must fail closed on disconnect and survive reboot as the existing local privacy latch does. Do not rely on network confirmation to exit locally. Mac policy must define whether suppression means stop new observations, terminate active screen capture, lock/blank selected apps, or all three. Log only transition timestamps and surface IDs, never captured content.
- **missing:** Relay fan-out of the local_privacy_latch state to Mac and browser; A Mac observation cancellation endpoint and browser command invalidation keyed by privacy epoch; Owner-configurable suppression policy for active windows and queued actions

### "“Run a complete pendant bench check.” With the pendant and audio bridge plugged into my Mac, exercise both audio directions, collect serial diagnostics, compare them to the measured acceptance limits, and tell me pass/fail plus the failing stage."
- **useful because:** The hardware is physically present and testable today even though LTE registration is not. One spoken command would replace a multi-repository bench procedure and catch exactly the class of failures that previously caused distorted audio, dropped blocks, and audible preambles. It gives the owner a trustworthy answer before wearing the device.
- **path:** pendant → Mac USB serial → mac-planner → relay-realtime
- **model tier:** Background/cheap model or deterministic parser for metrics and threshold comparison; realtime only to report the short result if the owner is actively waiting.
- **latency:** Fixture and serial collection 30–90 seconds; result summary immediately after the final receipt.
- **cost:** <$0.02 per run; almost all time is device fixture execution and serial capture, not inference.
- **security:** Bench-only capability must require both expected USB identities (/dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA) and never infer LTE registration from USB success. Do not record microphone content: use the existing synthetic diagnostic fixture. Store raw logs locally with bounded retention; send only metrics and a receipt upstream.
- **missing:** A bounded serial command/read action with exit status and device identity checks; A relay-side acceptance evaluator for alias rejection, codec CPU, mic drops, tx starvation, and zero preamble samples; A single orchestrated job that correlates pendant and bridge timestamps into one receipt

### "“Start local pendant mode.” While the pendant is USB-connected and LTE is unavailable, let me press the real button and speak through the real audio path, have the Mac relay the session to the local agent, and clearly label the session as offline/bench mode."
- **useful because:** The pendant is physically usable today but is not registered with the relay. This gives the owner a real end-to-end conversation and button/audio test at the desk instead of making LTE registration a prerequisite, while making the mode boundary explicit so a bench session can never be mistaken for normal mobile operation.
- **path:** pendant → Mac USB bench harness → mac-planner → relay-realtime
- **model tier:** Realtime for the conversation; use a cheap deterministic bridge for framing, serial forwarding, and disconnect recovery. Do not spend a second model on transport.
- **latency:** Button-to-session start under 500 ms; audio relay adds under 100 ms one-way beyond the existing local serial/audio budget.
- **cost:** Normal realtime inference cost per spoken turn; no additional model call for the bridge. USB forwarding and framing are the dominant engineering work.
- **security:** Bench mode must be opt-in, visibly indicated by the single LED pattern and a voice/banner announcement, and must never silently activate the microphone. Restrict serial access to the two expected device identities, do not persist raw audio, and terminate the session when either USB device disappears. The relay must attach an explicit `transport=usb_bench` label to every event and refuse to present it as LTE telemetry.
- **missing:** A purpose-built, bounded USB bench bridge for the nRF9160 and ESP32 serial protocols (not a general serial session); Local relay routing that accepts bench audio/events and returns generated audio without requiring device registration; A firmware/host mode flag and visible LED indication that distinguish USB bench mode from cellular mode

### "“Keep my commitments consistent.” If I ask the pendant to change something while the Mac, browser, or another automation changes the same appointment, document, or order, show me one concise conflict on the pendant, preserve both proposed outcomes, and let me choose which one becomes real."
- **useful because:** Today independent surfaces can race: a browser edit can invalidate a Mac plan, or a calendar move can make a prepared document and reminder wrong. The owner should never discover that disagreement later by seeing a duplicated booking, stale file, or contradictory message. This would make the hive behave like one accountable assistant rather than several opportunistic automations.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use deterministic identity/version checks and structured diffs first; reserve the expensive realtime model for explaining genuinely semantic conflicts in one spoken sentence. Background reconciliation should use a cheaper model.
- **latency:** Detect conflicts within 2 seconds of the second mutation; pendant explanation under 3 seconds; no mutation is committed during the conflict window.
- **cost:** Usually <$0.01 per conflict; storage of versioned intent records and state checks dominate, not inference.
- **security:** Never roll back an external side effect speculatively. Every mutation needs an idempotency key, origin surface, target identity, prior version, and proposed post-state. Sensitive document or order contents should be reduced to redacted field-level diffs. If the owner is unreachable, freeze only actions classified as conflicting and allow unrelated work to continue.
- **missing:** A shared intent and version ledger spanning calendar, files, browser sessions, and pendant commands; Read-back adapters that verify the committed external state after each mutation; A conflict coordinator with idempotent commit, preserved alternatives, expiry, and owner-choice events; Compact pendant rendering for two or more redacted outcomes

### "“Give this task access only until it is done.” Let me delegate a job across the browser and Mac with a one-time, narrow authority that automatically expires when the job completes, times out, or changes scope, and tell me on the pendant exactly what authority remains."
- **useful because:** The owner can currently launch powerful automation, but a long-lived session or queued job can outlive the reason it was granted. Short-lived, task-bound authority would let him delegate sensitive work without remembering to revoke browser sessions, files, or pending actions later.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-judgement → faculty-action
- **model tier:** Deterministic policy and expiry engine; realtime model only translates the owner’s spoken scope into a structured request and confirms ambiguous targets.
- **latency:** Scope receipt under 1 second; revocation on completion, timeout, or scope drift under 500 ms.
- **cost:** <$0.005 per delegation; token issuance, revocation, and audit storage dominate.
- **security:** Scopes must name exact origins, files, action classes, and expiry; no wildcard authority. A navigation, account change, or new side effect requires a new grant. Revocation must be enforced locally when relay connectivity is lost, and receipts must prove which scope authorized each action.
- **missing:** A cross-surface capability lease format with audience, resource, action, expiry, and parent job ID; Mac and browser enforcement hooks that reject expired or scope-drifting commands; Pendant-readable lease status and a local fail-closed revocation cache

### "“Show me the whole consequence before you do it.” For a multi-surface request, render a single preview of the final calendar, browser, file, and message changes—including collisions and what cannot be undone—then let me approve that exact bundle or edit one part without rebuilding the rest."
- **useful because:** A list of low-level clicks is not a consequence preview. The owner needs to understand the resulting world across surfaces before an automation sends, books, moves, or deletes anything. An atomic semantic preview would make ambitious delegation understandable rather than forcing him to supervise every step.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Cheap structured state projection and deterministic diffing; use the expensive model only to summarize the final diff in owner language.
- **latency:** Preview in under 5 seconds for ordinary jobs; edits should update only affected projections in under 2 seconds.
- **cost:** <$0.02 for a complex bundle; external read-backs and semantic diffing dominate.
- **security:** Preview reads must be clearly separated from writes and must not trigger website side effects. Every preview needs a snapshot timestamp and stale-state warning; approval binds to a hash of the exact projected bundle and expires after source changes.
- **missing:** Cross-surface snapshot adapters for calendar/files/browser/message targets; A semantic projection and diff engine that can represent external side effects consistently; Bundle approval and partial-edit protocol with stale-preview detection


## What it asked for

_Nothing._
## Its own summary

This round I recorded four owner-facing capabilities: redacted browser security-challenge handoff (OTP/payment approval without exposing secrets), a cross-surface privacy epoch that suppresses Mac/browser observation when the pendant latch is active, a complete synthetic pendant/audio bench check with metric-based pass/fail, and an explicitly labeled USB bench conversation mode for the currently connected hardware. The recorder flagged the first and fourth as close to existing backlog ideas, so they should be treated as refinements rather than assumed new primitives. The strongest genuinely useful gap is the cross-surface privacy propagation: local_privacy_latch exists, but Mac/browser enforcement and an invalidation epoch do not. The bench-check proposal is immediately actionable with today's plugged-in chips and the existing diagnostic fixture.

**Biggest unknown:** Whether the existing browser page-watch/approval work already emits a typed challenge event, and whether the relay has any supported local USB-bench audio ingress. I still need those live contracts before claiming either close proposal is more than connective wiring. What is concretely missing is a browser-origin-bound approval token, a privacy-epoch cancellation mechanism across Mac/browser queues, a bounded serial bench harness with exit-status receipts, and a relay route that labels USB sessions as bench-only.

