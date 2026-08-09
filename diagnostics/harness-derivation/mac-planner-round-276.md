# Harness derivation — mac-planner — round 276

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “remember why I chose this,” save the voice memo together with the Mac app/document or browser page I was looking at, and later answer “why did I do that?” with the original evidence."
- **useful because:** A bookmark records when, but not what the decision was about. Linking the owner's spoken rationale to the active work context turns fleeting thoughts into retrievable decisions without requiring them to stop and file notes.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime only for the short capture acknowledgement; background model extracts a title and links the memo to context. Retrieval uses the cheaper model unless ambiguity requires escalation.
- **latency:** Capture acknowledgement under 1 s; context attachment under 5 s; later retrieval under 3 s.
- **cost:** One short audio transcription plus a small extraction call per memo; retrieval usually under $0.01, dominated by transcription/context packaging.
- **security:** The memo and active URL/document identity leave the device. Redact page text by default and store only app, title, URL origin, and a hash unless the owner explicitly asks for content. Never capture passwords or private form fields.
- **missing:** A real semantic Mac context read for document identity and selected text (the pending mac_semantic_context_read request); A durable decision-ledger route keyed by the existing moment bookmark/memo IDs; A retrieval command that searches linked decisions rather than generic notes

### "If the Mac or relay connection drops during a task, tell me exactly which desktop steps finished, which did not, and offer one safe “continue” action when I reconnect."
- **useful because:** Today a lost connection can leave the owner unsure whether a file was written, a browser action happened, or a job needs repeating. A reconciled receipt prevents duplicate actions and makes overnight work trustworthy.
- **path:** relay → mac-bridge → pendant → dashboard
- **model tier:** No realtime model is needed for reconciliation; use deterministic receipt matching and a cheap summarizer only for the spoken one-sentence status.
- **latency:** Reconcile within 2 s of reconnect; spoken status within 4 s; continuation can run asynchronously.
- **cost:** Negligible model cost for deterministic jobs; occasional short summary call under $0.005.
- **security:** Receipts may reveal filenames, URLs, and command outcomes. Redact content and secrets, retain only action type/resource/status, and require the owner's existing destructive-action policy before offering a continuation that mutates data.
- **missing:** A stable cross-surface correlation ID joining POST /execute results to workbench receipts; A reconnect event from the relay to the pendant inbox; An idempotent continuation endpoint that can resume only unfinished steps

### "Run a pendant-and-audio health check from my Mac, and give me a plain-English report saying whether the microphone, Opus path, radio transport, and speaker path each passed."
- **useful because:** The owner currently gets opaque UART counters and can discover an audio failure only during a real conversation. A one-command check would catch the exact class of regressions that have already caused distorted or missing speech.
- **path:** mac-bridge → pendant → relay → dashboard
- **model tier:** Deterministic fixture and threshold evaluation first; use a cheap model only to turn measured counters into a concise explanation.
- **latency:** Bench run 30–60 s; report under 5 s after the final fixture packet.
- **cost:** No meaningful model cost; one short explanation call, dominated by the on-device fixture runtime.
- **security:** The diagnostic must never record or upload microphone content; transmit synthetic sequence numbers and counters only. Store reports in the workspace with restrictive permissions.
- **missing:** A bounded Mac USB-serial diagnostic action with exit code and captured stdout; A standard report schema for audio_path_diagnostic_fixture metrics and thresholds; A relay route that accepts the diagnostic report and associates it with firmware version

### "Answer important questions with an evidence card: tell me the answer, how fresh each source is, what sources agree or conflict, and save the cited provenance so I can audit it later."
- **useful because:** A fluent answer is not enough for decisions. The owner should be able to distinguish a current fact from an inference, spot stale calendar/mail/browser data, and revisit exactly what justified an answer without repeating the research.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic source collection and a cheaper synthesis model by default; reserve realtime only for the spoken answer when the owner is actively asking.
- **latency:** Spoken answer in 3–6 s for cached sources; up to 30 s for a fresh multi-source check, with an immediate progress acknowledgement.
- **cost:** Usually one small synthesis call, under $0.02; source retrieval and provenance storage dominate engineering cost rather than tokens.
- **security:** Provenance can expose private mail, URLs, and file names. Store redacted source identifiers and hashes by default, encrypt full evidence locally, and let the owner delete an evidence card independently of the answer.
- **missing:** A normalized provenance record with source timestamp, freshness, confidence, and contradiction fields; A dashboard/card representation that the pendant can summarize without reading private source bodies aloud; A retrieval route for previously saved evidence cards

### "Let me ask the hive to perform a multi-hour investigation while I am away, then hand me a versioned dossier that shows what changed during the investigation, which claims are uncertain, and an audio summary I can play from the pendant."
- **useful because:** Research currently produces a result, but the owner cannot inspect how it evolved, distinguish newly discovered evidence from earlier findings, or safely resume after a failed overnight run. A versioned dossier makes asynchronous work dependable and reviewable.
- **path:** relay → browser → mac-bridge → pendant → dashboard
- **model tier:** Background/slow model for collection and synthesis; realtime is used only when the owner asks for the final spoken briefing.
- **latency:** Runs asynchronously for minutes or hours; deliver a partial checkpoint within 10 minutes and a final audio summary shortly after completion.
- **cost:** Variable background research cost, roughly $0.10–$1 depending on breadth; browser fetches and repeated synthesis dominate.
- **security:** Limit browsing to owner-selected domains and redact secrets from captured pages. Preserve citations and timestamps, but do not retain full page bodies unless explicitly requested. Any external posting or account mutation remains prohibited without explicit confirmation.
- **missing:** A durable versioned dossier format with checkpoints, diffs, citations, and confidence; A scheduler/worker that can resume interrupted research without duplicating fetches; A pendant audio-delivery job linked to the final dossier version

### "From the pendant, let me ask “what do you remember about me?” and then correct or erase one fact, with a receipt showing every copy and cache that was changed."
- **useful because:** The owner can currently be remembered without a dependable way to inspect provenance, correct stale facts, or verify deletion across relay, Mac workspace, and derived indexes. A physical voice-accessible memory control makes the system accountable rather than silently accumulative.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Deterministic memory lookup, mutation, and deletion propagation; use a small model only to resolve natural-language references to the intended fact, with confirmation for ambiguous or sensitive changes.
- **latency:** List response under 3 s; correction/deletion receipt under 10 s when connected, with queued propagation when a node is offline.
- **cost:** Low model cost, generally under $0.01 per request; consistency tracking and secure deletion are the substantial work.
- **security:** Secrets and sensitive memories must be excluded from spoken summaries unless explicitly requested. Deletion must be cryptographic or tombstone-backed, cover derived indexes and Mac copies, and never pretend completion for an offline node. Corrections to high-sensitivity facts should require explicit confirmation.
- **missing:** A memory inventory API with provenance, sensitivity, retention, and replica fields; A deletion/correction protocol with durable per-node acknowledgements; A pendant-friendly confirmation and receipt format


## What it asked for

_Nothing._
