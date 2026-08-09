# Harness derivation — mac-terminal — round 245

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I ask 'did you really do that?', give me proof, not just a green check: tell me what changed, in which app/account, when, and show me the source trail if it was a browser task."
- **useful because:** A completion message is not evidence. This turns the pendant into a trustworthy witness: it catches commands that exited successfully but changed the wrong window/account, browser submits that were rejected, and jobs whose worker died after reporting success. It is especially valuable when the owner is away from the Mac and can only hear a short answer.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheap background verifier for deterministic receipt/post-state comparison; use realtime only to phrase the final spoken answer. No expensive model is needed when hashes, URLs, titles, and action receipts are sufficient.
- **latency:** Return a provisional 'checking' beacon immediately (<300 ms), then a verified result within 3 s for Mac actions and 8 s for browser actions. If a post-state cannot be observed, say 'unverified' rather than waiting indefinitely.
- **cost:** Usually <$0.01 per invocation: mostly one or two local HTTP reads and browser inspection; LLM cost is near zero for structured comparisons, with a small realtime completion only when the evidence conflicts.
- **security:** Evidence must redact command strings, tokens, page contents, and personal data. Store hashes, app/window identity, URL origin, account label, timestamps, and a bounded claim capsule—not screenshots by default. Speaking proof aloud can expose sensitive facts, so the pendant should say only the minimum and offer details on the private dashboard.
- **missing:** POST /jobs/:jobId/verify (or equivalent) that joins the job, action receipt, ledger step, and observed post-state; A postcondition schema for shell, UI, and browser actions (expected app/url/title/file hash/account); A durable job-to-ledger join; currently planMeta.jobId is null and ledgers remain open; A browser provenance record linked to the verification result; Pendant reply payload support for a compact evidence summary, distinct from the existing running/completed beacon

### "Take care of this before 4 pm; if you hit a decision only I can make, ask me once, otherwise keep going and tell me exactly what is still blocked when the deadline arrives."
- **useful because:** Today the owner must remember to poll jobs, notice a browser challenge, and re-explain unfinished work. This makes delegation survive a dropped pendant link and a sleeping Mac: the relay owns the deadline, the Mac and browser do the work when reachable, and the pendant delivers one sharply scoped question instead of repeated noise.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Background/scheduled tier for deadline tracking, retry ordering, and urgency ranking; realtime only for the one clarification turn or the final spoken handoff. Deterministic state machines should handle retries and escalation.
- **latency:** Acknowledge in <500 ms with a queued deadline; wake on a 30–60 s schedule and on Mac/browser heartbeats. Ask a clarification within 2 minutes of encountering the blocker, and provide a final blocked/completed report at the deadline.
- **cost:** <$0.02/day for ordinary delegations; dominated by occasional browser inspection and one short realtime clarification, not by polling.
- **security:** The relay must never infer authorization for irreversible actions from a deadline. Persist the exact unresolved choice and the minimum context needed to answer it, encrypting browser-origin/account identifiers. A missed heartbeat must produce 'not attempted' or 'stalled', never 'late but done'.
- **missing:** A deadline-owned work contract with explicit success conditions, clarification budget, retry window, and expiry behavior; A relay scheduler that can wake Mac and browser work without an active voice session; Cross-surface retry/resume with idempotency keys so reconnecting does not duplicate sends, purchases, or submissions; A single clarification queue delivered to the pendant and dashboard, with answer binding to the waiting job; A final deadline receipt that distinguishes completed, partially completed, blocked, and never attempted

### "What changed in the work I was looking at yesterday? Use the same project, browser account, and Mac context, ignore unchanged noise, and tell me only the decisions, status changes, and things I now need to do."
- **useful because:** The owner currently has to remember which tab, account, and project a prior conversation referred to. This creates a continuity view across the worn device, authenticated browser, Mac workspace, and always-on relay: it compares fresh evidence against the last deliberate checkpoint instead of dumping a generic briefing.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Background model performs extraction and structured diff; deterministic host/project/session matching narrows the evidence first. Realtime is used only when the owner asks aloud and the final diff needs a concise spoken rendering.
- **latency:** On a voice request, identify the prior context in <2 s, inspect only relevant pages/files in <6 s, and speak a 20–40 s delta. Overnight or on-demand refreshes run asynchronously and notify only when a high-confidence change is found.
- **cost:** <$0.03 per refresh, dominated by browser page inspection and extraction; much cheaper than resending whole pages or full conversation history each turn.
- **security:** Never diff arbitrary tabs or mix accounts. Scope each checkpoint to an explicit host, project/session, and browser account; retain short claims with source URL and timestamps, not page bodies. Conflicting or low-confidence changes must be surfaced as uncertain and never turned into an automatic action.
- **missing:** A first-class cross-surface checkpoint object tying pendant intent, Mac project/window, browser session/account, and relay conversation turn; Structured claim extraction and normalized diff for status, decisions, owners, and due dates; A browser watch/read path that can revisit the same authenticated session without copying page contents to the relay; A durable retention and deletion policy for checkpoint claims and their evidence; A voice command/response route that can select, amend, or forget a checkpoint

### "Where was that thing I saw last week—the chart about renewal rates? Find the exact page or local file, tell me why you think it is the one, and reopen it on the right Mac window without making me search through my history."
- **useful because:** The owner loses work at the boundaries between a closed authenticated browser tab, a local download, and a remembered voice conversation. A temporal cross-surface retrieval capability would turn vague human references into a source-backed result and an immediate reopen, rather than another generic search or an invented memory.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use a background indexing/extraction model to build compact embeddings and entities from browser titles/URLs, local filenames, and deliberately saved voice references; use realtime only to resolve the owner's short query and narrate the top result. Retrieval and confidence ranking should be deterministic where possible.
- **latency:** Speak a candidate in under 4 seconds and reopen only after confidence exceeds a configured threshold; return up to three candidates in under 8 seconds when ambiguous. Indexing happens asynchronously and must not delay ordinary Mac or browser work.
- **cost:** <$0.02 per query after local indexing; storage and embedding refresh dominate, with no need to resend page bodies or full audio transcripts.
- **security:** Index metadata and short owner-approved claims, not arbitrary page contents, passwords, or private tab text. Keep browser-account and host boundaries hard: never use a result from the wrong account merely because its words match. Reopening a page is reversible, but downloading or submitting anything is out of scope and must not be inferred from retrieval.
- **missing:** A cross-surface temporal index joining browser tab history, authenticated session metadata, local file metadata, and pendant turn/bookmark references; A provenance-preserving retrieval record containing the matching fields, timestamp, account/host scope, and confidence explanation; A Mac action that focuses or reopens the exact existing tab/window rather than merely launching a URL; A browser-extension export of safe metadata for closed tabs and navigations without exporting page contents; A compact pendant query/answer protocol that can carry a disambiguation choice offline and deliver it on reconnect

### "What did I promise in my last meeting with Priya, and when did I say I would do it? Give me the exact source moment, then put only the confirmed commitments into my task list."
- **useful because:** Important commitments currently disappear into separate meeting pages, voice turns, calendar events, and local notes. This capability answers a natural question with a cited moment and separates an actual promise from a suggestion or someone else's task, preventing both forgotten work and noisy task lists.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Background extraction identifies speakers, commitments, owners, and due dates from explicitly captured meeting/browser artifacts; realtime answers the question. A deterministic commitment state machine should require an owner/source/time tuple before creating a task.
- **latency:** Return cited candidates in 5 seconds for recently indexed meetings; schedule older indexing asynchronously. Task creation should complete within 2 seconds after the owner says 'put that on my list'.
- **cost:** <$0.04 per meeting refresh, mostly structured extraction; query-time cost is negligible when the meeting has already been indexed.
- **security:** Only process meetings and notes the owner explicitly links or records; do not silently record microphone audio. Keep participant identities and meeting content local where possible, redact unrelated text, and preserve a correction path when speaker attribution or commitment ownership is uncertain.
- **missing:** An explicit meeting-artifact capture contract spanning browser meeting metadata, owner-created pendant markers, and selected local notes; Commitment extraction with speaker/owner attribution, quoted evidence offsets, confidence, and due-date normalization; A task-write adapter that records the source commitment and supports correction or deletion; A source-moment playback/seek response that can point to the exact browser page, note, or owner timestamp without exporting the whole meeting; A policy separating 'remember this promise' from ambient recording, with a visible capture indicator

### "Before I send this document, show me every claim in it that came from my browser or a voice note, which source supports it, and what is stale or unsupported."
- **useful because:** Generated documents silently mix copied browser facts, remembered conversation, and model invention. The owner needs a source-aware preflight that works on the actual local file while following authenticated browser provenance, so they can fix one unsupported sentence instead of rereading the entire document.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** A background model extracts claims and aligns them to source evidence; deterministic hashing and file parsing identify the exact document version. Realtime only summarizes the findings or answers a spoken follow-up.
- **latency:** For a normal local document, produce a first risk-ranked report within 6 seconds and update incrementally as the file changes. Never block ordinary editing or send the document anywhere.
- **cost:** <$0.05 per document scan, dominated by extraction for novel prose; repeated scans reuse file and source hashes.
- **security:** Keep the document and source text on the Mac/browser boundary whenever possible; send only claim hashes and short evidence snippets to the relay. Do not infer support from lexical similarity alone, mark stale sources explicitly, and require the owner to choose whether any suggested correction is applied.
- **missing:** A local-document claim extraction and span-addressing service that can inspect the exact saved version; A provenance graph linking each claim to browser source URL/account, voice-turn marker, local file, timestamp, and freshness; A browser-side evidence capsule API that can prove a claim without exporting an entire authenticated page; A Mac diff/apply action for proposed corrections with an undoable receipt; A pendant-friendly report format that speaks only unsupported/high-risk claims and lets the owner request the full list


## What it asked for

_Nothing._
## Its own summary

Round 245 produced three owner-facing capabilities: proof-carrying completion (verified post-state and source trail rather than green checks), deadline-owned delegation with one clarification and honest expiry, and cross-surface project change diffs grounded in browser/Mac/account checkpoints. I also verified that the newly granted mac_read_diagnostics and mac_usb_serial_diagnostics schemas still do not resolve to live capabilities, so neither actually ran; the Mac agent and serial devices remain reachable only through existing routes/run_shell and the bench capture scripts.

**Biggest unknown:** Whether the orchestrator will add a real bounded UART diagnostic route and host diagnostics route, and whether existing browser provenance/workbench routes are live despite not resolving in the proposal recorder. The next useful implementation work is the missing joins: job↔ledger↔postcondition evidence, deadline work contracts, and checkpoint-scoped browser/Mac diffs.

