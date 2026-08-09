# Harness derivation — faculty-perception — round 252

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-perception** — Live /ops/status reports AI Pendant Agent ready: Accessibility and Screen Recording granted, all required permissions present, browser extension online with one Safari tab, relay reachable and Mac bridge online at 2026-08-09T03:42:55Z. This supersedes earlier denied-TCC context.
  - evidence: GET /ops/status HTTP 200 at 2026-08-09; permissions.ready=true, accessibility.trusted=true, screenRecording.granted=true, requiredMissing=[], browser.online=true, relay.reachable=true.
- **delivery-reality** — At 03:43Z Mac input reachability is verified (synthetic event posted; uiActionsWillReachTheScreen=true), Safari extension is online, but the latest pipeline run explicitly remains held_by_relay with awaitsDevice=true, provesPlayback=false, heard=unknown and no device_playback event. Relay acceptance and 24 kHz TTS completion are not hearing evidence.
  - evidence: GET /observe and GET /pipeline HTTP 200; pipeline job_692a6b6f... delivery fields state=held_by_relay, awaitsDevice=true, heard=unknown, provesPlayback=false; TTS event is 24000 Hz, 122630 bytes, zero clipped samples.

## Capabilities it proposed

### ""Tell me whether the thing you just did is actually observable, and show me the evidence—not just that the job says completed.""
- **useful because:** The system currently conflates Mac completion, browser mutation, relay acceptance, and owner-heard playback. This gives the owner a single honest verdict with the strongest available postcondition and explicit unknowns.
- **path:** browser → mac → relay → pendant → dashboard
- **model tier:** background for receipt synthesis; realtime only when asked by voice
- **latency:** Under 2 seconds for an existing job; under 5 seconds if a fresh browser snapshot is required.
- **cost:** <$0.01 per check; dominated by one small model summarization, not tool calls.
- **security:** Evidence may contain page text or private UI. Keep content on Mac, send hashes/claims to relay, and require confirmation before exposing sensitive snippets.
- **missing:** A shared receipt schema joining jobId, browser commandId, action ledger step, evidence capsule, and pendant playback state; A relay-side reader that distinguishes Mac postcondition from device playback; A browser-result hook that always records a capsule/provenance link

### ""What is on the screen I am looking at right now? Describe only what you can verify, and tell me if the page changed while you were reading it.""
- **useful because:** The owner can ask from the wearable while Safari is live. It combines the browser's authenticated view with Mac vision and gives a timestamped, change-detectable answer rather than an ungrounded visual guess.
- **path:** pendant → mac → browser → relay
- **model tier:** realtime for the short spoken answer; cheaper vision/OCR model for extraction and comparison
- **latency:** 2–4 seconds end to end.
- **cost:** $0.01–$0.05 per request depending on screenshot vision; hashes and metadata are negligible.
- **security:** Never send screenshots to the relay by default; redact secrets locally, return only the minimal grounded claim, and require confirmation before reading sensitive fields aloud.
- **missing:** A live bridge from browser_snapshot/screenshot to the existing evidence capsule store; A content hash and capture timestamp in the browser result contract; A voice tool that requests a current browser observation instead of relying on stale prompt context

### ""If my pendant is unavailable, keep me informed through the best channel that is actually online, and tell me which channel delivered it.""
- **useful because:** Today the Mac bridge and Safari can be online while the pendant is offline. The owner should not hear a false 'sent' or wait silently; the system should detect channel reality and route a reversible fallback.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** background routing/state machine; realtime only for a spoken fallback when a live audio path exists
- **latency:** Detect within 15 seconds of a stale heartbeat; fallback notification within 5 seconds after policy evaluation.
- **cost:** <$0.005 per event; mostly deterministic state evaluation.
- **security:** Fallback channels can expose private content on-screen or in notifications. Classify sensitivity locally, suppress high-sensitivity fallback by default, and require confirmation for external browser actions.
- **missing:** A durable channel-health policy that distinguishes pendant offline from merely absent in the registry; Delivery receipts for Mac notifications/browser surfaces and a real pendant playback event; A single deduplicated announcement ID across fallback channels

### ""What changed across my Mac, browser, and phone since I left—only tell me changes that matter, and don't read the private contents back to me?""
- **useful because:** The owner needs a private state delta, not a noisy event digest: a new email, changed document, logged-out session, calendar alteration, or browser transaction can matter even when no job was running. Today each surface can be inspected, but nothing creates one consent-bounded before/after view across them.
- **path:** pendant → relay → mac → browser → iOS → dashboard
- **model tier:** background state-diff model; realtime only to answer a follow-up by voice
- **latency:** 10 seconds for a bounded multi-surface diff; incremental updates under 30 seconds.
- **cost:** $0.02–$0.10 per invocation, dominated by local OCR/structured extraction; raw page and phone contents stay on-device.
- **security:** This is inherently cross-account and cross-device. Take explicit scope and time-window consent, compute redacted field-level hashes locally, suppress secrets and message bodies, and require confirmation before opening or reading sensitive changes aloud.
- **missing:** A user-consented snapshot protocol with before/after cursors for Mac apps, browser sessions, and iPhone Mirroring; Local redaction and semantic diffing for structured app state, not screenshots alone; A relay record that stores only claim hashes, source surface, freshness, and revocation—not private bodies

### ""If I say or press cancel, stop every in-flight action everywhere—even if the relay link is down—and prove what was stopped.""
- **useful because:** A remote agent can currently continue after a link interruption because cancellation is a server/Mac concern and the pendant has no authoritative local veto. The owner needs a physical, fail-closed stop that outranks queued Mac, browser, iPhone, and relay work.
- **path:** pendant → relay → mac → browser → iOS → dashboard
- **model tier:** deterministic firmware and relay state machine; no model required for the stop, cheap model only to summarize consequences
- **latency:** Local pendant veto under 100 ms; Mac/browser cancellation under 1 second; reconciliation when connectivity returns.
- **cost:** <$0.005 per invocation; negligible inference cost.
- **security:** A false trigger can abandon a useful task, so use a deliberate long-press or two-signal voice-plus-button policy. The veto must be local, signed, monotonic, and impossible for a queued command to override.
- **missing:** A pendant-persisted epoch/revocation counter that the Mac, relay, browser, and iPhone workers check before every side effect; Cancellation hooks in browser and iOS command runners, not merely job cancellation metadata; A relay protocol that rejects stale work epochs after reconnect and a receipt proving each surface observed the veto

### ""Before you act on a fact about me, check the independent sources and tell me if they disagree—don't silently choose one.""
- **useful because:** The system can currently inject stale machine-derived preferences and can read Calendar, browser, files, and iPhone state, but it has no cross-surface contradiction detector. This would prevent a confident action based on a stale timezone, old tab, cached permission, or conflicting calendar/contact data.
- **path:** pendant → relay → mac → browser → iOS → dashboard
- **model tier:** cheap background classifier for candidate conflicts, deterministic precedence and freshness rules for final verdict; realtime only when the owner asks
- **latency:** Under 3 seconds for known facts; under 10 seconds when fresh app/browser reads are needed.
- **cost:** $0.01–$0.04 per check; most work is local structured reads and hashing.
- **security:** Conflict reports can reveal private app state. Keep raw sources local, expose only the competing claims and provenance labels needed for the decision, and require confirmation before using a disputed fact.
- **missing:** A provenance-aware fact graph that records source origin, observation time, scope, and freshness for every cross-surface claim; Adapters for Calendar, browser session state, iPhone Mirroring, and relay memory that return comparable claims; A policy that marks contradictions unknown rather than resolving them by confidence alone


## Changes it proposed to its own stack

### `mac-harness` — Make /observe a mandatory, read-only preflight for every computer-use turn: capture foreground app, secure-input state, inputReachability status, browser tab identity, and timestamp; attach that observation ID to the action ledger and postcondition receipt. Refuse to claim a UI action reached the screen if the preflight is stale, secure input is active, or reachability is unverified.
- **owner gets:** Now that the exact agent has Accessibility and Screen Recording, actions can genuinely reach the screen. The owner gets fewer invisible clicks and can see which app/tab the system actually acted on, instead of trusting a generic 'success'.
- effort: Medium: wire existing /observe output into action ledger and receipt creation; no new permission work.  ·  risk: A stale or overly strict preflight could delay harmless actions. Recover by allowing a user-confirmed retry and recording the reason rather than silently bypassing it.
- cost: Negligible API cost; one local HTTP read per action batch.  ·  latency: Adds roughly 20–100 ms locally.
- security: Improves security by recording focus and secure-input boundaries; never persist screenshots or typed secret text.
- depends on: Keep /observe read-only and timestamped; Mount the existing browser provenance/evidence linkage into action receipts


## What it asked for

_Nothing._
## Its own summary

Round 252 established a materially changed live state: /ops/status, /observe, and /ops/snapshot now show the exact AI Pendant Agent has Accessibility and Screen Recording, verified input reachability, all required automation grants, an online Safari extension, and a reachable relay/Mac bridge. The latest pipeline still truthfully says relay-held, awaitsDevice=true, heard=unknown, provesPlayback=false despite successful 24 kHz TTS. I recorded both facts, informed faculty-action, and recorded/proposed three owner capabilities plus a preflight change: evidence-backed postconditions, grounded current-screen answers, channel-aware fallback when the pendant is unavailable, and /observe-attached action receipts.

**Biggest unknown:** Whether the newly listed nrf9160-pendant registry row can ever produce a real device-originated playback event; the system still has no verified pendant playback, and the granted continuity snapshot tool is currently resolver-ambiguous between /ops/snapshot and /pipeline. What I still need is a device playback emitter with job/artifact correlation, a relay-to-Mac evidence capsule bridge, and a selector-specific continuity read (or explicit direct route binding) so perception can answer without guessing.

