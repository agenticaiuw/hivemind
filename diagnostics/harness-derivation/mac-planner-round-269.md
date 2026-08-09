# Harness derivation — mac-planner — round 269

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-accessibility-state** — AI Pendant Agent currently has Accessibility and Screen Recording; synthesized input is verified reaching the screen, secure input is off, and Safari/4 browser sessions are live.
  - evidence: mac_readonly_inspect running_apps response at 2026-08-09T01:10:32Z: accessibility.trusted=true, screenRecording=true, eventsPost=true, inputReachability=verified; browser.sessions=4.

## Capabilities it proposed

### "When I press the pendant bookmark button, save exactly what I am looking at on the Mac—selected text or window title, active browser URL, and the nearest calendar meeting—and turn it into a follow-up capsule I can ask for later."
- **useful because:** The current bookmark records only a moment. This would preserve the actionable context that disappears when the owner changes windows, while requiring no speech and working even when the pendant is only USB-attached to the Mac.
- **path:** pendant → relay → mac-vision → browser-extension → mac-planner
- **model tier:** Realtime only for the short button acknowledgement; a cheaper background model extracts title, URL, and follow-up fields from the captured context.
- **latency:** Acknowledge the button in under 300 ms; capture Mac/browser/calendar state within 3 s; capsule extraction within 10 s.
- **cost:** About $0.01–$0.05 per capture, dominated by optional text summarization; raw metadata capture is effectively free.
- **security:** Selected text and URLs may contain secrets. Default to metadata-only and redact page text; require an explicit owner setting before sending selected text to the relay. Never capture passwords or secure-input fields.
- **missing:** A button-event fanout from offline_moment_bookmark to a Mac context capture request; A structured context-capsule record joining pendant timestamp, Mac window identity, browser tab and calendar event; A relay query route for later capsule retrieval

### "Run a short pendant health check every night while it is plugged into my Mac, and tell me tomorrow only if audio quality, packet loss, or the USB-connected device changed."
- **useful because:** The pendant and audio bridge are physically testable now, and recent audio failures were subtle codec/framing defects. A scheduled, unattended acceptance check would catch regressions before the owner relies on a call, without recording microphone content.
- **path:** pendant → mac-planner → relay → mac-terminal → mac-vision
- **model tier:** Use a cheap background model to compare bounded diagnostic counters against the last known-good receipt; escalate to realtime only when the owner asks what changed.
- **latency:** Run during a 60–90 second overnight window; produce a compact result by morning and speak only an anomaly.
- **cost:** Under $0.02 per run; compute is dominated by the local fixture and log parsing, not model tokens.
- **security:** The fixture must synthesize audio only and never read or persist microphone content. USB serial logs may include device identifiers; redact them from the relay and retain only counters, firmware hash, and pass/fail deltas. No firmware flashing or shell mutation should occur as part of the nightly check.
- **missing:** A scheduler job type that can target the currently USB-attached nRF9160 and ESP32 ports; A bounded Mac bench runner that invokes audio_path_diagnostic_fixture and returns structured counters, exit status, and firmware identity; A durable baseline comparator and anomaly notification record

### "When I engage the pendant's privacy latch, also mute the Mac's microphone and pause browser audio; when I release it, restore only the things that were on before."
- **useful because:** The pendant privacy latch currently protects the pendant's own capture and playback, but the owner can still be live in a Mac meeting or have browser audio playing. Coordinating the physical latch with the Mac makes one deliberate gesture a reliable whole-workspace privacy state.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** No expensive model is needed for the state transition; use deterministic event handling, with realtime only to tell the owner the concise resulting state.
- **latency:** Mute Mac microphone and pause browser audio within 500 ms of the latch event; restore in under 1 s after local release.
- **cost:** Near-zero model cost; it is a small event fanout and state snapshot.
- **security:** The relay must fail closed: if the link is down, the pendant remains locally private, and the Mac must not be falsely reported as muted. Store only pre-latch mute/playback state, encrypt the event, and never auto-unmute an app that the owner muted independently during the latch.
- **missing:** A relay event contract carrying local_privacy_latch enter/exit with delivery acknowledgement; A Mac privacy actuator that targets meeting apps and browser audio without relying on screen focus; A reversible state ledger for per-app microphone and playback state

### "While I was away, tell me exactly what the pendant, relay, Mac, and browser did on my behalf, in time order, and let me ask why any individual action happened."
- **useful because:** Today the owner can get individual job receipts or ask what happened to one Mac job, but cannot reconstruct a trustworthy cross-surface activity trail. A spoken, provenance-linked timeline would make unattended automation comprehensible and let the owner catch an unwanted browser navigation, file change, or pendant alert without manually searching logs.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use a cheap background summarizer to cluster receipts and events; reserve realtime for the owner's spoken drill-down questions.
- **latency:** Return a one-minute activity digest within 5 seconds; drill into one event within 2 seconds if its receipt is already indexed.
- **cost:** $0.01–$0.04 per digest, dominated by summarizing event metadata; drill-downs are near-zero when no new synthesis is needed.
- **security:** The timeline may expose mail subjects, URLs, file paths, and private audio-event metadata. Keep raw payloads local where possible, redact secrets before relay upload, enforce per-owner retention, and distinguish observed facts from inferred explanations. Never claim an action succeeded without its receipt.
- **missing:** A shared event envelope with timestamp, originating surface, intended command, touched resources, result, and receipt linkage; A cross-surface append-only activity index joining relay jobs, Mac action receipts, browser command results, and pendant event acknowledgements; A spoken query endpoint that can return provenance and uncertainty rather than only a prose summary


## What it asked for

_Nothing._
## Its own summary

Discovered fresh live state: AI Pendant Agent now has Accessibility and Screen Recording, synthesized input reaches the screen, secure input is off, and Safari has four durable sessions. Recorded three distinct cross-node capabilities: button-triggered context capsules, scheduled USB-connected pendant/audio-bridge health checks, and pendant privacy-latch fanout to Mac/browser microphone and audio state. The Safari Reading List request was rejected as an existing backlog item, not rephrased. I also broadcast the permission/state change to the hive.

**Biggest unknown:** The remaining practical gaps are implementation contracts: a typed Safari Reading List extractor, a structured context-capsule store/query route, a bounded USB bench runner with structured diagnostic receipts, and a fail-closed Mac privacy actuator that preserves per-app prior state.

