# Harness derivation — faculty-perception — round 240

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac input reachability** — As of 2026-08-09T02:01Z, the running AI Pendant Agent has Accessibility and Screen Recording granted; /observe reports inputReachability.status=verified, uiActionsWillReachTheScreen=true, secureInputActive=false, and /ops/status permissions.ready=true. Safari browser extension is online with two tabs and zero pending commands.
  - evidence: GET /observe and GET /ops/status both returned HTTP 200 with trusted=true, screenRecording=true, inputReachability=verified, browser online=true.
- **live Mac/browser state** — At 2026-08-09T02:01Z the Mac agent is fully ready (fullControlMode, computer-use loop enabled, vision upload consented), Safari is foreground, browser extension v1.2.0 is online with tabCount=2 and pendingCommands=0, and /observe exposes four durable browser sessions including YouTube and Google News.
  - evidence: GET /ops/status, GET /observe, and GET /browser/status returned HTTP 200; all reported browser online and no pending commands.

## Capabilities it proposed

### "Before you do anything consequential, tell me exactly what you are looking at, what changed since you decided to act, and whether the live screen/browser still matches the evidence you based the decision on."
- **useful because:** This would prevent the most dangerous class of hive error: the Mac or browser changes after perception but before action, while the model continues as if its old observation were current. It is a cross-node reality fence, not another generic status page.
- **path:** browser → mac → relay → dashboard
- **model tier:** Use the cheap background model to normalize observations and hashes; reserve realtime only for the owner's spoken confirmation when the target or evidence changed.
- **latency:** Under 800 ms for a normal check: browser snapshot and /observe in parallel, Mac evidence lookup locally, relay correlation only when a job or speech artifact is involved.
- **cost:** Usually <$0.01 in API cost; dominated by no model call or a small normalization call. Screen/browser metadata and hashes stay on the Mac unless the owner explicitly asks to share them.
- **security:** Never transmit page bodies or screenshots by default. Return app bundle, tab identity, URL origin, content hash, capture times, and a mismatch reason. Require confirmation if the target identity, logged-in account, or page hash changed.
- **missing:** A single correlation contract joining a browser command/evidence capsule to the Mac action ledger step and relay job/run ID; A read-only preflight route that atomically compares current browser/mac state to those correlation fields; A policy hook in faculty-action that blocks or asks for confirmation on mismatch

### "Before you read anything aloud, warn me if the current screen or browser contains secrets, private messages, financial data, or a logged-in account, and let me choose a redacted summary instead."
- **useful because:** A wearable voice assistant can leak more than a laptop because speech is audible to people nearby. This makes perception privacy-aware at the exact boundary where private browser/Mac state becomes public audio.
- **path:** browser → mac → relay → pendant → dashboard
- **model tier:** Run deterministic local classifiers first (URL/account patterns, DOM labels, app bundle, accessibility roles); use a small background model only for ambiguous regions. Realtime speaks only the short warning and asks the owner.
- **latency:** 250 ms for metadata-only pages, up to 700 ms for a browser snapshot; never block ordinary private-local actions unless content is about to leave the device as speech or relay data.
- **cost:** Near-zero for deterministic checks; <$0.005 for an ambiguous classification. Bodies and screenshots remain on the Mac. Only a redaction decision and a short safe summary may cross to relay.
- **security:** Fail closed for password fields, payment pages, private-message apps, and unknown authenticated pages. Do not log raw text, screenshots, account names, or classifier samples. The owner can explicitly approve one utterance; approval expires at the next navigation or tab switch.
- **missing:** A local sensitive-content classifier with explainable category and confidence; A speech gate before relay TTS/announcement streaming; A browser result contract carrying field-level sensitivity without exporting field values; A pendant-side emergency mute that works if the relay is unreachable

### "If my connection drops while I am speaking, tell me whether you captured a complete request, keep it from being repeated, and resume it only after the Mac and relay agree on the same request."
- **useful because:** Today a worn device, relay, and Mac can each have a different story about an interrupted utterance. This gives the owner one honest answer—captured, incomplete, pending, or safely resumed—instead of duplicate reminders or a silently lost command.
- **path:** pendant → relay → mac → dashboard
- **model tier:** Use firmware metrics and hashes locally; use a cheap background model on reconnect to compare transcript candidates. Realtime is used only if the owner must resolve an ambiguity.
- **latency:** Immediate local verdict at utterance end (<100 ms after capture); reconnect reconciliation within 2 s. Never execute from a low-confidence or conflicting candidate without confirmation.
- **cost:** Usually <$0.01 per reconnect, dominated by optional transcript comparison; no audio needs to leave the pendant until a valid link exists. Store only bounded hashes/quality metrics in the offline queue.
- **security:** The pendant must not persist raw speech by default. Bind a request commitment to boot/session ID, monotonic sequence, device identity, and capture-quality verdict; reject replayed or conflicting commitments. Show the owner when only a commitment exists and no transcript is recoverable.
- **missing:** A cross-node request-envelope schema with monotonic sequence, quality verdict, transcript hash, relay receipt, and Mac execution receipt; A reconnect reconciliation endpoint and idempotency rule shared by relay and Mac job tracker; Firmware emission of the accepted offline-capture-integrity-sentinel verdict into that envelope

### "When you refuse, pause, or ask me to confirm, show me the smallest honest explanation: which observation failed, which source supplied it, what is unknown, and exactly what would become safe if I confirmed."
- **useful because:** Today the owner can receive a cautious answer without knowing whether the blocker was stale UI state, missing permissions, an untrusted web page, a disconnected pendant, or an ambiguous instruction. A source-grounded refusal explanation turns uncertainty into an actionable choice instead of making the system feel arbitrary.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Generate the explanation from structured evidence with a cheap model or deterministic templates; use realtime only to speak the short explanation and confirmation question.
- **latency:** Under 300 ms after a decision is blocked; no extra browser or screen capture should be triggered merely to explain a refusal.
- **cost:** Near-zero when evidence is already in the action record; under $0.005 only when compressing several conflicting observations. Keep raw page text, screenshots, and transcripts local.
- **security:** Expose provenance and uncertainty without revealing secrets: redact values, show app/origin and hashes rather than content, and distinguish observed facts from model inference. Confirmation must name the exact scope and expire after one action or state change.
- **missing:** A structured refusal record containing reason code, evidence references, freshness, confidence, and the precise confirmation scope; A shared evidence-reference format joining Mac observations, browser capsules, relay job state, and pendant health frames; A renderer on pendant and dashboard that can present both a short spoken explanation and a detailed local audit view

### "When you use a remembered preference or fact about me, let me inspect who or what asserted it, how confident it is, when it was last used, and correct or quarantine it without deleting unrelated memories."
- **useful because:** A machine-derived value can currently look exactly like an owner preference and be injected into every prompt indefinitely. This lets the owner catch high-confidence false beliefs—such as a wrong timezone—before they silently steer routines, messages, or purchases.
- **path:** mac → relay → dashboard → pendant
- **model tier:** Use deterministic memory provenance and policy checks; use a small model only to explain consequences in plain language. Realtime should ask for confirmation before any correction or quarantine.
- **latency:** Under 400 ms for inspection from the memory projection; correction preview under 1 s. No background model call is needed for ordinary use.
- **cost:** Negligible API cost because the memory record already contains provenance, confidence, expiry, and usage metadata. A one-time explanation is <$0.002.
- **security:** Do not speak sensitive memory values aloud by default; show them locally or require a deliberate request. Quarantine must be reversible and scoped to one fact key/version, with an audit record; never silently rewrite owner data.
- **missing:** A read-only memory provenance endpoint exposing source.origin, confidence, expiry, pinning kind, useCount, and lastUsedAt with secret redaction; A quarantine/version layer distinct from DELETE /memory/facts/:idOrKey; Prompt projection rules that exclude quarantined machine-origin facts immediately and report the exclusion


## Changes it proposed to its own stack

### `relay` — Put relay-fetched browser text and routine announcement speech behind a privacy-preserving quarantine: attach source URL, content hash, sensitivity class, and expiry to each record; store only a redacted preview by default; enforce deletion at expiry for announcements and captured audio; reject relay persistence when no provenance/sensitivity decision exists.
- **owner gets:** A page the owner asked the relay to read should not become an untraceable, permanent copy of private web content. The owner gets a clear answer to what was retained, why, and until when, with sensitive text disappearing automatically.
- effort: Medium: extend serverBrowser read results and routine composition, add D1 deletion/sweep, and expose a retention/provenance view. Existing Mac evidence capsule fields can be reused rather than inventing a schema.  ·  risk: A too-aggressive classifier could remove useful context or make a routine fail. Recover by retaining a hash and source metadata, allowing explicit owner-approved retention, and making deletion auditable without restoring the body.
- cost: Negligible storage and CPU overhead; likely lower long-term D1/audio storage. No model cost for hashes and rules; optional classifier costs <$0.005 per page.  ·  latency: <50 ms for hashing/rule checks; asynchronous sweep. A model classifier must not sit on the interactive speech path unless the content is about to be spoken.
- security: Strongly improves privacy: no raw page body by default, source-linked records, enforced expiry, and a tombstone for deletion. URLs may themselves be sensitive and should be redacted to origin/path policy.
- depends on: A relay-side provenance ID/content-hash bridge to the existing Mac evidence capsule schema; A sensitivity classifier or browser-field annotations; A real scheduled deletion worker for relay announcements and audio


## What it asked for

_Nothing._
## Its own summary

The important grant is now verified live: the exact AI Pendant Agent binary has Accessibility and Screen Recording, /observe says inputReachability=verified and /ops/status says permissions.ready=true. Safari/browser extension is online with two active tabs and no pending commands. I recorded those facts and sent faculty-action the concrete evidence/correlation gap. This round proposed three owner-facing capabilities: pre-action screen/evidence reality fencing, privacy gating before any screen content becomes speech, and reconnect-safe request commitments for degraded/offline capture. I also proposed relay privacy quarantine with provenance, hashing, redaction, and enforced expiry.

**Biggest unknown:** The pendant is still absent from the relay registry, so no live device-originated evidence can establish receipt or playback. The main missing bridge is not observation on the Mac anymore: relay browser reads still emit no stable ID/content hash, browser provenance routes are unmounted, and no atomic contract joins current screen/browser state to the action ledger and relay job. I still need that bridge plus a defined relay-to-Mac speech/privacy gate before these proposals can be exercised end to end.

