# Harness derivation — mac-terminal — round 132

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Mark this moment.”"
- **useful because:** A physical press or spoken phrase while wearing the pendant captures the owner's current Mac context without requiring them to stop: active app/window, open Safari tab and URL, selected text or clipboard when available, a screenshot or DOM citation, and a short owner note. Later they can ask “what did I mark?” and jump back to the exact work state. This is a genuinely wearable-to-Mac memory primitive rather than another scheduled briefing.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime only for recognizing the mark and immediate acknowledgement; a cheaper background model normalizes the context bundle, deduplicates nearby marks, and writes searchable summaries.
- **latency:** Acknowledge the press in under 500 ms; capture the Mac/browser evidence within 3 seconds; indexing can take up to 30 seconds.
- **cost:** About $0.001–$0.01 per mark depending on whether transcription and summarization are needed; storage and screenshot retention dominate after model cost.
- **security:** The bundle may contain private screen contents, clipboard secrets, and authenticated URLs. Capture must be explicit (button/phrase), visibly indicate recording, redact passwords/token-like clipboard values, encrypt in transit and at rest, and offer one-command deletion. Never transmit the whole screen when a browser citation suffices.
- **missing:** A pendant button/event mapped to a mark intent while USB-tethered; A Mac context snapshot API that returns active window and focused text safely; A browser inspection payload that can be joined to the Mac snapshot with one timestamp; A retention and redaction policy for captured bundles; A query endpoint that retrieves marked moments and reopens the cited app/tab

### "“Fix that failure and tell me what you changed.”"
- **useful because:** When a Mac or browser job fails, the system should make the failure useful instead of merely reporting red. It captures the exact command/step, stderr, app and tab state, identifies whether the failure is transient, missing permission, bad input, or a real-world rejection, tries bounded reversible repairs (for example retrying after refreshing a stale tab or correcting a discovered path), and gives the pendant a short truthful result with a receipt. The owner gets recovery, not a dead end.
- **path:** mac-planner → mac-vision → browser-extension → relay-realtime → dashboard
- **model tier:** Use a cheap background model for log classification and repair-plan generation; use realtime only if the owner is actively conversing about the failure.
- **latency:** Surface the first truthful failure in 1 second, diagnose in under 5 seconds, and perform at most three repair attempts within 60 seconds.
- **cost:** Roughly $0.002–$0.03 per failed job; tokenized stderr and screenshots dominate. Most failures should use a local classifier with no model call.
- **security:** Retries must not silently repeat irreversible browser submissions or destructive shell commands. Preserve full stdout/stderr locally, redact secrets before relay, attach each attempt to an immutable receipt, and require an explicit owner instruction for any retry whose side effect is not known reversible.
- **missing:** A failure-triggered repair orchestrator that can distinguish retryable from side-effecting steps; Typed failure records containing argv, cwd, exit status, stderr, tab/session identity, and prior receipts; A dry-run/replay mechanism for safe repair plans; A pendant status event for failure, retry, and final outcome

### "“Read the useful parts of this download to me.”"
- **useful because:** The owner can point at a private Safari download and receive a concise spoken explanation through the worn device without manually finding, opening, or uploading the file. The browser identifies the download and its authenticated source, the Mac inspects it locally (including PDFs, images, and spreadsheets), the relay produces a cited digest, and the pendant audio bridge plays it with pause/skip controls. This joins browser sessions, local filesystem access, and wearable playback in a way no node can do alone.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Use a cheap document-extraction model or local parsers first; escalate only ambiguous pages or tables to the expensive model. Realtime is only for conversational follow-up while playback is active.
- **latency:** Identify the selected download in 1 second, extract text in 5 seconds for ordinary documents, and start first audio within 10 seconds; large files may process in background.
- **cost:** $0.005–$0.08 per document, dominated by OCR/vision and generated audio; local text PDFs should be near-zero API cost.
- **security:** Files and authenticated source URLs stay on the Mac unless the owner explicitly asks for cloud processing. Sandbox parsers, block macros/active content, redact credentials and personal identifiers in spoken output, and retain only a short-lived digest plus source hash.
- **missing:** Browser download-to-file identity and source metadata bridge; Local Mac document extraction/OCR service with bounded file size and parser isolation; Citation format that maps spoken claims to page/sheet/paragraph offsets; Streaming audio queue from relay to the USB ESP32 bridge with pause and resume events

### "“Stop everything you’re doing.”"
- **useful because:** A long press on the worn pendant (or the spoken phrase) immediately cancels active Mac shell jobs, browser workflows, queued audio, and relay background work, then reports exactly what stopped and what could not be interrupted. It gives the owner a physical, cross-surface escape hatch when the screen is busy, a workflow is looping, or the owner has changed their mind—something the Mac alone cannot provide when focus is elsewhere.
- **path:** pendant → mac-planner → mac-vision → browser-extension → relay-realtime → dashboard
- **model tier:** No expensive model is needed: a deterministic event fan-out cancels jobs; realtime is used only to phrase the final status if the owner asks a follow-up.
- **latency:** Emit the cancel event within 200 ms of the button press, request cancellation across surfaces within 1 second, and speak a truthful partial-completion report within 3 seconds.
- **cost:** Effectively zero model cost; small relay event and job-record overhead.
- **security:** The control is intentionally powerful but should not erase receipts or undo already-completed real-world actions. Require a distinct long press, provide haptic/audio acknowledgement, authenticate the USB serial device, make cancellation idempotent, and report jobs that do not support interruption.
- **missing:** Pendant firmware long-press event and USB serial command channel; Authenticated cancel fan-out from relay to Mac and browser sessions; Cooperative cancellation and process-group termination in the Mac executor; Browser step cancellation that leaves tabs in a known state; A dashboard showing cancelled, completed, and uninterruptible work separately

### "“What did I decide about this, and what evidence led me there?”"
- **useful because:** The owner should have an evidence-backed decision ledger: when they make a decision in conversation, Safari, or a Mac document, the system links the decision to the exact supporting page, file revision, message, and timestamp, then later answers with the conclusion, alternatives considered, and what would invalidate it. This is not a generic memory or briefing: it preserves why a decision was made across the wearable, authenticated browser, and Mac work context, so the owner can trust or revise it months later.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheap background model to extract candidate decisions and evidence links; use the realtime tier only for an on-demand spoken explanation or ambiguity resolution.
- **latency:** Capture a candidate decision within 10 seconds of an explicit owner statement or saved document change; answer a lookup in under 5 seconds, with deeper evidence reconciliation in the background.
- **cost:** Approximately $0.005–$0.05 per decision cluster; embedding/index storage and document diffing dominate, while explicit spoken decisions need little inference.
- **security:** The ledger may join highly sensitive browser pages, files, and voice transcripts. Keep raw evidence local where possible, store cryptographic hashes and least-content citations in the relay, separate personal/work scopes, redact secrets, and make deletion of a decision remove all linked evidence and derived summaries.
- **missing:** A cross-surface decision event schema with owner-authored versus inferred confidence; Mac file/document revision and active-window provenance capture; Browser DOM citation and authenticated-tab evidence snapshots that survive navigation; A durable evidence graph with contradiction and supersession handling; A pendant query/response mode that can cite sources without reading private content aloud in public

### "“Make this private now.”"
- **useful because:** A deliberate pendant gesture immediately enters a cross-surface privacy state: the Mac hides or locks sensitive windows, Safari pauses page extraction and clears transient captured text, the relay stops speaking private content, and the pendant gives a local confirmation. A second deliberate gesture restores the prior task. Today privacy controls are fragmented and require screen access; this gives the wearer a fast physical boundary in a shared room.
- **path:** pendant → mac-planner → mac-vision → browser-extension → relay-realtime → dashboard
- **model tier:** Deterministic policy and event fan-out; no model call is needed. Realtime only handles a conversational request to inspect or change the privacy state.
- **latency:** Local haptic/LED acknowledgement under 200 ms, Mac display/browser response under 1 second, and relay audio cutoff under 300 ms.
- **cost:** Near-zero API cost; modest engineering and encrypted state storage.
- **security:** The privacy gesture must be authenticated and require a long press to prevent accidental activation. It must fail closed on uncertain link state, never claim a window was hidden if the Mac did not confirm it, and keep an emergency local physical override. Do not rely on a model to decide what is sensitive during the emergency action.
- **missing:** A signed pendant privacy-state event and local indicator; Mac APIs to enumerate and hide/lock configured sensitive apps and stop active capture; Browser-session pause/resume semantics that preserve tabs without extracting content; Relay audio cancellation with confirmed state transitions; An owner-configurable privacy policy and recovery behavior after USB/LTE disconnect

### "“Tell me when my sources disagree about something important.”"
- **useful because:** The owner should get a concise alert when independently authenticated sources conflict—for example, a calendar invitation differs from a travel reservation, an order page disagrees with a shipping email, or a Mac document conflicts with a newer browser record. The system cites both claims, explains which is fresher or more authoritative, and asks only for the missing resolution. This prevents confident action on stale or contradictory information rather than merely reporting page changes.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Cheap background extraction and entity matching handle routine comparisons; use the expensive tier only for ambiguous conflicts or when the owner asks for a recommendation.
- **latency:** Detect a conflict during the next source observation, generally under 1 minute for active tabs and under 15 minutes for scheduled sources; deliver a spoken alert in under 3 seconds once confirmed.
- **cost:** $0.003–$0.03 per comparison batch; authenticated page extraction and OCR dominate, not the final classification.
- **security:** Cross-source joins can reveal sensitive relationships. Keep source content local, send only normalized claims and hashes to the relay, apply per-account scope rules, suppress low-confidence noise, and never alter either source while resolving a conflict.
- **missing:** A normalized entity/claim schema with source authority, freshness, and confidence; A cross-source matcher for browser pages, Mac files, and local communications; Conflict severity and quiet-hours policy that distinguishes actionable contradictions from harmless formatting differences; A cited alert format and owner resolution workflow that records which source won; Durable authenticated source observation beyond currently open tabs


## Changes it proposed to its own stack

### `hardware` — Replace the prototype nRF9160 pendant's single-button/single-LED interaction with a two-control safety interface: retain the primary action button, add a recessed red long-press cancel button and a small haptic motor, with firmware generating a debounced, signed CANCEL_ALL event over USB serial and LTE when available. The Mac relay should treat that event as a deterministic interrupt, not an LLM intent.
- **owner gets:** The owner can stop a runaway or unwanted action instantly without finding the Mac, waking a screen, or speaking over an active audio response. Haptic confirmation makes the result trustworthy in a noisy room.
- effort: Moderate hardware revision and low-to-moderate Zephyr firmware work; add input debounce, event framing, haptic patterns, and host-side fan-out tests.  ·  risk: A false press could cancel useful work; make the control recessed and require 800 ms hold plus haptic countdown. If the link is down, the pendant can still locally silence playback and queue the cancel event for delivery. Recovery is simply restarting a cancelled job from its receipt.
- cost: Approximately $2–$8 in switches, motor, driver, enclosure changes, and PCB revision; under 10 mA while haptic feedback runs, negligible standby impact. No per-invocation API cost.  ·  latency: Local acknowledgement under 100 ms; USB event delivery under 200 ms; LTE delivery depends on registration and network.
- security: Authenticate and sequence cancel frames so an injected USB serial byte cannot trigger control; do not include secrets in the frame. The event should cancel but never delete receipts or data.
- depends on: Pendant USB serial framing and heartbeat; Mac/browser cooperative cancellation with process-group handling; A durable, truthful event receipt for local and remote cancellation


## What it asked for

_Nothing._
## Its own summary

Round 132 produced four non-duplicate owner-facing proposals: (1) failure recovery that diagnoses failed Mac/browser jobs, attempts bounded safe repairs, and returns truthful receipts; (2) “read the useful parts of this download to me,” joining authenticated Safari downloads, local Mac extraction, cited summaries, and pendant/ESP32 playback; (3) a physical/spoken cross-surface “stop everything” interrupt; and (4) a hardware change adding a recessed cancel control plus haptic acknowledgement to the nRF9160 pendant. The first three were recorded as new connective capabilities, and the hardware change was recorded. Live discovery confirms Safari (3 tabs) and the home Mac bridge are online; the cloudflare-contract-test mobile device is offline. I also tested the newly granted mac_read_diagnostics schema, but it still has no implementation.

**Biggest unknown:** Whether the current nRF9160 prototype exposes a spare GPIO/usable enclosure location and whether the Mac executor/browser bridge can cooperatively cancel subprocesses and in-flight tab actions without leaving partial side effects. I still need an implemented read-only Mac diagnostics route, a real pendant USB event/heartbeat protocol, and cancellation semantics with per-step interruptibility; no further permission or approval gate is needed.

