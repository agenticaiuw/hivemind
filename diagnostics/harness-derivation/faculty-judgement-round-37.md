# Harness derivation — faculty-judgement — round 37

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Decide what deserves my attention now. Give me one short spoken brief when I have a spare moment, defer the rest, and let me say ‘why?’ or ‘do it’ to continue from the exact item.”"
- **useful because:** The current system can generate many briefs and watches, but it can still interrupt, duplicate, or present stale work at the wrong time. This turns the hive into an attention manager: urgency and freshness matter, but so do the owner's calendar, active Mac focus, current audio, and whether the pendant is available. The owner gets fewer interruptions and a continuous spoken thread instead of a pile of notifications.
- **path:** relay-realtime receives urgent events and owns the durable attention queue → mac-planner reads calendar, focus state, battery/connectivity, and recent task state → browser-extension supplies cited changes from already-authenticated tabs without exporting credentials → faculty-perception normalizes urgency, freshness, confidence, and required effort → faculty-judgement arbitrates an attention budget and chooses spoken brief, Mac notification, queued audio, or silence → pendant plays a 24 kHz item with item IDs; button/voice commands ask why, defer, bookmark, or continue → mac-vision/mac-terminal perform only the reversible follow-up, stopping for destructive confirmation
- **model tier:** Use a cheap background model to cluster/deduplicate events and score urgency; use the realtime tier only for the spoken interaction and the final choice among already-computed candidates. Do not send full browser pages or the whole memory context on every turn—send compact evidence cards.
- **latency:** Urgent event scoring under 5 seconds server-side; a spoken brief should start within 1 second once the owner is interruptible. Deferral and resume must be durable across a dropped pendant link or Mac sleep.
- **cost:** Roughly $0.01–$0.05 per daily owner, dominated by speech generation and background event extraction; realtime tokens are limited to the selected card and the owner's follow-up.
- **security:** Private page content stays on the Mac/browser bridge and only cited snippets plus sensitivity labels leave it. Never speak secrets aloud by default. ‘Do it’ must resolve to a typed, reversible action plan and request confirmation for sending, deletion, purchases, or external publication. Store only card metadata and short-lived audio, with deletion controls.
- **missing:** A durable attention-card schema with source, urgency, freshness, sensitivity, estimated listening time, and deduplication key; A cross-surface lease so only one surface speaks or notifies at a time; Calendar/focus/audio-playback signals from the Mac and a quiet-hours policy; Pendant item controls (pause, defer, bookmark, resume) that survive reconnects; A 24 kHz audio acceptance test and telemetry for packet loss, decode time, underrun, and end-to-end latency

### "“Catch conflicts in my real life before they become mistakes—like two commitments at once, a deadline that depends on an unavailable document, or a travel plan that no longer fits—and give me the smallest decision I need to make.”"
- **useful because:** Today the owner can ask for separate calendar, mail, browser, and Mac checks, but no one continuously reconciles those facts into a causal conflict. This would prevent missed commitments and wasted preparation by surfacing only the blocking contradiction, explaining its evidence, and proposing the least disruptive resolution rather than dumping another briefing on the owner.
- **path:** relay keeps a durable conflict inbox and can reach the owner even when the Mac sleeps → mac-planner indexes local calendar, reminders, files, and task state with provenance → browser-extension reads only already-authenticated tabs the owner has authorized, such as reservations or work portals → faculty-perception extracts dates, dependencies, availability, and confidence from each source → faculty-judgement identifies genuine collisions or broken prerequisites, asks one focused clarification through realtime voice, and records the owner's resolution → faculty-action uses Mac/browser surfaces to create reversible updates or drafts after approval, then reports what changed on the pendant
- **model tier:** Use a cheap background model for periodic entity/date/dependency extraction and graph reconciliation; use the realtime tier only for the concise conflict explanation and the one clarification question. Escalate to a stronger model only when sources disagree materially.
- **latency:** Incremental reconciliation within 1 minute of a source change; urgent collision notification within 10 seconds. The spoken explanation should be one short sentence plus an optional drill-down.
- **cost:** About $0.01–$0.08 per day, dominated by extraction from changed private pages and local documents; unchanged sources are represented by hashes and do not incur repeated full-context inference.
- **security:** Keep raw mail, page content, and documents on their originating Mac/browser surface. Share only normalized facts, citations, confidence, and sensitivity labels with the relay. Never infer or announce sensitive health, financial, or relationship conflicts aloud without a private-mode signal. Fixes that send, delete, purchase, or publish always require confirmation.
- **missing:** A provenance-preserving cross-surface fact/dependency graph with temporal validity and explicit contradiction records; Source adapters for local calendar/reminders/files and authenticated reservation/work pages; A conflict severity model distinguishing a true blocker from a harmless duplicate or stale copy; A focused clarification/resolution record that can be resumed after the owner is interrupted; Safe reversible update plans that can modify multiple surfaces atomically or clearly report partial completion


## Changes it proposed to its own stack

### `firmware` — Add an end-to-end audio contract and telemetry path rather than treating the 24 kHz decoder as a local success: tag every Opus frame with stream/item IDs and capture/playback timestamps; emit compact counters for capture overruns, packet loss, PLC use, decode time, resampler ratio, queue depth, underruns, and button interruption. The relay correlates these with transcode and WebSocket timestamps, while the Mac dashboard renders a per-session acceptance report. Define an automatic fallback ladder (24 kHz playback → lower bitrate/packet cadence → text/Mac notification) and resume from the last acknowledged item after reconnect.
- **owner gets:** The owner hears a consistent, resumable briefing instead of silence, clipped speech, or losing their place when the pendant link changes. It makes the requested superwideband path something that can be trusted every day, not merely something that passes a lab audio sample.
- effort: Medium-high: firmware frame metadata/counters and reconnect state, relay correlation and fallback, Mac acceptance report, plus hardware-in-the-loop tests across radio loss and sleep/wake.  ·  risk: Extra metadata and counters can increase bandwidth and firmware complexity; bound them to periodic aggregates and feature-flag rollout. If 24 kHz decode overruns the single core (currently about 87% when encode and decode overlap), downgrade before audio underruns. Recovery is automatic fallback plus a retained item cursor; never replay an item already acknowledged.
- cost: Negligible API cost; a few bytes per frame and a small periodic telemetry record. Engineering/test cost is the main expense. Product hardware may need a faster audio-capable MCU if sustained simultaneous encode/decode remains above the thermal or latency budget.  ·  latency: Counters are asynchronous. Fallback decisions add at most one packet interval (~60 ms) when queue health crosses a threshold; reconnect resume adds no extra spoken interaction.
- security: Telemetry contains timing and quality counters, not microphone PCM or decoded text. Stream/item IDs must be opaque, and retention should follow the existing short-lived audio policy.
- depends on: 24 kHz relay transcode and pendant playback path; Durable cross-surface job/item IDs and reconnect cursor; A hardware-in-the-loop audio test harness; An owner-visible audio acceptance report


## What it asked for

_Nothing._
## Its own summary

I discovered the current owner context, live device status, tools, and backlog. I recorded two non-duplicate proposals: an attention-budgeted cross-surface spoken queue that chooses when and how to interrupt, and firmware/relay audio-contract telemetry with resumable fallback for the 24 kHz path. The owner-facing value is fewer mistimed interruptions and reliable resumable audio, not another generic watcher or briefing.

**Biggest unknown:** The system still reports zero granted capabilities this round, so I cannot verify whether the cross-surface attention lease, interruption signals, durable item cursor, or audio acceptance harness now exist. The relay/Mac agents must confirm those implementation primitives and the remaining 24 kHz end-to-end test results.

