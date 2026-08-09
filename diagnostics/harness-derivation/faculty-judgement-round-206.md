# Harness derivation — faculty-judgement — round 206

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **owner request failures** — The owner's recent history contains many repeated headline and browser-inspection requests with outcomes 'failed' or 'No actions provided', while the owner prefers one short spoken sentence. This is evidence for failure-aware repair and concise truthful fallback.
  - evidence: discover(owner) returned repeated headline requests and 24 failed/empty outcomes in asked_for_and_did_not_get.

## Capabilities it proposed

### "When I repeat a request that failed, just fix the path or tell me plainly why it cannot be done—don't try the same broken thing again."
- **useful because:** The owner has accumulated repeated news and browser requests ending in 'failed' or 'No actions provided'. A failure-aware request repairer would turn opaque repetition into one useful recovery attempt, then a concise truthful explanation instead of burning attention and model cost.
- **path:** pendant → relay → mac → browser
- **model tier:** background for failure clustering and route selection; realtime only for the one-sentence spoken result
- **latency:** Under 1 second for a known failure signature; up to 5 seconds for one bounded alternate path
- **cost:** Usually <$0.01; dominated by one background classification call, with deterministic receipt matching doing most work
- **security:** Inspect only owner-scoped job receipts, action results, and route capability metadata. Never replay a mutation automatically; alternate paths must be read-only or reversible, and external sends still require confirmation.
- **missing:** durable failure-signature store keyed to normalized intent and surface; a bounded alternate-path planner that records why the first path was rejected; one response contract distinguishing no-op, unavailable, and completed

### "Give me the three most important world and US headlines from the last 12 hours, tell me when each was published, and let me ask 'what changed?' later without hearing stale news."
- **useful because:** This is the owner's most repeated unmet request. It would make a spoken brief auditable and temporally honest: fresh sources, deduplicated stories, short audio, and a later delta rather than regenerating the same headlines or silently presenting old results.
- **path:** relay → browser → mac → pendant
- **model tier:** background for source collection, clustering, and delta computation; realtime only for spoken formatting and follow-up
- **latency:** Initial brief 10–20 seconds; 'what changed?' under 3 seconds when source snapshots are cached
- **cost:** $0.02–$0.10 per brief depending on source-fetch/model clustering; follow-ups <$0.01 from cached snapshots
- **security:** Public-source URLs and article text leave the device; never mix authenticated browser tabs or owner mail into this brief. Cite every claim, retain only short redacted excerpts and hashes, and expire raw excerpts quickly.
- **missing:** durable news snapshot/delta store with publication and observed timestamps; source reliability and duplicate-story policy configurable by owner; a spoken follow-up resolver bound to the exact prior brief ID

### "Before you do that, show me exactly what would change on my Mac and in my browser, including anything irreversible, and let me approve only that exact preview."
- **useful because:** Current previews are action-specific and do not span a browser session plus Mac state. A cross-surface shadow run would let the owner understand consequences before a multi-step action, preventing accidental sends, deletes, purchases, or stale-page actions while preserving one deliberate approval boundary.
- **path:** pendant → relay → mac → browser
- **model tier:** background/local deterministic planner for the shadow plan and state diff; realtime only to summarize the diff and capture the owner's approval
- **latency:** 3 seconds for ordinary plans; 15 seconds for a browser-plus-Mac shadow run
- **cost:** $0.01–$0.05 per plan; dominated by browser/Mac state snapshots, not model tokens
- **security:** The shadow runner must use read-only browser actions and side-effect-free Mac probes, redact secrets from the spoken diff, bind approval to a hash of the exact plan and snapshots, expire it quickly, and refuse if state drift is detected.
- **missing:** cross-surface snapshot/diff schema for browser and Mac state; sandbox or transactional simulation for actions that cannot be previewed safely; approval binding from preview hash through physical_transaction_approval_latch

### "That fact is wrong—remember the correction everywhere, stop any pending action based on it, and tell me what else you changed."
- **useful because:** Today the owner can revoke evidence or delete isolated facts, but a correction does not propagate through derived memory, context-graph copies, queued audio, pending drafts, or prepared actions. A single spoken correction should prevent the system from continuing to act on stale or false personal knowledge.
- **path:** pendant → relay → mac → browser
- **model tier:** background deterministic dependency traversal and repair planner; realtime only to confirm the correction and summarize affected items
- **latency:** Immediate acknowledgement under 1 second; propagation and impact report under 10 seconds
- **cost:** $0.01–$0.05 per correction, dominated by dependency traversal and affected-item summarization
- **security:** Require explicit confirmation before deleting or mutating external artifacts. Preserve an auditable tombstone without retaining the corrected sensitive value. Never speak the old value back; scope the correction to owner-authorized entities and claims.
- **missing:** a durable dependency graph linking facts, context-graph entities, evidence capsules, browser provenance, brief items, drafts, and prepared actions; idempotent correction/tombstone propagation across Mac, relay, browser, and pendant queues; a repair preview showing every affected artifact before destructive cleanup


## What it asked for

_Nothing._
