# Harness derivation — unified — round 52

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **audio-uplink-gap** — The live pipeline currently reports pendant inputTelemetry sampleRate=15625 Hz while Mac TTS output is 24000 Hz mono PCM; output is native 24 kHz but uplink is not. Browser bridge is offline with 3 pending commands, and Mac computer-use is not ready because Accessibility and Screen Recording are ungranted.
  - evidence: GET /pipeline returned inputTelemetry {sampleRate:15625, format:pcm-s16le} and TTS meta {sampleRate:24000}; GET /ops/status returned browser online:false pendingCommands:3, accessibility trusted:false, screenRecording granted:false, ready:false.

## Capabilities it proposed

### "“Remember this page and why it matters.” Later: “What did I save about the tax form?”"
- **useful because:** A thought made while walking or browsing becomes a durable, searchable memory with the exact private page and evidence attached. Today the pendant, relay, browser session, and Mac each lack the complete chain, so important context is lost or copied manually.
- **path:** pendant → relay → browser → mac-bridge → dashboard
- **model tier:** Use realtime only to detect the short capture command and acknowledge it; use a cheaper background model to transcribe, extract the user's reason, normalize tags, and answer later retrieval queries.
- **latency:** Acknowledge locally/offline in under 300 ms; upload/spool within seconds when linked; background indexing under 30 s; retrieval spoken in under 2 s with a dashboard link.
- **cost:** About $0.005–$0.03 per capture depending on audio length and transcription/model use; storage and embedding/indexing dominate at scale, not realtime inference.
- **security:** Private page URLs, snippets, and voice can leave the pendant to the relay/Mac. Encrypt in transit and at rest, redact obvious secrets, inherit browser session sensitivity, and require confirmation before sharing/exporting or mutating the source page. Provide a physical privacy latch and per-item deletion.
- **missing:** A pendant-local capture/spool skill that survives a dropped link; A relay endpoint for encrypted chunk upload, deduplication, and delivery receipts; Browser bridge support to attach active tab identity and a bounded cited excerpt at capture time; Mac note/index integration with provenance, retention, and deletion controls; A retrieval API joining transcript, page evidence, and time/location metadata; A dashboard review/delete view and explicit user-visible capture indicator

### "“Continue this on my Mac when it reconnects.” The pendant should preserve the exact conversational handoff, then resume in the right browser tabs or app without making me repeat myself or accidentally repeating an action."
- **useful because:** Today a dropped link strands the owner's spoken context on the pendant and leaves the Mac/browser with disconnected pending work. This would make the hive behave like one continuous assistant: the owner can walk away mid-task, regain connectivity later, and receive a precise continuation with what was heard, what was attempted, and what still needs approval.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use realtime only for the immediate handoff acknowledgement. Use a cheaper background model to compress the conversation into a typed continuation capsule, reconcile pending receipts, and prepare the resume plan. Use realtime again only when the owner asks for the resumed spoken interaction.
- **latency:** Pendant acknowledgement under 300 ms, including offline confirmation. Capsule should spool locally immediately and reach the relay within seconds of reconnection. Resume planning within 10 seconds; no action should execute until preconditions and approval state are revalidated.
- **cost:** Approximately $0.005–$0.02 per handoff for transcription/summary and state reconciliation; storage and receipt retention dominate recurring cost. Most handoffs should avoid the expensive realtime tier.
- **security:** The capsule may contain private speech, page URLs, snippets, and pending action details. Encrypt it locally and in transit, bind it to the paired device and session, apply short retention, redact secrets, and require fresh approval whenever the target, fields, tab, or authorization state changed. Never replay an old approval merely because the task text matches.
- **missing:** A versioned continuation-capsule schema containing transcript references, active surface/session/tab identities, action receipts, preconditions, expiry, and approval state; Pendant-local durable handoff storage with bounded size and a visible pending-handoff indicator; Relay reconciliation that deduplicates retries and orders reconnect events without losing or duplicating commands; Mac/browser resume adapters that reattach to the correct workspace and report changed or missing context; A user-facing resume review showing what will happen next and why, with discard/export/delete controls


## Changes it proposed to its own stack

### `integration` — Add a hardware-bound approval handshake for irreversible actions: the relay creates a one-time action digest and nonce; Mac/browser return a human-readable preview plus provenance; the pendant speaks a compact summary and displays a challenge; a deliberate physical button gesture signs the nonce locally. The relay accepts execution only once, records the signed receipt, and invalidates it on any changed field, tab, session, or timeout.
- **owner gets:** When the owner approves sending mail, submitting a form, deleting a file, or buying something by voice, a malicious page or stale preview cannot silently substitute a different action. The owner gets a fast, unambiguous physical confirmation instead of trusting a screen prompt.
- effort: Medium-high: pendant firmware signing/gesture state, relay nonce and receipt service, browser/Mac preview canonicalization, and UI/audio wording; integration tests for replay, edits, disconnects, and prompt injection.  ·  risk: A lost or stuck button could block urgent actions; recover with explicit fallback to dashboard approval and timeout/cancel. Clock skew and link loss must fail closed. Never retain raw private keys in logs; support key rotation and device revocation.
- cost: Negligible inference cost; roughly one small signed JSON receipt per gated action. Hardware cost $0 if secure element/key storage already exists, otherwise $1–$3 for a secure element and a few mW active draw.  ·  latency: Adds roughly 0.3–1.0 s for challenge delivery and signature round trip on a healthy link; offline approval should queue but not execute until relay verification.
- security: Strongly improves origin binding, anti-replay, tamper evidence, and resistance to browser prompt injection. Requires secure key provisioning, encrypted transport, revocation, and clear spoken redaction so secrets are not exposed aloud.
- depends on: Canonical typed action schema shared by Mac and browser; Durable action receipts and undo records; Pendant local privacy latch and deliberate gesture handling; Relay connectivity and device identity/key provisioning

### `firmware` — Close the measured input-path gap: negotiate and validate a real 24 kHz mono PCM uplink between pendant, relay, and Mac instead of accepting the current 15,625 Hz capture while only rendering 24 kHz downlink. Add a capability handshake, frame-level resampling only as an explicit fallback, CRC/sequence checks, and pipeline telemetry that marks native-24k, resampled, or rejected rather than silently labeling every response superwideband.
- **owner gets:** The owner gets the speech quality they asked for and can trust the status indicator. In weak-link conditions the pendant still works, but it clearly reports a quality fallback instead of making a 15.6 kHz recording sound like a completed 24 kHz path.
- effort: High: firmware codec/SAI or ADC configuration, relay frame validation, Mac bridge negotiation, acceptance fixtures, and fault-injection tests for drops, reordering, clipping, and reconnect.  ·  risk: Native 24 kHz may exceed current uplink bandwidth or RAM; recover by negotiating 16 kHz/8 kHz fallback before capture and preserving the user's utterance. A bad resampler can add latency or artifacts, so gate rollout behind telemetry and retain the known-good mode.
- cost: No meaningful per-request model cost; potentially higher LTE-M data volume (about 53% over 15.625 kHz at 16-bit mono) and modest DSP/CPU power. Hardware may require a codec/clock change if the current audio front end cannot generate 24 kHz natively.  ·  latency: Adds a one-time negotiation (<100 ms) and small frame buffering (target <40 ms); native mode avoids a server-side conversion hop.
- security: No new data class, but telemetry must avoid retaining raw audio; authenticated capability negotiation prevents downgrade confusion or a spoofed format declaration.
- depends on: Authoritative 24 kHz audio acceptance criteria; Pendant audio hardware/clock capability confirmation; Relay and Mac pipeline frame-format validation; Audio fault-injection and end-to-end measurement tooling


## What it asked for

_Nothing._
