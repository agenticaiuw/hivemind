# Harness derivation — browser-extension — round 196

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What on the authenticated pages I already have open needs my attention right now?”"
- **useful because:** This turns the browser's unique access into an immediate, owner-triggered triage instead of a generic web search. It reads only the currently open logged-in tabs, groups actionable changes (deadlines, failed payments, requests, alerts), cites the originating tab, and delivers a short spoken answer plus an offline pendant alert if it is long. No invented site allowlist is needed: the task scope is the tabs the owner explicitly has open.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Background/cheap model for extraction and ranking; realtime only for the owner's follow-up voice question.
- **latency:** 5–15 seconds for 3–8 tabs; return partial results per tab if one hangs, rather than blocking the whole digest.
- **cost:** ~$0.01–$0.05 per run depending on extracted text; browser I/O and compact claim ranking dominate, not generation.
- **security:** Authenticated page text leaves Safari only to the local Mac/relay for this explicit request. Do not persist HTML or screenshots; emit host-keyed, 24-hour, ≤200-character claims with URL provenance. Ship the per-origin/category configuration empty and let the owner populate it later. Never include a tab's full content in the spoken alert.
- **missing:** A multi-tab browser action that returns tab IDs and bounded text/metadata in one job (the current extension has command-level actions but no reliable active-tab/list result exposed to this agent); A triage job that joins browser claims with local Calendar/Mail only when the owner asks for cross-source context; A pendant delivery adapter that accepts the existing offline_alert_inbox payload with provenance and expiration

### "“Fill this web form up to the point of submission, then tell me exactly what would be sent and where.”"
- **useful because:** The browser can do the tedious authenticated lookup and form filling while the owner keeps control of the consequential act. It resolves names, addresses, dates, or account details from the owner's logged-in pages, shows a field-by-field before/after diff and provenance, and leaves the form staged—not submitted—for a spoken decision. This is a concrete end-to-end handoff between browser reach, Mac orchestration, and the pendant, rather than another read-only page summary.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Realtime for clarifying missing fields and reading the proposed payload aloud; background model for field extraction and validation.
- **latency:** Under 20 seconds for a normal form, with immediate progress updates and a hard stop at submit/payment/send controls.
- **cost:** ~$0.02–$0.10 per form; OCR/DOM extraction and the final field-diff explanation dominate.
- **security:** Sensitive values are handled in the browser session and should be redacted in logs, claims, and speech according to the owner's future per-origin/category config. Preserve only field names, hashes/diffs, and source URLs. Do not click submit, purchase, send, or final confirmation as part of preparation; if the owner later explicitly asks, create a separate auditable execution step.
- **missing:** A browser form model that reports field labels, values, validation errors, and submit-like controls without serializing the whole DOM; A durable staged-form token that survives a relay turn but expires when the page or session changes; A pendant-friendly field diff renderer and explicit resume/abandon command

### "“Explain the thing I’m pointing at or have selected in Safari, and tell me what I can do next.”"
- **useful because:** A pendant press plus the browser's focused element/selection makes authenticated pages conversational at the exact point of confusion—an error message, chart, contract clause, or checkout option—without asking the owner to describe it aloud. The browser supplies DOM/selection context, Mac vision supplies a screenshot crop only when the target is canvas-rendered, and the relay turns it into a short spoken explanation and optional next-step preview.
- **path:** pendant → browser-extension → mac-vision → mac-planner → relay-realtime
- **model tier:** Realtime multimodal model only for the selected region and question; cheap extraction first for DOM text and accessibility labels.
- **latency:** 2–5 seconds for DOM text; under 10 seconds if a screenshot crop is needed.
- **cost:** ~$0.005–$0.03 per question; screenshot-token usage dominates and should be avoided when accessible text suffices.
- **security:** Send only the focused element/selection and a tightly cropped image, not the entire page. Do not store the crop or page text; return an ephemeral answer and retain only a short provenance claim if explicitly requested. The owner must be able to disable visual capture per origin once the empty configuration is populated.
- **missing:** An extension command returning active tab, selection, focused element, accessibility label, and bounding rectangle; A crop-only mac-vision action that accepts that rectangle without exposing the full screen; A pendant trigger that binds a press to the current browser context and carries the owner's follow-up utterance

### "“Find the evidence for this disputed charge across my logged-in accounts, build the strongest support case, and stage the dispute without sending it.”"
- **useful because:** Today the owner must manually correlate a bank transaction, merchant order history, shipment/refund status, and email receipts, then retype the story into a dispute form. This would turn the browser's authenticated reach into a coherent, source-linked case: identify the exact transaction, collect only the relevant records, detect contradictions (delivered vs refunded, duplicate charge, wrong amount), draft a factual timeline, and stage the dispute for review. It is substantially more useful than merely filling a form because it assembles evidence across sites and explains confidence and gaps.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Background model for cross-source retrieval, deduplication, timeline construction, and contradiction checks; realtime only for clarifying which transaction and answering review questions.
- **latency:** 30–90 seconds for three authenticated sources, with incremental source-complete updates; never wait indefinitely on one site.
- **cost:** ~$0.05–$0.25 per case; authenticated page extraction, deduplication, and evidence summarization dominate.
- **security:** Financial and account data must remain ephemeral except for a redacted case manifest. Store URLs, timestamps, field-level hashes, and short claims—not page HTML, screenshots, full card/account numbers, or message bodies. Redact secrets and unrelated transactions before any cross-site join. Do not submit the dispute or send a merchant message; show the exact staged narrative and attachments first. The owner's future per-origin and per-category configuration remains explicit and empty until supplied.
- **missing:** A browser job primitive for extracting a bounded record from several authenticated origins while preserving per-field source URLs and timestamps; A local evidence vault that stores encrypted, short-lived, redacted excerpts and supports deletion as one case; Cross-source entity matching for transaction/order/receipt identifiers with contradiction and confidence reporting; A staged-dispute adapter that maps the evidence timeline to a site's form without submitting it

### "“My trip just changed—check the airline and hotel pages I’m logged into, compare realistic alternatives against my calendar, and stage the best recovery plan.”"
- **useful because:** When travel breaks, the owner needs several authenticated systems at once: airline status/rebooking, hotel policy, email itinerary, and the local calendar. This capability would produce a ranked recovery plan based on actual availability, arrival windows, cancellation penalties, and calendar conflicts, then stage the selected changes without booking or canceling anything. The pendant can deliver a terse urgent summary while the Mac/browser retain the detailed alternatives for review.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Background model for timetable/policy extraction and constraint solving; realtime model for the owner's short choice conversation and spoken plan.
- **latency:** 20–60 seconds for initial options, then refresh availability immediately before staging; partial results are useful if one provider is unavailable.
- **cost:** ~$0.05–$0.30 per disruption; authenticated extraction and repeated availability checks dominate.
- **security:** Expose only itinerary-relevant fields to the model; redact passport, payment, loyalty, and unrelated reservation data. Treat availability as volatile and timestamp every option. Staging must be reversible and must not purchase, cancel, or send a request. Retain only the chosen plan's short claims and source URLs with short expiry.
- **missing:** A multi-origin travel record schema that normalizes flights, lodging, policies, and timestamps; A calendar constraint query that returns conflicts and travel-time buffers without exporting unrelated events; A volatile-option cache with automatic expiry and revalidation before any staged action; A browser adapter for previewing rebooking/cancellation consequences without clicking the final mutation

### "“Before my appointment, reconcile the new results and messages in my logged-in patient portal with my notes and calendar, then give me a concise question list.”"
- **useful because:** The owner currently has to hunt through portal tabs and messages, remember prior notes, and decide what deserves a clinician's attention. This would extract dates, test-result changes, clinician instructions, and unresolved questions, reconcile them with the owner's own notes and appointment timing, and produce a source-linked preparation brief—without diagnosing or sending anything. The pendant can read only the top few questions while the full evidence remains on the Mac for review.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Background model for chronology, delta extraction, and question drafting; realtime only to clarify the owner's concern or read selected questions aloud.
- **latency:** 15–45 seconds for a portal plus local notes; return an immediate warning if a new result is present before completing the full brief.
- **cost:** ~$0.03–$0.15 per preparation brief; portal extraction and chronology normalization dominate.
- **security:** Health data must be treated as highly sensitive: no full page persistence, no broad spoken playback in public, no sharing with unrelated agents, and short-lived encrypted evidence only. Keep medical facts attributed to the portal and clearly label model-generated questions as non-clinical. Never message a clinician or alter an appointment without a separate explicit action.
- **missing:** A health-record extraction profile that recognizes results, reference ranges, dates, instructions, and clinician messages while redacting identifiers; A privacy-scoped join between browser findings and selected local notes/calendar items; A pendant delivery mode that requires a private listening context or lets the owner request only titles/counts aloud; A provenance-aware chronology and change detector that distinguishes a new result from a repeated portal notification


## What it asked for

### `t17-1ceo` (tool) — browser_read_focus_context
- why: The browser's unique value is authenticated context, but current command-level read_page cannot reliably target the owner's active selection/focused control. This is needed for the highest-value 'explain what I'm looking at' workflow and for safe form staging.

```json
{
  "operation": {
    "type": "string",
    "enum": [
      "browser_read_focus_context"
    ]
  },
  "deviceId": {
    "type": "string",
    "description": "Optional registered browser device; empty means live Safari."
  },
  "tabId": {
    "type": "string",
    "description": "Optional tab identifier; empty means active tab."
  },
  "includeScreenshotCrop": {
    "type": "boolean",
    "description": "If true, return only a tightly bounded crop around the focus/selection."
  }
}
```

## Its own summary

Produced three distinct browser-only/cross-surface proposals: (1) owner-triggered triage of currently open authenticated tabs into a concise, provenance-linked attention digest and pendant alert; (2) authenticated form preparation with field-by-field diff and a hard stop before submit; (3) pendant-triggered explanation of the browser's focused/selected element using DOM context and crop-only vision. Requested one narrow read-only tool, browser_read_focus_context, and asked mac-vision whether crop-only bounds are supported. I still need the extension to expose active-tab focus/selection metadata and a durable staged-form representation; the existing browser command wrappers are not enough.

**Biggest unknown:** Whether Safari's extension API can provide focused-element/selection/accessibility metadata and a bounded screenshot crop, rather than only whole-page reads; and whether mac-vision can consume that crop without full-screen capture.

