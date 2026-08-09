# Harness derivation — browser-extension — round 218

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Keep an eye on this authenticated page and, if a meaningful change appears, tell me what changed, show me the exact evidence, and let me dismiss or reopen it from the pendant."
- **useful because:** This uses the one reach unique to Safari (existing login) while making the result actionable away from the Mac: semantic diffs rather than noisy reloads, provenance the owner can inspect, and a durable wearable alert when the browser is unattended.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** background change detector uses a cheap local/deterministic extractor; realtime tier only turns the selected diff into speech on demand.
- **latency:** Polling/diffing within 1–5 minutes of a change; under 3 seconds from pendant request to spoken evidence when Safari is online.
- **cost:** Negligible for polling and hashing; roughly one short realtime turn only when the owner asks for the evidence, with extraction preferably local and no page body sent to the model.
- **security:** The watch is explicitly opt-in per URL/session and should default to no persistence of page text. Store only a short changed-claim capsule, URL, timestamp, and selector provenance under existing browser TTL; surface login/session-expired state rather than attempting credential entry. Dismiss/reopen are reversible; never auto-submit page actions.
- **missing:** A semantic region-watch scheduler that can reuse a live authenticated browser session; A diff evidence capsule with selector/heading provenance and a pendant alert action; An owner-configurable per-origin watch policy, shipped empty

### "Before I commit this booking or purchase, check the logged-in page against my calendar and preferences, list every mismatch and hidden cost, and leave the final submit untouched."
- **useful because:** It catches date, timezone, duplicate-event, cancellation, and price mistakes at the last safe point—where browser access to the real session and Mac access to the owner's schedule jointly matter. The owner gets a concrete preflight, not a generic page summary.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → pendant
- **model tier:** deterministic extraction for dates, currency, fees, cancellation terms, and calendar conflicts; a cheaper model summarizes only ambiguous terms; realtime speaks the final checklist.
- **latency:** Under 10 seconds for a normal checkout/booking page, with a visible pending state if a terms section needs further extraction.
- **cost:** Low: structured extraction and calendar lookup are local; at most one short model call for ambiguous legal/fee language.
- **security:** Browser actions are read-only through a strict allow-set and stop before submit. Never persist checkout text or payment details; return only mismatch claims and source selectors. The owner can inspect the exact fields and URL before taking the irreversible action.
- **missing:** A structured browser form/checkout extractor for totals, terms, dates, and selected options; A calendar/preference conflict join that understands timezone and duplicate bookings; A pendant-readable preflight card with an explicit 'submit remains untouched' status

### "Audit the authenticated services I select for recurring charges or renewals, reconcile them with my local receipts and calendar, and give me one dated cancellation/renewal list—without changing any account."
- **useful because:** The browser can see subscription portals behind logins while the Mac can see local receipts and calendar entries; neither view alone reveals forgotten renewals, duplicate services, or a renewal that conflicts with a planned cancellation.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → pendant → dashboard
- **model tier:** background deterministic extraction and entity matching first; a cheap model clusters merchant names and dates; realtime is used only to answer follow-up questions or read the final prioritized list.
- **latency:** Run as a user-started batch in 1–3 minutes for 3–5 explicitly selected origins, with progressive results per origin.
- **cost:** Low-to-moderate: browser navigation and local receipt parsing dominate; one compact model call for ambiguous merchant/renewal matching, not a full-page context resend.
- **security:** Start with an empty explicit origin configuration; user selects origins each run. Read-only browser actions, no cancellation clicks, no payment data persistence. Persist only short-lived claims (merchant, amount, renewal date, URL provenance) under existing browser TTL and let the owner delete the resulting report.
- **missing:** A multi-origin browser batch runner that isolates sessions and reports login failures; Receipt/calendar entity resolution with confidence and duplicate suppression; A browser finding schema specialized for recurring-charge evidence and an auditable delete/export report

### "Save my place in this logged-in application, including the fields I have already reviewed and the exact step I reached, then let me resume it later from the pendant or another Mac without submitting anything."
- **useful because:** Today a dropped browser session or interrupted application forces the owner to rediscover where they were, while ordinary page memory cannot safely reconstruct a multi-step authenticated workflow. A resumable checkpoint preserves progress without taking the irreversible action on the owner’s behalf.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Local extension code captures structured, non-secret form state and step metadata; no model is needed to checkpoint. A cheap model can explain what will be restored; realtime is only for the owner’s resume request.
- **latency:** Checkpoint in under 2 seconds; resume preview in under 5 seconds, with a clear stale-session or changed-page result rather than guessing.
- **cost:** Near-zero model cost for capture/restore; one short model turn only if the owner asks for a spoken explanation of the checkpoint.
- **security:** Ship disabled by default until the owner explicitly enables an origin. Never capture passwords, payment numbers, tokens, or full page text. Encrypt checkpoints locally, bind them to origin and page fingerprint, expire them quickly, and restore only into a preview state. Never click submit or final confirmation.
- **missing:** Extension-side structured form-state capture with secret-field exclusion; Encrypted, expiring checkpoint storage and page/version validation; A resume-preview action that can repopulate fields without crossing a final-submit boundary

### "When a logged-in service changes its terms or privacy policy, show me only the clauses that changed since the last version I approved, explain the practical impact, and keep me from accidentally accepting the new version."
- **useful because:** A normal page reader can summarize today’s document but cannot establish what changed for this particular account. Version-aware, authenticated comparison turns opaque policy updates into a short actionable decision while the browser is still at the acceptance screen.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Local canonicalization and clause hashing identify changed sections; a cheaper background model summarizes only changed clauses; realtime reads the selected impact summary on demand.
- **latency:** Detection during an explicit visit or scheduled check within minutes; comparison and spoken summary within 10 seconds for a normal policy.
- **cost:** Low: hashes and diffs are local; model input is limited to changed clauses rather than whole policies.
- **security:** Owner selects origins explicitly. Store hashes and short clause claims with version/date provenance, not whole policy text. Never click acceptance. Treat inability to verify version identity as an alert, not as approval.
- **missing:** Authenticated policy-version watcher with canonical clause extraction; A durable per-origin approved-version ledger with short-lived source evidence; An acceptance-screen detector that can pause at the decision without mutating the page

### "Check the security pages of the accounts I choose, compare recent sign-ins, recovery methods, and active sessions with my known devices, and tell me exactly what looks unfamiliar without changing anything."
- **useful because:** The browser is the only node that can see account-security panels behind existing logins. Combining those panels with the Mac’s actual device state can reveal a compromised session or stale recovery method before it becomes an incident.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Deterministic extraction and device/session matching first; a background model clusters unfamiliar entries and explains uncertainty; realtime is reserved for an urgent spoken alert or follow-up.
- **latency:** A selected-origin audit completes progressively in 30–90 seconds; urgent anomaly alerts reach the pendant as soon as the first high-confidence mismatch is found.
- **cost:** Low-to-moderate: portal navigation is the main cost, with one compact model call for ambiguous device names or locations.
- **security:** Explicit per-origin selection, read-only browser action set, and no password/recovery-secret persistence. Store only an expiring anomaly claim with timestamp, account-origin, and evidence URL. Never revoke sessions, rotate credentials, or edit recovery settings automatically; show the exact proposed remediation separately.
- **missing:** Origin-specific security-page adapters that recognize sign-in, recovery, and active-session records; A local known-device registry tied to Mac hardware identity and owner-approved aliases; High-confidence anomaly scoring with duplicate suppression and pendant escalation


## Changes it proposed to its own stack

### `browser-harness` — Add a single deterministic browser command `browser_extract_region` that accepts tabId plus a CSS selector or the current selection, returns normalized text, heading, URL, and bounded character count, and expires the result after the requesting job. Keep it read-only and make the command receipt include the selector and timestamp.
- **owner gets:** The owner can ask about the exact paragraph, checkout section, or authenticated dashboard card in front of them instead of exposing an entire private page or manually copying it. It is the missing precision primitive behind contradiction checks and safe preflight audits.
- effort: Medium: extension content-script selection/selector capture, bridge schema, bounded result handling, and tests on Safari pages with shadow DOM and iframes.  ·  risk: Selectors can be stale or capture the wrong region; return a confidence/empty result and never silently widen to the whole page. Recovery is simply retrying with a new selection; no page mutation occurs.
- cost: Negligible runtime/API cost; bounded extraction reduces model context and privacy exposure.  ·  latency: Sub-second for current DOM; up to 2 seconds for an iframe or shadow-root traversal.
- security: Improves least-data handling. Do not persist extracted text; include origin and selector provenance only, and honor the existing empty per-origin policy.
- depends on: A functioning browser command resolver that unambiguously dispatches browser_read_page/browser_snapshot/browser_extract_region; Existing POST /execute browser action path


## What it asked for

_Nothing._
