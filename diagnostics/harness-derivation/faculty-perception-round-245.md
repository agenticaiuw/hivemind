# Harness derivation — faculty-perception — round 245

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **current Mac observability and permissions** — The live Mac agent is ready: Accessibility and Screen Recording are both granted, all required permissions are present, the browser extension is online with one Safari tab, and the relay is reachable with the Mac bridge online. The registered nrf9160-pendant remains offline, so pendant-originated health/playback cannot currently be verified.
  - evidence: GET /ops/status returned HTTP 200 at 2026-08-09T03:13Z: permissions.ready=true, accessibility.trusted=true, screenRecording.granted=true, browserExtension.online=true, relay.reachable=true, relay.payload.macBridgeOnline=true; discover(devices) reports nrf9160-pendant offline.

## Capabilities it proposed

### ""While I was away, tell me not just what happened but which facts disagree, what caused each outcome, and what I can safely resume.""
- **useful because:** This is the highest-value perception capability: it turns scattered Mac, browser, relay, and future pendant traces into a causal, uncertainty-labeled account instead of a misleading list of 'completed' jobs. It explicitly distinguishes socket delivery, Mac execution, browser mutation, and physical playback, and calls out gaps rather than inventing success.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** background model for reconstruction; realtime only to answer the owner's follow-up question
- **latency:** 2-5 seconds for a bounded 24-hour reconstruction; return partial results immediately when one surface is offline
- **cost:** Low-to-moderate per request; dominated by one background synthesis over capped event metadata, not audio or page bodies
- **security:** Export only redacted event metadata and capsule hashes by default; never include browser secrets or raw page text unless the owner asks. Resume recommendations require confirmation when an action was interrupted or physical playback is unknown.
- **missing:** A causal event schema with stable correlation IDs spanning relay job, pipeline run, browser command, action-ledger step, evidence capsule, and (when present) pendant playback record; Relay-side provenance IDs/content hashes for read_web_page; A real pendant-originated playback/consumption event (the accepted audio_delivery_ack_queue); A monotonic clock-offset estimate between pendant, Mac, and relay

### ""Before you let me act on something I read in Safari, prove that the page I saw is the page you are about to change, and tell me exactly what changed.""
- **useful because:** Prevents the most dangerous class of browser mistakes: acting on stale, redirected, logged-out, or changed content. The browser supplies the live session, the Mac supplies the action ledger and undo state, and the relay supplies a durable job boundary; perception can block or downgrade claims when the evidence does not match.
- **path:** browser → mac → relay → dashboard
- **model tier:** background model for comparison and explanation; deterministic hashes and URL/session checks first, model only for a human-readable discrepancy summary
- **latency:** Under 1 second for hash/session checks; under 3 seconds for a discrepancy explanation
- **cost:** Very low; mostly local hashing and bounded metadata, with occasional small background-model call
- **security:** Hash redacted DOM/text regions, never transmit passwords or secret fields. Require explicit confirmation for destructive mutations or when the tab/session identity changed. Preserve only digests and a short redacted claim.
- **missing:** Mount the existing browserProvenance routes and connect them to every browser result, not only the currently reachable Mac computer-use path; A relay read contract returning a stable request ID and content hash; A preflight compare route that atomically snapshots the live tab immediately before mutation; A hard policy hook in faculty-action that refuses mutation on capsule mismatch rather than merely warning

### ""Can I trust this answer right now, or is the system degraded in a way that could make it wrong?""
- **useful because:** The owner currently receives a fluent answer even when the browser session is stale, relay is reachable but the pendant is absent, permissions are partial, or capture quality was unusable. This produces a compact, source-specific trust certificate before action: freshness, authority, link health, capture quality, and what was not observed.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Deterministic health/freshness classifier on the Mac and relay; use a cheap background model only to phrase the explanation. Never let the realtime model infer health from silence.
- **latency:** Under 250 ms from cached telemetry; under 1 second when a live browser and relay probe are required
- **cost:** Near-zero recurring cost; bounded telemetry and hashes, with rare small-model phrasing
- **security:** Expose only health facts, timestamps, and redacted provenance. Do not reveal device credentials, browser URLs containing tokens, or raw microphone content. A red 'unknown' must be preserved rather than converted to green by model confidence.
- **missing:** A unified freshness/authority contract that marks each claim as observed, inferred, stale, or unavailable; The accepted offline-reality-beacon and offline-capture-integrity-sentinel wired into relay and Mac claim gating; A device heartbeat path that reflects the pendant's actual health (the current registry absence is not equivalent to offline); A policy in faculty-judgement that requires this certificate before high-impact actions

### ""Did this request happen twice anywhere, or did one retry only look like a duplicate? Show me every execution branch before I act again.""
- **useful because:** Retries can cross the relay, Mac bridge, browser extension, and pendant without sharing a single execution identity. This capability detects duplicate-intent forks before they create duplicate purchases, messages, edits, or reminders, and distinguishes a harmless replay from two real side effects.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Deterministic correlation and idempotency analysis first; a cheap background model explains ambiguous branches. Realtime is only for the owner's follow-up.
- **latency:** Under 500 ms for recent requests; under 3 seconds for a historical search across bounded ledgers
- **cost:** Low; metadata joins and hashes dominate, with occasional small-model explanation
- **security:** Hash intent and target identifiers rather than exposing private content. Never claim uniqueness when a surface was offline or its retention boundary was crossed. Require confirmation before replaying an unresolved branch.
- **missing:** A hive-wide intent UUID propagated unchanged from pendant utterance through relay, Mac job, browser command, and action ledger; An idempotency registry with target-scoped effect fingerprints and explicit retry/branch edges; Browser and pendant emitters that report accepted, started, committed, and unknown states; A dashboard view that shows parallel branches without collapsing them into one completed status

### ""Put the whole hive into privacy mode now, and prove that no microphone, browser page, screen image, or spoken response is being captured or retained.""
- **useful because:** Today privacy is inferred from separate settings and best-effort behavior. A coordinated, owner-visible privacy mode would make a strong promise across the wearable, relay, Mac, and browser: stop ingestion, drain or cancel active work, prevent new captures, and provide an attestation of what was actually stopped versus what was already persisted.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Deterministic control and attestation; no model should decide whether privacy mode succeeded
- **latency:** Acknowledge intent within 250 ms; complete shutdown and signed attestation within 2 seconds where links are live
- **cost:** Negligible runtime cost; engineering cost is protocol and state-machine work
- **security:** Privacy mode must fail closed locally when disconnected, revoke active relay/browser sessions, and clearly disclose already-retained audio, capsules, logs, or announcements. Exit should require explicit owner confirmation. The attestation must be cryptographically signed by each available node and mark unreachable nodes unknown.
- **missing:** A cross-node privacy-mode protocol with monotonic epoch and fail-closed local behavior; Pendant firmware support to mute microphone, stop audio transmission, and queue a signed local state change offline; Relay and Mac cancellation hooks covering realtime sockets, audio capture, browser reads, jobs, and queued announcements; Browser-extension enforcement that blocks new snapshots and reports whether an existing page capture is in flight; A retention receipt listing what was deleted, what remains under policy, and what could not be reached

### ""For anything consequential, give me a tamper-evident proof packet I can inspect later, including what each device independently observed and what it did not see.""
- **useful because:** A fluent answer is not a durable proof. This would create a human-readable, replayable packet for a consequential action or claim: independently signed observations from the pendant, relay, Mac, and browser, content hashes instead of secrets, clock uncertainty, retention limits, and explicit unknowns. The owner could audit a purchase, message, deletion, or automation after the fact without trusting one model's summary.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Deterministic packet assembly, signatures, hashes, and verification; background model may write a concise explanation but cannot alter evidence
- **latency:** Under 1 second to seal a packet after completion; under 2 seconds to render a human-readable audit view
- **cost:** Low per event; storage and cryptographic signing dominate, with no routine model call required
- **security:** Packets must redact secrets and support selective disclosure. Private raw audio, DOM, and screen images stay local unless explicitly exported. Key rotation, clock skew, offline buffering, and compromised-node warnings must be visible; an unsigned or partial packet must never be labeled verified.
- **missing:** Per-node signing keys and a verification-key directory; A shared event envelope with sequence numbers, parent IDs, monotonic timestamps, and clock uncertainty; Pendant firmware emission of signed health, capture, and playback facts; Relay and Mac receipt writers that seal the packet at action boundaries rather than relying on derived completed status; An export/verification UI that can be saved independently of the mutable stores


## What it asked for

_Nothing._
