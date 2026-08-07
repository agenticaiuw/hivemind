# Harness derivation — relay-realtime — round 112

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Since the last time I asked, what actually changed in this project—and what should I care about?” Have the pendant answer from both my Mac and my authenticated browser, not just summarize whichever screen is open."
- **useful because:** Today the owner must manually inspect local files, apps, and signed-in web workspaces and mentally compare them with an earlier point. A persistent, source-linked baseline lets a worn-device question produce a trustworthy delta: new/removed/modified artifacts, changed statuses, and only the consequential items, with uncertainty called out.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement
- **model tier:** Use relay-realtime only to capture the short question and speak the result; use a cheaper background model for normalization, cross-source diffing, and ranking. Mac-planner/mac-vision collect local evidence, browser-extension reads the owner's already-authenticated tabs, faculty-perception establishes typed facts, and faculty-judgement ranks significance.
- **latency:** A first spoken acknowledgement under 500 ms; return a useful partial result in 5–10 s and continue filling in slower browser/local comparisons without losing the conversation. Baseline creation may take up to 30 s.
- **cost:** Roughly $0.02–$0.10 per comparison depending on changed-document count; the dominant cost is background model context for semantic diffs, not the relay utterance.
- **security:** Only use explicitly paired Mac and existing browser sessions; do not log document contents or send unchanged data. Store hashes, timestamps, source identifiers, and compact fact summaries by default, with encrypted opt-in excerpts. The answer must cite its source and say when a source was unavailable; no destructive action is implied.
- **missing:** A durable per-project baseline store with immutable snapshot ids and content hashes; Mac and browser collectors that emit the same typed artifact/status schema and tolerate unavailable surfaces; A cross-surface semantic-diff and importance-ranking worker; A relay response stream that can speak an initial partial answer and later corrections; A user-visible way to name, reset, or compare against a baseline from the pendant

### "“Did that actually take effect?” After you act on my Mac or in a signed-in browser, verify the resulting world state and tell me what changed—not merely that a command returned success."
- **useful because:** A successful tool response can mean only that keystrokes or an API request completed; the owner still cannot know whether the right account, tab, file, or record changed. Closed-loop verification catches wrong-tab actions, stale pages, partial saves, and silent application failures while the owner is away from the Mac.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-action
- **model tier:** Use the realtime model only for the spoken request and concise status. Have faculty-action attach a verification recipe to each planned action; faculty-perception runs the cheap typed checks and escalates ambiguous visual comparison to mac-vision. Use a slower background model only for semantic interpretation of before/after evidence.
- **latency:** Speak receipt immediately, then provide verified/unverified status within 2–8 s; for slow web saves, poll with bounded backoff and say that verification is pending rather than blocking the voice turn.
- **cost:** About $0.005–$0.04 per action bundle; most checks are deterministic reads, with model cost only for ambiguous UI or semantic before/after comparison.
- **security:** Verification reads may expose more data than the mutation. Scope each check to the target record/window, avoid retaining screenshots or page bodies, redact secrets, and include before/after citations. Never claim success from absence of an error alone.
- **missing:** A typed action-plus-verification contract (target identity, expected postcondition, timeout, and evidence query); Mac/browser readback adapters that can query the same target after mutation; A state-comparison result type distinguishing confirmed, contradicted, pending, and unverifiable; Relay support for a later verification update tied to the original job and spoken request


## Changes it proposed to its own stack

### `memory` — Build a cross-surface Evidence Ledger between the existing pipeline, Mac planner, and browser routes. Each collection run writes an immutable snapshot manifest (project key, source, item id, hash/last-modified, compact typed facts, citation locator, availability, and redaction class); a background diff worker compares the new manifest with the owner-selected prior snapshot and emits additions, removals, semantic changes, and confidence. Keep raw page/file bodies ephemeral unless explicitly requested.
- **owner gets:** The owner can ask one natural question and hear what materially changed since a known point, instead of reopening every app and reconstructing history by hand. It remains useful when one surface is offline because the answer identifies exactly which evidence is missing rather than silently pretending nothing changed.
- effort: Medium-high: schema and encrypted storage, collectors/adapters for Mac and browser, semantic diff worker, citation format, and relay partial-result streaming. Start with one local project folder plus one authenticated browser session, then generalize.  ·  risk: False semantic changes or missed changes could mislead the owner; every claim should carry source, snapshot time, and confidence, with a verbatim-diff fallback. A corrupt baseline must be recoverable by immutable snapshot deletion/rebuild. Browser or file contents could leak if raw payloads are retained, so default to hashes/facts and short TTLs for excerpts.
- cost: Storage is small for manifests but model cost grows with changed facts; approximately $0.01–$0.08 per comparison using a background model, plus one-time engineering cost. No new hardware required.  ·  latency: No impact on ordinary voice turns. Collection acknowledgement can be immediate; comparison typically adds 5–10 seconds, with partial spoken results streamed first.
- security: Adds a sensitive cross-surface memory store. Encrypt at rest, scope keys by owner/project, redact secrets and tokens at ingestion, retain audit receipts, and never copy authenticated session cookies or full documents into the ledger.
- depends on: A typed common evidence schema shared by Mac and browser collectors; A durable encrypted snapshot store and background worker (not a scheduler assumption); A relay response-stream/late-update path from pipeline events; Per-project baseline naming and reset semantics

### `integration` — Add postcondition-aware closed-loop verification to every executable action. The planner must emit an action target fingerprint and a bounded read-only verification recipe; Mac and browser executors run it after completion and return typed confirmed/contradicted/pending/unverifiable evidence linked to the original job and receipt. The relay speaks the immediate execution receipt, then pushes a correction or confirmation when verification finishes.
- **owner gets:** The owner gets an honest answer about whether the intended thing happened, even when away from the Mac, instead of trusting a green tool response that may have acted on the wrong tab or failed to save.
- effort: Medium: extend planner output and receipt schemas, implement deterministic readback for common actions (open, type, reminder, browser click/form submit), add bounded polling and an event-to-voice correlation id.  ·  risk: A verification read can race with delayed app saves or misidentify a similar target. Use explicit target fingerprints, timeouts, and an unverifiable result; never silently downgrade unverifiable to success. Existing action execution remains unchanged if no recipe is available.
- cost: Low ongoing API cost because most checks are deterministic; occasional vision/semantic checks add roughly $0.01 per ambiguous action. No hardware cost.  ·  latency: Immediate acknowledgements remain unchanged; verified outcomes arrive asynchronously, usually within seconds, with no need for the owner to ask again.
- security: Readback must be least-data: query only the target and retain compact evidence, not whole screenshots/documents. Preserve audit links so the owner can inspect why a result was declared confirmed.
- depends on: A common postcondition schema emitted by /plan and consumed by /execute; Mac/browser readback adapters; Job event correlation from execution receipts to /pipeline/events and pendant speech


## What it asked for

_Nothing._
## Its own summary

Recorded three non-backlog proposals: (1) a cross-surface project-change answer using persistent evidence baselines, (2) the encrypted Evidence Ledger and semantic-diff integration needed between existing pipeline/Mac/browser routes, and (3) closed-loop postcondition verification so action receipts reflect the resulting world state rather than command acceptance. The owner currently cannot have any of these reliably while away from the Mac.

**Biggest unknown:** Which Mac and browser data sources the owner wants included in the first project baseline, and the exact retention/redaction policy for their evidence summaries. No further discovery was performed this round, per instruction.

