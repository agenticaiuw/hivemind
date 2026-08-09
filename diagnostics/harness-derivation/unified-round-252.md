# Harness derivation — unified — round 252

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “make sure this gets done,” carry it through every surface and tell me only when there is proof it happened—or exactly what blocked it."
- **useful because:** Turns the pendant from a planner that can claim success into an accountable operator: it can execute on the Mac/browser, verify the result against bound evidence, recover safe failures, and leave an explicit pending state instead of silently losing the promise.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for plan/evidence synthesis; realtime only for the spoken acknowledgement
- **latency:** Acknowledge intent in under 2 s; safe execution and verification may take up to 60 s, with progress spoken only at meaningful state changes.
- **cost:** Usually 1 background planning call plus 1 cheap evidence call; roughly $0.01–$0.05 depending on browser complexity. Mac/browser execution dominates latency, not tokens.
- **security:** Evidence queries must stay bound to explicitly named tabs/apps and redact secrets. Irreversible or unrepeatable steps require the existing physical transaction approval latch. Never say done from an executor receipt alone.
- **missing:** A production orchestrator caller for the existing commitment_evidence_query and workbench handoff primitives; A durable commitment state that joins spoken promise, plan digest, job, evidence candidates, and final disposition; Safe automatic retry only for replaySafety idempotent/additive; human continuation for unrepeatable/unknown; A user-facing pending/blocked view on the dashboard

### "Watch this logged-in page for the condition I named, and when it appears, prepare the next step—but never submit or send anything until I physically approve it on the pendant."
- **useful because:** This is the first useful form of unattended browser work: the relay can wait while the Mac sleeps or the page changes, the browser can use the owner’s existing authenticated session, and the pendant remains the authority for an irreversible submit. It avoids polling manually and avoids giving the browser an unbounded autonomous agent.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for condition extraction and page-state comparison; deterministic browser polling and approval state machine; realtime only to explain status when asked
- **latency:** Create watch in under 3 s; poll at a configurable 15–120 s cadence; surface a match within one poll; approval-to-submit under 5 s.
- **cost:** Near-zero model cost after setup; one background call to compile the condition and occasional cheap calls only when page structure changes. Browser polling and relay storage dominate.
- **security:** Bind the watch to an exact tab/session and URL pattern, redact page contents from relay logs, cap lifetime and poll count, and invalidate on navigation/login change. The prepared action must carry a digest/world fingerprint and require the existing physical_transaction_approval_latch; never accept approval from page text or a stale spoken phrase.
- **missing:** A durable relay watcher with lease/expiry and backoff, separate from ordinary one-shot browser commands; A browser snapshot-diff matcher that returns bounded evidence rather than raw page dumps; A handoff route that stages a matched action and pushes its nonce to the pendant inbox; A dashboard control to pause, revoke, or inspect the watch

### "Stop everything you are currently doing for me, cancel queued browser and Mac work, revoke any pending approvals, and tell me what could not be stopped."
- **useful because:** A single emergency stop is more useful than hunting through jobs or tabs when the owner notices an unsafe or unwanted action. It would coordinate relay claims, Mac jobs, browser leases, staged transactions, and pendant playback, then report residual risk instead of pretending cancellation is instantaneous.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic control plane; no model required except optional plain-language summary
- **latency:** Local pendant mute/cancel immediately; relay cancellation receipt under 2 s; Mac/browser acknowledgements within 10 s, with late completions explicitly reported.
- **cost:** No inference cost. Small bounded writes for cancellation intents and receipts.
- **security:** The stop command must be authenticated to the owner session and idempotent. It may cancel reversible work but must not claim to undo an irreversible external side effect. Preserve the audit trail, revoke approval nonces, stop queued audio/playback, and distinguish cancel-requested, cancelled, and already-committed.
- **missing:** A correlated cancellation fan-out endpoint spanning relay jobs, Mac jobs, browser commands, workbench contexts, and pending approvals; A durable cancellation barrier that late workers check before dispatch and before commit; A pendant-visible acknowledgement path that works offline and reconciles on reconnect; A residual-effects report linking each non-cancellable step to its receipt

### "Let me state rules like “never send messages without showing me the recipient” or “never upload my files,” then enforce those rules across the pendant, relay, Mac, and browser."
- **useful because:** The owner should not have to remember which surface might bypass a preference. A spoken policy would become an inspectable, versioned guard that blocks or stages actions everywhere, rather than relying on model judgment at each turn.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background model compiles natural-language rules into a constrained policy DSL; deterministic enforcement runs on every action and browser command
- **latency:** Compile and explain a rule in under 5 s; enforcement adds under 20 ms to local dispatch and does not delay audio.
- **cost:** One background call when a policy changes, typically under $0.02; enforcement is local deterministic code.
- **security:** Policies must fail closed for ambiguous high-risk rules, show exact matched action fields, and be versioned so an action receipt records which rule allowed or blocked it. Policy text and browser contents must not be sent to the model unnecessarily.
- **missing:** A policy DSL and validator covering action type, destination, data class, confirmation, and surface; A single pre-dispatch enforcement hook shared by Mac, browser, relay, and pendant-originated actions; Policy test cases showing allowed, blocked, and ambiguous examples before activation; A dashboard and voice command to inspect, suspend, and roll back policy versions

### "Keep sensitive page contents and files on my Mac whenever possible, and tell me exactly what left the machine before any service or model receives it."
- **useful because:** Today a browser or Mac task can expose more context than the owner intended, with no unified data-flow explanation. A local classification and redaction gate would make the system useful for logged-in work without turning every page into relay-visible data.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** local deterministic classifiers first; background model only for uncertain classification after redaction; realtime is not needed
- **latency:** Classify ordinary text in under 100 ms; uncertain content pauses for explicit approval rather than blocking indefinitely.
- **cost:** Near-zero for deterministic patterns and hashes; occasional small background calls for ambiguous content, under $0.01 each.
- **security:** Raw sensitive content must stay local by default. The relay receives only classifications, hashes, and redacted excerpts. The owner must be able to inspect the proposed outbound payload and revoke a session. It must not falsely claim that screenshots or browser-rendered pixels were redacted.
- **missing:** A Mac-local data classifier for credentials, personal identifiers, files, and page regions; A browser extraction contract that labels provenance and supports field-level redaction; A pre-model/pre-relay egress gate with an explicit blocked/approved receipt; A session-scoped exposure ledger visible to the owner

### "If I say “I’m in trouble,” use my pendant to start a clearly confirmed emergency workflow: alert the contacts I chose, show me what will be shared, and keep retrying until someone or I acknowledge it."
- **useful because:** The wearable is the one surface physically available when the Mac or browser is unreachable. A deliberate emergency workflow could bridge pendant, relay, phone/browser, and Mac while remaining different from an ordinary reminder or notification: it needs durable escalation, acknowledgement, and a truthful failure state.
- **path:** pendant → relay → mac-bridge → browser → iOS → dashboard
- **model tier:** deterministic workflow with background summarization only for the human-readable status; realtime voice is optional
- **latency:** Local pendant alarm and staged alert immediately; first delivery attempt under 5 s; retry/escalation on a bounded schedule until acknowledgement or explicit cancellation.
- **cost:** Minimal model cost; relay retries and messaging/provider fees dominate. The owner must choose contacts and acceptable channels.
- **security:** Never infer emergency from ordinary distress language without a configured trigger and confirmation policy. Require a physical confirmation or an owner-configured explicit phrase, disclose location/content being shared, encrypt contact data, rate-limit retries, and preserve a tamper-evident event trail. Location is unavailable today and must not be fabricated.
- **missing:** Owner-configured emergency contacts, channels, and confirmation/escalation policy; A relay durable escalation state machine with provider delivery receipts and leases; Firmware emergency pending/acknowledge/cancel behavior that works offline; A location source or an explicit no-location mode; iOS/browser delivery adapters and a dashboard acknowledgement surface


## Changes it proposed to its own stack

### `relay` — Add a cross-surface ‘state of delivery’ record for every assistant response: correlate relay acceptance, pendant receipt, bridge playback start/finish, interruption reason, and any queued retry under one opaque artifact ID. Expose a compact owner-facing timeline and make missing downstream receipts expire into an explicit unknown state rather than success.
- **owner gets:** When the pendant is silent, the owner can ask “did you answer me, or did the audio never arrive?” and get a truthful answer instead of a false successful job status.
- effort: Medium: extend the existing audio_delivery_ack_queue contract, add relay correlation and a small dashboard timeline, then instrument bridge/pendant event emitters. Test with the existing 24 kHz validator and fault injector.  ·  risk: Event loss or clock skew could produce unknown rather than false certainty; use monotonic sequence numbers, idempotent event IDs, bounded retention, and clearly label inferred versus device-confirmed states. Never store routine raw audio.
- cost: Negligible storage (bounded metadata ring plus relay rows); one cheap write per lifecycle event, no additional model calls.  ·  latency: No hot-path audio delay if events are fire-and-forget; owner timeline may lag by one polling interval.
- security: Opaque IDs and redacted metadata only; no transcript/audio in the receipt. Access must follow the existing bearer/session binding.
- depends on: audio_delivery_ack_queue (s9-vtxc) needs bridge acknowledgement correlation folded in; audio_path_diagnostic_fixture (s16-dbfs) for repeatable end-to-end event tests; A relay schema migration for correlated delivery artifacts


## What it asked for

_Nothing._
