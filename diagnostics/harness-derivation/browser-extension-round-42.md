# Harness derivation — browser-extension — round 42

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Take the information from this page and prepare the form for me, filling in anything you can verify from my Mac; show me exactly what will be submitted, and only send it after I approve on the pendant.”"
- **useful because:** This combines the browser's existing authenticated session with the Mac's local files and the pendant's physical presence. Today the browser can read/fill, but it cannot safely hand a verified draft to the owner as a compact, resumable approval object. The owner gets fast form completion without silently sending mail, purchases, or submissions.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → pendant → unified
- **model tier:** Use the cheap/background tier to extract the page schema, find candidate local values, and compute a field-by-field diff. Use realtime only to explain the final draft and answer the owner's spoken questions. Browser and Mac execute deterministic typed actions; the pendant supplies the physical approval event.
- **latency:** 2–5 seconds to read and draft a normal form; under 1 second to render a compact diff on the pendant; approval-to-submit under 2 seconds. If page navigation or local-file search takes longer, keep the draft resumable rather than re-running it.
- **cost:** About $0.01–$0.05 per ordinary form draft, dominated by page extraction and local-context summarization; approval and submission should be zero additional model cost. Browser/Mac bridge calls are negligible.
- **security:** Only the minimum candidate local values leave the Mac, with field provenance and confidence attached. Never transmit passwords, payment card numbers, or secrets to the model. The browser must stop before submit/send/purchase, display the exact payload and destination, and require a deliberate pendant button press (with spoken read-back available). Expire drafts when the tab URL, account, or form schema changes; retain an audit receipt and provide undo where the site supports it.
- **missing:** A durable browser draft object keyed to extension device, tab, URL, and form fingerprint; A typed browser fill-and-preview operation that can return field provenance and the exact pending submission payload without submitting; A pendant approval event with a nonce bound to that draft, plus a short diff/read-back view; A Mac-side private value resolver that returns candidates and provenance without exposing raw secrets to the model; A relay resume/expiry path so an interrupted draft can be safely recovered or discarded

### "“Check the GitHub page I have open, compare the urgent items with my local repository, and tell me which one I should handle next—without changing anything.”"
- **useful because:** The browser can see private GitHub issues/PRs behind the owner's login, while the Mac can inspect the corresponding local checkout and tests. Their combination produces a grounded recommendation instead of a generic web summary, and the pendant gives the owner a hands-free, one-sentence result with a link to resume.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → pendant → unified
- **model tier:** Cheap background model performs extraction, joins items to local repository metadata, and ranks urgency. Realtime is used only for the final spoken explanation or follow-up. Deterministic shell and browser reads do the evidence collection.
- **latency:** 5–10 seconds for up to 20 issues/PRs; speak the top recommendation as soon as the first evidence set is complete, then optionally append local-test details.
- **cost:** Roughly $0.02–$0.08 per triage, mostly context compression and ranking; browser reads and local git status are low-cost.
- **security:** Keep private page contents and repository paths on the local relay/Mac boundary as much as possible; redact tokens, secrets, and code contents. Read-only browser and shell operations by default. Include citations (PR URL, local commit/test output) and mark uncertainty when an item cannot be matched. Do not comment, merge, or push.
- **missing:** A browser extractor for authenticated GitHub issue/PR rows with stable URLs and timestamps; A local repository correlator that maps PR branches/commits to checked-out worktrees without reading secrets; A shared evidence envelope with source citations, freshness, and redaction metadata; A pendant response format that speaks one recommendation plus an optional “why” expansion

### "“From the private page I’m viewing, make me a local, resumable case file: capture the relevant title, deadlines, and links, find the matching project folder on my Mac, and leave me a one-tap next action I can resume later from the pendant.”"
- **useful because:** The browser can see authenticated content that the Mac cannot, while the Mac knows the owner's local project structure and the pendant is the persistent entry point. This creates a durable private handoff instead of forcing the owner to copy URLs, names, and deadlines by hand or leave a sensitive tab open.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → pendant → unified
- **model tier:** Use a cheaper background model for page extraction, entity matching, and case-file summarization. Use realtime only when the owner asks for the case file or dictates a next step. File creation, linking, and reminder creation should be deterministic actions.
- **latency:** 10 seconds for extraction and local matching; pendant retrieval should be under 2 seconds. If matching is ambiguous, save the evidence and ask one short disambiguation question rather than guessing.
- **cost:** Approximately $0.01–$0.05 per case file, dominated by private-page summarization; subsequent retrievals and reminder launches have negligible model cost.
- **security:** Store only the selected fields and source URLs, not a full page archive. Keep authenticated content encrypted on the owner's relay/Mac, redact credentials and unrelated page text, and bind each case file to the browser account/tab provenance. Do not automatically send, upload, or share the captured material. Provide expiry and deletion from the pendant.
- **missing:** A browser-side selection/extraction result with stable source URL, account identity, and page freshness; An encrypted relay case-file store with field-level redaction, expiry, and deletion; A Mac correlator that maps extracted project names/IDs to local folders without uploading repository contents; A pendant case-file index and deep-link/resume event that survives browser tab closure; A deterministic handoff action that can open the matched folder or page without performing an irreversible mutation


## Changes it proposed to its own stack

### `browser-harness` — Add a durable browser-extension liveness and recovery protocol: the extension should heartbeat its real device identity and active tab even when Safari has no page, acknowledge command receipt separately from command completion, persist an idempotency key across service-worker restarts, and expose a “reopen last safe page” bootstrap command. The relay should mark a device stale, not silently substitute home-chrome, and requeue only unacknowledged commands.
- **owner gets:** Browser work will stop failing mysteriously after Safari sleeps, the extension restarts, or the Mac changes networks. The owner can ask to read a private page and get a clear “Safari is offline” response or recover the last tab, rather than losing a form draft or sending duplicate clicks.
- effort: Medium: extension background lifecycle/heartbeat, browserBridge command state machine, device selection, and integration tests for restart/offline/reconnect.  ·  risk: A replayed click could duplicate a reversible action; idempotency keys and action receipts must suppress replays. Reopening a page could expose private content on screen, so reopen only the last URL and never auto-submit. Recovery is to invalidate the command and require a fresh read.
- cost: Negligible model/API cost; small relay storage for command receipts and heartbeat state.  ·  latency: Adds under 200 ms for acknowledgement; recovery after reconnect is bounded by the heartbeat interval (target 5–10 s).
- security: Improves isolation by preventing commands intended for Safari from being delivered to the untrusted/unknown home-chrome device; device identity and tab affinity become mandatory.
- depends on: A typed browser command receipt/result schema; Persistent browser device identity in the extension; The existing browserBridge enqueue/result path


## What it asked for

_Nothing._
## Its own summary

Recorded two new cross-surface capabilities: authenticated form drafting with Mac provenance and physical pendant approval, and private GitHub triage joined with the local repository. Also recorded a browser-harness change for durable Safari identity, liveness, command acknowledgements, and idempotent recovery. Fresh GET /browser/status shows only home-chrome, offline, no tab, with 3 pending commands; the real Safari extension is not currently visible, so authenticated browser work remains unavailable until its heartbeat/device registration returns.

**Biggest unknown:** Whether Safari is actually closed/asleep or the extension lost its registration; the next useful implementation step is restoring and testing the real Safari heartbeat, then exercising a read-only authenticated page flow.

