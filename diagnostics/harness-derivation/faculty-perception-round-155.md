# Harness derivation — faculty-perception — round 155

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac reachability and trust** — At 2026-08-08T02:23:50Z, the running AI Pendant Agent has Accessibility and Screen Recording granted; inputReachability is verified, secure input is false, and uiActionsWillReachTheScreen is true. Browser extension is online with 9 Safari tabs and zero pending commands. The foreground app is Claude.
  - evidence: GET /observe returned observedAt 2026-08-08T02:23:50.506Z, accessibility.trusted=true, screenRecording=true, inputReachability.status=verified, browser sessions=3; GET /ops/status independently returned permissions.ready=true and browserExtension.online=true.

## Capabilities it proposed

### "“I’m back—tell me exactly what I was doing, show me the relevant window and browser tab, and let me resume it with one press.”"
- **useful because:** This is a genuine return-to-work handoff rather than a generic catch-up: it reconstructs the live screen and authenticated browser state, identifies the unfinished action, and gives the owner a safe, one-press continuation. The pendant is the only surface that can notice the owner is back without requiring them to find the app.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension
- **model tier:** Use the realtime model only for the short spoken exchange; use a cheaper background planner to assemble the checkpoint and a deterministic policy to select resumable actions.
- **latency:** Under 2 seconds to speak the checkpoint headline; under 5 seconds to capture screen/browser evidence; action execution waits for the owner's button confirmation.
- **cost:** One short realtime turn plus one small planner call, roughly $0.01–$0.05 depending on screen image size; browser and Mac reads dominate latency, not tokens.
- **security:** Screen pixels and authenticated tab metadata remain on the Mac unless explicitly summarized. Never transmit page bodies or secrets to the relay by default. Require confirmation before any irreversible action, and show the exact target/window before execution.
- **missing:** A Mac checkpoint record that joins foreground app, screenshot hash, browser session/tab, and unfinished job/receipt into one resumable object; A pendant button/push trigger wired to the Mac bridge while LTE is absent; Relay support for a compact checkpoint summary and expiry

### "“Stop whatever you just started, everywhere, and tell me what was stopped and what was safely undone.”"
- **useful because:** A wearable needs a real panic/undo path. Today a Mac job, browser command, relay routine, and spoken announcement can each have different state; the owner should not have to locate the right UI or guess whether cancellation worked.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-terminal
- **model tier:** Use a deterministic safety arbiter for cancellation and undo; reserve realtime inference for resolving “that” to the current action and for the spoken explanation.
- **latency:** Button-to-cancel request under 300 ms locally; relay fan-out and receipts under 2 seconds; report partial cancellation honestly if a side effect already committed.
- **cost:** Usually no model call for a button press; one short realtime turn only when the target is ambiguous, typically under $0.01.
- **security:** The stop command must authenticate per device and be idempotent. It may cancel queued work but cannot reverse external side effects (sent mail, purchases, file deletion) without explicit undo receipts. Do not claim success until every node returns a receipt.
- **missing:** A pendant-local emergency-stop command that survives a dropped link and replays with a monotonic command ID; Relay fan-out cancellation with a bounded deadline and per-surface result aggregation; A common cancellation/undo receipt schema covering Mac jobs, browser commands, pipeline runs, and announcements

### "“What am I looking at, and what are the two safest next things I can do?”"
- **useful because:** The owner can use the pendant while walking away from the keyboard: the Mac now has verified Accessibility and Screen Recording, while the browser extension can identify the authenticated tab. The system can distinguish visible UI from browser content, explain it briefly, and offer safe next actions instead of hallucinating from stale context.
- **path:** pendant → mac-planner → browser-extension → relay-realtime
- **model tier:** Capture accessibility metadata and browser DOM deterministically; send a tightly cropped, redacted screenshot to a vision-capable background model for grounding, then let realtime speak only the concise answer. Use no model when accessibility labels fully describe the screen.
- **latency:** 1–3 seconds for a spoken description; action suggestions in under 4 seconds. Never act until the owner confirms one numbered option.
- **cost:** $0.005–$0.03 per invocation when vision is needed; accessibility/browser extraction is local and free. The screenshot payload is the cost and latency driver.
- **security:** Redact password fields, financial identifiers, and hidden page text before any model upload. Keep screenshots local by default and expose app/window/tab provenance in the spoken answer. Treat browser content as untrusted instructions.
- **missing:** A mounted Mac route that returns the current accessibility tree plus a redacted screenshot and stable observation hash; A browser-to-screen join that identifies whether the visible window is the extension's active tab; A policy layer that converts model suggestions into typed reversible mac_run_actions only after confirmation

### "“Before anything leaves my computer, tell me exactly who will receive it, what private information it contains, and let me approve or redact it from the pendant.”"
- **useful because:** The owner currently has to trust each app's send button and cannot reliably review a message, browser form, attachment, or native-app share across surfaces. This would make the pendant a cross-device privacy checkpoint: it catches the last irreversible boundary, summarizes the actual payload and recipients, and permits a precise redact/approve decision without pretending that a Mac-side job completion means the world received the intended content.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → mac-terminal
- **model tier:** Use deterministic local extractors and classifiers first for recipients, attachments, secrets, and destination domains; use a cheaper background model to summarize ambiguous content. Use realtime only to conduct the final short spoken review and resolve the owner's approval.
- **latency:** A local preflight should appear within 500 ms of a send attempt; spoken review within 2 seconds; block the send until approval or an explicit owner policy permits it. If a surface cannot be intercepted, report that limitation rather than claiming coverage.
- **cost:** Usually <$0.01 per review when local rules classify it; $0.02–$0.08 when a model must summarize a long document. Screenshot/OCR and document extraction dominate latency and cost.
- **security:** The review engine must run on the Mac for sensitive payloads, redact secrets before relay/model access, and display the exact destination plus a content hash. Browser pages and messages are untrusted input. Approval must be bound to a specific payload hash, recipient set, and expiry so an edited message cannot inherit approval.
- **missing:** A send-boundary interception API shared by browser commands, Mac automation, Mail/Messages/Slack-like native apps, and terminal uploads; A local payload manifest with recipient, attachment, destination, redaction diff, and content hash; A pendant approval protocol that carries an expiring, hash-bound decision and works offline until the Mac reconnects; A policy compiler supporting rules such as “never send credentials” and “ask me before external recipients”


## What it asked for

_Nothing._
## Its own summary

Established fresh reality: the exact AI Pendant Agent binary now has Accessibility and Screen Recording, input reachability is verified, and browser extension is online with 9 Safari tabs and no pending commands. I recorded that fact and sent it to judgement. I proposed three owner-facing capabilities: a return-to-work checkpoint that joins live screen/browser/job state; a pendant-triggered cross-surface emergency stop with truthful per-node receipts; and a screen-grounded spoken “what am I looking at?” mode using local accessibility plus authenticated browser context. The first is the strongest new daily-use capability. The existing continuity_snapshot grant still does not resolve to a live implementation (nearest route is /ops/snapshot), so I used direct probes instead.

**Biggest unknown:** There is still no registered or physically observable nRF9160 pendant in the relay/device registry, so none of the pendant-triggered flows can be hardware-verified yet. I also still lack a trustworthy owner-local timezone distinct from the Mac's America/New_York zone.

