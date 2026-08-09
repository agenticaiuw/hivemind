# Harness derivation — faculty-perception — round 136

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live mac perception and permissions** — At 2026-08-08T01:13Z, GET /ops/snapshot reports Mac agent online, browser extension online with Safari tab 1148327 at platform.openai.com Billing overview, accessibility trusted, screen recording granted, all listed automation apps granted, permissions.ready=true, relay reachable with D1 and mac bridge online. No pendant appears in this snapshot/device list.
  - evidence: Authenticated GET /ops/snapshot HTTP 200 response; corroborating GET /ops/status HTTP 200 response.

## Capabilities it proposed

### "Tell me whether a specific thing actually happened — for example, “did the reminder get spoken?”, “did the browser change take effect?”, or “did the pendant hear that?” — and show the independent evidence, contradictions, and what remains unknown."
- **useful because:** The system currently exposes completion-shaped records that can be false evidence: Mac execution, relay socket bytes, and browser command receipts are not the same as owner-visible outcome. A claim-level verdict would stop the mind from confidently acting on a stale or merely inferred success.
- **path:** pendant local telemetry → relay job/announcement state → mac-planner GET /ops/snapshot and GET /pipeline → browser-extension GET /browser/inspections and browser result records
- **model tier:** background for assembling evidence; realtime only when the owner asks during a live turn
- **latency:** Under 2 seconds for existing records; up to 10 seconds if a fresh browser inspection or USB sample is required.
- **cost:** Near-zero API cost for stored telemetry; roughly one cheap model call only when records conflict. The dominant cost is fresh browser/serial observation, not tokens.
- **security:** Must not expose page contents or secrets merely to prove a state. Return source IDs, hashes, timestamps, and redacted excerpts; require explicit confirmation before treating an unknown as success.
- **missing:** A typed claim/evidence join record with contradiction rules; A relay-to-Mac correlation ID for relay browser reads and speech artifacts; A real pendant-originated played/heard event when the pendant exists

### "Is the pendant and its audio bridge physically connected and healthy right now, even if the relay says no device is registered?"
- **useful because:** Today the owner can have a USB-attached nRF9160 and ESP32 that are testable locally while the relay registry remains empty. This answers the real bench question instead of mislabeling an unregistered wearable as absent or offline, and it gives action and judgement a trustworthy transport/session identity.
- **path:** mac-terminal USB serial discovery and read-only serial probes → nRF9160 pendant firmware → ESP32 audio bridge → relay GET /v1/devices/status and Mac bridge heartbeat
- **model tier:** background/cheap deterministic parser; no realtime model needed unless the owner asks for an explanation
- **latency:** 1–3 seconds for port presence and handshake; 15 seconds for a bounded health sample.
- **cost:** No model call for the normal path; one local serial read and one relay status GET. Hardware is already present; no recurring cloud cost.
- **security:** Serial output may contain credentials or audio metadata: redact token-like strings, never upload raw PCM, and require explicit confirmation before firmware flashing or reset. Presence is not proof of wearable-on-body.
- **missing:** A Mac agent read-only serial probe for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A transport-neutral session/boot identifier emitted by both firmware images; A relay endpoint that records USB-local health separately from registered-device online state

### "When did this happen, in one trustworthy timeline, and how certain are you about each timestamp?"
- **useful because:** Events currently mix relay UTC, Mac America/New_York resolution, browser last-seen times, and pendant timestamps that have no timezone. A timeline that preserves uncertainty prevents false ordering — especially “the owner heard it before the action” or “this happened while they were away.”
- **path:** relay event/job timestamps → Mac pipeline, action ledger, and machine timezone → browser heartbeat/inspection timestamps → pendant monotonic/session frames when connected
- **model tier:** deterministic time-normalization first; cheap background model only to explain conflicts
- **latency:** Under 500 ms from stored records; under 3 seconds when a fresh heartbeat is requested.
- **cost:** No model call for normalization; negligible storage for uncertainty intervals and source clocks.
- **security:** Do not infer the owner's physical location from America/New_York; label it as Mac-local resolution only. Preserve raw timestamps for audit but redact unrelated event content.
- **missing:** A clock-observation record for every source (offset, monotonic basis, sampledAt); A pendant session clock handshake; its current zoneless digits must remain unknown rather than borrowed from the Mac; A shared correlation ID carried from voice turn through relay, Mac, browser, and playback telemetry

### "Before you use or repeat something sensitive, tell me every place it will persist, the actual expiry behavior, and the smallest safe way to proceed."
- **useful because:** The owner currently has no single answer to where a spoken capture or browser page excerpt will live. Some stores are count-capped, some are byte-capped, and relay announcement/audio expiry is not actually enforced. This turns hidden retention into an understandable decision at the moment it matters.
- **path:** pendant capture metadata and failure buffer → relay audio, jobs, announcements, and D1 state → Mac audio, pipeline, evidence, and action stores → browser provenance and active-tab state
- **model tier:** Deterministic policy simulator; use a cheap model only to explain the result in plain language.
- **latency:** Under 1 second for known policies; never block on an unavailable device or pretend an advertised TTL is enforcement.
- **cost:** No recurring model cost; a small policy manifest plus read-only route. Occasional background sweep/index cost is bounded by existing storage caps.
- **security:** Do not copy sensitive content into the policy response. Treat retention metadata as security-sensitive, and distinguish 'withheld on read,' 'deleted,' 'never pruned,' and 'unknown.' Any deletion or redaction remains confirmation-gated.
- **missing:** One machine-readable retention/visibility manifest generated from the real code paths; Live policy introspection for relay announcements/audio and Mac stores; A preflight route that joins a proposed artifact's sensitivity class to each destination and retention rule

### "What can you not know right now, and which exact missing observation would make each answer trustworthy?"
- **useful because:** The current system can report healthy-looking Mac, browser, and relay states while lacking a pendant registration, owner-heard evidence, relay-browser provenance, or a comparable pendant clock. The owner needs an explicit boundary of knowledge, not a polished answer that silently fills gaps.
- **path:** faculty-perception over Mac ops snapshot and pipeline → relay registry, job, and announcement state → browser heartbeat/inspection state → pendant and ESP32 telemetry when physically available
- **model tier:** Deterministic blind-spot graph with a cheap model for phrasing; no realtime model required.
- **latency:** Under 2 seconds from current observations; stale or missing sources should be listed immediately, not retried into a false sense of certainty.
- **cost:** Near-zero inference cost; bounded metadata for each unknown and the observation needed to resolve it.
- **security:** Do not reveal secret route details or private page content while explaining a blind spot. Separate 'not observed,' 'observed false,' and 'structurally unobservable'; do not infer physical location from Mac timezone.
- **missing:** A typed negative-observation schema with reason codes (offline, unregistered, expired, permission-limited, no emitter, incomparable clock); Freshness and provenance fields on every cross-surface observation; A registry of resolvers that names the exact future event, route, or device signal that would close each unknown

### "Run a private end-to-end truth test: prove that a known throwaway token can travel from my microphone through the relay and Mac/browser surfaces and back to audio, identifying the first stage that fails without storing the token."
- **useful because:** The owner currently has many independent green lights but no way to distinguish a healthy control plane from a broken audio, transcription, routing, browser, or playback path. A disposable challenge-response test gives a concrete pass/fail boundary without using private speech or trusting completion labels.
- **path:** pendant microphone and speaker when connected → ESP32 audio bridge → relay WebSocket/STT/TTS path → Mac bridge pipeline and browser extension
- **model tier:** Deterministic challenge token and stage verifiers; no expensive model call unless the test must exercise natural-language transcription.
- **latency:** 10 seconds for a full round trip; each stage should report its own timeout and evidence.
- **cost:** One short synthetic audio exchange and bounded telemetry; negligible text-model cost, with optional TTS/voice costs dominating only if enabled.
- **security:** Use a random nonce that is never derived from owner data; do not persist raw audio or transcript, retain only salted token hash and stage timings. Never send the test through a real external action or browser mutation.
- **missing:** A test-mode protocol carrying a nonce and correlation ID across pendant, ESP32, relay, Mac, and browser; Per-stage challenge acknowledgements including capture, transcription, routing, synthesis, transport, and playback; A disposable-result route that automatically expires all test artifacts and reports the first failed boundary


## What it asked for

### `t14-svr6` (tool) — read_usb_device_health
- why: Perception cannot answer whether the physically connected nRF9160 and ESP32 are alive when the relay registry is empty. The owner needs a read-only bench truth that distinguishes USB presence, firmware boot/session, and audio bridge health from LTE registration.

```json
{
  "type": "object",
  "properties": {
    "ports": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": [
          "/dev/cu.usbmodem00096003658",
          "/dev/cu.usbserial-0287A9CA"
        ]
      },
      "minItems": 1,
      "maxItems": 2
    },
    "sample_ms": {
      "type": "integer",
      "minimum": 100,
      "maximum": 5000
    }
  },
  "required": [
    "ports"
  ]
}
```

### `c12-zmft` (context) — continuity snapshot tool resolution
- why: The granted read_continuity_snapshot tool is present in the prompt but its live resolver returned unresolved; I need to know whether this is temporary inventory drift or whether I should use GET /ops/snapshot directly and stop relying on the grant.
- would change: If it is unavailable, I will treat GET /ops/snapshot as the only live aggregate and avoid proposing or asserting continuity coverage from the unresolved tool.

## Its own summary

Fresh discovery established that the Mac agent and Safari bridge are online, Accessibility and Screen Recording are now genuinely granted (permissions.ready=true), relay is reachable with D1, and no pendant appears in the relay/device snapshot. I recorded this as live evidence. I proposed three distinct perception capabilities: claim-level evidence verdicts, a USB-local pendant/bridge health truth (not relay registration), and uncertainty-aware cross-surface timelines. I also queued a read-only USB serial health tool for the two named ports, since the current HTTP surfaces cannot answer that question. The granted read_continuity_snapshot tool itself failed live resolution; I asked the orchestrator whether to treat GET /ops/snapshot as the fallback.

**Biggest unknown:** Whether either physically connected serial chip is currently alive and what firmware/session/audio counters it reports; relay absence cannot answer that. Also unresolved is whether the continuity snapshot grant can be repaired or should be withdrawn.

