# Harness derivation — browser-extension — round 156

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser availability** — Safari extension is online and actively reports 9 tabs, including authenticated Gmail (mail.google.com) and X (x.com); the active tab is X. POST /execute with browser_list_tabs completed successfully with a receipt.
  - evidence: POST /execute action browser_list_tabs at 2026-08-08T01:54:51Z returned tabCount=9, Safari extension v1.2.0, Gmail tab 901464, active X tab 1163292.

## Capabilities it proposed

### "“Before I submit this form, check every field against the source documents in my Gmail/Drive and tell me exactly what is missing or inconsistent.”"
- **useful because:** This is a high-value browser-only safety net: Safari can see the authenticated form and source records that the relay cannot, while the Mac can compare dates, names, amounts, and attachments. It catches stale addresses, wrong invoice numbers, and missing uploads without taking the irreversible submit action.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use the cheaper background model for document retrieval/field comparison; use realtime only to answer the owner's short follow-up and speak the final discrepancy list.
- **latency:** 10–30 seconds for extraction and comparison; spoken result should begin within 2 seconds after the comparison completes.
- **cost:** ~$0.01–$0.08 per check depending on source-document volume; browser command latency and document context dominate, not model inference.
- **security:** Form contents and authenticated source documents leave Safari for the local Mac agent and relay unless a local-only mode is selected. Never persist raw fields by default; retain only a short-lived discrepancy capsule. Redact passwords, payment CVV, and unrelated email. The owner must explicitly invoke this and the system must stop before submit.
- **missing:** A browser action that returns typed form fields plus nearby labels without input values for password/payment fields; A local-only comparison mode that keeps extracted source text on the Mac; A deterministic field provenance map so each spoken discrepancy cites its source page/document

### "“Turn the event details I’m looking at in Safari into a reminder draft, preserving the source link and the page’s timezone; read the draft to me before creating it.”"
- **useful because:** Event pages hide dates, registration deadlines, and time zones in prose. The authenticated browser can read the exact page the owner is viewing, the Mac can create the reminder, and the pendant can announce a concise draft while the owner is away from the keyboard. It avoids silently creating a wrong-time reminder.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Background/standard model extracts structured event fields; realtime is only for the spoken confirmation and corrections.
- **latency:** 5–12 seconds from request to a spoken draft; reminder creation waits for the owner's explicit confirmation.
- **cost:** ~$0.005–$0.03 per invocation; extraction and browser round trips dominate.
- **security:** Only the active tab and visible event region should be read; do not capture login state or unrelated tabs. The reminder title, date, timezone, URL, and alert time are shown/spoken before creation. Creating the reminder is reversible but still requires explicit confirmation.
- **missing:** Active-tab scoped semantic extraction of event fields (including timezone and source spans); A confirmation token that binds the exact reminder draft to the subsequent create action; A spoken correction loop that can adjust date/time without rereading the whole page

### "“Verify that the cancellation/refund I made online actually took effect: check the service’s authenticated account, the confirmation email, and the matching transaction, then tell me what evidence agrees or conflicts.”"
- **useful because:** A successful click is not proof that money or access changed. Safari is the only node with the owner's authenticated service and mail sessions; the Mac can correlate identifiers and amounts, and the pendant can deliver a short verdict without making another mutation. This closes the loop on consequential web actions rather than merely automating clicks.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a background model for multi-page evidence extraction and identifier/amount reconciliation; realtime only speaks the final verdict or answers a follow-up.
- **latency:** 20–60 seconds for three authenticated sources; if a portal is unavailable, report partial evidence rather than waiting indefinitely.
- **cost:** ~$0.02–$0.12 per verification; browser navigation and page extraction dominate.
- **security:** Read-only by design, but transaction and email data are highly sensitive. Keep raw page text in an expiring local capsule, speak only merchant/status/amount/date, and never expose full account numbers or message bodies. Require the owner to name the transaction or select the relevant tab; do not infer from arbitrary tabs.
- **missing:** Cross-origin browser session orchestration that can bind the service tab, Gmail tab, and optional financial tab to one verification job; A typed evidence schema for refund/cancellation status, amount, transaction ID, and effective date; Conflict handling that asks the owner which source to trust instead of guessing

### "“Check my currently booked trip and tell me only what changed since I last looked—flight status, gate/time changes, messages from the airline, and whether my calendar needs updating.”"
- **useful because:** Travel disruption is where authenticated browser access matters: booking portals and airline messages are private, while public flight data alone is incomplete. Safari supplies the booking and inbox evidence, the Mac reconciles it with Calendar, and the pendant gives a compact alert while the owner is moving.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Background model performs scheduled or on-demand extraction and change classification; realtime speaks only urgent changes or answers “what changed?” in conversation.
- **latency:** On-demand result in 15–45 seconds; urgent gate/time changes should enqueue an alert within 2 minutes of the configured poll.
- **cost:** ~$0.02–$0.15 per trip check depending on number of portal pages and messages; browser session work dominates.
- **security:** Read only the selected booking/airline origins and relevant messages; never read payment details. Persist a normalized itinerary fingerprint and change summary, not raw boarding passes or email bodies. The owner must configure origins and quiet hours; never invent a travel profile.
- **missing:** A user-supplied origin/booking configuration and itinerary identity resolver; A cross-origin extractor for itinerary segments, local departure timezone, gate, and status; A change classifier that distinguishes volatile gate changes from meaningful cancellation/delay changes and routes only urgent ones to offline_alert_inbox

### "“I selected this order, invoice, or case number—find every matching record across my logged-in sites and email, then give me one consistent timeline with links back to each source.”"
- **useful because:** The same identifier is often scattered across a vendor portal, Gmail, a support system, and local records. Today no single node can correlate those private sessions. A user-selected token gives the browser a precise scope while the Mac and relay reconcile dates, amounts, statuses, and contradictory records into something the owner can act on.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a background model for cross-source retrieval and normalization; realtime is only for the owner's spoken question and concise result.
- **latency:** 15–60 seconds for a bounded search across configured origins; return partial results with clear source coverage rather than blocking on one unavailable site.
- **cost:** ~$0.03–$0.20 per lookup, dominated by authenticated navigation and page extraction.
- **security:** Search begins only from an explicit owner selection or dictated identifier, never arbitrary page contents. Origins and categories must be configured by the owner. Keep raw records in expiring local memory, speak redacted identifiers, and preserve per-fact source links so the owner can audit the result.
- **missing:** A selection-scoped browser capture carrying the selected text, origin, tab, and a short-lived nonce; A configured cross-origin search plan with per-site extraction rules and a maximum page/record budget; A provenance-preserving reconciliation format that can represent conflicting statuses without silently choosing one

### "“Read the access code, pickup instructions, or one-time reference from the private page I’m viewing and keep it available on my pendant until I say ‘clear it.’”"
- **useful because:** Owners routinely need a short secret or reference while their hands and eyes are away from Safari—at a building door, pickup desk, or phone call. The browser can retrieve the exact selected value, the Mac/relay can deliver it, and the pendant can replay it offline without exposing the whole page.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a small background extraction model or deterministic DOM field lookup; realtime is unnecessary except for the owner's request and a short spoken replay.
- **latency:** Under 5 seconds for extraction and first playback; replay must work offline after delivery.
- **cost:** Under ~$0.01 per invocation; transport and TTS dominate.
- **security:** This handles highly sensitive one-time data. Require explicit selection or field targeting, never infer codes from arbitrary tabs; encrypt in transit and at rest, auto-expire after a short owner-chosen TTL or one replay, and wipe on ‘clear.’ Do not show it in logs, receipts, or model context beyond the extraction step.
- **missing:** A pendant-side volatile secret buffer with immediate wipe and replay counter, distinct from ordinary alert storage; A browser result type for explicitly owner-selected short values with no page-text fallback; End-to-end redaction rules preventing the value from entering ordinary job logs and spoken transcript storage

### "“I’m on a support call—look up the account while I talk, and whisper only the next useful fact or question when I ask.”"
- **useful because:** During a live call the owner cannot safely navigate a private portal and listen at the same time. Safari can inspect the authenticated account, the Mac can maintain a call-side fact sheet, and the pendant can deliver short, on-demand prompts without sending a message or changing the account.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a fast background model for bounded account lookup and fact extraction; realtime handles only short owner queries and spoken answers, not the portal crawl.
- **latency:** Initial lookup under 10 seconds; each follow-up fact under 3 seconds, with an explicit ‘still searching’ response rather than stale guessing.
- **cost:** ~$0.02–$0.10 per call-side session, primarily page reads and context refreshes.
- **security:** The owner must explicitly start and end the call-side session and identify the account/page scope. Read-only, no form filling, no recording of call audio, no raw page persistence, and no sensitive values (full account numbers, passwords, payment data) in speech. Every answer includes its observed timestamp and source origin internally.
- **missing:** A bounded browser research session that can keep a private fact sheet while accepting incremental voice questions; A compact spoken-answer protocol with freshness/source metadata and a hard no-mutation action set for this mode; A session teardown that cancels queued reads and securely deletes the fact sheet on owner command


## Changes it proposed to its own stack

### `integration` — Connect authenticated browser verification jobs to the pendant's offline_alert_inbox as a delayed evidence follow-up. When a browser transaction is initiated or observed but its final state is not yet available, persist only a redacted job handle and expected evidence deadline; a background Mac/Safari check later resolves it and sends a priority alert containing status, amount/date, and a deep link back to the relevant tab. The alert must be deduplicated by transaction identifier and expire after resolution.
- **owner gets:** The owner can walk away after starting a cancellation, support request, or refund and still learn the outcome without keeping Safari open or remembering to ask again. This is a genuinely cross-node handoff: Safari sees the private account, the Mac retries it, the relay schedules the check, and the worn device delivers the result offline.
- effort: Medium-high: durable delayed-job state, browser session reattachment, redacted evidence normalization, and a relay-to-firmware alert adapter.  ·  risk: A stale or wrong page could produce a false resolution; label every alert with observed time and evidence source, retry conflicts, and allow the owner to dismiss/clear the pending handle. Recovery is a manual recheck command from the pendant or Mac.
- cost: ~$0.01–$0.08 per follow-up check plus negligible alert transport; browser polling and page extraction dominate.  ·  latency: No impact on the immediate request; outcome arrives on the configured cadence (for example 5 minutes, then 1 hour).
- security: Do not store raw page/email text or credentials. Store a salted transaction fingerprint, origin, redacted status, and expiry. The spoken/LED alert must omit full account numbers and message bodies.
- depends on: A durable browser job runner and session resurrection (chg-16bc5dee / chg-b1e17760); An authenticated page-watch implementation (chg-e767dfc0); The accepted offline_alert_inbox firmware skill; A relay scheduler that can wake a Mac-bound browser check

### `new-surface` — Add a browser-to-pendant ‘private handoff’ surface: Safari can send one explicitly selected page value (text, QR payload, address, or short reference) to a relay-issued nonce. The relay routes it to the Mac-bound pendant as an encrypted, expiring capsule; the pendant confirms receipt with a distinct tone, supports replay on button press, and wipes it on expiry, second use, or a spoken/button clear command. The capsule is deliberately not a browser page capture, job receipt, journal item, or normal alert.
- **owner gets:** The owner can move a private, short-lived piece of information from a logged-in web page into the physical world without carrying the laptop or exposing the entire page—useful for pickup codes, building access, reservation references, and directions.
- effort: High: Safari selection/QR extraction, nonce binding, relay routing, encrypted pendant delivery, volatile storage, replay/wipe UX, and explicit exclusion from logs and model context.  ·  risk: A wrong selection or shoulder-surfed playback could expose the value. Show the selected value and TTL before handoff, use a distinct confirmation tone, cap replay count, auto-wipe aggressively, and provide a physical clear action. If delivery fails, retain nothing and report failure.
- cost: Negligible model cost; roughly $0.01–$0.05 per handoff for relay traffic/TTS. Firmware work fits only if the volatile capsule is tightly bounded (for example <1 KB plus metadata).  ·  latency: 2–5 seconds while connected; after delivery, replay is local and sub-second.
- security: Higher sensitivity than ordinary browser extraction. Use per-handoff nonce, authenticated encryption, no raw value in logs/receipts/transcripts, origin and expiry metadata only, and owner-configurable categories that may never be handed off.
- depends on: A functioning Safari command enqueue path with an explicit selected-value/QR operation; Relay routing to a Mac-connected pendant rather than assuming LTE registration; A small firmware volatile secret buffer and wipe/replay state machine; The owner's empty-by-default per-origin and per-category privacy configuration


## What it asked for

_Nothing._
## Its own summary

Safari is genuinely usable now: the live extension reports 9 tabs, including authenticated Gmail, and POST /execute browser_list_tabs returned a receipt. I recorded that finding and proposed four owner-facing capabilities beyond simple browsing: pre-submit field/source reconciliation, event-page-to-reminder drafting with timezone provenance, cross-site cancellation/refund verification, and authenticated trip-change alerts. I also proposed a cross-node integration that turns unresolved browser transactions into redacted offline_alert_inbox follow-ups on the pendant. The strongest near-term opportunity is transaction verification plus delayed wearable notification: only Safari can see the private account, while the Mac/relay/pendant close the loop after the owner walks away.

**Biggest unknown:** The owner has not supplied the first authenticated origins or privacy rules, so these must remain explicit configuration rather than hardcoded site assumptions. The browser enqueue wrapper tools are still ambiguous/unimplemented, but direct POST /execute is working; a typed browser_read_page/browser_snapshot tool would make this agent less dependent on raw route calls.

