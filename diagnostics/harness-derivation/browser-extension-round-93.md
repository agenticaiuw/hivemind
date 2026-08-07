# Harness derivation — browser-extension — round 93

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-runtime** — Live browser status is currently offline: only home-chrome is listed, with tabCount null and 9 pending commands; Safari's previously persisted sessions are stale records (default time.is and two probe tabs), not proof of a live tab.
  - evidence: GET /browser/status returned online:false, devices:[home-chrome offline, tabCount:null], pendingCommands:9; GET /browser/sessions returned lastUsedAt values from 2026-08-07T06:26Z and earlier.

## Capabilities it proposed

### "“Compare the information across my logged-in sites and Mac, tell me what conflicts or changed, and prepare the next steps without sending or submitting anything.”"
- **useful because:** This is a genuinely cross-surface task: Safari can read private portals that the Mac APIs cannot, while the Mac can read local Calendar/Mail and create a review artifact. The owner gets one evidence-backed answer instead of manually reconciling tabs and local data.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-terminal → dashboard
- **model tier:** Use the cheaper background model for multi-page extraction, normalization, and conflict detection; use realtime only to clarify the owner's target entities and speak the final concise result. Use the local Mac model for deterministic file/calendar assembly.
- **latency:** A voice acknowledgement in under 2 seconds; background reconciliation in 1–3 minutes depending on authenticated tabs. Never wait on a single browser poll in the realtime turn; report completion through the pendant and dashboard.
- **cost:** Roughly 1 background model call per source batch plus one reconciliation call (dominant cost is DOM extraction/context resend); realtime cost is limited to acknowledgement and final summary. Local Mac actions add no model API cost.
- **security:** Private page text and local calendar facts leave Safari/Mac only to the relay/model for this explicit request. Store source URLs, timestamps, and short evidence hashes rather than raw page bodies by default; redact secrets and tokens. Filling drafts is allowed, but sending/submitting/purchasing remains outside the workflow and must never occur implicitly.
- **missing:** A first-class cross-source entity/field normalizer and conflict report (not merely a page watch); A durable job that can resume when Safari is offline and preserve per-source evidence across browser polls; A review artifact linking each conclusion to its Safari URL/DOM snippet and Mac source, with expiration when either source becomes stale; A working browser command enqueue implementation; the currently granted enqueue tools are schemas/stubs and Safari is presently offline with pending commands

### "“If one of my logged-in sites signs out or asks for verification while you’re working, tell me immediately, pause that site, and continue the parts you safely can.”"
- **useful because:** Browser automation currently risks treating a login page, MFA challenge, CAPTCHA, or expired session as ordinary content. Detecting auth-state transitions lets the owner recover the session without losing a multi-site job, while independent Mac/local work can continue and the pendant can warn them promptly.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Use deterministic browser heuristics and a cheap classifier for auth/MFA/CAPTCHA detection; use realtime only for the short spoken alert and any owner clarification. Do not spend the expensive model on every poll.
- **latency:** Detect on every browser result (sub-second locally), alert within 5 seconds of the extension result, and checkpoint/resume the remaining job asynchronously. No repeated polling while the site is blocked.
- **cost:** Negligible API cost for URL/title/DOM heuristics; occasional small classifier call only for ambiguous pages. Main cost is durable checkpoint storage and one resumed extraction call.
- **security:** Never extract or transmit OTP values, passwords, recovery codes, or CAPTCHA contents. Store only the blocked origin, reason category, timestamp, and the last safe checkpoint. Resuming after re-authentication should require an explicit owner signal (e.g. “continue”), but unrelated reversible local steps may proceed.
- **missing:** A browser result schema with an auth-state classification and safe redacted metadata; Durable per-step checkpoint/skip semantics in the browser job runner; A pendant notification event and dashboard queue item for blocked browser jobs; A tested recovery path when Safari reconnects after offline periods

### "“Use my logged-in websites to answer this, but keep the private page contents on my devices—send only the specific fields needed for the answer, and show me exactly what left each device.”"
- **useful because:** Today the browser can reach sessions that other nodes cannot, but a useful answer may require sending broad page text into a model context. This gives the owner practical data minimization: Safari extracts only an approved schema, the Mac performs joins or calculations locally where possible, and the pendant reports the sources and fields disclosed.
- **path:** pendant → browser-extension → mac-planner → mac-terminal → relay-realtime → dashboard
- **model tier:** Use deterministic local extraction and Mac-side computation first. Use a small background model only to map page labels to the owner's requested fields; use realtime only to explain the disclosure receipt or resolve an ambiguous field.
- **latency:** Preview the disclosure manifest within 2 seconds, extract and compute in under 30 seconds for ordinary pages, and ask no follow-up unless a requested field is ambiguous or unavailable.
- **cost:** Low API cost: most work is browser DOM selection and local computation. A small model call is needed only for semantic field mapping; raw page bodies are not sent, reducing context and token cost.
- **security:** Selectors and field values can themselves be sensitive, so redact values in logs and retain only field names, origin, timestamp, and hashes by default. The owner must be able to inspect the exact outbound field manifest before execution. Never extract passwords, OTPs, recovery codes, or payment secrets. A deliberate override may permit a raw snippet for a single field, with an expiring receipt.
- **missing:** A declarative per-request data-minimization manifest and field allowlist; A Safari-side extraction operation that returns typed fields without returning the full page; A Mac-local computation/merge endpoint that accepts typed browser fields and produces a result; A disclosure receipt visible on the pendant and dashboard, with retention and deletion controls

### "“When you tell me something from a logged-in site, prove that it was observed live just now, identify the exact account and tab it came from, and warn me if the evidence is stale or ambiguous.”"
- **useful because:** The owner cannot currently distinguish a live authenticated observation from a cached session, an old browser result, or a page that silently redirected to login. A compact freshness and provenance proof makes private-browser answers trustworthy without exposing the whole page.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Generate provenance deterministically from the extension result (tab/session, URL, title, observed timestamp, DOM-region hash, redirect/auth state). Use a cheaper model only to summarize the cited evidence; realtime speaks the short verdict.
- **latency:** Attach the proof during the same browser round trip; under 5 seconds for a normal read. Refuse to present a definitive answer when the tab heartbeat or evidence age exceeds the request's freshness bound.
- **cost:** Very low API cost: hashing and timestamp validation are local. Only the final natural-language summary uses a model, with short cited snippets rather than full page context.
- **security:** Do not reveal account identifiers beyond a user-chosen friendly label; hash or redact URLs containing tokens and query parameters. Keep DOM hashes and evidence snippets short-lived and deletable. The proof must attest to observation metadata, not claim that a page's content is truthful.
- **missing:** A typed browser observation receipt with tab/session identity, redirect chain, observation time, freshness deadline, and DOM-region hash; Clock/heartbeat validation between Safari and the Mac agent; A user-visible citation card and pendant speech format for freshness, account label, and ambiguity; A policy that prevents stale observations from being silently reused as current answers


## Changes it proposed to its own stack

### `browser-harness` — Add an auth-boundary event layer between browserBridge results and the durable job runner. For every browser result, run local redaction-safe checks for login/MFA/CAPTCHA/consent pages, emit an auth_blocked event with origin, tab/session, reason, and checkpoint ID, mark only that step blocked, and let the runner continue independent steps. Persist a resumable checkpoint; after Safari reconnects and the owner says continue, replay from the checkpoint rather than rerunning completed mutations or rereading secrets.
- **owner gets:** A long task will no longer silently fail or mistake a sign-in page for the requested data. The owner hears exactly which site needs attention, can sign in themselves, and gets the rest of the work completed without starting over.
- effort: Medium: deterministic URL/title/DOM signatures first, typed result/event schema, checkpoint persistence, resume tests for disconnect and MFA cases, plus pendant/dashboard notification wiring.  ·  risk: False positives could pause a legitimate page; recover by offering 'continue anyway' and recording the override. False negatives are mitigated by requiring expected-page markers before extraction. Never persist page credentials or OTP text.
- cost: Minimal storage and CPU; no model call for common signatures, with an optional low-cost classifier only on ambiguous pages.  ·  latency: Under 100 ms local classification per result; alert delivery under 5 seconds. Resume adds one browser round trip.
- security: Improves security by preventing accidental transmission of auth challenges and by making blocked states explicit. It adds only redacted event metadata and checkpoint IDs.
- depends on: A functioning browser command enqueue implementation (current granted enqueue tools remain stubs); Durable browser job/checkpoint runner (chg-16bc5dee remains open); Pendant/dashboard notification event plumbing

### `integration` — Introduce a privacy-preserving browser observation protocol: Safari returns typed, owner-approved fields plus a signed observation receipt (device/session, tab, origin, timestamp, redirect/auth state, freshness deadline, and region hashes), while raw DOM remains on the Mac. The Mac performs joins and calculations locally and sends the relay only the minimal result and citation metadata. Expired receipts become unusable rather than silently falling back to cached text.
- **owner gets:** They can ask questions about private sites without making entire pages part of model context, while hearing whether each answer is live, which session produced it, and exactly what was disclosed.
- effort: High: extension extraction contract, local field mapper, receipt signing/verification, Mac-local computation service, disclosure UI, and compatibility fallback for pages that cannot expose typed fields.  ·  risk: Some sites will resist stable selectors or change layout; fall back to an explicit ambiguous/unavailable result, never broad extraction by default. Clock skew or an extension restart could invalidate receipts; recover by reacquiring the page and issuing a new receipt.
- cost: Small persistent metadata and hashing overhead; reduced model-token cost because raw pages are withheld. Engineering cost is substantial across extension, Mac bridge, and dashboard.  ·  latency: One extra local validation step, typically tens of milliseconds; complex field mapping may add seconds but avoids transmitting and summarizing full pages.
- security: Strongly reduces sensitive data exposure and makes stale/cross-account evidence detectable. Signing keys must remain in the extension/Mac secure store; receipts should not contain secrets or full URLs with query tokens.
- depends on: A browser extension result schema that supports typed fields and redacted metadata; Mac-local field computation and receipt verification; Owner-facing disclosure and freshness UI/audio; A functioning browser command enqueue path


## What it asked for

_Nothing._
