# Harness derivation — mac-planner — round 257

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac accessibility and screen capture** — The AI Pendant Agent now has Accessibility and Screen Recording permission, synthesized input is verified landing, secure input is inactive, and UI actions should reach the screen. This unblocks real mac-vision/UI incident capture that was previously blocked.
  - evidence: mac_readonly_inspect(operation=running_apps) and foreground_app both invoked GET /observe at 2026-08-09T00:33:34Z and returned trusted:true, screenRecording:true, eventsPost:true, uiActionsWillReachTheScreen:true.

## Capabilities it proposed

### "Run a complete pendant bench check and tell me whether the microphone, 24 kHz speaker path, modem framing, and Mac bridge are healthy; if anything fails, leave a timestamped diagnostic report in my AI-Pendant-Workspace."
- **useful because:** The owner can validate the real USB-connected hardware with one spoken request instead of interpreting UART output or discovering an audio regression during a live call. It exercises both directions and produces a durable report another agent can act on.
- **path:** pendant → mac-planner → relay-realtime → dashboard
- **model tier:** Deterministic firmware fixture and parsers first; a cheap background model may turn counters into a short explanation. Realtime is unnecessary unless the owner is waiting for the result.
- **latency:** Bench run 30–90 seconds; return a compact result immediately when the receipt arrives, with the full report written atomically.
- **cost:** <$0.01 per run; nearly all cost is local compute and USB test time, not inference.
- **security:** The fixture must synthesize audio only and never capture or persist microphone content. Reports may include device identifiers and paths; redact those from any cloud transcript. Writing to the workspace is a local mutation and should have an explicit routine policy entry.
- **missing:** A bounded, machine-readable USB serial diagnostic invoker/parser on the Mac (the existing run_shell route is arbitrary and receipts lack exit codes); A relay command that schedules audio_path_diagnostic_fixture and waits for its report; A report schema mapping fixture counters to pass/fail thresholds

### "Before my next calendar meeting, quietly test the pendant and Mac connection, choose the safest audio profile, and alert me on the pendant only if the call would be unreliable."
- **useful because:** It prevents the owner from entering a meeting with a broken microphone, stalled browser bridge, or overloaded 24 kHz decoder. The check can happen before the meeting while the owner is away, and it reports only an actionable exception instead of another status dashboard.
- **path:** relay-realtime → pendant → mac-planner → browser-extension
- **model tier:** Rules and measured counters for readiness and profile selection; a small background model only classifies the calendar event and writes an exception sentence. No realtime model unless the owner asks why it failed.
- **latency:** Start 5 minutes before the event; a 10–20 second diagnostic window; alert at least 2 minutes before start.
- **cost:** <$0.02 per meeting, dominated by no model calls and a short local fixture; repeated healthy checks should be entirely deterministic.
- **security:** Calendar titles and meeting URLs are sensitive. Only inspect the next event's start time and conferencing metadata, do not store the title or upload meeting content. Never automatically join the meeting or change the owner's active call; profile switching must be packet-boundary-safe and recorded.
- **missing:** A scheduler trigger that binds a diagnostic to the next calendar event; A read-only Mac network/bridge readiness probe exposed to the relay; A policy-aware pendant alert route for a failed preflight; A deterministic threshold table combining audio_path_diagnostic_fixture and duplex_audio_congestion_guard

### "When I say 'something broke' after pressing the pendant bookmark, collect a privacy-redacted incident bundle from the Mac and browser, attach the latest pendant diagnostic counters, and leave me a bug report with the exact recovery steps or a ready-to-file issue."
- **useful because:** The owner should not have to reproduce a failure or remember which tab, app, and audio state caused it. A single physical marker defines the incident boundary; the Mac can capture UI and logs while the relay correlates wearable QoS, yielding a useful report rather than a vague timestamp.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Deterministic collection and redaction first; a background model summarizes the bundle and proposes recovery. Realtime is only needed if the owner asks for immediate spoken triage.
- **latency:** Acknowledge the bookmark locally in under 300 ms; collect within 10 seconds; produce a draft report in under 30 seconds.
- **cost:** <$0.03 per incident; dominated by one bounded summarization call, with screenshots and logs kept local unless the owner explicitly files the report.
- **security:** Incident material can include screen contents, URLs, filenames, and logs containing tokens. Redact secure-input fields, cookies, authorization headers, and secrets before upload; keep raw artifacts local with a retention limit. Filing externally or sending mail requires the owner's existing destructive-action confirmation policy.
- **missing:** A coordinated incident ID linking pendant bookmark, Mac action receipts, browser commands, and audio QoS; A redaction-aware log/screenshot collector with explicit artifact retention; An issue-draft/file route that never submits externally without confirmation

### "While I am looking at a document or web page, let me say 'make a shareable copy' and have the Mac identify and remove secrets, private names, cookies, tracking links, and hidden metadata, then show me the redacted result before saving it to my workspace."
- **useful because:** Today the owner must manually hunt through a document, browser export, and metadata before sharing. This would turn a dangerous, error-prone cleanup into a repeatable cross-surface operation while preserving the original and making the proposed disclosure visible before it leaves the Mac.
- **path:** mac-vision → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** A local deterministic scanner should catch metadata, URLs, emails, tokens, and known secret patterns; a small local model can suggest semantic redactions. The realtime model only speaks the short confirmation/result.
- **latency:** Preview in 5–15 seconds for a normal document or page; never send or upload the result before the owner sees the preview.
- **cost:** <$0.05 per operation; local OCR/scanning dominates, with model cost only for ambiguous semantic text.
- **security:** The raw source must stay on the Mac. Redaction suggestions should be generated locally where possible; the owner must see an exact diff and approve any external send. Originals must be immutable and retained; generated copies need provenance and a clear destination.
- **missing:** A Mac semantic document/page extractor that can read rendered text and metadata without flattening it into an opaque screenshot; A deterministic secret/PII and metadata scrubber with an exact redaction diff; A preview surface that can display the proposed copy and block external transmission until explicit confirmation

### "Let me ask, 'What exactly did the system do while I was away?' and receive a tamper-evident, human-readable timeline spanning pendant button events, Mac actions, browser commands, files changed, and spoken alerts, with uncertainty called out instead of invented continuity."
- **useful because:** The owner currently has scattered receipts and logs, not one trustworthy account of autonomous activity. A cross-node timeline would make unattended automation auditable, expose partial failures and duplicate retries, and let the owner quickly revoke or undo the right operation.
- **path:** relay-realtime → pendant → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic event correlation, hashes, and clock-skew handling first; a cheap background model renders the timeline into one short spoken answer. Realtime is only needed when the owner asks.
- **latency:** Timeline query under 5 seconds for a day; append events within 1 second; missing/late events must be marked immediately rather than silently joined.
- **cost:** <$0.01 per query; storage and event indexing dominate, not inference.
- **security:** The log can expose document names, URLs, and private alerts. Store raw events locally or encrypted, redact secrets in spoken summaries, separate audit hashes from payloads, and require explicit confirmation before exposing sensitive details aloud. Hash-chain integrity is not proof that an event source was honest, so source identity and clock uncertainty must be shown.
- **missing:** A shared event envelope and monotonic correlation ID accepted by pendant, relay, Mac, and browser; An append-only, hash-chained cross-node journal with retry/deduplication semantics; A dashboard/query route that can expose gaps, clock skew, and exact touched resources without leaking raw payloads


## What it asked for

_Nothing._
## Its own summary

Discovered live state and produced three non-duplicate cross-node capabilities: USB bench qualification with durable report, pre-meeting audio/bridge readiness preflight, and bookmark-bounded incident bundles with redaction and recovery steps. The Mac agent now has verified Accessibility and Screen Recording, so UI capture/action is no longer blocked.

**Biggest unknown:** The remaining practical blockers are a bounded machine-readable USB diagnostic runner/parser, a scheduler that binds the fixture to the next calendar event, durable cross-node incident IDs plus redaction/retention, and an unambiguous browser inspection operation (the current browser-tabs resolution ties at two equally scored capabilities).

