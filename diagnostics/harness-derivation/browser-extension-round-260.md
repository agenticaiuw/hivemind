# Harness derivation — browser-extension — round 260

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""What am I looking at?" Then, after I say "send it to my pendant," give me a short spoken summary of the active Safari page, with the title and the one next action I can take."
- **useful because:** This is the browser's unique reach turned into an instant wearable interaction: no copy/paste, no searching for the tab, and it works for pages behind existing logins. The browser supplies live text and provenance; the relay compresses it; the pendant delivers it while the Mac remains hands-free.
- **path:** pendant → relay → browser → mac-bridge
- **model tier:** Realtime for the brief spoken summary only; use a cheaper background model if the owner asks for a long digest.
- **latency:** Target 3–6 seconds from the spoken request; browser read is the dominant step.
- **cost:** One short realtime turn plus one browser read; roughly <$0.02 per request, dominated by model input/output.
- **security:** The page text leaves Safari for summarization, so default to the existing evidence capsule and 24-hour browser-fact TTL, never persist page text, and expose the URL/title before speaking. Ship an empty per-origin policy; the owner fills it later. No send/click occurs in this mode.
- **missing:** A reliable current-tab browser_read_page action callable from the relay voice intent (the raw POST /execute path works now, but the browser tool wrapper is unresolved); A voice intent that routes to the active tab and strips page text after summarization; A compact wearable response envelope carrying title, URL, and one next action

### ""Watch this authenticated page and tell me if anything important changes." Let me set a cadence, and alert me on the pendant only when a material claim or status changes; include a link and a one-sentence reason."
- **useful because:** The owner gets persistent value from browser sessions that no other node can reach: a login-protected dashboard, ticket queue, or account page becomes an attention filter rather than a page they must repeatedly check. The relay compares short-lived claims, and the pendant can deliver an alert even after the Mac link drops.
- **path:** browser → relay → pendant → mac-bridge → dashboard
- **model tier:** Background/scheduled model for polling, extraction, and semantic diff; realtime only when the owner asks why an alert fired.
- **latency:** Polling can be minutes to hours; alert delivery should begin within one cadence interval and queue locally if offline.
- **cost:** Low-cost browser reads and a small diff model per cadence; roughly $0.01–$0.10/day per watched page depending on frequency.
- **security:** Start with an empty per-origin configuration and explicit owner setup. Persist only host-keyed claims with the existing 24-hour browser TTL and provenance; never HTML, screenshots, or page bodies. Never auto-click or submit. Alerts should include only the minimum changed claim, and the owner can revoke a watch from the pendant.
- **missing:** A durable browser page-watch scheduler over browserSessions/pageWatch machinery; Semantic claim extraction and change thresholds that distinguish layout noise from material change; A watch lifecycle UI/API and pendant alert acknowledgement/revocation path

### ""Fill this out, but don't submit it." Show me a field-by-field preview, speak the sensitive fields privately, and let a single pendant press approve exactly this draft once; if the page changes, invalidate the approval."
- **useful because:** This is the highest-value browser capability: it turns authenticated web work into a safe, hands-free delegation without asking the owner to trust an opaque click. The browser can fill forms while the pendant supplies a physical, time-bounded approval; a stale page or altered field cannot silently become a submission.
- **path:** browser → pendant → relay → mac-bridge → dashboard
- **model tier:** Realtime for interpreting the request and speaking the concise diff; deterministic browser execution and hash checks do the rest.
- **latency:** Preview in 5–10 seconds; approval execution in under 3 seconds after the button press.
- **cost:** One short model turn plus browser actions, roughly <$0.03 per form; deterministic hashing dominates reliability, not API cost.
- **security:** Never submit on inferred intent. Create a canonical field diff, redact secrets from logs and speech, bind approval to origin + tab + form hash + expiry + session, and invalidate it on navigation or any changed field. Store provenance and undo metadata, not page bodies. This follows the owner's explicit destructive-action confirmation preference without inventing an origin allowlist.
- **missing:** A browser form-field extraction/fill primitive with canonical diffing; A pendant approval nonce/epoch channel and result receipt; A submit action that accepts only an unexpired matching form hash, plus invalidation on DOM/navigation changes

### ""Check this booking page against my calendar and tell me whether it conflicts with anything; if it does, name the conflicting event and leave the page unchanged.""
- **useful because:** This combines the browser's authenticated reach with the Mac's private calendar context into a decision the owner cannot get from either node alone. It prevents accidental double-booking without requiring the owner to copy dates, times, or timezone details into the assistant, and it deliberately stops before any reservation or cancellation.
- **path:** browser → mac-bridge → relay → pendant
- **model tier:** Use a cheap background extraction and deterministic timezone/interval comparison; use realtime only for the short spoken answer.
- **latency:** 10 seconds is acceptable: page extraction and calendar lookup can run in parallel, with the pendant answer arriving after the conflict check.
- **cost:** Usually <$0.02 per check; most cost is one small extraction/comparison call, not a long conversation.
- **security:** Only extract event title, start/end, timezone, and venue needed for the comparison. Do not persist booking-page text or calendar contents; retain a short-lived provenance capsule and speak the minimum necessary. Never click reserve, cancel, or submit. If the page is ambiguous, report uncertainty rather than guessing.
- **missing:** A browser-to-Mac structured handoff for normalized date/time facts with source anchors; A calendar interval query exposed to the browser workflow, including timezone normalization; A cross-surface conflict result that can be spoken and optionally shown with citations

### ""Compare the policy on this logged-in page with the current policy document in my workspace, and tell me exactly what changed; don't edit either one.""
- **useful because:** The browser can reach the live authenticated policy while the Mac can reach the owner's private source document. A side-by-side, provenance-backed difference report catches stale terms, pricing, or access rules that a browser-only reader or file-only assistant cannot see.
- **path:** browser → mac-bridge → relay → pendant
- **model tier:** Background model for document normalization and clause alignment; realtime only to answer follow-up questions about a reported difference.
- **latency:** 15–30 seconds for two reads and alignment; the owner receives a concise alert first and can request details.
- **cost:** Roughly $0.03–$0.15 per comparison depending on document length; context reduction and clause chunks keep cost bounded.
- **security:** Read only the selected page and explicitly named local document. Keep raw text ephemeral, retain only clause-level findings with URL/file provenance and short TTL, and never upload unrelated workspace files. No edits or navigation side effects.
- **missing:** A user-selectable local-document reference passed into a browser job; Clause-level normalization/alignment with exact source anchors on both sides; A redacted cross-source evidence capsule and spoken summary format

### ""Move the non-sensitive details from this authenticated page into the matching fields on the other open site, show me the mapping, and leave both pages unsubmitted.""
- **useful because:** The owner often has to transpose the same address, reference number, or appointment details between two logged-in services. Today the browser agent can read or act, but cannot safely produce a field-by-field, cross-origin transfer plan. This makes the tedious part automatic while preserving a clear boundary before any external write.
- **path:** browser → pendant → relay → mac-bridge → dashboard
- **model tier:** Deterministic field extraction, classification, and mapping first; a small model resolves labels that differ. Realtime only speaks the final mapping and ambiguity list.
- **latency:** 10–20 seconds for two pages; stop immediately if either page navigates or its form schema changes.
- **cost:** About $0.02–$0.08 per transfer preview, mostly field matching; no model call is needed for identical labels.
- **security:** Default deny transfer of passwords, payment data, authentication codes, health data, and hidden fields. Show origin-to-origin mappings and values before typing; never submit. Bind the preview to both tab IDs, origins, form hashes, and an expiry. Persist only redacted provenance, not either page body.
- **missing:** Cross-origin form schema extraction and a typed non-sensitive field classifier; A mapping preview that the pendant can summarize and the dashboard can display; A browser action batch that types only the approved mapping and invalidates on either page changing


## Changes it proposed to its own stack

### `browser-harness` — Add a browser-side 'claim stream' mode: on each read, normalize the page into labeled claims with DOM anchors and a content hash, then expose a diff event when the same tab/origin is reread. Keep raw text ephemeral; let the relay request only selected claim labels and let the extension report navigation/DOM changes that invalidate pending actions.
- **owner gets:** The owner can ask for changes or approve a draft with confidence that the answer refers to the same thing still on screen, rather than a stale page or a noisy full-page scrape.
- effort: Medium: extension content-script extraction, anchor normalization, hash/diff protocol, and relay integration.  ·  risk: Dynamic pages may produce false changes or miss canvas-rendered content; fall back to full read and mark confidence low. A browser restart invalidates all hashes.
- cost: Small ongoing CPU in Safari and tiny claim payloads; no meaningful model cost unless semantic diff is requested.  ·  latency: Adds under 500 ms to reads; semantic comparison can remain background.
- security: Improves minimization because only requested claims leave the browser; raw DOM is never persisted. Must ensure anchors do not leak hidden password values.
- depends on: browser_read_page working through the production command wrapper; A durable per-tab/session hash and invalidation event; The existing browser provenance and redaction machinery


## What it asked for

_Nothing._
## Its own summary

Discovered Safari is genuinely online with one live tab and verified the real path: POST /execute can list tabs and read page text with evidence/provenance. I recorded four new items: hands-free active-page summary to the pendant, authenticated page-watch with material-change alerts queued by offline_alert_inbox, hash-bound form preview with one-shot pendant approval, and a browser-harness claim-stream/diff mode that invalidates stale approvals. I also told mac-planner the wrapper is still unresolved despite the underlying route working.

**Biggest unknown:** The production voice/browser integration still lacks a resolved callable browser action wrapper; I can prove POST /execute works, but do not yet know which relay intent should own current-tab reads, watches, or approval nonce handling. The owner still needs to supply any desired authenticated origins and retention/speaking exceptions; defaults remain empty configuration plus existing short-lived claim retention.

