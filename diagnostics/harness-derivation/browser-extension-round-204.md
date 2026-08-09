# Harness derivation — browser-extension — round 204

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser live state** — Safari on MacIntel is online with 5 tabs, and POST /execute browser_read_page successfully returned the authenticated GitHub phone-harness page content in this round.
  - evidence: GET /devices discovery reported Safari on MacIntel · 5 tab(s) · online; POST /execute with browser_read_page returned status success and page text.

## Capabilities it proposed

### "“Tell me only when a logged-in website and my local records disagree about something important—like a delivery marked delivered online but missing from my mail or notes—and show me the evidence.”"
- **useful because:** The browser can see authenticated status pages that the Mac and relay cannot, while the Mac can see local mail/files/notes. Joining them catches silent failures instead of merely summarizing one source, and the pendant can surface a short alert while the discrepancy is still actionable. The default should be an empty, owner-configured set of origins and claim types, not invented sites or sensitivity assumptions.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Background/cheap model for scheduled extraction and claim normalization; realtime only when the owner asks a follow-up or an alert needs a concise spoken explanation.
- **latency:** A scheduled check may take 20–60 seconds and should finish in the background; an on-demand comparison should return a finding in under 15 seconds.
- **cost:** Roughly 2–5 cheap model calls per monitored claim plus one short realtime response only on request; browser/network latency dominates, not tokens.
- **security:** Read-only browser actions by default. Persist claims, not page bodies: host-keyed short-lived findings with URL/evidence provenance, and never speak or retain categories the owner later marks forbidden. Never submit forms or send messages. The origin/claim configuration ships empty and must be supplied explicitly by the owner.
- **missing:** A browser-to-local-records comparison job that accepts owner-supplied origin and claim selectors; A scheduler that runs that job and deduplicates previously seen discrepancies; A durable alert payload that carries both evidence links and an expiry to offline_alert_inbox

### "“Build me a decision brief from the authenticated pages I already have open, my local documents, and the public web; quote the exact figures and dates, flag conflicts, and tell me what I still need to verify—without changing anything.”"
- **useful because:** Today each surface can summarize only its own world. This would turn the browser's authenticated access into a cited, cross-source brief: private account facts from Safari, local context from the Mac, and public context from research. The owner gets an answer grounded in sources rather than a confident generic explanation, and can ask the pendant for a two-sentence version while the full evidence remains on the Mac.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Background/cheap model for extraction, normalization, and contradiction checks; use the realtime tier only to answer the owner's follow-up or compress the finished brief for speech.
- **latency:** Start in under 2 seconds, complete in 30–90 seconds depending on pages, then deliver a short alert and a browsable evidence packet.
- **cost:** One extraction call per source plus one synthesis call, typically a few cents; authenticated page loads and OCR/DOM extraction dominate latency.
- **security:** Read-only allowlists for browser actions and an explicit owner-supplied origin configuration. Store only short claims and provenance, never HTML, screenshots, credentials, or full page text. Redact sensitive claims from spoken output according to the owner's empty-until-configured policy. Require no confirmation because no mutation occurs.
- **missing:** A job orchestrator that fans one request out to browser, local files, and public research and joins claims by topic; A citation/evidence packet format that preserves source URL, capture time, and exact quoted span without storing the page; A pendant-friendly completion alert linking to the full brief

### "“What am I looking at right now?” while I’m on a Safari page, then “what matters here?” or “remember this exact claim.”"
- **useful because:** The owner should not have to read a URL or explain which tab is relevant. A pendant button/voice request can capture the active authenticated tab, extract the visible page, answer a focused question, and optionally save only a short claim with its URL and timestamp. This makes the browser an always-available second pair of eyes while preserving the existing no-page-body retention rule; it is different from scheduled monitoring because it is anchored to the tab the owner is looking at now.
- **path:** browser-extension → relay-realtime → mac-planner → pendant
- **model tier:** Realtime for the short answer and spoken follow-up; a cheap background extraction step can prepare a compact page representation if the page is long.
- **latency:** Visible-page capture and a two-sentence answer within 5–10 seconds; saving a claim can complete asynchronously after the answer.
- **cost:** One low-context realtime call per question, usually cents or less; page extraction and extension round-trip dominate.
- **security:** Read-only browser capture unless the owner explicitly asks for a separate mutation. Show the source title/URL in the answer, do not retain raw page text, and save only an owner-requested claim through the existing browser-finding TTL/provenance path. An explicit per-origin configuration remains empty until the owner supplies it.
- **missing:** A reliable active-tab capture/read action exposed to the planner (the current generic browser action can read a page but does not provide a stable active-tab identity to the caller); A pendant request intent that carries the current-tab context and distinguishes answer from save-claim; A short-lived page capsule passed between browser extraction and realtime without persisting raw content

### "“Drive this authenticated website with me watching: narrate each page transition, wait whenever the next step could commit a change, and let me say ‘back’ or ‘stop’ from the pendant.”"
- **useful because:** The owner gets a safe browser operator rather than a blind automation script. It can traverse a complicated logged-in workflow while preserving the human’s situational awareness, and the pendant provides an immediate physical stop path even when the Mac is across the room. This is especially useful for unfamiliar portals where the owner wants assistance, not a fully autonomous click sequence.
- **path:** browser-extension → relay-realtime → mac-planner → pendant
- **model tier:** Realtime for page-state narration, intent interpretation, and low-latency stop/back commands; a cheaper planner can prepare the next read-only action between transitions.
- **latency:** Narration and stop handling under 1 second after each browser result; page transitions may take 2–8 seconds. Never queue the next mutation while the previous page is unresolved.
- **cost:** One small realtime turn per transition plus browser round trips; approximately cents per short workflow, with cost proportional to page count.
- **security:** This is not a new permission gate: the owner already permits maximum access. Instead, make the workflow observable and interruptible. Before any irreversible action, speak the exact target, fields, and submit payload and pause. Keep a replayable action receipt, avoid retaining page bodies, and route the pendant stop signal locally when possible.
- **missing:** A streaming browser-session protocol that returns page transitions and accepts the next action incrementally rather than waiting for one opaque job; A pendant-to-relay interrupt event that cancels an in-flight browser command and leaves the tab in its current state; A browser action journal with checkpoints and an explicit ‘ready to commit’ state; A narration renderer that can summarize only the changed controls between page states

### "“Fill this application from the documents on my Mac, but leave anything ambiguous blank and show me the source document and exact value for every field before I submit.”"
- **useful because:** This turns the browser into a careful document-to-form bridge: it can use private local records without making the owner manually hunt through files, while preventing plausible-looking guesses. Field-level provenance and conflict detection are more useful than a generic autofill because the owner can correct one disputed value without redoing the whole form.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → pendant
- **model tier:** Cheap background extraction for local documents and field matching; realtime only to explain conflicts and read the proposed field list aloud.
- **latency:** Prepare a draft in 20–60 seconds; update individual fields within 3 seconds after correction. Never submit automatically.
- **cost:** One extraction/matching pass plus a small validation call, generally a few cents; document parsing and browser interaction dominate.
- **security:** Keep raw documents on the Mac and send only the minimum candidate value and provenance needed for each field. Do not persist application contents or page text. Show exact submit payload and require the owner's existing explicit commit instruction for the final submission.
- **missing:** A local-document-to-browser-field matcher with confidence and conflict outputs; A browser fill mode that records per-field provenance and supports leaving fields untouched; A compact pendant-readable review and correction protocol; A durable undo/checkpoint for a partially filled form


## Changes it proposed to its own stack

### `browser-harness` — Add a source-integrity witness to every browser finding: record host, canonical URL, capture time, normalized claim hash, and a small structural locator (heading/label path and surrounding character offsets), then provide a read-only recheck job that revisits the page and reports unchanged, changed, or no-longer-found. Keep the current rule of never storing HTML, page text, or screenshots.
- **owner gets:** When the system tells the owner “your account says X,” he can ask whether that exact claim is still true instead of trusting a stale summary. It catches silent edits and expired offers while retaining an auditable pointer to the authenticated source without leaking the page into memory.
- effort: Medium: canonicalization and locator extraction in the browser harness, a recheck endpoint, and result mapping into existing provenance. Test against dynamic pages and localization.  ·  risk: DOM redesigns may yield false “not found”; recover by reporting uncertainty and linking the original URL rather than asserting a change. Never treat a hash mismatch alone as fraud or trigger an external action.
- cost: Small storage increase per finding (well under 1 KB); one cheap background browser visit per recheck. No meaningful model cost.  ·  latency: Initial capture unchanged; recheck adds one browser round trip, typically 2–10 seconds.
- security: Improves integrity without retaining page content. Canonical URLs and locators can still reveal which origin was used, so protect them under existing provenance access and owner-configured origin policy.
- depends on: Existing POST /memory/browser-findings retention path; Existing GET /browser/provenance and POST /browser/provenance/trace; A stable browser extraction result containing title, URL, and bounded text spans

### `memory` — Add an owner-facing browser-memory ledger with two operations: ‘show me every active claim learned from Safari’ and ‘forget this claim/source now.’ The ledger should list host, URL, capture time, expiry, and the downstream brief/alert references, then revoke the selected finding and prevent it from being projected into future prompts. Do not expose or reconstruct the original page text.
- **owner gets:** The owner can see exactly what the system learned from authenticated browsing and erase a mistaken or sensitive claim immediately. Today provenance can explain where browser-derived information came from, but the owner lacks a simple, end-to-end way to revoke one claim and its downstream use from the pendant or Mac.
- effort: Medium: add finding-level identifiers and revocation state to browser memory, a projection filter, a small ledger endpoint/UI, and a pendant-friendly confirmation response.  ·  risk: Revoking a claim could make an existing brief appear incomplete; mark dependent outputs stale and explain why rather than silently deleting their history. Keep an append-only audit of the revocation event without retaining the claim value.
- cost: Negligible storage and model cost; one small lookup per prompt projection.  ·  latency: Under 200 ms for listing or revoking local findings; no impact on normal browser reads.
- security: Improves privacy and user control. The ledger itself must redact values according to the existing browser retention policy and require authenticated owner access.
- depends on: Existing POST /memory/browser-findings; Existing GET /memory/projection; Existing GET /browser/provenance; Existing POST /browser/provenance/trace


## What it asked for

_Nothing._
