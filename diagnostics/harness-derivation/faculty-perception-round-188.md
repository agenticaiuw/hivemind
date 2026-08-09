# Harness derivation — faculty-perception — round 188

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac and browser reachability** — At 2026-08-08T22:25Z the Mac agent reports Accessibility and Screen Recording trusted, inputReachability verified, browser extension online with zero pending commands, and Safari's live tab is a DoorDash order page (tab 3032326). Relay is reachable with D1 and Mac bridge online; no pendant appears in the device inventory.
  - evidence: GET /ops/status, GET /observe, GET /browser/status, and discover:devices live responses.

## Capabilities it proposed

### "Before you do anything consequential, tell me whether the evidence is trustworthy: is this the current authenticated page, is the Mac actually able to act, is the relay current, and did I really hear the last instruction?"
- **useful because:** This would be the system's most valuable perception capability: it prevents confident action on stale browser text, a disconnected bridge, an expired session, or an answer that was merely queued. It gives the owner one plain-language trust verdict with the exact weak link instead of making them inspect four surfaces.
- **path:** browser-extension → mac-planner → relay-realtime → faculty-perception → pendant
- **model tier:** Use a cheap background verifier for hashes, timestamps, and liveness; reserve realtime only to turn the resulting evidence into a short spoken answer.
- **latency:** Under 2 seconds when asked; browser snapshot and relay liveness dominate, with no vision model unless the page is ambiguous.
- **cost:** Usually <$0.01 in API/model cost; most cost is one browser read and small structured checks, not generation.
- **security:** Never expose page contents beyond the requested claim. Require a fresh authenticated browser result, explicit session/tab identity, Mac permission state, relay freshness, and eventually a device-originated playback event; if any is absent say unknown, never green. Consequential actions still require the existing confirmation policy.
- **missing:** A cross-surface evidence-quorum route that returns freshness, source identity, hashes, and an overall unknown/verified verdict; Relay-to-Mac browser provenance transport for cloud reads; A real pendant playback event (the accepted audio_delivery_ack_queue)

### "Watch the thing I am looking at and tell me only when it materially changes — for example when this order page changes from placed to delivered — with the old and new evidence attached."
- **useful because:** The owner currently has an authenticated DoorDash order tab but no dependable way to learn that its state changed while attention is elsewhere. This turns the browser's session into a quiet, provenance-bearing change detector rather than a chat-only lookup, and can speak once without repeatedly nagging.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → faculty-perception
- **model tier:** Use a background scheduler and content hashes/diff classification; use a small model only to label the semantic change. Realtime is used only for the final brief announcement.
- **latency:** Polling every 2–5 minutes is adequate for order/status pages; notification delivery should begin within 10 seconds of a detected change.
- **cost:** Low: browser reads and hashing dominate; <$0.02 per monitored page-hour with adaptive polling, and near-zero model cost for unchanged hashes.
- **security:** Store redacted snippets and hashes, not full account pages or payment data. Bind each watch to a tab/session and expire it; pause when the browser reports a login wall or tab identity changes. Never infer a delivery event from a stale screenshot.
- **missing:** A durable watch registry with tab/session binding and semantic field selectors; A browser-side change receipt containing URL, tab id, capturedAt, content hash, and redacted before/after regions; A relay push path that can require device playback acknowledgement before marking the owner notified

### "When I come back, give me a short 'what became unsafe or impossible' report: permissions lost, browser session expired, Mac went offline, relay stopped hearing, or anything I asked for that was never actually delivered."
- **useful because:** A normal success digest reports completed work, but completion is not reality. This report is specifically about negative evidence and capability loss, so the owner learns about a failed browser session or stale bridge before trusting the next action. It is useful even with no pendant because the Mac and relay are live today.
- **path:** faculty-perception → mac-planner → browser-extension → relay-realtime → pendant
- **model tier:** Run as a cheap scheduled/background comparison against signed snapshots; use realtime only when the owner asks aloud. No model call for unchanged state.
- **latency:** Capture snapshots opportunistically; answer in under 1 second from the stored diff, with a fresh liveness check only if the owner asks for 'now'.
- **cost:** Negligible model cost; bounded JSON snapshots and one small diff per wake cycle.
- **security:** Report only transitions with timestamps and source evidence. Treat absence as unknown when a source was not sampled; never claim an owner heard an announcement merely because relay sent socket bytes. Redact URLs, order details, and credentials from durable diffs.
- **missing:** A monotonic cross-surface health journal with explicit unknown/not-sampled states; A scheduler trigger on Mac wake, browser session change, and relay heartbeat loss; A pendant delivery/ack event to distinguish 'not delivered' from 'delivered but unheard'

### "Show me exactly why you believed something and acted on it: reconstruct the evidence, page state, permissions, model decision, and action result as they existed at that moment—not today's explanation."
- **useful because:** Today the system can retain fragments of jobs, browser activity, and pipeline traces, but cannot causally replay one decision across the relay, Mac, and browser. A time-anchored replay would let the owner detect stale evidence, mistaken interpretation, or an action that diverged from the plan, instead of trusting a post-hoc story.
- **path:** faculty-perception → relay-realtime → mac-planner → browser-extension → faculty-judgement → faculty-action
- **model tier:** Use deterministic event correlation and hashes first; invoke a cheaper text model only to summarize the reconstructed chain. Realtime is unnecessary unless the owner asks by voice.
- **latency:** Capture correlation continuously with sub-100 ms overhead; answer a replay query in under 3 seconds from local records.
- **cost:** Low ongoing storage and hashing cost; roughly <$0.01 per replay summary, dominated by optional summarization.
- **security:** The replay is more sensitive than ordinary logs because it can include page claims and intended actions. Encrypt locally, redact secrets before persistence, require explicit owner request, and clearly separate observed evidence from model inference. Never fabricate missing links.
- **missing:** A single immutable decision trace ID propagated from voice turn through browser reads, judgement, Mac execution, relay job, and device delivery; Content-hash snapshots of the exact browser/Mac state used for each decision, with retention and redaction policy; A reader that marks every missing or contradictory causal edge instead of silently stitching records

### "When an action could spend money, publish, delete, or send a message, prepare it everywhere but do not commit until I give a deliberate physical confirmation on the pendant while the exact browser preview is still fresh."
- **useful because:** A spoken yes can be accidental, overheard, or based on a stale page. This would create a real presence-bound commit gate: the browser preview, Mac plan, and pendant gesture must refer to the same one-time transaction, so preparation remains reversible and commitment is unambiguous.
- **path:** browser-extension → mac-planner → faculty-judgement → faculty-action → relay-realtime → pendant
- **model tier:** Use deterministic transaction tokens and policy checks; use a small model only to turn the prepared diff into a concise spoken preview. No realtime model is needed for token validation.
- **latency:** Preparation under 3 seconds; commit within 1 second after the pendant gesture, otherwise expire the token.
- **cost:** Negligible model cost; browser preview and transaction storage dominate, with one short spoken confirmation.
- **security:** Bind the token to user, tab/session, target, exact redacted before/after diff, expiry, and nonce. Reject if the page changes, session logs out, Mac permissions change, or relay/pendant freshness is unknown. Never treat a relay socket write as physical confirmation.
- **missing:** A cross-surface one-time transaction token understood by browser, Mac, relay, and pendant firmware; A pendant-local deliberate gesture/sequence that survives link latency and cannot be confused with push-to-talk; Action adapters that expose a canonical reversible preview and refuse execution without the matching token

### "Before any page, message, or document leaves my Mac, show me the exact redacted excerpt and tell me what the cloud model will receive; let me approve just this one use without exposing the rest of the page."
- **useful because:** The current browser and relay paths can read authenticated pages, while provenance and redaction are incomplete or local-only. The owner cannot inspect the actual boundary at the moment of use. A per-request privacy manifest makes cloud assistance useful without requiring blanket trust in the browser session or relay.
- **path:** browser-extension → mac-planner → relay-realtime → faculty-perception → pendant
- **model tier:** Deterministic local classifier/redactor first; a small local model may classify ambiguous fields. Realtime only speaks the short manifest and asks for approval.
- **latency:** Under 1 second for known patterns; up to 3 seconds for ambiguous classification, with cloud transmission blocked until approval.
- **cost:** Near-zero API cost for local redaction; a small model call only for novel ambiguous content.
- **security:** Default deny on secrets, payment data, health data, private messages, and login walls. The preview itself must not be sent to the relay before approval; record only a local hash and decision. Approval must bind to exact content hash, destination, purpose, and expiry.
- **missing:** A local preflight interception point covering browser reads, Mac actions, and relay voice/tool calls; A user-visible exact excerpt plus field-level redaction and destination manifest; A one-shot approval token enforced by every outbound path, not merely a prompt instruction


## What it asked for

_Nothing._
## Its own summary

Fresh reality: the exact AI Pendant Agent now has Accessibility and Screen Recording, input injection is verified, Safari's browser bridge is online with zero pending commands, and the live authenticated tab is a DoorDash order page. Relay is reachable on D1 and the Mac bridge is online; no pendant is registered. I added three owner-facing proposals: a cross-surface evidence-trust preflight, a provenance-bearing browser material-change watch, and a negative-evidence report for things that became stale/blocked/undelivered. What I still need is not another diagnostic endpoint: I need a shared evidence contract joining browser capture, Mac/relay freshness, and eventual pendant playback truth, plus durable watch receipts and a scheduler trigger.

**Biggest unknown:** Whether the owner has a real pendant available to pair; until one registers, all claims about physical receipt, playback, or worn-device liveness remain unknown.

