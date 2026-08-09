# Harness derivation — unified — round 170

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac/browser permissions and relay readiness** — GET /ops/snapshot reports AI Pendant Agent Accessibility and Screen Recording both granted, requiredMissing/optionalMissing empty, browser online with 9 Safari tabs and zero pending commands, relay reachable with D1 and durableAudio enabled, and Mac bridge online. This supersedes the older denied-permission context for current behavior.
  - evidence: GET /ops/snapshot at 2026-08-08T02:50Z returned permissions.accessibility.trusted=true, permissions.screenRecording.granted=true, agent.ready=true, browser.online=true, relay.reachable=true.

## Capabilities it proposed

### ""Repeat only the part of your last answer I missed.""
- **useful because:** When a bridge hiccup drops one audio segment, the owner gets a targeted replay instead of an entire answer or a confusing silence. It uses physical delivery evidence, not guesses, so the pendant can repair speech without duplicating already-heard content.
- **path:** pendant → relay → mac-bridge
- **model tier:** Realtime for selecting the missing artifact and a cheap deterministic path for range replay; no planner call unless the artifact is ambiguous.
- **latency:** Detect within 2 s of the turn; begin replay within 500 ms after the owner's request.
- **cost:** Usually <$0.01 per repair; dominated by TTS only if the original PCM/Opus artifact was not retained at the relay.
- **security:** Store only short-lived audio artifacts keyed by opaque turn IDs; never expose raw audio to Mac/browser. Require the pendant's delivery receipt and suppress replay if the artifact was already marked heard.
- **missing:** End-to-end range-aware replay endpoint joining audio_delivery_ack_queue records to relay artifacts; A compact pendant command for replaying an artifact byte range or packet interval; Retention/eviction policy for relay audio artifacts

### ""Fill in this web form, but show me exactly what will be submitted before you send it.""
- **useful because:** It turns the Mac/browser/pendant combination into a trustworthy high-stakes assistant: the browser supplies private session state, the Mac fills fields, the relay binds a preview to the exact page state, and the pendant supplies deliberate physical consent. The owner sees a concise spoken diff and can cancel without exposing credentials to the model.
- **path:** browser → mac-bridge → relay → pendant
- **model tier:** Background/planner model extracts fields and drafts the diff; deterministic executor performs only the approved browser commands; realtime model speaks the short preview.
- **latency:** Draft in 3-8 s, then wait indefinitely for physical approval; submit within 1 s of the signed approval event.
- **cost:** $0.02-$0.10 per form depending on page complexity; browser inspection and planner tokens dominate, not execution.
- **security:** Never send passwords, tokens, or full page contents to the relay; browser returns field labels, redacted values, and a page fingerprint. Bind preview to URL/origin, DOM digest, field digest, expiry, and a one-time nonce. Any navigation or DOM change invalidates it. Submission requires the physical_transaction_approval_latch event; failed or expired approvals must not retry.
- **missing:** A production relay implementation of the approval handoff contract and delivery/readback path; A browser-side structured form extraction and redaction protocol; An executor route that accepts only the approved plan digest and nonce, not free-form commands; A spoken/LED pending-preview presentation that works on the current USB-attached pendant

### ""Before I leave, tell me what I promised today and what is still unconfirmed.""
- **useful because:** It gives the owner a concrete end-of-day truth check across spoken commitments, Mac jobs, browser actions, and relay receipts, rather than a generic task list. It can distinguish evidence of completion from mere intent and surface only unresolved items for the next conversation.
- **path:** pendant → relay → mac-bridge → browser
- **model tier:** Background model extracts candidate commitments and summarizes evidence; deterministic evidence joins and date filtering; realtime only speaks the final short digest on request.
- **latency:** Under 10 s for a day's digest; no interruption of active speech and no unsolicited capture.
- **cost:** $0.01-$0.05 per digest; evidence retrieval is cheap, summarization dominates.
- **security:** Search only explicitly bound Mac apps/tabs and the owner's relay jobs; redact page contents and message bodies by default, returning provenance snippets only when needed. Never infer completion from absence of failure. Retain the digest and evidence links for a configurable short period, not raw transcripts.
- **missing:** A user-facing digest route that joins commitment_evidence_query results with relay receipts and Mac job outcomes; Explicit commitment lifecycle states (candidate, confirmed, completed, rejected, stale) and owner correction flow; A date-bound spoken interaction that uses the authoritative Mac timezone without claiming it is the owner's physical timezone

### ""Use my browser and Mac context, but do not send the underlying private content to the relay or model—just tell me the result.""
- **useful because:** The owner gets cross-surface assistance without handing page text, messages, documents, or account data to the cloud. The browser and Mac can perform local extraction and return only the minimum structured facts needed for an answer or action.
- **path:** browser → mac-bridge → relay → pendant
- **model tier:** Deterministic local redaction and claim extraction first; a background model may reason over signed, minimized claims; realtime only speaks the result.
- **latency:** 3-10 seconds for ordinary queries; local extraction must finish before any cloud request.
- **cost:** Usually $0.005-$0.03, substantially below sending full pages or documents; local extraction dominates latency, not tokens.
- **security:** Claims need provenance, freshness, audience, and sensitivity labels. Default-deny raw text, screenshots, DOM, clipboard, and credentials. The owner must be able to inspect the exact claims leaving the Mac, and a claim expires when its tab/app state changes.
- **missing:** A local semantic-minimization service in the Mac agent; A signed claim envelope and relay policy that rejects unminimized payloads; Browser and AppleScript extractors for common facts such as titles, dates, amounts, and status

### ""Keep my music playing, but make the pendant conversation clear and private.""
- **useful because:** The owner can use the pendant without stopping whatever they are listening to. The Mac and ESP32 bridge coordinate ducking, echo suppression, and restoration so the assistant is intelligible while music remains at the owner's chosen level.
- **path:** pendant → mac-bridge → relay
- **model tier:** Deterministic audio policy and DSP; no expensive model call beyond the normal realtime conversation.
- **latency:** Duck within 50 ms of capture start, restore within 150 ms after playback ends, with no audible clicks or preamble.
- **cost:** Negligible API cost; engineering effort is in bridge/Mac audio routing and measured DSP validation.
- **security:** Only inspect local audio route metadata, never record unrelated music. Respect the privacy latch as an absolute mute. Persist no music or mixed-room audio.
- **missing:** A Mac audio-route/mixer controller that can distinguish the assistant stream from other playback; Bridge-side ducking/echo-reference transport and calibration; A measured acceptance fixture for intelligibility, latency, and restoration

### ""Tell me whether this result is safe to rely on, and show me what changed since the last time you checked.""
- **useful because:** The owner gets a change-aware answer instead of a stale screenshot or an unqualified assertion. Browser state, Mac files, and relay observations are compared against a prior signed snapshot, with the pendant speaking the material differences and uncertainty.
- **path:** pendant → browser → mac-bridge → relay
- **model tier:** Deterministic snapshot/diff and freshness checks; background model summarizes material changes; realtime speaks only the final verdict.
- **latency:** Under 5 seconds for a previously indexed target; up to 15 seconds for a new browser/Mac target.
- **cost:** $0.005-$0.04 per check; model summarization and browser inspection dominate.
- **security:** Bind snapshots to explicit tab/app targets, origin or path, and owner-selected retention. Never treat missing data as unchanged. Redact sensitive values while retaining typed hashes and provenance. Require confirmation before acting on a changed result.
- **missing:** A durable, scoped snapshot store with typed field hashes and expiration; A diff/verdict schema separating unchanged, changed, unavailable, and unverifiable; A spoken owner-facing uncertainty vocabulary and optional browser/Mac evidence view


## Changes it proposed to its own stack

### `integration` — Ship the Mac-side USB conversation transport that pairs /dev/cu.usbmodem00096003658* (nRF9160 pendant) with /dev/cu.usbserial-0287A9CA (ESP32 bridge): discover both ports, authenticate a session nonce, carry the existing monotonic audio/button frames to the relay, and expose an explicit USB-owned/LTE-owned state with turn-boundary handoff. Add a local smoke test that presses the physical button, captures one uplink turn, receives 24 kHz downlink, and records packet/sequence receipts.
- **owner gets:** The owner can have a real conversation with the pendant on the desk today, even though LTE registration is not available, and can tell whether the worn hardware works before waiting for modem provisioning. A dropped cable or reconnect will not duplicate audio or strand a turn.
- effort: Medium: Mac serial framing/port discovery, relay session plumbing, and an end-to-end test against the two physically connected boards.  ·  risk: A reconnect could create duplicate turns or leave the bridge driving the speaker after ownership changed. Prevent with monotonic session and turn IDs, explicit ownership leases, and handoff only at turn boundaries; recover by closing the USB session and returning to idle.
- cost: Negligible API cost during USB transport; roughly 1-2 weeks engineering effort. No hardware cost.  ·  latency: USB should reduce local transport latency versus LTE; session startup may add 1-2 s for port discovery and handshake.
- security: Keep USB transport local and authenticated with a per-session nonce; do not treat a serial device name alone as identity. Raw audio remains on the local link unless the owner starts a relay conversation.
- depends on: usb_fallback_audio_session; 24 kHz superwideband audio-path acceptance criteria; A Mac serial transport implementation (not currently in the established tool list)


## What it asked for

_Nothing._
