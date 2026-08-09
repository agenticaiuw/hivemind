# Harness derivation — unified — round 221

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What have you inferred about me that I never explicitly asked you to remember? Show me the source, let me delete one item everywhere, and prove when it is gone.”"
- **useful because:** This directly fixes the owner's stated retention defect: extracted facts are currently invisible and cannot be individually erased. It makes memory something the owner can inspect and control rather than a hidden side effect.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** deterministic for listing, provenance matching, deletion receipts, and replication state; realtime only to explain the result conversationally
- **latency:** List under 1 s from the Mac graph; deletion receipt under 2 s locally, with off-machine replication explicitly marked pending until acknowledged
- **cost:** <$0.01 per request; dominated by one short conversational response, not reasoning
- **security:** Return only facts belonging to this owner and redact unrelated job history. Deletion must require an exact fact selection or physical approval for ambiguous matches; erase the fact, derived graph copies, evidence capsule, and relay replicas, but retain action audit history. Never claim remote deletion complete before relay acknowledgement.
- **missing:** A provenance-preserving fact inventory route over facts.json/context graph; A single erase transaction spanning local derived copies and relay D1/R2 replicas; Dashboard and pendant-friendly confirmation/readback of the exact fact and deletion state

### "“Find the document or page I was looking at about [topic], even if it is in a browser tab, Mail, Notes, or a file, and give me the exact place to open it.”"
- **useful because:** The wearable can hear the request but cannot see the owner's scattered digital context. A unified, citation-first retrieval action turns the Mac and authenticated browser into one searchable memory without asking the owner to remember which app held it.
- **path:** pendant → mac-planner → browser-extension → relay-realtime
- **model tier:** background planner for candidate retrieval and ranking; deterministic extractors for titles, URLs, paths, timestamps, and quoted evidence; realtime only for the spoken answer
- **latency:** Return first candidates in 3 s and refine in the background within 15 s; never block conversation on a full-disk search
- **cost:** $0.01–$0.04 per search; browser/Mac enumeration dominates, with one small ranking pass
- **security:** Search only explicitly bound browser tabs/apps and owner-selected locations; do not upload page contents or mail bodies to the relay/model by default. Show source, access time, and why each result matched. Opening a result is reversible; sending, moving, or sharing anything requires separate confirmation.
- **missing:** A read-only Mac file/mail/notes search action with structured citations that works without Accessibility; A browser snapshot/index endpoint that returns tab identity, title, URL, and permitted text snippets; A cross-surface result object with stable source IDs and expiration so spoken citations remain accurate

### "“Why did you do that, what exactly changed, and can I undo just that part?”"
- **useful because:** Today the system can execute Mac and browser work, but the owner has to know which job ID to inspect and receipts are fragmented. A spoken, step-level explanation with evidence and a safe undo choice makes delegated action trustworthy in daily use.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** deterministic join of ledger, receipts, browser results, and undo eligibility; a cheap planner groups steps; realtime only summarizes aloud
- **latency:** Answer in 1–2 s for a recent job; retrieve older evidence in under 5 s. Never execute undo in the explanation step.
- **cost:** <$0.01 per query; mostly local reads and one concise summary
- **security:** Bind the answer to the authenticated owner and exact job/step provenance. Distinguish observed state from the agent's claim, report missing evidence, and never imply browser or shell actions are undoable when they are not. Undo must be a separately confirmed operation and preserve the audit trail.
- **missing:** A stable cross-surface receipt join keyed by job/step rather than ad-hoc IDs; Structured before/after state for browser commands and shell actions, including exit status and target identity; A step-level undo endpoint that refuses unsupported or stale operations instead of offering whole-job guesses

### "“Pick up where I left off.”"
- **useful because:** The owner should be able to resume a project conversationally after a crash, sleep, or switching machines without replaying old actions. The system would reconstruct the last active work context—open browser work, project, unfinished drafts, pending decisions, and the last verified state—then ask what to do next.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** background model to assemble and rank context; deterministic workbench and receipt readers for state; realtime only for the concise spoken handoff
- **latency:** Initial handoff in 2 seconds from cached state; refresh browser/Mac evidence within 10 seconds without executing anything
- **cost:** $0.01–$0.03 per handoff; dominated by one context synthesis
- **security:** This must be context rehydration, never action replay. Show stale or missing evidence explicitly, exclude private tabs/apps unless previously bound, and require confirmation before opening or modifying anything.
- **missing:** A durable cross-surface context pack with last-known browser, project, and workbench state; A distinction between conversational continuation and executable action resumption; Owner-selectable project/tab bindings and expiry for stale context

### "“Read this page to me, and tomorrow continue from where you stopped.”"
- **useful because:** The owner can currently ask for browser work and separately receive audio, but cannot turn a long authenticated page into a durable, hands-free reading session. A resumable reading position would make the pendant useful while walking or working away from the screen.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** deterministic page extraction and paragraph position tracking; background model only for navigation or inaccessible-page explanation; realtime for TTS streaming
- **latency:** Begin speaking within 2 seconds of a bound page snapshot; pause/resume acknowledgement under 500 ms; persist position before each paragraph batch
- **cost:** $0.01–$0.05 per session, mostly TTS/audio processing; no model call for plain text pages
- **security:** Read only the explicitly selected tab and never expose page contents to the relay/model unnecessarily. Bind the bookmark to URL, tab/session identity, content hash, and owner; invalidate it when content changes materially. Do not follow links or submit forms without confirmation.
- **missing:** A browser action that returns stable, permission-scoped text segments and content hashes; A durable reading-session bookmark tied to page version and paragraph/character range; A pendant playback control for pause, resume, skip, and report-position events

### "“For the next hour, keep this conversation and anything I ask about it on this Mac; do not send it to the relay or expose it to browser pages.”"
- **useful because:** The owner needs a practical data-boundary mode, not only an emergency microphone mute. It would let them use local Mac automation and private notes while making a clear, time-limited promise that conversation content and derived context do not leave the machine.
- **path:** pendant → mac-planner → relay-realtime → browser-extension → dashboard
- **model tier:** deterministic policy enforcement and routing; no model should override the boundary; local Mac model/planner handles allowed work
- **latency:** Boundary acknowledgement under 300 ms; enforcement must happen before capture forwarding, persistence, browser injection, or relay dispatch
- **cost:** Near-zero incremental API cost; modest local state and audit receipts
- **security:** Fail closed if the policy state cannot be verified. Show remaining duration and affected surfaces. Prevent queued relay jobs, browser commands, extracted-memory writes, and cloud audio uploads during the window; retain only a minimal local audit record. Expiry must be explicit and safe, not silently extended.
- **missing:** A signed policy envelope understood by pendant, relay, Mac, and browser bridge; A relay admission check that rejects locally-scoped audio, jobs, and memory writes; A local-only conversation/planner path and a convergence receipt proving no prohibited surface received data


## Changes it proposed to its own stack

### `integration` — Make every delegated Mac/browser action emit a signed, step-level receipt with jobId, actionId, target identity, start/end timestamps, exit/status code, redacted parameters, before-state hash, after-state hash, and explicit undoability; add a join index consumed by the relay so a spoken query can resolve a step without knowing its internal ID.
- **owner gets:** When the pendant says it changed something, the owner can immediately know what, where, whether it actually succeeded, and whether only that change can be undone—rather than trusting a vague “done.”
- effort: Medium: extend action ledger/receipt schemas, browser result persistence, and relay read models; add migration and contract tests.  ·  risk: Receipts could leak sensitive URLs, text, or file names; redact parameters and encrypt relay fields. Hashes may be unavailable for volatile UI state, so report unknown rather than fabricate. Existing jobs need a versioned compatibility path.
- cost: Negligible storage growth if bounded and redacted; roughly 1–3 KB per action, with relay retention limits. No model cost on write.  ·  latency: Under 50 ms local write overhead; cross-surface explanation reads may add 100–500 ms.
- security: Improves auditability but creates a higher-value metadata store; bind receipts to owner/session, minimize content, and retain action history separately from user-memory deletion.
- depends on: A stable actionId on every executor and browser command; Structured exit/status capture for /execute and browser results; A versioned relay receipt index and owner-authenticated read route


## What it asked for

_Nothing._
