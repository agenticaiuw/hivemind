# Harness derivation — unified — round 272

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Before I leave, give me a one-sentence handoff of anything I started on the pendant that is waiting on my Mac, browser, or a link recovery—and tell me the one action that will unblock each item.”"
- **useful because:** The hive has physically different reach, but interruptions currently strand work across relay jobs, browser commands, Mac jobs, held alerts, and audio delivery. This is not another generic status page: it is a cross-surface owner handoff that groups one intent, identifies the blocking surface, and offers the smallest safe next step.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for grouping and summarization; deterministic for job/lease/receipt state; realtime only for the spoken one-sentence response
- **latency:** Precompute after every state change; spoken answer under 1.5 seconds and dashboard refresh under 1 second.
- **cost:** Low to moderate: deterministic joins dominate; background model only for concise wording of already-redacted state.
- **security:** Do not expose browser page contents or secrets in a pendant summary; use opaque job labels and explicit confirmation before any unblock action. Mark stale leases and uncertain completion as uncertain, never completed.
- **missing:** stable intent correlation across relay jobs, Mac jobs, browser commands, and pendant inbox items; blocking-state vocabulary and safe next-action contracts; owner-facing handoff endpoint and dashboard card; lease/receipt reconciliation that distinguishes never-started, in-flight, completed, and unknown

### "“When I say ‘use the account I’m looking at,’ prove which browser tab and session you mean before doing anything, and show me the target plus a short-lived physical-presence check on the pendant.”"
- **useful because:** Ambiguous browser identity is a dangerous gap: logged-in tabs can represent different accounts, and a spoken reference like ‘the account I’m looking at’ is not enough to bind an external action. This capability makes the browser’s unique reach usable without silently choosing the wrong identity, while leveraging the pendant as a human-presence boundary rather than trusting model interpretation.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic for tab/session binding and challenge expiry; realtime for clarification; no background model required
- **latency:** Target preview under 1 second, pendant challenge within 3 seconds, execution only after a fresh response; expire unresolved challenges after 60 seconds.
- **cost:** Very low: browser inspection plus signed challenge state; occasional realtime clarification.
- **security:** Never send page contents or credentials to the pendant; display origin/title/account label only. Bind approval to exact tab/session URL pattern, action digest, expiry, and one-time nonce. Deny if tab navigates or session changes. This is a proposal for a continuous target-binding layer, not a replacement for the existing per-transaction approval latch.
- **missing:** browser identity attestation (requested but not yet granted); tab/session fingerprint and navigation-change invalidation; short-lived presence lease bound to action digest; owner-visible target preview and refusal reasons

### "“Preview my routines for the next 30 days in the Mac’s timezone, including DST and missed-run behavior, and tell me exactly what the pendant, relay, and Mac will do if the Mac is asleep or I’m traveling.”"
- **useful because:** The system has an authoritative Mac timezone policy, but routine language such as ‘morning’ and ‘next Monday’ is easy to misread around DST, sleep, travel, and relay outages. A concrete dry-run lets the owner catch a routine that will fire at the wrong instant before it surprises them, without pretending the pendant has a timezone.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** deterministic scheduler simulation and timezone library; background model only to explain anomalies in plain language; realtime only for a spoken summary
- **latency:** Preview under 2 seconds for 30 days of routines; spoken anomaly summary under 1.5 seconds; applying a change requires explicit confirmation.
- **cost:** Very low: deterministic expansion of stored routines and lease/catch-up state; occasional short explanation generation.
- **security:** Treat America/New_York as the current Mac resolution zone, not the owner’s physical location. Display both local wall time and UTC instant, flag nonexistent/duplicated DST times, and never silently reinterpret a routine because the owner traveled. Do not transmit unrelated routine contents to the pendant.
- **missing:** dry-run routine expansion endpoint returning exact instants and DST annotations; explicit sleep/offline/catch-up semantics in the preview contract; relay/Mac execution trace for each simulated firing; dashboard timeline and pendant-readable anomaly summary

### "“Find the voice note where I mentioned the hardware test, quote the matching few seconds, and let me delete that note—including its audio—without touching my action history.”"
- **useful because:** Voice notes are deletable, but deletion is only useful if the owner can retrieve one by meaning rather than remembering an opaque note ID. This makes deliberate owner-created audio searchable while preserving the separate rule that action history is not erased with a note.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for transcription/embedding at note-ingest; deterministic filtering and deletion cascade; realtime only for spoken search and short quote selection
- **latency:** Search results under 3 seconds for the indexed library; playback starts under 1 second after selection; deletion acknowledgement under 2 seconds with off-machine replication marked pending.
- **cost:** Moderate background transcription/indexing cost proportional to owner-created notes; low per-query cost with a local index.
- **security:** Index only voice notes the owner deliberately created; keep embeddings and transcripts access-controlled; return minimal matching snippets, not unrelated room audio. Deletion must remove words, audio, embeddings, transcript copies, and relay replicas while retaining a non-content deletion receipt; require confirmation for destructive deletion.
- **missing:** search index tied to voice-note IDs and retention/deletion cascade; semantic search endpoint with bounded snippet evidence; audio quote-range metadata and playback route; replicated erase status for relay/off-machine copies

### "“Before you send, upload, or type anything outside this device, show me exactly what data will leave, who receives it, and let me redact fields while keeping the action otherwise unchanged.”"
- **useful because:** The existing approval concepts decide whether an action is allowed, but do not give the owner a data-level view of what a browser form, Mac command, or relay upload will disclose. The owner should be able to grant an action without granting unnecessary context, especially when the browser holds private accounts.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic payload extraction and redaction; background model only to label unfamiliar fields; realtime for a spoken summary
- **latency:** Preview under 2 seconds for normal forms/files; redaction update under 500 ms; no execution until the final payload digest is confirmed.
- **cost:** Low to moderate: deterministic inspection is cheap; labeling unknown fields is occasional background work.
- **security:** Never transmit the unredacted payload to the model merely to explain it. Keep secrets local to the Mac/browser, show hashes or masked values on the pendant, bind approval to the final redacted-payload digest, and refuse if the destination or payload changes.
- **missing:** structured outbound-payload interception for browser, Mac, and relay actions; field-level redaction transforms for forms, files, and API bodies; final payload digest included in the existing action/approval envelope; owner-facing privacy preview and audit receipt

### "“If my Mac is lost or replaced, restore this assistant on a new machine without restoring secrets or old audio, and show me exactly what came back.”"
- **useful because:** Today the owner’s useful state is distributed across the Mac workspace, relay records, browser sessions, pendant pairing, routines, and memory artifacts. A machine failure can strand that state or encourage an unsafe all-or-nothing backup. A selective, encrypted recovery capsule would preserve continuity while making secrets, audio, and extracted memory opt-in rather than silently restored.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic manifest, encryption, and restore verification; background model only to explain conflicts; realtime not needed
- **latency:** Create a capsule in under 1 minute; verify a new machine in under 10 seconds; restore selected state in under 2 minutes, excluding large audio.
- **cost:** Low ongoing storage cost for encrypted manifests and compact configuration; occasional relay storage and transfer cost during backup/restore.
- **security:** Use device-bound encryption and explicit per-category inclusion: routines, preferences, action audit, active jobs, browser bindings, extracted facts, and voice audio must be separate choices. Never export browser credentials or raw relay bearer tokens. Require physical pendant confirmation for pairing a replacement machine and show a restore receipt.
- **missing:** versioned selective-recovery manifest; encrypted relay escrow with key separation from the Mac; new-machine pairing and pendant confirmation flow; conflict resolution for routines, ledgers, and memory after restore; restore verification report

### "“How much autonomy have you used today, what did it change, and stop before you exceed the limits I set for money, messages, external sites, or destructive actions.”"
- **useful because:** The owner currently gets per-action safety decisions but no durable, understandable budget across the whole hive. A daily delegation budget would make autonomy predictable: the system can spend a bounded number of external writes or a bounded dollar amount, explain consumption, and halt before a surprising run-away sequence.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic counters, risk classification, and budget enforcement; background model only for daily summaries; realtime for threshold warnings
- **latency:** Enforcement must be inline with zero extra model round trips; dashboard and spoken usage summaries under 1 second.
- **cost:** Negligible compute/storage cost; small bounded ledger growth with daily rollups.
- **security:** Counters must be tamper-evident and keyed to action receipts, not model claims. Budgets should fail closed on unknown risk or missing receipt, distinguish previews from committed effects, and never treat an undo as erasing the original spend. Owner changes to budgets require explicit confirmation and an audit record.
- **missing:** owner-configurable budget schema by riskTier/action family/destination; atomic reservation and settlement against relay, Mac, and browser actions; daily rollup and explanation view; fail-closed behavior for unknown or unreceipted effects


## What it asked for

_Nothing._
## Its own summary

Round 272 produced four materially different owner-facing proposals: accountable routine simulation across Mac/relay/pendant, semantic search and precise deletion of owner-created voice notes, exact browser target binding with short-lived pendant presence, and a cross-surface interrupted-work handoff. The fact-provenance proposal collided with an existing backlog item, and crash-recovery activation also collided; I did not count or rephrase those. Current discovery shows Safari and home-macbook-bridge online, while the nRF9160 pendant is offline, so nothing here assumes live LTE. Still needed (without re-requesting queued items): browser_identity_attestation, the owner’s mandatory-confirmation policy for external actions, and an authoritative inventory/implementation of the unobserved workbench handoff/context routes. The strongest immediate owner value is the routine dry-run plus voice-note search, because both can be made useful on today’s Mac/relay surfaces without pretending the pendant is connected.

**Biggest unknown:** Whether the owner wants semantic indexing of deliberately created voice notes at all, and what exact confirmation policy should govern destructive deletion and external browser actions; those are policy choices, not facts recoverable from the live system.

