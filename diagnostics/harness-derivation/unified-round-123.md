# Harness derivation — unified — round 123

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser bridge live status** — Safari browser bridge is online with 3 tabs and zero pending commands as of 2026-08-07T17:43:56.897Z; current tab is example.com titled “Failed to open page”.
  - evidence: GET /browser/status returned online:true, tabCount:3, pendingCommands:0.

## Capabilities it proposed

### "“Make the pendant work as my voice terminal even when LTE is unavailable.”"
- **useful because:** This is the most immediately valuable missing behavior: the physically connected nRF9160 and ESP32 can be used today over USB, so the owner gets live voice instead of a dead wearable while LTE registration is absent. When LTE returns, the same conversation should continue without restarting.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → dashboard
- **model tier:** Realtime for the live conversation; a cheap background worker records the handoff and reconciliation receipt.
- **latency:** Local USB fallback should begin within 300 ms and keep round-trip conversational latency under 700 ms; LTE transition may take up to 2 s with no lost committed turn.
- **cost:** Negligible incremental model cost; local USB audio dominates. A fallback turn costs the same realtime inference as today, while health probes are sub-cent.
- **security:** USB audio and transcripts remain on the owner's Mac unless the live relay is explicitly selected. Never silently upload buffered offline speech; announce link mode and require confirmation before sending queued audio or actions.
- **missing:** A USB-serial audio/control adapter for the Mac harness; A relay session handoff protocol with sequence numbers and duplicate suppression; A pendant-visible link-mode indicator and reconnect state machine; End-to-end acceptance test with LTE absent, then restored

### "“Move this conversation to my Mac, use my logged-in browser if needed, and let me pick it back up on the pendant.”"
- **useful because:** The pendant is ideal for speaking and interruption, while the Mac/browser are the only surfaces that can inspect private pages and perform multi-step work. A resumable handoff would make the hive feel like one assistant rather than disconnected agents.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime only for the short handoff utterance; background/local planner handles browser work and writes a compact checkpoint.
- **latency:** A handoff receipt in under 1 s; resume should speak the current state in one short sentence within 2 s. Long browser work runs asynchronously.
- **cost:** One small realtime turn plus cheap planner calls; checkpoint storage is tiny and dominates neither latency nor cost.
- **security:** The checkpoint must include tab/session IDs but not page secrets or full private content. Browser actions remain reversible/draft-first, and any send/purchase requires the existing confirmation policy.
- **missing:** Cross-surface conversation checkpoint schema with expiry; Session-bound browser context reattachment and spoken resume event; A pendant gesture/phrase to resume the latest checkpoint; Unified receipt linking relay, Mac job, and browser command IDs

### "“When I’m interrupted, save exactly where we were and bring me back up to speed when I tap the pendant.”"
- **useful because:** Real wearable use is fragmented. A durable, privacy-scoped interruption card would preserve the last question, pending decision, evidence links, and unfinished action, then give a concise spoken catch-up without replaying or repeating work.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Cheap background summarization creates the card; realtime is used only to deliver the short spoken catch-up or clarify a decision.
- **latency:** Capture in under 500 ms on disconnect/button press; catch-up audio starts within 1 s after resume.
- **cost:** A few hundred tokens per interruption card; no extra inference on ordinary uninterrupted turns.
- **security:** Cards need TTL, encryption, and sensitivity labels. Do not store raw microphone audio by default; private browser snippets should be represented by citations and hashes, not copied content. Destructive pending actions must be clearly marked and never auto-resumed.
- **missing:** Disconnect/button event ingestion from the pendant; A compact checkpoint store with TTL and sensitivity filtering; Resume speech protocol and idempotent action status lookup; Owner-facing list of active interruption cards

### "“When I ask where an answer came from, show me the exact evidence on my Mac and read me the relevant sentence on the pendant.”"
- **useful because:** Today answers, browser work, and receipts are separate. The owner should be able to challenge any spoken claim and get a synchronized evidence view: the Mac opens the exact logged-in tab or local file region while the pendant speaks a short quotation, timestamp, and confidence—without exposing unrelated private page content.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheap model to select and compress already-captured evidence; reserve realtime for the owner’s spoken follow-up and short quotation.
- **latency:** Evidence response begins within 2 seconds; Mac navigation and highlighting may complete within 5 seconds.
- **cost:** Low: mostly retrieval and one short synthesis, with no new model call if an existing citation matches.
- **security:** Only reveal evidence from the current authorized session; redact secrets and unrelated DOM. Never navigate to a logged-out or different account. Require confirmation before opening an external URL.
- **missing:** A general claim-to-evidence index for spoken turns; Browser/local-file anchor protocol that can highlight an exact quote; A synchronized spoken evidence response event; Redaction and authorization checks across browser and Mac sources

### "“Notice when I’m in a loud place and make the pendant harder to misunderstand.”"
- **useful because:** A wearable that speaks identically in a quiet room and beside traffic is unsafe and frustrating. The pendant should locally estimate noise and speech intelligibility, tell the relay to shorten and repeat critical answers, and have the Mac render an optional full transcript so the owner does not lose detail.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** A tiny local classifier handles noise level; a cheap background model rewrites responses for clarity. Realtime is used only for the live turn.
- **latency:** Noise adaptation under 150 ms; the next response uses the new policy without an extra conversational turn.
- **cost:** Near-zero inference cost for local RMS/VAD; occasional cheap rewriting adds a few cents at most per noisy session.
- **security:** Keep raw microphone audio on-device for classification and discard it. Do not infer location or record an environment profile. Make adaptive shortening visible with one distinct tone or spoken cue.
- **missing:** Firmware VAD/noise estimator calibrated against the actual I2S microphone; A link-level speech-policy field in the relay protocol; A Mac transcript mirror for deliberately shortened responses; Acceptance tests across traffic, wind, and overlapping speech


## Changes it proposed to its own stack

### `integration` — Add a USB-local pendant transport beside LTE: a Mac daemon opens /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA, packetizes the existing Opus frames with a monotonically increasing session/sequence header, and exposes the same pipeline audio/events contract. The relay chooses USB or LTE per measured heartbeat and performs a two-phase handoff (stop accepting old path, replay only missing sequence numbers, then resume).
- **owner gets:** Their wearable remains usable today while physically tethered to the Mac and can move back to LTE later without restarting a conversation or duplicating speech.
- effort: Medium-high: Mac serial daemon, pendant framing changes, relay state machine, and hardware-in-loop tests.  ·  risk: A bad handoff could duplicate audio or strand a session; recover by keeping a short jitter/replay window and falling back to the last healthy path. No automatic upload of queued audio.
- cost: No model-cost change; one small always-on Mac process and modest serial CPU.  ·  latency: USB path should be faster than LTE; handoff adds up to 2 seconds only during transition.
- security: Treat USB as local trusted transport, authenticate the daemon with a per-install key, and visibly announce whether audio is local or remote.
- depends on: A USB-serial adapter implementation; Sequence-aware relay session handoff; Pendant firmware link-mode state machine

### `context` — Create a signed CrossSurfaceCheckpoint object linking relay session ID, latest turn ID, Mac job ID, browser session/tab IDs, pending action state, citations, sensitivity labels, and expiry. Write it atomically at interruption/handoff, then make resume consume it idempotently and emit one receipt rather than replaying commands.
- **owner gets:** They can stop speaking, use the Mac/browser for the hard part, and later tap the pendant to hear exactly what is still pending—without repeated actions or lost decisions.
- effort: Medium: schema, atomic storage, projection filters, and adapters in relay, Mac planner, and browser bridge.  ·  risk: Stale checkpoints could mislead; reject expired/session-mismatched records and speak that the state is stale instead of acting.
- cost: Tiny storage and cheap summarization; no realtime call needed to persist a checkpoint.  ·  latency: Sub-100 ms write; resume lookup under 200 ms before speech.
- security: Do not copy private page bodies into the checkpoint; store references/hashes and enforce sensitivity/TTL.
- depends on: Cross-surface checkpoint API; Browser session reattachment; Unified receipt index

### `firmware` — Implement a pendant interruption state machine using the single button and LED: short press marks a resumable checkpoint, long press cancels pending work, and link loss enters a local amber/heartbeat state. Persist only a compact checkpoint token (session hash, turn counter, mode, CRC) in flash; the Mac/relay resolves the token to private context.
- **owner gets:** A glance and one tactile gesture are enough to pause or resume safely when the owner is walking, driving, or cannot reach the Mac; the device never needs to retain sensitive transcripts.
- effort: Medium firmware plus relay event handlers; test button bounce, power loss, and reconnect races.  ·  risk: Accidental presses could cancel or mark work; use distinct press durations and LED confirmation, with no destructive action performed locally.
- cost: Negligible power and flash; under 2 KB firmware state and well under 1 KB RAM.  ·  latency: Immediate local feedback; server resolution on resume depends on link.
- security: Token is opaque and non-sensitive; bind it to device identity and expire it server-side.
- depends on: Cross-surface checkpoint schema; Pendant event uplink over USB/LTE; Owner-confirmed gesture semantics

### `new-surface` — Add a two-person interpreter mode spanning the pendant and Mac: the pendant button starts/stops alternating-speaker turns, local firmware marks speech boundaries, the relay translates each turn, and the Mac displays the original plus translation with speaker labels. Playback must suppress the owner’s outgoing turn until the translated incoming turn is complete, with a tactile/LED cue for whose turn is active.
- **owner gets:** The owner could use the worn device as a private live interpreter in a shop, appointment, or travel conversation instead of repeatedly handing over a phone or manually switching apps.
- effort: High: speaker-turn protocol, translation routing, echo/overlap handling, Mac transcript UI, and field testing with the existing half-duplex LTE link.  ·  risk: Translation errors or leaked speech could cause real harm. Show the original alongside every translation, announce uncertainty, provide an immediate cancel gesture, and default to local USB mode when LTE is unavailable rather than buffering speech for upload.
- cost: One translation inference per speaker turn; use a cheaper translation model by default, with realtime only for low-latency audio pacing. No new hardware required for a prototype.  ·  latency: Target 1.5–3 s per translated turn; overlapping speech must be rejected or queued explicitly rather than silently dropped.
- security: Do not persist raw audio by default. Encrypt transient transcripts, expire them after the session, and require an explicit start cue before the microphone becomes conversationally active.
- depends on: A speaker-turn marker in pendant audio packets; Relay translation stream with cancellation; Mac transcript/translation surface; A clear owner-selected language pair and privacy policy


## What it asked for

_Nothing._
## Its own summary

Round 123 produced three new owner-facing capabilities and three implementation changes: (1) USB-local pendant voice fallback with lossless LTE handoff, (2) spoken conversation handoff between pendant, Mac, and logged-in browser, and (3) interruption cards resumed by a pendant gesture. Changes specify the missing sequence-aware transport, signed cross-surface checkpoint object, and a local button/LED interruption state machine. Hardware reality is favorable today: both chips are USB-connected, while LTE is not registered. I also verified the Safari bridge is online with 3 tabs and zero pending commands, though its current tab reports “Failed to open page.”

**Biggest unknown:** The exact live POST schemas and firmware framing needed to implement the USB audio/control adapter and checkpoint handoff are still unspecified. I still need an implementable serial protocol contract, end-to-end audio acceptance thresholds, and owner-approved button/LED gesture semantics; the previously queued audio-path contexts/tools would resolve most of this.

