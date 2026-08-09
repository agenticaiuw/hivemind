# Harness derivation — mac-planner — round 212

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “what changed in my work portal?”, have the pendant give me only new, actionable items since the last check—without reading the portal aloud or mixing in routine mail."
- **useful because:** This turns an authenticated browser session into a durable, low-noise alert channel. The browser extension can inspect the already-open portal, the relay can remember a per-site cursor and rank changes, and the pendant can deliver a short answer while walking. It is specifically browser-session work, not a generic morning briefing.
- **path:** browser → relay → pendant → mac
- **model tier:** background for portal diffing and ranking; realtime only to answer a follow-up spoken question
- **latency:** under 10 seconds for an on-demand delta; under 2 minutes for a scheduled watch after the portal heartbeat
- **cost:** roughly $0.01–$0.05 per check depending on extracted page size; browser extraction and authenticated session polling dominate, not model tokens
- **security:** Only the browser extension sees authenticated content. Send structured diffs and redacted snippets to the relay, never passwords or full page dumps; per-site watches must be explicitly enabled and pause on logout or navigation to a different account. Speaking item titles aloud needs the existing inbox policy.
- **missing:** browser watch/diff cursor and per-site selectors in the browser harness; a relay route to persist last-seen hashes and urgency decisions for authenticated pages; an owner-configured schedule and site allowlist (not invented by the agent); a reliable LTE or USB-tethered delivery path for the pendant when the Mac is not nearby

### "Tonight, research this question and leave me a trustworthy packet on my Mac by morning: a one-page answer, source links, and a list of claims you could not verify. Tell me on the pendant when it is ready."
- **useful because:** This is the highest-value cross-node job: the relay can work while the owner sleeps, the browser can use sessions unavailable to the cloud, and the Mac can atomically stage a readable deliverable instead of dumping chat into a folder. The pendant is the completion signal and can answer “what is it?” without requiring the owner to find the file.
- **path:** pendant → relay → browser → mac
- **model tier:** background model for collection, extraction, and synthesis; realtime model only for the owner's spoken kickoff and morning questions
- **latency:** minutes to hours depending on scope; morning handoff should be under 5 seconds after the Mac receipt exists
- **cost:** about $0.10–$1 per packet; browser page extraction and repeated claim/source checks dominate
- **security:** Keep authenticated browser material local to the browser bridge; send only selected evidence excerpts and URLs to the relay. Every claim needs provenance and a confidence/unsupported label. Stage into an allowlisted workbench root, never overwrite an existing packet, and require an owner policy entry before opening or emailing anything.
- **missing:** a durable scheduled research job with retry and deadline semantics; browser-side source capture that preserves URL, title, timestamp, and excerpt boundaries; a synthesis schema that requires claim-to-source links and an explicit unverifiable section; a relay-to-pendant completion alert carrying the workbench receipt

### "If I engage privacy on the pendant, make the whole workspace private: stop pendant capture/playback, mute the Mac's input, pause authenticated browser watches, and lock the screen; when I release it, restore only what was active before and tell me what could not be restored."
- **useful because:** The current privacy latch protects the pendant but does not protect the nearby Mac or browser sessions. One physical action should create a coherent privacy boundary across every surface, especially when the owner needs to step away from a live meeting or shared room. The USB-connected pendant makes this testable now even though LTE is unregistered.
- **path:** pendant → mac → browser → relay
- **model tier:** deterministic firmware/event handlers and Mac/browser actions; no model call required except an optional spoken failure summary
- **latency:** under 500 ms from the pendant event to local Mac mute/lock; relay reconciliation within 5 seconds after link recovery
- **cost:** negligible per invocation; cost is implementation and a small state record, not inference
- **security:** Entering privacy must be local and must not wait on relay confirmation. Preserve only app identifiers and prior mute/watch state, never microphone data or page contents. Restore must be policy-controlled and conservative: if a meeting app or browser session changed while private, leave it paused and report the exception. USB serial identity must be authenticated so another process cannot spoof the event.
- **missing:** a pendant-to-Mac USB serial event transport (the requested mac_serial_exchange capability is still unavailable); a Mac privacy transaction that snapshots/restores system and meeting-app audio state; browser watch pause/resume tied to a privacy epoch; an explicit owner policy entry defining whether lock-screen and browser-session suspension are automatic

### "Let me start a long-running task from the pendant, but make it physically contingent: it may prepare drafts and stage files while I’m away, yet it can only publish, send, delete, or change an external system while my authenticated pendant is present. If the pendant disappears, pause safely and tell me exactly what is waiting."
- **useful because:** This gives the owner unattended preparation without unattended irreversible consequences. The pendant becomes a real-world presence key shared by the relay, Mac, and authenticated browser—not another software confirmation dialog that can be clicked by the wrong session. It is especially useful for overnight research, filing, messages, and browser workflows.
- **path:** pendant → relay → mac → browser
- **model tier:** deterministic policy and cryptographic state machine; background models may prepare drafts, but no model is needed to decide presence or release a side effect
- **latency:** presence loss should pause release within 1 second locally; presence restoration and a spoken pending-work summary within 5 seconds
- **cost:** under $0.01 per task beyond ordinary model work; engineering cost is dominated by device attestation, lease renewal, and making every external side effect resumable
- **security:** Presence must mean an authenticated pendant lease, not mere USB enumeration or a bearer token. Use challenge-response, short leases, monotonic counters, and fail-closed expiry. Prepared drafts must be isolated from published state; browser credentials and page contents stay in the browser. The owner must explicitly choose which action classes require presence, and a lost pendant must not leave a lease valid.
- **missing:** pendant firmware support for an authenticated rotating presence lease over USB and eventually LTE; relay-side lease issuance, revocation, and event ordering across reconnects; Mac and browser executors that split prepare/stage from commit/publish and can safely pause at the boundary; an owner-configured action-class policy naming which side effects require physical presence


## Changes it proposed to its own stack

### `integration` — Add a USB-tether session coordinator that treats the physically connected nRF9160 pendant and ESP32 bridge as a local gateway: discover both serial endpoints, authenticate a short-lived session, forward queued pendant inbox/bookmark/audio receipts to the relay, and expose link-loss/reconnect state to the Mac job queue. It must be an actual state machine (discover, handshake, sync, idle, reconnect), not a polling script.
- **owner gets:** The owner can use the worn device today while it is attached to the Mac, despite the pendant not being LTE-registered. Offline bookmarks and alerts would become useful immediately, and a dropped cable would no longer silently strand messages or leave the owner guessing whether a command reached the pendant.
- effort: Medium-high: serial framing/authentication, concurrent bridge and pendant sessions, durable sequence acknowledgements, and integration with relay jobs. Hardware is already connected at the documented USB paths; no board change is needed.  ·  risk: A reconnect or duplicate delivery could repeat an alert or audio chunk. Use monotonic sequence numbers, idempotent manifests, and acknowledgement before deletion; expose a receipt and retain failed payloads. Never treat USB presence as proof of owner intent for high-impact Mac actions.
- cost: Near-zero API cost; approximately 1–2 weeks engineering. No new hardware cost or meaningful power draw beyond the already-connected boards.  ·  latency: Local event delivery should be sub-second; initial sync may take seconds to minutes for queued audio, with bounded backpressure so it cannot starve Mac work.
- security: The serial endpoints need challenge-response authentication and per-session keys; redact payloads in logs. USB attachment alone should authorize transport only, not arbitrary desktop actions.
- depends on: mac_serial_exchange capability or an equivalent narrowly scoped serial read/write route; a relay endpoint for device sync receipts and queued inbox delivery; firmware sequence numbers for the existing offline queues


## What it asked for

_Nothing._
## Its own summary

This round I added three owner-facing capabilities and one concrete integration change: browser-session “what changed” deltas, overnight sourced research packets with atomic Mac handoff, a cross-surface privacy boundary, and a USB-tether session coordinator for the physically connected pendant/audio bridge. I re-discovered the live device set: Safari online and home-macbook-bridge online; the pendant is physically present but LTE is not registered. The strongest immediate opportunity is USB tethering, because it makes offline bookmarks, inbox alerts, and delivery receipts work today rather than waiting for cellular registration.

**Biggest unknown:** I still need a narrowly scoped mac_serial_exchange capability (serial discovery/read/write with framing and authentication) to test and implement the USB path. I also need the relay-side device-sync contract and confirmation of whether /watches is a real live route, plus the owner’s explicit policy for automatic Mac lock/mute and browser-watch suspension. Accessibility/Screen Recording remain owner-side TCC grants and are not needed for the USB sync design.

