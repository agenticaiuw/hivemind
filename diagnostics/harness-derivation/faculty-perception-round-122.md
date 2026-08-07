# Harness derivation — faculty-perception — round 122

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac accessibility reality** — At 2026-08-07T18:07Z AI Pendant Agent's Accessibility is untrusted and Screen Recording false; synthesized input is not accepted, so UI action receipts are not trustworthy. Automation grants are present and requiredMissing is empty, but permissions.ready=false.
  - evidence: GET /observe and GET /ops/snapshot both report trusted:false, eventsPost:false, uiActionsWillReachTheScreen:false, screenRecording:false; /ops/snapshot automation grants are true.
- **live browser reality** — Safari browser bridge is online with 3 sessions/tabs, including a logged-in Gmail inbox tab titled 'Inbox (14,987)'; the currently heartbeating extension tab is example.com with title 'Failed to open page'. No browser commands are pending.
  - evidence: GET /observe and GET /browser/status at 2026-08-07T18:07Z.
- **pendant reality** — Device discovery still shows only home-macbook-bridge online and cloudflare-contract-test mobile offline; no nRF9160 pendant is registered. Pipeline entries mentioning nrf9160/audio are historical relay records, not proof of a live pendant.
  - evidence: discover(devices) at this round plus granted live pendant observability context; GET /pipeline shows old nrf9160 events.
- **pipeline speech reality** — The relay/mac pipeline has rendered 24 kHz mono PCM successfully in historical runs (74.0 KiB, 1.578 s, zero clipped samples), but a prior run was waiting for approval on a shell action before speech was returned. Pipeline status can therefore distinguish rendered speech from completed world action.
  - evidence: GET /pipeline historical run job_309f5663... events.

## Capabilities it proposed

### "“Before you tell me something happened, prove whether it is live, completed, merely rendered, or only historical—and say what evidence you used.”"
- **useful because:** This is the system's most useful trust feature: it prevents the owner from being told that a pendant received audio, a browser form submitted, or a Mac action succeeded when the only evidence is an old pipeline event or a UI receipt that could not reach the screen. It turns perception into an explicit contract for judgement and action.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** deterministic for status/provenance joins; background gpt-4.1-mini only to phrase conflicts; realtime only when the owner asks aloud
- **latency:** Under 300 ms for a status answer from cached timestamps; under 2 s if it must query Mac/browser/relay in parallel
- **cost:** Usually zero model calls; <$0.001 for an occasional conflict explanation. Dominant cost is parallel device and route reads, not tokens.
- **security:** Expose only redacted provenance (device IDs, route, timestamp, state), never page contents or credentials. Any action claim must require a typed receipt from the relevant surface; absence or staleness must be spoken as uncertainty.
- **missing:** A typed cross-surface evidence ledger with freshness/expiry and explicit state taxonomy (live, acknowledged, completed, rendered, historical, unknown); Relay device delivery acknowledgements tied to a specific pipeline/audio object; A perception snapshot read tool or route that joins /observe, /browser/status, /pipeline, /jobs and relay device registry

### "“What can I safely rely on right now?”"
- **useful because:** The owner gets a one-sentence reality boundary before acting: Safari is online but the active tab failed to open, Gmail is logged in, the Mac bridge is live, the pendant is absent, and screen/UI automation cannot be trusted. This is materially different from a generic morning brief because it reports capability availability and evidence quality, not personal tasks.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** deterministic joins for the core answer; background model for a concise spoken rendering; realtime only for the live spoken request
- **latency:** 1 s target, with stale cached state clearly labeled if a surface misses its deadline
- **cost:** <$0.001 per invocation; most responses are deterministic. Cost is dominated by refresh probes when cached state expires.
- **security:** Do not disclose Gmail counts or tab titles unless the owner is authenticated to the pendant/session. Clearly separate a logged-in tab's existence from permission to read its content. Never imply UI control is safe while Accessibility is false.
- **missing:** A portable availability/evidence schema consumed by every surface; Per-surface freshness TTLs and a user-visible stale badge; A spoken response formatter that can enumerate blockers without escalating to planner

### "“Watch for contradictions between what the Mac, browser, relay, and pendant claim, and interrupt me only when the contradiction could cause me to miss or repeat something.”"
- **useful because:** Cross-surface contradictions are the dangerous failures: the Mac can say audio was uploaded while no pendant is registered; a browser bridge can report online while its active page says Failed to open page; a job can be waiting for approval while TTS says response rendered. A contradiction sentinel would stop duplicate submissions and false reassurance without noisy status spam.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** deterministic event correlation and hashes; background gpt-4.1-mini only to classify human impact; realtime only for urgent interruption
- **latency:** 5 s for normal correlation; under 1 s for contradictions involving irreversible actions or expiring alerts
- **cost:** <$0.002 per alert; mostly event processing and durable storage, with model calls only for ambiguous impact classification
- **security:** Store hashes and typed metadata rather than page/audio contents. Never interrupt for harmless stale cache differences. Require judgement confirmation before retrying any action whose completion state conflicts.
- **missing:** Cross-surface correlation IDs propagated from spoken command through relay, Mac job, browser command and delivery receipt; An append-only event stream with clock-skew tolerance and deduplication; A contradiction policy/acknowledgement state so the same alert is not repeated

### "“Replay the last interaction exactly: what the pendant captured, what you heard, what each machine believed I asked, what was actually done, and where the handoff stopped.”"
- **useful because:** Today a failed or delayed interaction is reconstructed from scattered pipeline entries and ambiguous receipts. The owner needs a single chronological replay with original audio references, transcriptions, planner interpretation, action attempts, approvals, device acknowledgements, and unresolved handoffs. This is a debugging and trust capability, not another status briefing.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Deterministic event assembly and audio indexing; background model only to explain disagreements in plain language; realtime only if the owner asks for spoken replay.
- **latency:** Two seconds for a compact replay index; under ten seconds for audio excerpts and cross-surface reconciliation.
- **cost:** <$0.003 per replay, mostly storage reads and optional transcription of missing segments; no expensive planner call for the normal path.
- **security:** Interaction audio and private-page evidence are highly sensitive. Require local owner authentication, encrypt stored references, redact page contents by default, and provide per-event deletion. Never fabricate missing audio; label gaps explicitly.
- **missing:** A durable interaction bundle keyed by one correlation ID across capture, STT, planner, action, approval, TTS, and device receipt; Clock-offset and sequence reconciliation across pendant, Mac, browser, and relay; A user-facing replay route with gap and provenance markers

### "“For anything consequential, show me the proposed change on the Mac, then require a deliberate physical confirmation on my pendant before sending or submitting it.”"
- **useful because:** The owner gets a reliable separation between drafting and commitment even when Mac UI automation is unreliable. The browser can prepare a private transaction, the Mac can show the exact diff, and the pendant's physical button becomes the final consent channel. This is safer than trusting a synthetic click or a spoken “yes” that could be misheard.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Deterministic diff and confirmation state machine; background model for draft explanation; realtime only to collect the initial request or read back the final diff.
- **latency:** Draft can take seconds; after the owner presses the pendant button, confirmation propagation should complete within two seconds or expire safely.
- **cost:** <$0.002 for diff summarization; no model call is needed for typed field diffs. Hardware cost is zero if the existing button is usable.
- **security:** Bind confirmation to a cryptographic nonce, exact diff hash, target account, and expiry. A button press must never approve a changed draft. Do not treat a dashboard click or UI receipt as equivalent physical consent.
- **missing:** A pendant-confirmation protocol and nonce storage; Typed before/after diffs for browser and Mac actions; A commit gate that every consequential action must pass, including retries

### "“When I lose connectivity, keep a private, ordered queue of what I asked and what still needs doing; when connection returns, ask me once about conflicts instead of silently replaying anything.”"
- **useful because:** A worn device can capture an urgent request while LTE is unavailable, while the Mac may independently see the same task or a changed webpage. The owner needs one conflict-aware handoff: preserve exact order and intent, surface duplicates and stale targets, and require a fresh decision before any queued external action. This is not background execution; it is safe continuity across disconnected bodies.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic encrypted queue, deduplication, and conflict detection; background model only to summarize competing interpretations; realtime for the brief reconnection prompt.
- **latency:** Capture must commit locally in under 100 ms; after reconnection, conflict inventory under five seconds; no action is replayed automatically.
- **cost:** Near-zero during offline capture; <$0.002 per reconnection conflict summary. Storage and synchronization dominate, not model tokens.
- **security:** Encrypt the offline queue, minimize retained audio after transcription, bind entries to device keys, and expire sensitive requests. Never upload a queued action without explicit reconnection policy and owner confirmation.
- **missing:** A pendant-local encrypted intent journal with monotonic sequence numbers; A relay reconciliation protocol for duplicate, superseded, and conflicting intents; A conflict-review surface spanning browser targets and Mac job state

### "“Tell me exactly why you refused, paused, or downgraded that request—and what single fact or permission would have let you continue.”"
- **useful because:** Today refusal, approval waits, missing Accessibility, absent pendant registration, and browser failures appear as disconnected implementation messages. The owner needs an actionable explanation that distinguishes policy, missing capability, stale evidence, unavailable device, and failed execution, then names the smallest unblock. This prevents repeated commands and makes the system teachable.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic refusal taxonomy and evidence links; background model only to turn structured causes into a short explanation; realtime for immediate spoken delivery.
- **latency:** Under 500 ms for known refusal causes; under three seconds when correlating a job and device evidence.
- **cost:** <$0.001 per explanation; normally no model call. Cost is dominated by retaining structured decision records.
- **security:** Explain policy without exposing hidden prompts, credentials, or private page contents. Reveal only the minimum evidence needed, and distinguish a security refusal from an ordinary missing permission.
- **missing:** Structured refusal/pause records with reason codes, evidence, and unblock conditions; A stable taxonomy shared by relay, Mac, browser, and pendant firmware; Owner-facing links from each spoken refusal to its underlying job or event


## Changes it proposed to its own stack

### `integration` — Add a USB-tethered hardware presence channel: the Mac bridge opens /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA, performs a read-only version/uptime/button/audio-loopback handshake, and publishes a short-lived local-attached status distinct from relay registration. Every pipeline event then carries transport=usb_serial or lte and an observed-at timestamp; relay history can never be presented as current hardware evidence.
- **owner gets:** The owner can wear/test the actual prototype today over USB and receive an honest answer about whether the nRF9160 and audio bridge are alive, without waiting for LTE pairing. It eliminates the most dangerous confusion in this system: historical 'waiting for the pendant' records being mistaken for a device that is currently connected.
- effort: Medium: serial framing/parser in the Mac bridge, two firmware diagnostic commands, status projection and dashboard badge; no cloud registration required for the first milestone.  ·  risk: Malformed serial data or a wedged device could stall the bridge; use timeouts, bounded reads, and a kill switch. Never interpret silence as offline without a completed handshake. Recover by closing/reopening both serial ports.
- cost: No model cost. A few hundred bytes of status per heartbeat and negligible Mac CPU; USB power is supplied by the owner's Mac. Hardware unchanged.  ·  latency: 1–3 s initial handshake, then sub-100 ms cached status; does not contend with LTE audio.
- security: Serial commands must be read-only and nonce-bound; do not expose microphone/audio payloads or accept firmware flashing through this channel. Local status is bearer-protected before relay publication.
- depends on: A small documented diagnostic frame in nRF9160 and ESP32 firmware; Mac bridge serial-port access and a new typed local-device status route; An evidence ledger that records transport and freshness separately from relay delivery

### `firmware` — Implement a pendant-side bounded 'reality marker' frame emitted on boot, button press, audio capture start/stop, playback start/stop, and link transition. The frame includes monotonic sequence, uptime, firmware hash, transport, and last acknowledged audio/job id; no speech content. Mac USB mode and LTE relay mode use the same schema.
- **owner gets:** When the owner asks whether the pendant heard or played something, the system can answer from a device-originated marker rather than inferencing from a server upload. It makes offline capture and delayed delivery observable even when LTE is absent.
- effort: Medium-high: reserve a compact binary frame, persist only the last sequence/ack in flash, integrate with WebSocket and USB diagnostics, and add relay ingestion.  ·  risk: Flash wear and framing bugs; rate-limit markers, CRC-protect them, and persist only transition/ack state. If firmware is old, the Mac must label marker support as unavailable rather than guess.
- cost: No API cost; under 1 kB RAM and a few KB flash/code, with negligible radio overhead because transition markers are sparse.  ·  latency: No audible-path impact; link-transition marker may add one small LTE record.
- security: Hashes and IDs can reveal activity timing; encrypt in transit and redact job identifiers in owner-facing speech. Never include raw audio or page data.
- depends on: USB-tethered hardware presence channel; A shared cross-surface evidence ledger; Relay ingestion for device-originated acknowledgements


## What it asked for

_Nothing._
