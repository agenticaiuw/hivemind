# Harness derivation — relay-realtime — round 81

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Bookmark this moment.” Later: “What was I doing when I bookmarked that?” or “Open the thing I bookmarked and give me the context.” A single pendant-button press (optionally followed by a short spoken label) should create a cross-device moment marker that correlates the pendant audio timestamp, the relay conversation, the Mac’s active app/window, and the browser tab/session that was in focus, then lets the owner retrieve or reopen that moment by natural language."
- **useful because:** The owner can capture an idea, confusing screen, or important transition without reaching for a phone or interrupting work. Unlike a reminder or transcript, it answers the retrospective question “what exactly was happening at that instant?” across the surfaces that individually cannot see one another.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use the realtime tier only to acknowledge the button/label and resolve the immediate reference. A cheaper background model should merge timestamped Mac-window/browser evidence with the voice run and produce a compact cited moment card; retrieval can use embeddings or structured timestamps before invoking a model.
- **latency:** Button acknowledgment under 300 ms; marker durability under 2 s when connected. Retrieval should return a short spoken answer within 3 s, with deeper context allowed asynchronously.
- **cost:** About $0.001–$0.01 per marker/retrieval depending on whether summarization is needed; most markers should be metadata-only and avoid an LLM call. Storage and Mac/browser event capture dominate engineering cost, not inference.
- **security:** Moment cards can contain sensitive audio, window titles, URLs, and authenticated page context. Default to short-lived raw evidence, encrypted storage, explicit per-surface redaction (password fields and page contents), and a visible delete-all-moments control. Reopening a tab or taking an action must remain distinct from merely describing it.
- **missing:** A pendant button-event uplink with a durable event id and monotonic timestamp (including an offline queue); A relay moment index joining voice-run timestamps to device events; A Mac observer that reports active application/window and a browser-extension observer that reports tab identity without leaking page secrets; A retrieval API that returns a cited moment card and optionally dispatches a safe open request; Retention, redaction, and deletion controls in the dashboard

### "“I’m leaving my Mac—pack up this work so I can resume it later.” Later, from the pendant: “Resume the work I packed up.” The system should create a handoff capsule containing the active Mac apps/windows, browser tabs and session identities, relevant document paths, unsaved-work warnings, the last voice instruction, and a plain-language next-step summary; on resume it should reopen only the selected capsule and report anything that changed."
- **useful because:** The pendant is worn precisely when the owner walks away. This turns leaving the desk into a recoverable boundary instead of losing the thread or reopening a dangerous pile of tabs. It combines the Mac’s local state, authenticated browser reach, relay persistence, and voice-only selection—none of those nodes can provide the complete handoff alone.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use realtime only for the leave/resume utterance and capsule selection. A cheaper background model summarizes titles, recent task context, and explicit next steps; deterministic collectors should provide the state and detect unsaved documents. No model should infer or transmit page contents unless requested.
- **latency:** A leave acknowledgment in under 500 ms, with capsule collection completing within 5 s and a spoken result immediately. Resume should confirm capsule identity in under 1 s, then reopen in stages and report failures within 10 s.
- **cost:** Roughly $0.002–$0.02 per handoff, dominated by optional summarization; collecting app/tab metadata should be free. Storage is small per capsule, but retaining authenticated URLs and document paths needs bounded retention.
- **security:** Capsules reveal work context and may contain sensitive URLs or local paths. Encrypt at rest, redact query strings and password/payment pages, retain only metadata by default, and make deletion easy. Resume must never silently submit, send, or mutate; it may reopen and restore windows, while any external action remains a separate request.
- **missing:** A Mac snapshot collector for active windows, document paths, unsaved-state indicators, and app-specific resume hints; A browser-extension snapshot that records tab identity and safe title/origin metadata while preserving session affinity; Durable relay storage for versioned handoff capsules with owner-selectable retention and conflict detection; A typed resume operation that can reopen state without executing page or document mutations; Pendant-friendly capsule listing, selection, and spoken failure reporting

### "“Before you act, tell me what you actually observed, what you inferred, and what could make that wrong.” For a request involving the Mac or an authenticated browser, the pendant should provide a compact spoken evidence report, then let the owner say “go ahead” or “use the other interpretation”; the report must cite the app/tab/screenshot or returned data it used and preserve that evidence with the action receipt."
- **useful because:** Today a fluent voice answer can blur perception, inference, and plan. This gives the owner a useful way to catch a wrong tab, stale page, mistaken person, or ambiguous instruction while away from the screen—without imposing confirmation gates on ordinary reversible work. It is a hive-native trust layer: perception sees evidence, judgement explains uncertainty, action executes, and relay makes it audible.
- **path:** pendant → relay → faculty-perception → faculty-judgement → faculty-action → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime handles the short explanation and disambiguation. Faculty-perception should use deterministic/vision extraction first; faculty-judgement can use a cheaper reasoning tier to compare evidence and alternatives. Escalate to the expensive tier only when evidence conflicts or the owner asks for an explanation.
- **latency:** Evidence report in 2–4 s for a Mac/browser read; under 1 s to accept a stated interpretation. Execution status remains asynchronous, with a concise receipt spoken when complete.
- **cost:** Approximately $0.005–$0.03 per nontrivial report, mostly vision or summarization; simple structured reads should cost almost nothing. Evidence hashes and metadata are cheap; retaining screenshots/page excerpts is the main storage cost.
- **security:** Reports can repeat secrets from authenticated pages or private screens. Apply field-level redaction before voice synthesis and storage, never read passwords or tokens aloud, encrypt evidence, and bind the owner’s choice to an immutable plan version so a changed page cannot silently turn approval into a different action. This is explainability, not a blanket permission gate.
- **missing:** A typed evidence envelope shared by perception, judgement, action, and relay (observations, timestamps, source, confidence, alternatives, redactions); Mac and browser adapters that emit source-cited observations rather than only opaque action results; A plan-version binding and stale-evidence check before execution; A pendant dialogue state that can accept a short correction or interpretation choice; Dashboard controls for evidence retention and redaction policy


## Changes it proposed to its own stack

### `integration` — Implement the granted relay_route_intent and server_browser_actions schemas, and add a shared job envelope that can represent Mac, browser, and relay work uniformly. The envelope carries intent, plan, receipts, provenance, and a user-facing spoken status string.
- **owner gets:** The owner gets consistent behavior: they can ask for something, have it routed to the right place, and later hear one clear status update, regardless of whether it ran on the Mac or in a sandboxed browser.
- effort: High: needs orchestration changes, a durable job runner for routing and execution, and a receipts/provenance model across surfaces.  ·  risk: Medium: misrouting could cause wrong actions. Mitigate with typed receipts, idempotency keys, and a strict rule that irreversible changes require explicit approval.
- cost: Medium: more storage for job envelopes and receipts; more compute for routing and monitoring.  ·  latency: Better perceived latency for simple requests; longer jobs run asynchronously.
- security: High sensitivity because it touches authenticated sessions and actions. Use least privilege, audit logs, and encrypted storage for secrets.
- depends on: Durable job runner; Browser command queue with typed results; Receipt/undo system across surfaces

### `hardware` — Add a tiny coin vibration motor driven by a low-side transistor and a low-power 3-axis accelerometer with interrupt wake, while keeping the existing button and LED as fallback. Firmware should expose a small event vocabulary (single tap, double tap, shake, long stillness) and queue events with monotonic timestamps; the relay should be able to request short haptic patterns for acknowledgement, completion, uncertainty, and failure.
- **owner gets:** The owner can use the pendant discreetly in public or while driving without staring at it or hearing a spoken interruption: a vibration confirms that a request was received, distinguishes completion from failure, and a tap can mark or correct a conversation state. Gesture input also works when the owner cannot reach the button precisely.
- effort: Moderate hardware respin and enclosure/acoustic testing; firmware interrupt/debounce and event uplink; relay protocol and pattern mapping; Mac/browser agents only need to consume the resulting event. Validate false positives during walking, clothing friction, and pocket/bag use.  ·  risk: Added power draw and mechanical noise; accelerometer gestures could create accidental commands, so initial firmware should emit events as annotations/acknowledgements rather than destructive actions. If the sensor fails, the original button/LED path remains functional. Require a physical long-press to enter gesture-learning or command mode.
- cost: Approximately $1–$4 in components and assembly at prototype quantities, plus a few mA peak during vibration and low tens of µA or less for an interrupt-capable accelerometer in standby. API inference cost is negligible; haptic patterns reduce unnecessary spoken responses.  ·  latency: Local acknowledgement can be under 50 ms; LTE event delivery remains network-bound. Accelerometer interrupt wake should be faster than button-to-relay handling and does not add conversational latency.
- security: Physical gestures are an additional command surface and can be triggered accidentally by someone holding the pendant. Keep high-impact gestures non-authoritative, require the existing deliberate button/voice interaction for mutations, sign events with device identity, and provide a dashboard switch to disable gesture commands while retaining haptic feedback.
- depends on: A small authenticated pendant-event protocol with monotonic timestamps and replay protection; Firmware power-budget validation against the nRF9160 pendant and existing one-button/one-LED wiring; A relay-to-pendant push channel for haptic patterns; Owner-configurable gesture semantics and observability in action receipts


## What it asked for

_Nothing._
## Its own summary

Recorded three new owner-facing gaps: cross-device moment bookmarks, leave/resume work handoff capsules, and an evidence-versus-inference report before Mac/browser actions. Also recorded a hardware change adding discreet haptic and gesture interaction. These are not available to the owner today and each names the missing cross-surface pieces.

**Biggest unknown:** Whether any of these connective features already has an unlisted implementation in the relay’s private surface; the exposed route inventory cannot establish that.

