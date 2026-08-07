# Harness derivation — relay-realtime — round 153

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If I say something that sounds like a task, choose the fastest surface to handle it and tell me who’s doing it."
- **useful because:** This makes the system feel like one assistant instead of a pile of tools. It reduces latency and prevents accidental Mac wake-ups for simple questions.
- **path:** relay → mac-bridge → browser → pendant
- **model tier:** Realtime for intent capture; cheaper planner for routing and execution when the user isn’t waiting.
- **latency:** Under 300ms to acknowledge and route; execution can take longer.
- **cost:** Low per invocation; main cost is misrouting — reruns are expensive.
- **security:** Intent metadata leaves the device; avoid sending full transcripts when not needed. Never fabricate execution status.
- **missing:** relay_route_intent implementation; typed intent taxonomy shared by relay and mac-planner; relay-side status events for routed jobs

### "Check that my audio path is healthy end-to-end and fix what you can automatically."
- **useful because:** The owner wears this daily; silent failures are brutal. A self-test catches codec, framing, and bridge issues before they ruin a conversation.
- **path:** pendant → bridge → relay → mac-bridge
- **model tier:** Realtime only for user-facing updates; self-test logic on-device and on Mac.
- **latency:** A quick test under 5 seconds with clear pass/fail.
- **cost:** Moderate; test packets and diagnostics dominate.
- **security:** Audio loopback may capture ambient speech; run only on explicit request and discard samples.
- **missing:** device skill for loopback capture/playback markers; bridge diagnostic command set; relay diagnostic endpoint for reporting and thresholds

### "Remember what we decided in this conversation, but keep it tiny and reusable later."
- **useful because:** Cuts repeated context cost and makes the assistant consistent without re-sending huge history every turn.
- **path:** relay → memory → mac-bridge
- **model tier:** Realtime summarizes; cheap model stores and retrieves.
- **latency:** Under 500ms to store a short summary; retrieval should be instant.
- **cost:** Low; cost dominated by embedding/summarization if used.
- **security:** Summaries can leak sensitive info; tag sensitivity and expiry, and keep private data on-device when possible.
- **missing:** typed memory schema for conversation decisions; relay memory write/read route; per-surface token budget enforcement

### "“Mark this moment.” Later, when I ask “what was I doing when I marked it?”, show me the exact Mac window/document, relevant browser tabs, and the surrounding words from my pendant—each with a timestamp and source."
- **useful because:** A worn button or voice marker would turn fleeting thoughts into reliable, searchable anchors. No single node can do this: the pendant supplies the moment and audio, the Mac supplies screen state, the browser supplies authenticated context, and the relay binds them while they are still fresh.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime only for the marker acknowledgment and later spoken query parsing; a cheaper background model aligns transcripts, screen metadata, and browser evidence.
- **latency:** Acknowledge the marker in under 500 ms; snapshot all online surfaces within 2 seconds; later retrieval under 3 seconds.
- **cost:** About $0.01–$0.04 per marker/retrieval, dominated by transcription and background evidence alignment; storage is small metadata plus optional short audio.
- **security:** Screen and authenticated-tab contents can be sensitive. Encrypt the event, apply a short default audio TTL, retain only cited snippets/metadata after alignment, and require an explicit spoken request to reveal private content.
- **missing:** A marker event endpoint joining pendant audio/button timestamps to a Mac snapshot; A Mac snapshot action for active window/document and browser tab metadata; An evidence-linked event index and retrieval query; A user-visible retention/deletion control

### "“I’m switching contexts.” Capture where I stopped, what remains unsent or unfinished, and a one-sentence next action. When I return and say “resume,” give me the shortest safe path back without reopening or submitting anything automatically."
- **useful because:** People lose work when they walk away from the Mac wearing the pendant. This creates a real wearable-to-machine handoff: the pendant declares the transition, the relay freezes a point-in-time record, Mac and browser expose unfinished state, and the next interaction reconstructs intent instead of guessing.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime handles the two short utterances; a low-cost background model extracts unfinished threads and ranks one next action from captured evidence.
- **latency:** Switch acknowledgment under 700 ms and state capture under 4 seconds; resume answer under 3 seconds.
- **cost:** Roughly $0.01–$0.03 per handoff, mostly transcript/context extraction; no continuous audio processing is needed.
- **security:** A frozen state may contain private drafts or page text. Store encrypted, expire stale handoffs, distinguish draft from submitted state, and never perform a mutation merely because the owner said resume.
- **missing:** A cross-surface context checkpoint schema with draft/submitted provenance; Mac active-work and unsaved-document inspection; Browser tab extraction of unsent form state without submission; Pendant transition markers and a resumable checkpoint store

### "“Give me the decision, not a dump.” For a question I name aloud, inspect the relevant open Mac work and authenticated browser pages, identify the competing options and missing evidence, then speak one recommendation with the strongest citations and a reversible next step."
- **useful because:** The owner currently has tools that can read pages or plan actions, but not a compact, evidence-backed decision assembled from the private browser and local work context. This is the hive’s highest-value synthesis: wearable intent, relay routing, browser sessions, Mac state, and judgement/action faculties produce an answer the owner can act on while walking.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-vision → faculty-perception → faculty-judgement → faculty-action → dashboard
- **model tier:** Realtime parses the question and gives a brief spoken result; faculty-perception and faculty-judgement run on a cheaper background tier, with faculty-action limited to preparing a reversible next step.
- **latency:** Start speaking a progress acknowledgment within 800 ms; deliver a cited recommendation in 8–20 seconds depending on page count.
- **cost:** Approximately $0.05–$0.20 per decision, dominated by private-page extraction and multi-agent synthesis; cache unchanged evidence within the session.
- **security:** Private tabs and local files leave their surfaces and enter the relay context. Use least-context retrieval, source-level sensitivity labels, encrypted transient buffers, and speak only the conclusion unless the owner asks for citations.
- **missing:** A decision-task router that selects relevant Mac and browser evidence; A typed evidence bundle with citations, freshness, and uncertainty; A faculty judgement response schema separating recommendation from action; A spoken progressive-status channel for multi-second synthesis

### "“Why is this failing right now?” While I am away from the keyboard, collect the current local test/build error, the relevant source diff, and authoritative documentation or issue threads from my authenticated browser; explain the likely cause aloud and prepare (but do not apply) the smallest patch with a replayable test."
- **useful because:** This is a genuinely wearable-first debugging loop: the pendant starts it and speaks the answer, mac-terminal supplies live failure evidence, mac-vision identifies the active project, browser-extension supplies private issue context and docs, and the relay keeps the investigation coherent. A Mac-only assistant cannot keep the owner informed while they are walking away or reconcile private browser context with local logs.
- **path:** pendant → relay-realtime → mac-terminal → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Realtime parses the spoken question and acknowledges immediately; a cheaper background planner gathers logs/docs and drafts the patch, while realtime returns only the concise diagnosis and asks no unnecessary follow-up.
- **latency:** Acknowledge under 600 ms; first useful diagnosis in 5 seconds; complete evidence-backed patch proposal in 20–45 seconds.
- **cost:** About $0.04–$0.15 per investigation, dominated by log summarization and authenticated documentation retrieval; unchanged project context should be cached.
- **security:** Source code, private issue pages, and logs may contain secrets. Redact credentials before relay transit, keep raw logs on the Mac where possible, cite exact local/browser sources, and require explicit confirmation before any patch or command executes.
- **missing:** A cross-surface debugging job that correlates local failures, source diffs, and browser evidence; A mac-terminal typed read-only diagnostics result with file/line citations; A patch proposal artifact containing diff, test command, and confidence; A progressive spoken status stream for investigations


## Changes it proposed to its own stack

### `interaction` — Add an end-to-end audio diagnostic handshake: pendant emits a known marker; bridge loops it; relay verifies timing, packet loss, and codec compatibility; Mac reports device driver state if connected.
- **owner gets:** Prevents confusing failures where the assistant seems unresponsive but the audio chain is broken.
- effort: Medium to high; requires firmware skill, bridge command, relay verification logic, and optional Mac reporting.  ·  risk: Diagnostics could capture ambient audio. Mitigation: use synthetic markers and discard captured audio immediately.
- cost: Moderate in bandwidth and compute during diagnostics; negligible when idle.  ·  latency: Adds a few seconds only when invoked.
- security: Keeps diagnostic data minimal and ephemeral; never store raw audio.

### `memory` — Introduce a compact conversation-decision memory: store short, schema-validated summaries with TTL, sensitivity tags, and source provenance; retrieval returns only task-relevant facts.
- **owner gets:** The assistant becomes consistent and efficient, without paying to resend large context every turn.
- effort: Medium; requires schema, storage routes, and retrieval integration with planners.  ·  risk: Stale or incorrect summaries could mislead. Mitigation: TTLs, confidence scores, and explicit overwrite rules.
- cost: Low; dominated by summarization/embedding if used.  ·  latency: Small write/read overhead; reduces future turn latency by shrinking context.
- security: Sensitive summaries remain scoped; avoid shipping private content to cheaper tiers unless necessary.

### `interaction` — Add a pendant-local privacy posture switch: a long press on the existing button toggles QUIET/PRIVATE mode, with the LED confirming the state. The relay must attach the posture to every voice run; in PRIVATE mode it may still perform Mac/browser work but returns only a generic spoken acknowledgment and places sensitive findings in a local-Mac review card. A second long press exits the mode.
- **owner gets:** The owner can walk into a meeting or public place and immediately prevent private calendar, browser, or source details from being spoken, without finding a phone or relying on a server guess about who is listening.
- effort: Firmware button state and LED feedback; relay session/posture propagation; Mac dashboard card and deferred result retrieval; browser/Mac agents need a `speak_policy` field.  ·  risk: A missed or ambiguous press could leave the owner in the wrong posture. Use a distinct 1.5-second hold, LED pattern, and spoken generic confirmation only; recover by holding again. If the link drops, firmware keeps the last posture locally.
- cost: Negligible API cost; small firmware change and a few bytes of session state.  ·  latency: No meaningful added latency; posture is local and attached before transcription routing.
- security: Improves confidentiality, but must be fail-closed for sensitive spoken output when posture is unknown or link state changes. Do not put raw private results in relay logs.
- depends on: A relay session field carrying privacy posture through /pipeline/audio, /pipeline/events, and downstream jobs; A Mac review-card/result endpoint for answers suppressed from speech; Firmware button gesture and LED state implementation


## What it asked for

_Nothing._
## Its own summary

Recorded four owner-facing capabilities and one interaction change. The strongest new direction is a wearable-to-private-context decision loop: the pendant starts a question, the relay coordinates Mac and authenticated browser evidence, judgement produces a cited recommendation, and action prepares only a reversible next step. Also recorded context checkpoints, a debugging investigation loop, and a pendant-local PRIVATE posture that suppresses sensitive speech while still allowing work to continue. Still needed: durable cross-surface evidence/checkpoint schemas, progressive spoken status, typed read-only Mac diagnostics, browser/Mac provenance, and firmware posture persistence. The marker idea was accepted but flagged as close to an existing backlog item, so it should not be treated as novel going forward.

**Biggest unknown:** Which exact live Mac routes implement /mac/plan and typed diagnostics; the recorder indicated those route names were not fully inventoried, so implementation planning must verify them before wiring the recorded capabilities.

