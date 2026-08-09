# Harness derivation — faculty-perception — round 239

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac perception surface** — At 2026-08-09T01:58Z the Mac agent is healthy (v0.5.0), Accessibility and Screen Recording are both trusted, all required permissions are ready, browser extension is online with two Safari tabs and zero pending commands, relay is reachable with D1 storage, and no pendant is reported by the live relay payload.
  - evidence: GET /ops/status and GET /health both returned HTTP 200; payload explicitly reports accessibility.trusted=true, screenRecording.granted=true, permissions.ready=true, browser.online=true, pendingCommands=0, relay.reachable=true, store=d1, macBridgeOnline=true. The relay payload contains no pendant registration.

## Capabilities it proposed

### "“What changed on my screens since I last looked?” Return only meaningful changes across the active Safari tab, mirrored iPhone, and Mac windows, with before/after timestamps and a spoken summary."
- **useful because:** The owner often returns to a device after an interruption and needs orientation, not a generic status report. A perceptual delta can reveal a new message, changed web price, completed download, or iPhone state change without rereading whole screens.
- **path:** browser: capture a redacted DOM/accessibility snapshot and tab identity → iOS via Mac mirroring: capture permitted screen/UI state and app identity → Mac: capture frontmost window, filesystem/job receipts, and relevant notification metadata → relay: retain a compact encrypted baseline pointer and deliver a concise alert when a high-value delta appears → faculty-perception: compare structured fields and screenshots locally, classify change significance, and report unknowns
- **model tier:** Use deterministic hashes/diffs and a cheap vision model for layout change; call gpt-5.6-luna only to summarize multiple meaningful deltas into speech. No realtime model unless asked live.
- **latency:** Baseline capture under 1 second; delta query under 3 seconds. Background polling should be event-driven or no faster than once per minute to avoid surveillance-like behavior.
- **cost:** Near-zero for structured diffs; roughly $0.002–$0.02 per visual comparison depending on screenshot size. Storage is bounded to two baselines per surface.
- **security:** Default to local-only baselines, redact message bodies and secrets, require opt-in per surface, pause during sensitive apps, and never send screenshots to the relay by default. The owner must be able to inspect/delete baselines.
- **missing:** A user-visible baseline/delta API with explicit per-surface opt-in; iOS mirroring structured capture and stable app/window identifiers; A local encrypted baseline store with retention and redaction; Significance rules that distinguish a real state change from animation, ads, or clock updates

### "“Can I test the pendant right now, and is this result from real hardware or a simulator?” Give a bench verdict before interpreting any audio or device telemetry."
- **useful because:** The current system can show historical pipeline audio while no pendant is registered, which is dangerously easy to mistake for live hardware behavior. A preflight verdict would save the owner from debugging phantom successes and would make the USB-connected bench genuinely useful today.
- **path:** Mac terminal/bridge: inspect the two known USB serial endpoints, firmware identity, boot/session markers, and bounded UART freshness → relay: compare device registry and websocket/heartbeat freshness, explicitly distinguishing absent, stale, and connected → pendant firmware: emit the offline-reality-beacon frame when connected → audio bridge: report codec mode, packet counters, and whether samples came from live I2S versus a fixture → faculty-perception: return a typed verdict (LIVE_HARDWARE, USB_BENCH_ONLY, SIMULATOR, HISTORICAL_ONLY, or UNKNOWN) with evidence and timestamps
- **model tier:** Deterministic checks and parsers first; use gpt-5.6-luna only to explain a mixed verdict. Never let a language model infer live hardware from old pipeline rows.
- **latency:** 1–3 seconds for a bounded serial and relay preflight; fail closed at 5 seconds. No continuous polling unless the owner starts a test.
- **cost:** No model/API cost for a clean deterministic verdict; under $0.01 when explanation needs the small model. Bounded UART reads are local.
- **security:** Read-only bench access, strict port allowlist, bounded bytes/time, no firmware flashing or shell passthrough, and redact credentials from UART logs. Treat historical captures as non-live and never upload raw serial logs by default.
- **missing:** The granted mac_usb_serial_diagnostics capability must be implemented and exposed to the Mac agent (it currently has no serial route/action); A shared test-run ID joining UART, audio-bridge, pipeline, and relay timestamps; A live-vs-historical field in pipeline/audio records; The nRF9160 is not currently registered, so LIVE_HARDWARE cannot be asserted until it appears

### "“Tell me this only when I can act on it.” Decide whether a new event should interrupt me now by observing my current Mac/browser/iPhone activity, scheduled quiet rules, and whether the pendant/audio path is actually reachable; otherwise queue it with a reason."
- **useful because:** It turns perception into respect for attention: the system stops speaking into a disconnected pendant or interrupting a focused task, while still surfacing urgent items at the first viable moment. The owner gets fewer useless interruptions and fewer silently lost ones.
- **path:** Mac: observe frontmost app/window, active job, permissions, and local quiet-state signals → browser: observe active tab and pending command state without reading page bodies unless needed → iOS via Mac: identify active app/call/navigation state when mirroring is available → relay: hold a bounded, priority-tagged pending item and expose delivery reachability → pendant/audio: use reality-beacon and playback ledger when available; otherwise mark speech unavailable → faculty-perception: classify reachability and interruption cost; faculty-judgement applies the owner's policy
- **model tier:** Deterministic policy and state classification first; use gpt-5.6-luna only to summarize why an item was deferred. Realtime is used only for an urgent live interruption.
- **latency:** Under 500 ms for local eligibility; under 2 seconds when querying relay or iOS. Re-evaluate on focus/route/audio events rather than polling aggressively.
- **cost:** Usually zero model cost; about $0.005–$0.02 for ambiguous multi-surface summaries. Relay storage is a bounded queue.
- **security:** Do not infer sensitive activity from raw screen content; prefer app identity and explicit owner policy. Never silently send messages or disclose notification contents. Urgent exceptions require a policy the owner explicitly sets.
- **missing:** A formal interruption policy with urgency, quiet hours, and deferral/expiry semantics; A reachability contract that distinguishes Mac display, browser, iPhone, relay, and pendant playback; Event hooks for frontmost-app and iPhone state changes; Durable deferred-item IDs and owner-visible reasons for every suppression

### "“At the exact moment you acted, what did you believe, what did you not know, and which screen/device evidence did that belief come from?” Show me a replayable, time-ordered perception record for that decision, not the current state."
- **useful because:** Current state inspection cannot reconstruct why a past action seemed justified after tabs, jobs, permissions, or device connectivity have changed. A frozen perception replay would let the owner audit mistakes, recover lost context, and distinguish stale inputs from reasoning errors without trusting a rewritten history.
- **path:** pendant: attach monotonic boot/session and local sensor/playback frames when present → relay: stamp voice-turn, routing, and delivery observations with server time and causality IDs → Mac: capture the exact context projection, machine state, action ledger preconditions, pipeline stage inputs, and job receipts used at decision time → browser: persist redacted tab identity, capsule/hash, command result, and freshness at the read moment → iOS via Mac: persist redacted app/screen/action evidence with the mirror session identity → faculty-perception: write an append-only, content-addressed perception bundle before judgement/action and serve a replay that explicitly marks missing branches
- **model tier:** Use deterministic capture, hashing, and joins; use gpt-5.6-luna only to explain the replay in the owner's requested level of detail. Never regenerate the historical belief with today's context.
- **latency:** Capture must add under 100 ms to an interaction; replay should load under 2 seconds locally and stream larger bundles on demand.
- **cost:** Small local storage cost (roughly 1–10 KB per decision after redaction and deduplication); negligible API cost except optional natural-language explanation.
- **security:** Keep raw screenshots, page text, phone content, and audio off the relay by default; store redacted hashes and local encrypted pointers, with per-record deletion and secret-field suppression. An append-only log must support revocation/tombstones without pretending the original evidence still exists.
- **missing:** A decision-scoped perception bundle schema with immutable content hashes and explicit unknowns; A pre-decision capture hook shared by relay voice, Mac planner, browser, iOS, and faculty judgement; Local encrypted retention/eviction with owner-visible deletion and redaction records; Stable causality IDs propagated through plan, execute, browser, iOS, pipeline, and optional pendant telemetry

### "“Did this secret ever leave my devices?” Trace one sensitive item across Mac logs, browser commands, relay requests, announcements, audio jobs, and pendant telemetry, and tell me exactly where it was seen, redacted, or cannot be ruled out."
- **useful because:** The owner has no way today to answer the most important privacy question after an AI interaction: whether a secret was merely displayed locally or was copied into a browser, relay prompt, speech output, or durable store. A bounded lineage report would make trust auditable instead of assumed.
- **path:** Mac: scan action ledger, pipeline metadata, browser provenance, evidence capsules, job receipts, and local audio/announcement records using secret-safe fingerprints → browser: inspect command/result/provenance links without exporting page bodies → relay: query request/job/announcement/audio metadata and retention state; never return raw secret text → pendant: report only hashed artifact IDs and playback/download events when connected → faculty-perception: correlate fingerprints and redaction tombstones, classify confirmed exposure vs possible exposure vs ruled out, and state coverage limits
- **model tier:** Deterministic secret fingerprinting, redaction-map inspection, and provenance joins first; use gpt-5.6-luna only to explain a result after the sensitive values have been removed.
- **latency:** Under 5 seconds for a single item; asynchronous for a whole workspace. No raw secret should be sent to the model or relay.
- **cost:** Negligible for local indexed metadata; roughly $0.01 for a natural-language explanation. A bounded local index is the main storage cost.
- **security:** The query itself must not echo or transmit the secret. Require local entry or a device-held hash, reject wildcard scraping, restrict relay responses to metadata, and say “not provable” when a store lacks coverage. Never claim deletion from an unbounded or unswept relay announcement/audio store.
- **missing:** A secret-safe lineage index that stores keyed fingerprints rather than values; Propagation of provenance links from relay voice/browser/routine paths into local evidence and ledger records; Read-only relay exposure reports for payload hashes, destinations, retention, and deletion status; A coverage matrix that distinguishes inspected stores from stores with no observability


## Changes it proposed to its own stack

### `memory` — Add a provenance gate to contextProjection: machine-origin facts of kind preference must never enter the cacheable '## Owner' head unless explicitly promoted by the owner. Keep them in a separately labeled machine-context section with a short freshness/contradiction marker; when a machine-origin preference conflicts with a live machine observation, automatically downgrade it to a warning rather than letting confidence and useCount make it dominate.
- **owner gets:** The owner stops hearing wrong personal settings as if he stated them. In particular, the pinned machine-written America/Chicago preference would no longer override the live America/New_York system zone in every prompt, preventing wrong routine times and date interpretations.
- effort: Small-to-medium: change projection selection and add a provenance/contradiction test; preserve the existing fact rather than deleting it, and expose a one-line repair suggestion.  ·  risk: Some useful machine defaults may disappear from the owner-facing context until promoted. Recovery is straightforward: show the quarantined value and allow explicit promotion; keep audit metadata so no fact is silently lost.
- cost: Negligible runtime/API cost; a few hundred bytes of context when a conflict exists.  ·  latency: No meaningful latency change; one deterministic filter and optional local-zone comparison.
- security: Improves privacy and authority boundaries by preventing machine-derived values from being represented as owner intent.
- depends on: GET /machine-context for live machine authority; GET /memory/projection for current projection behavior; A provenance-aware contextProjection change; no new hardware or permissions required


## What it asked for

_Nothing._
## Its own summary

Fresh discovery completed. Live Mac truth is now stronger: /ops/status and /health are 200; Accessibility, Screen Recording, and all required automation permissions are ready; Safari bridge is online with two tabs and no pending commands; relay is reachable on D1. I recorded three new owner-facing capabilities: screen-change deltas across Mac/browser/iPhone, a bench-vs-simulator hardware preflight verdict, and interruption arbitration based on actual reachability and attention. I also proposed a memory fix preventing machine-origin preferences (notably the stale America/Chicago value) from masquerading as owner intent. One attempted “prove it” capability collided with an existing trust-boundary backlog item and was not restated.

**Biggest unknown:** The nRF9160 pendant is still absent from the relay registry, and no live pendant playback can be asserted. The next genuinely useful missing evidence is a bounded USB serial diagnostic plus a shared test-run ID joining UART, ESP32 audio, Mac pipeline, and relay timestamps; until that exists, pipeline audio remains potentially historical rather than live hardware evidence.

