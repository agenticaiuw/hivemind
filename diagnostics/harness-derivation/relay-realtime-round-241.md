# Harness derivation — relay-realtime — round 241

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Tell me what’s happening right now with my devices and connection.”"
- **useful because:** When speech feels glitchy or a command seems slow, the owner needs a quick, trustworthy status snapshot without digging into logs.
- **path:** pendant → relay-realtime → mac-planner
- **model tier:** Realtime (relay) for the spoken summary; Mac only if a live check is needed.
- **latency:** 1-2 seconds for a basic snapshot; deeper diagnostics can take longer but should be announced.
- **cost:** Low. Prefer cached relay/device health signals and only query the Mac when necessary.
- **security:** Status may reveal identifiers and environment details. Keep it minimal and avoid serial numbers or sensitive network info unless explicitly asked.
- **missing:** A single consolidated health endpoint for relay-visible device and link state (USB, audio bridge, pendant, Mac agent).; Standardized fields for audio pipeline health, packet loss, and last error.; Permissions to read any additional state not already exposed via /v1/state/* or /v1/ops/*.

### "“Summarize what changed since the last time I asked.”"
- **useful because:** This reduces cognitive load. The owner gets a concise delta instead of a full re-briefing, which is perfect for a wearable voice interface.
- **path:** relay-realtime → mac-planner → browser-extension
- **model tier:** Cheaper background tier to compute and store deltas; realtime only to speak them.
- **latency:** Under 2 seconds to speak a short summary once the delta is prepared.
- **cost:** Moderate if it requires reading many sources; keep it bounded with watched sources and sampling.
- **security:** Changes may include sensitive content (mail, files, tabs). Require explicit scope and confirmation for sensitive sources.
- **missing:** A cross-surface change journal keyed by source (mail/files/browser/jobs).; A diffing format that is stable enough to store and replay.; A user-level preference for verbosity and scope.

### "“Warn me, through the pendant, when I am about to make a consequential mistake on the Mac—but never block me.” The warning should understand that I am composing an email, editing code, buying something in a browser, or deleting a file, and explain the specific mismatch with my stated project or preferences."
- **useful because:** The pendant is the one surface that can interrupt attention while the Mac is in front of the owner. This turns the system from a passive executor into a second pair of eyes without imposing the rejected confirmation-gate policy. It could catch an accidental production edit, an email to the wrong person, or a purchase that conflicts with a remembered constraint.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime relay for a one-sentence alert; a cheap background model on the Mac for continuous local classification and comparison against projected memory. Escalate only ambiguous/high-impact observations to the planner.
- **latency:** Under 500 ms from a Mac event to an alert when possible; otherwise batch at natural UI boundaries (field blur, navigation, save). Never speak more than one alert per cooldown window unless the owner presses for detail.
- **cost:** Usually near-zero incremental API cost with local event classification; roughly $0.001–$0.01 per escalated reasoning check. The dominant cost is vision/model calls for screenshots, so use accessibility metadata and DOM text first.
- **security:** Screen text, browser content, and drafts may leave the Mac only for an escalated check. Default to local redaction of secrets and credentials. Alerts are advisory and must not silently alter, block, or send anything.
- **missing:** A Mac event stream for active-app/accessibility/DOM changes rather than only request/response actions; A durable, debounced policy evaluator joining current UI evidence with memory projection; A relay-to-pendant alert path that is actually implemented (the existing inbox shape is the right destination); A Mac vision fallback for UI states with no useful accessibility metadata

### "“Find the thing I saw before—search my authenticated browser history, open tabs, Mac files, and voice notes, then tell me where it came from and reopen the exact source.” I should be able to describe it approximately (“the paper about the battery test from last month”), and the pendant should speak a ranked answer with a citation, not pretend a fuzzy match is certain."
- **useful because:** Today each surface knows only its own slice, so the owner must remember whether an item was in Safari, a local file, or a prior conversation. A provenance-preserving federated search would recover lost work while keeping uncertainty explicit and would work especially well when the owner is away from the desk and only has the pendant.
- **path:** pendant → relay → mac-planner → browser-extension → mac-terminal → dashboard
- **model tier:** Cheap retrieval/reranking on the Mac and relay; use the expensive realtime model only to resolve the spoken description and summarize the top result. Do not send full corpora to the realtime tier.
- **latency:** Speak an initial top match in 2 seconds, then optionally refine. A slow authenticated-browser search may return as an inbox update rather than holding the voice turn.
- **cost:** A local index makes ordinary queries <$0.001; occasional embedding/index refresh and one concise synthesis are the dominant costs, roughly $0.002–$0.02 per query.
- **security:** Browser history, private pages, files, and voice transcripts are sensitive. Index and search locally on the Mac; return only the selected snippets and URLs. Respect per-source sensitivity and never expose a private result merely because its text matches a public query.
- **missing:** A unified local index over browser history/tabs, files, memory facts, and voice-run transcripts with stable provenance IDs; Browser-extension access to history and authenticated page metadata, not only active-page commands; A search route that can query the Mac while the owner is away and return ranked evidence; A compact pendant spoken-result protocol supporting citation, confidence, and “open this” follow-up

### "“Before you change anything, rehearse the whole operation against a disposable copy and tell me exactly what would happen.” For a code change, use a temporary git worktree and test it; for a browser workflow, use a preview/draft path where available; for a file operation, use a snapshot. Let me say “apply that rehearsal” from the pendant to commit the already-reviewed result."
- **useful because:** The owner wants maximum access and does not want needless permission prompts, but a spoken preview is valuable when an operation has broad or irreversible consequences. This gives them confidence without turning the system into a confirmation gate for ordinary reversible actions, and it makes multi-step Mac/browser automation inspectable before it touches real state.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension → dashboard
- **model tier:** Use the Mac planner and local shell for deterministic cloning, snapshots, dry-runs, and tests. Use realtime only to translate the spoken goal and summarize the resulting diff; use a cheaper background model for large diffs or logs.
- **latency:** Return a plan and first risk summary within 3 seconds; let tests continue asynchronously and deliver a short pendant inbox result. Applying an unchanged, owner-requested rehearsal should begin immediately after the explicit spoken command.
- **cost:** Local filesystem snapshots and git worktrees are cheap; model cost is roughly $0.005–$0.05 per rehearsal depending on diff/log size. Browser preview support is the expensive portion because some sites have no draft or transaction mode.
- **security:** A rehearsal must be hermetic: no production credentials, network writes, mail sends, purchases, or destructive commands may escape the sandbox. The apply step must verify that the real target has not changed since rehearsal and should refuse stale patches rather than silently merging.
- **missing:** A first-class sandbox/rehearsal action type in the Mac agent with resource and network isolation; Snapshot/diff adapters for arbitrary files and app state, plus git worktree support; Browser transaction or draft adapters and an explicit classification of sites that cannot be safely rehearsed; A durable rehearsal artifact keyed to the exact goal, inputs, diff, tests, and target revision; A pendant command to select and apply a named rehearsal without replaying the entire conversation

### "“Stop the thing you just started.” A deliberate long press on the pendant should cancel the currently running Mac or browser job, close or undo only the actions that job owns where that is safe, and tell me exactly what was stopped and what could not be undone."
- **useful because:** When the owner is away from the Mac or notices an automation going wrong, waiting for a spoken turn or finding the right window is too slow. A physical abort path is the wearable's unique value: it can halt a runaway loop, accidental browser navigation, or an unexpectedly broad file operation before the owner reaches the keyboard.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** No expensive reasoning is needed for the first stop signal: relay forwards a signed cancellation to the owning job and the Mac agent enforces it. Use a cheap model only to summarize partial receipts; use realtime for the immediate spoken acknowledgement.
- **latency:** Acknowledge locally within 150 ms and deliver the cancellation to the Mac/browser within 500 ms when connected. If disconnected, the pendant must show a distinct abort-pending state and the relay must not claim success until a receipt arrives.
- **cost:** Negligible model cost; the engineering cost is cancellation propagation and compensating actions. A short final summary is <$0.001 per incident.
- **security:** The gesture must be hard to trigger accidentally and must never be treated as a general delete/undo command. Cancellation should be idempotent, scoped to the active job, logged with a receipt, and conservative about compensation: stop first, undo only operations with an explicit inverse.
- **missing:** A physical long-press/double-confirm abort gesture distinct from normal record/stop behavior; Cancellation tokens propagated from relay jobs through planner, shell, vision, and browser command queues; Cooperative cancellation checks in long-running Mac/browser actions; Per-action inverse metadata and a partial-completion receipt; A relay-to-pendant immediate status signal for abort-pending, stopped, and unable-to-undo


## What it asked for

_Nothing._
## Its own summary

Recorded four owner-facing gaps: advisory cross-device mistake warnings, provenance-preserving search across authenticated browser/Mac/voice sources, hermetic rehearsal-before-apply for consequential workflows, and a physical pendant abort for active jobs. Each names the cross-surface changes required rather than pretending today’s wiring is sufficient.

**Biggest unknown:** Whether the recorder’s similarity warnings indicate prior backlog entries that are genuinely duplicates; all four were accepted, but the warnings suggest especially the federated search and physical abort deserve a later ledger check before further refinement.

