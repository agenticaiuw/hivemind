# Harness derivation — unified — round 260

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Do it, but don't tell me it's done until you can prove the result is real.""
- **useful because:** The system currently has execution records and evidence queries, but an action can still be spoken as complete when the Mac/browser effect was never observed. This cross-surface completion gate would make the pendant trustworthy: execute, independently verify the intended state, and say done, uncertain, or failed with the exact missing proof.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic verifier first; background model only to explain contradictory evidence. Realtime is used only for the short owner-facing verdict.
- **latency:** Reversible local actions: under 3 seconds. Browser/network effects: up to 15 seconds with explicit 'checking' state; never wait indefinitely.
- **cost:** Usually <$0.01 in API/model cost; dominated by no-model HTTP/browser observations. Explanation uses a small background-model call only on conflict.
- **security:** Verification must be bound to the exact job, tab/app target, and expected postcondition; never treat a screenshot or text match alone as proof for an irreversible action. Secrets and page contents stay redacted. Require the existing physical transaction approval latch for high-risk writes.
- **missing:** Executor integration that makes a postcondition mandatory before the spoken completion event; A typed postcondition schema for Mac and browser action types; Independent observation receipts joined to the job ledger

### ""When I come back, give me the one-minute story of what changed while I was away—and only interrupt me if something truly needs me.""
- **useful because:** The system has separate jobs, browser results, pipeline events, commitments, and device alerts, but no owner-facing causal digest that explains changes rather than listing records. This gives the wearer a compact, privacy-redacted return brief: completed effects, failed/stale work, commitments with evidence, and a small set of decisions requiring action.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background model for clustering and wording; deterministic collectors and policy filters decide inclusion. Realtime only reads the final brief if the owner asks by voice.
- **latency:** Build in under 5 seconds on demand; scheduled refresh under 30 seconds. Never interrupt an active conversation; queue until the next natural turn.
- **cost:** <$0.02 per generated brief; most cost is context serialization, so send only deltas since the last acknowledgement.
- **security:** Default to redacted titles and domains, not page text or audio. Include only explicitly bound browser sessions/apps. Every item links to provenance and supports dismissal; extracted facts must obey the owner's listable/individually deletable rule.
- **missing:** A durable owner-acknowledgement cursor across relay, Mac, browser, and pendant; A delta aggregator that correlates job, commitment, alert, and audio-delivery events; A quiet-hours/urgency policy value rather than hardcoded interruption behavior

### ""If a task spans my browser and Mac, let me hand it off and pick it up later without repeating anything or losing where we were.""
- **useful because:** A real owner task can stop between browser navigation, Mac work, and a pendant interruption. The system already has durable workbench contexts and handoff inspection, but no owner-level handoff experience that packages the next safe step, completed effects, unresolved approval, and exact browser/app bindings. This would turn interruptions and machine restarts into continuity instead of duplicate actions.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic state machine for context, leases, replaySafety, and approval; background model summarizes the handoff in owner language.
- **latency:** Capture a handoff under 2 seconds; restore context under 5 seconds. If the next step is unrepeatable or approval-bound, stop and ask rather than guessing.
- **cost:** <$0.01 for deterministic handoff; optional <$0.01 summary call. Storage is bounded metadata, not audio or page secrets.
- **security:** Auto-continue only idempotent/additive steps with valid leases; block unrepeatable/unknown steps. Bind browser continuation to tab/session identity and Mac app/path. Never serialize credentials or page contents into the handoff. A physical approval event is required for staged high-risk actions.
- **missing:** Production caller for the existing workbench handoff engine; Orchestrator closeLedger integration so completed plans are not falsely marked interrupted; Relay job lease_until and requeue sweep; A user-facing 'resume this handoff' route and pendant delivery on the next conversation

### ""For the next two hours, do not send, buy, publish, or message anything unless I explicitly release that boundary.""
- **useful because:** The owner needs a temporary, explicit safety boundary that applies everywhere, not a permanent setting and not a per-action prompt. It should follow work across the pendant, relay, Mac, and browser, survive a link drop, expire automatically, and make blocked actions visible instead of silently discarding them.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic policy enforcement; no model call is needed to block or release. Realtime only confirms the boundary state conversationally.
- **latency:** Enforcement before dispatch, under 100 ms locally; relay-held work should be marked blocked within 1 second. Expiry must be checked at every boundary, not by a best-effort scheduler.
- **cost:** Negligible API cost. Bounded signed policy records and event receipts dominate storage, not inference.
- **security:** The boundary must be deny-by-default for named risk classes, cryptographically bound to the owner/session, monotonic against replay, and visible on the pendant. A physical release should be required for high-risk exceptions. Never infer scope from vague language; show the exact actions and expiry.
- **missing:** A cross-surface policy token enforced before relay claim, Mac dispatch, and browser command execution; A durable expiry and conflict-resolution record; A pendant-visible blocked-state and explicit release path

### ""Give this one task access to exactly what it needs, then prove that access is gone when the task ends.""
- **useful because:** Today approval authorizes an action, but it does not provide a least-privilege delegation that spans a logged-in browser session, Mac app, and relay job. This capability would issue a task-scoped, time-limited capability grant, constrain targets and data classes, revoke it on completion or cancellation, and show the owner a tamper-evident revocation receipt.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic authorization and revocation; background model may translate the grant into plain language but never decides its scope.
- **latency:** Grant and enforcement decisions under 200 ms; revocation receipt under 2 seconds after task settlement. If revocation cannot be confirmed, the task remains visibly unresolved.
- **cost:** <$0.01 per task, primarily event storage and browser/Mac policy checks; no model call required for normal operation.
- **security:** Do not expose credentials to the model or pendant. Bind grants to exact browser session/tab, Mac app/path, job, action types, data classes, nonce, and expiry. Revocation must be fail-closed and independently checked by each surface. High-risk grants still require the physical transaction latch.
- **missing:** A capability-token enforcement layer in the relay, Mac executor, and browser bridge; Browser and Mac adapters that can report revocation confirmation; A durable grant/revocation ledger separate from ordinary job receipts

### ""Show me exactly what information left my devices recently, where it went, and let me stop or erase the parts I choose.""
- **useful because:** The owner has privacy controls that stop future capture, but cannot currently inspect a unified, understandable record of what crossed the pendant, relay, Mac, and browser boundaries. A data-flow ledger would distinguish audio, transcript, page-derived facts, action metadata, and credentials, expose destination and retention state, support cancellation of queued transfers, and produce deletion receipts without deleting the action audit trail.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic lineage and deletion state machine; background model summarizes the ledger only after redaction.
- **latency:** Recent-flow view under 3 seconds; cancellation should take effect before the next upload attempt. Off-machine deletion reports requested/pending until replicated stores confirm it.
- **cost:** <$0.02 for an owner-readable summary; storage is bounded metadata with hashes and destinations, never routine raw audio.
- **security:** The ledger itself must minimize sensitive content: hashes, categories, destination, timestamps, retention, and provenance rather than payloads. Access is owner-only. Deletion of extracted facts and derived copies must remain separate from immutable action accountability. A privacy latch must stop new flows immediately even if the relay is unreachable.
- **missing:** Authenticated flow events emitted by every capture, relay upload, browser command, and Mac action; A cross-store deletion coordinator with pending/confirmed receipts; A dashboard and pendant query path that redacts secrets while preserving recognizable provenance


## What it asked for

_Nothing._
