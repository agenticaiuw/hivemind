# Harness derivation — faculty-perception — round 30

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-ui-reachability** — Mac agent is not UI-action capable right now: Accessibility trusted=false, screenRecording=false, input reachability failed, and ui_actions_will_reach_the_screen=false. It reports UI action success cannot be trusted until Accessibility is granted to AI Pendant Agent.
  - evidence: GET /observe at 2026-08-07T10:29:51.375Z; GET /ops/status at same period
- **browser-extension-connectivity** — home-chrome browser extension is offline with no active tab; Mac agent reports 3 pending browser commands.
  - evidence: GET /browser/status and GET /ops/status at 2026-08-07T10:29:51Z
- **pendant-offline-queue** — Pipeline contains pendant-origin events showing held alerts were surfaced (2 at uptime 323, 1 at uptime 114) and a moment bookmark was held on microSD while link was down.
  - evidence: GET /pipeline response, events from nrf9160 at 2026-08-07T07:12–07:22Z

## Capabilities it proposed

### "“What happened while I was disconnected? Give me the exact timeline, including anything that was only queued, anything that really ran, and anything that still needs attention.”"
- **useful because:** Today the owner can receive a late alert or a success-looking receipt without being able to distinguish offline capture, relay delivery, Mac execution, browser execution, and mere queueing. This gives them a causal, evidence-backed reconstruction after LTE, Mac, or browser outages—not just a list of notifications.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use deterministic event correlation and health snapshots first; use a cheaper background text model to summarize the reconstructed timeline. Use realtime only to speak the already-built summary when asked through the pendant.
- **latency:** Up to 3 seconds for a normal spoken query; background reconciliation runs incrementally whenever a device reconnects, so most results are already prepared.
- **cost:** Low: event joins, hashes, timestamps, and reachability checks dominate; roughly $0.001–$0.01 per generated summary depending on timeline length, with no model call when the owner only requests raw status.
- **security:** Authenticated browser URLs and page contents must not be copied into the relay or pendant; retain redacted event IDs, domains, hashes, action type, and state transitions. Require confirmation before exposing sensitive account details or replaying any queued action. Never infer execution from a client-reported success when reachability was false.
- **missing:** A durable cross-surface event ledger with one idempotency ID spanning pendant microSD records, relay jobs, Mac jobs, and browser commands; Reconnect-time reconciliation that records explicit state transitions (captured, uploaded, accepted, executed, observed, failed, expired) rather than appending disconnected logs; A verified Mac/browser preflight result attached to every action receipt, including Accessibility and extension reachability; A redacting timeline API and dashboard/pendant renderer that can distinguish evidence from inference

### "“If I ask you to do something while the connection is down, remember exactly what I meant, tell me that it is only saved locally, and ask me again before doing it when you reconnect if anything may have changed.”"
- **useful because:** The pendant can currently hold alerts and bookmarks, but the owner cannot safely entrust it with a spoken intent during an outage. This would preserve the intent without pretending it ran, then prevent stale actions when the Mac, browser session, permissions, or world state have changed.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Local pendant firmware stores a compact signed intent envelope; relay performs deterministic replay eligibility checks; a cheaper background model classifies whether context changed and drafts a confirmation. Realtime only handles the immediate spoken acknowledgement and final confirmation conversation.
- **latency:** Immediate local acknowledgement under 500 ms while offline; on reconnect, eligibility evaluation under 2 seconds and confirmation prompt on the next pendant interaction.
- **cost:** Negligible offline storage and event-join cost; approximately $0.001–$0.02 for a reconnect-time semantic-change assessment, depending on whether model review is needed.
- **security:** Do not store raw microphone audio or credentials on the pendant; store encrypted intent text or a user-approved structured command, creation time, expiry, required surfaces, and a nonce. Destructive, financial, communication, or authenticated-browser actions always require fresh confirmation. Expire intents and expose cancellation; never replay solely because connectivity returned.
- **missing:** An encrypted pendant intent envelope with expiry, nonce, and explicit offline acknowledgement state; A relay protocol for reconnect negotiation and duplicate-safe intent handoff; A context-diff service that compares the original assumptions with current Mac/browser state before replay; A pendant UI/audio state that clearly distinguishes saved-locally, awaiting-review, expired, and executed


## Changes it proposed to its own stack

### `integration` — Add a cross-surface perception firewall and truth ledger. Before any Mac/browser action result is allowed into a spoken answer or durable receipt, snapshot /observe, /ops/status, browser heartbeat state, and the relevant job/pipeline event. Attach reachability, permission, source, freshness, and verification level (executed, observed, queued, or unverified). If Accessibility is false, screen recording is absent, or the browser extension is offline, automatically downgrade UI receipts to blocked/unverified, quarantine stale pending commands, and have the relay surface a concise recovery fact on the pendant. Reconcile late pendant microSD alerts/bookmarks and browser results by idempotent event IDs rather than treating delivery as execution.
- **owner gets:** The owner will stop hearing 'done' when nothing reached the screen—a live defect right now. They will know whether something actually happened, is merely queued, or needs a permission/connection fix, even after leaving the Mac or losing LTE.
- effort: Medium: shared typed evidence schema, pre-action health snapshot, receipt gate, stale-command quarantine, and relay/pendant rendering; add integration tests for permission loss, browser disconnect, and late microSD delivery.  ·  risk: A transient health probe could conservatively say unverified and delay a harmless confirmation; recover by retrying observation and retaining raw job IDs. Never delete commands automatically—quarantine and expose them for review.
- cost: Small extra local probes and D1 event metadata; negligible model cost because this is deterministic, with one short fallback generation only when a spoken explanation is needed.  ·  latency: ~100–300 ms for local health snapshots; no extra model round trip on healthy paths.
- security: Improves safety by preventing false success claims and limiting stale authenticated browser commands. Evidence must redact page content/secrets and retain only hashes, IDs, URLs, and permission states.
- depends on: A typed shared context/provenance projection (chg-a82e0b13 or successor); Durable browser command queue with idempotency and tab affinity (chg-14accc01); Pendant offline-event IDs and acknowledgement semantics

### `hardware` — Add a low-power, battery-backed RTC with periodic LTE time calibration and a secure monotonic event counter to the pendant, and expose both wall-clock uncertainty and counter IDs in every offline alert, bookmark, audio, and intent record. The relay should preserve the original device timestamp instead of replacing it with upload time, then align device, relay, Mac, and browser clocks in the reconciliation ledger.
- **owner gets:** After an outage, the owner would get a trustworthy sequence of what happened—even when the pendant was offline for hours or crossed a timezone boundary—instead of ambiguous uptime timestamps or events appearing to happen when they finally uploaded.
- effort: Medium hardware revision plus firmware timestamp plumbing, LTE calibration, uncertainty tracking, and ledger integration; can be prototyped in firmware using the existing modem time before the RTC board revision is ready.  ·  risk: RTC drift, battery depletion, or bad network time could create misleading absolute times. Mitigate by retaining monotonic counters, reporting uncertainty bounds, rejecting backward jumps, and treating wall-clock time as approximate until calibrated.
- cost: Approximately $1–$3 BOM increase for an ultra-low-power RTC, crystal, and backup cell or supercapacitor; sub-milliwatt backup draw, with negligible API cost.  ·  latency: No user-visible latency; calibration occurs opportunistically after LTE registration.
- security: The secure counter and signed timestamps make replay/duplication harder. Do not put secrets in RTC metadata; protect the event key and allow clock reset only through authenticated firmware.
- depends on: Cross-surface event ledger and reconnect reconciliation; Firmware event schema carrying uncertainty and monotonic IDs; A defined authoritative timezone policy


## What it asked for

_Nothing._
