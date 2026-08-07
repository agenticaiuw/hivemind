# Harness derivation — browser-extension — round 29

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What am I looking at?” (or press the pendant button while a Safari page is open)"
- **useful because:** The browser is the only node that can see the owner's authenticated page, while the pendant is the only node immediately available for a spoken answer. This turns a private webpage into an on-demand, cited explanation without requiring the owner to copy text or switch apps.
- **path:** browser → mac-bridge → pendant → relay
- **model tier:** Use the cheaper background model for page extraction and initial summarization; use realtime only to acknowledge the button/voice request and speak the short answer. Escalate to the expensive tier only if the page is ambiguous or the owner asks a follow-up.
- **latency:** 3–6 seconds when Safari is online: extension capture 1–2s, extraction/summarization 1–3s, spoken response under 1s. If the page is unavailable, say so immediately rather than waiting through the queue timeout.
- **cost:** Roughly $0.01–$0.05 per invocation depending on page length; most cost is extracting and summarizing private page text, not the short realtime response.
- **security:** Private page text, URL, and optionally the current selection leave Safari for the relay/model. Default to the visible selection or bounded viewport text, include URL/title and source snippets in the answer, and avoid transmitting passwords or form values. No mutation occurs. A future setting should choose selection-only, viewport, or whole-page capture.
- **missing:** A browser extension command to return active-tab metadata, user selection, bounded visible text, and a screenshot/DOM excerpt in one typed result; A stable page-context token shared between browser, Mac planner, and pendant conversation so follow-up questions remain tied to the same tab without resending the entire page; A relay intent for the pendant button/utterance and a short-answer audio response path; Safari extension heartbeat recovery and pending-command expiry; current /browser/status reports Safari offline and two pending commands

### "“Reconcile this with my records.” (while viewing a logged-in order, invoice, appointment, or account page)"
- **useful because:** Today the browser can see a private portal and the Mac can see local files/calendar, but neither can reliably compare them as one evidence set. This would catch mismatched amounts, dates, names, cancellations, or missing confirmations before they become expensive mistakes, and would ask the owner only about genuine ambiguities.
- **path:** browser → mac-bridge → pendant → relay → dashboard-ux
- **model tier:** Use a cheaper background model for OCR/field extraction and deterministic comparison; use realtime only for the pendant’s brief clarification question and final spoken summary. Use the expensive tier only when records conflict semantically or the owner asks for interpretation.
- **latency:** 10–30 seconds for a single page against a bounded set of local records; up to two minutes for a multi-document reconciliation. The pendant should acknowledge immediately and report progress if browser extraction is slow.
- **cost:** Approximately $0.03–$0.20 per reconciliation, dominated by private-page/document extraction and conflict analysis; deterministic field comparisons should avoid repeated model calls.
- **security:** This joins browser-authenticated data with local files and calendar, creating a sensitive cross-source record. Process the smallest relevant fields, retain source URLs/filenames and hashes rather than raw copies by default, encrypt the reconciliation artifact, and expire it after the owner reviews it. Never alter either source. If a clarification is needed, speak only the conflicting fields—not the full account or document.
- **missing:** A user-invoked reconciliation job that accepts the active authenticated browser page plus an explicit local-record scope; Connectors that expose bounded calendar/files/notes fields with provenance and timestamps to the same job; A typed schema for normalized dates, currencies, parties, identifiers, and confidence-ranked conflicts; A pendant clarification interaction that can present two conflicting values and record the owner’s chosen interpretation; A review artifact showing side-by-side source evidence and an exportable correction checklist without performing the correction


## Changes it proposed to its own stack

### `browser-harness` — Add a privacy-bounded active-page context packet and lifecycle: the extension captures only the owner-selected text (falling back to a capped visible viewport), strips password/input values, assigns a pageContextId tied to tabId plus URL and DOM revision, and lets Mac/relay follow-ups reference that packet. Packets expire quickly, can be explicitly erased, and pending commands are cancelled when the device goes offline instead of accumulating.
- **owner gets:** The owner can ask a question about a private page naturally and then ask follow-ups without copying content or repeating the page. Offline Safari will produce a clear unavailable response rather than a mysterious delayed answer when it reconnects.
- effort: Medium: extension content-script capture and redaction, typed browser result schema, short-lived encrypted relay cache, and stale-command cancellation/reconnect tests.  ·  risk: Selection/viewport extraction could omit relevant content or redact too much; show the captured title/URL and a short source excerpt so the owner can detect that. If a device disconnects mid-request, mark it interrupted and allow one explicit retry; never replay a mutation.
- cost: Small storage and API overhead; approximately a few KB per active context packet and one summarization call per question. No hardware cost.  ·  latency: Adds under 500 ms for capture/redaction; avoids the current 45-second timeout when Safari is offline by failing fast on heartbeat state.
- security: Improves privacy by minimizing page transfer and removing form secrets, but page text still leaves the browser for model processing. Require explicit per-device encryption/authentication and short TTL; do not persist whole-page content by default.
- depends on: A working Safari heartbeat/status signal consumed by the queue; A typed cross-surface pageContextId contract; Relay intent routing for page questions


## What it asked for

_Nothing._
## Its own summary

Proposed a new cross-surface “What am I looking at?” workflow: a pendant request captures a privacy-bounded selection/viewport from the authenticated Safari tab, the Mac/background model summarizes it with citations, and relay speaks the answer plus supports page-tied follow-ups. Also proposed the needed short-lived pageContextId packet, secret redaction, fast offline failure, explicit erase, and stale-command cancellation. Live status currently shows Safari offline and two pending browser commands; mac-planner was notified.

**Biggest unknown:** The owner’s preferred capture scope (selection-only versus visible viewport versus whole page) and whether Safari will reconnect. I did not re-ask the previously denied/pending workflow-context request.

