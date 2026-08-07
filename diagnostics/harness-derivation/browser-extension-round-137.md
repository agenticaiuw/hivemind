# Harness derivation — browser-extension — round 137

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I’m on a private webpage, let me press the pendant and ask “what matters here?”—use the active Safari tab, extract the key facts, deadlines, and available next steps, and speak back a concise answer with links to the exact page sections."
- **useful because:** This turns the browser’s unique authenticated reach into an immediate hands-free assistant: no copying URLs or exposing private pages to public search, and the answer is grounded in what the owner is actually viewing.
- **path:** pendant → browser → relay-realtime → mac-planner
- **model tier:** Realtime for the short spoken answer; a cheaper background extraction model for page parsing and section ranking.
- **latency:** 5–8 seconds from button press to first spoken sentence; extraction can continue for up to 20 seconds if the page is large.
- **cost:** Roughly $0.01–$0.05 per invocation, dominated by private-page extraction and the realtime spoken response; no cost for idle browsing.
- **security:** Only the active tab’s extracted content leaves Safari, and it may contain sensitive account data. Never include hidden form values or cookies; show the source URL and section anchors, and require an explicit follow-up before any mutation.
- **missing:** A live browser command enqueue implementation (the currently granted wrappers are still stubs); Pendant button/event forwarding while USB-attached or LTE-registered; A page extractor that returns stable section anchors and bounded text

### "Compare the private pages I have open—such as two travel, insurance, shopping, or service offers—and tell me which option is actually best after fees, restrictions, dates, and cancellation terms, with a compact evidence table and the assumptions you used."
- **useful because:** Public search cannot see the owner’s personalized prices, account-specific terms, or already-open checkout pages. A multi-tab comparison can prevent expensive choices while preserving the owner’s existing logged-in context.
- **path:** browser → mac-planner → relay-realtime → pendant
- **model tier:** Cheaper background model for parallel extraction and arithmetic; realtime only to deliver the final spoken recommendation and answer follow-up questions.
- **latency:** 10–20 seconds for up to six tabs; speak an interim “I’m comparing the open pages” acknowledgement within 2 seconds.
- **cost:** About $0.03–$0.12 per comparison, dominated by extracting several private pages; arithmetic and table assembly are negligible.
- **security:** Data from separate authenticated sites must be kept within one task scope and not persisted by default. Do not infer or expose payment credentials; display source URLs, quote timestamps, and missing fields. No purchase or checkout submission without a separate explicit request.
- **missing:** Reliable live enqueue and tab enumeration for Safari; A structured extractor for prices, dates, exclusions, and cancellation clauses; A comparison result schema that preserves per-cell citations and uncertainty

### "If I see a suspicious-login, payment, or account-security notice in Safari, investigate it across the relevant logged-in pages, explain whether it matches my known devices and activity, and give me a prioritized containment checklist—without changing security settings or contacting anyone."
- **useful because:** Security notices are time-sensitive and hard to interpret across several account pages. The browser can reach the private alert and session/device history while the Mac can provide local time and device context; the pendant makes triage possible before the owner sits down.
- **path:** browser → mac-planner → relay-realtime → pendant
- **model tier:** Background model for evidence collection and correlation; realtime only for the concise spoken risk assessment and immediate follow-up dialogue.
- **latency:** Acknowledge in under 2 seconds and provide an initial assessment in 8–15 seconds; deeper account-by-account evidence can arrive within 45 seconds.
- **cost:** About $0.03–$0.15 per incident, depending on the number of private pages inspected; most cost is page extraction, not reasoning.
- **security:** This handles extremely sensitive security and financial data. Keep extraction ephemeral, redact tokens, passwords, full payment numbers, and recovery codes, and cite exact alert/session evidence. Never click revoke, reset, report, or contact-support controls; show those as proposed next steps only.
- **missing:** A live browser command enqueue implementation and robust active-tab/tab-list support; A device-identity binding between Safari account sessions and the owner’s Mac/pendant; A redaction-aware evidence store with automatic expiry; Account-specific security-page extraction recipes

### "Before I accept a new privacy policy, subscription, waiver, or checkout agreement in Safari, have the system read the actual agreement and the surrounding page, identify the obligations, renewals, data sharing, cancellation traps, and unusual clauses, and tell me exactly what accepting would commit me to—without clicking Accept."
- **useful because:** The owner can currently ask for a summary, but cannot reliably have the logged-in browser inspect the agreement behind the visible checkbox, distinguish the operative terms from marketing copy, and surface concrete future costs or rights surrendered. This would prevent costly consent made under time pressure.
- **path:** browser → mac-planner → relay-realtime → pendant
- **model tier:** Background model for clause extraction and structured risk comparison; realtime only for the short spoken explanation and the owner’s follow-up questions.
- **latency:** First plain-language warning in 5 seconds; full cited clause map in 20–60 seconds for an agreement up to 50 pages.
- **cost:** Approximately $0.05–$0.30 per agreement, dominated by extracting and processing the private terms; repeated unchanged clauses should be cached by content hash.
- **security:** Agreements may include account identifiers and financial details. Transmit only the rendered terms and nearby controls, redact credentials and payment data, retain the clause map briefly, and cite URL, section heading, and text excerpts. Never accept, subscribe, check consent boxes, or submit.
- **missing:** A browser extraction mode that captures the operative agreement plus the exact consent controls and linked amendments, not merely visible page text; A clause schema for money, renewal, cancellation, arbitration, data use, and permission grants with uncertainty and citations; A content-hash cache and version detector so the owner can tell whether the agreement changed since last review; A live browser command enqueue implementation and dependable Safari tab results

### "While I am in a web meeting, monitor the authenticated meeting page for my name, direct questions, decisions, and action assignments, then discreetly buzz or speak only when I need to respond; afterward give me a cited list of commitments and draft follow-ups without sending them."
- **useful because:** The owner cannot currently have the browser and pendant act as a quiet second pair of ears. This would catch an assignment buried in chat or a transcript without recording every meeting into the daily briefing, and would work inside meetings that public search and ordinary calendar access cannot see.
- **path:** browser → pendant → relay-realtime → mac-planner
- **model tier:** A low-cost streaming extraction model watches bounded transcript/chat deltas; realtime is reserved for urgent, low-latency owner alerts; a background model builds the post-meeting commitment list.
- **latency:** Detect and deliver a direct-question alert within 2–4 seconds; post-meeting summary within 2 minutes of the meeting ending.
- **cost:** Roughly $0.02–$0.10 per meeting hour depending on transcript cadence and audio availability; most cost is streaming transcript classification.
- **security:** Meeting content is highly confidential. Process only the meeting’s transcript/chat region, encrypt transient buffers, expire them promptly, show the source timestamp for each alert, and provide a hard pause. Never send chat or follow-up messages automatically.
- **missing:** A meeting-specific browser extractor for live transcript, chat, speaker, and meeting-state deltas; A low-latency browser result stream rather than one-shot page extraction; Pendant haptic alert and quiet-hours policy over USB/LTE; A post-meeting commitment object with speaker, timestamp, evidence, and draft-only follow-up state

### "When a site forces a cookie or privacy-consent choice, apply my standing privacy rules to the actual options, reject unnecessary tracking, keep essential functionality working, and show me a record of what was allowed and why—without silently accepting new marketing or data-sharing terms."
- **useful because:** Consent dialogs are designed for interruption and often hide the meaningful choices behind several screens. The owner cannot today delegate a consistent, explainable privacy preference across authenticated Safari sites while retaining a per-site audit trail.
- **path:** browser → mac-planner → relay-realtime → pendant
- **model tier:** A small background policy model classifies consent purposes and maps them to the owner’s standing rules; realtime is used only when choices conflict or a site’s operation would be affected.
- **latency:** Resolve ordinary banners in 3–8 seconds; pause and ask a concise question within 5 seconds when the policy is ambiguous.
- **cost:** About $0.005–$0.03 per consent flow, mostly page extraction; policy evaluation is cheap and can be local.
- **security:** Consent choices affect tracking and legal privacy rights. Store only site, purposes, choice, timestamp, and policy version—not identifiers or browsing history. Never accept terms of service, paid subscriptions, or data transfers under this capability; surface those separately for review.
- **missing:** A consent-dialog detector that follows nested preference centers and records each control’s semantic purpose; An owner-editable privacy policy with per-purpose defaults and site exceptions; A browser action receipt that records before/after consent state and supports immediate reversal where the site allows it; A live browser enqueue path and reliable result delivery


## Changes it proposed to its own stack

### `interaction` — Add a pendant long-press “browser context” gesture: the pendant emits a signed context-request event with a short request ID; the Mac binds it to the current Safari tab, extracts only the bounded visible/semantic page region, and routes the result to the relay for a spoken response. If the Mac or relay is briefly unavailable, the pendant stores the request ID and retries, never storing page contents.
- **owner gets:** The owner can invoke help from whatever private page is already in front of them without saying the site name, copying text, or reaching for the keyboard. It makes the browser’s authenticated reach feel like part of the wearable rather than a separate app.
- effort: Medium: firmware button gesture and retry event, Mac active-tab binding, browser extraction metadata, and relay correlation; test USB-first today, then LTE.  ·  risk: A stale tab could be used if focus changes between gesture and extraction; include tab URL/title and timestamp in the spoken answer and discard requests older than 10 seconds. Recovery is simply retrying the gesture. Avoid retaining page text on the pendant.
- cost: No per-event API cost beyond the eventual model call; roughly 2–6 kB firmware and under 2 kB RAM for the event/retry ring. No hardware cost on the current single-button nRF9160 prototype.  ·  latency: Button acknowledgement locally under 100 ms; browser extraction plus response target 5–10 seconds.
- security: The event should contain no page content or credentials. Use a per-device nonce and expiry, redact URL query strings, and transmit only to the authenticated Mac/relay channel.
- depends on: A functioning browser command enqueue path (currently requested wrappers are stubs); A Mac bridge API that reports the active Safari tab with timestamp; Pendant event forwarding over the current USB serial path and later LTE registration


## What it asked for

_Nothing._
## Its own summary

This round produced three distinct owner-facing additions: (1) spoken “what matters here?” from the active authenticated Safari page, (2) evidence-backed comparison of multiple private offers/pages including fees and restrictions, and (3) suspicious-login/payment/security-notice triage correlated with the owner’s known Mac activity. I also specified a concrete long-press interaction that binds the pendant to the current Safari tab without putting page contents on the pendant. What I still need is not another planning permission: the browser enqueue wrappers must become live, Safari must expose reliable active-tab/list-tab results, and the USB/LTE pendant event path plus ephemeral redaction-aware evidence handling must be wired. The current single-button nRF9160 prototype is sufficient for testing the gesture over USB today.

**Biggest unknown:** Whether the live Safari extension can currently create and report a tab through a real /execute browser action; the granted enqueue tools remain implementation stubs, so authenticated page workflows cannot yet be exercised end-to-end.

