# Harness derivation — faculty-judgement — round 226

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Give me a trustworthy answer from that page, but don't let the page's private details become part of my permanent memory—and let me revoke it later.”"
- **useful because:** Today browser evidence, derived facts, spoken audio, and revocation are disconnected. This would let the owner use authenticated/private pages without silently creating long-lived quotes or facts, while retaining a source-linked answer that can be inspected and revoked.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Use the cheap model for extraction and redaction; reserve realtime only for the owner's spoken synthesis. No model should receive raw page content unless the owner-approved destination policy permits it.
- **latency:** 2–5 seconds for a read-and-answer; under 1 second to show the source and revocation state in the dashboard.
- **cost:** About one cheap extraction call plus one short realtime synthesis when spoken; browser capture and revocation are local/D1 writes and dominate no model cost.
- **security:** Default to a short-lived redacted claim, never raw quote in fleet memory; classify before fan-out; require explicit confirmation before an extracted claim can drive an external mutation. Revocation must propagate to facts, graph copies, browser provenance, briefing queue, and relay projection, not merely tombstone the capsule.
- **missing:** Wire browserProvenance routes into production; Add capsuleId/source links to memory facts and context-graph copies; Make the Mac bridge write fleetMemory events and apply retractions; Implement a cross-store revoke cascade and a destination policy table; Add an owner-facing source/claim view in the dashboard

### "“When you give me a briefing, tell me what I actually heard, what was skipped, and whether the pendant played it successfully.”"
- **useful because:** A generated briefing is not the same as a delivered briefing. The owner currently cannot distinguish server acceptance, download, playback start, interruption, and never-heard items. This turns the wearable into an accountable communication channel rather than a black hole.
- **path:** relay-realtime → pendant → mac-planner → dashboard
- **model tier:** No expensive model for delivery accounting. Use deterministic ACK reconciliation and a cheap summarizer only when the owner asks for a missed-items digest; realtime is reserved for the short spoken answer.
- **latency:** ACK ingestion under 1 second online; a missed-item digest in 2–4 seconds on demand.
- **cost:** Negligible API cost for event reconciliation; one cheap summarization call only when collapsing many missed items.
- **security:** Store opaque artifact IDs and positions, not audio or transcript by default. Deduplicate signed offline events, reject stale/replayed device sequences, and never claim ‘you heard this’ from a download ACK alone. Sensitive item titles must be redacted in any spoken catch-up.
- **missing:** Join pendant delivery events to briefing item IDs and relay jobs; Expose a durable owner-facing playback ledger and missed-item query; Teach catchup/briefing triage to consume playback_finished versus interrupted/no_audio; Add a dashboard view and a spoken ‘what did I miss?’ action

### "“If a request spans my Mac and browser and one side fails, keep the task alive and bring me back to the exact next safe step—without retrying a side effect twice.”"
- **useful because:** A real-life task often crosses relay, Mac, and an authenticated browser. Today a crashed Mac job can remain processing forever, IDs do not join across surfaces, and a resumed context is not a recoverable execution checkpoint. This would preserve intent without silently duplicating a send, purchase, or deletion.
- **path:** relay-realtime → mac-planner → browser-extension → pendant → dashboard
- **model tier:** Deterministic lease/idempotency/recovery machinery first; use a cheap model to explain the checkpoint. Realtime only speaks the one next step when the owner returns.
- **latency:** Failure detection within the existing lease interval (target 30–60 seconds); resume explanation under 2 seconds.
- **cost:** Near-zero model cost for normal recovery; occasional cheap explanation call. Storage is a bounded relay job/checkpoint ledger.
- **security:** Requeue only idempotent/read or explicitly reversible steps. Any external side effect must remain parked behind the existing policy evaluator and physical approval latch. Bind relay, Mac, browser, action, and device delivery IDs; expire checkpoints and show the exact evidence used to decide a retry is safe.
- **missing:** Add lease_until and requeue sweep to relay_jobs; Persist relay-job↔Mac-job↔browser-command joins; Record typed step checkpoints and outcome/receipt before advancing; Make revalidate_pending_plan and autonomy_policy_evaluate mandatory at resume; Expose a durable owner-facing recovery card and pendant alert

### "“Do not tell me that action succeeded until you independently verify the result in the system where it should exist.”"
- **useful because:** A local receipt or HTTP 200 is not proof that an email was sent, a reminder exists, a browser change stuck, or a file has the intended contents. The owner gets a truthful distinction between accepted, observed, and verified outcomes instead of false completion.
- **path:** relay-realtime → mac-planner → browser-extension → pendant → dashboard
- **model tier:** Use deterministic postcondition checks whenever possible; use a cheap model only to translate conflicting observations into a short explanation. Realtime is only for the final spoken result.
- **latency:** Verification within 2–5 seconds after reversible actions; longer checks should become a pending card rather than blocking speech.
- **cost:** Usually no model call; one cheap explanation call only when observations disagree. Cost is dominated by the extra readback probes.
- **security:** Verification must be read-only and scoped to the intended target. Never infer success from a screenshot or stale cache; retain source timestamps and redact private result content from spoken output. Mutations still require existing policy and physical approval.
- **missing:** A typed postcondition schema for each action family; Readback adapters for Mail, Calendar/Reminders, files, browser state, and external confirmations; A durable link between the mutation receipt and its verification observations; Owner-facing statuses: accepted, applied, observed, verified, contradicted, unknown

### "“Before I leave, test the whole pendant path and tell me in one sentence whether I can rely on it.”"
- **useful because:** The owner should not discover after leaving Wi-Fi that recording, relay reachability, audio generation, download, or playback is broken. A single end-to-end readiness check would exercise the actual wearable path and report the failing boundary, not merely show that a server is healthy.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** Deterministic diagnostics and a short fixed-format report; no expensive model needed. Realtime may speak the one-sentence result.
- **latency:** 10–20 seconds for a full check, with a fast 2-second cached status for repeated queries.
- **cost:** Negligible model cost; one short synthetic audio artifact and bounded diagnostic traffic per explicit check.
- **security:** Use a synthetic phrase, never owner speech or private content. Do not retain the test audio beyond delivery confirmation. Clearly distinguish USB bench connectivity from the unavailable LTE product path, and never report readiness if only the Mac bridge was tested.
- **missing:** A production end-to-end probe that exercises capture, uplink, relay processing, downlink, download, playback, and ACKs; A signed readiness result with freshness and tested transport; A pendant-safe test mode that cannot accidentally trigger a real action; A dashboard history of failures without retaining audio content

### "“When automation gets stuck, give me a clean handoff packet for a human: what I wanted, what already happened, the exact next safe step, and links—without exposing secrets.”"
- **useful because:** Some tasks cannot be completed by automation because of CAPTCHA, an unfamiliar approval screen, missing permission, or an ambiguous choice. Today the owner receives an error or a vague failure. A bounded handoff would preserve momentum and prevent a human helper from repeating dangerous or already-completed steps.
- **path:** relay-realtime → mac-planner → browser-extension → pendant → dashboard
- **model tier:** Cheap model drafts the concise handoff from receipts and redacted evidence; deterministic code enforces secret stripping and step status. Realtime speaks only that a handoff is ready and where to find it.
- **latency:** Under 5 seconds after a blocked step; the packet can continue assembling asynchronously.
- **cost:** One small cheap-model call per handoff; storage is a bounded local note or dashboard draft.
- **security:** Never include passwords, tokens, OTPs, private form values, or raw screenshots by default. Mark every step as completed, not attempted, blocked, or uncertain. Do not send the packet externally without explicit confirmation; use expiring links and revoke the packet when the task is closed.
- **missing:** A typed handoff artifact joining intent, receipts, evidence, blockers, and next step; A secret-safe renderer that handles whole sentences correctly, not only key:value strings; A durable review/approve/export flow for local notes or a chosen recipient; A way for the receiving human's outcome to return and close the original task


## What it asked for

_Nothing._
