# Harness derivation — mac-planner — round 167

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Why did the last call glitch?"
- **useful because:** The system would correlate the pendant's congestion/diagnostic counters, relay pipeline events and audio packet gaps, and the Mac/browser job and network state into a timestamped causal explanation instead of making the owner reproduce a failure or guess whether LTE, Opus, or the Mac caused it. It can recommend one concrete fix and verify the next call.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** background for correlation and explanation; realtime only to acknowledge a live diagnostic trigger
- **latency:** Under 10 seconds for a post-call report; under 500 ms to acknowledge a live anomaly
- **cost:** ~$0.01–$0.04 per report; most cost is summarizing correlated telemetry, not raw collection
- **security:** Audio payloads must not leave the device; send counters, sequence numbers, timestamps and redacted job IDs only. Browser URLs and Mac app names need configurable redaction. No remediation should execute unattended unless it is a reversible setting change.
- **missing:** A durable cross-node correlation ID and clock-skew estimator across pendant, relay, and Mac; A relay endpoint that stores compact audio-QoS windows and joins them to pipeline/job receipts; A report generator that can cite exact packet ranges and distinguish evidence from inference

### "Put this exact thing on my Mac, but make me confirm it with the button on my pendant when I'm physically at the desk."
- **useful because:** A spoken request can be prepared by the relay and inspected by the Mac preflight, then a one-time nonce is shown in the Mac notification and acknowledged by the physically connected pendant button. This gives the owner a reliable 'I am here and this is the action I meant' control for destructive or externally visible work without requiring a microphone, keyboard, or Accessibility snapshot.
- **path:** relay → mac-planner → pendant → mac-vision
- **model tier:** realtime for the short spoken request and nonce matching; background for plan rendering and receipt verification
- **latency:** Plan preview within 2 seconds; pendant acknowledgement reflected within 1 second over USB; receipt within 5 seconds
- **cost:** ~$0.005–$0.02 per invocation; dominated by plan interpretation, not the button event
- **security:** The nonce must be single-use, expire quickly, and be bound to the exact preflight hash, Mac session, and pendant identity. Never treat a generic bookmark as consent. Do not transmit audio or secrets; expose only a redacted action summary. This is opt-in policy because the owner has not yet defined unattended-action classes.
- **missing:** USB serial pendant event ingestion and a relay-to-Mac nonce broker; A Mac notification/preview surface that displays the exact mac_action_preflight result; A policy configuration that lets the owner choose which action classes require physical acknowledgement; A firmware event path distinguishing a confirmation press from an ordinary moment bookmark

### "What was I doing when I pressed the bookmark button?"
- **useful because:** Every physical bookmark would become a useful cross-device anchor: the relay aligns the pendant timestamp with the Mac foreground app, open browser tabs, active job/plan, and nearby calendar event, then returns a redacted evidence card. The owner can recover context after an interruption without recording ambient speech or screen video.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** background for joining and summarizing; realtime only to confirm that the bookmark was received
- **latency:** Acknowledge in under 1 second; searchable context card in under 15 seconds
- **cost:** ~$0.005–$0.03 per bookmark query; token cost is bounded by metadata and selected snippets
- **security:** Default to metadata-only and redact URLs, document names, message bodies and typed secrets. Keep raw bookmark events local until relay acknowledgement; enforce per-source retention and a delete-by-bookmark operation. Never capture microphone or screen pixels implicitly.
- **missing:** A shared monotonic/event-time envelope and clock-offset calibration between USB pendant and Mac; A read-only Mac context endpoint returning foreground app, browser tab IDs/titles and active job IDs with redaction; A relay index keyed by bookmark ID that joins events across pipeline, browser, and Mac receipts; A user-visible retention/deletion control for context cards

### "Before I send this, tell me what I am committing to and remove anything that should not leave my devices."
- **useful because:** The relay would combine the exact draft from the authenticated browser or Mac app with the owner's private context, identify hidden commitments, secrets, accidental recipients, and unsupported claims, then present a minimal redacted diff and a plain-language consequence summary through the pendant. It can place the corrected draft back into the originating app only after the owner chooses the proposed version. This is a protective cross-node function, not merely a spell-checker: the browser holds the session, the Mac can edit the real draft, the relay performs the analysis, and the pendant gives the owner a channel-independent decision point.
- **path:** browser-extension → mac-planner → relay → pendant
- **model tier:** background model for extraction, policy checking, and rewrite; realtime model only for a short spoken explanation or an urgent send warning
- **latency:** Initial risk scan under 3 seconds for ordinary drafts; under 1 second for deterministic secret/recipient checks; never block typing while analysis runs
- **cost:** ~$0.01–$0.08 per checked draft depending on length and private-context retrieval; deterministic local scanners handle common secrets cheaply
- **security:** Draft text is highly sensitive and must remain on the Mac/browser when deterministic checks suffice; send only a minimal redacted representation to the relay, with explicit per-origin retention of zero by default. Never silently alter or send anything. Preserve the original, show an exact diff, bind any approval to a content hash and recipient set, and invalidate it when either changes.
- **missing:** A browser and Mac read/write draft interface that returns origin, recipient set, content hash, and selection boundaries without screenshots; A private policy/secret scanner that runs locally before any model call; A relay analysis contract that returns claims, commitments, redactions, confidence, and a content-addressed diff; A single-use approval-and-writeback protocol spanning browser session, Mac app, and pendant, with no approval surviving a draft or recipient change; Owner-configurable classes for never-send data, acceptable commitments, and redaction behavior

### "Give them only the information they need for this meeting, and make the bundle expire afterward."
- **useful because:** The system would resolve the meeting and recipient from Calendar/browser context, gather only the relevant files, mail snippets, and approved notes on the Mac, have the relay explain why each item is included, and create an encrypted, expiring bundle or draft in the authenticated browser. The owner sees a compact contents-and-leakage summary on the pendant before release. This turns scattered private context into a least-privilege handoff without manually hunting through tabs and folders.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** background model for relevance ranking and explanation; realtime only for the owner's final spoken choice
- **latency:** Preview in under 10 seconds for up to 50 candidate items; bundle creation under 5 seconds after approval
- **cost:** ~$0.03–$0.15 per bundle, dominated by relevance analysis and document extraction
- **security:** Never upload source files to the relay by default; build and encrypt locally, transmit only hashes and metadata for ranking where possible. Require exact recipient/domain binding, expiry and revocation, immutable manifest, and a visible list of excluded near-matches. Do not infer permission from calendar attendance alone.
- **missing:** A local content index spanning approved Mac files, Calendar/Mail sources, and authenticated browser pages; A policy engine for recipient, domain, classification, expiry, and allowed transformations; An atomic Mac bundle builder with encrypted manifest, expiration, revocation, and receipt; Browser APIs for creating the final draft/upload without exposing session cookies; Pendant rendering of a short manifest and an unambiguous approve/reject interaction

### "I told you what to do while I was away from the Mac. When it comes back, reconcile it with what changed and do only the parts that are still safe."
- **useful because:** The pendant can capture a structured intent offline, the relay can hold it durably, and the Mac can later compare the intent's preconditions with current files, browser sessions, calendar, and app state. Instead of blindly replaying stale actions, it produces a conflict list, applies only idempotent still-valid steps, and returns a concise result to the pendant. This is the missing continuity between a wearable that survives disconnection and a machine that can act.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** background model for converting the offline utterance into a bounded plan and explaining conflicts; deterministic executor for preconditions and idempotent steps
- **latency:** Queue acknowledgement under 1 second offline; reconciliation within 10 seconds of Mac return for a normal plan
- **cost:** ~$0.01–$0.06 per reconciliation; most work is deterministic state comparison
- **security:** Offline intents must be encrypted and scoped to an expiry and allowed action classes. Never replay a plan after recipient, URL, file hash, or account changes. Show stale/conflicting fields and preserve a receipt; destructive or externally visible steps remain unexecuted until an owner-selected policy authorizes them.
- **missing:** A pendant-to-relay structured intent envelope with durable deduplication and expiry; A Mac plan format with explicit preconditions, idempotency keys, touched-resource hashes, and partial execution semantics; Browser and Mac readback adapters for current state and conflict proofs; A reconciliation engine that can safely split a plan into applied, skipped, and blocked steps; A local or pendant-readable result card for offline/online completion


## Changes it proposed to its own stack

### `integration` — Add a monotonic event envelope and correlation service shared by pendant USB events, relay pipeline telemetry, Mac action receipts, and browser commands. Each event carries source clock, relay receive time, correlation ID, redaction class, and retention deadline; the service estimates clock offset and exposes a cited joined timeline rather than forcing each surface to guess timestamps.
- **owner gets:** The owner gets answers anchored to what actually happened — which app/tab was open at a bookmark, which packet gap caused a glitch, and which desktop action produced a file — instead of plausible but untrustworthy summaries.
- effort: Medium-high: protocol fields and clock calibration on the USB bridge/relay, a small durable index, adapters for existing receipts and browser results, and deletion/retention tests.  ·  risk: Clock correction could reorder events or accidentally join unrelated sessions. Use bounded uncertainty intervals, never fabricate ordering across overlap, and allow deletion by correlation ID. Recover by treating unjoined events as independent rather than guessing.
- cost: Low storage and compute; roughly a few hundred bytes per event plus index overhead. No model cost until a user asks for a summary.  ·  latency: Negligible on event ingestion; joined queries typically under 1 second, with background summarization under 15 seconds.
- security: Improves auditability but creates a sensitive metadata graph. Encrypt at rest, hash or redact resource identifiers, and enforce per-source retention and explicit deletion.
- depends on: USB serial event ingestion for the physically connected pendant; A relay durable event index; Mac/browser adapters that emit correlation IDs and redacted metadata; Owner-selected retention and redaction policy


## What it asked for

_Nothing._
## Its own summary

Round 167 produced four non-duplicate proposals: cited post-call audio root-cause reports; optional pendant-button physical acknowledgement bound to an exact Mac preflight hash; bookmark-anchored reconstruction of what the owner was doing; and the integration change that makes all three trustworthy via shared event-time/correlation envelopes. I also told mac-vision the live inspection state: ui_snapshot and browser/app inspection work, but owner-controlled TCC/vision consent remains unavailable. The immediate work is not another Mac action primitive; it is the missing cross-node event join, USB pendant event ingestion, and explicit retention/redaction policy.

**Biggest unknown:** Whether the relay already has any durable event/correlation index or USB-serial event reader that was not exposed in this round. The proposals deliberately mark those as missing rather than assuming they exist.

