# Harness derivation — browser-extension — round 65

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser bridge live state round 65** — Safari extension is currently offline; only home-chrome is registered and offline, with no tab. Browser sessions contain stale tabs and there are 5 pending commands.
  - evidence: GET /browser/status returned online:false, devices=[home-chrome tabCount:null], pendingCommands:5; GET /browser/sessions returned stale sessions last used 2026-08-07T06:26Z.

## Capabilities it proposed

### "Read this logged-in webpage and answer my question, but keep the private page contents on my Mac; send only the minimum redacted facts and citations needed for the answer to the relay and pendant."
- **useful because:** This is the browser's unique value without turning authenticated pages into an accidental cloud data export. The Mac/browser can inspect the owner's private session, extract only the relevant fields, redact names, tokens, account numbers, and unrelated text locally, then the relay can produce a concise spoken answer with a source URL and timestamp. It works across the browser, Mac, always-awake relay, and pendant, while preserving the owner's existing Safari login and materially reducing exposure.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use deterministic local extraction/redaction first; use background gpt-4.1-mini on the Mac for relevance and sensitive-field detection; reserve planner/realtime only for ambiguous questions or the live spoken response. Never upload the raw DOM by default.
- **latency:** 2–5 seconds for a normal page and question; up to 10 seconds when local semantic extraction is needed. The spoken response should begin with a short status while extraction runs.
- **cost:** Usually near-zero model cost for selector/text extraction and deterministic redaction; roughly one small gpt-4.1-mini call (about 2–4k input tokens) for relevance/redaction, plus normal realtime voice cost only if the owner is actively speaking. The dominant cost is raw-page context, which this design intentionally avoids sending.
- **security:** Redaction must happen before any relay or model request, with a deny-by-default classifier for credentials, payment data, health data, private messages, and hidden form values. Keep raw DOM in volatile Mac memory only, do not persist screenshots, and attach URL/DOM-locator/source hash rather than copied secrets. Ask before any navigation that could change state; this capability is read-only.
- **missing:** A functioning Safari extension heartbeat/result path (currently browser status is offline with five pending commands); A local redaction/extraction service with field-level sensitivity labels and a hard raw-DOM egress invariant; A typed relay payload for redacted evidence plus citations and an audit receipt visible on the Mac dashboard

### "Save the important parts of this private webpage to my pendant so I can ask follow-up questions later, even when my Mac and Safari are closed; keep the original link and tell me when the saved copy expires."
- **useful because:** Today a logged-in page is stranded in Safari: once the Mac sleeps or the tab changes, the pendant cannot continue the conversation. This would turn a private browser session into a deliberately scoped, expiring handoff that remains useful while walking or away from the desk, without creating a permanent archive of the whole account.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard-ux
- **model tier:** Use a background model on the Mac to select and compress only the page regions the owner names or that are directly relevant; use deterministic entity/secret scrubbing. Store the compact capsule and embeddings with a cheaper background tier. Use realtime only for the pendant's live follow-up speech; do not resend the whole page on each turn.
- **latency:** 20–60 seconds to create the capsule, with a spoken confirmation and progress update; follow-up answers in under 2 seconds while the capsule is available.
- **cost:** One background extraction/summarization call (roughly 4–8k input tokens depending on selected regions), then small retrieval prompts per follow-up. Storage and audio costs are minor; expiration and deduplication keep ongoing cost bounded.
- **security:** The owner must explicitly name or confirm the page/section to save. Encrypt the capsule at rest and in transit, bind it to the pendant pairing, attach source URL and capture time, and enforce an expiry (for example 24 hours by default). Never save passwords, hidden inputs, payment credentials, private-message bodies, or raw screenshots. Show a dashboard receipt of exactly which headings/quotes left Safari, provide immediate revoke/delete, and make the capsule read-only: no actions against the logged-in site.
- **missing:** A browser-to-relay private capsule API with encryption, expiry, revocation, and pendant-pair binding; A local browser extractor that produces a section-level manifest and refuses secret/hidden fields before upload; A relay retrieval tool usable by the realtime voice agent, with citations back to the original URL and capture timestamp; Pendant storage/UX for listing, expiring, deleting, and switching among saved capsules; A dashboard review receipt showing the exact selected excerpts and expiration


## Changes it proposed to its own stack

### `browser-harness` — Add a local-only evidence firewall between browser results and every model/relay call. Browser commands return typed fields (text span, URL, timestamp, locator, sensitivity label) rather than an unrestricted page blob; a Mac-side redaction pass removes credentials, hidden inputs, payment/health identifiers, and unrelated DOM, then signs a compact evidence packet. The relay and pendant APIs reject packets marked raw or unredacted. Include a visible 'what left this Mac' receipt and a one-click purge of the volatile raw capture. Also add startup reconciliation that marks the current five pending commands abandoned when the bridge is offline, instead of replaying stale actions after reconnect.
- **owner gets:** The owner can safely ask questions about logged-in sites and hear sourced answers without wondering whether an entire private page, password field, or stale browser action was exported or replayed. Offline Safari failures become explicit instead of silently accumulating commands.
- effort: Medium: typed result schema and redaction service in local-agent/browserBridge plus relay schema validation, dashboard receipt, and tests for hidden inputs, tokens, and reconnect races.  ·  risk: A false positive may omit useful context; recover by showing the missing-field reason and letting the owner explicitly request a specific field. A false negative is the main security risk, so enforce deny-by-default patterns and never send raw fallback. Abandoning stale commands could skip an intended read; show them in a recoverable queue and require a fresh request, while irreversible actions remain excluded.
- cost: One small local classifier call only for ambiguous fields; deterministic rules handle most pages. No additional relay model cost for redaction. Minimal local storage because raw captures are volatile and purged.  ·  latency: Adds roughly 50–300 ms deterministic processing, or 1–3 seconds for ambiguous local classification; no network round trip for raw content.
- security: Substantially reduces authenticated-page data exfiltration and prevents stale command replay. The signed evidence packet gives provenance without retaining the page.
- depends on: A functioning Safari extension heartbeat/result path; current GET /browser/status reports offline and five pending commands; A typed browser result contract in local-agent/browserBridge.js; Relay-side schema rejection for raw/unredacted evidence; Dashboard rendering for the egress receipt

### `context` — Add a content-addressed browser evidence cache shared between the Mac and relay: normalize each extracted page section into immutable chunks with URL, capture time, DOM locator, and a sensitivity class; send a chunk only once, then let follow-up pendant turns refer to chunk hashes and request only changed or newly selected sections. Expire private chunks automatically and invalidate them when the browser reports navigation or logout. Keep the cache separate from general memory and never index raw DOM.
- **owner gets:** Follow-up questions about a private page become fast and coherent instead of repeatedly rereading or re-uploading the page. The owner gets lower latency, lower cost, and a clear expiry boundary while still being able to verify every answer against the exact page capture.
- effort: Medium: canonical section hashing and invalidation in the browser harness, a relay chunk store with TTL and per-pair authorization, and a retrieval adapter for realtime and background models.  ·  risk: A stale chunk could produce an outdated answer; every answer must display capture time and source, and navigation/logout invalidates the namespace. Hash collisions or malformed extraction are handled by retaining a short hash plus a source-snippet checksum. If the relay is unavailable, the Mac can answer from its local cache or say it cannot verify freshness.
- cost: Reduces repeated prompt tokens substantially on multi-turn page investigations; adds small D1/R2 metadata and retrieval costs. No raw page persistence; only explicitly selected normalized chunks are retained.  ·  latency: First extraction is unchanged; later follow-ups should save roughly 0.5–2 seconds and thousands of repeated input tokens, with a small hash lookup.
- security: Improves least-privilege sharing by making each transmitted section explicit and revocable, but introduces a remote cache. Enforce per-pair encryption, TTL, deletion, and no-secret chunking before upload.
- depends on: A live browser result path and typed section extraction; Relay support for encrypted TTL chunk storage and hash-addressed retrieval; Realtime-agent support for citing chunk hashes and capture timestamps; Browser navigation/logout events to invalidate cached evidence


## What it asked for

_Nothing._
## Its own summary

Established live browser failure: Safari is offline, home-chrome is offline, sessions are stale, and five commands are pending. Proposed a new cross-surface privacy/evidence firewall (local typed extraction and redaction, relay rejection of raw DOM, provenance receipt) plus reconnect reconciliation that abandons stale commands rather than replaying them. Sent the state to mac-planner.

**Biggest unknown:** The Safari extension's current availability and the owner's first real authenticated workflow remain unknown. I still need a functioning heartbeat/result path and an actual live tab before I can verify private-page extraction end to end; no further context request is useful until the browser comes online.

