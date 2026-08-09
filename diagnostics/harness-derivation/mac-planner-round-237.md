# Harness derivation — mac-planner — round 237

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac host accessibility and browser state** — At 2026-08-08T23:08:48Z, AI Pendant Agent has Accessibility and Screen Recording trusted, synthesized input verified, secure input false; Claude is foreground. GET /observe reports 20 running apps and 3 durable browser sessions, while browser_tabs inspection is currently ambiguous between action:browser_inspect and POST /browser/inspect.
  - evidence: mac_readonly_inspect(operation=running_apps) resolved to GET /observe HTTP 200; mac_readonly_inspect(operation=browser_tabs) returned resolver ambiguity.

## Capabilities it proposed

### "“Is my Pendant system healthy right now? Run a full end-to-end check, and tell me exactly what failed.”"
- **useful because:** This is the single most useful near-term capability: the hardware is physically attached to the Mac today but not LTE-registered, so it can prove the real audio/serial/relay chain instead of guessing. One spoken request would run the synthetic fixture (never microphone content), inspect the Mac/bridge and relay pipeline, correlate counters and receipts, and speak a concise pass/fail diagnosis through the pendant. It turns hours of bench debugging into a repeatable owner-visible health check.
- **path:** pendant → mac-planner → relay-realtime → mac-terminal → dashboard
- **model tier:** Use a cheap background model to interpret bounded diagnostic counters and receipts; reserve realtime only for the owner's spoken request and the final short answer.
- **latency:** Start acknowledgement under 1 s; fixture and USB checks may take 30–90 s, with progress alerts and a final result.
- **cost:** Usually <$0.02 per run; dominated by one small diagnostic interpretation call, not audio generation.
- **security:** The fixture must be synthetic and explicitly never read microphone contents. USB commands are restricted to the accepted diagnostic procedure, with immutable logs and redacted serial output. Do not flash firmware or alter files without a separate explicit request.
- **missing:** A bounded Mac-terminal diagnostic procedure that arms audio_path_diagnostic_fixture over the currently connected serial device and returns structured counters (the accepted firmware skill exists, but no callable serial tool is present).; A relay correlation endpoint that joins fixture sequence numbers, pipeline events, and Mac job receipts into one health report.; A pendant alert/result presentation path for a long-running diagnostic.

### "“I’m leaving my Mac now. Keep this task alive, and finish it when the Mac or browser comes back—tell me on the pendant if you need me.”"
- **useful because:** Today a desktop plan is tied to the moment it is handed off. This capability makes the hive resilient: the relay freezes a versioned intent and evidence snapshot, the Mac planner executes only the remaining idempotent steps after wake, the browser facet reacquires its session, and the pendant receives either completion or a precise blocked question. The owner can walk away without losing a multi-step task or accidentally running it twice.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** A cheap background model validates and summarizes the checkpoint; realtime is used only for a live clarification on the pendant. Deterministic job state, hashes, and receipts do the actual orchestration.
- **latency:** Checkpoint acknowledgement under 2 s; resume within 10 s of Mac/browser heartbeat; completion or a blocked-state alert within 30 s of each retry.
- **cost:** <$0.01 per checkpoint/resume; dominated by occasional model summarization, with most retries deterministic.
- **security:** Persist only the minimum task intent, touched-resource manifest, and redacted evidence. Never persist page bodies or credentials. Resume must use an idempotency key and stop on changed files, changed browser identity, or an expired session; those states should alert rather than guess.
- **missing:** A first-class resumable task state machine with step hashes, lease/heartbeat expiry, and idempotent retry semantics across Mac and browser.; A browser-session reattachment result that says whether the original authenticated tab is still the same resource, rather than merely that Safari is online.; Pendant delivery of blocked/completed job events with a way to answer a clarification without reopening the whole task.

### "“Before I send this, check the browser selection, the attached Mac file, and today’s calendar context for contradictions or sensitive details; make a corrected draft and ask me on the pendant before sending.”"
- **useful because:** The dangerous failure is not typing the message; it is sending a plausible message with stale dates, the wrong attachment, or confidential material. This cross-node preflight gives the owner one dependable pause: the browser contributes the exact selected text and destination, the Mac contributes the named attachment and metadata, Calendar contributes current commitments, and the relay compares them, produces a redacted diff and corrected draft, then asks for a short spoken confirmation before any irreversible send.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Use a background model for extraction, contradiction detection, and sensitive-data classification; realtime only reads the short diff and captures the owner's confirmation. Sending remains a separate explicit Mac/browser action.
- **latency:** Selection and file inspection in 2–5 s; draft/diff in under 10 s; no send until the owner confirms on the pendant.
- **cost:** $0.02–$0.08 per preflight depending on attachment size; token cost is dominated by the selected text and extracted file/calendar fields, not whole documents.
- **security:** Default to selection-only browser capture and metadata/snippets for files; redact secrets, tokens, and unrelated calendar details before model submission. Keep the original attachment local. Confirmation must bind to a hash of the exact draft, recipient, and attachment list, and invalidate if any changes.
- **missing:** A typed cross-surface evidence bundle carrying browser selection, local-file hashes/metadata, and calendar facts with provenance.; A contradiction/sensitive-data checker that returns field-level findings rather than an opaque score.; A confirmation-bound send adapter for the browser or Mac that refuses if the draft or attachment hash changed.

### "“Why did that happen? Show me the exact chain from what I said on the Pendant to every browser, Mac, and relay action, and tell me where the result diverged from the plan.”"
- **useful because:** The owner currently gets outcomes and scattered job records, not an understandable causal history. A tamper-evident cross-node trace would connect the spoken request, model decision, browser command, Mac mutation, receipts, retries, and final state into one timeline. It would make failures diagnosable and let the owner identify an incorrect step without replaying the entire task.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use deterministic correlation, hashes, timestamps, and action receipts for the trace; a cheap background model summarizes the trace. Realtime only speaks the short explanation when requested.
- **latency:** Trace events recorded synchronously; a human-readable explanation in under 5 s for a normal task and under 20 s for a long-running job.
- **cost:** <$0.01 per task for event storage and summarization; storage retention is the dominant cost.
- **security:** Trace payloads must contain resource identifiers and redacted diffs, not passwords, full page bodies, or raw audio. The owner needs retention controls and deletion. Hash chains must cover event omission and clock skew, with explicit unknown gaps rather than invented continuity.
- **missing:** A single trace ID propagated from pendant request through relay planning, browser commands, Mac actions, and receipts.; Structured before/after resource diffs and failure reasons for browser and Mac actions.; An owner-facing causal timeline and retention/deletion controls.

### "“For this sensitive account change, show me the exact target, old value, and new value on the Pendant, then apply it in the authenticated browser only if the values still match.”"
- **useful because:** A browser session can be authenticated while the owner cannot reliably see which account, field, or value an automation is about to change. This capability uses the browser for session access, the Mac planner for deterministic field targeting, and the physically separate pendant as a second display and confirmation channel. It prevents stale-page edits, wrong-account changes, and silent substitutions without requiring the owner to hand over browser credentials.
- **path:** pendant → browser-extension → mac-planner → relay-realtime → dashboard
- **model tier:** Deterministic extraction and hash comparison should do the safety-critical work; use a small model only to explain labels. Realtime reads the exact diff and captures confirmation.
- **latency:** Render the proposed diff on the pendant within 5 s; apply only after confirmation; verify the resulting page within 10 s and report mismatch immediately.
- **cost:** <$0.02 per change; dominated by browser round trips, not model tokens.
- **security:** Never speak or persist passwords, recovery codes, or full account identifiers. Bind confirmation to origin, account fingerprint, field path, old-value hash, new-value hash, and an expiry. Abort if navigation, DOM identity, or values change. This is not appropriate for irreversible transfers without an additional owner policy.
- **missing:** A browser semantic field identity and post-write verification API with origin/account fingerprints.; A pendant-rendered structured diff and confirmation token bound cryptographically to that diff.; A relay policy classifying which account changes may use this flow and which must remain manual.

### "“Keep this project synchronized across the local folder, its browser workspace, and my Calendar; if two surfaces changed it differently, show me the conflict on the Pendant instead of choosing for me.”"
- **useful because:** The owner should not have to maintain the same project state in a folder, an authenticated web workspace, and Calendar by hand. A cross-node synchronizer would use file hashes, browser resource identity, and calendar event identity to propagate only declared fields, preserve each surface's provenance, and surface a compact conflict choice on the Pendant. It is more useful than blind automation because it refuses to silently overwrite a change made elsewhere.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Deterministic field-level merge and hashes handle synchronization; a cheap model can summarize conflicts. Realtime only presents the conflict and records the owner's selected resolution.
- **latency:** Detect changes within 30 s while all surfaces are online; propagate unambiguous changes within 10 s; conflict alert within 5 s of detection.
- **cost:** <$0.01 per sync cycle for ordinary metadata; storage and browser polling dominate, with model use only for ambiguous conflict wording.
- **security:** Use explicit per-project field allowlists; never mirror credentials or arbitrary page content. Keep an append-only change history and support rollback. A missing or expired browser session must be treated as unavailable, not as an empty source.
- **missing:** A durable project binding that maps a local directory, authenticated browser resource, and Calendar objects without relying on titles alone.; Field-level change feeds and compare-and-swap writes for browser and Calendar resources.; A conflict record format and pendant choice protocol that can apply one selected version atomically.


## What it asked for

_Nothing._
