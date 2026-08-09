# Harness derivation — mac-terminal — round 265

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Is the pendant-to-headphones path healthy right now? If not, recover it and tell me exactly where it failed.”"
- **useful because:** This is the highest-value everyday capability: it distinguishes pendant capture, USB/LTE/relay delivery, Mac bridge processing, and Bluetooth playback instead of saying “connected” when one segment is dead. It can recover a bridge process or restart the audio route, then verify an actual frame/ack and a real output device.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Cheap background health state machine for continuous probes; realtime model only to explain the result in the owner's words.
- **latency:** Initial answer under 3 seconds; bounded recovery under 15 seconds, with immediate pendant failure state before recovery completes.
- **cost:** Near-zero model cost for probes and deterministic recovery; occasional realtime explanation is the dominant cost.
- **security:** Audio health metadata and device names leave the Mac only as needed; no microphone content is retained. Restarting the bridge/Bluetooth route should be limited to the named audio components and recorded in the existing receipts.
- **missing:** A host-side bounded serial reader/parser for the two currently attached USB chips (the granted serial schema is unresolved; run_shell scripts are the available fallback); A machine-readable audio-chain health contract carrying per-segment sequence, age, and last acknowledgement; A deterministic recovery action for restarting the ESP32 bridge process and re-opening the selected A2DP output

### "“Run the bench acceptance test for the pendant and audio bridge, and give me a go/no-go report with the first failing frame and saved logs.”"
- **useful because:** The hardware is physically present now, so this turns today’s prototype into a repeatable truth check: enumerate both USB links, capture synchronized UART health, inject a short known audio stimulus, and verify the bridge reaches Bluetooth output without overrunning. It catches regressions that a green process-health page cannot.
- **path:** pendant → mac-bridge → dashboard
- **model tier:** Deterministic shell/test harness and a cheap summarizer; no realtime model is needed unless the owner asks a follow-up.
- **latency:** 30–60 seconds per run, with live progress and an immediate fail on missing ports or framing corruption.
- **cost:** Negligible API cost; local serial capture and a few seconds of audio are the dominant resources.
- **security:** USB logs stay on the Mac and contain diagnostics, not conversation audio. The test must use a generated tone or fixture, never open the microphone, and cap log retention and byte counts.
- **missing:** A real implementation of the bounded USB serial diagnostic call (the currently granted schema cannot resolve) or a typed wrapper over POST /execute run_shell; A synchronized framing/CRC parser and known-tone loopback fixture for the nRF9160 and ESP32; A dashboard report that links the test run, per-chip counters, and retained log paths

### "“Do that Mac task, but if it fails, recover only when it is safe, then show me what actually happened and whether the requested end state is true.”"
- **useful because:** This makes the shell tier dependable rather than merely powerful. For a concrete example, a request to reconnect the audio bridge or open a browser workflow would run, detect a nonzero/timeout/transport failure, choose a bounded fallback, and verify the postcondition. The owner gets an answer about the world, not a misleading completed job.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Cheap deterministic failure classifier and postcondition checker; realtime model only for ambiguous recovery choices or the final spoken explanation.
- **latency:** Normal actions remain unchanged; one fallback adds at most 5 seconds, while long-running commands report progress and can be abandoned without claiming success.
- **cost:** Usually zero model calls; fallback and verification are local. A model call is used only when the failure is genuinely ambiguous.
- **security:** No new data needs to leave the Mac. Recovery must be scoped to the requested app/device, preserve the full command/result receipt, and explicitly report when a mutation cannot be verified. Never infer success from process exit alone.
- **missing:** A declarative postcondition field on an action/job (for example, expected audio route, focused app, browser URL, or created file); Per-step exit code, timeout cause, and process identity in receipts, plus a durable retry-attempt link; A recovery planner that can select only idempotent or explicitly reversible fallbacks and then verify the postcondition

### "“Give this one task to my computer until 5 PM: only work on the Acme invoice in the open browser session, stop if the page changes, and show me proof of what changed.”"
- **useful because:** Today the owner can ask the system to act, but cannot express a bounded delegation contract that survives handoffs between pendant, relay, Mac, and browser. This lets them grant a temporary, auditable mandate with a target, expiry, allowed session, and stop conditions—not an indefinite blank check and not a brittle one-shot command.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime model extracts the spoken contract once; deterministic enforcement and expiry run on the relay and local agents. A cheaper model summarizes the final evidence.
- **latency:** Contract acknowledgement under 2 seconds; execution latency depends on the browser task; expiry and stop conditions must be enforced immediately without a model round trip.
- **cost:** One short realtime extraction plus a cheap final summary; enforcement is local and dominates neither latency nor cost.
- **security:** The contract must be scoped by domain, tab/session identity, action classes, object identifiers, and expiry. The browser must refuse actions outside the lease, even if a later planner suggests them. Credentials and page contents stay in the authenticated browser session; the dashboard shows an immutable action/evidence trail.
- **missing:** A first-class lease object with scope, expiry, stop conditions, and revocation state shared by relay, Mac, and browser; Browser-side enforcement that checks every command against the lease rather than trusting the planner; Pendant affordance to revoke the active lease immediately when the Mac is unattended; Evidence records that bind each changed field to the before/after browser state

### "“Before I send this message or submit this form, read back the commitments, amounts, recipients, and irreversible consequences; let me approve the exact diff from the pendant.”"
- **useful because:** The owner gets a meaningful last-mile check rather than a generic confirmation prompt. The browser supplies the authenticated form, the Mac extracts the actual submitted values, the relay produces a compact semantic diff, and the pendant provides a physical approval channel. This catches wrong recipients, amounts, dates, and accidental commitments at the point where they become real.
- **path:** browser → mac-bridge → relay → pendant → dashboard
- **model tier:** Cheap structured extraction first; realtime model only converts ambiguous fields into a spoken summary. Deterministic hash comparison binds approval to the exact pre-submit payload.
- **latency:** 3 seconds or less for ordinary forms; approval remains valid only for a short bounded window and invalidates on any page or field change.
- **cost:** Usually one small structured extraction and a short spoken response; browser snapshot and hashing dominate no API cost.
- **security:** Sensitive fields should be summarized by type and partially redacted, never copied into relay logs. Approval must bind to a canonical payload hash, origin, tab, and expiry; any mutation after approval requires a new approval. No send/submit occurs on silence or stale approval.
- **missing:** Canonical form serialization and semantic field classification in the browser extension; A relay-held approval token bound to payload hash, origin, tab, and expiry; Pendant confirmation protocol that carries the hash/nonce and handles link loss without guessing; A post-submit receipt proving the server accepted the exact approved payload

### "“While I’m away from my Mac, check my already-authenticated work portal, find only items that require my decision today, and read me a two-line brief with the source links.”"
- **useful because:** The owner currently cannot get this from the briefing path because it does not enter authenticated web sessions. This makes the browser’s unique access useful while keeping the Mac and relay out of the credential boundary: the browser reads the portal, extracts only decision-relevant claims, and the pendant delivers a compact interruption instead of a bulk dump.
- **path:** browser → relay → pendant → dashboard → mac-bridge
- **model tier:** Scheduled/background browser extraction with a cheap ranking model; realtime is used only if the owner asks a follow-up by voice.
- **latency:** Run on a 15–30 minute schedule; a new high-priority item reaches the pendant within one polling interval. Follow-up answers under 3 seconds while the browser session is online.
- **cost:** One small extraction/ranking call per changed page or portal batch; unchanged-page detection should avoid model calls. Browser polling and relay delivery dominate operational cost.
- **security:** Never export cookies, full page text, or portal credentials to the relay. Store short-lived claims with source URL, timestamp, and evidence capsule; allowlist the portal origin and require a dashboard opt-in. The pendant should speak only the minimum needed and offer the source link on the Mac.
- **missing:** A browser-session page-watch that supports authenticated work portals and change detection; Structured finding storage with urgency, decision-needed classification, source URL, and evidence capsule; A scheduled relay job that can wake the browser agent and deliver only newly actionable findings; A pendant notification policy that suppresses bulk and duplicate alerts


## Changes it proposed to its own stack

### `integration` — Add a bench-device adapter that registers the physically attached nRF9160 and ESP32 by USB identity, exposes bounded read-only UART frames, and maps them into the same health/event schema as the wearable and relay. It must explicitly label USB as bench-only and never pretend it is LTE registration.
- **owner gets:** The owner can test the real pendant today and get one truthful status view despite the relay reporting the pendant offline; failures become actionable (missing port, framing, encoder stall, bridge silence) instead of “device offline.”
- effort: Medium: host serial implementation, framing parser, registration heartbeat, and dashboard status card.  ·  risk: A stale USB registration could mask an actually disconnected device; expire it aggressively and show transport=USB-BENCH. Malformed frames must be discarded with counters, not treated as healthy.
- cost: Negligible API cost; modest Mac CPU and a few MB of bounded logs.  ·  latency: Health updates within 1 second; no impact on normal wearable path.
- security: Read-only USB diagnostics remain local. Do not expose raw audio or modem credentials through the relay.
- depends on: A real implementation behind the currently unresolved mac_usb_serial_diagnostics schema; A stable framed diagnostic protocol in both firmwares

### `relay` — Introduce a transport-independent audio health record keyed by turn_id and frame sequence: pendant capture, uplink acknowledgement, relay receipt, Mac bridge consumption, resampler output, and Bluetooth presentation each publish last_seq, age_ms, and error. Derive one end-to-end verdict only when every hop agrees on sequence progress.
- **owner gets:** When the pendant goes silent, the owner learns whether the microphone, network, relay, bridge, or headphones failed—and the system stops claiming an answer was heard when only half the path worked.
- effort: High: shared schema, probes in relay/firmware/bridge, sequence propagation, and dashboard/pending-state integration.  ·  risk: Clock skew can make ages misleading; use monotonic counters and local timestamps, and mark unknown rather than interpolate. Extra telemetry must not increase audio buffering.
- cost: Small bandwidth and storage overhead; no routine model cost.  ·  latency: Under 100 ms control-plane overhead if health frames are out-of-band.
- security: Use opaque turn IDs and counters; never include audio payloads in health records.
- depends on: The existing audio_link_truth_and_recovery firmware behavior; A bounded USB bench adapter for current testing; A shared pipeline event schema

### `mac-harness` — Add a postcondition-and-attempt envelope to every Mac action: preserve the original submitted action before any run_shell rewrite, record normalized dispatch action, attempt number, exit/timeout/signal, and a machine-checkable postcondition result. Link the envelope to the job, receipt, and ledger IDs, including recovery attempts.
- **owner gets:** The owner can trust “done” because the system can show both what it actually ran and whether the requested state became true—even when a shell command was rewritten, timed out, or the agent restarted.
- effort: Medium-high: executor receipt fields, orchestrator ledger closure/join, shell process status capture, and postcondition evaluators for files/apps/audio/browser.  ·  risk: Capturing too much command output or environment could leak secrets; store redacted summaries and hashes, not raw environment. A wrong postcondition is worse than no postcondition, so return unknown when unverified.
- cost: Negligible model cost; bounded receipt storage increases disk use slightly.  ·  latency: Milliseconds for receipt work; postcondition checks add at most a few seconds when requested.
- security: Improves auditability without changing the owner’s maximum-access policy; redact AGENT_TOKEN/relay keys and never persist them.
- depends on: POST /execute’s receipt path; A job↔ledger correlation field; Signal-aware run_shell execution and deterministic postcondition evaluators


## What it asked for

_Nothing._
