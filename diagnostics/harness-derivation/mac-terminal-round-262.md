# Harness derivation — mac-terminal — round 262

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-stack-status** — At 2026-08-09T03:16Z the Mac local agent, relay, and Safari extension are online; Safari has one YouTube tab. The nRF9160 pendant remains offline in device inventory. A recent Mac job's shell result already includes argv, exitCode, signal, timeout and outcome fields, so the previously described observability gap is partly closed in the live build. iPhone Mirroring probe reports locked.
  - evidence: GET /ops/snapshot 200; GET /jobs 200 recent entries; device discovery

## Capabilities it proposed

### "“Download this from the page, and tell me on my pendant when the file is genuinely complete and safe to open.”"
- **useful because:** Browser clicks alone cannot tell whether a download is still partial, blocked, or replaced by an HTML error page. This combines the authenticated browser session with the Mac filesystem and the always-available relay, then gives the owner a truthful wearable notification without moving the file through the cloud.
- **path:** browser → mac-bridge → relay → pendant
- **model tier:** Background model only for identifying the intended download and interpreting unusual page results; deterministic Mac checks handle size-stability, quarantine metadata, MIME/magic bytes, and SHA-256.
- **latency:** Begin watching within 1 second of the browser click; notify within 2 seconds after two stable size/hash observations, or immediately on a detected failure.
- **cost:** Very low: browser action plus local filesystem polling and one small relay event; no audio or large artifact upload.
- **security:** The file remains on the Mac. Store only path, size, hash, origin URL, and completion status unless the owner asks to inspect contents. Do not auto-open executables or bypass quarantine. Require explicit confirmation for opening or moving potentially dangerous files.
- **missing:** A browser-to-Mac download transaction ID and completion callback; A bounded local download watcher with magic-byte/quarantine checks; A relay event type for completed/failed download notifications and a pendant rendering policy

### "“Make this the same assistant on my Mac, phone, browser, and pendant—carry my current task and preferences across whichever one is reachable.”"
- **useful because:** Today each surface has partial session state and the owner cannot move an active thought, browser evidence, Mac work, and wearable conversation as one coherent task. A portable, owner-controlled continuity identity would let a phone or Mac take over when the pendant loses LTE, then return the result to the pendant without starting over.
- **path:** pendant → relay → mac-bridge → browser → iOS → dashboard
- **model tier:** Background model maintains a compact task state and resolves references; realtime is used only for the active spoken exchange. Deterministic state replication handles receipts, freshness, and conflict resolution.
- **latency:** Nearby handoff acknowledgement under 1 second; state convergence under 5 seconds after a surface reconnects.
- **cost:** Moderate persistent-state operations; model cost is limited by sending a compact state delta rather than full conversation/context on every handoff.
- **security:** A continuity identity must not become a bearer credential. Use device-bound keys, end-to-end encrypted task envelopes, explicit device revocation, and field-level redaction so browser cookies, phone secrets, and raw audio never replicate by default.
- **missing:** A device-bound continuity identity and key-management protocol; Encrypted delta synchronization for task state, evidence, and receipts; Conflict rules when Mac, browser, and pendant act concurrently; Client support on iOS and the pendant for handoff and revocation

### "“While I’m away, tell me if my Mac or browser session changed unexpectedly, and show me exactly what changed when I return.”"
- **useful because:** The current agent can act with broad Mac access and authenticated browser sessions, but the owner has no compact, trustworthy tamper/change report. A signed baseline of running agent identity, permissions, browser session metadata, and high-impact task receipts would distinguish normal work from an unexpected restart, extension replacement, session logout, or changed authorization.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic local attestation computes the baseline and diffs; a background model summarizes the changes. Realtime only reads an urgent short alert through the pendant.
- **latency:** Baseline update within 2 seconds of a relevant event; urgent pendant alert under 5 seconds; detailed report available on demand.
- **cost:** Low: hashes and metadata only, with occasional background summarization. No screenshots or full browser contents unless explicitly requested.
- **security:** The baseline itself describes installed apps, permissions, and sessions. Keep raw details local, send signed summaries, rotate relay keys, and make the owner re-pair after identity changes. This reports changes; it must not silently revoke access or kill jobs.
- **missing:** A Mac attestation snapshot with stable identity and permission hashes; Browser-extension/session identity change events; A relay-held signed baseline and diff store; Pendant alert semantics for urgent integrity changes


## Changes it proposed to its own stack

### `model-routing` — Add a local-first shell-result interpreter that classifies completed Mac jobs from exit code, signal, timeout, stderr signatures, and bounded stdout before invoking a language model. It should answer routine status questions from structured receipts, extract the next actionable error (for example missing path, permission, network, or serial-port absence), and escalate only ambiguous failures with the minimal relevant excerpt. For multi-step jobs, emit a machine-readable continuation hint rather than resending the entire transcript.
- **owner gets:** The owner gets an immediate, understandable answer to routine Mac work and does not pay a full realtime-model turn for “completed” or “port not found.” When something fails, the explanation points to the next useful action instead of dumping a truncated shell error.
- effort: Medium: define a small deterministic error taxonomy, wire it to job/receipt responses, and add an escalation adapter that selects excerpts and preserves provenance.  ·  risk: A classifier may mislabel an unusual command. It must state uncertainty, never claim success without exit status, and fall back to the full model on unknown signatures.
- cost: Reduces expensive model calls and context resend; adds negligible local CPU and storage.  ·  latency: Routine answers become sub-100 ms after receipt; ambiguous cases add one model call but with much smaller context.
- security: Less stdout leaves the device. Redaction must occur before escalation; avoid sending environment values, tokens, or raw downloaded content.
- depends on: Reliable numeric exit code and timeout fields in shell receipts; A bounded stderr/stdout artifact or excerpt API; A model-router hook in relay_job_status and Mac completion events

### `firmware` — Define a versioned, line-delimited diagnostic protocol on the existing USB console for both chips. On connection, each nRF9160/ESP32 emits a signed-by-firmware hello containing board ID, firmware build, boot reason, monotonic uptime, transport state, audio ring overruns/underruns, last acknowledged frame, and reset/error counters; a host may request a bounded snapshot or clear only volatile counters. Prefix every frame with chip ID, sequence, timestamp, length, and CRC, and keep human logs on a separate channel so bench parsers never have to scrape prose.
- **owner gets:** A plugged-in pendant stops being a mystery: the Mac can tell the owner exactly which chip booted, whether audio is flowing, and whether frames are being lost, instead of showing “offline” while capture scripts scroll by. It also makes a future repair or firmware update diagnosable without sending audio to the relay.
- effort: Medium firmware work on both chips plus a small parser and golden-frame tests; no product LTE transport change.  ·  risk: A malformed diagnostic frame must never affect audio or recording. Rate-limit snapshots, reject writes except the volatile-counter command, and keep the protocol disabled outside the authenticated USB bench mode.
- cost: Under a few KB of flash and a small static buffer; negligible power when USB is absent.  ·  latency: Hello on connect within 250 ms; snapshot under 100 ms and independent of audio timing.
- security: Diagnostic output can reveal firmware/build and counters but no content. Require the existing local-agent authorization for counter reset; never expose raw UART logs remotely.
- depends on: A real bounded serial reader/parser on the Mac (currently missing; mac_usb_serial_diagnostics remains unresolved); Stable frame schemas shared by nRF9160 and ESP32; A dashboard/relay adapter that maps the snapshot into a truthful device status

### `hardware` — Add a low-power BLE companion radio to the pendant, with a hardware-isolated UART bridge to the nRF9160. It should carry only authenticated control, state, and compressed low-rate audio metadata—not raw microphone streaming by default—and support encrypted GATT notifications for queued requests, action receipts, and link health. The nRF9160 remains the LTE/product radio; BLE provides a nearby-phone/Mac continuity path when LTE registration is absent.
- **owner gets:** The owner could still reach the assistant indoors, in a basement, or during LTE failure without plugging the pendant into a Mac. A nearby iPhone or Mac could relay a request and return truthful status while the pendant remains wearable, instead of appearing dead whenever cellular registration drops.
- effort: High: board respin, antenna/RF validation, companion firmware, pairing UX, relay phone/Mac transport, and coexistence testing with audio and LTE power states.  ·  risk: More radio firmware and a larger attack surface. Use authenticated rotating session keys, explicit pairing, replay protection, and a hard rule that BLE cannot unlock devices or execute high-impact actions without the existing action semantics.
- cost: Roughly $3–8 BOM increase plus PCB/antenna work; companion draw approximately 5–20 mA while connected and under 1 mA advertising, depending on duty cycle.  ·  latency: Nearby control acknowledgements under 200 ms; audio continuity depends on the companion codec and should not compete with the nRF9160 microphone hot path.
- security: Introduces a local proximity attack surface. Pairing must require physical button confirmation and device identity checks; do not expose raw audio or bearer credentials over unauthenticated BLE.
- depends on: A phone/Mac BLE relay implementation; A versioned pendant control protocol shared with the cloud relay; Power-budget and RF coexistence measurements on the actual pendant enclosure


## What it asked for

_Nothing._
