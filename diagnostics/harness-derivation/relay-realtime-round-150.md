# Harness derivation — relay-realtime — round 150

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Get me ready for my next meeting."
- **useful because:** A wearable assistant that can pull calendar context, open relevant docs, summarize threads, and prep a short spoken brief is a daily habit-forming feature.
- **path:** relay → mac-bridge → browser
- **model tier:** Planner for context gathering; realtime only to deliver the brief and take quick follow-ups.
- **latency:** Prep can take up to a minute; spoken output should be under 30 seconds by default.
- **cost:** Moderate; mostly context retrieval and summarization. Cached results reduce repeats.
- **security:** Calendar and documents are private. Summaries must stay within the owner’s context and avoid sharing beyond the session.
- **missing:** Cross-surface context assembler with provenance and freshness.; Reliable access to calendar/email/doc sources via Mac agent.; Audio queue support for pendant playback.

### ""Give me a spoken, evidence-backed answer about what is currently on my Mac screen and in my active browser tab, then let me say 'do it' to act on that exact context.""
- **useful because:** The owner can be away from the keyboard yet recover the precise situation they are looking at instead of receiving a generic Mac or web answer. The pendant supplies the voice and intent, Mac vision supplies pixels and application state, and the browser harness supplies authenticated page content; the relay can cite which surface each claim came from before any action.
- **path:** pendant → relay-realtime → mac-vision → mac-planner → browser-extension
- **model tier:** Realtime relay for the short spoken exchange; gpt-4.1-mini vision for a screenshot/UI grounding pass; gpt-5.6-luna only for the follow-up multi-step action; browser extraction locally in the extension where sessions are already authenticated.
- **latency:** Answer in 3-5 seconds for inspection, with a second short turn for execution. The owner tolerates a few seconds because this replaces walking back to the desk.
- **cost:** About $0.01-$0.05 per inspection depending on screenshot and page-token size; the expensive part is vision/context serialization, not relay routing.
- **security:** Screen pixels and authenticated page text leave the Mac only to the relay/model path and may contain secrets. Minimize to the active window/tab, redact password fields, retain the evidence bundle briefly, and make 'do it' explicitly target the displayed bundle rather than silently re-inspecting a changed page.
- **missing:** A relay endpoint that atomically snapshots active Mac window plus active authenticated browser tab and returns a cited evidence bundle; mac-vision support for a stable snapshot id and compact UI facts; A two-turn confirmation/context binding in the voice session

### ""I’m leaving my desk—snapshot the work context. When I come back and press the pendant, tell me only what changed in my editor, terminal, and authenticated browser tabs, and take me back to the exact place I left.""
- **useful because:** This turns the wearable into a genuine continuity surface across physical absence: the owner does not need to remember which window, tab, or command mattered. It is event-driven rather than a scheduled briefing, and it works across the Mac and browser session boundaries that no single node can see.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension
- **model tier:** Cheap background summarization of the two bounded snapshots; realtime relay only handles the return question and spoken delta. Use Mac planner/vision to restore exact app/tab/scroll anchors, not a language-model guess.
- **latency:** Snapshot under 2 seconds on departure; return delta under 5 seconds, with restoration immediately after the owner says 'take me there'.
- **cost:** Roughly $0.005-$0.03 per departure/return pair; storage and screenshot transfer dominate, so retain compact hashes, anchors, and diffs rather than full histories.
- **security:** Snapshots can contain private work and authenticated pages. Encrypt per owner, scope capture to foreground app and selected browser tabs, expire snapshots after a short retention window, and never expose the snapshot to another session.
- **missing:** A physical pendant departure/return event protocol and relay event ingestion; A durable per-session context snapshot store with semantic and pixel diffs; Mac APIs for active-app/editor/terminal anchors and browser APIs for tab URL, title, scroll, and restoration; A delta summarizer that can distinguish owner changes from background page churn

### ""I found a bug—use my voice to investigate it across the project, reproduce it, make the smallest fix, run the relevant tests, and tell me what changed and whether the test actually passed.""
- **useful because:** This is a real end-to-end capability rather than a chat answer: the pendant captures the problem while the owner is away, the Mac terminal and planner inspect and modify the repository, browser sessions can reproduce web-only behavior, and the relay gives a concise spoken result grounded in test output. It removes the current gap where delegation can act but cannot reliably explain verified completion.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension
- **model tier:** Realtime relay for intake and final narration; gpt-5.6-luna for planning and code changes; a deterministic local test runner for verification; browser automation only when reproduction requires an authenticated page.
- **latency:** Acknowledge within 2 seconds, then run asynchronously. Typical completion may take 1-10 minutes; the owner should be able to ask for a spoken checkpoint without restarting the work.
- **cost:** Approximately $0.05-$0.40 per issue, dominated by planner context and any vision/browser reproduction; tests themselves have no model cost.
- **security:** Repository contents, logs, and potentially authenticated web data are sensitive. Keep execution on the Mac, send only targeted excerpts, record exact commands and diffs, and never claim success unless an actual exit code and test artifact are attached. Code edits are owner-authorized under current policy but must remain undoable.
- **missing:** A durable issue job that carries transcript, repository snapshot, reproduction evidence, patch, and test receipts as one correlation id; Mac-terminal execution with streamed stdout/stderr and test-artifact capture exposed to the relay; A browser-to-terminal reproduction handoff for authenticated failures; A spoken checkpoint/status channel that does not require polling or a new voice run


## Changes it proposed to its own stack

### `integration` — Add a cross-surface sensitive-content guardian: before any Mac screenshot, browser extraction, or spoken readback is sent through the relay, mac-vision and the browser extension classify visible regions as password/OTP/payment/health/private-message content. Replace those regions with typed placeholders and attach a sensitivity manifest to the evidence/job receipt; the owner can say 'include the hidden field' to request an explicit one-shot reveal bound to the current session.
- **owner gets:** The owner can safely use the pendant around real work and authenticated sites without choosing between useful remote help and accidentally broadcasting a password or private message. It preserves task control while making the dangerous parts obvious in the spoken response.
- effort: Medium-high: shared redaction schema across Mac screenshots, browser DOM extraction, audio narration, and receipt storage; adversarial tests for OCR and DOM leaks.  ·  risk: False negatives could leak sensitive text; false positives could make a task frustrating. Recover with visible/ spoken placeholders, a per-session audit trail, and explicit one-shot reveal rather than silently disabling the whole workflow.
- cost: Small per-request classifier/token cost; roughly $0.005-$0.02 for OCR/DOM sensitivity checks, with no new hardware cost.  ·  latency: Adds about 100-400 ms for DOM checks and lightweight OCR; full-screen vision may add 1-2 seconds only when a screenshot is requested.
- security: Strongly improves data minimization, but the classifier itself sees the raw content locally. Keep classification on the Mac/extension, transmit only redacted artifacts and sensitivity labels, and expire reveal artifacts immediately.
- depends on: mac-vision screenshot and region metadata; browser extension DOM extraction with field labels; relay evidence bundles and job receipts; a session-scoped spoken one-shot reveal command

### `hardware` — Add a low-power coin vibration motor and a single capacitive touch strip to the nRF9160 pendant enclosure, driven by a tiny local event queue. Use distinct short patterns for listening, Mac job accepted, job finished, and sensitive-content redaction; use touch-and-hold as a local cancel/mute gesture while the Mac or relay is acting.
- **owner gets:** The owner gets private, glance-free confirmation and an immediate escape hatch in a noisy room or meeting, without waiting for speech or looking at an LED. This makes long-running cross-device work usable while walking away from the Mac.
- effort: Moderate enclosure/PCB revision and firmware event protocol; validate motor current against the existing battery and USB tethered test setup before enabling LTE use.  ·  risk: Motor noise can contaminate the microphone and added draw can reduce battery life. Isolate it mechanically, suppress microphone capture during vibration, cap duty cycle, and fall back to the existing LED/button when power is low.
- cost: Approximately $2-$8 in components plus enclosure/PCB work; roughly 10-30 mA only during a vibration pulse, negligible average draw with a duty-cycle cap.  ·  latency: Local acknowledgement under 50 ms; no relay round trip for cancel/mute.
- security: Improves privacy by providing local mute/cancel feedback; touch events must be debounced and authenticated to the paired session so an accidental touch cannot trigger an unintended workflow.
- depends on: Pendant firmware local event queue; relay/mac job lifecycle events; USB serial hardware test harness; audio bridge microphone mute control


## What it asked for

_Nothing._
