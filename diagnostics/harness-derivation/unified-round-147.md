# Harness derivation — unified — round 147

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Why did my last request fail—and can you fix the broken part without doing the task twice?”"
- **useful because:** Today a timeout, stale browser lease, dead bridge, or rejected action collapses into the same vague failure. This gives the owner a correlated explanation and a safe repair attempt, then revalidates the original job rather than silently replaying it.
- **path:** relay-realtime → mac-planner → browser-extension → mac-vision → unified
- **model tier:** background for correlation and hypothesis generation; realtime only to summarize over the pendant
- **latency:** Diagnosis under 3 seconds from existing receipts; an idempotent repair may take up to 20 seconds, with progress spoken only at milestones.
- **cost:** ~$0.01–$0.04 per incident, dominated by background synthesis; most evidence is local structured reads.
- **security:** Only bound tabs/apps and the named job are inspected. Repairs must be allowlisted and dry-run first; no automatic replay of unrepeatable or unknown actions. Ask before any repair that changes settings or opens a permissions pane.
- **missing:** A durable incident-to-job correlation ID carried from relay through Mac and browser receipts; A policy executor that consumes the existing repair_dry_run output and permits only idempotent repairs; A post-repair revalidation hook that compares the original plan digest and action receipts

### "“Before I say anything sensitive, prove that the pendant, relay, Mac, and browser are all private right now.”"
- **useful because:** A privacy latch can stop local capture, but the owner currently has no single human-readable proof that queued audio, relay persistence, playback, and browser exposure have converged to stopped. This turns a physical safety action into a verifiable state, not a hopeful LED.
- **path:** unified → relay-realtime → mac-planner → browser-extension → mac-vision
- **model tier:** deterministic checks first; background model only to explain discrepancies
- **latency:** A receipt in under 2 seconds after the latch event; if any surface is stale, say exactly which one and do not claim privacy.
- **cost:** <$0.005 per check; structured reads dominate, with no model call on the healthy path.
- **security:** The proof must be authenticated and minimize data: states, timestamps, queue counts, and hashes only—never transcript or raw audio. A stale or unverifiable surface is a failure, not an implicit pass. Clearing a stuck queue requires explicit confirmation.
- **missing:** A pendant-signed latch event and monotonic counter carried into the convergence receipt; Relay-side stop barrier that rejects late audio after the latch counter; Browser extension acknowledgement that microphone/tab capture and pending commands are stopped, not merely that the tab is online

### "“I missed the last few seconds—repeat only the unheard part, starting where playback actually stopped.”"
- **useful because:** A relay acknowledgement is not the same as hearing: Bluetooth can stall after delivery, and repeating the whole answer is frustrating and can expose already-heard sensitive content. The pendant/bridge receipt can identify the exact interruption boundary so the relay regenerates or resumes only the missing tail.
- **path:** relay-realtime → unified → mac-planner → pendant → mac-vision
- **model tier:** realtime for the short repair turn; deterministic sequence alignment and receipt lookup before any model call
- **latency:** Detect a playback gap within 1 second; begin the missing-tail response within 2 seconds after the owner's request.
- **cost:** ~$0.01–$0.03 per repair, dominated by regenerating a short TTS tail; no cost when a cached encoded segment is still available.
- **security:** Retain only encrypted, bounded, content-addressed segments until playback completion plus a short expiry; never infer hearing from relay delivery. Require the owner to ask for replay, and invalidate segments on the privacy latch. Do not replay across a conversation boundary without a matching turn nonce.
- **missing:** Bridge-to-pendant playback cursor receipts with monotonic frame ranges and interruption reason; Relay segment cache keyed by turn nonce and frame range, with secure expiry and privacy-latch invalidation; A TTS/streaming API that can start at a semantic or audio-frame boundary without repeating the already-heard prefix

### "“Compare the pages I have open, but do not send private tabs or their contents off my Mac; show me exactly which tabs were included.”"
- **useful because:** The owner can ask for browser research today, but the boundary is coarse: an authenticated open-tab brief can accidentally include a personal tab. This gives him a practical research mode that is useful precisely because the browser session remains local and inclusion is auditable.
- **path:** browser-extension → mac-planner → relay-realtime → unified
- **model tier:** local Mac model for tab classification, extraction, and redaction; background relay model only receives the selected excerpts and tab IDs
- **latency:** Classify and present the inclusion preview within 2 seconds; comparison within 8 seconds for up to 4 selected tabs.
- **cost:** <$0.02 per comparison; local classification is the dominant step, with relay tokens limited to excerpts rather than full pages.
- **security:** Default-deny for new tabs, login/account/payment/password pages, downloads, and tabs without an explicit owner binding. Show title/domain/fingerprint before transmission; send only extracted passages, never cookies, DOM-wide snapshots, or page history. Require confirmation if a sensitive classification is uncertain.
- **missing:** A browser-side sensitivity classifier that runs before page content leaves the Mac; An explicit per-request tab allowlist and inclusion receipt bound to tab/session fingerprints; A relay route that accepts only redacted excerpts plus citations and rejects unbound raw page payloads; A Mac-local preview UI or spoken confirmation path for the inclusion set

### "“Update the pendant and bridge tonight, but only if you can prove the new firmware boots, preserves privacy/audio settings, and can roll back without leaving me with a dead device.”"
- **useful because:** Firmware changes can currently be technically deployed but are not an owner-visible, cross-device transaction. A failed update could remove the owner's microphone, privacy latch, or 24 kHz path. This makes maintenance a safe household operation with a preflight, staged images, boot confirmation, and rollback evidence.
- **path:** mac-planner → relay-realtime → pendant → unified
- **model tier:** deterministic firmware manifest/signature/health checks; background model only explains the resulting receipt
- **latency:** Preflight under 10 seconds; update may take several minutes, with no conversational interruption and a final spoken receipt.
- **cost:** <$0.01 per update orchestration; USB transfer and hardware test time dominate, not model tokens.
- **security:** Only signed images with device-model/version/anti-rollback metadata may be flashed. Never overwrite the known-good slot until a complete boot-and-audio/privacy self-test passes. Keep serial logs redacted of audio. Require explicit owner confirmation for a production device and refuse if battery/USB stability cannot be verified.
- **missing:** A/B firmware slots or a bootloader with an atomic pending/confirmed image state on both chips; Signed artifact manifest and per-device compatibility/anti-rollback verification; A USB serial flasher/health protocol that can test button, privacy latch, 24 kHz audio, and bridge playback without recording room audio; A durable cross-device update receipt and automatic rollback controller


## Changes it proposed to its own stack

### `hardware` — Replace the prototype ESP32 classic A2DP bridge with an ESP32-S3 module that has external PSRAM and expose a hardware playback-cursor/underrun counter to the pendant link. Keep the current 44.1 kHz SBC output contract, but buffer only encrypted, short-lived encoded segments and report exact played frame ranges, Bluetooth disconnects, and underruns.
- **owner gets:** When headphones stall or reconnect, the pendant can tell the owner exactly what was heard and repeat only the missing words instead of guessing or replaying an entire answer. It also makes audio failures diagnosable rather than silent.
- effort: Medium-high: schematic/module swap, A2DP port validation, cursor protocol, firmware test fixtures, and an enclosure/power recheck.  ·  risk: ESP32-S3 Bluetooth Classic support and the existing precompiled stack must be verified before committing; a failed port falls back to the current HUZZAH32 bridge. More buffering must never become routine raw-audio retention; enforce short expiry and privacy-latch deletion in firmware.
- cost: Roughly +$8–$20 per bridge prototype for an S3 module/PSRAM and level-shifter or PCB changes; modest additional active RAM power, likely tens of mW, to be measured rather than assumed.  ·  latency: Cursor reporting is sub-frame; larger buffers could add latency, so cap them to the existing 60 ms packet cadence and measure end-to-end mouth-to-ear delay.
- security: Encrypted volatile/PSRAM segment cache only, explicit expiry, turn nonce binding, and immediate zeroization on privacy latch; no SD writes and no persistent transcript/audio.
- depends on: audio_delivery_ack_queue must accept bridge-originated frame-range receipts; A2DP Classic support on the selected ESP32-S3 stack must be confirmed; A secure short-lived segment cache and privacy-latch invalidation must be implemented; The owner must accept changing the prototype bridge hardware


## What it asked for

_Nothing._
## Its own summary

Round 147 produced three owner-facing capabilities and one hardware change. The highest-value addition is a failure explainer that correlates relay/Mac/browser/pendant evidence, applies only safe repairs, and revalidates without replaying an unrepeatable action. I also recorded a privacy convergence proof and exact-tail audio recovery, plus an ESP32-S3/PSRAM bridge direction for trustworthy playback cursors. The privacy proposal is intentionally close to the existing latch/convergence work, so its new value is authenticated cross-surface proof rather than another latch.

**Biggest unknown:** The remaining blockers are implementation contracts, not more reconnaissance: pendant-signed latch/playback counters, bridge frame-range receipts, relay stop barriers and expiring segment storage, and a policy executor that can consume dry-run repairs without replaying unsafe steps. The previously requested owner retention/deletion policy is still unanswered; I did not re-ask it.

