# Harness derivation — faculty-perception — round 125

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **device registry** — Live device discovery currently shows only Safari on MacIntel (online), home-macbook-bridge (online), and cloudflare-contract-test mobile (offline); no nRF9160 pendant or ESP32 bridge is registered.
  - evidence: discover(devices) at 2026-08-07T18:17:xx returned exactly three devices; /ops/status relay payload reports macBridgeOnline=true.
- **Mac UI reachability** — AI Pendant Agent is running, but Accessibility and Screen Recording are not trusted for its actual binary; synthesized UI events are not accepted and UI actions cannot be trusted.
  - evidence: GET /observe: accessibility.trusted=false, screenRecording=false, eventsPost=false, inputReachability.status=failed, uiActionsWillReachTheScreen=false.
- **browser bridge** — Safari browser extension is online with 3 tabs and zero pending commands; its current reported active tab is example.com titled 'Failed to open page'.
  - evidence: GET /browser/status and /ops/status at 2026-08-07T18:17:44Z.
- **relay audio history** — The pipeline contains historical nRF9160-originated and relay-uploaded audio records, including 24 kHz mono PCM rendering, but these records do not establish a currently connected pendant.
  - evidence: GET /pipeline returned completed historical runs with source nrf9160/cloud-relay and timestamps earlier on 2026-08-07; live device discovery has no pendant.

## Capabilities it proposed

### "When I ask you to act on my screen, first prove that the action channel is live; if Accessibility or Screen Recording is missing, explain exactly why and offer an AppleScript or browser-only alternative instead of pretending it worked."
- **useful because:** Stops silent no-op GUI actions—the most dangerous current failure mode—and still lets useful automation proceed through granted AppleScript or the live browser extension.
- **path:** pendant → mac-bridge → browser → dashboard
- **model tier:** realtime for immediate spoken refusal/alternative; background for capability classification
- **latency:** Under 1 second before any action is attempted
- **cost:** Near-zero; status reads and deterministic policy, with optional short realtime response
- **security:** Never claim success from a UI receipt when /observe says events are rejected. Alternatives must preserve approval semantics for external side effects.
- **missing:** Pre-action perception gate wired to action executor; Explicit mapping of task types to safe AppleScript/browser alternatives

### "If my pendant is disconnected, keep my request alive on the Mac and relay, then tell me when it was actually delivered to the wearable—not merely rendered or uploaded—and replay any missed response once the device reconnects."
- **useful because:** Makes the hive dependable despite today’s missing pendant: work can continue, but the owner is never misled into thinking a spoken response reached their body.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** background durable worker; realtime only when the owner asks for status or when delivery resumes
- **latency:** Persist within 1 second; resume/replay within 5 seconds of registration
- **cost:** <$0.02 per request; storage and polling dominate, not model inference
- **security:** Audio and request text need encrypted, bounded retention; replay requires device identity and deduplication so private speech is not sent to the wrong device. Require confirmation before replaying sensitive content aloud.
- **missing:** Live pendant registration and delivery acknowledgments; Durable job runner with a delivery state machine distinct from render/upload; Reconnect-triggered replay endpoint

### "Tell me whenever the system's records contradict one another—for example, a pipeline event says a pendant received audio while the live registry says no pendant exists—and show me the two source records instead of choosing one silently."
- **useful because:** The owner can distinguish a real device failure from stale telemetry or a simulated history, preventing false confidence in the most important perception layer.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** background deterministic consistency checker; realtime only to announce a detected contradiction
- **latency:** Detect within 10 seconds of a new event; speak in under 2 seconds when requested
- **cost:** <$0.005 per check; deterministic comparisons and storage dominate
- **security:** Expose only metadata and redacted snippets by default; contradictory private content stays local. Never delete either source record.
- **missing:** Cross-source invariant definitions (device registration vs pipeline delivery, browser online vs tab command receipt); An append-only contradiction log and owner-facing alert route

### "While I am in a meeting, let me ask “who is this, and what are we discussing?” and receive a private, confidence-labeled answer that fuses the pendant’s recent audio, my calendar invite, and the relevant authenticated browser or document tab—without saving the meeting by default."
- **useful because:** The owner gets instant situational awareness in a conversation without juggling apps or announcing that they need help; no single node can identify the live social context reliably.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** realtime for a short spoken answer; background model for calendar/document disambiguation and entity resolution
- **latency:** 3 seconds for identity/context answer; 10 seconds if a document search is needed
- **cost:** $0.01–$0.08 per query, dominated by realtime audio transcription and entity resolution
- **security:** Meeting audio and authenticated documents are highly sensitive. Keep a short rolling buffer, redact unrelated speakers, require explicit opt-in per meeting, and never persist audio or expose identity guesses without confidence and source labels.
- **missing:** Pendant microphone stream and local voice-activity segmentation; Relay-side ephemeral cross-modal context joiner; Mac calendar/document tab resolver with citation spans; A user-visible per-meeting recording/retention control

### "When I return to my desk, ask “what changed while I was gone?” and get a timeline that combines only meaningful changes in my Mac apps, authenticated browser tabs, pending jobs, and pendant alerts, with one source citation for every item."
- **useful because:** The owner can recover from interruptions in seconds instead of checking every app and wondering whether an old notification was already handled; this is a joint reconstruction none of the surfaces can make alone.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background/event-driven summarizer; realtime only to speak the final compact timeline
- **latency:** Incremental updates within 30 seconds; answer in under 3 seconds
- **cost:** $0.01–$0.05 per daily reconstruction; event indexing dominates, with cheap summarization
- **security:** Activity history is sensitive. Store event hashes and minimal excerpts, apply app/site allowlists, honor private-window and focus-mode exclusions, and require confirmation before mentioning sensitive apps aloud.
- **missing:** Cross-surface event correlation keyed by monotonic timestamps; Meaningful-change detectors for Mac app state and browser regions; Pendant alert acknowledgement receipts tied to the same timeline; A local encrypted event index with configurable retention

### "If I say “make sure that happened,” verify the complete chain from my spoken request to the final observable result: understand me on the pendant, inspect the right browser or Mac state, perform the approved step, and report evidence—or tell me exactly where the chain broke."
- **useful because:** Today a request can be transcribed, planned, rendered, queued, or acknowledged without the owner knowing whether the real-world result occurred. End-to-end verification makes the hive trustworthy rather than merely busy.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background verifier with deterministic checks; realtime for immediate status narration
- **latency:** 5 seconds after reversible actions; asynchronous completion for long jobs
- **cost:** $0.01–$0.10 per verification, depending on browser/document inspection and audio handling
- **security:** Evidence may contain private page content or screenshots. Keep evidence scoped to the requested object, hash/store minimal proofs, gate irreversible actions separately, and never treat a receipt as proof without an independent observation.
- **missing:** Typed end-to-end correlation IDs spanning audio, relay, planner, action, and observation; Independent postcondition observers for browser and Mac state; Pendant playback/acknowledgement telemetry; A verifier policy that distinguishes acceptance, execution, and observed outcome


## Changes it proposed to its own stack

### `context` — Add a freshness and epistemic-status envelope to every perception fact: observed_live, observed_stale, historical_event, inferred, or unavailable, with observedAt, source route, and expiry. Reject prompt projections that turn historical pipeline entries into present device claims.
- **owner gets:** The assistant will stop saying a disconnected pendant heard something merely because an old relay record exists; answers become visibly honest about what is known now.
- effort: Medium: typed schema, projection changes, and tests for contradictory device/pipeline states.  ·  risk: Older consumers may assume plain values and fail; recover with backwards-compatible fields and migration warnings.
- cost: Negligible API cost; small storage and context-token increase.  ·  latency: Milliseconds for envelope creation; occasional extra source read.
- security: Improves provenance; ensure source paths and private URLs are permission-filtered.
- depends on: A live device registry read; Existing /pipeline, /observe, /ops/status projections


## What it asked for

_Nothing._
## Its own summary

Fresh perception round complete. Live facts: the relay has no registered nRF9160 pendant or ESP32 audio bridge; only home-macbook-bridge and Safari are online. Safari extension has 3 tabs and zero pending commands, but its reported active tab is example.com / “Failed to open page.” AI Pendant Agent is running, yet Accessibility and Screen Recording are false; /observe says synthesized events are rejected and GUI receipts are untrustworthy. Pipeline contains historical nRF9160 and 24-kHz audio records, not proof of present connectivity. I recorded these facts, warned judgement/action, and submitted three new capabilities: contradiction detection across telemetry, a pre-action UI reachability gate, and durable disconnected-pendant work with delivery-only confirmation/replay.

**Biggest unknown:** Whether the two physically claimed USB serial devices actually exist and respond locally; the relay cannot establish that. I need a Mac-terminal observation of both /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA. Separately, the owner still needs to grant Accessibility and Screen Recording to the exact AI Pendant Agent binary before GUI perception/action can be trusted; that cannot be done by this system.

