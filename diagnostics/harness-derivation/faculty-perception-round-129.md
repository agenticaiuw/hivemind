# Harness derivation — faculty-perception — round 129

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-device-and-agent-state-2026-08-07** — Live /ops/status shows home-macbook-bridge online and browser extension online with 3 Safari tabs, but no pendant; AI Pendant Agent v0.5.0 has computer-use loop disabled, vision upload consent false, Accessibility and Screen Recording ungranted, while listed AppleScript automation grants are true. Relay is reachable and reports pendantPipelineTelemetry, pendantSpeech, persistentAgentState, and durableAudio capabilities.
  - evidence: GET /ops/status returned 200 at 2026-08-07T18:31Z with the complete agent/relay/browser state.
- **machine-timezone-2026-08-07** — Mac machine-context reports timezone America/New_York on MacBook-Air-6.local (macOS 26.5.2, arm64).
  - evidence: GET /machine-context returned 200 and machine.timezone=America/New_York.
- **browser-live-observation-2026-08-07** — Safari extension is online with 3 tabs, but its reported active tab is https://example.com whose title is 'Failed to open page'; pendingCommands=0. This is a live browser observation, not proof that all tabs failed.
  - evidence: GET /ops/status and GET /browser/status returned matching device state at 2026-08-07T18:31Z.

## Capabilities it proposed

### "“Did that really happen?” After any request, independently verify the intended postcondition across the right surfaces—DOM state in Safari, app state or file state on the Mac, relay receipt, and wearable delivery—and tell me exactly which parts are proven, unverified, or contradicted."
- **useful because:** Action receipts prove that an instruction was accepted, not that the world changed. This closes the dangerous gap where a form was filled but not sent, a file was written to the wrong place, or audio was queued but never delivered. It turns perception into a falsifiable contract rather than optimism.
- **path:** faculty-perception → browser-extension → mac-planner → relay-realtime → pendant → faculty-judgement
- **model tier:** Cheap background model maps each request to typed postconditions; deterministic route checks perform verification; realtime only reads the concise result aloud when the owner asks.
- **latency:** 1–3 seconds for local/browser checks, up to 15 seconds if relay/device delivery must be observed; return partial truth immediately rather than waiting indefinitely.
- **cost:** About $0.005–$0.03 per verification, mostly browser and relay calls; model use is small structured reconciliation.
- **security:** Capture only the minimum before/after fields and hashes, not full private pages or message bodies. Never claim sent/delivered from a local receipt alone; mark missing observation explicitly. Require confirmation only for a follow-up corrective action, not for read-only verification.
- **missing:** Typed postcondition schema attached to every job; Browser field/value and sent-vs-draft observation contract; Relay delivery acknowledgement and device playback receipt; A verifier that can query app/file state without Accessibility (AppleScript/allowlisted reads first)

### "“What am I missing?” Compare my current open browser pages, Mac jobs, reminders/calendar context, and recent relay conversation against my stated goal, then list only unresolved blockers and the one smallest next observation that would disambiguate each."
- **useful because:** The system currently can act and summarize, but it cannot tell the owner which uncertainty is preventing progress. A cross-surface blocker map prevents repeated attempts and exposes silent failures (for example, a browser tab that says ‘Failed to open page’ or a job with no delivery evidence) without taking action.
- **path:** faculty-perception → browser-extension → mac-planner → relay-realtime → unified
- **model tier:** Use a low-cost background model over compact typed observations and the active goal; deterministic freshness and contradiction checks should drive the result. Realtime is only for the spoken list.
- **latency:** Under 8 seconds on demand; each blocker should include its source and age, and stale data should trigger one targeted refresh rather than a broad crawl.
- **cost:** Approximately $0.01–$0.04 per check, dominated by one or two targeted browser/Mac reads.
- **security:** Do not summarize unrelated private tabs or calendar content; scope reads to the active goal and redact values not needed to establish the blocker. Observation is read-only; any suggested fix remains a separate confirmed action.
- **missing:** Goal-linked observation contracts and freshness/expiry rules; A unified contradiction detector for browser, job, relay, and device facts; Read-only calendar/reminder adapters with provenance

### "“Show me where reality diverged.” For a task or conversation, build a timeline of intent, plan, each attempted action, the browser/Mac state observed afterward, relay delivery, and device playback; highlight the first point where expected and observed state split, with a replayable evidence link."
- **useful because:** A current snapshot and postcondition check can say something is wrong, but not when or why. A causal divergence timeline lets the owner recover from silent failures without rerunning risky actions, and lets judgement choose the smallest correction. It is especially valuable while the pendant is absent because it distinguishes ‘never delivered’ from ‘delivered but not played’ rather than collapsing both into offline.
- **path:** faculty-perception → faculty-judgement → mac-planner → browser-extension → relay-realtime → pendant → unified
- **model tier:** Deterministic event correlation first; a cheap background model labels the first divergence and summarizes evidence. Realtime only narrates the result.
- **latency:** Under 10 seconds for existing events; up to 30 seconds if one missing postcondition observation must be refreshed. Never block on an unavailable pendant.
- **cost:** About $0.01–$0.05 per timeline, mostly compact event summarization; storage is small append-only metadata rather than page/audio bodies.
- **security:** Store hashes, route names, timestamps, tab IDs, and redacted field diffs instead of raw private content. Explicitly distinguish client receipt, relay acceptance, device delivery, and playback. Any replay or corrective action requires confirmation.
- **missing:** A single correlation ID propagated from voice intent through plan, job, browser command, relay event, and device playback; Immutable append-only observation events with monotonic timestamps and clock-offset metadata; Device delivery/playback acknowledgements (no pendant is currently registered)

### "“Remember this only while I’m here, and forget it when I leave.” Let the pendant create a temporary, local-first memory capsule from nearby speech, use it during the current situation across the Mac and browser, then automatically destroy it unless I explicitly promote specific facts to long-term memory."
- **useful because:** The owner can currently capture facts or ideas, but cannot safely create a bounded memory that follows a live situation without becoming permanent. This would make the pendant useful in meetings, errands, and private conversations while minimizing the risk of accidental retention.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Realtime model transcribes and tags only the live interaction; a cheap background model compacts the capsule and checks its expiry. Raw audio stays on-device unless explicitly promoted.
- **latency:** Under 500 ms for local capture and under 2 seconds for cross-device capsule updates; destruction should be immediate when the owner leaves or says forget.
- **cost:** About $0.01–$0.08 per capsule depending on duration; storage and transcription dominate, not the final summary.
- **security:** Default retention must be minutes or session-scoped, encrypted on pendant and Mac, and excluded from relay logs. Promotion must show the exact proposed facts and require explicit approval. Presence inference must be transparent and allow a physical button to force deletion.
- **missing:** Pendant-local encrypted scratch storage and presence/leave detection; A relay protocol for expiring, non-durable capsules; Memory promotion UI showing exact source spans and deletion receipts; Cross-surface capsule scope enforcement for Mac and browser

### "“Keep me oriented without interrupting me.” Use the pendant’s physical button, microphone, and local time to detect that I have entered a planned context, then quietly put the relevant Mac document, browser tab group, and next task in a spoken or tactile cue; suppress the cue if I am already speaking or moving through another context."
- **useful because:** Today the owner must remember to ask the system and manually assemble context. A worn device can notice the transition the Mac cannot—walking into a meeting, starting a routine, or returning to a project—and make the right context available without a screen takeover or a noisy notification storm.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-judgement
- **model tier:** A tiny on-device state machine handles button, timing, and audio-level triggers; a cheap background model selects relevant context. Realtime is reserved for the short spoken cue.
- **latency:** Local trigger under 200 ms; context assembly under 3 seconds; cues should be cancellable with one button press.
- **cost:** Less than $0.01 per cue after setup; model calls are small, while the main cost is maintaining context rules and optional speech output.
- **security:** No continuous raw audio upload: device emits only coarse trigger events unless the owner holds the button. Never infer sensitive location or conversation content without an explicit routine. Browser and Mac reads must be limited to the selected project.
- **missing:** Pendant firmware for local trigger/state machine and haptic/LED feedback; A cross-surface context bundle binding a project to document/tab/task identifiers; Presence/context transition policy with quiet hours and interruption suppression; Relay support for ephemeral push cues

### "“If I lose the connection, don’t lose my place.” Let the pendant and Mac maintain a signed, compact continuity card containing the current goal, last confirmed step, pending question, and expiry; when either reconnects, reconcile the cards and give me one spoken choice: resume, inspect what changed, or discard."
- **useful because:** The owner currently cannot distinguish a dropped link from completed work or safely resume a half-finished task after leaving the Mac. A continuity card uses the pendant’s physical presence and the Mac’s richer state together, preserving only the minimum needed to resume rather than replaying a whole private conversation.
- **path:** pendant → mac-planner → relay-realtime → browser-extension → faculty-perception → faculty-judgement
- **model tier:** Deterministic signed-card merge handles normal reconnects; a cheap background model summarizes conflicts. Realtime only presents the three choices.
- **latency:** Persist locally before link loss; reconnect reconciliation under 2 seconds. If cards conflict, present uncertainty rather than silently choosing.
- **cost:** Pennies per reconnect; payloads are tiny. The dominant cost is occasional conflict summarization.
- **security:** Cards contain no raw transcript or secrets, are encrypted and signed per device, expire quickly, and are deleted on discard. Never resume an external action automatically; resumption must re-enter the existing approval boundary.
- **missing:** A pendant-local durable continuity record; Signed versioned merge protocol across pendant, Mac, and relay; Reconnect event and acknowledgement semantics; Adapters that summarize browser/job state into a minimal card


## What it asked for

_Nothing._
