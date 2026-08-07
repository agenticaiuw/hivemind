# Harness derivation — mac-planner — round 73

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Pause this and save my place. Later, resume it exactly where I left off.”"
- **useful because:** A wearable user is often interrupted away from the Mac. Today the system can act on separate surfaces, but it cannot create one durable, evidence-backed handoff of the live task. This would preserve the actual work context—not just a reminder—then restore it without making the owner reconstruct tabs, drafts, files, and intent.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background model for checkpoint extraction, summarization, and deduplication; realtime only for the spoken confirmation and later resume command.
- **latency:** Acknowledge on the pendant in under 2 seconds; capture checkpoint within 10 seconds. Resume should restore the Mac/browser workspace within 15 seconds, then provide a 20-second spoken orientation.
- **cost:** About $0.01–$0.05 per checkpoint/resume, dominated by one multimodal/context synthesis call; local metadata capture and hashing are negligible. Avoid sending document bodies unless required.
- **security:** Checkpoint contents can include private browser pages, draft text, and file names. Default to metadata plus small owner-selected excerpts, encrypted at rest on the relay, short retention, and an explicit per-workspace sensitivity setting. Never submit, send, or alter external state on resume; opening tabs/files and restoring drafts must be separately represented and undoable.
- **missing:** A cross-surface checkpoint schema with versioned task/workspace IDs, source provenance, sensitivity labels, and TTL; Mac read-only capture implementation (the granted mac_readonly_inspect interface currently returns “no implementation yet”) for foreground app, UI/document context, open files, and browser tabs; Browser bridge support for exporting tab metadata and restoring a named tab set with session affinity, plus stale-device recovery; Relay durable encrypted checkpoint storage and a resumable job/receipt state machine; Mac restore transaction that can reopen apps/files/tabs and place draft text without losing the owner’s current workspace; Pendant command/event for pause/resume and a compact offline acknowledgement queue

### "“Tell me what needs attention, but don’t say anything private out loud.”"
- **useful because:** The pendant is always available but is an unsafe output channel for account names, message contents, codes, or sensitive work pages. The Mac/browser can inspect the private context while the relay and pendant provide attention, yet today there is no end-to-end channel-aware policy that changes the answer and output surface together. This would give a useful spoken alert while keeping details on the Mac dashboard or a selected private screen.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Cheap background classifier for sensitivity labeling and ranking; realtime only for the short spoken alert and follow-up interaction.
- **latency:** Under 3 seconds for a spoken count/category alert; private details available on the Mac within 5 seconds.
- **cost:** Roughly $0.005–$0.02 per brief, dominated by classification/summarization; local redaction and routing are negligible.
- **security:** The relay must never receive or synthesize more private content than necessary for classification. Keep raw page/mail text on the Mac/browser where possible, send only sensitivity labels and minimal task facts, encrypt any queued alert, and make spoken output categories-only by default. Codes, health, financial, and message bodies should be hard-blocked from audio. Dashboard details require the owner’s local session; log only policy decisions, not content.
- **missing:** A cross-surface sensitivity taxonomy and output-channel policy evaluator; Browser and Mail/Calendar adapters that emit local, typed facts with sensitivity labels rather than raw text; A relay protocol carrying category-only alerts and a private-detail retrieval token; Dashboard UI that displays the withheld details and explains why audio was minimized; Policy tests covering mixed results, queued/offline alerts, and accidental transcript leakage

### "“Find the exact thing I’m talking about and put it in front of me—don’t guess if there’s more than one.”"
- **useful because:** People refer to artifacts by imperfect memory (“the invoice from Tuesday,” “that draft I showed Sam”) rather than filenames or URLs. The pendant can capture the reference hands-free, the relay can resolve entities across local files, Mail/Calendar, and authenticated browser tabs, and the Mac can open the selected artifact. Today those stores are isolated and an ambiguous match either fails or risks opening the wrong private item. The owner should get a spoken disambiguation with source/date/participant hints, then one deliberate local open once they choose.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background model for candidate retrieval/ranking and entity resolution; realtime only for the short clarification exchange and confirmation.
- **latency:** Return up to three candidates in 5 seconds; open the chosen artifact within 3 seconds after selection. Never auto-open on a low-confidence match.
- **cost:** Approximately $0.01–$0.04 per query, dominated by embedding/entity-ranking and one synthesis call; keep raw content local and transmit compact candidate metadata.
- **security:** Search spans highly sensitive stores. Run source-specific retrieval locally where possible, return only minimal snippets and provenance, redact message bodies by default, and require an explicit pendant selection for ambiguous or sensitive results. Browser session cookies and full documents must never enter relay logs. Opening a file/tab is reversible navigation; sending, editing, or downloading is outside this capability.
- **missing:** A unified local artifact index spanning approved Mac files, Mail/Calendar records, and authenticated browser tab extracts, with freshness and provenance; A relay query protocol that carries opaque candidate IDs rather than private source content and supports a short disambiguation conversation; A pendant UI/voice protocol for listing candidates and selecting by number or distinctive hint, including offline queuing; Mac/browser open-by-opaque-ID adapters that revalidate identity and freshness before opening; Conflict, permission, and deletion handling so stale or inaccessible candidates are reported rather than silently substituted


## What it asked for

_Nothing._
## Its own summary

I discovered the current grants and verified that mac_readonly_inspect is still only a schema: all four attempted inspections returned “no implementation yet.” I recorded two new, cross-surface proposals: (1) an interruption checkpoint/resume flow that captures a bounded, provenance-rich workspace across pendant, relay, Mac, and authenticated browser, then restores it safely; and (2) channel-aware privacy routing so the pendant announces only category-level attention while private details remain on the local Mac/dashboard. I also notified faculty-action and mac-terminal of the inspection blocker and the need to distinguish evidence correlation from basic receipts. No microphone or Mac mutation was used.

**Biggest unknown:** Whether the orchestrator can actually implement the local read-only adapters and browser/session privacy-label protocol. Until then, the system cannot reliably inspect the current workspace, verify postconditions, or guarantee that private browser/mail details stay off the spoken channel.

