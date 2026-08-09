# Harness derivation — faculty-perception — round 204

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live cross-surface state at round 204** — The Mac agent is ready with Accessibility and Screen Recording granted; browser extension is online with three Safari tabs and zero pending commands; relay is reachable with the Mac bridge online; no pendant appears in the live device inventory (only home-macbook-bridge online and cloudflare-contract-test offline).
  - evidence: read_continuity_snapshot invoked GET /ops/snapshot at 2026-08-08T23:21Z; discover:devices returned Safari on MacIntel, home-macbook-bridge online, cloudflare-contract-test offline.

## Capabilities it proposed

### "Before you do anything consequential, tell me whether the target, permissions, session, and delivery path are actually valid right now — and stop if any part is only assumed."
- **useful because:** Prevents the most damaging class of failure: acting on a stale tab, revoked session, wrong app, unreachable relay, or a pendant that never acknowledged playback. It turns perception into a hard boundary before judgement/action.
- **path:** browser-extension → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Cheap background/state checks first; realtime only to explain a failed preflight in the owner's voice.
- **latency:** Under 500 ms for cached checks; up to 2 s when a browser snapshot or relay probe is required.
- **cost:** Near-zero model cost for structured checks; one short realtime turn only on failure. Dominant cost is browser/relay round trips.
- **security:** Never expose page contents or secrets in the preflight summary. Browser session identity and permission state leave the device only as redacted booleans. Consequential action still requires owner confirmation when target or scope changed.
- **missing:** A versioned preflight contract consumed by plan/execute; Browser snapshot freshness and target identity bound into the action receipt; A relay-side device/playback truth field rather than socket-write delivery

### "Find contradictions in what you remember about me and what the Mac, browser, relay, and clock say now, then show me exactly which source you trusted and what you refused to infer."
- **useful because:** The system currently injects a pinned machine-authored America/Chicago preference while the Mac is America/New_York. A contradiction auditor would prevent stale machine facts from silently steering schedules, reminders, and spoken answers.
- **path:** faculty-perception → mac-planner → browser-extension → relay-realtime → unified → faculty-judgement
- **model tier:** Background structured comparison; use the realtime tier only to summarize a contradiction the owner asks about.
- **latency:** Run on context refresh in under 1 s; interactive explanation under 3 s.
- **cost:** Low: deterministic normalization and hashes dominate; no model call for ordinary comparisons.
- **security:** Compare provenance and metadata, not private values where possible. Do not rewrite owner facts automatically. Any proposed correction must be explicitly confirmed by the owner.
- **missing:** A provenance-aware contradiction route that returns competing facts plus authority scope; A quarantine state for machine-authored pinned preferences; An origin-aware context projection that marks unresolved contradictions

### "Show me the evidence chain for one answer or action: what the browser displayed, what the Mac did, what the relay accepted, and which links in the chain are missing or stale."
- **useful because:** A claim-level evidence chain is different from a generic activity digest: it lets the owner audit one consequential answer instead of trusting a completed job. It exposes uncapsuled relay reads and distinguishes 'Mac executed' from 'owner heard'.
- **path:** browser-extension → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Deterministic evidence joining and freshness checks; cheap text model only to render the chain in plain language.
- **latency:** Interactive lookup under 2 s; archival indexing asynchronous.
- **cost:** Low model cost. Storage and hashing are the main costs; cap bodies and retain digests/tombstones, not secrets.
- **security:** Redact secrets before persistence; content-address claims; enforce capsule revocation and per-surface authorization. Never claim hearing from relay bytes or Mac completion.
- **missing:** Relay browser-read ID/hash transport into the Mac capsule store; Mounted browser provenance routes and an end-to-end correlation ID on voice, browser, job, and playback events; A defined device_playback emitter when a pendant exists

### "When I move from my Mac to the pendant, continue the exact task where I left off: tell me what is open, what I was trying to do, what remains uncertain, and let me resume without repeating myself."
- **useful because:** Today the surfaces share fragments but not a trustworthy task handoff. The owner should be able to leave the desk and resume from the wearable with the same target, evidence, pending decision, and safe next step—not a generic summary.
- **path:** mac-planner → mac-vision → browser-extension → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Cheap structured state extraction and deterministic joins; realtime only to speak the compact handoff on the pendant.
- **latency:** Capture a handoff in under 1 second when the owner says 'pause this'; resume speech within 2 seconds.
- **cost:** Low model cost; storage and browser snapshot capture dominate. Keep only redacted state, hashes, and bounded screenshots/evidence references.
- **security:** Handoff must bind to the owner's authenticated session and redact secrets, private page text, and credentials. Resuming a consequential action requires confirmation if the target changed.
- **missing:** A cross-surface task-handoff object with immutable target/evidence references and unresolved assumptions; Pendant registration and bidirectional event delivery; A Mac/browser hook that snapshots resumable state at pause and validates it at resume

### "Keep me from accidentally exposing private information: detect when a browser page, Mac screen, or pendant utterance contains a secret or sensitive context, then prevent it from being spoken, copied, uploaded, or used in an action unless I explicitly approve."
- **useful because:** The current system can join logged-in browser sessions, Mac automation, relay speech, and durable evidence, but the owner has no cross-surface privacy boundary. A single mistaken read-aloud or browser submission could leak credentials, financial data, or a private conversation.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Deterministic local classifiers and secret detectors first; a small background model for ambiguous classification; realtime only for an immediate spoken warning.
- **latency:** Under 150 ms for known secret patterns; under 1 second for screen/browser classification; never block ordinary non-sensitive interaction.
- **cost:** Low model cost with local pattern matching and bounded redacted previews. Screen analysis is the dominant compute cost.
- **security:** Classification and redaction should happen locally before relay upload. Store only hashes and labels by default. Explicit approval must be scoped to one destination, one field, and one action, then expire.
- **missing:** A shared sensitivity taxonomy and policy engine across browser, Mac vision, relay speech, and evidence storage; Pre-upload redaction hooks for screenshots, page reads, speech transcripts, and action parameters; A pendant-visible approval protocol that works offline and records the owner's decision

### "After you act across my browser, Mac, relay, and pendant, show me a causal undo plan—not just the last command—so I can reverse the whole change safely and know what cannot be undone."
- **useful because:** Existing job undo is local and step-oriented. Real tasks span browser mutations, files, messages, reminders, and spoken commitments; the owner needs dependency-aware recovery before an accidental chain becomes permanent.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Deterministic action graph and inverse-operation registry; use a slower model only to explain tradeoffs when inverses conflict.
- **latency:** Preview under 1 second for a recent task; execute each reversible step with receipt confirmation.
- **cost:** Low model cost; bounded ledger growth and occasional browser/Mac verification dominate.
- **security:** Never invent an inverse. Mark irreversible effects explicitly, require confirmation for destructive reversal, and preserve an append-only audit record without message/page secrets.
- **missing:** A cross-surface causal action graph linking browser command IDs, Mac job IDs, relay jobs, and owner confirmations; Inverse operations for common browser and Mac mutations, with pre/post state hashes; A dependency-aware planner that refuses unsafe reversal order


## Changes it proposed to its own stack

### `integration` — Add a signed, short-lived reality token produced by faculty-perception. It binds browser tab/session fingerprint, Mac permission readiness, relay reachability, target capsule hash, and freshness timestamps; /plan and /execute must reject or downgrade any action whose token is absent, expired, or mismatched.
- **owner gets:** The assistant stops acting on yesterday's page or a different logged-in account and can explain precisely what changed instead of failing silently.
- effort: Medium: token schema, joiners, and enforcement in planner/action plus tests for stale and mismatched surfaces.  ·  risk: A false stale result may delay an action; recovery is a fresh read and re-plan. Never make the token a bypass around owner confirmation.
- cost: Negligible storage and hashing; no per-action model call.  ·  latency: Adds roughly 100–400 ms for cached checks, up to one browser read when stale.
- security: Improves security by binding actions to observed targets; signed token must contain pseudonyms and hashes, never page secrets.
- depends on: Browser provenance route mounting; Relay browser-read ID/hash bridge; Defined freshness policy for each surface

### `memory` — Introduce a contradiction quarantine for machine-originated pinned facts: when a live authoritative source disagrees, keep the fact immutable but exclude it from the default context projection until the owner reviews it; record the competing source, scope, and observed timestamps.
- **owner gets:** A stale machine preference can no longer silently steer every reminder and schedule while still remaining available for audit and explicit recovery.
- effort: Small-to-medium: projection filter, review endpoint/UI, and a deterministic authority matrix; no new fact schema required.  ·  risk: An over-aggressive filter could hide a legitimate preference. Recovery is one-click restore or explicit owner confirmation; owner-origin facts remain untouched.
- cost: Minimal; bounded metadata only.  ·  latency: Negligible projection overhead.
- security: Reduces unauthorized inference and makes provenance visible; do not transmit raw competing values to relay unless needed.
- depends on: Provenance-aware contradiction detector; Owner review surface; Authority scopes for machine, browser, relay, and owner facts


## What it asked for

_Nothing._
