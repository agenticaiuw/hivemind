# Harness derivation — mac-terminal — round 209

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “pick this up on my Mac,” carry the current conversation to the Mac, open the relevant browser/session and project, and let me continue there without repeating myself."
- **useful because:** The pendant is excellent for capturing intent while moving, while the Mac and browser are the only surfaces that can expose the owner's authenticated work. This creates a genuine handoff instead of another isolated voice command: the exact turn, provenance, active project, and browser session travel together, and the Mac reports back when the handoff is actually ready.
- **path:** pendant → relay-realtime → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime only parses the short handoff utterance and confirms the target; a cheaper background model compacts the turn and selects a project/session. The Mac planner and browser harness perform deterministic open/focus/read actions; realtime speaks readiness or failure.
- **latency:** Acknowledge on the pendant in under 500 ms; Mac/browser preparation may take 2–8 s and must return a truthful ready/failed state rather than pretending the handoff happened.
- **cost:** About $0.002–$0.01 per handoff depending on compaction; browser and Mac calls dominate latency, not tokens.
- **security:** The handoff may include sensitive browser URLs, page titles, and a short transcript. Keep it on the relay/Mac, never send page contents to the model unless needed; require explicit confirmation before submitting forms or mutating a page. Expire the handoff bundle after completion or 24 hours.
- **missing:** A durable cross-surface handoff bundle joining turn ID, project, browser session, and readiness state; A Mac wake/prepare action that can focus the selected project and browser tab and emit a completion event; A relay-to-pendant completion event carrying the handoff ID, not just a generic job result

### "Tell me when a browser download has finished, whether it looks like a real document or a partial/installer file, and where it came from; if I say “keep it,” organize it into the active project."
- **useful because:** Today a download silently lands in ~/Downloads and the owner must manually inspect it. The browser knows the originating authenticated page, while the Mac can distinguish partial downloads, installers, screenshots, and duplicates. The pendant can deliver a short alert without opening a microphone or requiring the owner to hunt through Safari.
- **path:** browser-extension → mac-planner → relay → pendant → dashboard
- **model tier:** No realtime generation for detection: browser and Mac emit structured events, and a small background model classifies only ambiguous filenames/types. Realtime is used only if the owner asks for a spoken explanation or organization command.
- **latency:** Detect within 2 seconds of a completed download; classify and alert within 5 seconds. Organization runs only after the owner's explicit “keep it” instruction.
- **cost:** Near-zero for ordinary files using metadata and hashes; under $0.001 for ambiguous classification. Hashing large files is the main local cost.
- **security:** Never upload file bytes by default. Keep source URL, title, filename, size, hash, and download status on the Mac; redact query strings and authentication tokens from URLs. Moving a file is reversible only if the original path is retained. Require confirmation for delete/overwrite.
- **missing:** A browser download-completed event with source-tab provenance and a stable download ID; A Mac watcher that correlates the browser event with /sweep/survey and emits a typed classification; A relay event and pendant inbox item for the alert, with deduplication across reconnects; An explicit keep/organize operation that records the original path and project destination

### "When I reconnect, let me ask “what happened while I was away?” and hear only new, actionable outcomes from my Mac jobs, watched browser pages, and reminders, with a way to say “open that” on the Mac."
- **useful because:** The owner currently gets disconnected pieces: a job record, a browser watch, or a reminder, but no causal catch-up. A relay that remembers the last acknowledged point can turn an offline interval into one concise spoken queue, and the Mac/browser can immediately open the selected item instead of making the owner search for it.
- **path:** relay → pendant → mac-planner → browser-extension → dashboard
- **model tier:** A cheap background ranker groups and prioritizes event records; realtime only handles the short question, item selection, and spoken answer. Opening the selected item is deterministic Mac/browser work.
- **latency:** Return a first five-item digest in under 2 seconds from relay-held records; opening an item can take 2–6 seconds and must report the actual destination.
- **cost:** <$0.005 per catch-up in the common case; summarization tokens dominate, while event retrieval is local.
- **security:** The digest can expose sensitive filenames, URLs, and reminder text over audio. Speak only titles and minimal summaries, require a follow-up for details, and bind “open that” to the selected event ID rather than a fuzzy title. Expire or acknowledge entries atomically so reconnects do not repeat them.
- **missing:** A durable per-surface cursor recording the last event acknowledged by the owner; A normalized event envelope linking job IDs, browser provenance IDs, reminder IDs, and delivery state; Relay-side ranking/deduplication across offline inbox, jobs, and page-watch events; A pendant command that selects an item from the spoken digest and a Mac/browser resolver that opens its recorded target

### "If I ask “why did you do that?” or “put it back,” explain the whole chain from my pendant words through the relay, Mac, and browser, then restore the exact prior state when that is possible."
- **useful because:** Today the owner can see isolated job, browser, and action records, but cannot understand one end-to-end decision or recover it as a single event. A causal explanation and cross-surface rewind would make delegation trustworthy: it would identify the source utterance, pages and data used, exact Mac/browser mutations, and distinguish a true undo from an irreversible step.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard → unified
- **model tier:** Use a cheap background process to assemble the causal graph and classify reversibility. Realtime only answers the short why/undo request and asks for clarification when multiple reversible branches exist; deterministic adapters perform restoration.
- **latency:** Explain in under 2 seconds from durable records; begin reversible restoration within 1 second and report each completed or impossible step as it happens.
- **cost:** <$0.01 per explanation; restoration is mostly local record lookup and Mac/browser calls. Token cost is dominated by summarizing a large causal chain, so send only the selected subgraph.
- **security:** The graph may contain private URLs, transcripts, filenames, and form values. Keep raw values on the originating device, send redacted summaries to the model, and make irreversible steps explicitly report “cannot undo” rather than fabricate success. Restoration must be idempotent and bound to the original action IDs to avoid replaying a different page state.
- **missing:** A cross-node causal event protocol that carries one immutable intent ID from pendant turn through relay planning, Mac execution, browser commands, and outcome; A durable graph join between job IDs, action receipt IDs, browser provenance/command IDs, and before/after state snapshots; Per-action compensators for browser and Mac mutations, with an honest irreversible marker and idempotency key; A pendant query/selection flow for choosing one chain when several actions happened close together

### "Let me say “make this a private room” and have the pendant, Mac, and browser coordinate privacy immediately: stop spoken output, hide or lock sensitive browser content, and restore the previous working state when I say “resume.”"
- **useful because:** A person wearing the pendant cannot reliably protect a screen or spoken response when someone walks up. No single node knows enough: the pendant knows the owner's immediate intent, the Mac controls display/audio, and the browser owns authenticated tabs. Coordinating them gives the owner a fast, reversible privacy mode instead of manually closing work.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime classifies only the two short commands; all changes are deterministic: mute/duck audio, hide or lock selected windows, suspend browser observation, and restore recorded state. No background model is needed.
- **latency:** Visible/audio privacy changes within 300 ms of the button-confirmed command; restoration within 1 second. If one surface is unreachable, the pendant must say which protection did and did not happen.
- **cost:** Near-zero model cost; local Mac/browser operations dominate and can run in parallel.
- **security:** The system must fail closed for spoken sensitive content but never claim the screen is private if the Mac/browser did not acknowledge. Save only encrypted pre-state (focused app, window visibility, volume, tab visibility), expire it after restoration, and keep this distinct from an irreversible lock or logout.
- **missing:** A coordinated privacy-session state machine with acknowledgements from pendant, Mac, and browser; Mac actions to snapshot/restore focused-window visibility and audio output without losing work; A browser command to hide or freeze authenticated tab content and stop page-watch delivery; A local pendant confirmation and timeout rule that reports partial protection truthfully


## Changes it proposed to its own stack

### `integration` — Introduce an immutable end-to-end intent envelope and causal graph: every pendant turn receives an intent_id; relay plans, Mac jobs, browser commands, receipts, provenance records, and before/after snapshots reference it. Persist only redacted metadata centrally while retaining sensitive payloads at the originating surface. Add a graph query that can select one intent and enumerate its exact descendants and compensators.
- **owner gets:** The owner gets one answer to “what happened?” instead of hunting through unrelated Mac jobs and browser records, and can ask for a specific action chain to be restored without accidentally undoing neighboring work.
- effort: Medium-high: schema and propagation changes across relay, local-agent execute/journal, browser command/result, and dashboard; implement a compact durable graph with retention and redaction.  ·  risk: Missing one propagation edge would produce an incomplete explanation; mark chains incomplete rather than silently implying completeness. Graph corruption should not affect execution, and old records need a legacy/unknown node type.
- cost: Low storage overhead for hashes, IDs, timestamps, and state summaries; no recurring model cost unless the owner requests an explanation.  ·  latency: Negligible on execution; graph writes are append-only and can be batched, while explanation lookup should be sub-second.
- security: Improves auditability but centralizes metadata. Encrypt sensitive edge payloads locally, hash or redact URLs/form values, restrict graph queries to the owner token, and enforce retention.
- depends on: A durable browser provenance/trace API with stable command IDs; Mac receipts that preserve exit status, effective command identity, and before/after state; Relay event delivery that preserves intent_id across reconnects


## What it asked for

_Nothing._
## Its own summary

Three new cross-surface capabilities were recorded: (1) a spoken “pick this up on my Mac” handoff joining the pendant turn, active project, and authenticated browser session; (2) provenance-aware browser download alerts that classify incomplete/installer/duplicate files locally and organize only after “keep it”; and (3) an offline catch-up question that deduplicates new Mac jobs, browser watches, and reminders and opens a selected item on the Mac. I also verified the granted USB serial diagnostic schema is still unresolved in the live inventory, so it cannot inspect the physically connected nRF9160/ESP32 this round.

**Biggest unknown:** Whether relay already has durable per-owner event cursors and acknowledgement semantics, and whether the browser extension emits download-completed events with source-tab provenance. Those determine how much of the three proposals is genuinely missing rather than connective wiring.

