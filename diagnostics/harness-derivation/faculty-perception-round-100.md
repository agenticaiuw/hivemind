# Harness derivation — faculty-perception — round 100

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-device-registry** — At 2026-08-07T14:30Z, only home-macbook-bridge is online; home-chrome is offline with 0 tabs reported, and cloudflare-contract-test is offline. GET /v1/devices/status is not a route on this agent.
  - evidence: GET /ops/status and GET /browser/status returned home-macbook-bridge online, home-chrome offline, cloudflare-contract-test from device discovery; GET /v1/devices/status returned HTTP 404.
- **mac-observability** — At 2026-08-07T14:30:59Z, the Mac agent is in full-control mode but not ready: Accessibility and Screen Recording are false, inputReachability is failed, and synthesized UI events are not accepted. AppleScript automation grants are present. Browser extension is offline with 10 pending commands.
  - evidence: GET /ops/status and GET /observe: permissions.ready=false, accessibility.trusted=false, screenRecording.granted=false, inputReachability.status=failed, browser.online=false, pendingCommands=10.
- **audio-path-observation** — The most recent completed historical pipeline rendered 24 kHz mono s16le PCM (75,734 bytes, 1,578 ms, no clipped samples) and relay accepted it, but the live pendant is not connected; another historical audio-native input was 15,625 Hz PCM. This is evidence of recorded pipeline behavior, not a live pendant test.
  - evidence: GET /pipeline returned completed TTS event metadata with sampleRate 24000, format s16le, pcmBytes 75734, clippedSamples 0, and a separate nrf9160 audio-native event with sampleRate 15625; live device discovery shows no pendant.

## Capabilities it proposed

### "When my browser or Mac comes back online, tell me what changed in my logged-in pages since the last verified check, with the evidence, and queue a short spoken alert on my pendant; never replay stale commands or submit anything."
- **useful because:** Today the browser is offline with 10 pending commands and the pendant is absent, so queued work can become ambiguous. This would make reconnection truthful: the relay preserves a verified baseline, the browser rechecks rather than blindly replaying, the Mac reconciles evidence, and the wearable eventually delivers one concise alert when available.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → unified
- **model tier:** background for scheduled/reconnection diffing; deterministic hashing and command invalidation first; realtime only if the owner asks follow-up by voice
- **latency:** Reconnection acknowledgment under 2 seconds; page rechecks may take 10–60 seconds and should continue as durable background work.
- **cost:** Usually one cheap background call per changed watch (gpt-4.1-mini), roughly 2k–4k input tokens; unchanged pages use no model. Realtime is not used unless the owner asks.
- **security:** Private authenticated page extracts remain on the Mac/relay and must be scoped per watch with URL/tab/session provenance and retention limits. Never replay a mutation after a disconnect; require owner confirmation for sends, deletes, purchases, or submissions. Pendant audio may expose sensitive summaries to anyone nearby.
- **missing:** A durable watch baseline and reconnect reconciler that can invalidate queued browser commands by session and idempotency key; A relay-side pending-alert queue with deduplication and delivery acknowledgment to a future pendant; Browser extension online/reconnect event with verified tab identity and typed read-only snapshot; A live pendant registration and playback path (currently no pendant is connected)

### "Why didn't that work? Show me the exact timeline from my spoken request through the relay, Mac, browser, and pendant, identify the first point of failure, and tell me what was verified versus merely claimed."
- **useful because:** Today the system can leave contradictory evidence: a browser command may remain queued, a UI action may report success while Accessibility rejects it, and audio may be accepted by the relay although no pendant is present. The owner needs one causal, evidence-backed explanation rather than another optimistic completion sentence. This is a diagnostic capability, not a new action runner or page watcher.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Deterministic event-graph construction and contradiction detection first; use a cheap background model only to phrase the final explanation. Realtime is reserved for a spoken follow-up.
- **latency:** Return an initial failure boundary in under 3 seconds from retained events; deeper reconstruction can run in the background for up to 30 seconds.
- **cost:** No model call for indexing, correlation, or permission/state checks. Approximately 1k–3k background-model input tokens only when the causal chain needs natural-language explanation.
- **security:** Diagnostics may expose private page titles, message metadata, audio timing, and account activity. Keep raw payloads local or encrypted, redact secrets and page contents by default, expose provenance links only to the owner, and apply short retention with explicit deletion. Never infer success from an unverified receipt.
- **missing:** A cross-surface event envelope with globally unique correlation IDs, monotonic sequence numbers, source clock, and observedAt time; A durable causal graph joining pendant audio, relay jobs, Mac jobs, browser commands/results, TTS artifacts, and delivery acknowledgments; Explicit truth states separating requested, accepted, executed, observed, delivered, and acknowledged; Clock-skew measurement and uncertainty intervals across Mac, relay, browser, and future pendant; A redaction/retention policy and owner-facing diagnostic export

### "Did I actually hear the answer? Prove whether this specific reply reached my ears, and if not, resume it once without repeating anything I already heard."
- **useful because:** A relay accepting PCM is not proof that a pendant downloaded or played it, and a playback completion event is not proof the owner heard it. The owner should get a truthful distinction between generated, delivered, played, and acknowledged audio, especially after LTE drops or a device reconnects.
- **path:** relay-realtime → pendant → mac-planner → unified
- **model tier:** Deterministic lifecycle and device acknowledgments; no model needed for status. Use realtime only if the owner asks for a spoken explanation.
- **latency:** Lifecycle status under 1 second when online; offline playback receipt can arrive on reconnect. Resume must begin within 2 seconds after explicit owner request.
- **cost:** Negligible model cost; small relay storage for per-audio segment receipts. Optional low-cost TTS only for a resumed or missing segment.
- **security:** Playback acknowledgments reveal device presence and listening times. Authenticate the device, bind receipts to a one-time audio object and owner session, avoid storing microphone recordings, and require explicit confirmation before replaying sensitive content. Never claim 'heard' from a transport-level receipt.
- **missing:** Pendant firmware playback lifecycle telemetry with segment-level downloaded, decoded, started, paused, completed, and interrupted events; A local owner acknowledgment gesture or voice confirmation that distinguishes heard from merely played; Relay receipt schema with idempotent audio IDs, sequence numbers, and reconnect reconciliation; A resumable audio manifest that can skip acknowledged segments and expire securely; Live pendant registration and an exercised end-to-end test; no pendant is currently connected


## Changes it proposed to its own stack

### `relay` — Add a reconnect reconciliation ledger spanning browser sessions, Mac jobs, relay delivery, and eventual pendant alerts. On extension/bridge reconnect, atomically mark queued commands stale, re-read each watch's authenticated page, compare against the last verified semantic snapshot, attach tab/session/time/source hashes, and emit one deduplicated alert only for meaningful differences. Persist per-item state transitions (queued, invalidated, rechecked, changed, delivered, acknowledged, expired).
- **owner gets:** The owner gets a reliable answer after sleep, travel, or a dropped connection instead of an unexplained queue of old actions or duplicate alerts. It also makes clear when no change was verified, rather than implying the page was checked.
- effort: Medium-high: relay D1 schema/state machine, browser reconnect hook and typed snapshot, Mac reconciliation worker, and pendant alert adapter; test disconnects at every transition.  ·  risk: A reconnect race could double-run a command or miss a change. Recover with idempotency keys, lease expiry, monotonic snapshot versions, and a manual review queue for conflicts. If a page cannot be revalidated, report unknown rather than treating it as unchanged.
- cost: No model cost for hashes/state transitions; one background mini call only when semantic extraction or summarization is needed. Small D1/R2 storage increase per watch and alert.  ·  latency: Reconnect acknowledgment remains immediate; reconciliation is asynchronous, typically seconds per page.
- security: Store only normalized extracts and provenance hashes by default, encrypt sensitive extracts, enforce session ownership, and never retain page text past watch TTL without explicit setting.
- depends on: Browser extension reconnect and verified tab identity; Durable browser watch baseline/semantic extraction; Relay pending-alert deduplication and acknowledgment; A future registered pendant; until then surface alerts in the Mac dashboard


## What it asked for

_Nothing._
