# Harness derivation — faculty-judgement — round 154

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live surface readiness** — As of the live /ops/status probe, Mac Accessibility and Screen Recording are trusted, browser extension is online with 9 tabs, relay is reachable with D1, and macBridgeOnline is true. This supersedes the older denied snapshot for current planning, but does not establish LTE pendant registration.
  - evidence: GET /ops/status returned permissions.accessibility.trusted=true, screenRecording.granted=true, browser.online=true, relay.reachable=true/store=d1, macBridgeOnline=true.

## Capabilities it proposed

### "“Run a safety drill: prove that if I hit the pendant’s stop latch, the currently running voice, Mac job, browser command, and queued audio all stop—and show me any surface that failed.”"
- **useful because:** This is the most important thing the hive could do: an emergency control is only real if cancellation crosses every body. Today the pendant is physically testable over USB, while /ops/status reports the Mac, relay, and browser online; a synthetic, reversible drill can measure propagation instead of trusting code paths. It gives the owner a single honest answer before relying on the latch in an emergency.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** background for preparing the synthetic drill and correlating receipts; realtime only to narrate the owner’s physical press and final result
- **latency:** Preparation under 5 seconds; after the owner presses the physical stop button, surface ACKs and a spoken verdict within 3 seconds, with late ACKs tracked for 30 seconds
- **cost:** Usually <$0.01: deterministic orchestration and existing telemetry dominate; no model call unless the owner asks for explanation
- **security:** Must use a sandboxed synthetic job with no external side effect, never cancel the owner’s real work, and require an explicit spoken/dashboard confirmation before starting. The pendant receives only an opaque drill token. USB serial is the current transport; LTE registration is not assumed.
- **missing:** A test-mode cancellation envelope accepted by relay, Mac, browser runner, and pendant without touching real jobs; A drill coordinator that joins the existing relay job, Mac job, browser command, pipeline, and pendant stop-token IDs; A dashboard timeline and timeout verdict for each ACK; hardware-in-the-loop USB serial harness for the connected nRF9160

### "“Did I actually hear that briefing? Give me a per-item delivery receipt, not just ‘the job succeeded’.”"
- **useful because:** A generated audio receipt is not evidence that the owner heard anything: downloads can fail, playback can be interrupted, or the wrong artifact can be played. This closes the loop from relay generation through Mac pipeline, pendant download, playback start, finish, and interruption, so the owner can ask which headlines were truly heard and safely replay only the missing ones.
- **path:** relay → mac → pendant → dashboard
- **model tier:** background deterministic reconciliation; realtime only for a spoken one-sentence answer when asked
- **latency:** ACK ingestion is sub-second when connected; offline ACK replay reconciles within 5 seconds of reconnect; a receipt query under 1 second
- **cost:** Near-zero model cost; storage and authenticated event ingestion dominate, with at most a cheap summarization call for a human-readable discrepancy explanation
- **security:** Events must be authenticated to a device session, idempotent by event ID and monotonic sequence, and carry opaque artifact IDs rather than transcript/audio. Do not claim ‘heard’ from downloaded alone; distinguish downloaded, started, finished, interrupted, checksum error, and no-audio.
- **missing:** A durable per-briefing-item artifact manifest linking source item IDs to audio artifact IDs; Relay/D1 storage and query routes for pendant delivery events, including offline replay and duplicate suppression; A UI and spoken vocabulary that reports ‘played through’ versus ‘delivered but not heard’

### "“Before you send or speak anything, show me exactly what crosses each boundary—relay, browser tab, Mac app, and pendant—and let me approve only the redacted version.”"
- **useful because:** The current redaction classifier and outbound-origin checks operate in separate paths, and pendantSpeech can speak text without the briefing redaction gate. The owner needs a concrete, itemized data-flow preview: destination, fields, sensitivity classification, masking applied, retention, and the exact policy rule. This makes privacy a decision the owner can inspect rather than an invisible hope, especially when browser sessions and third-party TTS are involved.
- **path:** dashboard → relay → mac → browser → pendant
- **model tier:** deterministic policy/data-flow evaluation first; use the cheaper background model only to explain a blocked field in plain language; realtime only to answer a short approval prompt
- **latency:** Preview in under 500 ms for known payloads; approval must remain valid for at most 2 minutes and be invalidated if the payload, destination, or source evidence changes
- **cost:** <$0.005 per preview; hashing, classification, and policy evaluation dominate; no model needed for ordinary payloads
- **security:** Default fail-closed: no raw secrets or unclassified text leave the Mac, and spoken output must be treated as a public recipient unless the owner explicitly changes policy. The preview itself must not leak the withheld value; include hashes/lengths and reversible redaction samples only. Bind approval to a content hash, destination, policy version, and expiry; require physical approval for external side effects.
- **missing:** A single data-flow manifest schema shared by redaction, httpPolicy, originFanOut, browser sessions, relay context handoff, TTS, and pendant speech; A real enforcement hook in local-agent/pendantSpeech.js and audioBrief.js, not only briefingTriage.redactForDelivery; Owner-editable destination-to-data-class policy with named rules and audit receipts; ship conservative defaults without inventing the owner’s trusted allowlist; A preview/approval route that revalidates the content hash and provenance immediately before transmission

### "“Let me trial a new routine or interruption policy for a week without it acting on my real life, then tell me whether it helped.”"
- **useful because:** The owner should be able to experiment with quiet hours, briefing frequency, browser watches, and reminders without silently creating or changing real commitments. A shadow mode would replay real observations against a proposed policy, predict what would have been spoken or deferred, and compare that with the owner’s explicit feedback before activation.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** background deterministic simulation over recorded events; use a cheap model only to summarize patterns; realtime is unnecessary except for an explicit start/stop command
- **latency:** Starting a trial under 2 seconds; daily simulation under 10 seconds; weekly report under 30 seconds or generated asynchronously
- **cost:** Usually <$0.05 per week; event storage and simulation dominate, with optional summarization as the only model cost
- **security:** Shadow mode must be read-only: no reminders, browser mutations, external messages, or pendant interruptions. Raw content should remain local where possible; retain only event metadata, policy decisions, and owner feedback. The trial must have an explicit expiry and be visibly labeled as simulation.
- **missing:** A durable shadow-trial store with policy version, start/end, observations, simulated decisions, and owner ratings; A replay adapter for routines, page watches, briefing triage, attention arbitration, and audio delivery without invoking mutation paths; A dashboard comparison of current versus proposed policy, including false suppressions and unwanted interruptions; A safe way for the owner to promote a tested policy atomically after review

### "“At the end of the day, tell me what actually derailed me, which interruptions helped, and what one change would make tomorrow calmer.”"
- **useful because:** The system currently records jobs, browser activity, pipeline events, briefings, and some policy decisions, but leaves the owner to infer causality. A daily causal retrospective would connect interruptions to subsequent task abandonment, successful completion, replayed audio, and owner corrections—without pretending correlation is proof—and recommend one reversible change rather than another endless dashboard.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Background model over deterministic event joins and rule-based causal candidates; realtime only when the owner asks follow-up questions
- **latency:** Generated asynchronously after the owner’s local evening boundary; spoken summary available in under 5 seconds when requested
- **cost:** <$0.10 per daily report; event joining is local/cheap and the background summary is the dominant cost
- **security:** Keep raw mail, page bodies, audio, and credentials out of the report prompt. Use redacted event IDs and short, owner-visible evidence links. Clearly label correlation, allow deletion of the report, and never automatically change routines or send feedback externally.
- **missing:** A durable cross-surface event join keyed to one interaction or attention decision rather than unrelated job namespaces; A definition of outcome signals such as task completion, abandonment, replay, interruption dismissal, and owner correction; An owner-facing causal report with confidence, counterexamples, and one-click reversible recommendations; Retention and deletion propagation for the derived report across Mac and relay


## Changes it proposed to its own stack

### `hardware` — Add an independent capacitive wear/contact sensor and a hard audio-output inhibit line to the pendant, with firmware exposing only a coarse worn/not-worn state and an authenticated state transition. When not worn, private or unapproved speech is electrically blocked before the ESP32 audio bridge; the Mac and relay must treat stale or absent wear state as not-worn.
- **owner gets:** The pendant should not read a private message aloud into a room merely because it was set down, handed to someone, or left near other people. This is a physical recipient check that remains effective during a dropped link or a compromised software session.
- effort: New board revision, electrode/contact mechanism, low-power sensor driver, fail-safe audio inhibit, signed state telemetry, and enclosure testing. Prototype with a USB-connected development board before layout.  ·  risk: False not-worn readings defer useful speech; false worn readings must fail closed by requiring a fresh authenticated transition. Recovery is automatic after a stable contact interval. It must never be used to infer the owner’s location or identity.
- cost: Roughly $2–8 in components and PCB/enclosure changes; negligible average power if duty-cycled, with a brief sensor wake on playback.  ·  latency: About 100–500 ms to establish stable contact before allowing private playback; public status can remain immediate.
- security: Improves physical disclosure resistance. Do not transmit raw capacitance or body measurements; expose only signed coarse state and epoch.
- depends on: A policy that distinguishes public-safe speech from private/unapproved speech; A fail-closed audio gate in the nRF9160/ESP32 path; A replay-resistant wear-state transition counter


## What it asked for

_Nothing._
