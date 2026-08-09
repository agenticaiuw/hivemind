# Harness derivation — browser-extension — round 223

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Stage this logged-in web action, show me exactly what will be sent, and after I approve on the pendant, submit it.”"
- **useful because:** This is the safest way to make the browser materially useful for high-value forms, messages, and purchases without forcing the owner to copy text between voice, Safari, and the pendant. Safari owns the session; the relay can explain the payload; the pendant provides a physical approval and the browser performs the final submit.
- **path:** browser-extension → relay-realtime → pendant → mac-planner
- **model tier:** Use the realtime tier only to interpret the spoken goal and summarize the staged diff; use the local/browser action machinery for deterministic field filling and submission.
- **latency:** Stage in 5–15 seconds; approval result and final submit in under 5 seconds.
- **cost:** Usually one realtime turn plus browser actions, roughly $0.01–$0.05 depending on page complexity; browser extraction and deterministic actions dominate latency, not tokens.
- **security:** The browser must retain the authenticated session but never send passwords or full page text to the model. Show a field-level diff, destination origin, and payload hash. A pendant approval is required only for the final irreversible submit, and the staged draft expires after a short TTL. If the page changes, invalidate the approval and restage.
- **missing:** A durable staged-transaction record binding origin, tab, field diff, payload hash, and expiry; A pendant approval event carrying that transaction ID; A browser action that verifies the hash immediately before submit

### "“Watch the authenticated page I’m looking at for the one change that matters, and put a short alert on my pendant; don’t save the page.”"
- **useful because:** The owner can turn any currently authenticated Safari page into a one-shot personal monitor without naming a site in advance. The browser reads only the requested claim, compares it against a baseline, and the relay delivers a concise alert even if the Mac link later drops. This is uniquely useful because only Safari has the owner’s login and only the pendant can interrupt him away from the screen.
- **path:** browser-extension → relay-realtime → pendant → mac-planner
- **model tier:** Use a cheaper background model for scheduled polling and semantic comparison; use realtime only when the owner asks a follow-up about the alert.
- **latency:** Initial baseline under 10 seconds; scheduled checks can be minutes apart; alert delivery within one poll interval.
- **cost:** Low: one small extraction/comparison per check, roughly fractions of a cent to a few cents daily; browser polling and authenticated session availability dominate.
- **security:** Default to an empty owner-supplied per-origin rule. Persist only the short claim, host, URL, evidence capsule, and 24-hour TTL; never page HTML, screenshots, or credentials. Alert text must pass the existing category speaking policy. Stop watching when the tab/origin changes or the session expires.
- **missing:** A user-visible one-shot watch record tied to tab/origin and a semantic selector; A scheduler that invokes browser extraction while Safari is online; A change-to-offline_alert_inbox delivery adapter

### "“Read the private dashboard I’m on, answer my question with the exact supporting figures, and leave a short cited note on my Mac.”"
- **useful because:** It turns an authenticated page into a durable, auditable answer rather than an ephemeral spoken summary: Safari supplies access, the model extracts only evidence relevant to the question, the Mac writes a note, and the pendant can read the result later. This is valuable for private work dashboards and account portals that public search cannot reach.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a background/standard model for extraction and citation assembly; reserve realtime for the owner’s follow-up question or spoken compression.
- **latency:** Answer in 10–20 seconds and create the note in the same job; follow-up playback should begin within 3 seconds.
- **cost:** Approximately $0.01–$0.08 per request, dominated by model context for extracted evidence; cap evidence to relevant snippets rather than forwarding the page.
- **security:** Only claims relevant to the explicit question leave the browser. Store provenance and short-lived findings, not page text. Notes should include source URL, retrieval time, and claim confidence, but redact configured categories. Never silently broaden extraction to neighboring tabs.
- **missing:** A browser evidence extractor that returns bounded snippets with DOM locators; A citation-aware note writer that can attach browser provenance; A cross-surface job receipt linking spoken answer, note, and source claims

### "“I’m leaving my desk—secure my browser sessions now, and tell me if anything could not be closed.”"
- **useful because:** A physical pendant command would let the owner rapidly close or lock authenticated Safari sessions when walking away, without returning to the Mac. The browser is the only node holding those sessions; the pendant is the only node reliably with the owner. This provides a concrete security action that voice-only control cannot safely guarantee.
- **path:** pendant → browser-extension → relay-realtime → mac-planner
- **model tier:** No expensive model is needed for execution. Realtime may interpret the spoken request, while the browser extension performs a deterministic session-lock/close operation and reports exact results.
- **latency:** Begin within 2 seconds and report each tab’s result within 10 seconds.
- **cost:** Near-zero model cost; the dominant cost is extension and Safari API engineering.
- **security:** Require a local physical button gesture or explicit spoken phrase plus pendant proximity; never claim success without per-tab receipts. Default action should close tabs or invoke site logout where supported, not erase history or cookies. The owner must be able to configure exceptions such as a music tab.
- **missing:** A browser command for lock/close/logout with per-tab results; A pendant-originated emergency action event; A Safari extension handler that can identify authenticated tabs without transmitting page contents; A persistent exception policy for tabs the owner chooses to keep open

### "“Compare the two private offers open in Safari, explain the tradeoffs from their actual terms, and leave me one recommendation with the quoted evidence.”"
- **useful because:** The owner can make a consequential decision using private pages that public search cannot access. Safari reads both authenticated offers, the model aligns equivalent terms rather than merely summarizing each page, and the Mac leaves an auditable recommendation. This is materially different from asking about one dashboard: it requires cross-tab entity and clause alignment.
- **path:** browser-extension → relay-realtime → mac-planner → pendant
- **model tier:** Use a background model for extraction, normalization, and comparison; use realtime only to answer follow-up questions or read the recommendation aloud.
- **latency:** Produce a comparison in 20–40 seconds, with progress feedback if either page is slow.
- **cost:** Approximately $0.03–$0.15 per comparison, dominated by two-page clause extraction and alignment; evidence should be bounded before model submission.
- **security:** Only the explicitly selected tabs participate. Keep quotations short, redact configured categories, and store claims plus provenance rather than page bodies. Recommendations must distinguish quoted facts from model judgment and identify stale or conflicting terms.
- **missing:** A multi-tab browser extraction operation with stable tab identity; A clause/term normalization and alignment pipeline; A recommendation artifact containing evidence spans, uncertainty, and provenance; A Mac note action that preserves the artifact structure

### "“When I’m on a private site, let me point to one field or paragraph and ask the pendant about exactly that—without sending the rest of the page anywhere.”"
- **useful because:** This would make authenticated browsing genuinely hands-free while sharply reducing data exposure. The extension would capture only the focused DOM region and its label, the relay would answer in one short sentence, and the pendant would speak it back. No other node can combine the owner’s private browser focus with an always-available spoken interface.
- **path:** browser-extension → relay-realtime → pendant
- **model tier:** Realtime is appropriate because this is an interactive, low-latency question about the owner’s current focus. Send a small bounded context window, not the page.
- **latency:** Answer within 3–6 seconds after the focus/query event.
- **cost:** About $0.005–$0.03 per query; the dominant constraint is low-latency context transfer, not extraction.
- **security:** The extension must send only the focused element, nearby labels, origin, and an explicit user question. Password, payment, hidden, and configured-sensitive fields must be excluded locally. Do not persist the context or answer unless the owner explicitly asks to save it.
- **missing:** A focus-context browser event that captures bounded visible DOM text and semantic labels; A pendant/browser correlation ID for the owner’s question; Local redaction of password, payment, and configured-sensitive field types before relay submission; A low-latency browser-to-relay event path


## What it asked for

_Nothing._
