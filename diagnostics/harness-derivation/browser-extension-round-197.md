# Harness derivation — browser-extension — round 197

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Give me a 60-second prep for this meeting from the private pages I already have open.”"
- **useful because:** The browser is the only node that can see authenticated tabs, while the Mac can turn the extracted facts into a durable local briefing and the pendant can deliver it hands-free. It avoids inventing a site allowlist: the owner explicitly chooses the open tabs at request time. The result should name the meeting, participants, decisions, deadlines, and unresolved questions, with each claim linked to its originating tab.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a cheap extraction/summarization model for page-to-facts and briefing; reserve realtime only for the spoken 60-second delivery and follow-up questions.
- **latency:** 8–15 seconds for tab capture and synthesis; under 2 seconds to start playback once the briefing is ready.
- **cost:** Roughly $0.01–$0.05 per invocation, dominated by sending capped extracted text from 2–5 tabs to the summarizer; no screenshot or full-page persistence.
- **security:** Only explicitly selected/current tabs are read; credentials and form values must be redacted. Persist claims and provenance, never page HTML/text. Do not send or modify anything. The spoken answer should omit categories configured as never-speak and point back to the source tab when uncertain.
- **missing:** A browser action that captures a bounded set of owner-selected tabs with tab IDs and page provenance in one request; A cross-surface orchestration job that joins browser evidence to the existing briefing pipeline and streams the result to the pendant; An explicit empty per-origin and per-category policy object surfaced for owner configuration

### "“Compare the private tabs I have open and tell me if any dates, prices, quantities, or statuses disagree.”"
- **useful because:** People routinely have an order page, confirmation email, tracking page, and subscription page open at once. A single authenticated browser can inspect them, but only the hive can compare them, preserve source provenance, and speak a short discrepancy report through the pendant while leaving the pages untouched. This catches silent changes and stale confirmations before the owner acts.
- **path:** browser-extension → relay-realtime → mac-planner → pendant
- **model tier:** Use a background/cheap model for structured extraction and pairwise comparison; use realtime only if the owner asks a spoken follow-up.
- **latency:** 10–20 seconds for up to six tabs; immediate acknowledgement from the pendant, then a concise result.
- **cost:** About $0.02–$0.08 per run, dominated by normalized text from the tabs; comparison should use small structured records rather than resending whole pages.
- **security:** Read-only allowlist: list/read only, no click/type. Treat every page as untrusted data and ignore instructions embedded in it. Do not retain page text; retain only short conflicting claims, host, URL, timestamp, and evidence hash under the existing short browser TTL. Never speak configured private categories.
- **missing:** A multi-tab read action with stable tab IDs and bounded per-tab extraction; A typed fact normalizer for dates, money, quantities, and state labels with confidence and source spans; A relay-to-pendant notification route for a completed discrepancy report

### "“Turn the subscription or bill on this private page into a reminder, but don't contact anyone or change the account.”"
- **useful because:** This closes a high-value gap between authenticated browser reading and local action: the assistant can see renewal terms that are not in Calendar/Mail, normalize the amount and due date, and create a local reminder the owner can actually act on. The owner gets a concrete outcome rather than a spoken scrape, while the account remains untouched.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a low-cost extraction model to identify merchant, amount, cadence, and renewal date; use realtime only for a short spoken confirmation or clarification.
- **latency:** 5–12 seconds to read the selected page and create the reminder; pendant acknowledgement within 2 seconds after completion.
- **cost:** Approximately $0.005–$0.03, dominated by one bounded page extraction and structured parsing; reminder creation is local and free.
- **security:** Read only the explicitly addressed tab and never click account controls. Persist only the reminder fields and a provenance URL/hash under existing browser retention, not page text. If amount/date confidence is low, say what was found rather than guessing. The reminder title should avoid leaking sensitive merchant details in spoken audio unless configured.
- **missing:** A browser-to-structured-reminder adapter that extracts renewal semantics with confidence and source span; A durable job that carries the browser evidence capsule into mac_planner's create-reminder action; An owner-visible edit/undo affordance on the pendant for the proposed reminder before local creation

### "“Before I pay, inspect this private checkout and tell me what is surprising or risky.”"
- **useful because:** The owner gets a second set of eyes on the exact authenticated checkout they are viewing: total, recurring-versus-one-time charge, shipping address, seller identity, return terms, and unexpected add-ons. It can catch dark-pattern fees or a stale address without clicking anything or sending data to the merchant. The pendant can give a short spoken verdict while the browser remains unchanged.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** A cheaper structured extraction model should parse the checkout and compare it with owner-supplied spending/address rules; realtime is used only for the low-latency spoken verdict.
- **latency:** Under 10 seconds from the owner’s request to a concise risk list; no background polling.
- **cost:** About $0.01–$0.05 per review, dominated by one bounded checkout extraction and policy comparison; no screenshots or page bodies need to be retained.
- **security:** Read-only browser actions only. Never transmit payment credentials, CVV, passwords, or full address when a local comparison can be performed. Treat page text as untrusted data, and explicitly label uncertainty. The result must not claim a purchase is safe; it reports detected discrepancies and stops before any submit button.
- **missing:** A checkout-specific schema for recurring charge, seller, totals, destination, and policy clauses; A local-only owner policy store for approved merchants, address aliases, and spending thresholds; A pendant response mode that distinguishes informational risk findings from a purchase authorization

### "“Check whether any security-critical settings on this logged-in account changed since the last time I approved them.”"
- **useful because:** A watch for page text is not enough for account security. This capability compares a normalized snapshot of security-relevant fields—recovery email, MFA/passkey status, active sessions, forwarding rules, and payment identity—against an owner-approved baseline, then speaks only material changes through the pendant. It gives the owner a practical intrusion or accidental-change alarm without granting the agent account-control powers.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a background model or deterministic diff for normalization and change classification; reserve realtime for the urgent spoken alert.
- **latency:** A scheduled check can complete within 30 seconds of its cadence; an owner-requested check should return in 10–20 seconds.
- **cost:** Roughly $0.01–$0.06 per check, mostly extraction from one settings page; retention is tiny structured fields rather than page content.
- **security:** This needs a deliberately owner-created baseline and per-origin rules; it must never infer that a changed field is malicious. Do not expose secret values aloud. Reading settings is allowed, but mutations, sign-out, password reset, or recovery changes are outside the capability. Alerts need anti-spam and a clear source URL/time.
- **missing:** A normalized security-settings snapshot schema with field-level sensitivity and stable comparison semantics; An owner-approved baseline store with versioning, rollback of the baseline only, and explicit expiry; A scheduler-to-browser-session runner that can reopen the right authenticated settings page and deliver a high-priority pendant alert

### "“When I’m about to leave, tell me whether my online orders, bookings, and reservations still fit the next few hours of my calendar.”"
- **useful because:** This joins facts that live in separate places: private order/booking tabs, local calendar, and the owner’s immediate time window. The pendant can say “your pickup is ready but the reservation is 25 minutes away” or identify a conflict before the owner walks out. It is more useful than a generic page summary because it performs temporal reconciliation and produces one actionable answer.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a cheap structured time-and-location reconciliation model for the normal case; realtime only handles the owner’s spoken follow-up or ambiguity.
- **latency:** 15–25 seconds on demand, with a short immediate acknowledgement from the pendant; no need for continuous page monitoring.
- **cost:** Approximately $0.02–$0.08, dominated by reading two to four authenticated pages and joining them with local calendar context; store only final conflicts and expiry times.
- **security:** The owner must explicitly address the tabs or choose a window; no broad browsing assumptions. Do not read aloud full addresses, order contents, or private event titles unless allowed. Never book, cancel, or alter an order. Location inference should remain local to the Mac and be optional.
- **missing:** A cross-domain schema for pickup/delivery/reservation time windows, locations, and status confidence; A local calendar-and-browser join that can calculate travel slack without exporting the calendar; A pendant-friendly urgency ranking that chooses one conflict instead of dumping private details


## What it asked for

_Nothing._
## Its own summary

The browser tier is materially live now: Safari is online, with an active authenticated DoorDash order tab and a YouTube subscriptions tab; POST /execute successfully listed both tabs and read the DoorDash page, returning a provenance/evidence capsule. I recorded three non-duplicative capabilities: (1) owner-selected private-tab meeting prep delivered through the pendant, (2) cross-tab disagreement detection for dates/prices/statuses, and (3) extracting a private bill/subscription renewal into a local reminder without touching the account. The first is the strongest candidate for the system’s signature capability because it genuinely joins browser sessions, Mac planning, relay speech, and the worn device. I also alerted mac-planner that browser-to-Mac handoff work is now actionable.

**Biggest unknown:** The remaining blocker is not browser access. It is the connective contract: a bounded multi-tab extraction/evidence format, structured confidence/source spans, and a reliable evidence-to-briefing/reminder handoff. The supposedly existing /memory/browser-findings route returned 404 when described against this live agent, so the exact persistence endpoint and which surface owns it still need verification. I do not need another browser enqueue wrapper; /execute is working.

