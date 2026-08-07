# Harness derivation — browser-extension — round 138

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Compare the same appointment, order, balance, or deadline across the logged-in Safari tabs I have open, show me the exact sources, and tell me if anything conflicts.”"
- **useful because:** Private sites often disagree or show stale states in different tabs. The browser is the only node with those sessions; a cited cross-tab comparison prevents acting on the wrong date or amount without changing anything.
- **path:** browser-extension → mac-planner → faculty-perception → faculty-judgement → relay-realtime → pendant
- **model tier:** background for extraction and normalization; realtime only to answer the spoken follow-up
- **latency:** 5–15 seconds for up to six already-open tabs; immediate spoken result once comparisons finish
- **cost:** About $0.01–$0.05 per comparison; browser extraction and model reconciliation dominate, not page loading
- **security:** Private page text stays on the Mac/relay path and must be minimized to the requested fields; cite URL/tab/time, redact unrelated content, and require confirmation for any proposed mutation (none in this read-only ask).
- **missing:** A multi-tab browser extraction action that returns stable tab IDs and field-level citations; A normalization/reconciliation routine for dates, currencies, statuses, and time zones; A spoken result route that can reference browser evidence

### "“Save the important facts from this logged-in page for me to use later, with the source and an expiry, so you can still answer when Safari is closed—never save the whole page.”"
- **useful because:** The owner can turn a fleeting authenticated page into a small, sourced handoff usable from the pendant away from the Mac, without making browser credentials or an entire private page part of long-term memory.
- **path:** browser-extension → mac-planner → faculty-perception → relay-realtime → pendant
- **model tier:** background extraction/classification; cheap relay retrieval for later questions
- **latency:** 3–8 seconds to extract and confirm the selected facts; sub-second retrieval from the pendant conversation
- **cost:** Roughly $0.005–$0.03 per capture; token cost is bounded by selected fields, with storage negligible
- **security:** Store only explicitly selected facts, source URL, timestamp, sensitivity label, and TTL in encrypted local capture; never persist cookies, page dumps, passwords, or hidden fields. Tell the owner exactly what was retained and delete on request.
- **missing:** A browser command for semantic field selection rather than whole-page capture; A TTL/sensitivity-aware private fact store shared by relay and Mac; Pendant utterances for listing, expiring, and deleting browser-derived facts

### "“Read what is currently visible in my Safari tab while I work, keep a short spoken companion of the page’s headings, warnings, and selected changes, and let me ask about it hands-free.”"
- **useful because:** This makes the browser’s private visual context available while the owner’s hands and eyes are busy: the extension reads only the active tab, the Mac summarizes it, and the pendant answers without exposing the screen to a public web tool.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** small/background model for DOM-to-outline and change filtering; realtime model only for conversational questions
- **latency:** Initial outline under 4 seconds; updates within 2 seconds after navigation or an owner-requested refresh
- **cost:** $0.005–$0.03 per outline/update, mostly proportional to changed DOM text; realtime follow-ups are normal voice cost
- **security:** Transmit extracted text, not screenshots, by default; restrict to the active tab and owner-invoked duration, show URL/title and a stop command, redact password/payment fields, and never click or submit from this mode.
- **missing:** Extension push events for active-tab navigation/DOM changes (current bridge is poll/command oriented); A bounded DOM diff and sensitive-field redactor; A low-latency browser-context channel into the pendant conversation

### "“If a logged-in site asks for a security check, tell me which site and what it is asking for through the pendant, let me complete the challenge in Safari, and then resume the task without ever reading or storing the code.”"
- **useful because:** Authenticated browser work currently breaks at MFA, passkeys, and consent interstitials. The browser can see the challenge while the pendant can alert an owner who is away from the screen; resuming preserves the task instead of abandoning it or mishandling secrets.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → faculty-action
- **model tier:** Realtime for the short challenge explanation and owner dialogue; background model for task resumption and page-state verification
- **latency:** Alert within 2 seconds of challenge detection; resume within 10 seconds after the owner completes it
- **cost:** Approximately $0.01–$0.05 per interruption, dominated by the resumption check and voice turn
- **security:** Never extract OTPs, passkeys, recovery codes, or challenge answers. Send only origin, challenge type, visible instruction, and completion state. Require explicit owner initiation of the challenge and abort on origin change.
- **missing:** Challenge/interstitial detector in the Safari extension; A paused browser-task state with resumable checkpoints; Origin-bound completion signal that contains no secret

### "“Turn the text I select in my private Safari page into a short, sourced explanation or translation in my ear, without sending the rest of the page.”"
- **useful because:** A user can isolate exactly one confusing clause, medical instruction, contract term, or foreign-language passage instead of exposing an entire authenticated page. The pendant makes this useful while reading hands-free.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Realtime for a short selected passage; background model for longer explanation or translation
- **latency:** Under 3 seconds for a passage under 500 words
- **cost:** About $0.003–$0.02 per request, proportional to selected text
- **security:** Only the explicit selection and page origin leave Safari; redact nearby form fields, do not retain by default, and speak a warning if the selection appears to contain a secret.
- **missing:** Extension API for owner selection capture with origin and DOM location; A command/result type carrying selection-only text; A redaction classifier for secrets in selected text

### "“Make a private webpage easier to read for this session—remove clutter, enlarge the relevant section, and read it aloud—then restore the page exactly when I’m done.”"
- **useful because:** The owner should be able to use authenticated sites despite dense layouts, distracting banners, or poor accessibility without permanently changing settings or handing credentials to another service. Safari can modify the live page; the pendant supplies control and narration.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** Small background model to identify clutter and target content; realtime only for spoken controls
- **latency:** Apply a temporary view within 2 seconds; restore in under 1 second
- **cost:** Approximately $0.005–$0.03 per transformation; mostly one classification call per page
- **security:** Use an isolated reversible stylesheet/DOM overlay, never delete or submit content, preserve a before-state checksum, and auto-restore on lease expiry or tab navigation. Do not transmit page text unless narration is requested.
- **missing:** Extension content-script capability for reversible CSS/DOM overlays; Before/after page-state tracking and automatic restoration; A bounded reader-mode/narration extractor


## Changes it proposed to its own stack

### `browser-harness` — Add a read-only /browser/compare operation that accepts up to six existing session/tab IDs plus typed field intents (date, amount, status, identifier), runs extraction in parallel, normalizes locale/time zone/currency, and returns per-field values with URL, tabId, title, timestamp, and source excerpt. It must report disagreement rather than pick a winner.
- **owner gets:** They can ask one spoken question and know whether their open private tabs agree before relying on an appointment, order, or balance.
- effort: Medium: extension result schema, parallel dispatcher, normalization library, and cited spoken rendering.  ·  risk: A stale tab or dynamic page can look authoritative; surface freshness and disagreement prominently, never mutate pages. Recover by rerunning a selected tab.
- cost: Small background-model cost per comparison, bounded by six short extracts; no new storage required.  ·  latency: Parallel extraction should keep typical response under 10 seconds.
- security: Only requested fields leave the browser; redact unrelated DOM and password/payment inputs.
- depends on: Stable tab/session affinity in browserBridge; Field-level citation result type; A reconciliation prompt or deterministic normalizer

### `browser-harness` — Add an owner-invoked active-tab change stream: Safari emits navigation plus debounced accessibility/DOM-region diffs for the current tab for a lease of at most 15 minutes; server redacts inputs and forwards only changed headings, alerts, and selected regions to the voice pipeline. Include explicit start/stop events and a byte/token budget.
- **owner gets:** While hands or eyes are occupied, the pendant can announce a newly visible warning or answer a question about the private page currently in front of them, without screen takeover.
- effort: High: extension event hooks, redaction/diffing, backpressure, lease expiry, and pipeline integration.  ·  risk: Pages may contain secrets in text or accessibility labels; default to no stream, stop on tab switch or lease expiry, and show active status. Recover by requesting a fresh snapshot.
- cost: Low-to-moderate per-minute model cost only when enabled; bandwidth is limited to diffs.  ·  latency: Updates target 1–2 seconds after a meaningful DOM change.
- security: Sensitive-field redaction and active-tab scoping are mandatory; no screenshots or form values by default.
- depends on: Extension push/event protocol (current bridge is polling); DOM diff and sensitive text classifier; Voice pipeline event subscription


## What it asked for

_Nothing._
