# Harness derivation — faculty-perception — round 29

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-actionability** — At 2026-08-07T10:27Z, the Mac bridge and relay are reachable, but local-agent readiness is false because Accessibility is not trusted and Screen Recording permission is missing; computer-use loop is disabled and vision upload consent is false.
  - evidence: GET /ops/status HTTP 200: agent.ready=false; permissions.accessibility.trusted=false; permissions.screenRecording.granted=false; computerUse.loopEnabled=false; visionUploadConsented=false.
- **browser-availability** — At 2026-08-07T10:27Z, the Chrome browser extension is offline; its last seen time is 2026-08-07T09:21:08.821Z and 3 commands are pending.
  - evidence: GET /browser/status HTTP 200 returned online=false, home-chrome online=false, pendingCommands=3.
- **offline-pendant-events** — The live pipeline contains pendant-origin offline-store events: a moment bookmark captured while link_at_capture=down and held alerts surfaced later; these events are represented as processing runs rather than a clearly acknowledged/closed state.
  - evidence: GET /pipeline HTTP 200 showed nrf9160 runs with meta.storage=microSD, origin=pendant-offline-store, bookmark link_at_capture=down, and alert_delivered events.
- **mac-timezone** — The Mac machine-context currently reports timezone America/New_York.
  - evidence: GET /machine-context HTTP 200 returned machine.timezone=America/New_York.

## Capabilities it proposed

### "“Before you act, tell me what is actually reachable right now, what is stale or queued, and what you can safely do offline; when I reconnect, reconcile anything my pendant captured.”"
- **useful because:** Today relay reachability is being mistaken for actionability: Mac bridge is online but not ready, browser is offline with 3 pending commands, and pendant offline bookmarks/alerts appear as processing runs. The owner needs one truthful answer before relying on an action, plus a de-duplicated recovery report after reconnect.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard-ux
- **model tier:** Use a cheap background model to normalize and summarize signed status/events; use realtime only to speak a short immediate preflight answer during a pendant conversation. Do not spend the expensive tier interpreting raw telemetry.
- **latency:** Preflight under 500 ms from cached signed attestations; reconnect reconciliation within 10 s of a heartbeat, with a concise spoken result when complete.
- **cost:** Usually <$0.01 per reconciliation; dominated by a small background summarization call. Preflight should be rule-based and nearly free.
- **security:** Never expose private tab titles, account state, or audio contents in a broad status summary. Bind attestations to paired device IDs, include timestamps/TTL and capability scopes, and redact sensitive event payloads. Require confirmation before replaying queued browser or Mac mutations; offline pendant captures may be sensitive and need owner-controlled retention.
- **missing:** A typed cross-surface availability attestation contract distinguishing reachable, ready, permitted, stale, offline, and queued; Durable event IDs plus explicit received/acknowledged/applied states for pendant offline alerts/bookmarks and relay forwarding; A reconciliation endpoint that atomically deduplicates pendant events against relay/Mac journals; A dashboard and spoken preflight renderer that cites freshness and refuses to claim completion from mere connectivity

### "“When you tell me something happened, let me ask ‘why do you believe that?’ and hear a short, human-readable proof that connects what I said on the pendant to the exact device, account, page, and outcome involved.”"
- **useful because:** The owner cannot today distinguish a spoken model claim, a queued request, a Mac execution, a browser observation, and a confirmed external outcome. A cross-surface proof view would let them challenge mistaken state without reading logs, especially when a bridge reconnects late or an action has multiple partial results.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard-ux
- **model tier:** Generate the proof structure deterministically from signed events and receipts; use a cheap background model only to compress it into plain language. Realtime should speak only the short explanation when the owner asks during a live call.
- **latency:** Return the structured proof in under 300 ms from local/relay indexes; speak a concise explanation within 2 seconds. Deep historical reconstruction can run asynchronously.
- **cost:** Near-zero for indexing and deterministic joins; typically <$0.01 for optional plain-language compression. Storage and signature verification dominate rather than model usage.
- **security:** Proofs must not leak private page contents, credentials, raw audio, or unrelated activity. Use scoped disclosure: default to hashes, titles, timestamps, permission scopes, and redacted snippets; require explicit confirmation to reveal sensitive evidence. Preserve tamper-evident history without making immutable deletion impossible for retained audio or private data.
- **missing:** A common signed evidence-envelope format spanning pendant audio, relay transcription/response, Mac plans and receipts, browser observations, and device acknowledgements; A causal-link index connecting one owner utterance to derived plans, actions, external effects, and failures across reconnects; Owner-facing proof rendering with progressive disclosure and redaction controls; A verifier that marks claims as observed, inferred, attempted, or externally confirmed rather than presenting them all as facts


## Changes it proposed to its own stack

### `integration` — Create a cross-surface readiness-and-reconciliation ledger. Each pendant, relay, Mac, and browser heartbeat publishes a signed capability attestation with observed_at, expires_at, permissions, and scopes (for example: can_speak, can_receive_audio, can_read_private_tab, can_execute_GUI). Every offline pendant alert/bookmark and every queued browser/Mac command gets a globally unique event ID and a state machine received -> acknowledged -> applied/rejected, with atomic deduplication. The relay exposes one snapshot consumed by realtime, judgement, action, and dashboard instead of inferring readiness from online booleans.
- **owner gets:** The owner gets an honest answer such as “I can hear you and speak, but I cannot control the Mac or read Chrome; two pendant notes are waiting,” rather than a false impression that the system is ready. Reconnects stop producing duplicate alerts or silently replaying stale commands.
- effort: Medium-high: shared schema and D1 tables, firmware event-ID persistence/ack upload, Mac/browser attestation producer, relay reconciliation worker, and dashboard/speech rendering; migration needs compatibility with current pipeline records.  ·  risk: Incorrect expiry could cause unnecessary refusal, while incorrect permission reporting could permit an unsafe action. Default to fail-closed for mutations, retain immutable transition history, and provide a manual “show pending/reconcile” view. Recover by replaying idempotent events from the ledger.
- cost: Small D1 writes per heartbeat/event and occasional cheap summarization; no realtime call required for the ledger. Firmware storage is a few KB for a ring of event IDs and acknowledgements, not routine audio.  ·  latency: Cached preflight adds <100 ms locally; cross-surface reconciliation is asynchronous and should complete within seconds after heartbeat.
- security: Improves security by making permissions and freshness explicit, but attestations and event metadata are sensitive. Pair and authenticate every producer, minimize payloads, encrypt in transit, and apply retention limits.
- depends on: A typed context projection/contract shared by all surfaces; A durable event acknowledgement model for pendant offline-store records; Mac and browser producers that can report permission-scoped readiness rather than only online status


## What it asked for

_Nothing._
