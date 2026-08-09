# Harness derivation — relay-realtime — round 160

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “pick this back up,” have the pendant and Mac reconstruct the exact work context I abandoned—frontmost app, selected text, open document or browser tab, and the last unfinished action—and read me a two-sentence orientation before offering the next reversible step."
- **useful because:** The owner can resume work hands-free after walking away instead of hunting through windows and tabs. This is a genuinely joint capability: the pendant supplies the spoken request and identity, the Mac supplies live UI/document state, and the relay turns a potentially huge snapshot into a useful spoken handoff.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime relay for intent capture and a short spoken orientation; mac-vision/mac-planner for state extraction and action proposal; use a cheaper background model to compress the context snapshot.
- **latency:** Initial orientation within 4 seconds; state extraction may take up to 10 seconds if the Mac must inspect a document or browser tab.
- **cost:** About $0.01–$0.05 per resume, dominated by one vision/state extraction and a small summarization call; no cost while idle.
- **security:** The snapshot can contain private document text, browser content, and selection data. Keep raw captures on the Mac, send only the minimum cited spans to the relay, redact secrets, and never expose a tab or document merely because it is open. Reversible proposed actions need no confirmation under owner policy.
- **missing:** A Mac route that atomically captures frontmost app, window, selection, document identity, browser tab URL/title, and pending local-agent job state; A stable context snapshot ID with short-lived relay retrieval and redaction; A mac-vision result that distinguishes visible UI from inferred document state

### "Let me say “make this understandable” while pointing at anything on my Mac, and have the pendant speak a concise explanation of the exact visible region or selected text, then let me ask follow-ups without repeating what was on screen."
- **useful because:** This turns the wearable into an always-available comprehension tool for dense code, charts, error dialogs, and authenticated web pages. The owner can keep their eyes on the physical task or walk around while the Mac contributes visual truth and the relay maintains a small conversational reference.
- **path:** pendant → relay → mac-vision → mac-planner → browser-extension
- **model tier:** gpt-4.1-mini or equivalent local computer-use/vision loop for screenshot/OCR grounding; realtime relay only handles dialogue, reference resolution, and short speech; a cheaper summarizer handles long selected text.
- **latency:** First explanation in 5 seconds for a visible region; follow-up answers in 2 seconds when the same captured frame remains valid.
- **cost:** Roughly $0.02–$0.10 per explanation depending on screenshot resolution and OCR; follow-ups can reuse the frame and cost far less.
- **security:** Screenshots may include passwords, personal mail, or confidential work. Process the frame on the Mac, attach a frame hash and bounding box rather than retaining full screenshots in relay memory, expire frames after the turn, and make the owner explicitly invoke capture with the button/utterance.
- **missing:** A live Mac-vision capture-and-ground route accepting a region or selection and returning citations/bounding boxes; A relay-side frame reference with expiry and invalidation when the frontmost window changes; A pendant conversation mode that preserves the referenced frame across follow-up turns without resending the screenshot

### "While I am away from my desk, let me dictate a change to the exact thing I was last looking at—“replace the selected paragraph with this,” “reply to that message,” or “run the test and tell me why it failed”—and have the system reopen the saved context, perform the smallest edit, and speak back a diff and verification result."
- **useful because:** This is the closest thing to a remote pair-programmer that uses the wearable's physical presence and the Mac's reach. It avoids vague commands by binding the utterance to a previously captured object and gives the owner an audible, inspectable result rather than silently changing a file or message.
- **path:** pendant → relay → mac-planner → mac-vision → mac-terminal → browser-extension → dashboard
- **model tier:** Realtime relay resolves references and confirms the intended object; mac-planner selects a concrete plan; mac-vision/browser-extension/mac-terminal execute and verify; use a cheaper model for diff compression and test-log summarization.
- **latency:** Acknowledge intent in under 1 second; complete ordinary edits in 10–30 seconds; long tests become an asynchronous job with a spoken completion alert.
- **cost:** $0.03–$0.20 per operation, dominated by planning/vision and test-log summarization; browser and Mac execution have no model charge beyond those calls.
- **security:** Stale context could edit the wrong file or send the wrong reply. Bind each target to app/document/tab identity, selection hash, and capture timestamp; refuse on mismatch and speak the mismatch. Keep full diffs/logs on the Mac, send only a summary, and record an undoable receipt.
- **missing:** A durable cross-surface anchor for selection/document/tab identity that survives the owner walking away; An execution primitive for atomic edit-plus-diff-plus-test verification across editor, terminal, and browser; A stale-anchor detector and undo handle exposed to the relay; A real durable job runner for tests and relay event delivery for completion


## Changes it proposed to its own stack

### `context` — Build a cross-surface Context Anchor Ledger. On an explicit pendant capture, the Mac records a compact, signed anchor: frontmost app/window, document or tab identity, selection hash and bounded text excerpt, scroll/URL, visible UI hash, and timestamp. The relay stores only the anchor ID and redacted summary. Every later voice action must resolve the anchor and return fresh identity/visual hashes before acting; mismatches produce a spoken stale-context explanation instead of execution. Keep an append-only undo/diff receipt and allow one-tap invalidation from the pendant.
- **owner gets:** The owner can leave the desk and later refer to “that paragraph,” “the page I was on,” or “what I was doing” without risking an edit to a different tab or document. It makes remote wearable control trustworthy rather than merely powerful.
- effort: Medium-high: Mac hooks for editor/browser selection and frontmost state, a signed schema shared with relay, stale matching, bounded redaction, and receipt integration.  ·  risk: Window identity APIs differ across apps and selections can change while away. Fail closed on mismatch, expire anchors, and retain the last known anchor only as a readable explanation. Recovery is reopening the captured app/tab and taking a new explicit capture.
- cost: Small storage and one hash/metadata write per capture; approximately $0.01 or less for optional summarization. No routine audio or screenshot retention.  ·  latency: Capture under 300 ms; resolution adds 0.5–2 s for fresh Mac inspection.
- security: Improves security by preventing stale-target actions, but anchors may contain sensitive titles/excerpts. Encrypt relay metadata, redact by default, short TTL, and keep full content on the Mac.
- depends on: A Mac endpoint exposing atomic frontmost/selection/document/tab capture; Shared anchor schema and signed freshness token; Undoable action receipts already present

### `relay` — Add a relay-side Conversation Continuation Kernel that keeps a typed reference graph for one voice session: anchor IDs, pending Mac/browser jobs, cited observations, and user corrections. It should answer deictic follow-ups (“that one,” “why,” “undo it”) by resolving graph edges, not by replaying the entire transcript, and should invalidate edges when job receipts or fresh observations disagree.
- **owner gets:** The owner can conduct a natural, multi-turn hands-free interaction while walking, without restating URLs, filenames, or prior results and without the relay hallucinating which “that” they meant.
- effort: Medium: typed state machine, bounded memory projection, receipt/event adapters, and explicit expiration rules.  ·  risk: A bad reference resolution can cause an unintended action. Restrict unresolved references to explanation/read-only responses, speak the ambiguity, and require a new explicit target capture for mutations.
- cost: Reduces repeated context-token spend; modest Durable Object/storage cost per active session.  ·  latency: Adds under 100 ms for local graph resolution; no extra model call for ordinary follow-ups.
- security: Use per-session encryption and erase graph state on session expiry; never put raw secrets in the graph.
- depends on: Context Anchor Ledger; GET /jobs/:jobId receipts; relay event delivery that is actually implemented; Typed observation/action result envelopes


## What it asked for

_Nothing._
