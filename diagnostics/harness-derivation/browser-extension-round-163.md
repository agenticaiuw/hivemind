# Harness derivation — browser-extension — round 163

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser live state** — Safari extension is online with 9 tabs, including an authenticated Gmail inbox and active X home tab; POST /execute with actions:[{type:'browser_list_tabs'}] successfully returned tab IDs and receipts.
  - evidence: Live POST /execute response at 2026-08-08T02:18:13Z: ok:true, 9 open web tabs, Safari extension online.

## Capabilities it proposed

### "“Check the authenticated pages I already have open and tell me what actually needs my attention.”"
- **useful because:** This is the highest-value browser-only capability: the extension can see logged-in work and service pages that relay/web search cannot. It turns nine open tabs into a prioritized spoken answer, while preserving the owner's existing sessions and avoiding a fabricated site list. The owner supplies per-origin read/extract/redact/never-store rules; with an empty configuration it reports only titles/URLs and asks to add origins.
- **path:** browser-extension → mac-planner → relay-realtime → relay-realtime → pendant
- **model tier:** Background model performs page extraction, diffing, and priority ranking; realtime is used only to answer a follow-up or speak the final short result.
- **latency:** Initial scan 10–30 seconds for 3–10 tabs; spoken result within 3 seconds after the scan. A scheduled scan can run while the owner is away.
- **cost:** Roughly $0.01–$0.08 per scan depending on extracted text and number of tabs; browser I/O and diffing dominate less than model summarization.
- **security:** Page text may contain mail, financial, or work secrets and must stay in the local agent unless the owner’s explicit per-origin policy permits relay/model processing. Persist only hashes and redacted issue summaries, never raw page text. Do not infer allowed origins or sensitive categories; require the owner’s inspectable configuration. Reading is reversible; any suggested action stops before submission.
- **missing:** A browser page-watch/scan job that can enumerate and extract configured tabs, compute semantic diffs, and attach tab IDs; An owner-editable per-origin and per-category privacy configuration, initially empty; A background scheduler that invokes the scan and sends a compact result to the relay; A prioritizer that recognizes actionable changes without opening links or submitting forms

### "“Fill out this authenticated form from the document I’m looking at, then read me exactly what would be sent without submitting it.”"
- **useful because:** The browser can reach the logged-in form and the Mac can locate the source document, but neither alone can safely bridge the two while the owner is away from the keyboard. This produces a ready-to-review draft, speaks a field-by-field diff through the pendant, and leaves the final submit as a deliberate owner action.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → pendant
- **model tier:** A background model extracts and normalizes source fields; mac-vision/browser automation performs deterministic field filling; realtime handles only the owner’s short spoken corrections and review.
- **latency:** 2–8 seconds for a short form, up to 30 seconds for multi-page forms. Stop at the review screen and return an exact payload preview.
- **cost:** About $0.03–$0.20 per form, dominated by vision/model calls for ambiguous fields; deterministic browser actions are cheap.
- **security:** Credentials remain in Safari. Never transmit raw form contents or source documents beyond the local Mac unless the configured origin permits it. Mask high-risk fields (passwords, payment numbers, government IDs) in speech and receipts by default. Never click submit, send, purchase, or consent controls; preserve the filled page as a local draft and provide a clear undo/reload path.
- **missing:** Cross-surface field provenance linking each filled value to a source document span; A browser form schema/DOM extractor that distinguishes editable fields from submit/consent controls; A local review artifact with exact outgoing payload and per-field confidence; Pendant interaction for approve/edit/reject individual fields without requiring keyboard access

### "“I’m looking at a logged-in page—tell me what this section means and what I need to do next, without saving the page.”"
- **useful because:** This is an on-demand private web copilot unavailable to the relay or search: the browser extension reads the exact authenticated view, the owner can point by selecting a section or using the active tab, and the pendant gives a hands-free explanation plus next steps. It avoids the latency and privacy cost of continuously indexing every page.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** Realtime handles the short question and concise spoken answer; a cheaper background model can parse a long page locally before the realtime response. Use vision only when DOM extraction cannot identify the selected region.
- **latency:** 2–5 seconds for a normal section; under 10 seconds for a long or visually rendered page. If extraction fails, say so rather than hallucinating.
- **cost:** About $0.01–$0.06 per question; page extraction is local and the realtime summary is the main cost.
- **security:** Raw authenticated page text should remain on the Mac by default and be redacted before any relay call. Do not store page content, screenshots, or question transcripts unless an explicit origin policy allows it. Never click links or mutate the page as part of explanation; if the owner asks for an action, create a separate preview step.
- **missing:** Active-tab/selection targeting from Safari so the owner can identify the relevant section unambiguously; A local redaction-and-compression stage that sends only the selected section or structured facts; A one-shot browser question route that binds extraction, provenance, and spoken response to a tab/session ID; A no-persistence transcript mode for authenticated content

### "“While I’m in this authenticated web meeting, listen for the agenda item I name, look up the relevant private document in another tab, and whisper me a concise answer through the pendant—without speaking or sending anything into the meeting.”"
- **useful because:** Today the browser can hold the meeting session, but it cannot privately connect meeting context, another authenticated tab, and the owner’s worn audio channel. This would let the owner participate more effectively without exposing the assistant to other attendees or risking an accidental chat message. It is a genuinely multi-surface capability: Safari supplies private session access, the Mac correlates tabs and local documents, the relay handles the spoken request, and the pendant provides a private low-disruption response.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** Realtime model handles the low-latency whispered question and response; a cheaper background model indexes only the explicitly selected agenda/document snippets during the meeting.
- **latency:** Whisper response in 3–6 seconds after a pendant request; never block or alter meeting audio/video. If source retrieval takes longer, return a brief acknowledgement and finish asynchronously.
- **cost:** Approximately $0.03–$0.15 per question, dominated by realtime audio and multimodal context; local tab correlation and document lookup are inexpensive.
- **security:** Meeting audio and private documents are highly sensitive. Default to push-to-ask, selected-tab/document scope, no recording, no transcript persistence, and local redaction before relay processing. The assistant must be physically and visually silent to other participants, never click meeting controls, post chat, or unmute. Show source tab/document and confidence in the owner’s private pendant response.
- **missing:** A meeting-isolated browser context that can identify the active call tab while forbidding meeting mutations; A local, ephemeral audio/DOM correlator that accepts only the owner’s explicit agenda cue and selected private source tabs; A private pendant whisper channel with ducking/volume restoration and an interruption-safe response queue; A provenance packet linking each answer to the exact meeting cue and source document without retaining raw content; A policy configuration the owner can explicitly set for which meeting origins and document origins may be combined

### "“Build me a private evidence packet for this dispute from the logged-in order, receipt, and policy tabs, and leave the claim ready for my review.”"
- **useful because:** The owner cannot currently ask one node to reconcile several authenticated tabs into a coherent, source-linked case. This would turn scattered private records into a dated evidence bundle, identify contradictions or missing proof, and prepare—but never send—the claim. It uses browser-only access that web search and the relay do not have, while the Mac can generate a local artifact the owner can inspect.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → pendant
- **model tier:** Background model performs document extraction, timeline construction, and contradiction checking; realtime is only for the owner’s clarifications and a brief spoken status.
- **latency:** 30–90 seconds for three to eight tabs; return a local draft packet and a short pendant summary. Long-running extraction may continue in the background.
- **cost:** About $0.10–$0.60 per packet, mostly OCR/vision and synthesis over several pages; local PDF assembly is negligible.
- **security:** Receipts, addresses, and payment details remain on the Mac by default. Redact account numbers and unrelated orders from the packet. Store the draft encrypted and temporary, with an explicit expiry. Do not submit a claim or send an attachment; preserve source URLs and timestamps so the owner can verify every assertion.
- **missing:** A local multi-tab evidence collector with per-origin scope and deduplication; Source-span provenance and contradiction detection across rendered pages and downloaded documents; An encrypted, expiring packet artifact with a human-readable review view; A browser handoff that opens the exact source tab beside each generated claim

### "“Save this private web task exactly where I left it, remind me later on the pendant, and resume it in the same authenticated tabs without losing my place.”"
- **useful because:** A dropped Mac link, crash, or interruption currently destroys the owner’s working context. This would make the browser an interruptible extension of the wearable: the Mac records a redacted task capsule (tabs, headings, scroll/selection anchors, and reversible field state), the relay schedules a reminder, and Safari restores the exact session when the owner returns. It is more useful than reopening URLs because it preserves which account, page section, and draft state were active.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** No expensive model for capture/restore; use a cheap background model only to label the capsule and generate a short reminder. Realtime is reserved for a spoken ‘resume that task’ request.
- **latency:** Capture under 1 second; restore under 5 seconds for a normal task. If a session expired or a page changed, show a discrepancy report instead of silently continuing.
- **cost:** Under $0.01 per capture/restore; storage and browser operations dominate, with occasional small-model labeling.
- **security:** Never persist cookies or credentials. Encrypt the capsule locally, store only configured origins, redact secrets and form values by default, and expire capsules automatically. Restoring a draft must not submit or send anything; display changed fields and require the owner’s existing action policy for any mutation.
- **missing:** An encrypted local task-capsule store with origin allowlist, expiry, and redaction; Safari APIs to restore tab order, scroll/selection anchors, and safe draft state after a restart; Relay reminder records that point to a capsule rather than copying page text; A pendant command and response format for listing, pausing, and resuming capsules


## Changes it proposed to its own stack

### `browser-harness` — Add a browser_capture_selection action that returns only the user-highlighted DOM text plus a stable tab URL, heading path, and character offsets; require the extension to clear the captured buffer after one request and expose a no-persistence receipt. If no selection exists, return a structured 'no selection' result rather than the whole page.
- **owner gets:** The owner can highlight one confusing clause or line in a logged-in page and ask the pendant for an explanation without exposing an entire inbox, dashboard, or document. It makes private browser help precise, faster, and safer than whole-page extraction.
- effort: Medium: Safari content-script selection capture, command/result schema, tab/session affinity, and local redaction tests.  ·  risk: DOM sites can report stale or deceptive selection text; show URL and heading provenance and say when capture is empty. Recover by falling back to an explicit page read only when the owner asks. Never mutate the page.
- cost: Negligible runtime/API cost; roughly 1–2 weeks engineering effort, no hardware cost.  ·  latency: Sub-second capture and 1–3 seconds less model processing because context is smaller.
- security: Improves privacy by minimizing authenticated text leaving the Mac; still needs per-origin policy and masking for selected secrets.
- depends on: The existing POST /execute browser action queue and Safari extension result receipts; The per-origin redaction machinery in local-agent/httpPolicy.js, originFanOut.js, browserSessions.js, and redaction.js; The owner choosing whether selected text may be sent to the relay/model


## What it asked for

_Nothing._
## Its own summary

Safari is live and now has 9 tabs; I verified the real path is POST /execute with an actions array, not the ambiguous browser enqueue wrappers. I recorded four owner-facing proposals: authenticated attention radar, authenticated form drafting with spoken field review and no submit, one-shot private explanation of a selected logged-in page section, and a concrete browser_capture_selection harness change. The first is the strongest system-level capability because it combines private Safari sessions, Mac extraction, relay ranking, and the pendant’s offline alert path.

**Biggest unknown:** The owner has not supplied the explicit per-origin/per-category privacy configuration (which authenticated origins may be read, spoken, or persisted). I also still need the extension-side selection-capture action and a scheduler/page-watch implementation; do not invent site rules until the owner configures them.

