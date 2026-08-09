# Harness derivation — faculty-judgement — round 245

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Learn when your interruptions and suggestions are actually useful, and quietly get better without taking more authority.”"
- **useful because:** Today every body can generate an interruption, but none records whether I accepted it, dismissed it, corrected it, or never heard it. A trust calibration layer would make the pendant less noisy and more accurate over weeks while preserving the owner’s hard boundaries: it may change ranking and wording, never permission to send, buy, delete, or speak private content.
- **path:** pendant → relay → mac → browser
- **model tier:** Cheap background model for weekly pattern summaries; deterministic counters for every event; realtime model only when converting a spoken correction into a labeled feedback event.
- **latency:** No added latency to the initial answer. Record feedback locally in under 50 ms; update calibration asynchronously within 1 minute; weekly summary under 30 seconds.
- **cost:** Near-zero for counters and rule updates; roughly $0.01–$0.05 per weekly summary depending on event volume. The expensive model is not called per interruption.
- **security:** Store outcome labels and source IDs, not raw mail/page text. Calibration is advisory and bounded by the owner policy; it cannot lower a confirmation requirement or promote a sensitive item to spoken delivery. The owner can inspect and reset each source’s score.
- **missing:** A durable cross-surface event correlation key joining relay job, Mac action, browser command, pendant artifact, and owner feedback; A production writer for attention decisions and a read/write calibration store; A physical or spoken feedback vocabulary (useful / not useful / wrong / already handled) and a dashboard reset view

### "“When you say something is done, check the real world afterward and tell me only if it did not stick.”"
- **useful because:** A completed Mac receipt currently proves that a command was accepted, not that the intended state exists. This capability would let the owner ask for a postcondition (“make sure the reminder exists”, “make sure the browser form saved”, “make sure the brief played”) and receive a truthful pass, mismatch, or unverifiable result. It prevents silent failures without turning every action into an expensive interactive workflow.
- **path:** relay → mac → browser → pendant
- **model tier:** Deterministic postcondition checks first; a cheap background model maps the owner’s plain-language goal to typed checks; realtime is used only when the owner asks for an immediate explanation.
- **latency:** For reversible local actions, verify within 2 seconds after completion. Browser checks may take up to 10 seconds. If a source is offline, queue a bounded verification and do not claim success.
- **cost:** Usually no model cost after the initial typed plan; $0.001–$0.01 for ambiguous goal-to-check mapping. Browser and Mac latency dominate, not tokens.
- **security:** Verification must be read-only and least-privilege: never resubmit a form or resend mail as a ‘check’. Sensitive fields are represented by hashes or presence/absence. Any repair is a separate policy decision and requires the existing confirmation rules.
- **missing:** A typed postcondition language for files, reminders, browser state, audio delivery, and calendar/mail readability; A durable link from the original action to its verification plan and later evidence; Read routes for reminders/notes and a reliable EventKit authorization probe; current empty calendar results can mean denial; A scheduler that retries verification after offline surfaces return without creating duplicate actions

### "“Choose the least disruptive way to reach me based on whether the pendant can actually deliver it, and never pretend I heard something I did not.”"
- **useful because:** A briefing can be generated successfully yet never downloaded or played; a Mac can be awake while the pendant is unavailable. This delivery-aware surface chooses spoken audio, queued inbox, Mac text, or deferred delivery from live reachability and explicit owner policy, then reports ‘delivered’, ‘queued’, or ‘not heard’ instead of conflating generation with receipt. It is the difference between an assistant that made content and one that actually got the owner’s attention.
- **path:** relay → pendant → mac → browser
- **model tier:** Deterministic routing and deduplication; cheap background model only compresses a backlog when several items must be coalesced; realtime model is reserved for a live spoken request.
- **latency:** Route a new item in under 200 ms from known state. Reconcile delivery ACKs within 5 seconds of reconnect. Never wait on a model before recording the delivery state.
- **cost:** Negligible for routing and ACK reconciliation; $0.002–$0.02 only when coalescing multiple undelivered items into a spoken digest. LTE reconnect and audio generation dominate wall time.
- **security:** The relay stores opaque artifact IDs, hashes, urgency, expiry, and sensitivity—not raw private text unless the owner policy permits it. A secret or private item defaults to Mac-local display/queue, never opportunistic speaker output. Duplicate ACKs and replayed offline events must be idempotent.
- **missing:** A durable delivery-state record joining briefing item, audio artifact, pendant session, and owner-visible item ID; Production mounting of record_pendant_delivery_event and a replay-safe ACK ingestion path; A real durable attention arbiter; the granted attention_arbitrate schema is currently unresolved and cannot be treated as live; A single owner policy defining audio versus screen versus queue, including what ‘heard’ means for interrupted playback

### "“Give you temporary permission to handle one narrow class of work, then automatically take it back.”"
- **useful because:** The owner currently has only coarse, implicit authority: some actions are allowed, some require confirmation, and the model must infer the boundary every time. A time- and scope-limited authority lease would let them say, for example, “Until 5 PM, reschedule internal meetings under 30 minutes, but never send mail or spend money.” Every relay, Mac, browser, and pendant decision would carry the lease ID and fail closed after expiry or scope drift. This is more useful than repeated confirmations and safer than a permanent allowlist.
- **path:** pendant → relay → mac → browser
- **model tier:** Deterministic policy evaluation for every action; realtime model only parses the spoken grant and asks for missing bounds; no model call during execution.
- **latency:** Grant parsing under 2 seconds; action checks under 20 ms; revocation reaches connected surfaces within 1 second and is enforced locally on the pendant immediately.
- **cost:** Negligible per action after the lease is compiled; approximately $0.01–$0.05 when a spoken grant needs clarification and compilation.
- **security:** Leases must be least-privilege, explicit about targets, spend, audiences, expiry, and reversibility. They cannot authorize destructive actions, secret disclosure, or physical approval bypass. The pendant must hold a signed revocation epoch for link-loss safety. Every use needs an owner-readable receipt and automatic expiry.
- **missing:** A durable relay-side authority-lease store with revocation and expiry; A cross-surface lease identifier carried through relay jobs, Mac actions, browser commands, and pendant envelopes; A real implementation of autonomy_policy_evaluate rather than the currently unresolved schema; A spoken and dashboard flow for reviewing, narrowing, and revoking active leases

### "“Before anything leaves my Mac, show me exactly what crosses the boundary, who receives it, and the smallest safe version you could send instead.”"
- **useful because:** Current redaction is pattern-based and scattered: it can mask credentials but cannot answer the owner’s real question, ‘what information is this action about to disclose?’ A departure preview would compute a field-level diff for prompts, browser forms, mail drafts, TTS, and relay handoffs, offer a redacted/minimized alternative, and require confirmation only when the destination or data class is outside policy. This makes privacy legible at the moment it matters rather than after an incident.
- **path:** mac → browser → relay → pendant
- **model tier:** Deterministic extraction, sensitivity classification, and destination policy first; a cheap model summarizes the diff in plain language; realtime is used only if the owner asks a spoken follow-up.
- **latency:** Preview in under 500 ms for local text and under 3 seconds for a browser or relay payload. No external transmission occurs while previewing.
- **cost:** Usually zero model cost for structured fields; roughly $0.001–$0.01 for a concise explanation of an unstructured payload.
- **security:** The preview itself must not upload the unredacted candidate. Secret fields are shown as type and hash, not value. The minimized payload must be independently rechecked immediately before send because page state and policy may change. Owner-approved exceptions expire and are tied to one destination and action.
- **missing:** A typed outbound-payload interception point covering prompts, TTS, browser actions, and Mac automation; A destination/data-class policy store with owner-editable rules and provenance for each decision; A correct sentence-safe secret masker and field-level diff representation; A final pre-send hook that cannot be bypassed by a direct executor path

### "“Run a safe rehearsal of the things I rely on, and warn me before a broken permission, stale session, dead link, or expired credential surprises me.”"
- **useful because:** The owner should not discover during an urgent request that the browser bridge is offline, calendar reads are silently unauthorized, the pendant cannot deliver audio, or a Mac job has become orphaned. A rehearsal would execute only read-only probes and synthetic no-op transactions across the relay, Mac, browser, and pendant, then produce a short owner-facing readiness score with the exact first failing boundary and a repair recommendation. It tests the whole experience, not just whether each process is alive.
- **path:** relay → mac → browser → pendant
- **model tier:** Deterministic probes and synthetic receipts; a cheap background model turns failures into one short explanation. Realtime is unnecessary unless the owner asks for diagnosis.
- **latency:** A daily lightweight rehearsal under 10 seconds; a full on-demand rehearsal under 60 seconds. It must never block live conversation or mutate owner data.
- **cost:** Near-zero API cost; bounded Mac/browser probe time is the dominant cost. Optional synthetic audio costs only a small local artifact and should be deleted after ACK.
- **security:** No real mail, purchases, deletions, form submissions, or external messages. Synthetic identifiers must be unmistakable and never enter the owner’s real accounts. Probe results should expose capability state and timestamps, not secrets. Failures must be actionable without automatically broadening permissions.
- **missing:** A standard read-only probe contract for each surface, including a pendant loopback and audio checksum without spoken content; A durable readiness history with regression detection and owner-visible receipts; A truthful EventKit permission probe distinct from AppleScript automation permission; A job lease/requeue mechanism so the rehearsal itself cannot become a misleading orphaned success


## What it asked for

_Nothing._
