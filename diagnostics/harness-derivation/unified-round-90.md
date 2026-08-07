# Harness derivation — unified — round 90

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Before I confirm this booking or appointment, tell me if it conflicts with anything I already committed to, and if it does, give me the best alternative.”"
- **useful because:** The browser is where the owner commits to dates, the Mac has the authoritative local calendar and files, the relay can keep the check alive across a dropped pendant link, and the pendant can interrupt with a concise spoken warning before an irreversible submit. This prevents double-bookings and missed travel buffers without requiring the owner to copy details between apps.
- **path:** browser-extension → mac-planner → relay-realtime → unified
- **model tier:** Use a cheaper background model for extraction and conflict ranking; use realtime only for the pendant warning and the owner's follow-up. No expensive model is needed for routine calendar overlap checks.
- **latency:** Under 2 seconds after the browser has a stable draft/preview; if the Mac or relay is offline, hold the browser at preview and say that verification is unavailable rather than guessing.
- **cost:** Usually <$0.01 per check; dominated by one structured extraction/reconciliation call. Browser and Mac reads are local/relay I/O, not model cost.
- **security:** Read only the minimum fields from the draft page and calendar (title, start/end, location, travel buffer); do not transmit page secrets or unrelated events. Never submit, cancel, or reschedule automatically. Require explicit owner confirmation after showing the conflict evidence and the exact proposed change.
- **missing:** A browser pre-submit/preview interception hook that reliably emits the draft fields before the site commits; A typed calendar-availability and travel-buffer read on the Mac with provenance and freshness; A relay-held pending decision record with expiry and an audible pendant confirmation/timeout path; A deterministic policy for quiet hours, ambiguous time zones, and recurring-event conflicts

### "“Call the company for me, explain the problem, and bring me in only if they ask for money, identity verification, or a decision.”"
- **useful because:** A browser session can handle chat/forms, but many real problems still require a phone call. The Mac can place and hold the call, the relay can keep the workflow alive, and the pendant can let the owner hear the live conversation and answer sensitive questions without surrendering control. The agent can do the repetitive explanation while preserving the owner's voice, identity, and approval boundary.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → unified
- **model tier:** Use a cheaper background model to prepare the case summary, account-safe script, and decision checklist. Use realtime only for live speech recognition, turn-taking, and pendant handoff during the call.
- **latency:** The call should connect within 10 seconds; live relay speech-to-speech should stay under 800 ms end to end. If the link degrades, pause the agent's speech and keep the owner connected rather than improvising.
- **cost:** Approximately $0.05–$0.50 per call depending on duration and telephony/transcription pricing; realtime audio and carrier minutes dominate, not the planning model.
- **security:** Never disclose passwords, full payment details, or one-time codes. Detect requests for identity verification, charges, legal consent, cancellation, or commitments and transfer audio to the owner before answering. Store only a short outcome receipt by default; retain the transcript only with explicit opt-in. The owner must be able to mute/terminate locally on the pendant.
- **missing:** A telephony bridge with a dedicated call identity and lawful recording/transcription controls; Full-duplex audio routing between carrier, relay, Mac, and pendant with barge-in and local mute; A live policy gate that classifies sensitive prompts and transfers control to the owner before speech is sent; A durable call case record containing the owner's approved facts, prohibited disclosures, and final outcome; Jurisdiction-aware consent and recording behavior


## Changes it proposed to its own stack

### `integration` — Add a pre-commit 'commitment collision' protocol spanning browser, Mac, and relay: the browser extension emits a normalized draft (site, action, start/end, timezone, location) with a one-time request ID; the Mac returns cited calendar conflicts and a configurable travel-buffer calculation; the relay stores the pending decision, expires it, and pushes a compact warning plus evidence reference to the pendant. The browser must remain in preview until an explicit approve token matching that request ID is received.
- **owner gets:** The owner gets a last-second, spoken warning before accidentally booking over an existing commitment, with an explanation they can trust and no surprise submission. It still works if they walk away briefly because the relay remembers the pending decision.
- effort: Medium-high: browser extension event hook, typed Mac calendar reader, relay state machine, pendant prompt/timeout, and end-to-end tests across dropped links and duplicate events.  ·  risk: Sites with unusual confirmation flows may not expose a safe preview; fail closed and let the owner continue manually. Duplicate browser events are handled by request IDs/idempotency. If the Mac is unavailable, show 'not verified' rather than asserting no conflict. Recovery is reload/clear the pending draft without mutating the site.
- cost: Negligible relay storage and local reads; roughly one inexpensive structured model call only when semantic extraction is needed.  ·  latency: Adds up to 2 seconds before confirmation; cached calendar and deterministic overlap checks can keep common cases below 500 ms.
- security: Draft metadata and selected calendar fields leave the browser only to the authenticated relay/Mac path; no page credentials. Approval tokens are single-use and scoped to the exact draft hash.
- depends on: Browser bridge must expose a reliable pre-submit/preview event; Typed calendar availability and travel-buffer reader on Mac; Relay durable pending-decision state and pendant push/confirmation channel


## What it asked for

_Nothing._
## Its own summary

Discovered owner priorities and live devices, then recorded a new cross-node capability and integration change: a browser booking/appointment preview is checked against the Mac calendar and travel buffers, held by relay across link loss, and announced on the pendant before a single-use approval token permits submission. Told faculty-judgement about it.

**Biggest unknown:** The system still lacks authoritative 24 kHz audio acceptance thresholds and production pendant constraints, plus a verified browser pre-submit interception hook and typed Mac calendar/travel-buffer reader. The granted inventory is empty this round, so I cannot claim those implementation pieces landed.

