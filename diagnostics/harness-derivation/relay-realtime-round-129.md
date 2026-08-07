# Harness derivation — relay-realtime — round 129

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If the connection drops while I’m talking, keep a short record of what we agreed and pick up the task when the Mac is available again."
- **useful because:** Right now a dropped link can lose the plan and force the owner to restate everything. A resilient handoff keeps momentum and reduces friction, especially when the owner is away from the Mac.
- **path:** pendant → relay → mac-bridge → browser
- **model tier:** Realtime for the live summary; mac-planner (cheaper, slower) for continuing the task once a target is online.
- **latency:** Under a second to confirm the handoff was saved; continuation can happen later.
- **cost:** Small realtime cost to summarize and store a compact intent; the expensive part is any later browser/Mac work, which runs off the realtime path.
- **security:** Stores a brief, sensitive snapshot (intent summary, referenced services). Must encrypt at rest, redact secrets, and avoid storing full audio unless the owner explicitly asked for a recording. Any action after resume should be reversible or require approval.
- **missing:** A relay-side job/intent journal that can resume work without a scheduler; Implementation for relay_route_intent and relay_job_status beyond schema; A durable browser job runner for public pages when the Mac is offline; A typed context projection so we store only relevant facts

### "“Check the authenticated work portal I currently have open against my Mac’s local project files and calendar, then tell me which commitments conflict or are at risk—without changing anything. Keep the source evidence so I can ask ‘why?’ or ‘what should I move?’ from the pendant.”"
- **useful because:** Today the browser can see logged-in portal pages and the Mac can see local project context, but no single capability can join those private surfaces into a trustworthy, spoken decision brief. This gives the owner an actionable conflict list while away from the Mac, with drill-down evidence and no accidental edits.
- **path:** pendant → relay-realtime → browser-extension → browser → mac-planner → mac-terminal → dashboard
- **model tier:** Use relay-realtime only to capture the request and deliver a short spoken result; use a cheaper background orchestration/model for extraction, normalization, date/entity matching, and conflict ranking. mac-planner/mac-terminal gather local calendar/project evidence, while browser-extension/browser read the already-authenticated portal.
- **latency:** Acknowledge immediately; return an initial brief within 30–60 seconds. Evidence expansion on a follow-up can take up to 10 seconds.
- **cost:** Roughly $0.03–$0.15 per run, dominated by portal/page extraction and cross-source reasoning; relay speech itself should be a small fraction.
- **security:** Private authenticated portal content and local files/calendar leave their respective surfaces only to the relay’s authenticated backend. Default to read-only, show source URLs/file names and timestamps, redact unrelated content, and require explicit confirmation before any suggested rescheduling or edits.
- **missing:** A cross-surface evidence joiner that can request typed read snapshots from browser sessions and the Mac in one correlated run; A durable evidence bundle with source provenance, freshness, and follow-up query support; A background fan-out/fan-in worker and a pendant delivery path for results after the owner stops speaking; Conflict-ranking and date normalization that understands project commitments rather than only keyword search

### "“Make a private context capsule from what I’m looking at and the last thing I said, so the Mac and browser agents can act on it. Keep it for 15 minutes, let me ask follow-ups from the pendant, then erase it.”"
- **useful because:** The owner repeatedly pays latency and context cost because each voice turn starts cold and the wearable cannot see the Mac or browser. A short-lived, owner-named capsule would let one spoken reference (‘that invoice’, ‘this page’, ‘the error I just showed you’) travel coherently across the pendant, authenticated browser, and Mac without making broad permanent memory.
- **path:** pendant → relay-realtime → browser-extension → browser → mac-planner → mac-vision → dashboard
- **model tier:** Realtime handles only capsule creation, naming, and concise spoken confirmations. A cheaper background model compresses the transcript and page/screen observations into structured entities and citations; downstream agents consume the capsule rather than receiving the full history each turn.
- **latency:** Create an acknowledgement in under 1 second; collect browser/Mac observations and publish the capsule within 3–8 seconds. Follow-up resolution should be under 2 seconds when the capsule is warm.
- **cost:** About $0.005–$0.04 per capsule, mainly compression and optional screen/page extraction; follow-ups become cheaper because large context is not resent.
- **security:** Capsules must be encrypted, scoped to the owner/session, explicit about which surfaces contributed, and hard-expire after the requested TTL. Never silently include microphone audio, unrelated tabs, or unrelated Mac windows. Mutating actions still need the normal action path; deleting a capsule should be immediate and auditable.
- **missing:** A relay-side ephemeral capsule store with TTL, size limits, provenance, and explicit delete; A browser-extension observation endpoint and Mac observation endpoint that contribute typed snapshots to the same capsule id; Tool contracts allowing mac-planner/browser agents to resolve a capsule id instead of receiving copied raw context; Pendant affordances for capsule name/TTL confirmation and a spoken ‘forget that capsule’ command

### "“What did the system do for me yesterday, and what is still unresolved? Give me a spoken, source-linked audit across my Mac actions, browser work, and pendant requests; if I say ‘undo the last one,’ take me to the exact reversible receipt.”"
- **useful because:** Today status is fragmented: the owner can ask about a known relay job, but cannot reconstruct a day of work across Mac actions, authenticated browser activity, and voice requests. A time-bounded spoken audit would restore trust, expose dropped or partial work, and make the existing receipt/undo mechanisms usable without remembering a job id.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension → browser → dashboard
- **model tier:** Use a low-cost background model to cluster logs, receipts, browser inspections, and voice-run history by task and confidence; use relay-realtime only to answer the owner’s short follow-up and route a specifically identified undo.
- **latency:** Initial acknowledgement immediately; a day-range audit in 10–30 seconds; a receipt detail or undo target in under 3 seconds.
- **cost:** Approximately $0.02–$0.10 per audit, dominated by log retrieval and summarization; follow-ups are inexpensive if the normalized audit is cached briefly.
- **security:** Only the owner’s authenticated records may be included. Distinguish attempted, completed, failed, and unknown actions; never infer completion from an intent. Cite timestamps, surface, and receipt/job ids. Undo must target one exact reversible receipt and report when no safe inverse exists; do not expose secrets from logs.
- **missing:** A cross-surface audit index that correlates voice runs, relay jobs, Mac receipts, and browser request ids into task threads; A typed status vocabulary for partial/unknown outcomes and a citation-rich spoken result format; A time-range query and short-lived cache exposed to the pendant, plus an exact receipt selector for undo


## Changes it proposed to its own stack

### `integration` — Add a cross-surface handoff ledger for interrupted voice tasks: when the relay detects a dropped uplink mid-conversation, it stores a compact intent summary plus any confirmed constraints, then notifies mac-planner to resume when available, and optionally uses a server browser runner for public pages.
- **owner gets:** The owner doesn’t have to repeat themselves after a network hiccup. Tasks continue on the best available surface, and results come back as a short spoken receipt.
- effort: Medium to high: requires a small intent-summary format, relay persistence, mac-planner resume support, and a fallback path for public web steps.  ·  risk: Resuming with stale assumptions. Mitigate by storing only confirmed facts, requiring re-validation before irreversible actions, and providing a clear spoken summary of what will happen next.
- cost: Low per task (small summaries). Most cost comes from Mac/browser work executed later.  ·  latency: Fast save/ack during the call; continuation can be asynchronous.
- security: Sensitive context may be stored; encrypt, minimize, and expire. Do not store full audio by default.
- depends on: Typed context projection service for minimal summaries; Durable browser job runner for public pages; Resume API in mac-planner


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing capabilities: (1) a cross-surface conflict brief joining authenticated browser commitments with Mac project/calendar context, (2) expiring spoken context capsules that prevent repeated context transfer across pendant, browser, and Mac, and (3) a provenance-linked spoken audit of what the hive did and what remains unresolved. Each proposal names the missing connective infrastructure rather than pretending the existing routes already provide it.

**Biggest unknown:** Whether the existing audit/history routes already expose enough stable cross-surface identifiers to implement the audit index; I did not re-discover because the owner explicitly ended discovery for this round.

