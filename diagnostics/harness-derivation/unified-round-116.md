# Harness derivation — unified — round 116

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Keep my conversation understandable even when the pendant's cellular link is struggling, and tell me afterward if anything was lost.”"
- **useful because:** Today the measured link can drop 388 uplink packets while the assistant speaks. The owner needs graceful degradation and an honest, cross-device receipt rather than silently missing a command.
- **path:** pendant → relay-realtime → mac-planner → dashboard-ux
- **model tier:** Realtime handles only the live short-turn audio exchange; a cheap background model compares packet/sequence receipts with the transcript and prepares the post-call quality note.
- **latency:** Audio adaptation must react within one 60 ms frame; the post-call loss report can arrive within 30 seconds of hangup.
- **cost:** Low per call: telemetry and receipt storage dominate, with a small background summarization call only when loss or fallback occurred.
- **security:** Packet telemetry and transcripts are sensitive. Send sequence numbers and quality metrics by default, retain raw audio only under the existing retention policy, and require confirmation before sharing diagnostics externally.
- **missing:** A durable pendant-side sequence/utterance spool that survives a dropped link; A relay-to-pendant delivery receipt indexed by interaction; A measured audio-path preflight and fault-injection harness; A local privacy/mute policy for diagnostic capture

### "“Continue this on my Mac.”"
- **useful because:** A spoken interaction often reaches the point where a screen is useful. The owner should be able to hand off the exact live conversation—not re-explain it—and receive a reviewable workspace with the transcript, cited sources, unfinished questions, and suggested next action. The pendant provides intent and continuity; the relay preserves the session; the Mac and browser can materialize the result.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard-ux
- **model tier:** Realtime only detects the short handoff command and session identifier. A cheaper background planner assembles the workspace, opens only the relevant Mac apps/tabs, and produces a concise spoken confirmation.
- **latency:** Acknowledge on the pendant in under 500 ms; create the Mac workspace and open browser context within 10 seconds. Never block the live audio loop on Mac work.
- **cost:** Low: one compact session projection and one background planning call; browser and Mac execution dominate latency, not tokens.
- **security:** The handoff may expose private authenticated pages on the Mac. Require same-owner session binding, show the exact tabs/files opened in a receipt, inherit browser read permissions but preserve destructive-action confirmation, and never silently submit or send anything.
- **missing:** A first-class handoff token that binds a pendant interaction to a Mac job without resending the full transcript; A compact session projection containing transcript, citations, pending decisions, and expiry; A workspace renderer that can create a reviewable folder/note and reattach only the necessary browser tabs; A spoken completion receipt that names what was opened and what remains for the owner

### "“Put the one-time code I just said into the login page I’m looking at.”"
- **useful because:** The owner can authenticate hands-free without copying a sensitive OTP through clipboard, chat history, or persistent memory. The pendant hears the code, the relay delivers it only to the owner-selected active browser tab, and the Mac/browser reports whether the field was filled—never the code itself.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** Realtime performs constrained digit/character recognition only; deterministic relay and browser code handle routing and field insertion. No general-purpose model should see or retain the OTP.
- **latency:** Acknowledge capture in under 300 ms and fill the selected field within 2 seconds. Expire the secret after 30 seconds or immediately after successful insertion.
- **cost:** Negligible API cost; the work is protocol and browser-extension hardening. No background model call is necessary.
- **security:** An OTP is a high-value secret. Require a deliberate pendant gesture plus an active-tab binding, visually and audibly identify the destination origin before insertion, encrypt it in transit, keep it in memory only, redact it from logs/transcripts/receipts, refuse cross-origin redirects and password fields, and require confirmation for any non-OTP field. If origin or field classification is uncertain, do nothing.
- **missing:** A firmware/relay ephemeral-secret channel that bypasses transcript and recording persistence; Browser-side origin and field-type attestation for the selected tab; A one-shot insertion primitive with zeroized buffers and an insertion receipt that contains metadata but not the secret; A pendant gesture or spoken confirmation policy for high-sensitivity input


## Changes it proposed to its own stack

### `hardware` — Replace the prototype nRF9160 audio path for the product with a modem/SoC architecture that has a dedicated audio DSP (or second application core), a clocked 24 kHz-capable microphone front end, and a full-duplex LTE-M data budget with independent uplink/downlink scheduling. Keep the relay protocol profile-negotiated so the current DK remains a compatibility fixture, but make the product's measured profile the default.
- **owner gets:** The pendant would stop dropping roughly eight seconds of speech when it talks over LTE-M, respond with less delay, and deliver genuinely wideband speech instead of upsampling a 15.625 kHz microphone signal. Conversations would feel natural rather than half-duplex and lossy.
- effort: High: select and prototype a replacement cellular/audio reference design, redesign microphone clocking and board layout, port modem and Opus tasks, then validate RF, thermal, battery, and acoustic performance in an enclosure.  ·  risk: A new modem or clock tree can introduce RF certification, driver, power, and acoustic regressions. Recover by retaining the nRF9160 DK as a negotiated narrowband fallback and requiring an A/B hardware qualification test before switching production defaults.
- cost: Hardware NRE and certification are the dominant costs; expect roughly $20–$60 additional prototype BOM depending on modem/DSP choice, with higher peak current during simultaneous audio. API cost is negligible.  ·  latency: Lower encode/decode contention and true concurrent transport should reduce conversational turnaround and packet loss; LTE scheduling remains the limiting factor.
- security: A new modem increases firmware and supply-chain attack surface. Require signed firmware, isolated audio DSP boundaries, TLS keys in secure storage, and no raw audio persistence outside the existing retention policy.
- depends on: 24 kHz product compatibility target and end-to-end acceptance thresholds; Measured full-duplex LTE-M profile from the audio fault-injection and validation work; Production pendant constraints beyond the current nRF9160 DK

### `integration` — Add a signed, expiring cross-surface handoff envelope. The pendant emits only a handoff intent plus sessionId; relay mints a one-time token whose payload references a compact session projection (transcript segments, citations, pending decisions, sensitivity labels, and expiry). mac-planner redeems it once, creates a reviewable workspace, and records opened tabs/files and the receipt. Do not copy the entire transcript into every prompt.
- **owner gets:** Saying “continue this on my Mac” would work reliably and privately: the Mac would pick up the exact conversation with its sources and unfinished work, without making the owner repeat themselves or leaking unrelated history.
- effort: Medium: define envelope schema and signing/expiry, add one redeem route and session projection, connect pendant intent to relay, and add Mac workspace/receipt handling.  ·  risk: Replay or over-broad context could expose private data or duplicate work. Mitigate with one-time nonce, short TTL, audience binding (specific Mac agent), sensitivity filtering, and idempotent redemption; recovery is a fresh handoff if redemption expires.
- cost: Negligible API cost; saves context tokens by projecting only relevant segments. Small D1 storage increase for envelopes and redemption audit records.  ·  latency: One relay round trip plus Mac setup, target under 10 seconds; live pendant acknowledgement remains immediate.
- security: Improves security versus resending full transcripts, but signing keys and audience checks become critical. Log token redemption without logging payload contents.
- depends on: Session projection service with provenance and sensitivity labels; Mac workspace renderer and reviewable receipt; A pendant/relay handoff intent event


## What it asked for

_Nothing._
## Its own summary

I discovered the live stack: the Mac agent exposes 120 routes, including session, browser, pipeline, planning, execution, and receipt paths; the pendant remains a prototype nRF9160 with 15.625 kHz mic capture, 24 kHz decode resampled to a 31.25 kHz wire clock, ~87% single-core encode/decode load, and measured LTE-M contention that has dropped about 7.8 seconds of uplink speech. I recorded three concrete additions: a product hardware architecture with dedicated audio processing/full-duplex capability, a cross-surface “continue this on my Mac” capability, and a signed one-time handoff envelope that avoids retransmitting full context. The most useful new connective feature is the handoff envelope: it turns existing sessions, browser inspection, Mac execution, and receipts into a seamless pendant-to-Mac workflow.

**Biggest unknown:** I still need authoritative 24 kHz product compatibility and end-to-end acceptance thresholds, production pendant constraints beyond the DK, and the owner's acceptable phone-companion/privacy boundary. The audio preflight/fault-injection, delivery-receipt, offline spool, and privacy-latch requests remain unanswered, so I cannot honestly claim the audio path is ready for acceptance. No new grants or tools appeared this round.

