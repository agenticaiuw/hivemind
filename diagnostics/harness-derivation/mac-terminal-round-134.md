# Harness derivation — mac-terminal — round 134

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-extension** — The live Mac/browser fleet is online with three Safari tabs, but browser_read_page on the Gmail tab failed: the extension does not have access to the frame. Two example.com tabs are also titled “Failed to open page.”
  - evidence: GET /jobs and GET /logs at 2026-08-07T17:53Z show browser_list_tabs success and browser_read_page failure with reason 'Failed to execute script. Extension does not have access to this frame.'
- **timezone** — Owner memory says America/Chicago, while live /machine-context reports timezone America/New_York; scheduled routine times therefore need an explicit authority rather than trusting the Mac zone.
  - evidence: owner discover output remembered timezone America/Chicago; GET /machine-context reports machine.timezone America/New_York.

## Capabilities it proposed

### "“If something I asked you to do fails, fix it yourself using the best available surface and tell me exactly what you recovered.”"
- **useful because:** Today a browser read failed because the extension lacked access to the frame, while the Mac and relay were healthy; the owner gets a dead-end failure instead of an answer. This would let the always-awake relay classify the failure, ask the Mac to repair/reopen or use an authenticated alternate path, and use the pendant for a concise truthful recovery notice. It is only valuable as a hive behavior: browser session state, Mac execution, relay retry policy, and worn notification must cooperate.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard-ux
- **model tier:** Background/cheap model for diagnosis and retry planning; realtime model only for the spoken recovery explanation.
- **latency:** Retry within 10 seconds for a local/browser error; at most two alternate strategies before speaking a clear failure. No silent indefinite loops.
- **cost:** Roughly $0.005–$0.03 per recovered task; dominated by an extra planner call and, if needed, one browser extraction. Local Mac/browser operations are otherwise free.
- **security:** Private page content must stay in the authenticated browser/relay path and not be copied to third-party services. Reopening tabs is reversible; never retry a send, purchase, delete, or submit automatically. The owner hears whether the result came from a fallback and receives the original error plus evidence.
- **missing:** A typed failure taxonomy distinguishing frame-permission, stale-tab, offline-surface, timeout, and command errors; A bounded alternate-surface retry orchestrator with idempotency keys and a no-repeat side-effect rule; A pendant event/voice receipt that distinguishes recovered, partially recovered, and failed; Browser bridge remediation for extension access to the current frame

### "“What time is it?” and “When will my scheduled brief actually run?” should always use my real timezone, even when the Mac, relay, and pendant disagree."
- **useful because:** The owner profile says America/Chicago while live machine context reports America/New_York. A spoken time answer or routine can therefore be wrong by an hour. A single timezone truth service would reconcile owner preference, Mac system zone, relay UTC, and any device-reported offset, surface a conflict instead of silently choosing, and show the next run in the owner's local time. This is a small interaction with outsized daily trust impact.
- **path:** pendant → relay-realtime → mac-planner → dashboard-ux
- **model tier:** No expensive model needed for offset calculation; use deterministic time-zone logic, with the realtime model only to phrase a conflict or ask which zone is authoritative.
- **latency:** Under 100 ms for current time and schedule conversion; conflict notice within one spoken turn.
- **cost:** Negligible API cost; deterministic route work. Occasional model phrasing is under $0.001.
- **security:** Store only an IANA timezone identifier and provenance, never location coordinates. A timezone change should be explicit and logged because it changes scheduled actions. Existing reminders should display both the original zone and converted next-run time during a transition.
- **missing:** An authoritative timezone record with owner preference, source, confidence, and effective-from timestamp; A scheduler that computes and returns nextRunAt in both UTC and owner-local time; A live consistency check across /machine-context, relay clock, and device telemetry; A pendant command/receipt for resolving a timezone conflict

### "“Use the clearest voice you can, and if the audio link degrades, keep talking and catch me up when it recovers.”"
- **useful because:** The current prototype decodes 24 kHz audio on the nRF9160 at roughly 25 ms per 60 ms packet while the ESP32 must resample to 44.1 kHz SBC for headphones; both chips are physically connected over USB today but the pendant is not LTE-registered. A link-aware speech path could detect USB/LTE/Bluetooth quality, select a lower-bitrate fallback without dropping the conversation, buffer only the missing spoken sentence, and replay a short catch-up when the bridge returns. The owner experiences uninterrupted conversation rather than codec silence and does not need to know which node failed.
- **path:** pendant → bridge → relay-realtime → mac-planner → dashboard-ux
- **model tier:** Realtime model for the live dialogue; deterministic firmware/relay DSP for codec and jitter decisions. Use a cheaper background model only to summarize missed audio into a catch-up sentence.
- **latency:** Keep interactive audio under 250 ms one-way when healthy; switch codec within 150 ms of loss; catch-up no longer than one sentence after recovery.
- **cost:** No extra model cost during healthy calls; a recovery summary costs about $0.001–$0.01. Bandwidth and battery are the dominant costs, especially if redundant packet protection is enabled.
- **security:** Audio remains between pendant, relay, Mac bridge, and the owner's headphones; do not persist raw audio. A tiny encrypted transcript/hash of the missed segment may be retained only until acknowledged, then deleted. Never replay private speech aloud after the owner has changed context without a visible/spoken cue.
- **missing:** A measured end-to-end audio health beacon carrying packet loss, jitter, queue depth, codec, and transport identity; Runtime Opus profiles and a PLC/FEC mode that fit the nRF9160 CPU/RAM budget; ESP32 bridge support for silence concealment and bounded catch-up buffering without starving A2DP; Relay policy that marks sentence boundaries and generates a missed-audio digest; A Mac USB serial transport manager that distinguishes a disconnected cable from a stalled audio stream

### "“When I’m in a meeting or around other people, keep private information out of the room, but still let me know if something truly urgent needs me.”"
- **useful because:** The owner should not have to remember to mute a wearable before a calendar event, disconnect headphones, or walk into a shared space. The Mac can know the meeting/window context, the browser can know which account is active, the relay can classify urgency, and the pendant/ESP32 can choose haptic, delayed, or spoken delivery. This is a physical privacy behavior, not just another briefing or page watch.
- **path:** pendant → bridge → mac-planner → browser-extension → relay-realtime → dashboard-ux
- **model tier:** Cheap deterministic policy for meeting state, output route, and urgency thresholds; realtime model only for compressing a genuinely urgent alert into one safe sentence.
- **latency:** Enter privacy mode within 2 seconds of a calendar/window/headphone change; urgent alerts delivered within 5 seconds by haptic or neutral spoken cue.
- **cost:** Near-zero API cost during normal operation; occasional urgency classification under $0.005. Main cost is firmware/bridge integration and testing false positives.
- **security:** Sensitive content must never be emitted by the ESP32 speaker or Mac speakers while privacy mode is active. Store only mode state and event metadata, not room audio or continuous microphone recordings. Calendar titles and browser account names require local-only handling.
- **missing:** A cross-surface privacy-mode state machine with explicit owner overrides; Calendar/meeting and headphone/proximity signals on the Mac; A pendant haptic or LED vocabulary for urgency without content; Relay output redaction that can produce a neutral cue before any private detail; A reliable bridge route that can hard-mute playback immediately

### "“Before you say anything sensitive out loud or use my logged-in accounts, make sure I’m actually the person wearing the pendant.”"
- **useful because:** A logged-in Safari session and an always-awake relay can outlive the owner’s attention; a nearby person could hear mail, calendar, or account details if the Mac is unattended. A deliberate button gesture or short local challenge on the worn nRF9160 can act as a presence proof, while the Mac and browser enforce it for sensitive reads and the relay suppresses speech until it is fresh. This gives the owner a usable privacy boundary that no Mac-only agent can establish.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard-ux
- **model tier:** No model for cryptographic challenge/response or policy; realtime model only interprets the owner’s spoken intent after the device proof succeeds.
- **latency:** Under 500 ms for a button challenge over USB/BLE/LTE when connected; expire proof after 2 minutes or on transport change.
- **cost:** Negligible per-request API cost. Engineering cost is secure firmware state, key provisioning, and enforcement hooks in Mac/browser/relay.
- **security:** Use a device-held private key or secure element challenge, never a spoken PIN or secret in prompts. Do not treat USB connection alone as proof. Sensitive page text, mail, and account actions must fail closed when proof is absent or stale; non-sensitive status remains available. Recovery requires an explicit local re-pair flow.
- **missing:** Secure identity and key provisioning for the pendant prototype and eventual product; A signed challenge/response protocol understood by relay, Mac agent, and browser bridge; A sensitivity policy for spoken output, browser reads, and Mac actions; Firmware button/LED feedback and replay-resistant nonce handling; Enforcement hooks that prevent sensitive results from reaching the voice renderer

### "“Don’t interrupt me three times about the same thing; give me one alert at the best moment and remember that I’ve acknowledged it everywhere.”"
- **useful because:** Calendar, browser watches, Mac jobs, and relay routines can all discover the same event, while the pendant, Mac, and browser may each notify independently. A shared attention ledger would deduplicate by semantic event, rank urgency against the owner’s current context, deliver through exactly one suitable surface, and synchronize acknowledgment so a dismissal on the pendant suppresses duplicate Mac/browser alerts. This is different from a briefing: it governs real-time attention across the whole hive.
- **path:** relay-realtime → pendant → mac-planner → browser-extension → dashboard-ux
- **model tier:** Cheap background/event model for clustering and urgency; deterministic delivery and acknowledgment logic; realtime model only for an urgent spoken alert.
- **latency:** Cluster and suppress duplicates within 1 second; deliver urgent items within 3 seconds; batch nonurgent items at the next attention window.
- **cost:** Usually under $0.002 per event for clustering, with most work in local durable state. No additional cost for acknowledgments or haptic delivery.
- **security:** The ledger must use opaque event IDs and minimal summaries, keeping sensitive browser content in its source surface. An acknowledgment must not silently approve a destructive action. The owner can inspect, undo dismissal, and choose per-source quiet rules.
- **missing:** A durable cross-surface event identity and semantic deduplication ledger; Delivery/acknowledgment receipts shared by pendant, Mac, browser, and relay; An attention policy using meeting/privacy/audio state and quiet hours; A user-facing queue to restore or inspect suppressed events; Per-event source provenance so the owner can open the original evidence


## What it asked for

_Nothing._
## Its own summary

This round produced three new owner-facing capabilities: (1) cross-surface recovery when browser/Mac work fails, with bounded alternate strategies and truthful spoken receipts; (2) authoritative timezone reconciliation, because owner memory says America/Chicago but live Mac context says America/New_York; and (3) adaptive end-to-end speech that preserves conversation through USB/LTE/Bluetooth degradation and gives a short catch-up. I also recorded the live browser frame-access failure and notified all agents. A fourth shell-forensics proposal was correctly rejected as already covered by an existing flight-recorder idea, so I did not restate it.

**Biggest unknown:** Whether the browser bridge can be repaired by opening the correct frame/permissions or needs a different extraction path, and what the actual USB serial/audio telemetry looks like while the pendant and ESP32 are connected. Still needed: a live audio/link health beacon, a timezone authority contract, browser frame remediation, and bounded cross-surface retry orchestration.

