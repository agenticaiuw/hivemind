# Harness derivation — mac-planner — round 243

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Check my authenticated work portal every weekday morning and tell me only what is genuinely urgent or requires me.”"
- **useful because:** Turns a browser session the Mac agent cannot otherwise see into a concise spoken queue, without dumping portal noise or requiring the owner to open the site. This is the previously denied request re-filed against the browser harness, where the authenticated session actually lives.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Background/cheap model for polling and first-pass ranking; realtime only to answer a follow-up spoken question.
- **latency:** Scheduled poll can take 10–30 seconds; spoken result should be ready within 3 seconds after the morning routine fires.
- **cost:** Low: one browser snapshot/diff plus a small ranking call per poll; dominated by portal page size, with incremental DOM/text hashes avoiding repeated full context.
- **security:** Never export cookies, passwords, or full page HTML. Keep extraction inside the browser extension, send only redacted changed-item title, age, sender/owner, and link. Owner must explicitly authorize the portal origin and polling schedule; destructive portal actions are out of scope and would require a separate request.
- **missing:** A browser page-watch/diff routine that can run on an authenticated session and retain only redacted item fingerprints; An owner-configurable origin allowlist and urgency rules; A scheduler trigger that can invoke the browser watch and deliver its result to the pendant inbox

### "“I’m stuck—figure out the single next action I should take, and if it’s safe, put me there.”"
- **useful because:** The pendant is the only surface that can ask this hands-free, while the Mac and browser are the only surfaces that can see the actual work state. The system would stop giving generic summaries and instead select one concrete, context-aware next step, such as opening the right document, replying to the already-selected message, or resuming the correct authenticated page.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Realtime model interprets the short spoken request and delegates; a cheaper judgement model ranks calendar/mail/project/browser candidates; the Mac planner executes only the selected open/focus action.
- **latency:** Under 4 seconds to speak the proposed next action; under 8 seconds to open the target surface after the owner says “do it.”
- **cost:** Moderate per invocation: bounded Calendar/Mail reads, one browser snapshot when relevant, and a short ranking call. Cost is controlled by sending metadata and snippets, not entire documents.
- **security:** The system must distinguish navigation/opening from sending, deleting, or submitting. Keep credentials and page bodies in their native surfaces; redact message bodies by default. The owner should be able to say “just tell me” versus “put me there,” with mutation classes never inferred from a vague request.
- **missing:** A cross-surface candidate normalizer that gives calendar/mail/browser/project items stable IDs and deep links; A lightweight next-action ranking policy with explicit exclusions (no send, submit, delete, or purchase); A spoken result/receipt path from Mac execution back to the pendant

### "“Send that to the right person.”"
- **useful because:** A short pendant bookmark or spoken note becomes a routed, reviewable communication: the relay captures intent, the browser finds the relevant authenticated conversation or contact, and the Mac prepares the message in the correct app. The owner no longer has to remember who should receive a thought or hunt through tabs later.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** Realtime for the owner’s brief utterance; a cheaper background model resolves recipient candidates and extracts the note; realtime returns only the ambiguity question if there are multiple plausible recipients.
- **latency:** Ask one disambiguation question within 3 seconds; draft in under 10 seconds. Never send without an explicit final spoken confirmation.
- **cost:** Moderate: transcription plus a bounded contact/conversation search and one draft-generation call. Dominant cost is authenticated page extraction, which should be limited to candidate names and recent thread labels.
- **security:** Recipient resolution is high-risk: show the proposed recipient, channel, and exact draft on the Mac before sending, and speak a short confirmation on the pendant. Do not copy address books or full conversations to the relay; browser-side matching should return opaque candidate IDs and redacted labels. Sending, posting, or external sharing remains a separate confirmed action.
- **missing:** A browser-side contact/thread resolver that returns candidate IDs without exporting private page data; A durable link from an offline_moment_bookmark or voice memo to the owner’s current spoken intent; A Mac draft-only action and receipt that can be confirmed from the pendant

### "“Do it, then prove to me it really took effect.”"
- **useful because:** Today the Mac executor can report that it issued clicks or keystrokes, but that is not evidence that a web app saved, sent, or updated anything. A post-action witness would inspect the resulting browser state (or native app state), compare it to the intended change, and give the owner a concise success or failure on the pendant instead of a misleading execution receipt.
- **path:** mac-planner → browser-extension → relay-realtime → pendant
- **model tier:** Cheap deterministic verifier first (URL, visible confirmation, changed record fingerprint); realtime model only interprets ambiguous visual evidence and explains failure.
- **latency:** Verification within 5 seconds for ordinary browser actions; if inconclusive, tell the owner immediately rather than waiting.
- **cost:** Low-to-moderate: one bounded post-action inspect and a hash/fingerprint comparison; model cost only for ambiguous pages.
- **security:** Never claim success from an executor receipt alone. Keep before/after snapshots redacted and short-lived. For sends, purchases, deletes, or submissions, require the owner to see/hear the exact target and retain an auditable before/after receipt; a failed verification must not retry automatically.
- **missing:** A plan-level assertion schema describing the expected postcondition (URL, text marker, record fingerprint, or file hash); A browser verification command that can run after a Mac action and return redacted evidence; A unified receipt that joins Mac execution, browser observation, and pendant delivery

### "“I was offline for a while. Reconcile everything I said, everything you attempted, and tell me what still needs doing—without doing anything twice.”"
- **useful because:** A dropped LTE link, a sleeping Mac, and retried browser/Mac jobs currently leave separate fragments: pendant bookmarks and audio retries, relay jobs, and desktop receipts. The owner needs one trustworthy recovery answer that distinguishes captured intent, attempted action, confirmed outcome, and safe-to-retry work. This is not another briefing or inbox; it is causal reconciliation across a network partition, with duplicate suppression.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Background reconciliation model builds the event graph and identifies conflicts; realtime model answers the owner’s short recovery question and asks only about genuine ambiguity.
- **latency:** When connectivity returns, reconcile within 30 seconds; spoken answer within 3 seconds after the owner asks.
- **cost:** Moderate one-time cost after reconnection: compact event manifests and receipts, then a small conflict-resolution call. Audio bodies stay on their originating device and are not resent into the reasoning context.
- **security:** Treat unacknowledged actions as unconfirmed, never successful. Preserve idempotency keys and target fingerprints; do not replay sends, purchases, deletions, or submissions automatically. Show the owner a redacted conflict list and require confirmation for any retry or compensation action.
- **missing:** A cross-node append-only event envelope with monotonic device sequence, server receipt, idempotency key, and causal parent; A reconciliation service that joins pendant_store records, relay jobs, Mac receipts, and browser result commands without copying private payloads; A recovery plan that classifies each item as captured, attempted, confirmed, conflicted, or retryable and can hand one selected retry to the existing planner

### "“When I come back to this document or web page, remind me what I meant to do here.”"
- **useful because:** A timestamp reminder is easy to miss; an artifact-linked reminder appears only when the owner is actually back at the same file, URL, meeting thread, or project. The pendant can capture the intent immediately, while the Mac/browser can later prove that the matching artifact is in view and deliver the reminder at the useful moment.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Cheap background matcher compares normalized file/page identifiers and expiry; realtime is used only to interpret a vague captured note or answer a spoken follow-up.
- **latency:** Detect a matching foreground artifact within 2 seconds of navigation or focus; deliver a short pendant alert without interrupting active audio.
- **cost:** Low: hashes, titles, URLs, and short owner-authored notes; no repeated page-body or document upload. Main cost is browser heartbeat and Mac observation while the feature is armed.
- **security:** Store an opaque artifact fingerprint rather than sensitive document contents. Support expiry, one-shot delivery, and a local privacy latch. Never infer a match from a broad keyword alone; require exact origin/path or a high-confidence document identity.
- **missing:** A capture record that accepts an artifact anchor (file identity, URL/origin, or calendar event) alongside the existing timestamp bookmark; Foreground artifact events from Mac and browser with stable, redacted identifiers; A relay matcher and deduplicating pendant delivery policy for artifact-linked reminders

### "“Find a time with them, but don't commit me until I hear the options.”"
- **useful because:** The pendant can identify the person and constraints hands-free; the Mac knows the owner's real calendar; the browser may hold the authenticated scheduling or messaging session. The system can offer a few conflict-free options and prepare—not send—the appropriate reply, preventing the common failure where a generic assistant proposes times that are already impossible.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Realtime parses the request and ambiguity; a cheaper scheduling model computes options from Calendar and the authenticated scheduling page; realtime reads back three options.
- **latency:** Return options in 8 seconds for a normal week; draft the reply after the owner selects one, with no unattended send.
- **cost:** Moderate: bounded Calendar range read, one browser inspection, and a small scheduling call. Cost is proportional to candidate events, not full mail or page bodies.
- **security:** Treat attendees, calendar details, and authenticated scheduling data as private. Keep the recipient and proposed times explicit. Never send, book, cancel, or expose calendar details without a separate owner confirmation; timezone and working-hours assumptions must be spoken when uncertain.
- **missing:** A cross-surface identity resolver for “them” that can return candidates without exporting address books; A scheduling constraint contract covering timezone, working hours, travel/buffer, and acceptable alternatives; A draft-only browser/Mac action with a durable pending proposal that the pendant can present and expire


## What it asked for

_Nothing._
## Its own summary

This round produced four distinct owner-facing capabilities: browser-authenticated work-portal triage (re-filed against the browser harness), cross-surface next-action selection, recipient-aware “send that to the right person” drafting, and postcondition verification that proves a Mac/browser action actually took effect. The live inventory confirms Safari (2 tabs) and the Mac bridge are online, so these can be prototyped on the Mac today; the wearable’s LTE registration remains unavailable, so pendant delivery must be tested through the attached/relay path.

**Biggest unknown:** The remaining blockers are product policy and missing connective contracts, not discovery: the owner must name/authorize portal origins and urgency rules; the system needs browser-side redacted contact/thread resolution, a plan postcondition schema plus unified Mac/browser receipt, and a cross-surface candidate normalizer for next-action ranking. I do not need to re-request Accessibility, semantic-context access, or serial transport this round.

