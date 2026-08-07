# Harness derivation — browser-extension — round 105

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser availability round 105** — Live browser access is currently unavailable: GET /browser/status reports online=false, only home-chrome with no tab; POST /execute browser_navigate to example.com timed out. All five browser enqueue grants remain schema-only stubs.
  - evidence: GET /browser/status returned online=false and pendingCommands=9; POST /execute browser_navigate returned no response within 20s.

## Capabilities it proposed

### "“What am I looking at?” (or press the pendant’s browser button) and hear a concise explanation of the Safari page or selected region I’m currently viewing, with links back to the source; do not save the page after answering."
- **useful because:** This is an immediate, low-friction bridge between the owner’s private browser session and the pendant. It can explain a logged-in dashboard, error, chart, or article without the owner reading aloud or exposing credentials, while keeping the page ephemeral rather than turning it into a durable watch or briefing.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use the realtime model only for the owner’s spoken question and a short spoken answer; use a cheaper background model for DOM cleanup/region extraction when the page is large, then pass only the compact evidence to realtime.
- **latency:** Target 2–5 seconds after the button/utterance: 0.5–1 s to capture the active tab or selection, 1–3 s for extraction and summarization, then streaming speech. Fall back to title/URL plus visible text if extraction fails.
- **cost:** Typically one compact realtime turn plus one inexpensive extraction call; roughly dominated by realtime input/output tokens, with extraction under a few cents unless a screenshot/large DOM is required.
- **security:** The extension must capture only on explicit button press or the matching utterance, never continuously. Send visible/selected text and URL, redact password/payment fields and hidden DOM, mark the result ephemeral with a short TTL, and do not persist page contents or screenshots. Ask before any click, typing, navigation, or other mutation; this capability is read-only.
- **missing:** A functioning browser command enqueue implementation (all currently granted enqueue tools are schemas/stubs).; A live Safari heartbeat and an active-tab/selection capture command; current /browser/status shows Safari offline and no tab for home-chrome.; A bounded ephemeral context handoff from browser extraction to the realtime voice pipeline, with DOM redaction and automatic deletion.

### "“Guide me through this page one step at a time.” I want the pendant to describe the next useful control in my currently open private Safari page, wait for my spoken confirmation, then re-check the page and continue—without clicking or typing for me."
- **useful because:** This would make unfamiliar authenticated dashboards, government forms, and complex settings usable while the owner keeps their hands free. It provides navigation assistance without handing over control or requiring the owner to read a screen aloud, and it works on private pages that public web tools cannot access.
- **path:** browser-extension → relay-realtime → pendant → mac-planner
- **model tier:** Use a cheaper background model to normalize the page’s accessibility tree and identify candidate controls; use the realtime model only to maintain the short spoken turn, answer follow-up questions, and choose the next step from the compact current-state description.
- **latency:** First instruction within 3 seconds of the request; after each confirmation, re-capture and answer within 2–4 seconds. Stop cleanly if the tab changes, becomes unavailable, or the page contains an unrecognized destructive action.
- **cost:** One small extraction call per step and a short realtime exchange; cost scales with the number of confirmed steps, not the full page size. The dominant cost is repeated realtime audio turns.
- **security:** Read-only by default: no click, type, submit, navigation, or clipboard access. Capture only the active tab after an explicit request, exclude password/payment/hidden fields, and retain the accessibility snapshot only for the current step. Show the URL/title and identify destructive controls clearly. No credentials or page snapshot should be sent to unrelated surfaces.
- **missing:** A working Safari extension command queue and heartbeat/active-tab identity.; A browser action that returns a compact accessibility tree with stable element labels, roles, and bounding regions rather than only raw page text.; A short-lived step session that compares successive captures, detects tab/page changes, and feeds only the current candidate controls to relay-realtime.; Pendant-level confirmation/correction intent handling (yes, next, back, stop, that one, explain it) tied to the browser step session.

### "“Explain this private form field by field in plain English, tell me what information it is asking for and what the consequences are, and remember my place while I answer aloud.” Do not fill or submit anything."
- **useful because:** Owners routinely face confusing medical, benefits, immigration, insurance, and account forms behind logins. Today they must copy sensitive fields into a separate assistant or decode them alone. This would provide contextual explanations grounded in the actual form while preserving owner control and avoiding unauthorized completion.
- **path:** browser-extension → relay-realtime → pendant → mac-planner
- **model tier:** Use a background model to segment labels, help text, validation rules, and nearby policy text into field records; use realtime only for the owner’s spoken questions and concise explanations. Escalate ambiguous legal or medical interpretation as uncertainty, not a confident answer.
- **latency:** Explain the first visible field within 3 seconds and subsequent fields within 1–2 seconds from a spoken “next”; preserve a resumable field index if the owner pauses or switches tabs.
- **cost:** One extraction/segmentation call per form view plus short realtime turns; costs are dominated by spoken interaction, with field records kept compact.
- **security:** Capture only the current form after an explicit request. Exclude existing values, password fields, uploaded documents, and hidden inputs unless the owner explicitly asks about one. Keep field metadata ephemeral and never transmit spoken answers as form mutations. Clearly distinguish page-provided instructions from model interpretation.
- **missing:** Active-tab browser capture with form-label/help-text and validation-rule extraction.; A field-session state store containing only field IDs, labels, explanation status, and current position, with short TTL.; A relay intent mode that routes spoken answers to explanation/navigation rather than browser typing.; A reliable no-tab and cross-origin-frame error path.


## Changes it proposed to its own stack

### `integration` — Add an explicit ephemeral browser-to-voice handoff in the local agent: on a pendant intent or browser-button event, dispatch browser_snapshot/read_page to the active Safari tab, run deterministic redaction (password/payment/hidden inputs plus truncation), attach tab URL/title and extraction timestamp, stream the compact payload into the realtime pipeline, and delete the payload after the spoken response or a 60-second TTL. Return a typed failure when no live tab/extension exists instead of waiting for the 45-second browser timeout.
- **owner gets:** The owner can ask about whatever is on their private screen and get an answer quickly without copying text, while page contents do not accumulate in memory. When Safari is unavailable, they get an immediate understandable answer rather than a long silence.
- effort: Medium: browser bridge event/command plumbing, redaction and TTL store, one relay adapter, and end-to-end tests for no-tab, extraction failure, and large DOM cases.  ·  risk: A redaction bug could leak sensitive page text; mitigate with deny-by-default field filtering, size limits, audit metadata without content, and automatic deletion. A stale active tab could be summarized; include URL/title/timestamp and say when capture is stale. Recovery is a normal retry after the extension heartbeat returns.
- cost: Negligible storage cost due to 60-second TTL; one small extraction plus one realtime turn per request. Large pages should be truncated before model input.  ·  latency: Reduces failure latency from the current 20–45 second timeout to an immediate no-tab response; successful path target 2–5 seconds.
- security: Improves privacy versus durable page watches: explicit capture only, no continuous observation, no persistence, field redaction, and content deletion after response.
- depends on: A real implementation of browser command enqueue and Safari heartbeat/active-tab reporting; A pipeline event or intent hook that can correlate the owner’s utterance/button press to one browser capture; Deterministic browser payload redaction and TTL deletion


## What it asked for

_Nothing._
