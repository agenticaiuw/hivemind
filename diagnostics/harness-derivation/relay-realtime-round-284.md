# Harness derivation — relay-realtime — round 284

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Tell me what’s going on right now with my setup and what’s likely to break before I notice."
- **useful because:** The owner gets a quick, actionable health snapshot: relay status, job backlog, audio path constraints, and device connectivity hints. It’s a daily driver feature for a wearable system that spans several machines.
- **path:** relay → mac-bridge → pendant → dashboard
- **model tier:** realtime for the spoken summary, cheaper tier for collecting and ranking signals
- **latency:** Under a second for a short spoken summary; detailed diagnostics can be offered as a follow-up.
- **cost:** Low. Most signals are already collected; the cost is in aggregation and summarization.
- **security:** Health summaries can leak metadata (device names, job titles). Keep spoken output minimal and avoid sensitive identifiers.
- **missing:** A unified, queryable health endpoint for relay+mac+browser+pendant (today signals are scattered); A policy for what counts as degraded vs failed, with owner-tunable verbosity

### "While I’m speaking, if I’m being vague, ask me a quick clarifying question instead of guessing and doing the wrong thing."
- **useful because:** This prevents expensive misfires. On a wearable, a fast clarification beats a wrong action, especially when the Mac is unattended.
- **path:** relay → mac-bridge → browser
- **model tier:** realtime (clarification must be low-latency)
- **latency:** Prefer a single short question under a second; only one clarification before proceeding.
- **cost:** Very low. It replaces a costly action with a brief turn.
- **security:** Clarifications can surface sensitive context. Keep questions minimal and avoid requesting secrets unless necessary.
- **missing:** A lightweight ambiguity scoring rule wired into the relay turn (so it knows when to ask); A standard fallback phrasing library sized for the pendant speaker

### "If I’m in the middle of a task on the Mac, help me continue it from the pendant without touching the keyboard."
- **useful because:** This is the single most useful capability: a seamless handoff between desktop and wearable. The owner can step away and still progress work (review status, open the next item, leave a quick note) through voice.
- **path:** mac-bridge → browser → relay → pendant
- **model tier:** realtime for the dialog, cheaper tier for UI actions and planning
- **latency:** Short spoken updates under a second; UI actions can take a few seconds.
- **cost:** Moderate. Planning and UI control can be more expensive than simple actions, but it avoids context switching for the owner.
- **security:** Can touch sensitive apps and data. Use reversible actions by default; confirm before sending messages, deleting, buying, or destructive edits.
- **missing:** Reliable cross-surface context handoff (what was open, what was selected, what ‘next’ means); A standardized ‘continue’ intent that can map to Mac actions, browser actions, or a follow-up plan

### "“Handle this sensitive task end to end, but show me exactly what will be sent before anything leaves my devices.” I speak the request on the pendant; the relay gathers the relevant authenticated browser/Mac context, produces a redacted preview, and I can accept or revise it by voice before execution."
- **useful because:** Today the owner must either trust a large opaque planner action or manually shuttle private context between devices. This would make the hive useful for email, forms, messages, and uploads without leaking unrelated page text or committing an accidental interpretation.
- **path:** pendant → relay → browser → mac-planner → mac-vision
- **model tier:** Realtime relay for the short clarification and spoken preview; background gpt-5.6-luna for planning and a cheaper verifier for field-level redaction/diff.
- **latency:** Preview in 3–8 seconds for a single page/form; execution after a brief spoken accept/revise turn.
- **cost:** About $0.03–$0.15 per request, dominated by planner context and one verification pass; no recurring cost beyond existing Worker/browser traffic.
- **security:** Raw authenticated page content must remain on the Mac/browser wherever possible. The preview must identify destination, recipients, attachments, and changed fields; execution must not occur until an explicit spoken accept. Redaction errors could expose secrets, so fail closed for credentials, tokens, and unrelated page regions.
- **missing:** A field-level provenance/redaction service that can turn browser/Mac observations into a stable preview; A spoken accept/revise state machine spanning the relay and the existing pendant inbox/outbox; Structured dry-run receipts and an execute-after-accept link between plan and execution

### "“Watch my real work, not just a page: if a meeting, message, or document changes in a way that affects the task I told you about, interrupt me with the one decision I need to make.” The relay correlates authenticated browser changes, Mac state, and my standing task, then asks only when the change crosses my configured importance threshold."
- **useful because:** The owner currently has to remember to ask again after a task is handed off. A cross-surface watch would turn the pendant into an always-available executive filter: it notices a changed deadline, reply, build failure, or approval request even while the owner is away from the Mac.
- **path:** pendant → relay → browser → mac-planner → mac-vision
- **model tier:** Cheap scheduled/standing-watch checks and deterministic diffs first; gpt-5.6-luna only for relevance ranking and a one-sentence decision prompt; realtime only when speaking the alert.
- **latency:** Changes surfaced within 1–5 minutes of a check; spoken alert under 2 seconds once selected.
- **cost:** Roughly $0.01–$0.08 per check depending on page/document volume; relevance calls dominate, so deterministic hashing and local extraction should be the default.
- **security:** Authenticated content and task correlations are sensitive. Store hashes/excerpts and provenance rather than whole pages, scope each watch to an explicit task, expire findings, and never speak message contents aloud until the owner requests detail. The owner must be able to pause a watch from the pendant.
- **missing:** A unified watch adapter for Mac apps, browser sessions, and local files, rather than page-only watches; A durable scheduler/worker that runs while the relay is awake and retries offline-device delivery; Task-scoped change correlation and a pendant pause/ack control

### "“Teach me what I am seeing without sending the scene or my voice to the cloud.” I press the pendant while looking at an object or screen; the Mac camera/screen and the pendant audio are joined locally, the Mac returns a concise spoken explanation, and only the final question and answer are retained if I ask."
- **useful because:** This is the single most useful new behavior: the pendant becomes an immediate, private accessibility and troubleshooting companion while the owner is away from the desk. It can read a label, explain a tool, identify a cable, or diagnose a screen without uploading a continuous camera feed.
- **path:** pendant → mac-vision → mac-planner → relay
- **model tier:** Local Mac vision/audio preprocessing and gpt-4.1-mini computer-use/vision loop for ordinary frames; realtime relay for turn-taking and 24 kHz speech; escalate to gpt-5.6-luna only for difficult reasoning.
- **latency:** First spoken answer in 2–4 seconds after the press; subsequent “look closer” turns under 2 seconds.
- **cost:** $0.005–$0.05 per turn if frames are downsampled and processed locally; relay speech and occasional escalation dominate.
- **security:** Camera and screen capture must be visibly active only during a press-held session, with a hard local indicator and automatic frame discard. Never upload frames by default; faces, documents, and passwords need local masking. Retention is opt-in and should use existing capture provenance.
- **missing:** A Mac-local camera/screen capture bridge with press-scoped lifetime and local redaction; A bidirectional low-latency audio/vision session protocol between pendant, relay, and Mac; A mac-vision loop that can return image-grounded claims with coordinates/confidence, not just click actions; A pendant-side ‘repeat/closer’ control compatible with its one-button interaction

### "“Reconcile these systems and tell me what is inconsistent.” I name a project, person, or event on the pendant; the hive compares the authenticated browser, Mac apps, and local files, identifies contradictions with evidence, and offers one repair plan rather than silently choosing a source."
- **useful because:** Real work is full of stale calendar invites, conflicting documents, duplicate contacts, and status messages. No single browser or Mac action can establish cross-system truth; this would save the owner from manually checking every surface and prevent the assistant from acting on stale context.
- **path:** pendant → relay → browser → mac-planner → mac-vision
- **model tier:** Cheaper deterministic extraction and entity/time matching first; gpt-5.6-luna for contradiction classification and repair planning; realtime only for the concise spoken finding and follow-up question.
- **latency:** Initial comparison in 10–30 seconds for three sources; speak the first conflict as soon as found, then continue in background with a completion alert.
- **cost:** $0.05–$0.30 per reconciliation, dominated by multi-source extraction and planner context; cache stable document fingerprints to keep repeated checks cheap.
- **security:** Cross-source joins can reveal more than any individual app. Keep source excerpts local, attach provenance and timestamps to every claim, scope access to the named entity, and never overwrite a source without an explicit repair selection. A missing source must be reported as unknown, never treated as agreement.
- **missing:** A cross-surface entity and contradiction graph with timestamped evidence; Connectors that extract structured facts from Mac apps/local files as well as authenticated browser pages; A repair-plan format that lists every affected source and supports partial execution; A spoken/background continuation channel for reporting conflicts discovered after the initial answer


## What it asked for

_Nothing._
## Its own summary

Recorded four owner-facing capabilities: a pre-send redacted preview with voice revision, cross-surface change interruption, private press-scoped visual assistance, and cross-system contradiction reconciliation. The required changes are explicit in each record: provenance/redaction and dry-run state, unified Mac/browser watches with background delivery, a local camera/screen bridge plus bidirectional vision session, and an evidence-backed entity/contradiction graph with partial repair plans. A hardware encoder/haptic control was proposed but correctly rejected as already present in the backlog, so I did not rephrase it.

**Biggest unknown:** Whether the existing watch and job-completion routes already expose enough cross-surface provenance to implement the interruption and reconciliation behaviors, or whether only their page/job-specific slices exist.

