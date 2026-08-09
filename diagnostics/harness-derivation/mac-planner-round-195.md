# Harness derivation — mac-planner — round 195

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-accessibility-and-screen-recording** — The live Mac observation now reports AI Pendant Agent trusted for Accessibility, synthesized input verified, secure input inactive, and Screen Recording true; UI actions can reach the screen. This supersedes the older denied snapshot for current runtime state.
  - evidence: mac_readonly_inspect foreground_app resolved to GET /observe at 2026-08-08T02:39:18.952Z; response accessibility.trusted=true, eventsPost=true, screenRecording=true, uiActionsWillReachTheScreen=true.

## Capabilities it proposed

### "If the pendant has no cellular signal, let me keep talking and listening through it while it is plugged into my Mac."
- **useful because:** The hardware is physically connected now but LTE registration is not. This would make the pendant useful in dead zones and during development instead of silently becoming a paperweight, while preserving the same microphone, button, LED, and 24 kHz playback experience.
- **path:** pendant → mac-planner → relay-realtime → mac-vision
- **model tier:** Realtime for the voice turn; no background model is needed except optional connection diagnostics.
- **latency:** Button-to-session establishment under 1 second; uplink/downlink added latency under 100 ms over USB plus the existing relay path; reconnect after cable loss within 2 seconds.
- **cost:** Negligible inference overhead beyond the conversation; engineering cost is a USB serial framing/bridge implementation and test time.
- **security:** USB possession becomes local access to the voice session. Bind the bridge to the paired pendant identity, show an unmistakable LED connected state, and stop forwarding audio immediately when the cable disappears. Do not expose arbitrary serial commands through the voice path.
- **missing:** A real mac_serial_exchange capability (the pending request is still unavailable); A Mac bridge route that converts framed pendant PCM/control packets to the existing relay audio pipeline and back; A pairing/session handshake and cable-loss cleanup in relay-realtime

### "When I ask 'what am I looking at?', use the Mac screen and browser context to answer through the pendant, without me touching the keyboard."
- **useful because:** This is the highest-value cross-node loop: the worn device supplies the natural question and audio output, the relay coordinates it, and the Mac is the only node that can see the current screen and authenticated browser. It turns the system from a voice chatbot into an assistant that understands the owner's immediate work.
- **path:** pendant → relay-realtime → mac-vision → browser-extension → mac-planner
- **model tier:** Realtime multimodal model only for the captured visual/context turn; use a small classifier first to decide whether a screen read is actually requested.
- **latency:** Capture current screen/window and browser metadata within 500 ms; answer begins within 2 seconds and stays to the owner's default one spoken sentence.
- **cost:** Roughly $0.01–$0.05 per visual turn depending on image tokens; browser metadata can replace a screenshot when sufficient and reduce cost.
- **security:** Screen capture can reveal passwords, secrets, and private communications. Require an explicit phrase or button action, crop to the foreground window, redact known password fields and secure-input screens, and discard the image after answer generation. Never run actions merely because the screen was inspected.
- **missing:** A resolved read-only ui_snapshot capability with a stable schema (the current resolver tie is still ambiguous); A relay route that correlates one pendant utterance with one Mac snapshot and enforces ephemeral retention; A browser context adapter that supplies DOM-visible title/selection while excluding credentials

### "Tell me, through the pendant, what the Mac agent changed in the last hour and show me the files or tabs it touched."
- **useful because:** Automation is currently powerful and FULL_CONTROL_MODE has no approval gate. An owner-facing spoken audit makes that power legible: it joins relay job receipts with Mac action results and browser activity, so the owner can detect an unexpected mutation without opening logs.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Cheap background model to aggregate and redact receipts; realtime only to answer the owner's spoken query from a cached hourly ledger.
- **latency:** Maintain the ledger continuously with no conversational latency; answer a one-hour audit query in under 2 seconds, with a follow-up drill-down on demand.
- **cost:** Under $0.005 per query if receipts are structured; storage and redaction dominate, not model tokens.
- **security:** Audit records can contain URLs, filenames, document text, and secrets. Store hashes, resource classes, and redacted labels by default; retain full details only in the local workspace. Never speak secret values or page bodies. The audit must be append-only and distinguish planned, attempted, succeeded, and failed actions.
- **missing:** A unified append-only receipt schema spanning POST /execute, browser commands, and relay jobs; A relay query route that filters receipts by time and session and returns redacted touched-resource summaries; A Mac-side post-action receipt for FULL_CONTROL actions, since the current action path bypasses actionRisk and does not provide a typed approval event

### "When you tell me something through the pendant, let me ask 'why?' and hear the exact sources, timestamps, and uncertainty behind that answer."
- **useful because:** A short spoken answer is convenient but currently opaque. Provenance-on-demand would let the owner trust or challenge a briefing, browser summary, or Mac action without opening logs: the pendant asks, the relay traces the answer, and the Mac/browser provide the underlying evidence.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Use a cheap structured provenance formatter; reserve realtime inference for the owner's follow-up question and only when evidence needs verbal compression.
- **latency:** Keep provenance records alongside every answer; return a two-sentence spoken explanation within 2 seconds, with an optional deeper written artifact in the workspace.
- **cost:** Less than $0.005 per follow-up when source references are structured; storage and redaction are the main costs.
- **security:** Source titles and URLs may expose private mail, work pages, or secrets. Speak only redacted labels by default, require an explicit request for full details, and preserve the original evidence locally rather than sending it back through the voice channel. Provenance must distinguish observed facts from model inference.
- **missing:** A provenance envelope attached to relay answers, browser summaries, and Mac plans/actions; A durable local evidence bundle with source hashes, timestamps, and retention expiry; A relay query that resolves a spoken follow-up to the exact prior answer without replaying unrelated private context

### "Before an agent sends, deletes, or buys something in my browser, let me approve it with one deliberate press on the pendant and hear exactly what will happen first."
- **useful because:** The owner wants automation but not invisible high-impact mutations. A physical confirmation channel is harder to trigger accidentally than a browser click and works while the Mac remains focused elsewhere. It restores meaningful control without turning ordinary reading or drafting into approval dialogs.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** Realtime only for the short spoken preview; policy evaluation and token matching should be deterministic and local to the relay/browser bridge.
- **latency:** Preview within 1 second; approval press accepted for 30 seconds; execution receipt within 3 seconds or explicit expiry/failure.
- **cost:** Near-zero model cost for structured actions; one short realtime response per high-impact approval.
- **security:** A stolen or unattended pendant could authorize actions. Bind tokens to a specific action hash, browser session, account scope, and short expiry; invalidate on any page or amount change; never treat a generic button press as approval. Keep the owner's configurable policy authoritative.
- **missing:** A relay-issued single-use approval-token route understood by the browser bridge; A browser-side action hash and preview protocol for send/delete/purchase operations; Firmware/bridge handling for a confirmation press without adding a new gesture or confusing the existing bookmark button


## What it asked for

_Nothing._
