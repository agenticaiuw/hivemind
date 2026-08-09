# Harness derivation — browser-extension — round 214

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “review this purchase,” inspect the authenticated cart or checkout page in Safari, read back the item, seller, total, shipping, delivery date, subscription terms, and return policy, then leave the form filled but stop before buying. Let me say “buy it” only after I have heard the exact final total."
- **useful because:** It turns the browser's unique access to logged-in shopping sessions into a safe spoken decision packet: the owner can shop hands-free without losing the final irreversible step or having to find the Mac screen.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** Realtime for the short spoken review and confirmation; background/local extraction and arithmetic should use the Mac planner or a cheaper model, not realtime.
- **latency:** Under 10 seconds to inspect and summarize a normal checkout; filling fields can continue in the background, but never submit without the owner's explicit follow-up.
- **cost:** One short realtime turn plus one local browser extraction, roughly $0.01–$0.05 depending on page complexity; browser and Mac work dominate latency, not tokens.
- **security:** Checkout pages contain addresses, payment metadata, and possibly health-sensitive purchases. Send only extracted fields and provenance to relay, never screenshots or card numbers; stop before purchase and preserve the existing purchase confirmation policy.
- **missing:** A checkout-specific extraction schema for totals, seller, delivery, subscription, and returns; A browser-side “filled but not submitted” checkpoint and undo receipt; An explicit spoken confirmation handoff bound to the exact cart fingerprint

### "Find the important page I was looking at yesterday, tell me what changed since then, and put me back at the exact section I had reached."
- **useful because:** This is a browser-only continuity problem: Safari owns authenticated tabs and scroll state while the pendant is the quickest way to ask. It rescues work across a dropped Mac session instead of making the owner remember a URL or search again.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** Use a cheap background model to rank tabs and compare short-lived page claims; use realtime only to answer the owner's spoken request and narrate the result.
- **latency:** 15 seconds for tab inventory, page extraction, and diff; navigate and restore the best candidate immediately, then speak a one-sentence result.
- **cost:** Usually one browser pass and a small model call, under $0.02; the expensive part is authenticated page extraction and waiting for dynamic content.
- **security:** Do not persist page bodies, screenshots, or raw URLs beyond the existing browser provenance and 24-hour finding TTL. Require an explicit per-origin configuration when none exists; expose the selected tab, host, and evidence before any navigation that could alter unsaved work.
- **missing:** A durable per-tab checkpoint containing host, title, canonical URL, semantic section anchor, and extraction timestamp; A page-diff worker that compares claims rather than HTML; A browser action to restore a semantic anchor without discarding unsaved form state

### "Read the next unread item in my authenticated web app, turn only its actionable deadlines into reminders, and tell me which item you used."
- **useful because:** It combines the browser session nobody else can reach with the Mac's reminder surface and the pendant's offline alert inbox. The owner gets deadlines from a private web workflow without a daily portal ritual or losing them when the Mac disconnects.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Background model ranks unread items and extracts dates; realtime is used only for a concise spoken confirmation or ambiguity question. Deterministic date parsing and reminder creation stay local.
- **latency:** 20 seconds for one unread page; create reminders immediately after extraction and deliver a compact alert later if the pendant is offline.
- **cost:** One small extraction call, typically under $0.03; browser page load and dynamic authentication are the main cost.
- **security:** Ship only deadline, title, host, and provenance—not page text—to the relay and memory. Never infer a deadline from ambiguous language without marking uncertainty; reminders should include a source URL and be undoable. Empty origin/category policy remains the default until the owner supplies it.
- **missing:** A browser unread-item selector and deterministic deadline/date extraction; A cross-surface reminder receipt linking reminder ID to browser provenance; A deduplication rule for changed deadlines and an offline alert payload

### "While I am on a private booking or appointment form, tell me whether its date, time, location, and names conflict with my calendar or notes, and point out the exact fields I should fix before I submit."
- **useful because:** No current surface can join an authenticated page with the owner's local schedule while preserving the page as the source of truth. It prevents expensive double-bookings and identity mistakes at the moment they are made, without sending the form.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Local deterministic extraction first for dates, times, locations, and names; a cheap background model resolves wording ambiguities; realtime only speaks the concise conflict report.
- **latency:** Under 12 seconds after the page settles; fill nothing automatically, but offer exact reversible field edits if the owner asks.
- **cost:** One page extraction plus a small local calendar/files query, usually under $0.03; dynamic page waits dominate.
- **security:** Do not send full page text or unrelated calendar entries to the relay. Return only matched fields, conflict reason, host, and provenance; treat uncertain matches as uncertain and never silently alter or submit the form.
- **missing:** A structured private-form extractor for date/time/location/person fields; A local cross-source conflict matcher over Calendar and Notes; A field-level report and reversible edit plan tied to the current page state

### "I’m looking at an invoice or payment request in Safari—check whether the sender, amount, and bank details match my prior records and reputable public information, then tell me what is inconsistent before I pay."
- **useful because:** This gives the owner a fraud check that no single node can perform: Safari supplies the authenticated invoice, the Mac supplies prior local records, and the relay compares public evidence while the pendant makes the warning hard to miss.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Cheap background extraction and deterministic amount/account comparison first; use a research model for public-source corroboration; realtime only delivers the warning and confidence in one short sentence.
- **latency:** 30 seconds for a normal invoice; if evidence is incomplete, say so rather than blocking the owner or pretending verification.
- **cost:** One browser extraction, one local lookup, and a small web-research call, roughly $0.03–$0.15; public-source retrieval dominates.
- **security:** Never transmit full account numbers, payment tokens, or invoice bodies. Hash or last-four redact identifiers, keep claims short-lived with source URLs, and make the spoken result explicitly advisory. It must never pay, reply, or alter the invoice.
- **missing:** Invoice/payment-field extraction with strict identifier redaction; A local-record matcher for vendors and prior amounts; A public-source corroboration and confidence model that distinguishes absence of evidence from evidence of fraud; An offline-alert payload for high-confidence mismatch warnings

### "Compare the contract or policy I have open in my logged-in browser with the earlier copy in my Mac workspace, and tell me only which obligations, prices, dates, or cancellation terms changed, with the section for each change."
- **useful because:** The browser can reach the current private document while the Mac can reach the owner's prior file; combining them catches silent amendments and renewal traps without making the owner manually download, search, or line-edit two versions.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use deterministic document text and clause extraction where possible, then a cheaper comparison model; realtime only summarizes the changed clauses and answers follow-up questions against retained provenance.
- **latency:** 20–45 seconds for two ordinary documents; return a partial, clearly labeled comparison if either page or file is inaccessible.
- **cost:** One browser read, one local file read, and a bounded comparison call, roughly $0.03–$0.10; OCR or dynamic document rendering is the main variable.
- **security:** Keep full documents on the Mac where possible. Send only changed clause snippets, hashes, and source locations to the relay; do not persist the documents as browser findings. Never accept, sign, or send an amended agreement.
- **missing:** A browser PDF/document extraction path that preserves section anchors; A local file selector for the matching prior version; Clause-level semantic diff with confidence and source offsets; A spoken follow-up mode that can quote only the selected clause


## What it asked for

_Nothing._
## Its own summary

Recorded three distinct browser capabilities. Highest-value: an authenticated checkout review that reads every final amount/renewal/return term aloud, fills but never submits, and binds any later “buy it” to the exact cart fingerprint. Also recorded authenticated-page continuity (semantic checkpoint + claim diff + safe restore) and unread-web-item deadline extraction into Mac reminders plus the pendant’s offline alert inbox. What remains is implementation work, not another browser wrapper: checkout-field schema/cart fingerprint, semantic tab checkpoints and anchor restoration, unread-item/deadline extraction with reminder provenance and deduplication. I do not need another generic enqueue tool; the existing browser path is sufficient.

**Biggest unknown:** Which authenticated origins and web-app semantics the owner actually wants first; the configuration should remain empty until he supplies them, rather than inventing a site list.

