# Harness derivation — mac-planner — round 299

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Send this to my phone” — take the item I’m currently looking at on my Mac, put it into the right iPhone app through iPhone Mirroring, and tell me when it is actually sent.”"
- **useful because:** The owner can move a link, selected text, or a file from the Mac context into Messages/Reminders/Notes on the real phone without breaking concentration or manually re-finding it. The pendant is the low-friction trigger, while the Mac is the only node that can reach iPhone Mirroring.
- **path:** pendant → relay → mac-planner → ios-control → dashboard
- **model tier:** Realtime only for the spoken command and final confirmation; use a cheaper background planner to classify the current Mac/browser item and choose the target app.
- **latency:** Acknowledge in under 1 s; inspect current context in 2–4 s; complete in under 10 s. If iPhone Mirroring is unavailable, say so rather than pretending delivery happened.
- **cost:** About $0.01–$0.04 per invocation; most cost is model classification of the current context, not the deterministic Mac/iPhone actions.
- **security:** The item may contain private text or a logged-in page. Keep extraction and transfer on the Mac, redact previews in relay logs, and require an explicit target (Messages/Notes/Reminders/contact) when ambiguity could send data to the wrong person. Report the post-action receipt, not merely a click.
- **missing:** A reliable semantic read of selected text/current document beyond the existing coarse host observation; Stable ios_* action names in the published Mac action manifest; A receipt that includes the target app and post-send state

### "“Run the pendant audio bench test and explain the result.”"
- **useful because:** The chips are physically attached over USB today, so the owner can validate the real microphone/modem/playback path now instead of discovering an audio regression during a call. The Mac runs the existing serial/J-Link fixture, the relay turns raw counters into a pass/fail explanation, and no microphone content is recorded.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** Use a cheap background parser for bounded serial logs and threshold comparison; reserve realtime for the owner's spoken request and a short diagnosis.
- **latency:** Start within 2 s, collect a 30–90 s fixture run, then return a concise result with packet loss, encode/decode timing, underruns, and the first failing criterion.
- **cost:** Under $0.01 per run; the dominant cost is local fixture time, not inference.
- **security:** Serial output can contain paths or identifiers; redact those from relay logs. The fixture must use synthetic audio only and must never run arbitrary shell supplied by the owner without a fixed allowlisted procedure. Preserve the raw receipt locally for reproducibility.
- **missing:** A fixed Mac bench procedure that invokes the accepted audio_path_diagnostic_fixture over the currently connected USB devices; Bounded serial-log ingestion with exit status and timestamps joined to one job receipt; A small result schema shared by firmware, Mac, and relay

### "“Do this across my Mac, browser, and phone, but only call it done when every surface confirms it.”"
- **useful because:** This is the system's single most useful missing behavior: one spoken intent can produce a coordinated outcome rather than a chain of unverified clicks. For example, save a browser invoice to a Mac workbench folder, add the due date to Calendar, and send the link to the owner's phone—with a durable checkpoint if any surface drops.
- **path:** pendant → relay → mac-planner → browser-extension → ios-control → dashboard
- **model tier:** Use a slower background model to decompose and validate the plan; use realtime only to clarify one ambiguity and report completion. Deterministic executors perform each step and a receipt checker validates resulting state.
- **latency:** Plan in under 5 s; execute independent steps in parallel where safe; report partial completion within 15 s and continue recoverable work in the background. Never say “done” until each requested surface has a positive receipt.
- **cost:** Roughly $0.03–$0.10 per multi-surface job; browser/page interpretation and verification dominate, while file/calendar/message operations are cheap.
- **security:** This can move private documents and send external messages. Keep a per-step redacted audit trail, show the exact touched resources on the dashboard, and stop on ambiguous recipient, destructive file operation, or external send unless the owner's policy explicitly permits it. Retries must be idempotent so a dropped link cannot duplicate a message or calendar event.
- **missing:** A shared job graph/receipt schema spanning browser, Mac, iPhone, and pendant events; Reliable browser dispatch for list/read/navigate actions (currently ambiguous in the live resolver); Postcondition readers for Calendar, Files, browser state, and iPhone apps; A resumable cross-surface orchestrator that uses workbench handoffs without claiming incomplete work is finished

### "“Where did I see the thing about the blue contract?” — search my current Mac files, open browser sessions, Calendar/Mail, and the mirrored iPhone, then answer with the exact source and a link or app location.”"
- **useful because:** Today information is fragmented across authenticated surfaces the owner cannot search together. This would turn a vague spoken memory into a provenance-backed answer, rather than an ungrounded model guess or a manual hunt through tabs and apps.
- **path:** pendant → relay → mac-planner → browser-extension → ios-control → dashboard
- **model tier:** Use a cheap background retrieval/ranking model over bounded source extracts; use realtime only to ask one clarification and speak the ranked answer.
- **latency:** Acknowledge immediately; return first grounded candidates in 5 seconds and continue deeper search for up to 20 seconds. Every result must identify its source surface and timestamp.
- **cost:** $0.02–$0.08 per search, dominated by OCR/page extraction and reranking; local file and calendar queries are inexpensive.
- **security:** Search results may expose private mail, work portals, or phone content. Keep raw extracts on-device, send only redacted candidate passages to the relay, scope searches to explicitly named sources when possible, and never search a third-party authenticated site merely because it is open.
- **missing:** A unified, permission-scoped index spanning local files, browser sessions, Mail/Calendar, and iPhone Mirroring; Stable browser read operations and a bounded iPhone content reader; Source provenance IDs that survive relay summarization; A spoken disambiguation flow when two sources are equally plausible

### "“Show me exactly what will leave this Mac, then send it.” — preview the final text, file, recipients, destination, and browser/phone actions on the pendant, and after my spoken approval execute the complete share."
- **useful because:** The owner gets one reliable boundary between private local context and external communication. Today the system can act across surfaces, but it cannot produce one comprehensible, end-to-end disclosure preview before a message, upload, or phone share.
- **path:** pendant → relay → mac-planner → browser-extension → ios-control → dashboard
- **model tier:** Use a background model to assemble and redact the deterministic preview; realtime handles the short spoken approval and reports the final receipt. No model should invent recipients or mutate the payload while presenting the preview.
- **latency:** Preview in under 3 seconds; approval-to-action under 8 seconds; if any destination changes after approval, invalidate the preview and stop.
- **cost:** $0.01–$0.05 per send, mostly payload classification and redaction; execution and receipt verification are local.
- **security:** The preview itself can contain secrets, so show it locally on the pendant/dashboard with redacted relay logs. Bind approval to a content hash, recipient set, and destination; never reuse approval after a retry or payload change. This is an explicit owner policy choice, not an assumption about the current FULL_CONTROL_MODE.
- **missing:** A canonical cross-surface payload and recipient manifest; A local pendant/dashboard preview channel with enough text for meaningful review; Hash-bound approval and post-send verification across browser and iPhone; Owner-configured policy entries for which destinations may be approved by voice

### "“I’m moving away from the desk — keep my attention coherent.” — coordinate Mac media, iPhone Mirroring, browser audio, and the pendant so interruptions are ducked, queued, and restored without losing the task state."
- **useful because:** The owner's attention currently belongs to separate devices: a Mac video can play over a pendant response, an iPhone call can steal focus, and queued alerts can arrive at the wrong moment. A single attention handoff would make the system feel continuous while the owner moves between desk and phone.
- **path:** pendant → relay → mac-planner → ios-control → browser-extension → dashboard
- **model tier:** Use deterministic event arbitration and a cheap background state machine; realtime is only for conversational audio and should not decide whether to interrupt.
- **latency:** Detect a competing audio/focus event within 250 ms, duck or queue within 500 ms, and restore the prior media/task state within 2 seconds after the interruption ends.
- **cost:** Below $0.01 per transition; this is primarily event routing and local audio/UI control, with no model call for ordinary transitions.
- **security:** Do not capture or transcribe unrelated calls or media. Store only app names, durations, and opaque task IDs. The owner must be able to force a local privacy latch that blocks all cross-surface attention events, and restoring media must not send messages or resume external actions.
- **missing:** A shared attention-state protocol between pendant, relay, Mac, browser, and iPhone; Reliable foreground/audio and call-state events from iPhone Mirroring and browser; A local queue with priority, expiry, and restoration checkpoints distinct from the existing alert inbox; Per-app owner policy defining which sources may interrupt and which may only queue


## What it asked for

### `t24-rz9r` (tool) — browser_context_action
- why: The browser extension is online, but the current browser wrapper resolves list/read/snapshot/navigation ambiguously and cannot reliably inspect the active tab. Cross-surface tasks need a deterministic read before acting.

```json
{
  "type": "object",
  "properties": {
    "operation": {
      "type": "string",
      "enum": [
        "browser_list_tabs",
        "browser_snapshot",
        "browser_read_page",
        "browser_navigate"
      ]
    },
    "session_id": {
      "type": "string"
    },
    "url": {
      "type": "string"
    },
    "redact": {
      "type": "boolean"
    }
  },
  "required": [
    "operation"
  ]
}
```

## Its own summary

Round 299 produced three recorded cross-node capabilities: dependable Mac-to-real-iPhone handoff from the current context; a fixed synthetic USB audio-bench report; and verified multi-surface completion with durable partial receipts. I also confirmed live Mac state: AI Pendant Agent has Accessibility and Screen Recording, synthesized input is landing, iPhone Mirroring is foreground, and four browser sessions are present. I queued browser_context_action (t24-rz9r) with real enum operations and informed browser-extension.

**Biggest unknown:** The remaining hard blocker is deterministic browser read/dispatch: the active browser is real, but browser inspection/list/read/navigation currently resolves ambiguously. After that, semantic selected-text/document extraction, stable ios_* action/postcondition receipts, and a shared cross-surface job graph are still needed.

