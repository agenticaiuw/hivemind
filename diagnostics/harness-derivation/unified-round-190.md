# Harness derivation — unified — round 190

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I reconnect after being away, tell me which commitments are still unresolved, show the strongest evidence for each, and let me close or snooze them by voice without searching every app myself."
- **useful because:** A commitment query alone is an ad-hoc search; it does not maintain a durable owner-facing set of open promises or distinguish evidence from completion. This turns the system into a reliable memory for things the owner said they would do, across browser and Mac surfaces, while retaining provenance and avoiding fabricated completion.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** background for extracting candidate commitments and periodic evidence refresh; realtime for the short reconnect briefing and the owner's close/snooze command
- **latency:** Prepare deltas while idle; first spoken summary within 2 s of a reconnect or explicit request; close/snooze receipt within 3 s.
- **cost:** Moderate: deterministic evidence scans dominate, with a small background model pass per new conversation; <$0.03 per daily refresh, near-zero for no-change days.
- **security:** Search only explicitly bound Mac apps and browser tabs, using commitment_evidence_query. Never mark complete from absence of evidence; require owner confirmation or a strong, cited receipt. Snoozes need an expiry and must not delete evidence. Sensitive commitments should be summarized on the pendant without quoting page contents.
- **missing:** durable commitment records with lifecycle states open, snoozed, completed, rejected; scheduled evidence refresh and reconnect delta generation; a close/snooze command path that records owner intent and links it to evidence

### "Give me a daily trust report: what the system changed, what it retained, what it could not deliver, and whether anything is waiting for my approval or deletion."
- **useful because:** The owner currently has separate job, browser, audio, privacy, and memory surfaces but no single answer to the human question 'what did you do or keep while I was away?' A concise, provenance-linked report makes autonomous behavior legible without requiring dashboard archaeology.
- **path:** relay-realtime → pendant → mac-planner → browser-extension
- **model tier:** background deterministic aggregation with a cheap summarizer; realtime only when the owner asks for a spoken report or drills into an item
- **latency:** Generate incrementally and cache; speak the top-level report within 2 s, with drill-down receipts within 4 s.
- **cost:** Low: mostly bounded event aggregation; <$0.01 per daily report, with model cost only for summarization of changed items.
- **security:** Default to counts, categories, and opaque IDs on the pendant; do not speak page text, message bodies, or inferred facts unless explicitly requested. Separate 'attempted', 'accepted', 'delivered', 'heard', 'retained', and 'deleted'. Never claim off-machine deletion is complete without a receipt. The report itself must not create a new durable copy of sensitive content.
- **missing:** a normalized cross-surface event vocabulary and daily checkpoint; retention-aware aggregation that excludes deleted content while preserving action audit entries; a spoken drill-down protocol bound to one receipt or pending deletion

### "What is the single thing blocking the work I asked for, and what can I do about it? Give me the shortest path to unblock it, not a list of logs."
- **useful because:** Failures are currently scattered across Mac jobs, browser leases, relay processing, permissions, and the unregistered pendant. The owner needs a causal bottleneck answer: one blocking dependency, evidence, the next owner action, and what will happen automatically after it is fixed. This prevents repeated requests and misleading 'working on it' replies.
- **path:** relay-realtime → mac-planner → browser-extension → pendant
- **model tier:** background deterministic diagnosis and ranking; realtime only to explain the selected bottleneck and answer follow-up questions
- **latency:** Return a first bottleneck in under 3 s from cached health; refresh live evidence within 8 s when explicitly requested.
- **cost:** Low to moderate: bounded health/evidence reads, with a small planner call only when multiple independent blockers compete; <$0.02 per diagnosis.
- **security:** Read-only by default. Show only the minimum evidence needed, redact tokens/page content, and distinguish owner action, automatic repair, and impossible-with-current-permissions. Any repair or permission-setting action must be separately confirmed and produce a receipt.
- **missing:** a dependency graph linking jobs to leases, permissions, device/link state, and pending approvals; a ranking policy that chooses one bottleneck rather than dumping raw diagnostics; owner-facing next-step and revalidation records tied to the same incident

### "Before you answer a consequential question, tell me whether you actually verified it, what time the evidence was fresh, and what you are merely inferring; let me say 'show me' to hear the smallest supporting receipt."
- **useful because:** The owner cannot currently distinguish a live observation from cached context, model inference, or an action the system merely intended. A compact evidence contract would make spoken answers trustworthy without forcing a dashboard review, especially when browser state, Mac state, relay state, and pendant state disagree.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** realtime for the short answer and uncertainty label; background/deterministic work for evidence collection, freshness checks, and receipt compression
- **latency:** Normal answer remains under 2 s when evidence is cached; a 'show me' drill-down under 4 s; stale evidence must be labeled immediately rather than delaying indefinitely.
- **cost:** Low to moderate: hashes, timestamps, and bounded receipt selection are cheap; model cost is limited to verbal compression, roughly <$0.01 per drill-down.
- **security:** Speak summaries and opaque receipt IDs by default, never secrets or full page/message contents. Bind each claim to an allowed surface and timestamp; do not manufacture citations when no evidence exists. Evidence access must be read-only and respect browser-tab/app bindings.
- **missing:** a claim-level evidence envelope with source, observation time, freshness deadline, and inference status; a response policy that refuses or qualifies unsupported consequential claims; a pendant-friendly receipt drill-down and verification cache


## What it asked for

_Nothing._
## Its own summary

This round produced three distinct recorded capabilities: (1) a durable cross-surface commitment ledger with evidence-backed completion and voice close/snooze; (2) a daily trust report separating attempted/accepted/delivered/heard/retained/deleted and approval/deletion waits; (3) a single-bottleneck diagnosis that explains the blocker, evidence, owner action, and automatic next step. The inferred-facts list/erase proposal was correctly rejected as an existing capability, so I did not rephrase it.

**Biggest unknown:** The remaining work is implementation detail rather than another concept: commitment persistence and lifecycle states; a normalized, retention-aware event/checkpoint stream for the trust report; and a dependency graph/ranking policy for bottleneck diagnosis. The system also needs live inventory confirmation for the newly granted diagnostic tools before treating their routes as implementation dependencies.

