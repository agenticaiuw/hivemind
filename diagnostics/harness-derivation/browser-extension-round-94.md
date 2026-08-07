# Harness derivation — browser-extension — round 94

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Read the private page I’m looking at, tell me the important points over the pendant, and give me the exact cited snippets or fields if I ask a follow-up."
- **useful because:** It combines the only browser-private reach with the pendant’s hands-free interaction: the owner can ask while away from the keyboard, get an evidence-backed answer rather than a lossy summary, and continue with a focused question without exposing the page to public search.
- **path:** browser-extension → mac-planner → relay-realtime → unified → faculty-perception → faculty-judgement
- **model tier:** Use the cheap extraction/summarization path for ordinary page text; invoke realtime only for the owner’s live spoken follow-ups; use vision selectively for charts or layout-only evidence.
- **latency:** Initial extraction and spoken brief within 8–15 seconds; follow-up answers within 2–4 seconds when the cited page snapshot is cached.
- **cost:** Usually one browser extraction plus a small summarization call (roughly <$0.02); chart/layout questions add one vision inference. Audio generation/transport is the secondary cost.
- **security:** Authenticated page text, URLs, and selected screenshots leave Safari for the local Mac/relay processing path; redact secrets and unrelated regions, retain the evidence packet briefly, and never submit forms or send messages as part of this read-only flow.
- **missing:** A working browser command enqueue implementation (all currently granted enqueue tools are schema-only); An active Safari heartbeat/tab lease and a command that returns stable tab-scoped extraction with source locators; A compact evidence-packet handoff from browser-extension to relay-realtime, including snippet hashes and optional screenshot regions; A pendant follow-up correlation ID so spoken questions stay bound to the same page snapshot

### "Compare these two logged-in pages privately—such as my insurance explanation of benefits and a provider bill—and tell me only the mismatches, missing items, and dates I should check, without showing either full page to the cloud or saving them."
- **useful because:** Today the owner can read one private page or prepare a browser transaction, but cannot safely reconcile sensitive information across authenticated sites. This would turn the browser’s unique access into a practical error-catching tool while minimizing exposure of medical, financial, or account data.
- **path:** browser-extension → mac-planner → faculty-perception → faculty-judgement → relay-realtime → unified
- **model tier:** Run deterministic field extraction and normalization on the Mac first; use a cheap background model for reconciliation, escalating to realtime only when the owner asks a spoken clarification. Do not use the expensive live tier for the initial comparison.
- **latency:** Collect both pages in 10–20 seconds and return a concise discrepancy list within 30 seconds; spoken follow-ups should use the cached comparison packet in under 3 seconds.
- **cost:** Typically two authenticated extractions plus one small structured-comparison call, roughly $0.02–$0.08 per comparison; screenshots or ambiguous layout add vision cost.
- **security:** Raw authenticated pages must remain on the Mac or be transformed into a minimized field packet before any relay/model call. Store only selected fields, hashes, and source locators with a short TTL; require explicit user selection of the two tabs and never submit or alter either site.
- **missing:** A browser-side or Mac-side redaction/normalization worker that can extract selected fields before model transmission; A typed two-source comparison job with independent tab/session leases and provenance for every compared field; A short-lived encrypted result packet consumable by the pendant without retaining full page content; A functioning browser command enqueue implementation and reliable Safari heartbeat so the two selected tabs can actually be read


## Changes it proposed to its own stack

### `browser-harness` — Add an extension-heartbeat-aware queue reconciler: when Safari is offline, stop dispatching and expire or explicitly park stale browser commands after a bounded TTL; on reconnect, replay only commands with a valid idempotency key and matching tab/session lease, while exposing per-command state (queued, parked, expired, replayed) and a recovery summary. Clear the current 9-command ambiguity rather than letting old work silently accumulate.
- **owner gets:** The owner will not get surprise navigation or form actions from yesterday’s requests, and will know exactly what was skipped while the laptop or Safari was asleep. Work resumes safely when the browser returns instead of appearing to hang.
- effort: Medium: bridge queue state machine, heartbeat transition handling, TTL worker, and dashboard/route tests for offline and reconnect cases.  ·  risk: A command that the owner expected to continue may expire; retain its original payload and offer an explicit retry. Idempotency and session lease checks prevent duplicate actions after reconnect.
- cost: Negligible API cost; small local JSON/D1 metadata growth for command states and expiry records.  ·  latency: No added latency while online; reconnect adds one reconciliation pass before new commands dispatch.
- security: Improves safety by preventing stale authenticated actions; payloads remain local to the existing browser bridge and should inherit current retention controls.
- depends on: A functioning browser command enqueue implementation; The existing browser heartbeat/status and request-id/idempotency plumbing (chg-14accc01); Durable browser job runner (chg-16bc5dee)

### `integration` — Define and wire a short-lived BrowserEvidencePacket shared between browser-extension, faculty-perception, and relay-realtime: packetId, tab/session lease, URL/title, extraction timestamp, ordered snippets with DOM locators and hashes, normalized fields, and optional screenshot crop references. Let follow-up voice turns request only packet citations, and invalidate packets on tab navigation or TTL expiry.
- **owner gets:** When the owner asks “where did that come from?” while walking, the pendant can quote the exact private-page evidence immediately instead of rereading or sending the whole page again. Answers remain tied to the page they actually saw.
- effort: Medium: schema, browser result adapter, relay lookup route, invalidation hooks, and citation formatting in spoken responses.  ·  risk: A stale citation could mislead after navigation; lease/TTL invalidation and visible URL/timestamp in the response mitigate this. Screenshot crops may contain adjacent sensitive data and must be region-limited.
- cost: Low: metadata and snippet hashes are tiny; avoids repeated full-page context and therefore can reduce model/API cost.  ·  latency: Follow-ups become near-instant from cached packet; initial page extraction unchanged.
- security: Improves minimization by passing selected snippets rather than whole authenticated pages, but packets need encrypted-at-rest short retention and strict per-session access.
- depends on: A functioning browser enqueue implementation; Stable tab/session affinity and typed browser extraction results; A relay lookup path keyed by authenticated packetId; Existing /research page inspection and /pipeline/audio integration

### `browser-harness` — Add a local, declarative cross-tab comparison primitive that accepts two tab leases plus a field-extraction/redaction schema, computes normalized differences on the Mac, and emits only a typed discrepancy packet (field, values, source locator, confidence, timestamp). The raw DOM never enters the relay prompt; the packet is encrypted, short-lived, and invalidated if either tab navigates.
- **owner gets:** The owner can catch billing, booking, policy, or account inconsistencies across private sites without handing complete sensitive pages to the cloud or manually copying them between tabs.
- effort: High: extension must read two leased tabs, Mac bridge needs a local extraction/normalization engine and schema validation, and relay/pendant need discrepancy-packet rendering with citations.  ·  risk: Incorrect selectors or normalization could produce a false mismatch or miss one; show source fields and confidence and label the result as a comparison aid, never an authoritative financial or medical decision. No write action is permitted.
- cost: Small local CPU/storage cost; lower recurring model cost because only normalized fields and mismatches are sent, typically a few kilobytes.  ·  latency: Adds local extraction time (roughly seconds) but avoids full-page upload and reduces remote context latency.
- security: Strongly reduces data exfiltration and retention, but the local Mac process still handles sensitive data; enforce per-tab leases, encrypted temporary files, TTL deletion, and audit records.
- depends on: Real browser command enqueue implementation and Safari heartbeat; Two-tab session affinity with typed extraction results; Local redaction/normalization runtime; Short-lived discrepancy packet route consumed by relay-realtime


## What it asked for

_Nothing._
## Its own summary

Round 94 established a concrete integration gap rather than another generic browser feature. Live status is currently offline (Safari not heartbeating; home-chrome also offline) with 9 pending commands, while three stale sessions remain on disk. Every granted browser enqueue wrapper still returns “schema but no implementation,” so I cannot dispatch even list_tabs. I recorded two owner-facing improvements: heartbeat-aware queue expiry/reconciliation to prevent stale authenticated actions, and a short-lived BrowserEvidencePacket tying private-page snippets/crops to tab leases for fast pendant follow-ups. I also notified mac-planner of the blocked enqueue path.

**Biggest unknown:** Whether the Safari extension is merely asleep/disconnected or the bridge has regressed; we still need a real enqueue implementation plus one live heartbeat/tab to verify end-to-end navigation, extraction, result posting, and stale-command reconciliation.

