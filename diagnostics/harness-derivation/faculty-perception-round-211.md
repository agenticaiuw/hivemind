# Harness derivation — faculty-perception — round 211

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-perception-state** — The exact AI Pendant Agent identity now has Accessibility and Screen Recording granted; /ops/snapshot reports permissions.ready=true, requiredMissing=[], vision loop enabled, browser extension online, relay reachable, and no pending browser commands. The relay registry remains inaccessible from the Mac agent at /v1/devices/status; the known device table still has no nRF9160 pendant, so pendant playback remains unobserved.
  - evidence: GET /ops/snapshot returned HTTP 200 at 2026-08-09T00:06Z with accessibility.trusted=true, screenRecording.granted=true, ready=true, and relay payload reachable; GET /v1/devices/status on localhost returned 404 (Mac-agent route, not relay registry).

## Capabilities it proposed

### "Before you act on anything I asked about in a browser, tell me if the page or account state has changed since you read it, and stop if the evidence is stale."
- **useful because:** The system can currently read a page and later act on a different page while presenting the old reading as current. A content hash plus live browser inspection would prevent wrong-account, stale-price, and changed-form mistakes.
- **path:** browser-extension → mac-planner → faculty-perception → faculty-judgement → faculty-action → relay-realtime
- **model tier:** background for hashing and comparison; realtime only to explain a mismatch
- **latency:** Under 500 ms when an action is about to run; no model call for an unchanged hash
- **cost:** Usually <$0.001 per check; dominated by one browser inspection, not tokens
- **security:** Hashes and URLs leave the Mac only if needed for a relay-mediated action; never transmit page bodies or form values. Require explicit confirmation when the target changed, permissions changed, or the account identity is uncertain.
- **missing:** A relay-returned stable read identifier and content hash for cloud browser reads; A pre-action guard in faculty-action that compares the current browser evidence capsule to the action target; Mount browser provenance routes so the comparison is durable

### "When I come back, give me a short, confidence-labeled account of what actually happened while I was away, separating seen, delivered, played, and merely planned work."
- **useful because:** The current continuity data conflates Mac completion with owner-heard completion, while browser and relay events have different retention. This would make absence recovery honest instead of claiming that completed jobs were heard.
- **path:** relay-realtime → faculty-perception → mac-planner → browser-extension → faculty-judgement → faculty-action
- **model tier:** background model assembles the digest; realtime model only answers follow-up questions
- **latency:** First spoken summary in 2 seconds from the snapshot; deeper provenance loaded on demand
- **cost:** <$0.01 per return, dominated by summarization; no cost when nothing changed
- **security:** Only event metadata and redacted titles should be spoken or synced. Never expose browser bodies, secrets, or stale announcements. Label coverage gaps and retention limits in the output.
- **missing:** A device-originated played/interrupted event reader tied to the accepted audio_delivery_ack_queue; A single chronological join key across browser commands, Mac jobs, relay jobs, and pipeline runs; A policy that marks the digest best-effort when sources are capped or missing

### "Run a bench test that proves an audio response was captured, sent, decoded, and physically played, then show me the exact first failing stage instead of saying completed."
- **useful because:** The pendant is absent from the registry today, but the hardware source and Mac USB bench are real. A single test would turn firmware work into measurable evidence and catch regressions that relay completion currently hides.
- **path:** mac-terminal → mac-planner → relay-realtime → faculty-perception → faculty-judgement → pendant
- **model tier:** background model interprets bounded logs and metrics; no realtime model needed
- **latency:** A 30-60 second bench run, with a result within 3 seconds of capture completion
- **cost:** <$0.02 per run; mostly local shell and relay traffic, not model inference
- **security:** USB reads are restricted to the two known bench ports and bounded byte/time budgets; audio fixtures are synthetic by default. Do not upload raw microphone audio; upload counters, sequence numbers, hashes, and stage timestamps only.
- **missing:** Implement the granted bounded USB serial reader on the Mac; A test fixture that drives the nRF9160 and ESP32 bridge and correlates offline-reality-beacon with offline-capture-integrity-sentinel; A relay test receipt that joins pipeline stages to audio_delivery_ack_queue events

### "If I ask you to do something on screen, first identify the exact app, window, account, and visible target, then let me hear that compact fingerprint before any irreversible action."
- **useful because:** Accessibility and Screen Recording are now live for the exact agent identity, so the system can finally perceive the UI rather than guessing from focus or stale browser state. A spoken target fingerprint makes destructive actions auditable and catches wrong-window errors.
- **path:** mac-vision → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action → relay-realtime
- **model tier:** realtime only for the short target fingerprint; use the cheaper vision loop for inspection and background OCR
- **latency:** 1-2 seconds for perception; no confirmation for reversible actions, explicit confirmation for send/delete/purchase
- **cost:** <$0.02 for a normal inspection; screenshots/OCR dominate, with no call when AppleScript identifies the target exactly
- **security:** Screenshots stay on the Mac and are redacted before any relay use. Never read password fields or hidden windows. Confirmation must bind to the fingerprint and expire if the window changes.
- **missing:** Wire the now-ready Screen Recording and Accessibility permissions into the vision loop; A target-fingerprint schema shared by browser commands and Mac action receipts; A confirmation token invalidated by focus, URL, account, or screenshot-hash changes

### "Tell me before a firmware or relay update makes my audio worse: compare the new build against the last known-good hardware run and refuse rollout when codec CPU, drops, alias rejection, or playback acknowledgements regress."
- **useful because:** The audio path is now excellent by measured criteria, but those numbers can silently regress in a later build. A cross-node release gate protects the owner's hearing instead of relying on a green software test.
- **path:** mac-terminal → pendant → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** background model summarizes benchmark deltas; deterministic thresholds make the go/no-go decision
- **latency:** Under 2 minutes for a USB bench run; block promotion immediately on a failed threshold
- **cost:** <$0.05 per candidate build; local hardware tests dominate
- **security:** Use synthetic audio and counters only; do not upload microphone recordings. Sign the firmware/build ID and benchmark receipt so a stale result cannot authorize deployment.
- **missing:** A persistent signed baseline receipt store for the measured 24 kHz criteria; The bounded USB serial reader and automated fixture for both physically connected chips; A deployment gate that consumes audio_delivery_ack_queue playback outcomes, not relay byte delivery

### "Let me say “keep this on my Mac,” and have the system enforce that boundary end to end: detect secrets or private page regions locally, prevent them from reaching the relay or model, and tell me exactly what was withheld when the task finishes."
- **useful because:** Today the browser, Mac, relay, and wearable can collaborate, but the owner cannot express a per-task data-residency boundary that is technically enforced across all four. This would make powerful automation safe for banking, health, work, and private messages rather than merely asking the model to be careful.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** A deterministic local redaction/classification engine makes the boundary decision; use a cheaper background model only to summarize withheld fields. Never send the sensitive content to the expensive realtime tier.
- **latency:** Under 150 ms for local classification on each browser result; under 1 second to produce a withheld-fields receipt. Block rather than wait when the classifier is uncertain.
- **cost:** Typically below $0.005 per task; local classification dominates and relay inference is reduced because less content leaves the Mac.
- **security:** This must fail closed: no screenshot, DOM text, clipboard, audio transcript, or action parameter crosses the boundary unless explicitly allowed. Keep only salted region fingerprints and category/count metadata locally; require confirmation to widen scope. The classifier itself must not log raw sensitive values.
- **missing:** A task-scoped residency policy and capability token propagated from voice turn through browser command, Mac action, relay job, and receipt; A local preflight interceptor for screenshots, DOM extracts, clipboard, transcripts, and outbound tool arguments; A relay-side policy verifier that rejects payloads lacking an allowed residency token rather than trusting client claims; A compact owner-readable withheld-content receipt with deterministic reasons and revocation support


## Changes it proposed to its own stack

### `context` — Make every projected machine fact carry an authority-and-freshness envelope into judgement: source origin, observedAt, expiresAt, and whether it is a live measurement or a pinned preference. Reject machine-derived preferences that contradict a newer local measurement instead of injecting them into the Owner head.
- **owner gets:** The owner should never receive actions based on a stale machine claim such as the pinned America/Chicago timezone when the Mac is actually America/New_York. Contradictions would become visible and self-correcting without deleting the owner's data.
- effort: Medium: projection metadata, contradiction detector, and a judgement-side refusal path.  ·  risk: Some familiar commands become clarification questions until the conflict is resolved; recover by showing both values and their provenance.
- cost: Negligible runtime cost; one small metadata block per projection.  ·  latency: Under 50 ms locally; no model call for agreeing facts.
- security: Improves privacy by preventing broad projection of low-authority facts; preserves secrets and does not copy values to the relay.
- depends on: GET /memory/projection; GET /machine-context; GET /ops/snapshot


## What it asked for

_Nothing._
## Its own summary

Established a new live fact: the exact AI Pendant Agent identity now has Accessibility and Screen Recording, with permissions.ready=true, vision loop enabled, browser extension online, relay reachable, and zero pending browser commands. The nRF9160 pendant is still absent from the Mac-visible/known registry, so physical playback remains unknown. Recorded proposals for authority-aware context projection, spoken UI target fingerprints, and regression-gated audio releases; also submitted cross-surface proposals for stale browser evidence, confidence-labeled away summaries, and a hardware bench proof path (the recorder flagged those as close to existing backlog items, so they should not be repeated).

**Biggest unknown:** The system still cannot prove pendant playback or run the USB bench workflow: it needs the bounded serial reader/fixture and the relay-side consumer of the already-accepted audio_delivery_ack_queue. It also needs a relay-to-Mac provenance bridge for cloud browser reads; current Mac evidence capsules do not cover relay-service reads.

