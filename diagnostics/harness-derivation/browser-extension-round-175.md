# Harness derivation — browser-extension — round 175

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-live-state** — Safari extension is online with 9 tabs; active tab is https://x.com/home (tabId 1163292). POST /execute with {actions:[{type:'browser_read_page'}]} successfully returned live page text, evidence capsule, and receipt. Browser work is currently executable through probe_http even though the granted enqueue wrappers are ambiguous/unimplemented.
  - evidence: GET /browser/status returned online=true, tabCount=9; POST /execute browser_read_page returned status success with title Home / X and receipt rcpt_90bf31ae-6ab9-46a6-924b-a947b5db3270.

## Capabilities it proposed

### "“Read the authenticated page I have open, tell me only what requires my attention, and speak the answer through my pendant.”"
- **useful because:** This is the browser tier’s uniquely valuable job: a logged-in page can be understood in the owner’s voice conversation without copying credentials or asking him to switch devices. It turns the pendant into an ambient 'what matters here?' button for portals, dashboards, inboxes, and account pages.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** Use the realtime model only to interpret the owner’s spoken request and deliver a concise spoken result; use a cheaper background model for page extraction, deduplication, and urgency ranking. Browser reads the current Safari tab, relay binds the result to the active voice turn, and Mac-planner supplies local context only when explicitly requested.
- **latency:** 3–6 seconds for text extraction and a short spoken answer; if the page is large, speak an immediate 'I’m reading the current page' acknowledgement and finish within 15 seconds.
- **cost:** Usually one small background extraction call plus a short realtime response; roughly $0.01–$0.05 depending on page size. The dominant cost is sending page text, so extract headings/rows and discard boilerplate before model input.
- **security:** Page text may contain financial, medical, or work secrets. Keep raw text in an in-memory, short-TTL evidence capsule; redact credentials, tokens, and hidden fields; never put page content into long-term memory by default. The owner must explicitly ask before any click, typing, or mutation.
- **missing:** A reliable 'current active Safari tab' browser action (rather than relying on the extension’s last heartbeat tabId); A streaming browser-read result that can be attached to a live pendant turn; An empty, owner-configurable per-origin retention/redaction policy exposed in the UI

### "“Keep watching this logged-in page and alert me on the pendant only when a new decision, deadline, or money-related change appears.”"
- **useful because:** A one-time read answers now; a semantic watch prevents the owner from repeatedly checking authenticated portals. The browser keeps the session, a background relay job compares normalized page states, and the pendant delivers a compact alert even when the Mac is unattended.
- **path:** browser-extension → relay-realtime → mac-planner → pendant
- **model tier:** Run scheduled polling and structural diffing with a cheap background model or deterministic extractor. Escalate to the realtime model only to turn a detected change into a spoken, prioritized alert. The Mac agent owns scheduling and can wake Safari; the relay owns comparison and delivery.
- **latency:** Polling can be every 15–60 minutes, configurable per origin; after a detected change, alert generation under 10 seconds. No need to hold a realtime model open between changes.
- **cost:** Low: most polls should be DOM hash/selector comparisons; one background extraction only on changed regions. Roughly $0.001–$0.02 per poll depending on extracted text volume, plus negligible alert synthesis.
- **security:** Do not store whole pages or screenshots. Persist only origin, selector/region fingerprints, normalized change summaries, and expiration. Ship with no origin rules: the owner explicitly chooses origins and categories (may speak / never speak / never persist). Never click, submit, or expose a changed secret automatically.
- **missing:** A durable authenticated browser-watch scheduler that can poll without an interactive voice session; Per-origin selectors and owner-editable retention/speech policy built on existing browserSessions/httpPolicy/redaction machinery; A device delivery acknowledgement and deduplication key so repeated alerts do not spam the pendant

### "“When I leave my Mac, lock my authenticated browser sessions and hide every private tab; when I return with the pendant, restore only the tabs I approve.”"
- **useful because:** The pendant can act as a physical presence token for the browser’s most sensitive surface. A single spoken command or device event protects logged-in tabs when the owner walks away, while the browser extension preserves a recoverable tab manifest without persisting page contents. No cloud-only agent can reliably know both the owner’s physical presence and Safari’s live sessions.
- **path:** pendant → browser-extension → mac-planner → relay-realtime
- **model tier:** Use deterministic local logic for lock, tab hiding, and session manifest encryption; use the realtime model only to interpret a spoken lock/unlock request and summarize which origins are pending approval. No model should receive page text for this feature.
- **latency:** Lock in under 2 seconds after a pendant event or voice command; unlock/restore within 5 seconds, with explicit per-origin approval spoken or shown on Mac.
- **cost:** Near-zero model cost for automatic events; at most a tiny realtime interpretation call for natural-language commands. Main cost is engineering secure local state and Safari extension APIs.
- **security:** The manifest itself reveals visited origins, so encrypt it locally and expire it. Never transmit cookies, page text, or credentials. Default to lock-only if the relay is unreachable; require proximity/physical pendant presence for restore, and provide a Mac emergency unlock path.
- **missing:** A pendant-to-Mac presence/lock event bridge that works over the currently connected USB serial hardware and later LTE; Safari extension commands to hide/restore tabs and clear sensitive tab previews without closing sessions; Encrypted local tab-manifest storage with per-origin allow/deny restore policy; A visible recovery control if the pendant battery or link fails

### "“Before I accept these terms, privacy settings, or a permission prompt, tell me what is materially new compared with the last version I accepted, and remember my decision.”"
- **useful because:** The owner routinely encounters consequential consent screens that are easy to click past and impossible for the pendant, relay, or Mac alone to interpret in context. The browser can see the authenticated, exact document and the owner’s prior decision history; the relay can explain only material changes in plain speech; the pendant can let the owner defer, accept, or reject without losing the page. This is a decision aid, not an auto-clicker.
- **path:** browser-extension → relay-realtime → pendant → mac-planner
- **model tier:** Use deterministic document extraction, section hashing, and a cheap background model to identify changed clauses. Use the realtime model only for the owner’s follow-up questions and a short spoken explanation. Never have a model click acceptance automatically.
- **latency:** Detect a consent/permission surface within 2 seconds of navigation; produce a material-change briefing in 5–10 seconds. Keep the page available while the owner asks questions, with no timeout that forces a decision.
- **cost:** Typically $0.01–$0.05 per changed-document analysis; hashing and selector detection should avoid model calls when the version is unchanged. Realtime cost is limited to the owner’s questions.
- **security:** Terms can include account, employment, health, or financial context. Keep the source document and extracted diff in encrypted local storage with a configurable expiry; persist only document hash, origin, version/date, decision, and the owner’s chosen scope. Treat acceptance as high-impact: present the exact target, changed clauses, and final action, then require an explicit owner command; never infer consent from conversation.
- **missing:** A browser detector for consent/permission UI and a stable capture of the exact document or dialog text; A local versioned consent ledger with per-origin retention controls and export/delete support; A spoken decision protocol that distinguishes explain, defer, reject, and accept, and hands acceptance to the browser only after an explicit confirmation; A browser result receipt that records the accepted target and document hash

### "“When I’m on an authenticated account page, make me a private, tamper-evident record of exactly what it says now, and later show me what changed or prove what I saw.”"
- **useful because:** Owners lose access to the most important evidence—billing status, account balances, delivery promises, cancellation confirmations, and support messages—when a site changes or a dispute starts. The browser can capture the logged-in source no other node can reach; the Mac can seal it locally; the relay and pendant can later answer questions without pretending an old page is still live.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use deterministic capture, hashing, timestamps, and local encryption as the source of truth. Use a cheap background model only to label sections and compute human-readable diffs; use realtime for a spoken query over the owner’s sealed records.
- **latency:** Capture in under 3 seconds after an explicit owner command; later lookup and diff under 5 seconds. Do not run continuously unless the owner creates a watch.
- **cost:** Near-zero model cost for a text snapshot and cryptographic seal; $0.01–$0.03 for semantic diffing of two captures. Storage is the dominant cost, so default to compressed text plus hashes and let the owner opt into screenshots/PDFs.
- **security:** This is sensitive authenticated content. Store encrypted and locally by default, with per-origin expiry, export, and destruction. The relay receives only a query result or diff, not the archive. Clearly label a capture as owner-requested evidence and include URL, origin, timestamp, hash, and capture limitations; never claim legal admissibility.
- **missing:** An explicit browser capture action that preserves exact text, selected DOM, URL, timestamp, and optional screenshot/PDF as one immutable envelope; A local encrypted evidence vault with hash-chain or signature support and owner-controlled retention; A diff/query service that can answer against sealed captures without uploading the archive; Pendant controls for capture, list recent evidence, and delete


## What it asked for

_Nothing._
## Its own summary

This round established that the real Safari extension is live with nine tabs and that authenticated-page reading works now via POST /execute (browser_read_page), returning evidence capsules and receipts. I recorded three forward capabilities: voice-grounded reading of the current authenticated tab; semantic authenticated-page watches that alert the pendant only on meaningful changes; and a physical pendant privacy shield that locks/restores Safari sessions. The form-filling idea was rejected as an existing duplicate, so I did not restate it. The most useful immediate product is the first one: the owner can ask what matters on the page already open in Safari and hear a concise answer without moving devices.

**Biggest unknown:** The remaining blocker is product policy, not browser reach: the owner must supply the first origins and per-origin rules for what may be read aloud, retained, or watched. Technically, the next missing pieces are a stable current-tab action, durable watch scheduler, pendant-to-Mac presence event, and Safari hide/restore commands; the existing enqueue wrappers are still ambiguous, but direct /execute is working today.

