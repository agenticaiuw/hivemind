# Harness derivation — ios-control — round 4

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Read the last few iPhone notifications and tell me which ones need me; draft replies, but don’t send anything.”"
- **useful because:** The phone is where time-sensitive personal work arrives, while the pendant is the only interface always available. It combines ambient iPhone observation with safe triage instead of forcing the owner to pick up the phone.
- **path:** pendant → relay → mac-bridge → iOS → dashboard
- **model tier:** realtime for the spoken request and concise summary; gpt-5.6-luna background/local planner for notification grouping and draft generation; no model call for OCR extraction beyond the existing vision tier.
- **latency:** 3–6 seconds when mirroring is active; if the phone is picked up or the Mac is locked, say unavailable and retain the request rather than acting blindly.
- **cost:** Usually one realtime turn plus one small planner/vision pass, roughly $0.01–$0.05; OCR and local event transport dominate latency, not tokens.
- **security:** Notification contents leave the phone through the Mac bridge and relay unless OCR is kept local. Never send replies without explicit confirmation; redact notification text from durable logs and require Face ID/owner presence for sensitive apps.
- **missing:** A local iOS mirroring inspector/control daemon with notification-region capture and pause/lock state; A direct relay-to-iOS-node authenticated channel independent of Mac planner routing; App-sensitive redaction and confirmation policy

### "“When I say ‘put this on my phone’, send the current answer or a selected note to the iPhone, opening the right app and leaving it ready for me to review.”"
- **useful because:** It closes the gap between voice conversation and the device where the owner actually reads and edits things. The owner can capture an idea while walking, then find a reviewable draft on the iPhone without dictating app-specific steps.
- **path:** pendant → relay → mac-bridge → iOS → dashboard
- **model tier:** realtime parses the short command; background/local planner chooses the target app and formats the payload. Use the expensive model only for ambiguity; deterministic templates handle Notes, Reminders, and clipboard handoff.
- **latency:** Under 5 seconds for Notes/clipboard; up to 10 seconds if an app must launch through mirroring. Queue safely when mirroring is paused and notify on resume.
- **cost:** Near-zero to $0.01 per invocation for deterministic destinations; ambiguity resolution is the dominant model cost.
- **security:** Writing to the phone is reversible only if drafts are used. Never tap Send, Buy, Delete, or Share without confirmation. Payload should be encrypted in transit and expire from relay storage after handoff.
- **missing:** Target-app adapters for iOS mirroring (Notes, Reminders, Messages draft); A frontmost-window lease that safely brings Mirroring to the active Space before pointer events; Reliable completion receipts from the iOS node

### "“Keep trying that phone task, and tell me when it is ready—without touching anything if I pick up my phone.”"
- **useful because:** This makes iPhone automation dependable in daily life: mirroring naturally pauses when the owner uses the phone, so queued work can wait and resume rather than fail or click the wrong place. The pendant can report completion without the owner watching the Mac.
- **path:** pendant → relay → mac-bridge → iOS → dashboard
- **model tier:** Deterministic state machine for pause/frontmost/lock detection and retries; gpt-5.6-luna only replans after a UI change or failed receipt; realtime speaks only state changes.
- **latency:** Detect pause within 1 second, stop pointer injection immediately, resume within 2–5 seconds after mirroring returns. Locked Mac remains a hard stop with a clear queued status.
- **cost:** <$0.01 for normal runs; costs occur only on UI replanning after a failure.
- **security:** A hard interlock must refuse all taps/types when pixels are absent or Mirroring is not frontmost. Queue contents should be encrypted and expire; owner confirmation required before any external side effect.
- **missing:** Mirroring lifecycle and pixel-availability telemetry exposed to relay; A persistent idempotent iOS job queue with pause/resume receipts; A direct relay push channel to the pendant for completion announcements

### "“Move the one-time code I’m looking at on my iPhone into the waiting browser form, without reading it aloud or saving it.”"
- **useful because:** Today the owner must manually transcribe fragile OTPs between the phone and browser. A private, ephemeral bridge would remove errors while keeping the secret out of speech, logs, screenshots, and durable memory.
- **path:** pendant → relay → mac-bridge → iOS → browser → dashboard
- **model tier:** Deterministic local OCR and field targeting; realtime only handles the spoken request and confirmation. No cloud LLM should receive the code.
- **latency:** 2–4 seconds while Mirroring and the browser are available; fail closed if either surface is stale, locked, or ambiguous.
- **cost:** Negligible API cost; local OCR, encrypted handoff, and browser field focus dominate.
- **security:** OTP is highly sensitive. Keep pixels/OCR on the Mac, encrypt in memory between iOS satellite and browser extension, zeroize after one paste, never persist or speak it, and require the owner’s explicit request for each transfer. Refuse password fields and non-OTP destinations.
- **missing:** A local-only OCR extractor that recognizes OTPs without sending screen content to the relay; A one-shot encrypted handoff channel between iOS satellite and browser extension; Browser field classification and zeroization receipt

### "“If a call or meeting starts while I’m wearing the pendant, tell the caller I’ll respond later only after I approve the exact message.”"
- **useful because:** The phone knows the incoming caller and meeting context, while the pendant is the only interface that can ask discreetly without the owner opening the phone. It prevents missed commitments without autonomous social messages.
- **path:** pendant → relay → mac-bridge → iOS → browser → dashboard
- **model tier:** Deterministic event correlation for calls/calendar/focus state; realtime composes a one-sentence spoken approval prompt; planner is used only to draft alternatives from calendar context.
- **latency:** Announce within 2 seconds of the event; sending occurs only after an explicit pendant button/voice approval, with a 30-second expiry.
- **cost:** Usually <$0.01 per event; realtime drafting and speech are the main costs, with local event correlation free.
- **security:** Never infer approval from silence or a casual utterance. Show/speak the exact recipient and message, require explicit confirmation, and keep call/calendar content out of persistent logs. Do not act while the phone is being actively used or the Mac is locked.
- **missing:** Read-only iOS call/calendar event stream with recipient identity; A pendant confirmation primitive bound to the displayed message hash; A Messages/phone action adapter that can send only the approved text

### "“When I leave my phone behind, warn me through the pendant and show me the last safe place it was seen; don’t contact anyone or change settings.”"
- **useful because:** The pendant and phone occupy different physical locations, so together they can catch the common failure of leaving the phone behind—something neither a Mac nor a phone-only app can reliably do. The owner gets a discreet warning before the loss becomes expensive.
- **path:** pendant → relay → mac-bridge → iOS → dashboard
- **model tier:** Deterministic proximity/heartbeat and last-seen state; no LLM needed except optional natural-language phrasing.
- **latency:** Detect a missing heartbeat within 30–60 seconds; speak one concise warning and update the dashboard. Suppress warnings while the owner is intentionally stationary or phone use is detected.
- **cost:** Near-zero model/API cost; periodic encrypted heartbeats are the dominant resource use.
- **security:** Location is sensitive. Store only coarse last-seen location or named zone, encrypt it, expire history quickly, and expose it only to the owner. This must be warning-only: no remote lock, wipe, calls, or messages.
- **missing:** A phone-to-pendant proximity/heartbeat protocol that works without relay LTE registration; A local Mac bridge fallback while USB-connected; A privacy-preserving last-seen zone store and false-alarm suppression


## Changes it proposed to its own stack

### `new-surface` — Create an iOS-control satellite on the Mac: a small signed local daemon owns the iPhone Mirroring window, continuously publishes read-only pixel/OCR/lifecycle state to the relay, and accepts short-lived, capability-scoped action leases. The relay addresses this satellite directly as an independent node; mac-planner becomes an optional coordinator rather than the transport. Every action requires a current frontmost-window lease plus pixel proof, and produces an idempotent receipt with pause/lock reasons.
- **owner gets:** The owner gets one reliable phone agent that can answer and queue work from the pendant without depending on the Mac planner being in the conversational path. It can safely wait while they use the phone and resume later, instead of silently failing or risking a tap on the desktop.
- effort: Medium-high: local daemon, relay registration/auth, lifecycle telemetry, action leases, receipt protocol, and a small iOS-specific planner adapter. Can be prototyped now over the existing USB-connected Mac with no phone hardware changes.  ·  risk: A daemon bug could inject unintended actions or expose private screen data. Recover with default-deny leases, frontmost/pixel interlocks, kill switch, action allowlists, and automatic expiry; retain read-only mode as fallback.
- cost: Low recurring API cost; OCR can remain local and planner calls happen only on ambiguous UI. Rough engineering effort 1–2 weeks; no hardware cost.  ·  latency: Read state every 0.5–1 s locally; relay command round trip roughly 100–500 ms plus mirroring UI settling. Better than routing every action through the general Mac planner.
- security: Improves isolation if the satellite has a separate key and narrow scopes, but creates a new privileged local endpoint. Encrypt relay traffic, rotate keys, bind to the known Mirroring process/window, redact screenshots, and require confirmation for external side effects.
- depends on: A granted ios_mirroring_inspect capability or equivalent local capture/OCR API; Relay registration and push route for a non-LTE Mac-local node; Persistent job receipts carrying paused/locked/frontmost state


## What it asked for

_Nothing._
## Its own summary

This round produced three distinct cross-node owner capabilities: (1) spoken notification triage with drafts but no sends, (2) “put this on my phone” reviewable handoff, and (3) pause-safe phone jobs that stop on pickup/lock and resume with receipts. I also proposed the highest-value structural change: a direct relay-addressable iOS-control satellite on the Mac with read-only pixel/OCR state, frontmost/pixel interlocks, scoped action leases, and idempotent receipts—so the iPhone node is independent in routing while remaining physically Mac-local. The owner can test the USB-connected setup today; LTE registration is not assumed.

**Biggest unknown:** Exact ios_* harness actions and lifecycle telemetry remain unknown, as does whether relay can register/push to a Mac-local node independently of mac-planner. I asked mac-planner and relay-realtime for those inventories; the already-pending ios_mirroring_inspect grant is still needed. The direct satellite also needs relay registration, pause/resume receipts, and a safe frontmost-window lease.

