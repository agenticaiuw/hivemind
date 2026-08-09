# Harness derivation — faculty-action — round 269

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I missed the last answer—let me replay just that answer.” A clockwise turn on the pendant’s future wheel should replay the most recent complete response, even if the cellular link dropped after delivery."
- **useful because:** The pendant is the only surface present at the moment the owner misses speech. This handles ordinary human interruption, not just failed downloads: it uses the already-delivered answer, resumes from a precise cursor, and avoids asking the owner to repeat the entire request.
- **path:** pendant → relay-realtime → home-macbook-bridge
- **model tier:** Use no model for replay; relay selects the stored artifact and cursor. Use a cheap background model only if the requested answer has expired and a transcript-only compact reconstruction is needed.
- **latency:** Start local replay within 150 ms of the wheel gesture; if the artifact is not local, begin relay retrieval within 500 ms and speak a short haptic/audio status cue.
- **cost:** Near-zero when cached; roughly one storage lookup and no inference. Reconstruction fallback is a small background-model call, dominated by transcript tokens.
- **security:** Persist only opaque response ID, codec/rate, checksum, cursor, expiry, and replay count on the pendant; never persist page contents or secrets. Require a bounded replay count and delete on expiry.
- **missing:** A rotary encoder and second button in the pendant enclosure; Firmware INBOX manifest fields for response cursor and replay count; A relay verb that returns a bounded audio range by opaque artifact ID

### "“Run a 24 kHz audio health check and tell me if today’s voice path is still trustworthy.” After a firmware or bridge change, automatically run a bounded loopback/golden-fixture probe, compare measured alias rejection, codec CPU, mic drops, tx starvation, and preamble silence against acceptance criteria, and refuse to advertise superwideband if any gate fails."
- **useful because:** The owner gets an honest answer about whether speech quality is intact instead of trusting a configuration label. A failed path degrades explicitly to a known-good mode and produces a concise reason, while the expensive probe runs only after changes or on demand.
- **path:** relay-realtime → home-macbook-bridge → pendant
- **model tier:** No model for measurement or gating. Use a cheap background model only to turn the structured receipt into a human-readable explanation.
- **latency:** Capabilities-only check under 1 s; a 10–30 s fixture/loopback run is acceptable after a firmware update and should never block ordinary conversation.
- **cost:** No inference cost for probes; modest Mac/bridge CPU and storage for receipts. Explanation costs only a few hundred tokens when requested.
- **security:** Fixture audio must be synthetic or explicitly owner-selected; never open a microphone for a golden fixture. Persist hashes and metrics, not raw speech. Do not silently switch modes during a live call; announce and require confirmation for a quality-affecting downgrade.
- **missing:** A relay-side policy that consumes audio_path_probe receipts and publishes a signed path-quality verdict; A firmware/bridge version identifier attached to each probe receipt; A safe fallback negotiation from 24 kHz to the known-good path

### "“Bookmark this moment so I can return to exactly what was happening.” Pressing the pendant bookmark button should atomically bind the audio timestamp to a privacy-preserving Mac/browser state snapshot; later I can ask for “the bookmark from when I was on that page” and resume with the original answer or action receipt."
- **useful because:** A bookmark that contains only audio is hard to use later. Binding the moment to foreground app, browser session identity, URL hash, and action/job IDs lets the whole system recover context without copying page contents to the pendant or pretending a stale browser state is current.
- **path:** pendant → relay-realtime → home-macbook-bridge → Safari on MacIntel
- **model tier:** No model for capture or lookup. Use the realtime tier only when the owner asks a vague natural-language lookup; use a cheap background model to summarize multiple matching bookmarks.
- **latency:** Capture acknowledgment under 250 ms; snapshot completion under 1 s. Lookup should return candidate bookmarks in under 2 s before any optional summary.
- **cost:** Negligible for capture; storage is a compact event record. Optional lookup summarization costs a small background-model call.
- **security:** Store hashes, app identifiers, session IDs, and sensitivity labels by default; keep URL/page text on the Mac. Private/secret bookmarks require explicit owner confirmation before exposing details, and stale browser identity must be reported rather than refreshed deceptively.
- **missing:** An atomic cross-surface bookmark transaction joining pendant event time, pipeline cursor, Mac observe snapshot, and job/action IDs; A browser-state hash/sensitivity envelope that can be matched without exporting page contents; A lookup route that returns provenance and freshness for bookmark candidates

### "“Never let this leave my devices: keep client documents and private messages local, but still let you act on them.” Define a user-owned data boundary once, then have the pendant, relay, Mac planner, and browser enforce it per field: local-only content may be inspected and transformed on the Mac, while the model receives only redacted predicates, hashes, or owner-approved excerpts."
- **useful because:** Today privacy is a collection of endpoint promises. The owner cannot express one durable rule that follows a document from Safari to Mac automation to relay and back. This makes sensitive automation usable without forcing the owner to choose between convenience and sending secrets to the model.
- **path:** pendant → relay-realtime → home-macbook-bridge → Safari on MacIntel
- **model tier:** Use the realtime model only to interpret a new policy sentence once. Compile it into deterministic field-level rules; all subsequent enforcement is local and model-free.
- **latency:** Policy compilation under 3 s. Enforcement adds less than 100 ms for ordinary actions; any denied transfer should fail closed immediately.
- **cost:** One small policy-compilation inference per policy change; negligible recurring cost. Mac-side classification may use existing metadata and hashes.
- **security:** The relay must never receive the protected payload merely to decide whether it is protected. Rules, policy version, and denial receipts are signed; the pendant stores only policy ID/version, never content. Ambiguous classification must deny or request an owner-approved excerpt.
- **missing:** A policy compiler producing a signed, deterministic field-level data-boundary manifest; Content classification and redaction hooks in Mac planner/browser result paths; A relay admission check that rejects payloads lacking the required policy proof

### "“If I become unreachable, make sure a truly urgent thing still reaches me, but do not wake me for ordinary notifications.” Let the relay and Mac classify events against an owner-defined urgency contract, deliver only urgent items through the pendant’s inbox, and require an explicit acknowledgement; unanswered urgent items escalate through a bounded retry schedule and then surface as an honest undelivered state."
- **useful because:** The owner currently has no dependable distinction between an important interruption and notification noise. This makes the pendant a reliable emergency channel without turning it into an always-on notification stream, and it remains truthful when the device is offline.
- **path:** relay-realtime → home-macbook-bridge → pendant
- **model tier:** Use a cheap background model for ambiguous notification classification; deterministic rules handle known senders, keywords, calendar severity, and expiry. Realtime is used only when the owner asks why something escalated.
- **latency:** Known urgent events enqueue within 1 s; classification under 5 s. Escalation follows explicit deadlines, never an unbounded retry loop.
- **cost:** Low background inference cost only for ambiguous events; compact inbox records and a few signed delivery receipts.
- **security:** Do not put message bodies or secrets in the pendant payload. Send a redacted title, source class, urgency, expiry, and opaque retrieval ID. The owner must opt into sources and escalation windows; every delivery and acknowledgement is deduplicated.
- **missing:** An urgency-policy data model with source, severity, quiet-hours, and escalation fields; A relay scheduler that can distinguish delivered, acknowledged, expired, and unreachable states; A Mac-side event adapter for permitted notification/calendar/message sources

### "“Before you send anything irreversible, read me the exact consequence in one sentence and let me cancel without seeing the private contents.” For a staged Mac or browser action, generate a redacted consequence statement and a compact diff/provenance receipt, deliver it to the pendant, and accept a cancel gesture or approval only against the signed operation digest."
- **useful because:** Physical approval exists, but a pending light or pattern does not tell the owner what will happen. This gives them meaningful consent without leaking form contents or passwords to the wearable, and prevents an approval for one action from being replayed against another.
- **path:** faculty-judgement → faculty-action → relay-realtime → pendant → home-macbook-bridge → Safari on MacIntel
- **model tier:** Use a cheap model to draft the one-sentence consequence from structured action metadata; deterministic redaction, digesting, expiry, and gesture handling must happen without a model. Realtime is unnecessary unless the owner asks for clarification.
- **latency:** Prepare statement within 1 s; owner gets a concise pending cue immediately and can cancel locally in under 200 ms. No action executes until the signed digest is approved.
- **cost:** Small inference call per staged action, dominated by action metadata rather than page contents; negligible device storage.
- **security:** The model and pendant receive only a sensitivity-labeled summary, not secrets or page contents. The digest binds target, operation, parameters, expiry, and risk class; mismatches, expiry, and duplicate approvals fail closed.
- **missing:** A structured consequence/diff schema emitted by the planner; A redaction service that can prove summary coverage without exposing protected fields; A relay envelope joining the summary digest to the existing physical transaction approval latch


## What it asked for

_Nothing._
## Its own summary

Discovered current live inventory: home-macbook-bridge and Safari are online; nrf9160-pendant is registered but offline. Recorded three distinct owner-facing capabilities: (1) wheel-driven replay of the last complete answer with cursor/checksum/expiry semantics, (2) measured 24 kHz path health gating based on real loopback/golden-fixture metrics, and (3) atomic bookmark capture joining pendant audio time with privacy-preserving Mac/browser state and action receipts. A stale-state circuit-breaker proposal was correctly rejected as already covered by the existing freshness-gated commit barrier, so I did not rephrase it.

**Biggest unknown:** The product-direction rotary encoder/extra button is not yet physically integrated, and the relay lacks the bounded audio-range replay verb, version-bound audio probe policy/fallback negotiation, and atomic cross-surface bookmark transaction. Those are the concrete things still needed; no microphone was opened and no hardware was modified.

