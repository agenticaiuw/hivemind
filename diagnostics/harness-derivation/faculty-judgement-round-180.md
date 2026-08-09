# Harness derivation — faculty-judgement — round 180

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **reconcile_personal_state resolution** — The granted reconciliation tool did not execute a read-only reconciliation; it resolved the request to POST /briefing (low confidence) and marked invoked:false because POST has side effects. It cannot currently be trusted as a state read.
  - evidence: reconcile_personal_state(domains=[timezone,permissions,scheduled_briefings,browser_connectivity,audio_queue], as_of=2026-08-08T03:00:00Z) returned resolvedTo POST /briefing, confidence 0.472, invoked false, wouldHaveCalled POST /briefing.

## Capabilities it proposed

### "“Let me use the pendant reliably while it is plugged into my Mac, even though LTE is not registered; when I press the button, carry my voice through the Mac to the relay and play the reply back through the ESP32 bridge.”"
- **useful because:** This is the highest-value thing the owner can get today: the physical pendant is present and testable now, but treating it as LTE-only makes the real hardware appear dead. USB-tether mode turns the Mac into a transparent transport without changing the owner's button-and-speaker experience, and falls back cleanly when the cable disappears.
- **path:** pendant → mac-planner → relay-realtime
- **model tier:** Realtime only for the live turn; a cheap deterministic USB session/packet broker handles framing, and the relay model handles speech. No model should be spent on transport supervision.
- **latency:** Button-to-uplink under 150 ms after capture starts; downlink playback begins within 500 ms after the first accepted audio chunk. Cable removal must stop/requeue within 1 s.
- **cost:** Negligible incremental API cost; the dominant cost remains the normal realtime voice turn. Engineering is a USB serial broker plus session authentication and packet routing, not additional inference.
- **security:** The Mac must not silently become a trusted radio: bind the serial device identity, authenticate a short-lived device session, encrypt or MAC framed audio/control packets, and invalidate the session on detach. Never expose raw PCM in logs; keep only opaque artifact IDs and delivery receipts. A physical stop latch must cancel capture/playback before reconnect retries.
- **missing:** USB-serial transport adapter for /dev/cu.usbmodem00096003658* and ESP32 /dev/cu.usbserial-0287A9CA; relay device-session registration and short-lived credentials for a tethered (non-LTE) pendant; a single framed protocol joining nRF capture, relay audio, and ESP32 playback with sequence/checksum/ACK semantics; Mac-side supervisor that detects detach, reconnects, and does not duplicate a turn

### "“Before you decide how to interrupt me, replay a sample of my recent mail, calendar, browser-watch, and scheduled-brief events, show me which would have been spoken or deferred, and let me change the policy without guessing my preferences.”"
- **useful because:** The code already has several independent triage policies and the owner has not stated quiet hours or what content may be spoken. A policy-rehearsal view makes the consequence of each knob visible before it affects the owner's day, and turns the placeholder policy into an owner-controlled instrument rather than hidden thresholds.
- **path:** relay-realtime → mac-planner → browser-extension → pendant
- **model tier:** Background/cheap model for grouping and summarizing historical events; deterministic scoring for the replay. Realtime only when the owner asks a spoken follow-up.
- **latency:** A 7-day replay in under 5 s; a policy edit preview in under 1 s after cached inputs. No interruption should change until the owner explicitly applies the policy.
- **cost:** Low: one background summarization call per replay, dominated by input volume. Deterministic reruns should be free after event snapshots are collected.
- **security:** Default to metadata-only previews: no subject/body spoken during rehearsal unless explicitly requested. Preserve source links and sensitivity labels; redact before TTS. Applying policy is a reversible settings mutation and must produce an audit receipt. Calendar emptiness is not evidence when EventKit is unreadable, so the replay must mark that source unknown rather than all-clear.
- **missing:** durable event snapshots with source timestamps and provenance sufficient for deterministic replay; a real, mounted attention arbiter (the current attention_arbitrate grant is unresolved); an owner-facing policy version/apply route that records who changed which field and supports rollback; a safe EventKit readability probe shared by briefing and notification readers; a dashboard or spoken compact explanation of each matched policy rule

### "“Make sure the brief I was supposed to hear actually reached the pendant; if playback stopped or the checksum failed, quietly put that item back at the next safe opportunity and tell me what was missed.”"
- **useful because:** Server acceptance is not owner receipt. A spoken briefing can be downloaded but never played, or stop halfway while every job receipt says success. Closing that loop means the owner can trust that ‘tell me’ means heard, not merely generated, without manually inspecting logs.
- **path:** relay-realtime → mac-planner → pendant
- **model tier:** Deterministic state machine for artifact delivery, deduplication, retry, and item correlation; cheap background summarization only to explain a missed item. Realtime is unnecessary unless the owner asks immediately.
- **latency:** Ingest device ACKs within 2 s of reconnect; classify a stalled item after 30 s or an explicit interruption; queue one bounded retry without interrupting speech.
- **cost:** Near-zero model cost. Storage is small event metadata; network cost is bounded by one retry of an existing audio artifact. The expensive part is not inference but robust correlation and idempotent replay.
- **security:** Store only opaque artifact/item IDs, byte counts, positions, and reason codes—not transcript or PCM. Authenticate device session and monotonic sequence, reject replayed ACKs, and do not retry a secret item into an unapproved speaking context. Every retry must pass the attention/autonomy policy and expose an undo/suppress option.
- **missing:** durable join from briefing item to audio artifact and source evidence; a relay-side delivery state machine consuming authenticated offline ACKs (record_pendant_delivery_event currently resolves only as a side-effect description); idempotent restage/retry operation that preserves item identity and playback position; a policy-aware retry scheduler that distinguishes interruption, checksum error, and never-downloaded

### "“Before I send this email or submit this web form, check the actual recipients and destination, scan the content for secrets and third-party personal data, explain anything risky in one short sentence, and require one physical pendant confirmation if it leaves my trusted boundary.”"
- **useful because:** The current redaction machinery protects some model prompts, but it does not make an outbound decision about who will receive a draft. This prevents the expensive, irreversible mistake of sending a credential, client detail, or private attachment to the wrong address or domain while keeping ordinary drafts fast.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Deterministic local classifiers first; a small background model may summarize the specific risk. Realtime is only for the owner's spoken question or final short explanation.
- **latency:** Under 500 ms for known patterns and recipients; under 3 s for a model-assisted review. Never delay ordinary local drafting once the owner has explicitly approved the destination class.
- **cost:** Usually zero model cost; occasional small classification call dominates. No content should leave the Mac unless the existing outbound policy permits it.
- **security:** The guardian itself must not transmit the draft to a third-party model by default. It must inspect recipient, URL, attachment names, sensitivity classification, and secret patterns locally; show only masked excerpts; issue a one-time physical challenge bound to an exact content hash and recipient set; invalidate it if either changes.
- **missing:** recipient- and destination-aware policy table with owner-editable trusted origins; a local scanner that covers attachments, non-US identifiers, addresses, and third-party names beyond current redaction patterns; browser/mail draft interception before submit/send; physical approval challenge bound to a draft hash and recipient set; a receipt that records what was checked without retaining the raw draft

### "“When I am about to buy, book, or accept something in the browser, compare the final page with the confirmation or receipt that arrives in mail, call out price/date/cancellation/recipient mismatches, and give me a compact pendant readback before I approve.”"
- **useful because:** A browser page can change between search and checkout, fees can appear late, and a confirmation can disagree with what the owner thought they accepted. Comparing two independently held sources catches costly mistakes before submission, rather than merely logging that a click happened.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Cheap deterministic field extraction and comparison first; background model only handles ambiguous labels or terms. Realtime produces the short spoken discrepancy summary.
- **latency:** Initial comparison under 4 s; final pre-approval readback under 1 s once both sources are available. No external submission until the owner confirms the exact comparison result.
- **cost:** One small extraction/comparison call for unusual pages; browser and mail reads dominate latency, not tokens.
- **security:** Never send credentials, full payment data, or page bodies to the model unnecessarily. Keep only field hashes and source locators in the audit record. Treat missing receipt, changed recipient, or ambiguous cancellation language as a block, not an inferred match. Bind physical approval to the final page hash and extracted fields.
- **missing:** schema for normalized transaction fields and source confidence; a way to wait for and associate the matching receipt email with the browser transaction; comparison rules for currency, taxes, time zones, cancellation windows, and recipient identity; a reviewable approval packet that the pendant can read without receiving secrets; browser submit interception that prevents stale approval after page mutation

### "“When my Mac wakes, the browser reconnects, or the pendant comes back online, tell me what changed while I was away in terms of unfinished work—not a log dump—and offer only the next safe, reversible step for each item.”"
- **useful because:** Today the owner can have jobs, browser commands, briefings, and audio in different lifecycle states without one honest account of what remains. A recovery digest would turn outages and sleep into a comprehensible continuation instead of duplicate actions, forgotten drafts, or false completion.
- **path:** relay-realtime → mac-planner → browser-extension → pendant
- **model tier:** Deterministic reconciliation of receipts, leases, browser commands, and delivery events; a cheap background model compresses only the resulting deltas. Realtime is reserved for the owner's request or a one-sentence urgent notice.
- **latency:** Produce a bounded recovery digest within 3 s of reconnection; never execute automatically. Revalidation of a selected step under 1 s before offering it.
- **cost:** Low model cost; most work is querying and comparing durable records. Cost is bounded by a small delta window, not the full history.
- **security:** Use opaque IDs and provenance links, omit raw page bodies and secrets, and mark unknown rather than assuming failure or success. Every offered continuation must pass stale-plan revalidation and autonomy policy; mutations remain separately confirmed and undoable.
- **missing:** a true cross-surface foreign key joining relay, Mac, browser, and pendant IDs; job leases and orphan recovery so processing does not look permanently active; a durable delta cursor for reconnect epochs and offline pendant events; an owner-facing recovery digest route with explicit unknown/stale states; a safe resume planner that stages, revalidates, and offers one reversible step rather than replaying blindly


## Changes it proposed to its own stack

### `integration` — Ship a USB-tethered pendant gateway on the Mac: claim the nRF9160 serial device, authenticate a short-lived device session, bridge framed mic/control packets to the relay, and route relay Opus downlink to the ESP32 serial/I2S playback path. Add detach-safe session invalidation, sequence/checksum ACKs, and a single-flight turn guard so reconnect cannot duplicate a conversation.
- **owner gets:** The pendant they are actually wearing becomes usable today over the cable instead of waiting for LTE registration; pressing the button feels like using the finished product, and a cable pull fails safely rather than losing or duplicating speech.
- effort: Medium-high: serial framing and broker, relay session endpoint, and end-to-end hardware test across both USB devices.  ·  risk: A malformed or stale serial frame could inject audio/control or duplicate a turn. Recover with authenticated sequence numbers, single-flight correlation, stop-latch precedence, bounded replay, and forced session invalidation on detach.
- cost: No meaningful API-model increase; modest Mac CPU/USB I/O. Existing audio bandwidth and Opus costs dominate.  ·  latency: Adds roughly one local serial hop; target under 150 ms capture startup and under 500 ms downlink start.
- security: Creates a new local trust boundary. Require device identity plus ephemeral session keys, redact logs to IDs/metrics, and never let the relay assume LTE-level identity from mere USB presence.
- depends on: USB serial protocol definition for the live nRF9160 and ESP32 paths; relay endpoint for tethered device-session registration; durable artifact/device ACK ingestion and deduplication; Mac supervisor lifecycle and permissionless serial access


## What it asked for

_Nothing._
