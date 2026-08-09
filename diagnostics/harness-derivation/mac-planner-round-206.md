# Harness derivation — mac-planner — round 206

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Keep me focused: while I am in a meeting, driving, or clearly deep in work, suppress routine notifications across the pendant, Mac, and browser, but surface only genuinely urgent items and give me a ranked catch-up when the context ends."
- **useful because:** Today each surface can queue alerts, but none knows that the owner is currently in a calendar event, presenting in a browser tab, or actively typing. This makes the hive behave like one considerate assistant instead of three independent interrupt sources. It is the strongest everyday capability because it protects attention without requiring a manual mode toggle.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Cheap background classifier over structured signals; relay-realtime only for an actually urgent delivery decision. Never send page or mail bodies to the classifier unless the existing redaction policy permits it.
- **latency:** Context changes recognized within 5 seconds; urgent interrupt decision under 1 second; end-of-context digest within 30 seconds.
- **cost:** Low: mostly event rules and a small classification call per context transition; roughly $0.001-$0.01 per transition, dominated by model calls only when urgency is ambiguous.
- **security:** Calendar titles, foreground app, browser URL/title, and alert metadata leave their nodes only as redacted features. The owner must explicitly configure which urgency classes may break focus; an empty policy must queue everything. Never infer driving from raw location or microphone data.
- **missing:** A cross-surface interruption arbiter and policy schema with owner-configured allowed urgency classes; Relay fan-out that can mark an alert as suppressed, delivered, or digest-only across the existing pendant inbox and browser notifications; A context-end trigger from Calendar/browser/Mac activity

### "Carry this task through my logged-in browser and Mac, but verify the result at every boundary: if the website says it succeeded, confirm the matching local file/calendar change, and if anything disagrees, stop, preserve a receipt, and tell me exactly what remains."
- **useful because:** Cross-surface tasks currently fail opaquely when a browser command, Mac action, or network handoff partially completes. The owner gets either duplicate submissions on retry or no trustworthy answer. A verified saga would make high-value workflows such as submitting a form and filing its receipt, downloading an invoice and recording it, or booking and calendaring an appointment reliable.
- **path:** browser → mac-planner → relay → dashboard → pendant
- **model tier:** Deterministic state-machine and hashes for execution/verification; use a cheap model only to map the owner's natural-language goal to a bounded plan. Realtime is unnecessary except for a short pendant status update.
- **latency:** Preview in under 3 seconds; each boundary verification under 5 seconds; resume after a dropped node within 1 minute of reconnect.
- **cost:** Low API cost, roughly $0.002-$0.02 per workflow; latency and browser-site waits dominate, not inference.
- **security:** Authenticated browser sessions remain on the browser node; send only redacted success predicates and hashes to relay. Never treat a page's text claim as proof. The owner must set policy entries for each domain/app mutation; an empty policy halts before mutation. Receipts must exclude secrets and form contents.
- **missing:** A browser action executor that exposes postcondition probes rather than only success text; A relay saga/orchestration record with idempotency keys, checkpoints, retries, and compensating actions; Typed postcondition adapters for common Mac artifacts (file hash, calendar event identity) and browser artifacts (URL/entity id); Owner-configured unattended mutation policy

### "Find where I saw this before: search my recent logged-in browser pages and local Mac files/mail for the topic I say, rank the matching sources, and open the best one only after telling me which source it is."
- **useful because:** The owner's information is split between authenticated browser sessions, local files, Mail, and Calendar. Ordinary search cannot reach all of those, while asking the owner to remember which surface they used defeats the pendant's value. This provides a source-grounded recall path: the answer includes provenance and can reopen the exact page or file rather than hallucinating a summary.
- **path:** pendant → relay → browser → mac-planner → dashboard
- **model tier:** Cheap retrieval/reranking over redacted titles, URLs, filenames, and mail snippets; use the expensive realtime tier only to turn the final ranked evidence into a short spoken response. Never use a model to invent a result when no source matches.
- **latency:** Return first ranked candidates in 5 seconds; open action after explicit owner confirmation in the next turn; long searches can stream progress to the pendant.
- **cost:** Approximately $0.002-$0.03 per query depending on indexed source count; browser inspection and local indexing latency dominate.
- **security:** Search stays scoped to the owner's pre-authorized account and directories. Do not transmit full mail bodies or page content by default; return snippets with source IDs and redact secrets. Opening a matched URL/file is a mutation and must obey the owner's runtime policy, with an empty policy stopping at ranking.
- **missing:** A unified, permission-scoped index spanning browser inspection history, local files, Mail, and Calendar; A source-provenance result schema with stable IDs, timestamps, snippets, and confidence; A relay query route that can accept a spoken topic and stream ranked results back to the pendant; Explicit owner policy for which directories, browser domains, and mail account may be searched

### "Only give me an answer when you can show where it came from and distinguish firsthand evidence from an inference: check my authenticated browser, Mac sources, and the relay's prior records, tell me when sources disagree, and let me ask you to open the evidence."
- **useful because:** The owner should be able to trust a spoken answer without confusing a model's confident synthesis with a fact. This is not another search or briefing: it is an evidence contract that carries provenance, freshness, source disagreement, and uncertainty through every node, then makes the supporting artifact inspectable on the Mac or browser.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Deterministic evidence collection and freshness checks first; a cheap model extracts claims and compares sources; realtime is used only to speak the compact result. Escalate to the expensive tier only when sources conflict and the owner asks for adjudication.
- **latency:** First evidence-backed answer in 5 seconds for cached/indexed sources; 15 seconds for a live browser check; source opening begins only after the owner asks.
- **cost:** About $0.003-$0.04 per question, dominated by live authenticated-page inspection and conflict-resolution calls; cached claim checks are nearly free.
- **security:** Keep authenticated page contents and mail bodies on their owning node; send claim hashes, redacted snippets, origin, timestamp, and confidence to the relay. Never expose a secret merely because it is evidence. Opening a source is a separate owner-policy-controlled action, and an empty policy must refuse it.
- **missing:** A claim/provenance envelope shared by relay, browser, and Mac with source identity, capture time, freshness, and extraction span; A privacy-preserving cross-node evidence index and contradiction detector; Browser adapters that can re-check a logged-in page and return a bounded evidence excerpt rather than only page text; A spoken response format that says unknown or disagreement instead of smoothing it over

### "Give me a room-safe answer: summarize my mail, browser pages, or calendar without speaking names, secrets, or sensitive details aloud, and let me privately request the redacted details on the Mac instead."
- **useful because:** A wearable that speaks is inherently public, but the useful information is often private. Today redaction is a per-request preference rather than an output guarantee tied to the actual playback surface. This capability lets the owner use the pendant in a room without abandoning mail and browser assistance, while preserving a richer private view on the Mac.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Deterministic field-level redaction before any model call; cheap summarization of the safe projection; realtime only for the short spoken version. A private Mac expansion can use a stronger model when needed.
- **latency:** Speak a safe 2-3 sentence answer within 5 seconds; private expansion appears on the Mac within 10 seconds.
- **cost:** Low, roughly $0.002-$0.02 per request; redaction and source reads dominate, not model inference.
- **security:** The safe projection must be generated before audio encoding, and raw content must never enter the spoken transcript or audio cache. Use domain/app sensitivity rules plus named-entity and secret detectors, retain the private expansion only as a short-lived Mac job, and require an owner-selected policy for what categories are safe to say aloud.
- **missing:** A playback-bound redaction stage in the relay that operates before TTS/audio generation; Shared sensitivity labels for Mail, Calendar, browser content, and local files; A private Mac handoff route that renders withheld details without sending them to the pendant; A persistent owner policy for room-safe categories and retention


## Changes it proposed to its own stack

### `integration` — Ship a USB-local pendant gateway on the Mac that detects /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA, exposes a single authenticated local transport to the relay, and bridges button/bookmark events, staged audio, diagnostics, and link state with sequence numbers and replay protection. When LTE is unregistered, it should explicitly advertise 'USB-local' rather than pretending the pendant is online over cellular.
- **owner gets:** The wearable is physically on the owner's desk today but cannot register with the relay, so the owner cannot exercise the real button/audio path or use it as a dependable local companion. This would make the hardware useful immediately over USB and make failures honest instead of silently looking like a dead pendant.
- effort: Medium: a launchd-managed serial gateway, framing/parser integration for both boards, reconnect/backoff, and relay device-session support; then a hardware-in-the-loop smoke test for bookmark and 24 kHz playback.  ·  risk: Serial disconnects, stale device paths, or duplicate replay could create repeated bookmarks or audio. Use monotonic sequence numbers, an on-disk bounded spool, atomic acknowledgements, and a visible disconnected state; never fall back to microphone capture without the existing local privacy latch.
- cost: Negligible inference cost. Engineering work only; approximately 1-3 W while the boards are USB-powered, with no new hardware purchase.  ·  latency: Local button events and status under 100 ms; audio adds only USB serial buffering (target under 50 ms).
- security: The gateway is a new local privileged bridge and must use the existing bearer/session authentication, restrict device paths to the two enumerated USB serial identities, and redact serial logs. It must not expose arbitrary shell or raw microphone data.
- depends on: Relay device-session endpoint and explicit transport=usb-local state; Serial framing contract for nRF9160 and ESP32 bridge; Owner-configured launchd/autostart policy; An implementation of the pending mac_serial_exchange capability or an equivalent approved serial tool

### `hardware` — Revise the pendant around a hardware-rooted identity and unmistakable physical privacy control: add a secure element for device attestation/key storage and a latching, electrically enforced microphone-and-speaker disconnect switch with a visible mechanical state indicator. The firmware must refuse to claim privacy when the switch state cannot be read, and the relay must bind sessions to the attested device rather than a copied bearer credential.
- **owner gets:** The owner gets a wearable they can trust even if the Mac or relay is compromised: a physical action truly disconnects both listening and playback, while the device proves which pendant is speaking. That is stronger than a software LED or a server-side privacy flag and makes unattended cross-node actions safer.
- effort: High: board spin, secure-element provisioning and recovery process, firmware boot/session integration, relay attestation, and an abuse-tested privacy circuit. Preserve the current board as the USB development target while the revision is validated.  ·  risk: A failed switch or provisioning error could strand the pendant or falsely report privacy. Design normally-open power gating, boot-time self-test, a local LED indication independent of the radio, factory recovery keys, and a degraded mode that disables audio rather than guessing. Added components increase size and assembly complexity.
- cost: Roughly $3-$10 added BOM per unit for secure element, switch, and indicator circuitry; negligible steady-state power impact, with a small boot-time attestation cost.  ·  latency: Attestation adds under 500 ms at session start; privacy switching is electrical and immediate, independent of network latency.
- security: Major positive: keys never leave the secure element and the kill switch is enforceable below firmware. Requires careful key provisioning, revocation, and physical tamper assumptions; it does not protect a compromised owner account from authorized actions.
- depends on: A relay attestation endpoint and device-key registry; A firmware privacy state that treats hardware disconnect as authoritative; A board revision with microphone/speaker power gating and a readable latching switch; Owner-facing recovery and replacement procedure


## What it asked for

_Nothing._
## Its own summary

Produced three new owner-facing capabilities and one stack change: (1) cross-surface verified browser+Mac workflows with postcondition checks, idempotent saga checkpoints, and receipts; (2) USB-local pendant gateway so the physically connected but LTE-unregistered nRF9160/ESP32 hardware works today with honest transport state; (3) provenance-aware “where did I see this?” retrieval across logged-in browser, Mac files, Mail, and Calendar. A focus/interruption concept was recorded but flagged close to existing backlog, and a bookmark-context variant was correctly rejected as a duplicate rather than rephrased.

**Biggest unknown:** The remaining blocker is not another Mac action primitive: it is policy and relay integration. I still need an owner-configured unattended-action policy (domains/apps/directories, redaction, mutation classes) and server-side contracts for USB-local device sessions, cross-surface provenance indexing, and verified browser postconditions. Accessibility remains owner-managed and cannot be granted from this harness; the pending serial exchange capability is also unavailable, so the USB gateway is a proposal rather than executable work this round.

