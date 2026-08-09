# Harness derivation — faculty-perception — round 157

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live mac/browser/permissions state round 157** — GET /ops/snapshot and /ops/status are live: Mac agent ready with Accessibility and Screen Recording granted, Safari browser bridge online with 9 tabs and 0 pending commands, relay reachable on D1, and no pendant appears in the discovered device registry. GET /pipeline contains historical runs whose completion stops at relay_result; no device_playback event is present in the observed completed news run.
  - evidence: Authenticated GET /ops/snapshot, GET /ops/status, GET /browser/status, and GET /pipeline in round 157.

## Capabilities it proposed

### "Tell me whether the system's claim that an answer was delivered is actually trustworthy, and show me the exact contradiction if it is not."
- **useful because:** Today a pipeline can say completed while only proving that the relay accepted bytes; this gives the owner a precise confidence fence instead of a falsely reassuring status. It would catch the observed pattern: relay_result done with no device_playback evidence, and stale pendant-origin events despite no registered pendant.
- **path:** relay-realtime → relay → mac-planner → browser-extension → faculty-perception → faculty-judgement
- **model tier:** background cheap model for continuous reconciliation; realtime only when the owner asks a spoken question about a specific delivery
- **latency:** Under 2 seconds for a queried artifact; periodic reconciliation can run every 5 minutes without affecting conversation latency.
- **cost:** About $0.001–$0.01 per reconciliation batch, dominated by text summarization only when raw events conflict; normal matching is deterministic.
- **security:** Return event IDs, timestamps, source, and confidence—not private audio or page text. Treat Mac-authored telemetry and pendant telemetry as separate trust domains; never upgrade relay acceptance to playback. Owner confirmation required before redelivering or declaring an item heard.
- **missing:** A defined device_playback/played event emitted by firmware (the existing accepted audio_delivery_ack_queue is the intended foundation); A relay reader that joins device playback events to the artifact/job and preserves contradiction records; A single authenticated cross-surface snapshot route that actually resolves; the currently granted read_continuity_snapshot fails resolution and nearest live route is GET /ops/snapshot

### "Before you promise that my pendant is available, tell me which link is alive right now: USB attachment, audio bridge, relay registration, browser bridge, and last heartbeat—each separately."
- **useful because:** The owner currently has a Mac and browser that are live while the nRF pendant is absent from the relay registry; collapsing these into one 'device online' boolean causes actions to be aimed at a body that cannot receive them. This matrix would make offline/USB testing useful without pretending LTE registration exists.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement
- **model tier:** Deterministic state join with a small background model only to explain ambiguous transitions; no realtime model needed for the measurement.
- **latency:** 1 second when asked; USB and bridge probes sampled every 10 seconds, relay/browser freshness under 90 seconds.
- **cost:** Negligible API cost; local serial enumeration and existing health routes dominate. Optional explanation is under $0.002 per request.
- **security:** Expose device IDs only in redacted form and never serial payloads or bearer credentials. USB presence is not proof of owner wearing the device; say 'attached to Mac' rather than 'worn.' Require confirmation before routing private speech to a newly seen serial device.
- **missing:** A read-only USB serial health probe for the physically attached nRF9160 and ESP32 bridge (the previously requested tool is still unavailable); Firmware heartbeat/registration that reports identity and monotonic freshness to the relay; A shared schema distinguishing physically attached, locally responsive, relay-registered, and owner-heard

### "After you change something in an app or website, tell me whether the visible state actually changed, what changed, and whether the browser and Mac disagree."
- **useful because:** Action receipts currently describe commands and transport, not the resulting world. With Accessibility and Screen Recording now granted, the system can finally verify the postcondition on the Mac and compare it with the browser extension's tab state, catching silent failures such as a click that was accepted but never applied.
- **path:** mac-vision → mac-terminal → browser-extension → mac-planner → faculty-perception → faculty-action
- **model tier:** Cheap deterministic postcondition checks first; vision model only for ambiguous screenshots or semantic UI changes, and realtime only if the owner is waiting interactively.
- **latency:** 2–5 seconds after an action; up to 10 seconds for a vision fallback. No extra work when an app supplies a structured AppleScript/API readback.
- **cost:** $0 for structured readbacks; roughly $0.003–$0.03 for an occasional screenshot vision check, dominated by image tokens.
- **security:** Screenshots may contain private messages, passwords, or financial data; redact known secret regions and retain only a hash plus a short semantic result. Never infer success from a screenshot when the target is a login, payment, deletion, or message send without owner confirmation.
- **missing:** A postcondition contract on each reversible action (expected app, URL, selector/state, and timeout); A mounted browser provenance route so the observed URL/tab/claim can be joined to the action ledger; A redacting screenshot verifier that emits a bounded result rather than storing raw images

### "When I am about to close the lid or walk away, give me a truthful 'safe to leave' handoff: what is still unsaved, what is still running, what the browser has not applied, and what the pendant cannot receive—and let me postpone or hand each item off."
- **useful because:** The owner should not have to remember whether a Mac job, browser command, cloud response, or spoken answer is stranded when they disconnect. This is a physical-world handoff decision, not another task list: it distinguishes work safely persisted, work awaiting a local machine, and work that will be unreachable when the owner leaves.
- **path:** pendant → mac-planner → mac-terminal → mac-vision → browser-extension → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Deterministic inventory and state joins first; a cheaper background model explains only ambiguous unsaved-work or browser states. Realtime is used only for the pendant's spoken handoff summary.
- **latency:** A 3–5 second scan after a button press or voice request; up to 15 seconds when screen verification is needed. Handoff must fail closed if freshness is unknown.
- **cost:** Typically under $0.01 using existing structured routes; $0.01–$0.05 when screenshot interpretation is needed. The dominant cost is vision tokens, not the state joins.
- **security:** The report may expose document names, message subjects, and private tabs; speak only counts and app names by default, with owner confirmation for details. Never close apps, send messages, or upload work automatically. Persist only opaque item IDs, status, and expiry—not document contents.
- **missing:** A cross-surface handoff contract with freshness timestamps and explicit states: persisted, resumable, blocked-local, browser-pending, relay-queued, pendant-unheard, and unknown; A Mac unsaved-document and active-write observer that can report postconditions without scraping private content; A browser command lease/finalization protocol so pending commands are either acknowledged by the extension or safely canceled before disconnect; A relay queue export that identifies speech/audio still awaiting a reachable device; A pendant button/voice mode that requests the scan locally and can announce a bounded result offline


## What it asked for

_Nothing._
## Its own summary

Fresh live truth: Mac agent is ready with Accessibility and Screen Recording granted; Safari bridge is online with 9 tabs and zero pending commands; relay is reachable on D1; no pendant is present in the discovered relay device list. Pipeline history still shows a response as relay_result/done without device_playback, so 'completed' remains transport evidence, not owner-heard evidence. I recorded three capabilities: contradiction-aware delivery confidence, a USB/relay/browser connection truth matrix, and postcondition verification for Mac/browser actions.

**Biggest unknown:** The newly granted read_continuity_snapshot cannot resolve at runtime: its resolver scores only the existing GET /ops/snapshot route below threshold. I still need an actually callable authenticated continuity snapshot (or a resolver binding to GET /ops/snapshot), plus the missing physical USB probe and firmware playback/heartbeat events to distinguish attached, registered, received, and heard.

