# Harness derivation — faculty-judgement — round 275

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Tell me whether my Mac and pendant are running out of space, what is consuming it, and give me a safe cleanup preview before you delete anything.”"
- **useful because:** The owner has repeatedly asked for free disk space and Downloads counts and received failures. This would answer the practical question, correlate Mac Downloads, relay job/audio artifacts, and pendant diagnostic/storage pressure, then produce one reviewable cleanup plan rather than silently deleting files. It is cross-body: the Mac sees files, the relay sees queued work, and the pendant reports its own failure-path storage.
- **path:** mac → relay → pendant
- **model tier:** background for inventory and ranking; realtime only for the short spoken answer
- **latency:** Inventory in 10–30 seconds; preview can arrive later as a durable job, with a one-sentence immediate acknowledgement.
- **cost:** Low: one background model call for ranking and wording; dominant cost is local disk enumeration and relay/device reads, not inference.
- **security:** Never upload filenames or file contents by default; send only sizes, age, type, and opaque artifact IDs. Deletion is always preview-first and requires owner confirmation. Audio on the pendant remains governed by its failure-path-only SD rule.
- **missing:** A real Mac storage/Downloads inventory route or a constrained df/find action with structured size output; A relay endpoint exposing artifact/job storage usage; A pendant storage-health telemetry event and authenticated read route; A typed cleanup-plan route that can be previewed, approved, and undone

### "“If something I asked for failed because a surface was offline or lacked permission, remember the exact request, tell me what blocked it, and retry it when the right surface returns—without doing it twice.”"
- **useful because:** The owner's history is full of repeated failed probes and repeated requests. Today a failed Mac/browser/pendant handoff can become a dead end or be manually retried with duplicate side effects. A durable, owner-visible retry intent would preserve the request and its evidence, distinguish unavailable from denied from empty data, and re-run only after a fresh preflight says the needed surface is usable.
- **path:** relay → mac → browser → pendant
- **model tier:** background for classification and retry scheduling; realtime only to state the blocker and receipt
- **latency:** Immediate blocker in under 2 seconds; retry is event-driven on reconnect or permission change, not a polling conversation.
- **cost:** Very low inference cost: deterministic state machine plus occasional small classification call. Storage and connectivity watchers dominate.
- **security:** Retry records contain intent metadata, not secrets or page contents. Mutating/destructive intents remain staged and require the same owner confirmation after revalidation; idempotency keys and expiry prevent duplicate execution. Every retry must expose its prior failure evidence.
- **missing:** A durable cross-surface intent/retry record joining relay job ID, Mac job ID, browser command ID, and pendant sequence; A real job lease/requeue mechanism for orphaned relay jobs; Connectivity/permission change events from Mac, browser, and pendant; A retry executor that invokes revalidate_pending_plan and autonomy_policy_evaluate before any mutation

### "“Did I actually hear yesterday’s brief, and if not, give me only the missing items once—then mark which ones were downloaded, started, finished, or interrupted.”"
- **useful because:** A generated/accepted audio job is not proof the owner heard it. With the pendant offline at times and duplicate scheduled briefings already present, the owner needs a truthful ‘heard’ boundary: no replay of completed items, a compact recovery of interrupted ones, and an explanation tied to the exact artifact and playback evidence.
- **path:** relay → pendant → mac
- **model tier:** background for deduplication and compact recovery selection; realtime only when the owner asks or presses play
- **latency:** State query under 2 seconds from receipts and delivery events; recovery brief generated asynchronously if many items are missing.
- **cost:** Low: deterministic event reconciliation, with a small background summarization call only for interrupted/missing content.
- **security:** Use opaque artifact IDs and item hashes in the relay; do not persist or speak source text merely to report delivery state. A completed ACK must be authenticated to the pendant session and deduplicated by event ID. Never infer ‘heard’ from download alone.
- **missing:** A production delivery-event ingestion route that persists authenticated pendant ACKs and handles offline replay; A durable mapping from briefing item to audio artifact and source evidence; A single scheduler/coalescer that prevents duplicate morning briefs from creating duplicate items; A read API returning per-item delivery state and a replay plan

### "“Give me a complete, encrypted, portable copy of everything this assistant knows about me and every action it took, with source links, then let me choose exactly what to restore on a new Mac or relay.”"
- **useful because:** The owner should not be trapped by a relay database, a Mac workspace, or an opaque memory projection. Today facts, context-graph records, evidence tombstones, job receipts, browser provenance, audio metadata, and pendant events live in separate stores with no trustworthy export or import contract. A verified portability bundle would make the assistant auditable, replaceable, and recoverable after a machine loss without restoring revoked or expired material.
- **path:** relay → mac → browser → pendant
- **model tier:** background deterministic export/import validation; no expensive realtime model is needed except to explain conflicts in plain language.
- **latency:** Export under a minute for normal stores and asynchronous for large evidence/audio indexes; import is staged, validated, and only committed after explicit confirmation.
- **cost:** Low API cost; hashing, encryption, schema validation, and local I/O dominate. No raw content should be sent to a model.
- **security:** Encrypt to an owner-held key, require an explicit local confirmation to export or import, exclude secrets and expired/revoked bodies by default, and preserve tombstones so deleted evidence cannot be resurrected. The pendant receives only a bounded encrypted manifest, never the archive's source text or credentials.
- **missing:** A versioned cross-surface export schema covering facts, graph, evidence, receipts, browser provenance, fleet memory, and pendant delivery events; A durable join between relay jobs, Mac jobs, browser commands, audio artifacts, and device sequences; Import validation that enforces revocations, TTLs, sensitivity policy, and idempotent conflict handling; Owner-key management and a local-only export/import UI

### "“Before you ever act autonomously, run in shadow mode for a week: predict what you would do from my mail, calendar, browser, and pendant context, but do nothing, then show me where your predictions disagreed with what I actually chose.”"
- **useful because:** The owner cannot currently calibrate trust safely: policy checks and receipts describe individual actions, but there is no period in which the assistant proves its judgement without side effects. A shadow mode would expose false urgency, missed commitments, bad surface routing, and privacy mistakes before autonomy is enabled, using the owner's real choices as evaluation data.
- **path:** relay → mac → browser → pendant
- **model tier:** Cheap background model for candidate ranking and explanation; deterministic policy evaluation and source reads should handle most cycles.
- **latency:** No interruption during shadow capture; a daily or weekly report in under a minute, with on-demand drill-down.
- **cost:** Moderate background inference over sampled events; cap it by scoring only decision boundaries and storing hashes/labels rather than replaying full content.
- **security:** Shadow mode must be read-only and must not submit, message, delete, or speak sensitive content. Store only proposed action class, policy matches, source references, and the owner's eventual choice; raw content remains at its source and can be revoked.
- **missing:** A durable decision-observation log linking candidate judgement, evidence snapshot, policy version, owner choice, and outcome; A read-only event fan-in from Mac, browser, relay routines, and pendant delivery/interrupt events; A replay evaluator that can compare the same state against a later state without mutating it; Owner-facing calibration metrics and an explicit promotion gate from shadow to prepare/execute

### "“Run a safe red-team drill against my assistant: use synthetic secrets and fake urgent messages to show whether anything could be spoken, sent, deleted, or approved without the right confirmation, then give me a pass/fail report.”"
- **useful because:** The owner has no way today to verify the safety boundary end to end. Individual redaction, policy, approval, browser, relay, and pendant components may each look correct while a composition leaks a secret or performs an action. A synthetic, non-destructive drill would make those failures observable before real personal data or external side effects are at risk.
- **path:** relay → mac → browser → pendant
- **model tier:** Deterministic test harness and background evaluator; realtime is unnecessary except for a short spoken result. Synthetic fixtures avoid sending owner data to a model.
- **latency:** A standard suite in 1–5 minutes, with immediate stop on the first unexpected external mutation or disclosure.
- **cost:** Low model cost; most work is fixture setup, isolated browser sessions, receipt inspection, and teardown.
- **security:** Use disposable accounts/files and a network-deny sandbox where possible. The drill must never use real mail recipients, purchases, credentials, or owner audio. Any unexpected mutation fails closed and requires cleanup review. Results should retain hashes and receipts, not synthetic secrets in spoken output.
- **missing:** An isolated fixture/sandbox runner for Mac, browser, relay, and pendant paths; A synthetic-data generator and canary detector that catches secrets in prompts, TTS payloads, logs, and outbound requests; A cross-surface assertion engine joining policy decisions to actual receipts and device delivery events; A durable test report with explicit pass/fail criteria and no destructive teardown assumptions


## What it asked for

_Nothing._
## Its own summary

This round produced three owner-facing capabilities: a cross-body storage/Downloads pressure and safe-cleanup preview; durable failure-aware retry of requests without duplicate side effects; and per-brief-item proof of downloaded/started/finished playback with selective recovery. The first and third address the owner's repeated failed disk probes and the system's current inability to distinguish generated audio from audio actually heard. I also confirmed that the newly granted semantic tools (cross_surface_preflight, pendant_diagnostics_and_bug_draft, audio_brief_item_action, record_pendant_delivery_event, attention_arbitrate) are schemas but unresolved against the live inventory, so they cannot yet be honestly invoked.

**Biggest unknown:** Whether the relay has any durable backing in this deployment for new retry records, delivery ACKs, and storage telemetry. The next thing needed is a live route/store inventory for those three seams, plus a real structured Mac disk-inventory action. The pendant remains offline and LTE-unregistered; USB is bench-only, so none of these should be promised as a shipping pendant behavior until the LTE path is available.

