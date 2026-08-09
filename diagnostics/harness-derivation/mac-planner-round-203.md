# Harness derivation — mac-planner — round 203

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **current-device-status** — The live device inventory reports Safari on MacIntel with 9 tabs online and home-macbook-bridge online; no LTE pendant device is listed, consistent with USB-attached but unregistered hardware.
  - evidence: discover(devices) returned Safari on MacIntel · browser · 9 tab(s) · online; home-macbook-bridge · mac_bridge · online; cloudflare-contract-test · mobile · offline.

## Capabilities it proposed

### "When I tap the bookmark button, save exactly what I was doing so I can resume it later: the active browser page, the app and file I was in, my next calendar event, and a one-sentence resume card waiting on my Mac."
- **useful because:** A physical tap is the fastest reliable marker when attention changes. The worn device supplies the moment, the Mac supplies private desktop context, Calendar supplies intent, and the relay turns them into a durable return-to-task card instead of a vague timestamp or voice memo.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for extracting a short resume card; realtime only for the optional spoken acknowledgement
- **latency:** LED acknowledgement immediately; context capture within 3 seconds of USB bookmark; resume card available within 10 seconds
- **cost:** ~$0.01–$0.04 per bookmark, dominated by one small summarization call; zero model cost if the card is just structured metadata
- **security:** Capture only the active tab URL/title and explicitly redacted excerpt, never passwords or form values. Store the card in the owner's workspace with a retention limit. Opening the saved tab or changing files should remain an explicit Mac action, not happen silently.
- **missing:** A serial event bridge that forwards the shipped offline_moment_bookmark over the currently connected USB pendant; A Mac context collector that can return active app/document identity and a redacted browser excerpt, beyond the existing browser_tabs observation; A relay endpoint and dashboard view for bookmark-to-resume cards

### "Before the Mac sends an email, deletes a file, or completes a purchase, give me a spoken one-sentence preview on the pendant that names the exact target and change; let one deliberate pendant press approve only that exact action, then show me a receipt."
- **useful because:** The owner already wants destructive actions confirmed, but desktop prompts are easy to miss and a generic approval is unsafe. Binding approval to an action hash makes the pendant a physically separate, understandable confirmation surface while the Mac remains the only executor.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** realtime for the short spoken preview only; background for receipt wording and redaction
- **latency:** Preview in under 2 seconds after preflight; approval dispatch in under 500 ms; receipt within 3 seconds
- **cost:** Usually <$0.01 per action; TTS/audio transport and relay calls dominate, not reasoning
- **security:** The preview must redact message bodies, secrets, and payment details while still naming recipient/domain, file path, or merchant. The approval token must be single-use, expire quickly, include an action hash and originating surface, and be rejected if the Mac/browser plan changes. Never let a stale spoken preview authorize a new action.
- **missing:** A relay-mediated action-hash approval protocol connecting pendant button events to a specific Mac/browser job; A Mac executor hook that pauses high-impact plans after mac_action_preflight and resumes only with the matching token; A pendant spoken-preview queue entry distinct from the existing alert inbox, or a typed urgent alert payload with action-hash metadata

### "While the pendant is plugged into my Mac, make it a full voice terminal even without LTE: route its microphone and 24 kHz speaker audio through the USB serial bridge and the Mac's network to the relay, using the same button, privacy latch, queued replies, and transcript as cellular mode, then automatically return to LTE when the radio is registered."
- **useful because:** The wearable is physically real and testable now, but it is not LTE-registered. USB tethering removes that dead zone: the owner can wear and speak through the actual pendant in the workshop, validate the entire experience, and keep a call alive when cellular coverage disappears without switching to a laptop microphone.
- **path:** pendant → mac-bridge → relay → browser → dashboard
- **model tier:** Realtime voice model for the call; no extra model for transport selection or packet forwarding
- **latency:** USB audio framing under 30 ms one-way; relay failover decision under 2 seconds; no audible gap longer than one 60 ms playback frame when switching transports
- **cost:** Same per-minute realtime cost as cellular; modest Mac CPU/USB bandwidth, with no additional inference cost
- **security:** Pair the exact USB serial IDs to the owner's relay identity and encrypt audio before it leaves the Mac. Do not expose a generic serial-to-network forwarder. Privacy-latch state must be authoritative locally and suppress both USB and LTE uplink. Tear down the tether when the device is unplugged and record transport changes in the call receipt.
- **missing:** A bounded USB audio/control transport between the nRF9160 pendant, ESP32 bridge, and Mac; the currently pending mac_serial_exchange is needed for the first implementation; Relay session support for a transport-neutral audio stream and seamless sequence-number continuity across USB and LTE; Firmware/bridge mode selection and packet framing that preserves the shipped Opus 24 kHz/60 ms contract

### "Find the answer to one question across my Mail, Calendar, open browser sessions, and workspace files, then tell me the answer with a source trail and point out any contradictions instead of silently choosing one."
- **useful because:** Today each surface can be inspected separately, but the owner cannot ask one cross-surface question and receive an auditable answer. This would turn scattered personal context into a trustworthy answer while preserving uncertainty and provenance.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background model for retrieval, contradiction detection, and synthesis; realtime only to speak the final one-sentence answer
- **latency:** Under 15 seconds for a normal question; return partial sources if one surface is unavailable
- **cost:** Approximately $0.02–$0.10 per query, dominated by context extraction and synthesis; deterministic retrieval should run before model use
- **security:** Source content stays on the Mac/relay boundary and is redacted before synthesis. Never expose hidden browser credentials, full email bodies, or secret memory facts to the pendant. Every claim needs a source identifier and timestamp; conflicting sources must be surfaced, not merged silently.
- **missing:** A unified read-query planner spanning mac_read_sources, browser inspection, and workspace indexing; A provenance/contradiction result schema that the relay can compress into a spoken response and dashboard citations; A bounded local workspace search capability with file-level redaction

### "At the end of each day, show me a private replay of what the system actually changed across my Mac, browser, and pendant: before/after summaries, unfinished actions, and links to receipts, with a single command to undo each reversible change."
- **useful because:** Receipts exist per job, but the owner cannot currently understand the whole day's impact or distinguish completed work from partial failure. A cross-surface replay makes autonomous assistance inspectable without forcing the owner to remember which agent did what.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background model to summarize the day's structured event ledger; no realtime inference required
- **latency:** Generate within 30 seconds on demand or at a scheduled evening time; pendant summary in one short sentence with dashboard detail available
- **cost:** <$0.05 per daily replay; event aggregation is deterministic and summarization dominates
- **security:** Use redacted diffs rather than raw email or page contents. Keep destructive actions visible even if their details are sensitive. Undo must verify the original receipt and refuse if the resource has changed since the action. Retain the ledger for a configurable period.
- **missing:** A cross-surface immutable event ledger joining Mac, browser, relay, and pendant receipts; A reverse-operation registry that can safely expose only actually reversible mutations; A daily replay route and dashboard timeline with partial-failure grouping

### "Before I accept, decline, or move a calendar invitation, tell me the real consequences across my day: conflicts, travel or preparation time, related mail and files, and what would become overdue; let me compare two proposed times without changing anything."
- **useful because:** Calendar conflict detection alone misses preparation, travel, related commitments, and downstream deadlines. A counterfactual view lets the owner make a decision from the pendant while the Mac and browser gather the private context, without accidentally editing the calendar.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background model for entity linking and consequence ranking; realtime only for speaking the selected comparison
- **latency:** Initial comparison within 10 seconds; alternate-time comparison within 5 seconds using cached context
- **cost:** $0.02–$0.08 per invitation, mostly entity linking and synthesis; calendar conflict checks are deterministic
- **security:** Do not send, accept, decline, or modify invitations during analysis. Treat browser pages and mail as untrusted text; extract only event, people, deadline, and location fields. Show which assumptions produced each consequence and redact sensitive attendees or contents in spoken output.
- **missing:** A read-only counterfactual calendar engine that can clone a day state and calculate consequences without mutating Calendar; Cross-source entity linking for invitation ↔ mail thread ↔ workspace files ↔ browser session; A compact comparison payload that the pendant can speak and the dashboard can expand


## What it asked for

_Nothing._
