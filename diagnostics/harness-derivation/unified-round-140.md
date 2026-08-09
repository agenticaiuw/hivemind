# Harness derivation — unified — round 140

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac and browser readiness** — As of Round 140, /ops/status reports AI Pendant Agent ready with Accessibility and Screen Recording both granted, browser online with 9 Safari tabs, relay reachable, and no required permissions missing. This supersedes the earlier denied-permission snapshot.
  - evidence: GET /ops/status returned permissions.accessibility.trusted=true, screenRecording.granted=true, ready=true; browser.online=true; relay.reachable=true.

## Capabilities it proposed

### ""Give me a private, shareable postmortem for the last failed conversation.""
- **useful because:** When audio or a browser action fails, the owner currently has to expose raw logs or guess. This produces a redacted artifact that explains the turn timeline, transport handoffs, packet loss, model/relay outcome, and whether playback was actually acknowledged—without exporting conversation audio or page contents by default.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background model for summarization after deterministic collection; realtime only to acknowledge that collection has started.
- **latency:** Under 3 seconds to collect and hash evidence; 5–15 seconds for the background narrative.
- **cost:** ~$0.01–$0.05 per report; dominated by background summarization, not collection.
- **security:** Default artifact contains counters, opaque IDs, timestamps, and hashes—not raw audio, transcripts, URLs, or page text. Require explicit confirmation to include any transcript or browser evidence; expire the artifact after 24 hours.
- **missing:** A deterministic exporter that joins pendant/bridge counters, relay receipts, Mac jobs, and browser command outcomes into one redacted bundle; An artifact download/share route with expiry and content-class consent; A stable correlation ID spanning USB turns and relay jobs

### ""Before you act in my browser, tell me the exact data that will leave this Mac, and let me approve only that payload on the pendant.""
- **useful because:** A page action can be safe in effect but still leak a secret in a typed field or URL. This gives the owner a concrete outbound-data manifest—not a vague risk label—then binds the exact manifest to the pendant's physical transaction approval. It works with the browser's authenticated sessions while keeping page contents off the pendant.
- **path:** pendant → relay → mac-bridge → browser
- **model tier:** Deterministic extraction and hashing first; background model only to turn the manifest into plain language. Realtime is reserved for the short spoken explanation.
- **latency:** 1–2 seconds for extraction and staging; execution starts only after the physical approval receipt.
- **cost:** ~$0.005–$0.02 per staged action; model cost is optional and small.
- **security:** Never send secrets or page bodies to the pendant. Manifest contains field names, destination origin, byte counts, and keyed hashes; sensitive values are shown as type/length/redaction. Approval nonce, expiry, plan digest, and one-shot replay guard must be enforced before browser submission.
- **missing:** A browser-side outbound payload inspector that intercepts form/navigation/API bodies before dispatch; A relay-backed delivery path for staged manifest and approval receipt; A browser executor gate that refuses any payload differing from the approved digest

### ""Show me exactly what would change across my Mac and browser if I did this—without touching anything—and let me inspect the result as one change set.""
- **useful because:** Today planning is fragmented: a Mac plan, browser plan, and file preview do not produce one coherent before/after picture. The owner should be able to rehearse a multi-surface request, see affected files, tabs, records, and outbound requests together, and abandon it with zero side effects.
- **path:** relay → mac-bridge → browser → dashboard → pendant
- **model tier:** Deterministic shadow execution and state capture; background model only summarizes the resulting diff.
- **latency:** 3–10 seconds for a bounded rehearsal; long jobs stream progress and remain non-mutating.
- **cost:** ~$0.01–$0.08 per rehearsal, dominated by optional summary generation; shadow reads and hashing are local.
- **security:** Shadow execution must use isolated temporary directories, browser request interception, and read-only credentials. Never submit forms, send messages, or expose secrets in the diff. The result should expire and be bound to the exact world fingerprints it observed.
- **missing:** A universal dry-run executor for Mac and browser actions, not just individual preview routes; Filesystem and browser state adapters that emit typed before/after diffs; A dashboard view that merges the changes into one reviewable change set; A stale-world check that invalidates the rehearsal when the real state moves

### ""Apply this same approved change to every matching place, but stop and show me the first mismatch instead of guessing.""
- **useful because:** Bulk actions across files, browser tabs, reminders, and other records are where a single silent mismatch becomes expensive. The owner gets an all-or-nothing-or-paused change set: deterministic matching, per-target preconditions, a physical approval for the set, and a precise stop point when one target differs.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic matcher, precondition checker, and transaction coordinator; background model may identify candidate matches but cannot expand the approved set silently.
- **latency:** Preview under 5 seconds for up to 100 targets; apply begins immediately after approval and pauses within one target of a mismatch.
- **cost:** ~$0.02–$0.15 per change set depending on target count and optional planning model use.
- **security:** Approval binds the complete target list, operation digest, and per-target world fingerprints. Newly discovered matches are excluded and reported, never auto-added. Irreversible or unrepeatable targets require explicit separate handling.
- **missing:** A cross-surface change-set schema with immutable target membership; Per-target compare-and-swap/precondition support in Mac and browser executors; A coordinator that can pause, compensate safe steps, and report unresolved targets; Dashboard and pendant presentation for a potentially large target set


## Changes it proposed to its own stack

### `integration` — Add a correlation spine for USB-tethered calls: every button edge, audio frame, bridge acknowledgement, relay job, model response, and playback receipt carries a compact turnId plus monotonic sequence; the Mac bridge writes only redacted metadata to a bounded ring and emits a signed close record at the turn boundary. Reconcile late LTE and USB events by turnId rather than wall-clock time.
- **owner gets:** The owner gets truthful answers after a handoff or outage—whether a reply was captured, delivered, and heard—without pretending that Mac time and the pendant's zoneless clock are comparable. It also makes the currently testable USB session useful for diagnosing the real wearable path.
- effort: Medium: firmware/ESP32 frame headers, bridge metadata ring, relay schema/index, and Mac reconciliation tests.  ·  risk: Malformed or duplicated frames could create false receipts; reject unknown sequence windows, use monotonic deduplication, and fall back to 'unknown' rather than claiming success. Ring overflow must drop diagnostics, never audio.
- cost: Negligible storage and bandwidth (roughly 32–64 bytes per event); no routine SD writes and no additional model calls.  ·  latency: Sub-millisecond local metadata work; no added audio buffering. Reconciliation can be asynchronous after playback.
- security: Use opaque IDs and keyed hashes; never put audio, transcript, page content, or secrets in the spine. Signed close records prevent a stale USB reconnect from being mistaken for a fresh turn.
- depends on: usb_fallback_audio_session; audio_delivery_ack_queue (s9-vtxc); duplex_audio_congestion_guard (s15-rzms); A relay schema for turn correlation and a bridge implementation

### `hardware` — Add a physically latching, normally-open microphone power cutoff and a separate hardware playback mute path on the wearable, both outside the nRF9160 GPIO/software control loop. Expose their state to firmware as read-only inputs so the software can report the hardware truth, but make neither path capable of being re-enabled remotely.
- **owner gets:** The owner gets a privacy guarantee that survives a crashed firmware, compromised relay, wedged USB session, or accidental software regression: when the physical privacy control is off, the microphone is electrically disconnected and the speaker is silent.
- effort: High: wearable board revision, analog/audio power design, debouncing and state sensing, enclosure control, and validation against the full-duplex I2S path.  ·  risk: A stuck switch or contact bounce could disable a conversation; fail safe, show an unmistakable LED state, and provide a local-only recovery path. Added switching noise must be measured in the 24 kHz path.
- cost: Roughly $2–$8 in added components and PCB area at prototype volume; negligible steady-state power when open, small leakage and switch overhead when enabled.  ·  latency: Electrical mute is immediate—faster than a radio or firmware command. Firmware state reporting can be asynchronous.
- security: Strongly improves privacy by making remote reactivation impossible. The hardware state must be included in signed diagnostics so software cannot claim capture is active when the mic is physically cut.
- depends on: local_privacy_latch behavior; A product wearable PCB rather than the current nRF9160 DK; Measured microphone and amplifier power domains suitable for independent cutoff; A privacy-state diagnostic field in the relay/Mac status surfaces


## What it asked for

_Nothing._
