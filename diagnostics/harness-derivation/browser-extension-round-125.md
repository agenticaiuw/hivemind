# Harness derivation — browser-extension — round 125

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-live-state** — Safari extension is online with 3 tabs, active tabId 901786, URL https://example.com, but it reports title 'Failed to open page'; no commands are pending. This is a changed state from prior tabCount=0.
  - evidence: GET /browser/status returned online=true, tabCount=3, tabId=901786, tabUrl=https://example.com, tabTitle='Failed to open page', pendingCommands=0 at 2026-08-07T17:47:44.698Z.

## Capabilities it proposed

### "When I say “what am I looking at?”, read the currently active Safari page, answer my question from that page aloud, and give me the exact section or link you used."
- **useful because:** This turns the pendant into an immediate voice interface for the authenticated page already in front of the owner—no copying URLs, screenshots, or tab hunting. It uniquely combines the worn microphone/speaker, Safari session access, and cited extraction.
- **path:** pendant → browser → relay-realtime → mac-planner
- **model tier:** Realtime for the short spoken question and answer; use a cheaper background extraction model for long pages, then return only the grounded result.
- **latency:** Answer in 3–6 seconds for a normal page; stream “reading the page” immediately and fall back to a compact cited result if extraction is slow.
- **cost:** Roughly $0.01–$0.05 per request depending on page length; browser extraction and input tokens dominate, not the short spoken response.
- **security:** Only the active tab’s visible/extracted content leaves Safari and is retained briefly. Never expose cookies or hidden form values. Show URL, section heading, and quoted evidence so the owner can catch a wrong-tab result.
- **missing:** A reliable active-tab browser_read_page/snapshot dispatch with tab affinity; A pendant utterance intent that includes the active Safari tab identity; Citation-bearing page extraction returned through the relay voice path

### "Before I submit anything in Safari, check the filled form for accidental secrets or private data going to the wrong recipient, explain each risk aloud, and show me a corrected draft without submitting it."
- **useful because:** A last-second privacy review catches pasted API keys, personal addresses, internal URLs, or an attachment sent to the wrong destination—especially when the owner is moving quickly. It uses browser access that no other node has and the pendant for an immediate warning.
- **path:** browser → mac-planner → pendant → relay-realtime → faculty-judgement
- **model tier:** Use a cheaper background model for field classification and destination comparison; reserve realtime for the concise spoken findings and owner dialogue.
- **latency:** Inspect a normal form in under 5 seconds and speak a risk summary within 2 seconds after extraction; never silently submit or alter the original.
- **cost:** About $0.01–$0.08 per inspection; DOM extraction plus classification of pasted text/attachments dominates.
- **security:** Sensitive values must be redacted before leaving the Mac where possible; send hashes/types and minimal surrounding labels, not full secrets. The owner policy allows maximum access, so this is advisory and non-blocking: preserve the original and present a corrected copy, requiring explicit spoken approval only to apply/send.
- **missing:** Form/recipient semantic extraction including attachments and contenteditable fields; Local secret/PII detector and destination trust comparison; A side-by-side draft artifact with field-level before/after provenance

### "Compare the private page I’m viewing with my saved rules and documents, tell me what violates or differs from them, and prepare a list of questions or edits—without sending anything."
- **useful because:** The owner can evaluate a lease, insurance quote, vendor agreement, benefits page, or school form against their own requirements while it is still behind a login. This is a genuinely cross-node task: Safari supplies private facts, Mac supplies local reference documents, and the pendant makes the result conversational.
- **path:** browser → mac-planner → mac-terminal → pendant → relay-realtime → faculty-perception → faculty-judgement
- **model tier:** Background model performs document/page alignment and clause comparison; realtime handles only the owner’s follow-up questions and a short prioritized briefing.
- **latency:** Initial comparison in 15–30 seconds, with progressive findings; follow-up answers under 4 seconds when the extracted evidence is cached.
- **cost:** Approximately $0.05–$0.30 per comparison; long private documents and page excerpts dominate token cost. Cache normalized excerpts and hashes to avoid resending unchanged text.
- **security:** Keep source documents on the Mac when possible and send only relevant excerpts, hashes, and citations to the model. Do not infer legal/financial certainty; label discrepancies and uncertainty. No edits or submissions occur without a separate owner command.
- **missing:** A permissioned local-document selector and redacted excerpt service; Cross-source provenance linking browser DOM regions to local document passages; A comparison schema for rules, exceptions, confidence, and unresolved questions

### "When a website asks me to accept cookies, consent to tracking, or agree to new terms, explain the practical consequences in plain language, identify what is optional, and prepare the least-invasive choice for me to review."
- **useful because:** Owners routinely face opaque consent screens while logged into private services. Today the system can read pages or click controls, but it cannot reason over the consent text, distinguish optional from required permissions, and present a clear privacy-preserving choice before anything is accepted.
- **path:** browser → pendant → relay-realtime → faculty-perception → faculty-judgement
- **model tier:** Use a background model to parse the full policy and compare vendor purposes; use realtime only for the short spoken explanation and follow-up questions.
- **latency:** Show the first plain-language summary within 5 seconds and a recommended choice within 15 seconds; never click acceptance automatically.
- **cost:** $0.03–$0.20 per consent screen, dominated by policy text extraction and comparison against the owner’s stated preferences.
- **security:** Policy text and the site identity leave the browser; do not expose unrelated page content or credentials. Recommendations must be advisory, with the exact toggles and consequences shown before any click.
- **missing:** A consent-banner and policy-section extractor that maps purposes to individual controls; Persistent owner privacy preferences with exceptions and expiry; A reversible preview of the exact browser clicks, without submitting them

### "Help me exercise my privacy rights on a logged-in site: find its export, correction, or deletion controls, explain what will happen and what I may lose, fill the request, and leave it ready for my approval without sending it."
- **useful because:** The owner cannot realistically locate and understand privacy controls across every service. This would turn browser access into a practical personal-data steward while preserving a hard stop before an irreversible deletion or legal request.
- **path:** browser → mac-planner → pendant → relay-realtime → faculty-judgement
- **model tier:** Background model researches the site’s control path and summarizes consequences; realtime handles the owner’s questions and approval preview.
- **latency:** Locate controls and prepare a request in 20–60 seconds; provide incremental progress so the owner knows it is working.
- **cost:** $0.05–$0.40 per service, depending on policy length and number of authenticated screens.
- **security:** Deletion/export requests can be irreversible and may affect shared accounts. Keep the original request and all populated fields visible, redact credentials, and require explicit owner approval immediately before submission.
- **missing:** A site-policy/control discovery workflow spanning authenticated pages; A structured privacy-request draft with consequences, retention caveats, and required identity fields; A durable but encrypted audit artifact showing exactly what would be sent

### "Turn any logged-in web app into a spoken, accessible walkthrough: tell me the page landmarks and available actions, let me say which action I mean, and read back the result without taking an irreversible action."
- **useful because:** Many private portals are difficult to use by voice or with visual attention divided. The pendant should let the owner operate unfamiliar authenticated sites through semantic landmarks rather than CSS selectors, while Safari supplies the session no other node can reach.
- **path:** pendant → browser → relay-realtime → mac-planner → faculty-perception → faculty-action
- **model tier:** Realtime for intent disambiguation and short confirmations; a cheaper model builds the page landmark/action map and caches it for the session.
- **latency:** Landmark map in under 8 seconds; each reversible action confirmation in under 3 seconds.
- **cost:** $0.02–$0.15 per page map, with caching reducing repeated extraction and model costs.
- **security:** The action map must clearly label navigation versus mutation. Preserve the owner’s maximum-access policy, but never infer an irreversible click from an ambiguous spoken phrase; read the target and resulting change first.
- **missing:** Semantic landmark/action extraction for arbitrary authenticated DOMs and canvas-heavy apps; Voice reference resolution such as “the second invoice” tied to stable element IDs; Post-action verification that reads the resulting page rather than assuming success


## Changes it proposed to its own stack

### `browser-harness` — Add an extension-side privacy firewall that classifies DOM nodes before any browser result is posted: redact passwords, auth tokens, payment numbers, hidden inputs, and unrelated off-screen regions; return typed placeholders plus locator hashes, while allowing the owner to explicitly request a narrowly scoped reveal for one field.
- **owner gets:** Private-page assistance becomes safe to use routinely: the system can summarize logged-in pages without accidentally exporting credentials or every hidden form value, while still being able to inspect exactly the field the owner asks about.
- effort: Medium: Safari content-script classification, result schema changes, test corpus for forms and rich web apps, and an explicit reveal command.  ·  risk: False positives could hide useful text; recover by returning a redacted result with a clear “field omitted” marker and allowing scoped reveal. False negatives remain possible, so never claim the browser is a security boundary.
- cost: Negligible API increase because redacted placeholders are shorter; modest extension CPU/memory during extraction.  ·  latency: Add roughly 50–200 ms for local classification per page extraction.
- security: Strongly reduces accidental secret exfiltration and limits page scope before relay/model exposure; explicit reveals become auditable events.
- depends on: Typed browser result schema with DOM locators and tab/session affinity; A way to request one-field scoped reveal from an active tab

### `interaction` — Create a cross-surface “private page packet”: every browser answer is emitted as a compact object containing tab identity, URL/title, quoted evidence spans, freshness, and safe-to-reuse normalized facts. The relay can speak it, Mac can save it, and later turns can refer to packet IDs instead of resending page text.
- **owner gets:** The owner can ask a follow-up like “compare that with the quote I saw yesterday” and get a grounded answer without repeating the whole page or losing which private tab the fact came from.
- effort: Medium-high: shared packet schema, short-lived encrypted storage, citation rendering, and packet-aware voice/context retrieval.  ·  risk: Stale or wrong-tab facts could mislead; show freshness and source on every spoken/visual answer, expire packets, and require re-read when a task is consequential.
- cost: Reduces repeated input-token cost substantially; small storage cost for encrypted excerpts and hashes.  ·  latency: First read unchanged; follow-ups become faster because only packet IDs and relevant spans are loaded.
- security: Private excerpts remain scoped, encrypted, and expiring; packet access must be tied to the owner session and tab identity.
- depends on: Browser extraction with citations; Compact task-relevant context projection; Authenticated short-lived packet store


## What it asked for

_Nothing._
