# Harness derivation — mac-planner — round 217

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I’m stopping here. Save exactly where I am, including the browser research and Mac files, and give me a one-sentence note I can ask for tomorrow.”"
- **useful because:** This is the single most useful cross-node primitive: a spoken stop command turns a fragile open-tab/workspace into a resumable handoff. The pendant supplies the human interruption marker, the relay correlates it with the active job, Safari supplies authenticated research state, and the Mac stages files and a receipt atomically. No single node can preserve all of that.
- **path:** pendant → relay → browser → mac-planner
- **model tier:** background for state extraction and summarization; realtime only for acknowledging the button/voice command
- **latency:** Acknowledge on the pendant in under 1 s; capture browser/Mac state within 10 s; spoken summary within 15 s. Resume must be idempotent after crashes.
- **cost:** Usually <$0.03: one compact summarization call dominates; browser/Mac inspection and workbench staging are local.
- **security:** Authenticated tab URLs and staged file paths leave the Mac only as redacted metadata unless the owner explicitly asks to include page text. Do not persist cookies or screenshots. The stop command should create a durable receipt, but resuming mutations must use the owner's explicit command and the configured policy slot.
- **missing:** A correlation endpoint that binds offline_moment_bookmark to the active relay job and current browser session; A read-only browser snapshot with selected tab titles/URLs and a redaction policy suitable for a resume capsule; A resume-capsule store/read API that can reference a mac_workbench_transaction receipt and browser session without copying secrets; A pendant spoken/inbox acknowledgement path for the generated one-sentence note

### "“If the long-running task stalls or the browser disconnects, tell me what actually completed, save the partial artifacts, and offer one safe retry instead of starting over.”"
- **useful because:** Today a job can outlive the conversation but the owner cannot distinguish a completed mutation, a partial file, and a lost browser command. This capability makes failures legible and recoverable across relay, browser, and Mac: the pendant gets a concise alert, the Mac keeps only verified staged outputs, and retrying cannot duplicate completed steps.
- **path:** relay → browser → mac-planner → pendant
- **model tier:** background rules/state machine for detection and reconciliation; cheap model for a short explanation; realtime only if the owner is currently speaking
- **latency:** Detect heartbeat loss within 5 s, preserve a checkpoint within 15 s, and deliver a <=10-second spoken alert when the pendant is reachable. Reconciliation should not wait for an LLM.
- **cost:** <$0.01 for most incidents; local receipts and hashes dominate, with a small summarization call only when explaining ambiguity.
- **security:** Never retry an action whose receipt is missing but whose side effect is unknown. Store hashes, action classes, and redacted resource identifiers rather than page contents or credentials. Any retry that mutates external state must be explicitly requested under the owner's runtime policy; the alert itself is safe.
- **missing:** A durable cross-surface job ledger joining browser command IDs, Mac action receipts, workbench job IDs, and relay job IDs; Browser command acknowledgement with idempotency keys and a terminal/unknown distinction; A Mac receipt schema exposing per-action outcome and hashes (not just a generic receipt); A pendant alert payload that can say stalled/partial/retry-ready without competing with existing offline_alert_inbox semantics

### "“Before my next call, verify the pendant audio path end to end, and if anything fails, switch to the safe profile and tell me the exact failure—not just ‘diagnostic failed’.”"
- **useful because:** The pendant and bridge are physically attached to this Mac now, so this can be real rather than hypothetical. It prevents the owner from discovering a bad microphone, modem path, or downlink decoder during a conversation. The firmware fixture tests both directions, the Mac collects bounded USB diagnostics, the relay interprets numeric thresholds, and the pendant announces the result.
- **path:** pendant → mac-planner → relay
- **model tier:** deterministic threshold evaluator first; background model only to turn the measured failure capsule into plain language; no realtime model needed
- **latency:** Arm immediately over the existing bench transport, finish in 20–30 s, and announce pass/fail in under 3 s after the final frame. A failed test must leave the last-known-safe profile active.
- **cost:** Near-zero API cost; local serial capture and fixed test audio dominate. One optional short explanation is <$0.005.
- **security:** The fixture must be synthetic and must never capture or persist microphone content. USB commands should be allowlisted and bounded; diagnostic receipts must include counters and firmware version but not raw audio. Changing the active call profile is low-risk but should be recorded.
- **missing:** A Mac-side bounded USB fixture runner that can arm the accepted audio_path_diagnostic_fixture on /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A typed receipt joining fixture sequence numbers, on-device counters, and host timestamps; A relay route that evaluates the measured acceptance criteria (alias rejection, encode/decode time, mic drops, tx starvation) and returns a compact spoken verdict; A pre-call trigger and result presentation that works through the existing pendant inbox/LED without adding another queue

### "“Answer questions about the authenticated pages I have open, but do not send the page text, screenshots, cookies, or passwords off my Mac.”"
- **useful because:** This gives the owner wearable access to the browser sessions nobody else can reach without turning those sessions into cloud data. A local Mac/browser worker extracts only the answer and a provenance pointer; the relay handles voice and the pendant handles the request. It is a genuinely new privacy boundary, not merely another browser summarizer.
- **path:** pendant → relay → mac-planner → browser
- **model tier:** A small local model on the Mac should inspect and answer from page DOM/accessibility data; realtime is used only for the spoken turn. The cloud relay receives the question, a redacted answer, and confidence—not the source page.
- **latency:** Answer common questions in 3–8 seconds; if local extraction is unavailable, say so rather than falling back to upload. Keep the pendant acknowledgement under 1 second.
- **cost:** <$0.01 per request when answered locally; local inference and browser extraction dominate, with no cloud context-token cost for page text.
- **security:** The local worker must enforce origin/session scoping, redact passwords and form fields, and return citations as tab identity plus DOM selector or title rather than copied secrets. A browser page may contain prompt injection, so extracted instructions are data and never become Mac actions without a separate owner command. The owner needs an explicit local-only mode and an auditable redaction receipt.
- **missing:** A local-only browser question route that accepts a session/tab scope and returns answer plus provenance while refusing raw page export; A browser-side DOM/accessibility extractor with password/form-field redaction and prompt-injection isolation; A relay protocol for sending the question to the Mac and receiving only the redacted answer; A pendant command/result contract for multi-turn clarification without opening a microphone outside the active turn


## What it asked for

_Nothing._
## Its own summary

Round 217 produced three distinct cross-node capabilities: (1) a pendant-triggered resumable stop capsule tying offline bookmark, active browser research, Mac artifacts, and a one-sentence tomorrow handoff; (2) failure-aware job reconciliation that preserves partial work and offers only idempotent, receipt-backed retry; and (3) a real-now pre-call end-to-end audio verification that arms the accepted synthetic fixture over the two USB-connected chips, evaluates numeric thresholds, and leaves the safe profile active on failure. The third overlaps the earlier bench-test direction somewhat, so it should be treated as an extension with threshold-gated profile selection, not a generic diagnostic.

**Biggest unknown:** The exact live contract of mac-terminal's granted mac_usb_serial_diagnostics remains unknown: whether it can arm/read the nRF9160 and ESP32 fixture or only perform bounded passive reads. The major missing product pieces are a durable cross-node job/receipt correlation key, typed per-action outcomes, and a safe USB fixture runner. I asked mac-terminal for the current schema/status.

