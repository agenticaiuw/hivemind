# Harness derivation — relay-realtime — round 109

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Why are you telling me that, and what exactly did you use?” Give me a spoken, source-linked explanation for any answer or action produced across my Mac, browser, and pendant."
- **useful because:** Today the owner can receive a result while away from the Mac but cannot reliably distinguish a live browser observation, a stale Mac receipt, an inference, or an unverified claim. A single provenance explanation would make the hive trustworthy: it would name the source surface, capture time, relevant excerpt/action receipt, and confidence, then read a short version aloud with an optional detail request.
- **path:** pendant → relay → mac-planner → browser-extension → browser → dashboard
- **model tier:** Realtime relay summarizes a precomputed provenance record into a brief spoken answer; a cheaper background model (or deterministic formatter) builds and normalizes the record from Mac receipts and browser observations. Do not spend the realtime tier reconstructing history.
- **latency:** Initial answer under 2 seconds when provenance is already attached to the result; up to 5 seconds for a live browser/Mac lookup. Detail follow-ups should stream incrementally and never require the owner to repeat the original question.
- **cost:** Usually below one extra cheap-model call per answer; dominant cost is storing/transporting compact excerpts and metadata, not generation. Full page text and screenshots should be retained only when explicitly requested.
- **security:** Authenticated browser content, Mac paths, and voice history can be sensitive. Relay must pass source references and redacted excerpts by default, preserve the existing browser/Mac session boundaries, and require an explicit spoken request before reading secrets or full page content aloud. Provenance must distinguish observation from model inference and never fabricate citations.
- **missing:** A shared provenance schema and immutable correlation ID carried from relay voice run through /research, browser inspection, Mac plan/action, and final spoken response; A result envelope that attaches source snippets, timestamps, freshness, and action receipt IDs to every downstream result; Relay endpoint to fetch a compact provenance bundle and a pendant-friendly detail level without resending the whole conversation; Dashboard view to inspect and revoke provenance records independently of ordinary operation history

### "“Stop that now.” Cancel the Mac or authenticated-browser task currently running, then tell me exactly what completed, what was prevented, and whether anything needs undoing."
- **useful because:** A worn pendant is often the only interface available while a delegated task runs. Existing status and undo records are not an immediate stop control: the owner cannot reliably halt a long browser workflow or Mac plan after noticing a wrong target. An explicit interrupt with a bounded stop point prevents the next queued action while preserving an honest partial-result report.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → browser → dashboard
- **model tier:** Realtime relay recognizes the short interrupt and sends a deterministic cancellation signal; no expensive model call is needed. A cheap background formatter summarizes the completed action receipts after the worker acknowledges cancellation.
- **latency:** Cancellation acknowledgement within 500 ms from relay receipt; downstream agent must stop before its next action and acknowledge within 2 seconds. Summary can arrive within 5 seconds, even if the Mac or browser is temporarily offline.
- **cost:** Negligible inference cost; dominant work is an always-available cancellation channel and durable receipt writes. A small heartbeat while a job is active is acceptable to make the stop latency honest.
- **security:** The cancel command must be bound to the owner's active voice session and current job, not an arbitrary job ID spoken by an attacker. Cancellation must never silently imply rollback: report completed mutations separately and offer existing undo only where a receipt supports it. Browser session tokens and Mac credentials stay on their original surfaces.
- **missing:** A first-class cancel endpoint and job state transition (cancelling, stopped, completed) spanning relay, Mac planner, and browser command queue; Cooperative cancellation checkpoints before every Mac/browser action, including a lease/heartbeat expiry that stops work when the relay disappears; A pendant utterance-to-active-job binding that handles “that task” without asking the owner to remember an ID; A partial-execution summary envelope linked to action receipts and a dashboard control for operators


## Changes it proposed to its own stack

### `relay` — Publish a relay capabilities endpoint and a live routing table (similar to the Mac agent’s /capabilities) so this surface can be inventoried without guessing or probing.
- **owner gets:** Fewer misroutes and faster iteration. The relay can reliably say what it can do right now, which reduces silent failures and wasted rounds.
- effort: Medium. Define a small schema, expose it from the worker, and wire it to whatever routers/tools are actually live.  ·  risk: Low. Main risk is exposing internal names; mitigate by redacting secrets and only listing callable, supported intents/tools.
- cost: Tiny per request. Mostly developer time.  ·  latency: None in steady state; slight overhead for introspection calls.
- security: Medium. Needs careful filtering to avoid leaking internal routes or tokens.

### `integration` — Implement the granted schemas (relay_route_intent, server_browser_actions, relay_job_status) as real services with receipts, idempotency keys, and typed results. Route intent by calling the right downstream tool, not by prompt convention.
- **owner gets:** They get predictable behavior: tasks go to the right place, browser work can happen even if the Mac is offline, and status is available later without guessing.
- effort: High. Requires orchestration changes, durable storage, and a browser runner backend.  ·  risk: Medium. Misrouting could trigger unintended actions; mitigate with reversible defaults and receipts.
- cost: Moderate ongoing cost for storage and occasional headless browser runs.  ·  latency: Improves perceived latency by giving immediate acknowledgement while work continues elsewhere.
- security: High. Needs strict origin controls, session binding, and careful handling of authenticated pages.
- depends on: relay capabilities endpoint for introspection; durable job persistence on relay

### `firmware` — Upgrade the audio capture path to support a 24 kHz end-to-end mode (mic capture, encoding, transport, and relay storage), with fallback to current 16 kHz/Opus when bandwidth is constrained.
- **owner gets:** Better voice quality for dictation and conversation, especially when reviewing later audio notes or receipts.
- effort: High. Touches firmware, modem transport, and server decoding/storage.  ·  risk: Medium. Higher bandwidth and CPU usage could reduce battery life or break on poor LTE-M links; mitigate with adaptive bitrate and fallback.
- cost: Moderate. More compute and data per minute; may increase storage costs.  ·  latency: Slightly higher processing time; could be offset by better encoding settings.
- security: Low. Same content, different fidelity; ensure encryption and retention controls remain intact.

### `interaction` — Add true barge-in and resumable speech: the pendant continuously detects owner speech during relay playback, immediately ducks/stops audio, tags the interruption to the active voice turn, and lets the relay answer the interruption without losing the unfinished response. The relay keeps a compact sentence-level cursor and can resume only when the owner says “continue.”
- **owner gets:** The owner can naturally correct a misunderstood request or ask “which one?” without waiting through a long spoken answer. While away from the Mac, this makes delegated-task updates conversational instead of forcing repeated button presses or discarded context.
- effort: Medium: pendant audio-duck/VAD firmware, duplex stream state in relay, interruption-aware turn correlation, and a small resumable-response record. Test LTE jitter, overlapping speech, and button-triggered fallback.  ·  risk: False VAD triggers could cut off useful speech; recover by requiring a short speech threshold and retaining the response cursor. A dropped link must discard or expire the cursor rather than replay private audio. Never resume automatically after an ambiguous interruption.
- cost: One short-lived cursor and VAD metadata per active turn; no meaningful model-cost increase because the interrupted response is not regenerated. Streaming audio bandwidth remains the dominant cost.  ·  latency: Barge-in should duck playback in under 150 ms and route the new utterance in under 500 ms; resumption adds no model latency if the remaining audio was already synthesized, otherwise it uses the normal realtime path.
- security: Keep unsent synthesized audio and interruption text encrypted and expire them after the session. Do not log microphone audio used only for VAD; retain transcript only under the existing voice-run policy.
- depends on: A duplex pendant audio transport with playback-interruption events; Relay turn state that can address an active response and attach follow-up speech to it; Sentence/chunk boundaries in realtime output so resumption cannot repeat or skip content


## What it asked for

### `s17-0h3y` (skill) — completion_summary_queue
- does: Stores short completion summaries and a source receipt reference locally so the pendant can play them when the owner taps, even if the relay connection is spotty.
- must be on-device because: It must work when the owner is moving through poor coverage and needs quick access without waiting for a round trip.
- trigger: button press when summaries are waiting
- storage: small ring buffer in local storage (e.g., a few KB per item, capped at ~10 items)
- RAM budget: Minimal; keep only the current item in RAM and stream from storage when playing.

## Its own summary

Recorded three actionable additions: (1) cross-surface provenance answers that cite live browser observations and Mac receipts, (2) a voice-bound immediate stop for in-flight Mac/browser work with an honest partial-execution report, and (3) duplex barge-in/resumable speech so the owner can interrupt and continue a response naturally. The first two require connective contracts despite many underlying routes already existing; the third needs pendant duplex audio and relay turn state.

**Biggest unknown:** Whether the pendant transport is currently half-duplex and whether it exposes playback-duck/VAD interruption events; that determines the firmware and relay scope for the barge-in change.

