# Harness derivation — unified — round 218

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Every morning, tell me only what changed since yesterday in my scheduled research brief, with links and a short audio version I can play on the pendant."
- **useful because:** The owner gets a useful delta instead of hearing the same briefing repeatedly; citations remain available on the Mac while the pendant delivers the compact spoken result.
- **path:** relay → browser → mac-planner → pendant
- **model tier:** background for fetching/diffing and citation synthesis; realtime only when the owner asks a follow-up
- **latency:** Background run may take up to 90 seconds; spoken playback should be queued within 10 seconds after completion.
- **cost:** Typically 1 background synthesis call plus browser fetches; roughly $0.01-$0.05 per daily brief, dominated by model summarization and page retrieval.
- **security:** Read only the explicitly configured research sites and the prior briefing; do not send unrelated browser tabs. Store citations and a content hash, not full pages by default. Require confirmation before any follow-up action suggested by the brief.
- **missing:** A persistent per-topic normalized snapshot and content-hash history; A diff-aware briefing job that can suppress unchanged claims; A relay-to-pendant audio enqueue path that records playback acknowledgement

### "When I say “save this,” capture the page or document I am looking at, make a short cited note, and let me find it later by asking the pendant what I saved it for."
- **useful because:** It turns a fleeting browser moment into a retrievable, provenance-preserving memory without forcing the owner to copy URLs, title text, or explanations manually.
- **path:** pendant → browser-extension → mac-planner → relay
- **model tier:** Realtime for the one-sentence intent and confirmation; background for note extraction and indexing.
- **latency:** Acknowledge capture in under 2 seconds; produce the cited note in under 15 seconds; search response under 5 seconds.
- **cost:** About $0.005-$0.03 per capture/search, dominated by extraction and embedding or lexical indexing; browser reads are otherwise local.
- **security:** Only inspect the focused tab after the deliberate “save this” utterance. Exclude passwords, payment pages, and hidden tab contents. Persist URL, title, selected/visible excerpt, timestamp, and a content hash; ask before storing sensitive excerpts or sharing the note elsewhere.
- **missing:** A browser command that returns a bounded visible excerpt with page identity and a stable content hash; A provenance-linked note index with per-item deletion and replica erase status; A spoken pendant search intent that queries only the owner’s saved captures

### "Show me the facts you inferred about me this week, each with its source and where it was copied, and let me forget one everywhere without deleting the action history."
- **useful because:** The owner can audit and correct memories the system created without being asked, while preserving the separate accountability record of actions it took.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Deterministic lineage and deletion planning; realtime only for the spoken selection and confirmation, with no model deciding deletion scope.
- **latency:** List a bounded page in under 5 seconds; deletion plan in under 3 seconds; remote erasure reports requested/pending until receipts arrive.
- **cost:** Near-zero for listing and erasure; at most $0.001-$0.01 for rendering a concise spoken summary.
- **security:** Never speak secret fact values by default in a public setting. Show evidence snippets only after the owner requests them. Deletion must be item-specific, idempotent, authenticated, and preserve immutable action history; clearly distinguish local deletion from pending relay/replica deletion.
- **missing:** A first-class extracted-fact ledger with source capsules, derived-copy references, and deletion receipts; A cross-surface erase coordinator covering facts.json, context graph, relay replicas, and browser-derived caches; A pendant UI/voice command that paginates inferred facts without exposing unrelated secrets

### "Before my scheduled work starts, check only the sites I named and tell me whether any session has expired or is waiting for me to sign in; do not click or submit anything."
- **useful because:** The owner learns about authentication blockers before a task fails, without giving the agent permission to alter accounts or navigate sensitive pages.
- **path:** relay → browser-extension → mac-planner → pendant
- **model tier:** Deterministic page-state classifier for signed-out/MFA/session-expired signals; realtime only to explain the affected site when asked.
- **latency:** Run as a scheduled preflight in under 20 seconds for up to 10 bound sites; speak one concise warning before the scheduled task.
- **cost:** Near-zero when inspecting existing tabs; roughly $0.001-$0.01 only for ambiguous page-state classification.
- **security:** Require an explicit allowlist of URL origins and tab bindings. Never read or transmit password fields, OTPs, page text beyond bounded auth-state markers, or cookies. Read-only by default; no refresh, click, or form submission.
- **missing:** A typed browser auth-state inspection result with confidence and evidence category, not page content; A scheduler dependency/preflight gate that can warn without cancelling the task; A signed, privacy-minimized receipt proving no mutating browser action occurred

### "Tell me when two sources in my own workspace disagree about something important—like a calendar time versus an email, or a document versus a browser page—and read me the conflict with both citations, without choosing a side or changing anything."
- **useful because:** The owner catches silent schedule and commitment contradictions before acting on the wrong version. The system exposes uncertainty instead of confidently merging incompatible records.
- **path:** relay → mac-planner → browser-extension → pendant
- **model tier:** Background model for extracting and comparing claims; deterministic source binding, timestamps, and citation retention; realtime only when the owner asks for an explanation.
- **latency:** Scheduled scans complete within 60 seconds; urgent conflict alerts are queued for the next safe speech boundary, never interrupting by default.
- **cost:** Roughly $0.02-$0.10 per scan depending on the number of bound documents; deterministic comparisons should avoid model calls for unchanged content.
- **security:** Scan only owner-selected folders, calendars, mail threads, and browser origins. Preserve exact source locations and timestamps, but do not copy full sensitive documents into relay storage. Never auto-resolve, edit, send, or reschedule; require explicit confirmation for any later action.
- **missing:** A cross-surface claim extraction and contradiction index with source/version provenance; A freshness-aware comparison policy that distinguishes a correction from a stale copy; A pendant alert payload that carries two citation handles and an uncertainty explanation without exposing document contents

### "For any answer that could affect a decision, tell me separately what you directly observed, what you inferred, and what remains unknown, with a way to inspect the underlying source without repeating private content aloud."
- **useful because:** The owner can distinguish evidence from model interpretation and avoid treating a plausible guess as a fact, especially when the answer combines the browser, Mac, relay, and pendant.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Deterministic provenance assembly for observed fields and source handles; a low-cost model may summarize inference, but it cannot alter evidence labels.
- **latency:** Normal answer in under 5 seconds; source inspection on demand in under 10 seconds.
- **cost:** Small incremental cost, about $0.001-$0.02 per answer for structured claim extraction; source reads remain local where possible.
- **security:** Speak only redacted evidence summaries by default. Keep raw source contents on the originating surface, use expiring opaque handles, and log every source disclosure. Never present inferred text as a quoted observation.
- **missing:** A response contract with explicit observed/inferred/unknown claim types and source handles; A cross-surface provenance resolver that can reopen the bound source without copying it to the relay; A pendant interaction for asking to inspect one claim at a time

### "Let this one website perform only the specific task I just described for the next ten minutes, then show me exactly what it is allowed to touch and revoke it automatically when done."
- **useful because:** The owner gets useful browser automation without granting the agent broad ongoing authority; a narrow, expiring delegation is easier to understand and safer to recover than a permanent session permission.
- **path:** pendant → relay → browser-extension → mac-planner
- **model tier:** Deterministic scope compiler and policy checker; realtime model parses the owner’s request, but execution is restricted to a signed capability token and the existing physical approval latch.
- **latency:** Scope preview under 3 seconds; physical approval and first action within 5 seconds; automatic expiry is immediate at deadline or task completion.
- **cost:** About $0.005-$0.03 per delegation for scope interpretation and receipts; browser execution cost is otherwise local.
- **security:** Bind the token to one origin, one task digest, allowed action types, resource selectors, expiry, and a maximum action count. Never delegate credential entry, purchases, deletion, or message sending without a separate confirmation. Revoke on tab change, navigation outside the origin, or scope mismatch; retain an audit receipt without page secrets.
- **missing:** A least-privilege browser capability-token format and verifier; A real bridge from physical_transaction_approval_latch decisions to browser command authorization; A revocation and scope-violation event path that reaches the pendant before further actions


## Changes it proposed to its own stack

### `integration` — Build a research-delta coordinator between the existing routine, research briefing, speech, and pipeline records. Persist per-topic canonical claim hashes and citation IDs; on each run compute added/removed/changed claims, suppress unchanged material, generate speech only for the delta, and attach the briefing ID and claim hashes to the audio delivery acknowledgement. If no claims changed, emit a quiet no-change receipt instead of audio.
- **owner gets:** Daily research briefings become short and genuinely new, and the owner can ask which spoken claim came from which source rather than hearing an opaque summary.
- effort: Medium: a background coordinator, normalized claim schema, diff tests, and wiring to existing briefing speech and delivery records.  ·  risk: Poor extraction could classify a paraphrase as new or hide a meaningful correction. Preserve the prior full briefing, show a 'changed classification' explanation on request, and fall back to the full brief when confidence is low.
- cost: Small additional storage for hashes and citation metadata; one background model call per topic/run, with lower audio/model cost when nothing changes.  ·  latency: Adds roughly 5-20 seconds to scheduled research runs; no impact on live conversation.
- security: Store hashes, source URLs, and bounded citation excerpts by default, not whole pages. Respect the configured site allowlist and never inspect unrelated tabs.
- depends on: A durable per-topic claim/citation snapshot store; A typed audio-delivery acknowledgement that accepts briefing and claim identifiers; A scheduler hook that can enqueue a no-change receipt without speaking audio

### `browser-harness` — Add a read-only auth-state probe for explicitly bound tabs. It should classify only signed_in, signed_out, session_expired, mfa_waiting, consent_blocked, or unknown from URL/title/DOM markers, strip all field values, and return tab binding, freshness, confidence, and a no-mutation receipt. Let routines invoke it as a preflight and warn the owner without executing the routine's actions.
- **owner gets:** Scheduled work fails less often for a simple expired login, while the agent gains no ability to enter credentials, click consent, or submit forms.
- effort: Medium: extension-side classifier, route schema, allowlist enforcement, tests for common login states, and routine preflight wiring.  ·  risk: A site redesign can cause false unknown or false signed-out results. Treat unknown as a warning rather than a blocker, expire cached results quickly, and never infer state from cookies or secrets.
- cost: Negligible runtime cost; small extension and server implementation effort; no model call needed for known markers.  ·  latency: Under 1 second per bound tab, typically parallelized; adds at most a few seconds to a scheduled preflight.
- security: Strictly read-only. URL origins and tab IDs are allowlisted; DOM extraction is limited to auth-state markers and receipts contain no page text, cookies, tokens, or form values.
- depends on: A typed browser inspection result with real auth-state enums; Routine preflight hooks that can warn without mutating or cancelling; Per-tab binding persistence with expiry


## What it asked for

_Nothing._
## Its own summary

This round I recorded four owner-facing capabilities and two concrete changes. The strongest is a research-delta brief: scheduled research compares normalized claims, speaks only changes, and links every spoken claim to citation and delivery receipts. I also recorded provenance-preserving “save this” capture, inferred-fact audit/erase with replica status, and read-only browser authentication preflight; the last health-check idea was rejected as an existing capability, so I did not repeat it. Concrete changes specify the missing research-delta coordinator and a typed, no-mutation browser auth-state probe.

**Biggest unknown:** The remaining work is mostly the missing connective contracts, not more routes: (1) durable per-topic claim/citation snapshots and a diff schema; (2) a typed audio-delivery receipt that carries briefing/claim IDs; (3) a bounded browser auth-state enum and routine preflight hook; and (4) a first-class extracted-fact lineage/erase ledger spanning local graph, relay replicas, and evidence capsules. I still need those contracts implemented before the owner can experience the proposals end to end.

