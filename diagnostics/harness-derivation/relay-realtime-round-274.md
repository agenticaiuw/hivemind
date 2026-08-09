# Harness derivation — relay-realtime — round 274

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If I lose my connection, save what I was trying to do and resume it when I’m back online."
- **useful because:** This makes the system feel reliable. The owner doesn’t have to re-say or re-issue commands after a drop; work resumes when the Mac or browser becomes available.
- **path:** pendant → relay → mac-bridge → browser
- **model tier:** Realtime to capture the intent; background tier to resume when connectivity returns.
- **latency:** Capture should be instant. Resume can wait for the next availability event.
- **cost:** Mostly storage and reconciliation; compute is small, dominated by retries and idempotency checks.
- **security:** Must not replay destructive actions without explicit confirmation. Needs idempotency keys and a safe checkpoint before irreversible steps.
- **missing:** A cross-surface command ledger with idempotency and replay protection; Connectivity-change triggers and a resume policy; A way to serialize intent safely for later execution

### "If I say “save this for the project” while looking at a logged-in web page, have the pendant capture the page I mean, ask only if there are multiple plausible targets, and produce a durable project note on my Mac with the source URL, title, timestamp, and a short spoken confirmation—even if I walk away before it finishes."
- **useful because:** Today the owner must manually bridge the pendant, authenticated browser, and Mac. This turns a fleeting spoken reference into a traceable artifact without making them repeat URLs or stay near the laptop.
- **path:** pendant → relay → browser → mac-planner → mac-terminal
- **model tier:** Realtime relay for intent and one clarification; background mac-planner for extraction, filing, and receipt generation.
- **latency:** Acknowledge within 1 s; clarification within 3 s; complete in under 30 s when browser and Mac are online. Queue the result for later pendant playback if the owner leaves.
- **cost:** About $0.01–$0.05 per invocation depending on page extraction and planner turns; browser/Mac execution dominates latency, not speech.
- **security:** Authenticated page content and the resulting note leave the browser/Mac only through the existing relay job path. Never read arbitrary tabs without a target match; include URL and capture time in the receipt. Creating the note is reversible, but sending or sharing it must remain a separate explicit action.
- **missing:** A cross-surface target-resolution operation that can inspect the active browser tab and current Mac project context, rank candidates, and ask one spoken disambiguation question.; A durable artifact writer that stores source provenance and links it to the relay job receipt.; A live wiring of the context projection into conversationContext.js so the relay knows project/editor preferences without resending legacy memory.

### "Give me a “panic button” phrase or two-press gesture that immediately locks my Mac, pauses active browser sessions, and tells me on the pendant exactly which protections succeeded or failed."
- **useful because:** When the owner is away from the laptop, they currently cannot reliably contain an exposed or unattended session from the one device they are wearing. A single spoken/physical emergency action would reduce the time from noticing risk to containment.
- **path:** pendant → relay → mac-planner → browser → phone
- **model tier:** Realtime relay for recognition and status; deterministic Mac/browser action broker for containment; no expensive model after the command is classified.
- **latency:** Begin containment within 1 s, report first results within 5 s, and continue collecting receipts asynchronously. The pendant must announce partial failure rather than claiming success.
- **cost:** Usually under $0.01 per event; dominated by Mac wake/link latency. No browser-model inference is needed for the fixed sequence.
- **security:** This is intentionally high impact and must require a deliberate physical gesture or a pre-enrolled spoken phrase plus a current pendant session nonce. It should lock, not shut down or delete data. Browser session pausing must be scoped to the owner's registered browser, and every action needs an immutable success/failure receipt.
- **missing:** A firmware/relay emergency command path that survives an ordinary voice-turn timeout and cannot be confused with normal dictation.; A Mac action for lock-screen and a browser action for revoking/pausing registered sessions, with idempotent execution and per-step receipts.; A prioritized alert delivery path that can distinguish complete, partial, and failed containment and surface it through the existing pendant inbox.

### "Let me say “what am I looking at?” and have the pendant answer with a compact, confidence-ranked explanation assembled from the active Mac window, the selected text, and the current browser page—then let me say “that one” to act on the exact item it just described."
- **useful because:** The owner is often away from the screen or cannot comfortably read it while wearing the pendant. Today the available computer-use pieces do not preserve a shared referent between perception, spoken explanation, and a follow-up action.
- **path:** pendant → relay → mac-vision → mac-planner → browser
- **model tier:** gpt-4.1-mini vision loop for screenshot/OCR grounding; realtime relay only handles the two short turns; mac-planner executes the confirmed follow-up.
- **latency:** Return a 1–2 sentence description in 3 s; retain the ranked referents for 60 s; execute “that one” in under 5 s.
- **cost:** Roughly $0.01–$0.08 per inspection depending on screenshot/OCR size; follow-up actions are cheap. The dominant cost is image tokens.
- **security:** Screenshots may contain private data and must remain scoped to the active window or explicitly selected tab. Do not infer sensitive content aloud unless requested. The follow-up must use the exact referent ID from the inspection receipt, not a fresh guess.
- **missing:** A currently enabled Mac vision/computer-use loop with a stable screenshot/OCR endpoint and referent IDs.; A short-lived cross-turn referent store shared by relay and Mac agents, including expiry and confidence.; A voice-turn resolver that maps pronouns such as “that one” to the prior referent and rejects stale or ambiguous IDs.

### "Answer “what changed because of me today?” with a spoken, trustworthy digest of every Mac and browser mutation made through the hive, grouped by task, with the exact app/site and a one-word status; let me say “undo the last one” to reverse only a reversible change."
- **useful because:** The owner currently has to inspect scattered job records and cannot tell whether a spoken request caused one change, several partial changes, or none. A concise end-of-day accountability view makes automation safe enough to trust when the owner was away.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Cheaper background summarizer over structured receipts; realtime relay only resolves the time range and the selected receipt for undo.
- **latency:** Digest in under 5 s from cached receipts; undo acknowledgement in 1 s and completion within 10 s.
- **cost:** Under $0.02 per digest; receipt retrieval and compact summarization dominate.
- **security:** Only include actions attributable to this owner and this pendant/session. Never summarize page contents by default, only metadata and declared action results. Undo must target a receipt ID, be idempotent, and refuse if state has diverged.
- **missing:** A unified immutable mutation ledger joining Mac, browser, and relay receipts with actor, target, before/after summary, and reversibility.; A receipt query and spoken grouping endpoint; current job receipts are per-job rather than a cross-surface audit view.; A safe inverse-action planner that can validate the precondition before invoking the existing undo route.

### "When I say “I’m leaving,” have the pendant coordinate a departure checklist: ask the Mac for unsaved work and active automations, close or pause only the items I name, verify the browser has no pending command, and tell me what remains before I walk away."
- **useful because:** The pendant is worn away from the Mac, so the owner currently cannot establish a reliable handoff state before leaving. This combines awareness and selective cleanup without blindly shutting down work in progress.
- **path:** pendant → relay → mac-planner → browser
- **model tier:** Realtime relay for the short checklist dialogue; deterministic status collectors and mac-planner only for named reversible actions.
- **latency:** Initial inventory within 4 s; each selected action within 10 s; continue asynchronously with a compact completion alert.
- **cost:** About $0.01–$0.04 per departure; mostly Mac/browser round trips.
- **security:** Default is report-only; never close unsaved documents or terminate jobs without the owner naming the item. Include app/job identifiers and preserve receipts. A lost connection must yield “unverified,” never “done.”
- **missing:** A cross-surface inventory endpoint that atomically snapshots unsaved Mac documents, active jobs, browser commands, and pending relay events.; A spoken selection protocol with stable item IDs across multiple turns.; A final-state verifier that distinguishes stopped, completed, and unreachable surfaces.


## What it asked for

_Nothing._
## Its own summary

Recorded five owner-facing capabilities. The strongest is a provenance-preserving “save this for the project” flow that resolves the active authenticated page, files a sourced artifact on the Mac, and confirms asynchronously. Other recorded capabilities cover emergency containment from the pendant, screen-grounded referents, a cross-surface change digest with safe undo, and a verified departure checklist. The main missing pieces are not another generic planner: they are cross-surface identity/referent stores, a unified mutation ledger, atomic inventory/final-state verification, and explicit emergency containment primitives. Several proposals were flagged as close to existing backlog items, so they should be treated as recorded but not rephrased again.

**Biggest unknown:** Which exact live Mac/browser action types and routes implement the missing primitives; the recorder explicitly warned that several named routes/actions were not fully inventoried. No further discovery was possible this round.

