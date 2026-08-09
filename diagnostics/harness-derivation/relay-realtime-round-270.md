# Harness derivation — relay-realtime — round 270

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If a task fails, tell me what went wrong and offer the shortest safe next step."
- **useful because:** Failure handling is where assistants feel real. The owner hears a brief diagnosis and can choose to retry, open the relevant app, or send a note—without digging through logs.
- **path:** relay → mac-bridge → mac-vision → pendant
- **model tier:** Realtime for triage phrasing; cheaper tier for log/receipt analysis.
- **latency:** Under a second to acknowledge, then a brief spoken summary once the failure is detected.
- **cost:** Dominated by retrieving receipts/logs and summarizing them; minimal realtime cost.
- **security:** Receipts may contain sensitive text. Use redaction and default to high-level explanations; ask before reading detailed content aloud.
- **missing:** A reliable way to detect failure states and map them to user-facing categories; Redaction rules for spoken summaries; An intent path to trigger the shortest safe next action

### "“Is this invoice actually paid?” Reconcile the evidence across my email/files on the Mac, my authenticated browser portal, and my iPhone, then tell me the answer, confidence, and exactly which sources disagree."
- **useful because:** Today each surface can be queried separately, but nobody can establish a trustworthy answer when systems disagree. This turns the pendant into a cross-system fact checker rather than a launcher.
- **path:** pendant → relay → mac-planner → browser → iOS → dashboard
- **model tier:** Realtime relay handles the short spoken question; faculty-perception extracts dated evidence from Mac, browser, and iPhone in parallel; a cheaper background judge model normalizes entities, detects contradictions, and computes confidence; relay speaks only the conclusion and offers the source trail.
- **latency:** First acknowledgement under 500 ms; parallel evidence within 10 s; if a portal is slow, speak a provisional result and push a corrected result when the watch completes.
- **cost:** Roughly $0.03–$0.15 per investigation, dominated by browser/iPhone screenshots and the judge pass; no expensive realtime generation beyond the final sentence.
- **security:** Authenticated page contents, mail, files, and phone data leave their surfaces to the relay/judge. Keep raw evidence encrypted and short-lived, redact unrelated message bodies, show source names and timestamps, and require confirmation before any suggested payment or correction.
- **missing:** A cross-surface evidence envelope with entity IDs, timestamps, provenance, and contradiction links; Parallel Mac/browser/iOS evidence collection under one investigation job; A confidence-and-disagreement judge and a spoken/source-trail result format; Explicit retention and redaction policy for investigation evidence

### "“Save exactly where I am and get me back here tomorrow.” Later, when I press the pendant, restore the relevant Mac app and browser tabs, reopen the right document or message, and briefly remind me what I was trying to do."
- **useful because:** People lose work not because files vanish, but because the surrounding state vanishes. A durable, cross-device return point would let the owner leave the Mac without reconstructing a task from memory.
- **path:** pendant → relay → mac-planner → browser → iOS → dashboard
- **model tier:** Realtime relay records the intent and gives a one-sentence acknowledgement. A background state-capture model turns active Mac/browser/iPhone state into a minimal semantic resume packet; on return, mac-planner executes restoration and relay summarizes differences before speaking.
- **latency:** Capture acknowledgement under 1 s. Save within 5 s. Restoration may take up to 20 s, with a short progress alert and a final spoken summary.
- **cost:** About $0.01–$0.06 per save/restore, mostly screenshot summarization and one planning pass; storage is small JSON plus references, not copied documents.
- **security:** Resume packets may contain document titles, URLs, selected text, and private app state. Encrypt them, allow per-packet expiry/deletion, never store passwords or page bodies, and require confirmation before reopening a sensitive app or sending anything.
- **missing:** A first-class resume-packet schema with semantic intent, app/window identity, tab references, selection anchors, and expiry; Mac and browser snapshot adapters plus iPhone Mirroring state capture; A restoration engine that tolerates changed tabs/documents and reports what could not be restored; A pendant gesture/voice command and durable packet listing

### "“Why didn’t that work?” After any failed or partial request, reconstruct a causal timeline across my pendant audio, relay job, Mac actions, browser commands, and iPhone actions, identify the first failure and what state each surface was left in, then offer the safest recovery."
- **useful because:** Today a failure is reported as a vague job error and the owner has to interrogate every node manually. A causal timeline would make the hive accountable and recoverable, especially when one device succeeded while another timed out.
- **path:** pendant → relay → mac-planner → browser → iOS → dashboard
- **model tier:** A cheap background correlator joins append-only operation receipts and device telemetry by operation ID; faculty-perception classifies the first fault versus downstream symptoms; realtime relay gives a short explanation, while the dashboard exposes the detailed timeline.
- **latency:** Speak an immediate “I’m tracing it” acknowledgement under 500 ms; initial diagnosis in 3 s; deeper correlation and recovery plan within 15 s.
- **cost:** About $0.005–$0.04 per diagnosis, dominated by log retrieval and an inexpensive correlation model; no browser or screenshot work unless the evidence requires it.
- **security:** Logs can contain URLs, filenames, transcripts, and device identifiers. Redact payloads by default, retain hashes and metadata longer than raw content, bind records to an owner-visible operation ID, and never silently retry a consequential action.
- **missing:** A shared operation ID propagated from pendant capture through relay, planner, browser, and iOS; Append-only receipts with start/end, retries, partial effects, and device health snapshots; A causal correlator that distinguishes first failure from timeout cascades; A recovery planner that can verify current state before proposing or executing repair


## What it asked for

_Nothing._
