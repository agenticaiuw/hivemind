# Harness derivation — unified — round 196

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I ask 'what needs my attention?', give me one short spoken answer containing only items that are still actionable, with the source and freshness checked across my Mac, browser, pendant inbox, and relay jobs."
- **useful because:** The owner currently gets scattered reminders, browser failures, queued alerts, and completed routines with no single trustworthy attention list. This turns the hive into an attention filter rather than another notification stream, while refusing stale or already-settled evidence.
- **path:** relay → pendant → mac-bridge → browser → dashboard
- **model tier:** background for collection and deterministic deduplication; realtime only to phrase the final one-sentence answer
- **latency:** Under 3 seconds when asked; background refresh may take 30-90 seconds
- **cost:** Usually <$0.01 per refresh; dominated by one small background synthesis, not realtime inference
- **security:** Only explicitly bound browser tabs and Mac job/routine records; redact message contents by default. Never send, delete, buy, or alter a task without confirmation.
- **missing:** A typed attention-item schema with source, observedAt, expiresAt, actionability, and evidence link; A cross-surface deduplicator that marks completion rather than merely counting records; A pendant inbox payload for a compact attention digest and acknowledgement state

### "Tell me whether the system is ready for a private conversation right now, and if not, say exactly which surface is still listening, recording, queued, or exposed."
- **useful because:** The privacy latch and convergence check can establish local mute, but the owner needs a plain-language preflight before speaking in a sensitive setting. A single answer spanning pendant capture/playback, relay persistence, Mac jobs, and browser exposure is a capability no node can honestly provide alone.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic checks first; realtime only for the short spoken verdict
- **latency:** Under 1 second for the normal path; under 3 seconds if a diagnostic snapshot is needed
- **cost:** Near-zero model cost; one compact synthesis only when any check is ambiguous
- **security:** Default-deny: unknown state yields NOT PRIVATE. Do not include captured words, URLs, or secrets in the spoken result. Require a physical latch action to change state, never a voice command.
- **missing:** A signed privacy preflight receipt that binds latch state, capture state, relay queues, Mac capture jobs, and browser exposure to one timestamp; A policy for what 'browser exposed' means (active tab only versus all bound sessions); A pendant-local red/green/unknown indicator distinct from ordinary inbox LED meanings

### "Show me the things you inferred about me that you are remembering, one at a time, and let me say 'forget that' to erase that fact, its derived copies, and its source evidence everywhere you can reach."
- **useful because:** The owner explicitly cannot see extracted facts today, yet those facts shape future answers. This gives them a recognizable review-and-erase interaction instead of asking them to trust an invisible memory store. It respects the rule that action history remains auditable while inferred personal facts are removable.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic retrieval, binding, and deletion planning; realtime only to present one fact and interpret the owner's short confirmation
- **latency:** First item under 2 seconds; each erase receipt under 5 seconds, with off-machine replication reported as pending rather than falsely complete
- **cost:** <$0.01 per item review; dominated by no model work, with one short realtime turn only if wording is ambiguous
- **security:** Require physical transaction approval for deletion of a fact and its evidence capsule, never rely on voice identity alone. Redact secret facts until the owner explicitly opens one. Keep job history and action receipts untouched. Every deletion needs an append-only receipt and a list of replicas still pending.
- **missing:** A typed fact lineage record linking each extracted fact to source evidence and every derived copy; A read-only review route that returns human-recognizable fact text plus provenance without exposing unrelated secrets; An idempotent erase operation spanning local facts, context graph, relay replicas, and evidence capsules with pending replication status; A pendant inbox/card payload for review prompts when the owner is next in conversation

### "When I say “use this site,” have the pendant read back the exact site identity, account, amount, and irreversible consequence before I approve it physically, then show me a receipt that the browser acted on that exact page and nothing else."
- **useful because:** The owner can authorize sensitive browser actions today only through a general approval concept; they cannot hear a compact, cryptographically bound description of the browser target before committing. This makes the wearable a trustworthy last-look channel for actions the browser alone can execute but cannot safely summarize.
- **path:** pendant → browser-extension → relay → mac-planner → dashboard
- **model tier:** deterministic extraction and page binding; realtime only to read the short preview and receipt
- **latency:** 3 seconds for preview, 5 seconds for post-action receipt
- **cost:** <$0.02 per invocation; page extraction and receipt hashing dominate, not model tokens
- **security:** Never transmit page secrets to the pendant; speak only allowlisted fields. Bind approval to tab/session URL, DOM snapshot hash, account label, amount, and expiry. Require physical_transaction_approval_latch; reject navigation or DOM changes.
- **missing:** A browser-side immutable target snapshot and field allowlist; A relay record that binds the physical approval nonce to the browser command and resulting receipt; A receipt verifier that distinguishes page navigation from successful business completion

### "Let me ask “what changed since I left?” and hear only verified changes across my Mac files, browser sessions, scheduled routines, and pendant state, with each item labeled new, changed, or unchanged since the last check."
- **useful because:** The owner currently has many surfaces that can drift while they are away, but no single time-bounded change feed. This gives them a reliable re-entry point after sleep, travel, or a lost link without replaying stale history or exposing raw private content.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** background snapshot/diff engine; realtime only to compress the verified diff into speech
- **latency:** Under 4 seconds on demand; snapshots can be maintained asynchronously
- **cost:** <$0.01 per check; hashing and metadata comparison dominate
- **security:** Store hashes and metadata by default, not file contents or page text. Bind browser diffs to explicitly selected sessions. Treat inaccessible or stale surfaces as unknown, never unchanged. Require confirmation before opening or mutating a changed item.
- **missing:** A durable cross-surface baseline with owner acknowledgement checkpoints; Typed diff events for files, tabs, routines, pendant inbox/state, and relay jobs; A redaction policy for names, URLs, and filenames in spoken summaries


## Changes it proposed to its own stack

### `hardware` — Add a tiny fuel-gauge IC with a thermistor input to the eventual wearable pendant, expose signed battery percentage, voltage, temperature, charging state, and estimated time-to-empty over the existing telemetry envelope, and have the relay/mac surfaces retain only the latest value plus bounded history.
- **owner gets:** When the owner asks 'what is the battery percentage?', the system can answer about the device they are wearing rather than guessing from Mac state or admitting that the prototype has no gauge. It also prevents a surprise dead pendant during a conversation.
- effort: Hardware respin and board-layout work; firmware I2C driver and calibration; relay schema and Mac/pendant display integration. Prototype on the DK with an external gauge before committing the wearable PCB.  ·  risk: Gauge drift, thermistor failure, or stale telemetry could mislead the owner. Every reading must carry age and validity; stale or absent data must be spoken as unknown. Recover by falling back to voltage plus last-known timestamp and never fabricating a percentage.
- cost: Roughly $1-3 BOM and sub-mA measurement draw, plus PCB area; exact choice depends on the eventual battery chemistry and enclosure.  ·  latency: No meaningful conversation latency; telemetry can sample every 30-60 seconds and immediately on charge/discharge transitions.
- security: Battery telemetry is low sensitivity but should be authenticated so a forged low-battery event cannot trigger needless behavior. Do not export raw location or infer where the owner is.
- depends on: Owner must choose the eventual battery chemistry and product constraints; the current nRF9160 DK has no fuel gauge and is not the wearable design.; Define a typed telemetry envelope and freshness semantics across relay and Mac.; Do not treat America/New_York or any other Mac timezone as a pendant location.

### `interaction` — Add a two-channel 'explain before act' contract: every multi-surface action must produce a compact pendant preview with target, scope, and consequence, and a machine-verifiable postcondition receipt; if the postcondition cannot be observed, the system must say 'submitted, outcome unknown' rather than claiming success.
- **owner gets:** The owner would stop hearing confident completion claims when a browser, relay, or Mac action only submitted a request. They would know exactly what will happen before approval and exactly what was physically verified afterward.
- effort: Define a shared preview/postcondition schema, thread it through planner, relay, browser extension, Mac executor, and pendant speech, then add negative tests for stale pages, lost links, and ambiguous receipts.  ·  risk: Extra previews may feel slow and some actions lack observable postconditions. Recover by classifying actions as verified, submitted-unknown, or not-started and letting the owner opt into terse previews for low-risk actions.
- cost: Negligible runtime cost; one small structured record per action and occasional low-tier summarization.  ·  latency: Adds roughly 0.5-2 seconds before high-risk actions; no delay for already-safe reads.
- security: Improves least privilege and auditability, but previews must exclude secrets and receipts must not become a new sensitive content store.
- depends on: A shared typed action contract across browser, Mac, relay, and pendant; Physical approval nonce binding for high-risk actions; Per-action postcondition probes rather than generic HTTP success


## What it asked for

_Nothing._
## Its own summary

This round I recorded three owner-facing capabilities: a cross-surface actionable-attention answer, a default-deny private-conversation preflight, and owner-visible fact review/erasure with lineage and off-machine pending receipts. I also recorded a hardware change for a real pendant fuel gauge; the current DK has no gauge, so battery percentage cannot be answered honestly. The recorder flagged the first two as near existing attention/privacy ideas, so the genuinely new parts are the actionability/freshness deduplication and the signed, default-deny preflight contract—not another queue or latch.

**Biggest unknown:** I still need the owner's product decisions for the eventual wearable battery chemistry, talk/standby time, size/thermal limits, and whether 'browser exposed' means active tabs only or every bound session. Engineering-wise, the next missing pieces are typed fact lineage/erase routes, a signed privacy preflight receipt, and a telemetry envelope with age/validity; I do not need Accessibility or Screen Recording permissions to define these.

