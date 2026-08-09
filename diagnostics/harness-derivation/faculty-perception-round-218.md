# Harness derivation — faculty-perception — round 218

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac permission and surface truth** — GET /ops/snapshot at 2026-08-09T00:26Z reports the exact AI Pendant Agent identity has Accessibility and Screen Recording granted, all listed AppleScript automation grants present, requiredMissing empty, and ready=true. Safari browser extension and Mac bridge are online; no pendant appears in the live device list.
  - evidence: read_continuity_snapshot(include=['relay','pipeline']) resolved to GET /ops/snapshot, HTTP 200; body status.permissions.ready=true, accessibility.trusted=true, screenRecording.granted=true, browser online=true, relay macBridgeOnline=true; discover devices listed only Safari on MacIntel, home-macbook-bridge, cloudflare-contract-test.

## Capabilities it proposed

### "“Is the system actually okay right now, or is one of the devices lying?”"
- **useful because:** The system currently has mutually misleading states: the Mac agent and browser are live, relay registry has no pendant, and a pinned machine-derived timezone fact contradicts the authoritative Mac zone. A perception-only contradiction report would prevent judgement/action from treating stale or inferred state as fact.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified → faculty-perception
- **model tier:** Background/cheap model for correlation; realtime only when the owner asks aloud.
- **latency:** Under 2 seconds for the normal voice answer; 10 seconds for a deeper audit.
- **cost:** ~$0.001–$0.01 per on-demand report; dominated by one compact snapshot, not generation.
- **security:** Read-only. Do not transmit page bodies or secret memory values; return contradiction classes, timestamps, and source provenance. Require confirmation before any proposed repair. The pendant is currently absent, so say 'not observed' rather than 'offline'.
- **missing:** A correlation endpoint that compares the live relay registry, Mac /ops status, browser heartbeat, pipeline freshness, and memory-fact provenance in one bounded response.; A contradiction taxonomy distinguishing absent, stale, inferred, and directly device-reported state.

### "“Continue the thing I was doing before I got interrupted.”"
- **useful because:** Today the collective can report separate jobs, browser tabs, and pipeline runs, but cannot establish which one is the owner's current thread. This would produce one resumable checkpoint: the active tab and visible region, the last successful Mac action and undoability, the last relay turn, and whether the pendant ever confirmed playback—without pretending completion means it was heard.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → unified → faculty-perception → faculty-judgement
- **model tier:** Cheap background model builds and ranks checkpoints; realtime model only asks a disambiguating question when confidence is low.
- **latency:** 2–4 seconds when asked; checkpoint updates should be asynchronous and batched.
- **cost:** ~$0.002–$0.02 per resume request; storage is a bounded few KB per checkpoint.
- **security:** Browser titles/URLs and action details may be sensitive. Keep bodies out of the checkpoint, redact secrets, and show the source and age of each assertion. Never resume or mutate automatically; judgement must ask confirmation for a destructive next step.
- **missing:** A cross-surface checkpoint schema with a stable checkpoint ID and per-field evidence links.; A Mac-side writer that snapshots the current browser session, job receipt, and pipeline stage at interruption boundaries.; A pendant-originated playback field from the accepted audio_delivery_ack_queue, so 'last response' can be marked unheard rather than completed.

### "“For every factual thing you just told me, show me what was observed, when, and whether it could have changed.”"
- **useful because:** A spoken answer currently collapses live device facts, Mac-derived facts, browser readings, and model inference into one voice stream. This would let the owner challenge one sentence and receive its exact evidence, age, hash, and uncertainty instead of a vague citation or a replay of the whole turn.
- **path:** relay-realtime → mac-planner → browser-extension → unified → faculty-perception → faculty-judgement
- **model tier:** Cheap model creates claim/evidence links; realtime model only narrates the requested subset.
- **latency:** Normal answer remains under 1 second; provenance ledgering is asynchronous. A challenge should return in under 3 seconds.
- **cost:** ~$0.001–$0.01 per turn plus bounded local JSON storage; hashing and redaction dominate CPU, not tokens.
- **security:** Never persist raw secrets or full private pages. Store redacted content hashes, source host/path, capture time, and a short withheld/visible excerpt. Revocation must hide expired or revoked evidence while preserving a tombstone. Treat relay browser output as untrusted until a Mac capsule is minted.
- **missing:** A relay-to-Mac claim receipt carrying a turn ID, claim IDs, content hashes, and source timestamps.; A claim-level renderer that distinguishes observed, reported-by-device, inferred, and asserted facts.; A voice command and route to retrieve one claim's evidence without exposing unrelated browser or memory content.

### "“If you misheard me, fix the conversation before doing anything.”"
- **useful because:** The pendant can now measure capture quality locally, but today that verdict does not control the conversational loop. A noisy, clipped, or gap-filled utterance can still become an apparently confident transcription and reach judgement/action. This capability would make the system stop, explain the measurable defect in one short sentence, and request only the missing phrase before any side effect.
- **path:** pendant → relay-realtime → mac-planner → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Realtime model for the repair turn; no background model needed unless repeated degradation requires a summary.
- **latency:** Local reject under 150 ms after utterance end; repair prompt within 1 second; never wait on the relay to reject unusable audio.
- **cost:** Normally one extra short realtime turn only when quality is degraded; roughly $0.002–$0.03 on those turns.
- **security:** A low-quality utterance must never be interpreted as consent. Keep raw audio local unless the owner explicitly permits upload; transmit compact quality metrics and sequence IDs. Require explicit confirmation if the repaired phrase changes a destructive action.
- **missing:** Firmware-to-relay transport for the accepted offline-capture-integrity-sentinel verdict.; A relay policy that gates transcription/action on the verdict and correlates it to the utterance sequence.; A judgement rule that distinguishes 'repeat requested' from 'owner declined'.

### "“When I lose connection, keep my request safe and finish it later—but never act on a guess.”"
- **useful because:** A wearable conversation can outlive LTE, Wi‑Fi, or the Mac bridge. Today an offline request is either lost or risks being reconstructed from incomplete context. This would preserve a bounded, encrypted intent envelope on the pendant, then let the relay and Mac jointly resolve it after reconnect, with an explicit stale-context check before action.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Small local classifier for capture/queue eligibility; background model for resolution after reconnect; realtime only to ask for confirmation.
- **latency:** Queue decision under 200 ms offline; reconnect reconciliation under 5 seconds; no action until provenance and freshness checks pass.
- **cost:** ~$0.005–$0.05 per reconciled request; local storage is a bounded ring, not routine SD writes.
- **security:** Encrypt the envelope at rest and in transit; exclude raw secrets unless the owner explicitly says to retain them. Expire intents after a configurable age, bind them to the capture sequence and firmware session, and require confirmation when browser/page state or facts changed.
- **missing:** A pendant-held encrypted intent envelope and replay-resistant sequence protocol.; A relay endpoint that accepts queued envelopes and returns durable acceptance without claiming execution.; A Mac resolver that joins the envelope to current browser/job/context evidence and emits an explicit stale-context verdict.

### "“Before you send or change anything important, prove that the person, account, and page you are acting on are the ones I meant.”"
- **useful because:** A logged-in browser session can silently be on the wrong tab, account, or stale page, while Mac state and relay context look healthy. Today the system can act with session access but cannot provide a cross-surface identity proof. This would detect mismatches before action and turn them into one precise confirmation question.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Cheap deterministic checks first; background model compares page/account/task identity; realtime model only asks the final confirmation.
- **latency:** Under 2 seconds for normal actions; under 5 seconds for a deeper account/page comparison.
- **cost:** ~$0.002–$0.02 per guarded action; most checks are local hashes and structured metadata.
- **security:** Never read or persist passwords, tokens, or full private pages. Use redacted account labels, origin/URL hashes, tab/session pseudonyms, and freshness timestamps. A mismatch must fail closed; the owner can explicitly override once for that action only.
- **missing:** A browser extension identity attestation containing origin, account pseudonym, tab/session ID, and capture time.; A Mac-to-relay signed context assertion so the relay can verify that the page evidence and requested action belong to the same turn.; A judgement policy defining which actions require identity quorum and how overrides expire.


## Changes it proposed to its own stack

### `integration` — Now that the live Mac snapshot reports Accessibility and Screen Recording granted for com.aipendant.agent, add a startup readiness transition that runs one harmless observe-only computer-use probe, records the binary identity, permission result, and timestamp, and exposes a short-lived 'visual control verified' lease to mac-vision. If the probe fails later, invalidate the lease rather than letting the planner assume readiness.
- **owner gets:** The owner gets reliable visual computer control instead of a green permission badge that may not match the running process. It also makes the newly granted capability usable immediately and makes regressions explainable.
- effort: Small integration change plus one observe-only probe and tests; no new model or hardware.  ·  risk: The probe must not click, type, navigate, or capture sensitive content. If the probe is too strict, visual control may be disabled; recover by falling back to AppleScript/browser actions and re-probing on the next startup.
- cost: Negligible API cost; one local probe per startup.  ·  latency: Adds under 1 second at startup, no per-turn cost.
- security: Improves security by binding readiness to the exact signed app identity and expiring the lease. Do not store screenshots; store only status and timestamp.
- depends on: GET /ops/snapshot; GET /observe; GET /ops/status; mac-vision computer-use loop


## What it asked for

_Nothing._
## Its own summary

Established live truth: the exact AI Pendant Agent identity now has Accessibility and Screen Recording, all required automation permissions are present, browser and Mac bridge are online, and no pendant is registered. Recorded that fact. Proposed three new owner-facing perception capabilities: contradiction radar, cross-surface interruption resume checkpoints, and claim-level spoken evidence replay; also proposed an integration change that turns the newly granted permissions into a verified expiring visual-control lease.

**Biggest unknown:** The pendant remains physically absent from the relay registry, so no current observation can establish pendant connectivity or playback. I still need a real pendant connection/heartbeat and a relay-to-Mac claim receipt path before any answer can honestly assert that the owner heard audio or that relay browser facts have durable provenance.

