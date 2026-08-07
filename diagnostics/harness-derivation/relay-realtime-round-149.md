# Harness derivation — relay-realtime — round 149

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Keep an ear on what I’m doing and step in when I’m stuck, then hand off to my Mac or browser if needed."
- **useful because:** This becomes a real daily co-pilot: the pendant hears confusion, repeated failed attempts, or a request for help, and routes to the right surface without the owner having to explain the whole situation.
- **path:** pendant → relay → mac-bridge → browser
- **model tier:** Realtime for detection and prompting; cheaper Mac planner for execution; browser only if a web session is required.
- **latency:** Under a second for the nudge; seconds to minutes for Mac/browser follow-up.
- **cost:** Low per minute for detection; execution cost dominated by Mac planning and any browser actions.
- **security:** Audio stays on-device/relay for detection; only task summaries and necessary context are sent. Avoid sending raw audio unless the owner explicitly says so.
- **missing:** Implemented relay_route_intent for explicit routing and status callbacks; A lightweight event stream from pendant/bridge to relay for interaction signals; Policy for what counts as 'stuck' and a safe fallback when detection is wrong

### "If I say 'summarize what just happened', give me a concise recap and what’s next."
- **useful because:** Owners can finish a voice interaction and get a clear, spoken summary and a suggested next step—great for walking, commuting, or multitasking.
- **path:** relay → mac-bridge
- **model tier:** Realtime to assemble the spoken recap; Mac for pulling receipts and context when available.
- **latency:** 1-2 seconds for a recap, longer if receipts need fetching.
- **cost:** Cheap if using existing job receipts; cost rises with extra context retrieval.
- **security:** Summaries should avoid sensitive content unless it was part of the task; receipts can be referenced without exposing raw data.
- **missing:** A durable, cross-surface 'interaction log' that the relay can query without resending context; Standardized receipt formats across Mac actions and browser actions

### "When I say “meeting mode,” have the pendant listen for the next conversation, continuously extract only decisions, commitments, and names/deadlines, then send me a short spoken recap and create dated follow-up items in the right Mac app, with links to the relevant authenticated browser page when one is mentioned."
- **useful because:** The owner can leave the Mac behind and still turn a real-world conversation into actionable, attributable work instead of manually reconstructing it later. The pendant supplies proximity audio, the relay supplies low-latency capture and recap, the Mac supplies durable artifacts, and the browser supplies session-aware source links.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime relay for start/stop cues and a compact rolling transcript; background cheaper model for diarization, decision extraction, and deadline normalization; Mac planner only for final artifact creation.
- **latency:** Start acknowledgement under 500 ms; spoken interim cue within 3 s after a detected commitment; final recap within 30 s of stopping. Processing can be batched every 10–20 seconds.
- **cost:** Roughly $0.02–$0.15 per 30-minute meeting depending on audio transcription and extraction; audio upload and transcription dominate.
- **security:** Conversation audio and extracted names may leave the pendant and be retained. Require an explicit button/voice start and stop, a visible LED while recording, automatic deletion of raw audio after extraction, and a local-only mode when no uplink exists. Browser links must be citations, not copied page contents unless requested.
- **missing:** A pendant recording session primitive with explicit LED state and bounded raw-audio retention; Streaming audio segmentation/transcription and speaker/decision extraction worker; A cross-surface artifact API that can create dated follow-ups and attach browser citations; A reliable way to associate spoken page names with the owner’s currently authenticated browser tabs

### "Let me say “make this a brief” while wearing the pendant: have the relay collect the current authenticated browser tabs and the relevant Mac project files, reconcile contradictions, and deliver a cited one-page brief as a file in the project folder plus a spoken three-sentence summary."
- **useful because:** Today browser research, local files, and the wearable conversation are separate worlds. This would produce a useful artifact that combines sources the owner can reach only through different physical nodes, rather than merely answering from one surface.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-terminal → dashboard
- **model tier:** Cheap background synthesis model for retrieval, source normalization, and drafting; realtime tier only handles the spoken command and completion summary; planner/terminal perform bounded file creation.
- **latency:** Acknowledge immediately; deliver within 60–120 s for up to eight tabs and one project directory. If source collection exceeds that, provide a partial cited brief rather than blocking the conversation.
- **cost:** Approximately $0.05–$0.30 per brief; context ingestion and synthesis dominate, with browser extraction and file scanning kept bounded.
- **security:** Authenticated tab contents and local project files are sensitive. Never broaden beyond explicitly selected tabs/project; preserve source URLs and local paths in the artifact; redact credentials and tokens; keep an audit record and make the generated file reversible.
- **missing:** A single request-scoped source selector spanning browser sessions and Mac paths; A bounded local-project indexing/read route exposed to the relay; A citation-preserving synthesis worker that can reconcile conflicting sources; An artifact delivery route with atomic write and receipt semantics

### "When I approach my Mac wearing the pendant, let me tap its button and say “handoff,” then move the active voice task, transcript context, and browser tab focus from the remote relay onto the Mac; when I leave, the pendant remains the conversational control and the Mac locks the handoff context."
- **useful because:** The owner should not have to restart or repeat a task when moving between walking and desk work. The physical pendant provides an unambiguous proximity gesture, the relay preserves continuity, the Mac takes over rich execution, and the browser extension transfers the authenticated tab context.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime relay handles the tiny handoff dialogue; no expensive synthesis is needed. Mac and browser agents resume the existing task state rather than re-planning it.
- **latency:** Button acknowledgement under 200 ms; handoff complete within 3 s over USB and under 8 s over LTE/Wi-Fi. Context transfer must be resumable if the link drops.
- **cost:** Under $0.01 per handoff; dominated by a small context transfer, not inference.
- **security:** The handoff token is effectively a physical bearer credential. Bind it to a rotating device key, require a fresh button press, expire tokens quickly, and never transfer raw browser secrets or full audio history. Lock or revoke the Mac-side session when the pendant disconnects.
- **missing:** Firmware device-key identity and button gesture for handoff; A relay session-transfer endpoint with resumable, minimal context snapshots; Mac USB/serial presence detection and a handoff/resume consumer; Browser extension support for exporting/importing tab focus without exposing cookies


## Changes it proposed to its own stack

### `relay` — Add a self-describing /capabilities endpoint for the relay surface, including granted tools, available routes, and current wiring status (implemented vs schema-only).
- **owner gets:** Faster diagnosis when something fails. The assistant can tell the owner what’s actually possible right now instead of guessing or wasting turns.
- effort: Medium: add route, hook into build metadata, expose wiring flags.  ·  risk: Low. Risk is leaking internal details; mitigate by returning only capability names and statuses, not secrets.
- cost: Low per call; small maintenance cost.  ·  latency: Negligible.
- security: Ensure output is sanitized and excludes tokens, session identifiers, and private config.

### `integration` — Implement relay_route_intent as the explicit routing path from realtime to mac-planner/mac-vision, with status callbacks and a durable intent id.
- **owner gets:** Natural voice commands reliably land on the right agent, and the owner can ask what happened without re-explaining.
- effort: High: needs backend wiring, intent id propagation, and job record linkage.  ·  risk: Medium. Misrouting would be confusing; include clear fallback to mac_delegate when ambiguous.
- cost: Low per intent; main cost is development and testing.  ·  latency: Small overhead; reduces costly retries.
- security: Log intent metadata only; avoid storing raw utterances unless needed for debugging and explicitly allowed.

### `browser-harness` — Implement server_browser_actions using an isolated, ephemeral browser session with strict allowlists and artifact capture (DOM snapshot, extracted text, evidence links).
- **owner gets:** Lets tasks continue even when the Mac is offline, and gives verifiable results the owner can trust.
- effort: High: needs Browser Run integration, session isolation, and evidence capture.  ·  risk: High. Browser automation can leak credentials or take unintended actions; enforce allowlists and read-only modes by default.
- cost: Moderate per run; dominated by cloud browser time.  ·  latency: Higher than local actions; acceptable for unattended workflows.
- security: Strong isolation, no credential reuse across tasks, explicit user authorization for write actions.

### `interaction` — Add a physical conversational checkpoint protocol: after the relay hands a multi-surface task to Mac or browser, it emits a compact spoken 'contract' (goal, scope, expected artifact, and expiration), accepts a single spoken correction during a short grace window, and otherwise lets the downstream plan continue. The contract and correction become immutable metadata on the resulting receipt.
- **owner gets:** The owner can correct a misunderstood request while walking away without repeating the entire task, while still knowing exactly what the remote agents were told to do. This is materially safer and more usable than silent handoff or a long clarification dialogue.
- effort: Medium-high: relay session state, audio playback/interruption handling, downstream request metadata, and receipt display all need coordinated changes.  ·  risk: A late correction could race an action already executed. Use monotonic request versions, stop accepting corrections once execution begins, and clearly speak when the window closes; recover by issuing a compensating action or undo where available.
- cost: Negligible model cost; one extra short response per delegated task. Storage is tiny per request.  ·  latency: Adds 1–3 seconds only when the owner chooses to correct; normal delegation remains immediate.
- security: Improves transparency but places task scope in receipts. Encrypt or minimize spoken contract metadata and never include secrets from browser pages.
- depends on: A durable request/job identity shared by relay, Mac planner, and browser command queue; A pendant audio interruption or short-grace playback mechanism; Receipt records that store request version and spoken correction


## What it asked for

_Nothing._
## Its own summary

Recorded four new proposals: (1) explicit meeting mode that turns wearable conversation audio into cited, dated follow-ups across pendant, relay, Mac, and authenticated browser; (2) a spoken “make this a brief” workflow that fuses authenticated tabs with local project files into a cited artifact; (3) a spoken contract/correction checkpoint for remote delegated tasks; and (4) physical pendant-to-Mac session handoff when the owner returns to the desk. The common missing pieces are cross-surface request identity, bounded context transfer, audio/session controls, and browser/local-source correlation—not another generic planner or scheduler.

**Biggest unknown:** Whether any of these cross-surface connective proposals collide with backlog entries whose full descriptions were not available in this round; all four were accepted by the recorder.

