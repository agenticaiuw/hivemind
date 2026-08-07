# Harness derivation — mac-planner — round 22

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“When I ask you to do something that takes time, keep working after I leave and tell me exactly what happened when it’s done.”"
- **useful because:** Turns isolated voice/tool calls into a personal hive mind: the relay can accept work instantly, delegate to the Mac or server browser, retry offline nodes, run parallel subtasks, and deliver a concise receipt rather than losing work when the voice session ends.
- **path:** relay → mac-bridge → browser → dashboard → iOS → pendant
- **model tier:** Use realtime only to acknowledge/enqueue and answer status questions. Use a cheaper background model for decomposition, ranking, summarization, and retries; use the Mac planner/browser model only for the concrete action each node can perform.
- **latency:** Enqueue acknowledgement under 500 ms. Status event within 2 s of each state transition. Background jobs may run minutes or overnight; no voice turn should block on them.
- **cost:** Roughly $0.01–$0.10 per ordinary multi-step job, dominated by planner/browser tokens; receipts should use a small model and cached event summaries. Avoid sending the entire history/context on every heartbeat.
- **security:** The ledger must isolate owner/job scopes and encrypt sensitive artifacts. A receipt must list every side effect (files, messages, purchases, browser mutations) and source node. The owner has chosen maximum Mac access/no confirmation gates, so preserve that policy but provide immutable audit and an emergency cancel/kill switch. Never put raw mail, credentials, or page bodies in notifications; authenticated browser sessions stay on the browser node. Use leases, idempotency keys, and dead-letter recovery to prevent duplicate destructive actions.
- **missing:** A durable enqueue endpoint callable by the relay without holding the voice request open; One append-only job/event/receipt schema shared by relay, Mac bridge, and browser watch; Mac worker lease/heartbeat/result adapter over /v1/bridge/work; Server-side scheduler with retry, timeout, cancellation, and offline-node fallback; Push delivery of terminal summaries to pendant/iOS/dashboard and optional audio artifact generation; Cross-node artifact references and correlation IDs for parallel subtasks

### "“Just give it the goal; figure out whether the Mac, browser, pendant, or server should do each part, and use whichever can.”"
- **useful because:** Removes manual routing and enables parallel work: authenticated browser work stays in the browser, local files/apps stay on the Mac, durable research runs server-side, and the pendant remains the always-available interface. The owner gets one coherent answer instead of tool-specific failures.
- **path:** relay → mac-bridge → browser → dashboard → iOS → pendant
- **model tier:** A cheap background router classifies each subtask from a capability registry and decomposes independent work. Use realtime only for clarification and progress narration; invoke the expensive Mac/browser planner only after routing. Use a small summarizer to merge receipts and detect conflicts.
- **latency:** Route and acknowledge in under 300 ms; start independent subtasks within 1–2 s. Merge partial results as they arrive; wait only for dependencies explicitly marked blocking.
- **cost:** About $0.005–$0.03 per routing/merge operation with a small model and compact capability metadata; execution costs remain task-dependent. Cache registry and avoid passing full transcripts to every node.
- **security:** Capability declarations must state data scopes and side effects, not just names. Route secrets only to the node that already holds them; authenticated sessions and local files must not be copied into relay prompts. Record routing decisions and node receipts. Because Mac execution is intentionally ungated, provide a visible live activity stream and kill switch rather than silently weakening owner policy.
- **missing:** Versioned capability registry with node health, data locality, latency, and side-effect metadata; Dependency-aware DAG planner and parallel fan-out/fan-in executor; Common event/receipt protocol and conflict resolver; Per-node scoped credentials and artifact handles; Cancellation propagation and offline fallback policy; Dashboard view showing which node is doing what and why

### "“While I sleep, prepare tomorrow’s brief and leave me a short audio queue I can listen to from the pendant.”"
- **useful because:** Makes the wearable useful without a live conversation: overnight jobs combine calendar, mail, completed task receipts, and explicitly authorized browser watches, then deliver a prioritized, interrupt-free briefing when the owner is ready.
- **path:** relay → dashboard → iOS → pendant → mac-bridge → browser
- **model tier:** Scheduled/background work uses a cheap model for extraction, deduplication, and ranking; a small synthesis model writes the script. Realtime is used only if the owner asks follow-up questions while listening.
- **latency:** Run during a configurable overnight window; produce the brief before the owner’s chosen wake time. Pendant playback starts locally within 200 ms after a button press, with resumable chapters.
- **cost:** Typically $0.02–$0.08 per brief, dominated by summarizing new mail/browser evidence; cache unchanged source summaries and synthesize only deltas. Audio generation/storage adds a small per-minute cost and should expire automatically.
- **security:** Default to snippets and metadata; exclude sensitive mail, private browser pages, and message bodies unless explicitly enabled. Show source links and a “why included” label in iOS/dashboard. Encrypt audio, expire it after a short retention period, and ensure a lost pendant cannot replay another person’s brief without pairing.
- **missing:** Reliable scheduled job runner and source snapshot timestamps; Audio generation plus offline pendant download/resume/expiry protocol; Calendar/Mail/browser connectors with per-source privacy scopes; A quiet-hours and interruption policy; Cross-node receipt aggregation and deduplication


## Changes it proposed to its own stack

### `memory` — Replace per-surface hand-written fleetContext prompts with a shared, event-sourced personal memory broker. Every node writes typed facts, preferences, commitments, and task outcomes with provenance, confidence, sensitivity, expiry, and visibility scope; each surface requests a relevance-filtered context slice by task rather than receiving a giant static prompt. Add contradiction resolution and supersession, plus a nightly cheap-model compaction job.
- **owner gets:** Telling the pendant once that a deadline moved, a preference changed, or a task was completed becomes immediately true on the relay, Mac, browser, dashboard, and iOS. The assistant stops repeating stale questions and avoids exposing unrelated private history to whichever node is acting.
- effort: Medium-high: D1 schema/API, extraction and conflict rules, per-node adapters, migration of fleetContext.js, and dashboard provenance UI; 2–4 weeks for a robust prototype.  ·  risk: Bad extraction or conflict resolution could create false memories or hide a real one. Keep original events immutable, show provenance/confidence, support correction and tombstoning, and fall back to the raw session when confidence is low.
- cost: Small ongoing background-model cost for extraction/compaction; lower per-turn token cost because context is sliced and deduplicated. Storage grows with events but remains modest in D1/R2.  ·  latency: A relevance query should add under 150 ms from D1/cache; first-time extraction is asynchronous and must not block realtime acknowledgement.
- security: Sensitivity labels and node scopes are mandatory; browser credentials/page bodies never enter shared memory by default. Encrypt sensitive facts and log every cross-node read.
- depends on: Durable job/event identifiers and receipt schema; A memory API that supports provenance, scope, expiry, and correction; Per-surface context adapters replacing prompt-string concatenation

### `hardware` — Build the wearable revision around the nRF9160 with an ultra-low-power 6-axis IMU on the unused I2C bus, a vibration/LRA haptic driver, and a real microphone/audio front end with physical mute. Keep the current button/LED as fallback, but expose motion gestures (double-tap, pickup, shake) and haptic acknowledgement locally; buffer only short event metadata unless the owner explicitly records audio.
- **owner gets:** The pendant can recognize that it was picked up, worn, or tapped and acknowledge actions silently in a meeting, even with the phone/Mac disconnected. Motion context lets the hive mind distinguish an accidental button press from an intentional request and deliver completion alerts without requiring the owner to stare at a screen.
- effort: High: industrial redesign, low-power driver/firmware, enclosure and battery validation, audio EMC testing. Prototype with BMI270-class IMU, DRV2605L-class haptic driver, and a digital MEMS mic.  ·  risk: False gesture triggers, comfort/battery degradation, and accidental recording are serious risks. Require a physical mute that cuts mic power, use conservative gesture thresholds with local-only classification, and expose battery/recording state through haptic patterns and LED. Gracefully disable sensors if power or I2C faults occur.
- cost: Approx. $8–$20 BOM increase in small volumes (IMU $1–3, haptic path $2–5, mic/audio $1–4, mechanics/battery allowance); roughly 1–5 mA active sensor/haptic bursts, with sub-100 µA IMU suspend target. No continuous cloud-token cost for local gestures.  ·  latency: Local gesture acknowledgement under 50 ms; event upload is asynchronous and does not delay voice. Audio front end may reduce capture latency but requires buffering/RAM discipline against the 211,608 B application RAM and existing Opus footprint.
- security: Physical mic cutoff and a local recording indicator reduce covert-capture risk. Motion events should be coarse and opt-in; never upload raw accelerometer streams by default. Haptic patterns must not encode sensitive content in public settings.
- depends on: A production wearable board/enclosure rather than the current nRF9160 development kit; Firmware skills for low-power I2C IMU, haptic patterns, and physical mic-mute state; Shared event ledger so local events can be correlated without uploading raw sensor data


## What it asked for

_Nothing._
## Its own summary

Proposed a durable cross-node job ledger with leases, heartbeats, append-only receipts, retries, cancellation, and pendant/dashboard delivery; a shared event-sourced memory broker replacing per-surface prompt hand-writing; capability-aware DAG routing across relay/Mac/browser; overnight audio briefings; and a production pendant revision with low-power IMU, haptics, physical mic mute, and local gesture handling. I also aligned relay and browser-extension agents on the common receipt/event contract. The granted Mac read-only inspection tool is still unimplemented, so I could not verify running apps, foreground app, or Accessibility state.

**Biggest unknown:** The concrete durable queue/receipt API and worker lifecycle are still undefined, and the Mac inspection harness has no implementation. Until those exist, routing and background work remain proposals rather than an end-to-end reliable hive mind.

