# Harness derivation — mac-planner — round 116

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Let me have a normal conversation through the pendant even when the connection is busy—keep my speech from disappearing, and keep replies understandable.”"
- **useful because:** The live trace proves 24 kHz TTS is being rendered and accepted (75,734-byte PCM), but the measured LTE-M link drops about 7.8 seconds of uplink when 24 kbps downlink overlaps it. This capability turns the current demo into a conversation that remains usable under the exact condition the owner will encounter.
- **path:** pendant → relay → mac-planner
- **model tier:** Realtime for the conversational turn; deterministic firmware/relay control for congestion decisions; no planner-tier model call.
- **latency:** Add no more than one 20–40 ms control interval. Keep audio playout under 120 ms of additional buffering; a codec-mode change may take one frame (60 ms).
- **cost:** Negligible model cost. Relay CPU/storage rises modestly for packet statistics and short Opus transcode buffers; LTE data may fall because the adaptive mode lowers bitrate during contention.
- **security:** Only transport quality metrics, codec mode, and packet sequence numbers leave the pendant; never audio-derived content. Persist no speech beyond existing retention. No confirmation is needed because this changes transport quality, not an external side effect.
- **missing:** Firmware telemetry for sequence gaps, jitter-buffer depth, modem send-queue occupancy, and button/turn state; A relay codec-negotiation and prioritization state machine that can lower uplink bitrate or pause nonessential downlink frames without dropping speech; Mac TTS output packetization that can emit a negotiated Opus profile instead of always uploading a large 24 kHz PCM blob; An end-to-end fault-injection test that overlaps owner speech and reply audio and verifies bounded loss/recovery

### "“Read this private page for me, but guarantee that passwords, payment details, and other secrets never leave my Mac; tell me exactly what you withheld.”"
- **useful because:** Today browser access and relay access are separate trust decisions: a logged-in page can be read, but the owner has no enforceable, per-request guarantee that sensitive DOM fields are removed before content reaches a server-side model, nor a receipt proving what was withheld. This would let the owner use authenticated sites without choosing between usefulness and uncontrolled disclosure.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** A deterministic local redaction engine handles known sensitive fields and page metadata; a slower background classifier may suggest additional candidate regions but cannot override deterministic policy. Realtime only speaks the short result and redaction summary.
- **latency:** Local scan and redaction under 300 ms for a normal page; at most 1 second added before the spoken answer. Never upload the original page as a fallback when the scanner is uncertain.
- **cost:** No required realtime-model increase; modest Mac CPU for DOM classification and a small relay/database cost for hashed redaction receipts. The dominant engineering cost is testing false negatives against real authenticated sites.
- **security:** The original DOM, screenshots, and secret values must remain on the Mac. Send only redacted text plus field-type counts and salted hashes of region identifiers. Treat uncertainty as deny-and-report, not allow. Make policy version, withheld categories, and source URL visible in a local receipt; require explicit owner configuration to permit any category.
- **missing:** A browser-extension content firewall that runs before extraction and covers DOM text, attributes, accessibility labels, screenshots, clipboard, and form values; A Mac-local redaction service with versioned rules, fail-closed behavior, and a typed redaction manifest; Relay and realtime request contracts that accept only redacted payloads and reject un attested/raw browser content; Dashboard and pendant-readable receipts stating which categories were withheld, with local audit and revocation; A corpus of representative logged-in pages to measure false negatives without exporting their secrets


## Changes it proposed to its own stack

### `integration` — Add a closed-loop AudioQoS session shared by pendant firmware, Cloudflare relay, and Mac audio pipeline. The pendant emits compact 1-second counters (uplink loss, jitter, queue depth, playout underruns); relay computes a mode (normal, uplink-protect, recovery) and sends a signed mode update; Mac TTS packetizer and relay Opus transcode honor that mode. In uplink-protect, cap/reshape downlink and reserve modem budget for microphone packets; in recovery, refill the jitter buffer gradually. Record the mode and counters in the existing pipeline event/receipt stream so each call can be diagnosed without retaining speech.
- **owner gets:** When the owner speaks while the agent replies, their words will no longer vanish for several seconds, and a degraded connection will recover gracefully instead of producing silence or a late burst of audio. The owner also gets an honest explanation in a completion receipt when quality was reduced.
- effort: Medium-high: a firmware telemetry packet and state machine, relay session state and packet scheduler, Mac/Opus packetizer changes, plus an automated contention test. This is a focused vertical slice rather than a new surface.  ·  risk: A bad mode update could starve replies or cause oscillation. Use monotonic sequence numbers, hysteresis (minimum 2 seconds per mode), a 5-second local timeout to return to normal, and retain the current static 24 kHz path as fallback. Recovery is automatic on reconnect.
- cost: No additional model calls. A few dozen bytes/sec of telemetry and small relay memory per active call; adaptive mode should reduce LTE airtime during contention. Engineering/test cost is the dominant cost.  ·  latency: Telemetry/control under 1 second; at most one 60 ms codec frame to change mode, with up to 120 ms intentional jitter buffering during recovery.
- security: Telemetry contains transport statistics only. Authenticate mode updates to the paired pendant; do not upload raw microphone samples beyond the existing audio path, and keep diagnostic counters under the existing audio-retention policy.
- depends on: Pendant firmware support for loss/jitter/queue counters and a local fallback mode; Relay scheduler and Opus profile negotiation; Mac TTS/Opus packetizer that can honor a per-session audio mode; A contention/fault-injection harness covering simultaneous uplink and downlink

### `browser-harness` — Insert a fail-closed privacy firewall between the browser bridge and every research/realtime request. Each extraction returns a redacted payload plus a signed manifest containing policy version, source tab/session, withheld categories, byte counts, and a hash of the original region map; the relay accepts the payload only when the manifest attests that raw DOM, screenshots, form values, and clipboard data were not included. Keep the original and region map on the Mac, expose a local review/rollback endpoint, and emit the manifest hash into the existing job and pipeline receipts.
- **owner gets:** The owner can ask for help on a logged-in page without trusting an invisible promise. They receive a concrete, reviewable statement of what was blocked, and a policy failure cannot silently turn into secret exfiltration.
- effort: High: extension interception plus Mac-local classifier, signed request schema, relay rejection path, and adversarial tests for secrets hidden in attributes, screenshots, accessibility trees, and copied text.  ·  risk: False positives may make answers less complete; false negatives are unacceptable. Fail closed on classifier uncertainty, maintain a user-editable allowlist of non-sensitive fields, and provide a local-only re-run after policy changes. Recovery never retries with the raw page.
- cost: No additional model calls on the normal path; Mac CPU and test-maintenance cost are significant, with small relay storage for manifests. Data egress decreases.  ·  latency: Typically 100–300 ms local processing; complex pages may add up to 1 second. No network round trip is added for policy decisions.
- security: Strongly improves confidentiality only if cryptographic attestation is verified server-side and keys never leave the Mac. A compromised extension remains an explicit threat requiring code signing and version pinning.
- depends on: Browser bridge interception before /research and realtime submission; Mac-local secret classifier and durable policy store; Relay schema validation that rejects unredacted or unattested payloads; Receipt/dashboard rendering for redaction manifests


## What it asked for

_Nothing._
## Its own summary

Fresh discovery found the Mac bridge online and relay reachable, but the browser extension is offline with 9 pending commands. Live pipeline evidence shows 24 kHz mono TTS already renders successfully (75,734-byte PCM), while hardware measurements show simultaneous LTE-M audio loses about 7.8 seconds of uplink. I recorded two new, non-gating proposals: an owner-facing congestion-resilient conversation capability and a concrete AudioQoS integration linking pendant telemetry, relay scheduling, and Mac packetization. The missing work is between existing pipeline routes, not another planner model.

**Biggest unknown:** The granted mac_readonly_inspect and mac_read_sources tools still have schemas but no implementations, so I cannot verify foreground apps, tabs, Calendar, or unread Mail from this round. For the audio work, the remaining unknown is firmware-side queue/loss telemetry and whether the relay can prioritize packets at the modem/WebSocket boundary; an end-to-end contention test is needed to measure that.

