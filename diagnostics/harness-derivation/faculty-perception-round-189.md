# Harness derivation — faculty-perception — round 189

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live_mac_observability** — At 2026-08-08T22:29Z the Mac agent is ready: Accessibility and Screen Recording are granted, inputReachability is verified, browser extension is online with 2 tabs and 0 pending commands, relay is reachable with D1 and mac bridge online. Foreground app is loginwindow, not an owner app. No pendant appears in live devices; only home-macbook-bridge is online.
  - evidence: GET /observe and GET /ops/status both returned 200; device discovery lists Safari browser and home-macbook-bridge online but no nRF pendant.

## Capabilities it proposed

### "When I say “what am I looking at?”, tell me what is actually in front of me right now and what the AI can safely infer from it."
- **useful because:** The system currently has verified screen/input access and a live Safari bridge, but no owner-facing perceptual answer that joins the foreground app, browser tab, relay freshness, and recent pipeline state. This would replace guesses with a timestamped answer and explicit unknowns.
- **path:** pendant → mac-planner → mac-vision → browser-extension → relay-realtime → faculty-perception
- **model tier:** Realtime model only for the short spoken synthesis; deterministic observation and confidence scoring should run on the Mac/relay without an LLM.
- **latency:** Under 2 seconds: parallel observation in <500 ms, optional screenshot/OCR in <1.2 s, spoken answer in the remainder.
- **cost:** Usually near-zero model cost if foreground/tab metadata suffices; one vision call only when the owner asks for visual details, dominating cost.
- **security:** Screen pixels and tab URLs can contain secrets. Never upload a screenshot to the relay by default; keep raw pixels on Mac, redact URLs/tokens, report browser login-wall uncertainty, and require a per-session opt-in for cloud vision.
- **missing:** A single perception aggregator that joins GET /observe, browser state, relay freshness, and pipeline recency; A Mac-local redaction/OCR adapter for screenshot details under the now-verified Screen Recording permission; Pendant registration/heartbeat if the answer must be available away from the Mac

### "When I say “why didn’t that happen?”, give me a causal account—not just a failed status—showing where the request stopped and what evidence supports each step."
- **useful because:** A completed Mac job is not proof of speech or hearing, and a relay-delivered announcement is not proof of playback. This would distinguish permission denial, stale browser command, Mac execution, relay acceptance, audio degradation, and absent pendant evidence in one answer.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement
- **model tier:** Cheap background model or deterministic rule graph builds the causal chain; realtime is used only to phrase the already-grounded result when asked aloud.
- **latency:** For a recent job, <1 second from local cached telemetry; deep lookup across relay and Mac <3 seconds.
- **cost:** Minimal: structured joins and confidence labels dominate; no model call for the common path, small text-model call for ambiguous explanations.
- **security:** Expose only redacted command labels and provenance, never raw shell arguments, page contents, tokens, or screenshots. Treat every “completed” fallback as Mac-completed rather than owner-heard.
- **missing:** A normalized event graph joining job receipts, browser command results, pipeline stages, relay job state, permissions, and device playback events; Firmware emission of the accepted audio_delivery_ack_queue events and relay reader for playback start/finish; A stable cross-surface request ID propagated from voice turn through Mac and browser

### "When I say “keep this for when I’m back,” capture the exact browser evidence, create a resumable task, and later tell me only if it is still actionable and has not already been heard."
- **useful because:** This makes the browser, Mac, relay, and pendant cooperate around a real interruption: a content-addressed capsule preserves what was seen, the Mac tracks the task, the relay survives sleep, and the pendant becomes the return channel. It avoids repeating stale or already-consumed information.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → pendant → faculty-perception → faculty-action
- **model tier:** Background model extracts a short task title and actionability; deterministic capsule hashing, expiry, deduplication, and delivery state require no expensive model.
- **latency:** Capture confirmation under 2 seconds; later return briefing under 1 second from local state, with relay lookup allowed up to 4 seconds.
- **cost:** Low: one small extraction call per save and no call on return unless the capsule changed; storage and browser transport dominate.
- **security:** Use existing redaction and content hashes; never store raw secrets or full authenticated page bodies in relay announcements. Require confirmation before external action, and explicitly label stale/uncapsulated relay reads as unsafe to act on.
- **missing:** A mounted browser provenance route and a relay-to-Mac evidence transport that carries capsuleId/contentHash; A resumable-task record linking capsuleId to job/action and an owner return condition; A device-aware heard/consumed check using the accepted bounded NVS playback ledger, with graceful Mac-only fallback while no pendant is registered

### "Before I rely on you, tell me whether you can currently hear me, understand me, reach the thing I’m asking about, and get the answer back to me—with a single confidence verdict and the specific weak link."
- **useful because:** The owner should not have to discover mid-conversation that the pendant is absent, the browser session is stale, or the relay is unreachable. This is a preflight of the whole human-to-action path, not a generic device-status page.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception
- **model tier:** Deterministic rules and recent telemetry; realtime model only turns the verdict into a brief spoken explanation.
- **latency:** Under 1 second from cached telemetry; up to 3 seconds when a fresh relay/browser heartbeat is necessary.
- **cost:** Effectively no model cost on the normal path; small bounded storage for recent preflight results.
- **security:** Expose capability classes and freshness, not URLs, screen pixels, credentials, or raw audio. Never claim microphone or playback health without a device-originated report.
- **missing:** A unified preflight contract with separate hear, understand, reach, execute, and return channels; Pendant-originated health and playback telemetry when the pendant exists; A freshness policy that marks stale observations unknown rather than treating them as healthy

### "Show me what the system knew at a particular past moment and why it reached the conclusion it did, without pretending that today’s state was true back then."
- **useful because:** When an action, recommendation, or notification is questioned later, the owner needs a time-indexed reconstruction: which browser tab, permissions, relay state, pipeline evidence, and stored facts were actually visible then. Current snapshots cannot answer historical questions safely.
- **path:** relay-realtime → mac-planner → browser-extension → mac-vision → faculty-perception → faculty-judgement
- **model tier:** Background model summarizes an immutable evidence bundle; deterministic timestamp normalization and provenance selection do the substantive work.
- **latency:** Two seconds for a recent event; under ten seconds for a bounded historical reconstruction.
- **cost:** Low-to-moderate storage cost for compact metadata and hashes; model cost only when converting a selected bundle into prose.
- **security:** Persist hashes, labels, and redacted metadata by default. Authenticated page bodies and screenshots remain local and expire; historical views must show retention gaps rather than fill them with current values.
- **missing:** Append-only, bounded observation checkpoints across Mac, browser, relay, and pendant; A clock/provenance contract distinguishing Mac-local time from pendant monotonic time and relay time; A replay reader that labels count-capped or missing history as unavailable

### "Warn me when two parts of your memory or live environment disagree about a fact that could change what you do, and show me which source is authoritative instead of silently choosing one."
- **useful because:** A stale machine-derived preference can be pinned, high-confidence, and injected into every prompt while contradicting live reality. The owner needs conflicts surfaced before they affect schedules, locations, permissions, or external actions.
- **path:** relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement
- **model tier:** Cheap background conflict detector using source provenance, timestamps, scope, and authority rules; realtime only explains a conflict when it affects the current request.
- **latency:** Continuous/background detection within seconds of a new observation; under 1 second when checking a fact during a voice turn.
- **cost:** Very low: structured comparisons over existing facts and snapshots; occasional small model call only for human-readable phrasing.
- **security:** Do not expose hidden memory values unnecessarily. Show the conflicting claims, provenance class, age, and consequence, with sensitive values masked. Never overwrite owner facts automatically.
- **missing:** A normalized claim model shared by memory, machine observations, browser evidence, and relay state; Explicit authority and scope rules for each claim kind; A user-facing resolution workflow that can retire or correct a claim with confirmation

### "What of my screen, browser, voice, files, or memory left this machine recently, and what exact purpose did each transmission serve?"
- **useful because:** The owner currently cannot obtain a complete, trustworthy egress account across relay voice, browser rendering, Mac jobs, and evidence capture. A privacy ledger would make the system auditable rather than asking the owner to trust invisible cross-surface movement.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception
- **model tier:** Deterministic local/relay accounting with a cheap background summarizer; no realtime model unless the owner asks for a spoken explanation.
- **latency:** A current answer in under 2 seconds; historical export under 10 seconds.
- **cost:** Small bounded append-only metadata ledger; negligible model cost. Hashes and byte counts, not payload duplication, dominate storage.
- **security:** The ledger itself can reveal sensitive URLs and destinations, so redact domains or classify them according to owner policy. Keep payloads off the ledger, encrypt local records, and make deletion auditable. It must report unknown egress rather than claim completeness when a subsystem is not instrumented.
- **missing:** A mandatory egress event emitted by relay voice/audio, browser rendering, Mac vision uploads, and evidence capture; A shared data-class taxonomy covering screen pixels, audio, page text, file content, memory facts, and metadata; A tamper-evident local ledger plus a relay receipt for what crossed the device boundary


## Changes it proposed to its own stack

### `integration` — Add a perception-grade event envelope propagated from the initial voice turn through browser command, Mac action, relay job, and (when present) pendant playback. Each envelope carries a UUID, observedAt, source, confidence, redaction class, and terminal evidence class (observed, accepted, executed, delivered-to-socket, physically-played). The aggregator must refuse to collapse stronger claims out of weaker ones and must expose gaps as first-class unknowns.
- **owner gets:** The owner gets an honest answer about what actually happened instead of a green “completed” badge that may only mean the Mac ran a command. Failures become diagnosable and stale browser or relay facts cannot silently become action instructions.
- effort: Medium-high: shared schema, propagation at Mac/relay/browser boundaries, migration adapters for existing jobs, and a small read-only explanation endpoint.  ·  risk: Old jobs lack IDs and evidence classes; adapters must label them legacy/unknown rather than fabricate continuity. A propagation bug could split one request into multiple chains, recovered by deterministic parent IDs and explicit orphan status.
- cost: Negligible storage; modest D1 and local JSON growth bounded by existing retention caps. No per-event LLM cost.  ·  latency: <10 ms for envelope creation; no added model latency. Cross-surface explanation may wait on a bounded 2–4 s relay read.
- security: High benefit if redaction is mandatory before propagation; hashes and labels cross surfaces, raw commands/page text stay local. Requires rejecting envelopes containing credentials or authorization-like fields.
- depends on: A pendant-originated playback event from the accepted audio_delivery_ack_queue work; A stable relay browser-read identifier/content hash and Mac capsule bridge; Mounting browser provenance routes and defining legacy evidence semantics


## What it asked for

_Nothing._
