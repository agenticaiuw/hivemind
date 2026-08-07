# Harness derivation — relay-realtime — round 139

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Check this private page and draft the form for me, but stop before submitting."
- **useful because:** It saves time on tedious web workflows while keeping the owner in control. Drafting plus a clear preview reduces errors and prevents accidental changes.
- **path:** relay → browser → mac-bridge → relay
- **model tier:** Planner/extractor on a cheaper tier; realtime only narrates and confirms.
- **latency:** Initial response under a second; extraction and drafting can take longer; preview must be crisp and sourced.
- **cost:** Moderate: browser session work dominates. Drafting and summarization cost depends on page complexity.
- **security:** Must keep authenticated data within the owner’s environment; never auto-submit; require explicit approval before irreversible changes.
- **missing:** A hardened authenticated browser command queue with typed results; Semantic diffing to detect meaningful changes; Provenance capture for extracted fields and drafts

### "Give me a 30-second audio brief of what I missed, with links I can review later."
- **useful because:** A wearable is perfect for quick catch-up. A short spoken summary plus a Mac review queue lets the owner stay informed without stopping what they’re doing.
- **path:** relay → mac-bridge → browser
- **model tier:** Brief generation on a cheaper summarizer; realtime only plays back and handles follow-ups.
- **latency:** Brief playback must start quickly; background gathering can happen ahead of time when available.
- **cost:** Moderate: gathering sources (calendar/mail/files/tabs) dominates; summarization is relatively cheap.
- **security:** Must separate public and private data; avoid reading sensitive tabs unless explicitly included; keep audio retention limited and deletable.
- **missing:** Scheduling or background run support; Audio queue creation/playback controls on relay and pendant; Per-source permission and scope selection

### "While I am wearing the pendant in a meeting, say “capture this meeting privately” and have the system record only the meeting audio, identify speakers locally, produce a concise action-item summary, and draft (but not send) follow-ups in the right browser or Mac app when the meeting ends."
- **useful because:** The owner gets reliable meeting memory without manually handling a recorder, transcript, or notes. The pendant is the always-present trigger and microphone, while the Mac/browser supply calendar and drafting surfaces; no single node can do the complete workflow.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use realtime only to recognize the short command and acknowledge it; use a cheaper background transcription/summarization model after capture, with local speaker segmentation where possible.
- **latency:** Immediate acknowledgement under 500 ms; rolling capture may be streamed or chunked; summary and drafts can arrive within 5 minutes after the owner ends capture.
- **cost:** Roughly $0.05–$0.30 per hour of meeting depending on transcription volume; storage and audio upload dominate, not the realtime turn.
- **security:** Audio and transcript are highly sensitive. Default to encrypted local buffering, explicit physical start/stop feedback, automatic deletion after the summary is accepted, and never send drafts without a separate explicit command. Calendar invitees and bystanders must not be exposed unnecessarily.
- **missing:** pendant audio capture/start-stop protocol and local encrypted buffering; background transcription and speaker segmentation worker; calendar-aware meeting association; draft creation APIs across Mac and authenticated browser sessions; retention/deletion controls and visible capture state

### "From the pendant, say “check whether the invoice matches the contract” and have the system find the relevant contract in my Mac files, find the invoice in my authenticated browser session, compare amounts, dates, line items, and renewal terms, then tell me only the discrepancies and where each came from."
- **useful because:** This turns a vague spoken request into a high-value verification that currently requires manually navigating two private surfaces. It uses the pendant for intent and response, the Mac for local files, and the browser for authenticated records; the answer can be useful even when the owner is away from the desk.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension → dashboard
- **model tier:** Use realtime only for intent extraction and a short spoken result. Use a background reasoning model for document extraction and comparison, with deterministic arithmetic and cited source spans.
- **latency:** Acknowledge immediately; return a preliminary result in 30 seconds and a complete comparison within 2 minutes, depending on document size and browser availability.
- **cost:** Approximately $0.03–$0.20 per comparison; OCR/document parsing and browser extraction dominate token cost.
- **security:** Contracts and invoices are private and may contain financial data. Keep source documents on-device where possible, send only extracted fields to the relay, preserve citations, and never email or modify records. Browser session cookies must remain in the browser harness.
- **missing:** cross-surface document identity matching; Mac file search/read tool exposed to the relay workflow; typed extraction of tables and terms with source spans; browser-to-Mac evidence bundle and comparison worker; large-result delivery that can be summarized over speech

### "When my service is failing, say “triage the outage” to the pendant and have it collect the relevant Mac logs and git state, inspect the authenticated deployment/dashboard tabs, correlate the timestamps, and tell me the most likely cause plus the safest next command—without changing production."
- **useful because:** The owner can start incident triage while away from the keyboard and get one evidence-backed answer instead of separately searching terminal logs and private dashboards. The wearable supplies immediate intent, the Mac supplies local runtime evidence, and the browser supplies deployment context.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension → mac-vision → dashboard
- **model tier:** Realtime handles the short command and progress acknowledgements only. A cheaper background model performs log normalization, timestamp correlation, and hypothesis ranking; deterministic parsers should extract commits, errors, and deploy IDs.
- **latency:** Acknowledge in under 500 ms; first hypothesis within 20 seconds; full cited triage within 90 seconds. Any production mutation remains a separate spoken request.
- **cost:** About $0.02–$0.15 per incident, dominated by log volume and dashboard extraction; redact and truncate before model submission.
- **security:** Logs can contain tokens, customer data, and infrastructure details. Redact secrets locally, scope collection to an incident window, retain an evidence hash and citations, and default to read-only. Never run a suggested rollback implicitly.
- **missing:** incident-window selection and local secret redaction; Mac log/git collection route with typed evidence; browser dashboard inspection tied to the same incident/deploy ID; timestamp-normalized evidence joiner; voice-sized hypothesis/result formatter


## Changes it proposed to its own stack

### `relay` — Implement relay_route_intent and relay_job_status as real endpoints backed by the relay’s job/history store, with a minimal envelope for intent, target, and correlation id. Add spoken status output passthrough to avoid wording drift.
- **owner gets:** The pendant can hand tasks off reliably and later report exactly what happened, without guessing or rephrasing. That’s trust, in the owner’s ear.
- effort: Medium: define storage schema, wire to existing job records, add correlation and indexing.  ·  risk: Misrouting could start the wrong task; mitigate with target validation and conservative defaults. Status mismatch could mislead; mitigate by requiring receipts and never upgrading status text.
- cost: Low per call; storage growth proportional to jobs and receipts.  ·  latency: Fast intent routing; status reads should be instant.
- security: Ensure job records do not leak sensitive content; store references and hashes where possible.
- depends on: relay has access to job store (D1) and receipt linkage from downstream

### `browser-harness` — Build a durable authenticated browser job runner that can execute typed actions (navigate, read, extract, fill) with tab/session affinity, idempotency keys, and typed results, plus a semantic diff layer for page-change detection.
- **owner gets:** This makes ‘handle it and show me’ actually work across sessions, so the owner isn’t redoing work every time the browser reconnects.
- effort: High: requires queueing, persistence, and careful session binding.  ·  risk: Authenticated automation risks unintended actions; keep irreversible steps as drafts requiring approval and require provenance for all extracted data.
- cost: Moderate; dominated by browser automation time and storage for results.  ·  latency: Slightly higher, but predictable and resumable.
- security: Keep credentials confined to the local browser/session; never ship secrets to relay logs.
- depends on: session binding and receipt capture in browser bridge; reliable command queue semantics

### `interaction` — Add a ‘spoken preview’ contract: before any irreversible action, generate a concise, evidence-backed spoken summary with before/after fields and a confirmation token the owner can reference (“approve with token 7Y2”).
- **owner gets:** Prevents accidental changes while still letting the system do real prep work. It’s confidence you can hear.
- effort: Medium: requires standardizing receipts and generating previews from typed results.  ·  risk: If previews are wrong, the owner could approve a bad change; mitigate by requiring provenance snippets and hashes.
- cost: Low to moderate; preview generation is cheap relative to automation.  ·  latency: Minimal; preview generation happens after drafting.
- security: Previews must avoid reading aloud sensitive data unless explicitly allowed; redact by default.
- depends on: typed results and provenance from browser/mac actions; receipt chain available to relay


## What it asked for

_Nothing._
