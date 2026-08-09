# Harness derivation — mac-planner — round 182

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I enter privacy mode on the pendant, immediately make the whole hive go dark: stop relay capture, close or suspend browser sessions, cancel queued Mac actions, and record a local-only audit marker; when I exit, restore only the surfaces I explicitly allow."
- **useful because:** A pendant privacy latch currently protects the gadget, but another node could still be capturing, holding an authenticated tab, or executing a queued action. This gives the owner one physical, offline-capable privacy boundary across every surface.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-action → faculty-judgement
- **model tier:** Deterministic state machine and policy routing; no model call for entry/exit. Use the cheap model only to explain the resulting audit summary.
- **latency:** Local microphone/playback mute immediately; relay and Mac/browser quiescence target <1 s when linked, with a durable pending state when disconnected.
- **cost:** Negligible per transition; one small state event and optional audit summary.
- **security:** Privacy entry must be fail-closed and local even without LTE. Do not transmit the reason or audio. Browser session suspension must preserve no page contents and use a per-session owner policy; queued high-impact Mac jobs must be cancelled or marked blocked, never silently resumed. Exit is local but requires explicit surface allow flags.
- **missing:** A relay-wide privacy-state protocol with monotonic epoch and fail-closed expiry; Mac endpoint to cancel/pause all pending jobs and acknowledge quiescence; Browser bridge command to suspend authenticated sessions without destroying their cookies; A persistent owner policy mapping privacy mode to surfaces and an audit receipt

### "If a Mac or browser job fails while I am away, tell me on the pendant exactly what failed and offer a single-button retry that is safe against duplicate files, messages, or payments; after retry, report a short receipt."
- **useful because:** Today a server plan can be handed to the Mac, but failure recovery is split across logs and job records. The owner should not have to return to the laptop or remember a job id to recover from an interrupted action.
- **path:** relay-realtime → mac-planner → browser-extension → pendant → faculty-perception → faculty-action
- **model tier:** Deterministic receipt classifier and idempotency checks; cheap model only for compressing technical failure into spoken language.
- **latency:** Failure surfaced to the pendant within 2 s when linked; retry starts on the next press and returns an acknowledgement within 5 s.
- **cost:** <$0.002 per failure/retry, mostly relay event and optional summarization; no model cost for normal success.
- **security:** Never retry blindly for sends, purchases, deletes, or external side effects. Each job needs an idempotency key, touched-resource digest, and a resume-safe boundary. The pendant should expose only redacted app/resource names, not message bodies or secrets. Owner policy must decide which classes may be retried physically.
- **missing:** A durable cross-node failure event schema with retry eligibility and idempotency key; Mac/browser executors must emit step-level receipts and persist atomic checkpoints; Pendant inbox integration that renders retryable failures as a distinct alert action; A policy table for retryable versus always-stop action classes

### "Before an automated Mac or browser action sends an external message or publishes data, give me a redacted one-line preview on the pendant and let me approve or reject it with the physical button; low-risk local actions continue without interruption."
- **useful because:** The system can act across authenticated apps, but the owner has no compact way to catch a wrong recipient, wrong attachment, or accidental disclosure while away from the screen. A physical preview makes the pendant a useful last-mile safety control without forcing approval for ordinary desktop work.
- **path:** relay-realtime → mac-planner → browser-extension → pendant → faculty-judgement → faculty-action
- **model tier:** Deterministic destination/data-class classifier first; cheap model for redacted one-line summaries; realtime only if the owner asks a follow-up question.
- **latency:** Preview generated before dispatch in <1 s; button decision expires after 30 s; rejected/expired actions never leave the device.
- **cost:** <$0.005 per gated action, dominated by summarization; zero for actions classified as local/read-only.
- **security:** Default-deny on uncertain external side effects. Redaction must happen before audio leaves the relay and must omit message body, secrets, and full filenames. The action digest must bind recipient, destination, and payload hash so changing a plan after approval invalidates it. The owner must configure which action classes are gated; this must not silently override the stated maximum-access policy.
- **missing:** A pre-dispatch interception seam in Mac and browser executors; A typed outbound-risk and redaction schema shared by relay, Mac, and browser; Pendant inbox record with approve/reject/expiry semantics and a monotonic action digest; Owner-configurable policy entries defining gated destinations and data classes

### "Find the thing I was working on when I say 'where did I leave the draft about X?' Search my recent Mac files, browser tabs, Calendar/Mail metadata, and pendant bookmarks together, rank likely matches with reasons, and open the chosen result only when I ask."
- **useful because:** The owner currently has fragmented search surfaces and no way to connect a remembered pendant moment to a local file or authenticated tab. A single evidence-ranked answer would recover work across the exact boundaries that make this hive worthwhile.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement
- **model tier:** Cheap retrieval/ranking model over redacted metadata; realtime model only for the spoken ambiguity resolution.
- **latency:** First ranked candidates in <3 s; opening a chosen local file/tab is a separate explicit action.
- **cost:** ~$0.002-0.02 per query depending on candidate count; indexing can run locally with no model cost.
- **security:** Search metadata locally where possible; never send full Mail bodies, page contents, or file contents unless the owner asks. Exclude password managers, private browsing, and protected folders. Return provenance and confidence, and ask a clarifying question rather than opening a low-confidence result.
- **missing:** A federated retrieval endpoint joining Mac file metadata, mac_read_sources, browser session metadata, and pendant bookmark ledger; Incremental local index with redaction and per-source retention controls; Relay query protocol that can fan out while the pendant conversation remains responsive

### "Tell me which promises I have made but not yet kept: reconcile what I said in pendant conversations, what I wrote or sent from Mail/browser, and what my Calendar says, then show only commitments with missing evidence and let me close one with a spoken update."
- **useful because:** The owner gets reminders and search, but not an evidence-based answer to the painful question 'what did I commit to that is still hanging?' This would connect spoken intent to observable follow-through across nodes instead of producing another ungrounded task list.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Background model extracts candidate commitments and entities; deterministic joins against Calendar/Mail/browser receipts; realtime model only answers the final spoken query.
- **latency:** Nightly reconciliation in the background; an on-demand answer in under 5 seconds with evidence links and an explicit unknown state when evidence is absent.
- **cost:** Approximately $0.02-$0.10 per daily reconciliation depending on transcript volume; local metadata joins and unchanged commitments should be incremental and free.
- **security:** Commitment extraction is sensitive. Keep transcript bodies and message content local where possible, store only a redacted commitment, parties, due window, confidence, and evidence pointers. Never infer that silence means failure; distinguish 'no evidence found' from 'not done.' External follow-up messages require a separate owner-authorized action policy.
- **missing:** A cross-surface commitment schema with provenance, confidence, due-window, and explicit done/unknown states; A relay job that can correlate pendant transcripts with mac_read_sources results and browser action receipts without copying full content; A local append-only evidence index for sent mail, calendar changes, browser submissions, and completed Mac jobs; A spoken close/update operation that records the owner's correction without rewriting source evidence

### "Before I ask you to do a multi-app task, show me a time- and data-impact simulation: which files, accounts, tabs, calendar commitments, and downstream jobs would change, what conflicts it creates, and what the reversible rollback would be—without touching anything."
- **useful because:** The current preflight can classify an action list, but it cannot tell the owner the human consequences of a plan spanning Calendar, Mail, files, and authenticated browser state. This lets the owner choose a plan based on consequences rather than trusting a terse action preview.
- **path:** relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement
- **model tier:** Deterministic dependency/resource analysis first; cheap model turns the graph into a concise spoken explanation; no realtime reasoning except for follow-up questions.
- **latency:** Simulation in 2-8 seconds for a normal plan; no side effects and no confirmation required because it is strictly speculative.
- **cost:** <$0.02 per simulation; cost is dominated by fetching source metadata and graph expansion, not generation.
- **security:** Use metadata and redacted previews by default. Do not execute probing actions against external services. Mark unknown side effects explicitly instead of claiming rollback. Authenticated browser data must stay in the browser harness unless the owner requests a specific field.
- **missing:** A dry-run planner that expands semantic consequences across Mac actions, browser commands, Calendar/Mail, and queued jobs; A resource/dependency graph with before/after projections and rollback recipes; Browser-side read-only impact inspection for forms, uploads, and session mutations; A common plan-diff format that the pendant, Mac UI, and relay can render consistently

### "When different apps refer to the same person, project, or deadline by different names, ask me once to resolve the identity and then keep Calendar, Mail, browser, and pendant references linked—with a visible way to correct a mistaken link."
- **useful because:** The hive cannot reliably join evidence when 'Acme renewal,' 'Acme contract,' and an abbreviated browser tab may be the same work. A corrected identity link would make cross-node retrieval and follow-through dependable without guessing silently.
- **path:** relay-realtime → mac-planner → browser-extension → pendant → faculty-perception → faculty-judgement
- **model tier:** Cheap entity-resolution model proposes matches; deterministic confidence thresholds and explicit owner corrections govern merges and splits.
- **latency:** Suggest matches asynchronously; ask a one-sentence clarification during the next relevant interaction, under 2 seconds; corrections propagate within 10 seconds.
- **cost:** <$0.01 per new entity candidate; most updates are local graph operations.
- **security:** Never merge people or projects solely from name similarity. Preserve source-specific identifiers and provenance, support undo/split, and keep sensitive contact details local. A low-confidence match must remain separate rather than leaking context across identities.
- **missing:** Cross-source entity resolver over Calendar/Mail, browser metadata, Mac files, and pendant ledger; Owner-facing merge/split/correct protocol available by voice and Mac UI; Source-scoped stable identifiers and provenance edges in the context graph; A redaction-aware graph query so one surface cannot retrieve another surface's private fields by default


## What it asked for

_Nothing._
## Its own summary

Round 182 produced three new accepted cross-node capabilities: hive-wide fail-closed privacy mode (pendant latch quiesces relay/Mac/browser), pendant preview/approve for outbound external side effects, and federated 'where did I leave it?' retrieval across Mac, browser, Calendar/Mail metadata, and pendant bookmarks. A fourth USB-tethered full-terminal proposal collided with an existing backlog item, so I did not restate it. I still need a real serial exchange tool/bridge for /dev/cu.usbmodem00096003658* and the ESP32 bridge, plus the missing semantic Mac context operation (window/document identity and selected text). Accessibility/Screen Recording remains owner-blocked; the designs must degrade to metadata-only observation.

**Biggest unknown:** Whether the existing relay/browser implementations already expose a durable privacy epoch, outbound interception seam, or federated retrieval index; the live route inventory names no dedicated endpoints for those pieces.

