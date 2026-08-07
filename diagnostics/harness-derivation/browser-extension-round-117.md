# Harness derivation — browser-extension — round 117

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-state** — At 2026-08-07T14:58Z, GET /browser/status reports Safari online but tabUrl empty and tabId 901493 (extension/start-page heartbeat), while POST /execute browser_list_tabs returns an authenticated Gmail tabId 901464 and succeeds. The bridge has a state/reporting inconsistency: heartbeat identity and command enumeration disagree.
  - evidence: GET /browser/status 200: tabCount=1, tabId=901493, tabUrl=""; POST /execute browser_list_tabs 200: tabId=901464, title Inbox (14,987), url https://mail.google.com/mail/u/0/#inbox.

## Capabilities it proposed

### "“Open the site I’m already logged into, find the item I mean, fill out the response, and read me exactly what would be submitted—but don’t send it until I say ‘send.’”"
- **useful because:** This uses the browser’s unique reach into existing authenticated sessions while keeping the owner in control of the one irreversible boundary. It turns a vague spoken request into a concrete, tab-specific draft with field values and a final diff, then can resume without losing context when the owner gives the go-ahead. The pendant supplies intent and confirmation, the relay keeps the workflow alive, Mac-planner coordinates, and Safari performs the authenticated read/write.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Use the realtime tier only to resolve the owner’s spoken target and announce the concise draft; use a cheaper background/local planner for DOM extraction, field mapping, validation, and receipt generation. No model should infer a submit approval from silence.
- **latency:** Read/navigation 2–8 seconds; draft extraction 3–15 seconds depending on page; spoken preview under 5 seconds after extraction. After an explicit ‘send,’ submit and receipt within 2–10 seconds.
- **cost:** Typically 1 realtime turn plus 1–3 cheap planner calls; roughly $0.01–$0.08 per invocation, dominated by page-content tokens and any screenshot fallback.
- **security:** Page contents and proposed field values leave Safari for the local Mac agent/relay; redact passwords, payment credentials, and hidden tokens from model context. Bind every action to the originating tabId, URL/origin, and a short-lived workflow nonce. Never submit based on an old preview, changed URL, or ambiguous speech; require a fresh exact preview and explicit ‘send.’
- **missing:** A production browser enqueue tool rather than the currently granted schema-only wrappers; A tab-bound workflow state storing extracted fields, preview hash, URL/origin, and expiry; A browser action for deterministic form fill plus a separate submit action that validates the preview hash; A compact spoken/readable diff and receipt route shared with the pendant; Redaction of secrets and sensitive form controls before page content reaches the model

### "“Find the page I was looking at yesterday—the one with the red invoice—and bring it back.”"
- **useful because:** Today the owner must remember which site, account, and tab contained something. This capability would let the pendant turn a vague visual or temporal memory into a search across the owner’s own authenticated browsing history, then reopen the best match in Safari. It is different from searching the public web or summarizing currently open tabs: the value is recovering a personally encountered page that no other node can access or identify.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Use a cheap background model to index page titles, URLs, timestamps, visible text, and optional low-resolution visual descriptors locally on the Mac. Use realtime only to resolve the owner’s short spoken description and announce ranked matches. Never send the entire private browsing archive to the realtime model.
- **latency:** Initial indexing runs opportunistically in the background. A retrieval request should return three ranked candidates in 2–6 seconds and reopen the selected page within 2 seconds after the owner chooses it.
- **cost:** Near-zero incremental API cost when indexing locally; one small realtime turn per request, typically under $0.02. Storage and local embedding/index maintenance dominate.
- **security:** The index contains sensitive authenticated page content and browsing history, so encrypt it locally and scope records to the browser profile. Exclude passwords, payment fields, private-message bodies, and pages marked sensitive. Require an explicit spoken choice when multiple accounts or similarly named pages match; never silently navigate to a high-risk site or restore a form with unsent data.
- **missing:** A durable, encrypted, per-profile browsing-memory index with retention controls; An extension event or polling protocol that reports visited-page snapshots and timestamps without capturing secrets; Local multimodal or text retrieval over page appearance and content; A ranked-candidate response channel to the pendant and a browser navigation action bound to the selected result; Owner controls to pause indexing, delete individual records, and set retention duration


## Changes it proposed to its own stack

### `browser-harness` — Implement one canonical browser_command_enqueue tool that submits browser_* actions to POST /execute, waits for the extension result, and returns typed result plus receipt. It must accept deviceId/tabId/sessionId, reject mismatched tab affinity, propagate timeout/error reasons, and expose list_tabs/read_page as read-only operations. Deprecate the five duplicate schema-only enqueue wrappers instead of leaving callers to guess which is live.
- **owner gets:** The owner can actually ask the browser agent to inspect or act in an authenticated Safari tab; today the backend path works, but the agent-facing tools are all stubs, so browser usefulness depends on an accidental direct HTTP probe.
- effort: Small-to-medium: tool adapter, typed schema, result normalization, and integration tests for online/offline, timeout, wrong tab, and receipt propagation.  ·  risk: A duplicate enqueue could replay a queued command or target the wrong login. Use command IDs, idempotency keys, tab/origin binding, and return failures without retrying mutations. Recovery is explicit status plus cancellation via existing browser command deletion.
- cost: Negligible API cost; one local relay round trip per action. Engineering cost is primarily bridge tests.  ·  latency: No additional model latency; approximately 0.1–1 second adapter overhead plus extension polling time.
- security: Improves security by making tab and origin binding mandatory and preventing accidental cross-device dispatch; page content remains sensitive and must be redacted by callers.
- depends on: A stable POST /execute browser action contract; Safari extension polling and POST /browser/result/:commandId, verified online; Typed receipt schema from the existing action receipt implementation

### `integration` — Reconcile browser heartbeat and command-side tab enumeration into one authoritative device snapshot. On each browser action, refresh/compare tabId, windowId, URL, title, and active state; mark the device as ‘online-but-stale’ when heartbeat and list_tabs disagree, and require a fresh list_tabs before any tab-targeted mutation.
- **owner gets:** Prevents an authenticated action from landing in the wrong Safari tab or silently operating on a stale session—especially important when the owner has multiple windows or the extension’s heartbeat is still reporting its bridge/start-page tab.
- effort: Medium: normalize extension heartbeat payloads, add reconciliation in browserBridge/browserSessions, and cover tab-close/navigation races with integration tests.  ·  risk: A stale heartbeat could pause a legitimate task. Recovery is automatic re-enumeration and a clear spoken status; never replay a mutation merely because the tab reappeared.
- cost: One cheap list-tabs bridge call on detected mismatch; no model cost.  ·  latency: Adds roughly 0.5–2 seconds only on mismatch before an action.
- security: Reduces cross-tab/session confusion and limits authenticated content/actions to the verified origin and tab.
- depends on: Safari extension heartbeat endpoint; POST /execute browser_list_tabs; Tab/session affinity and typed result work already present in browserBridge.js/browserSessions.js

### `memory` — Add an encrypted local ‘personal web memory’ service between the Safari extension and Mac planner. On each completed navigation or explicit owner capture, normalize a page fingerprint (origin, title, timestamp, headings, user-visible text hash, and optional locally computed visual embedding), redact sensitive controls, and retain only configurable summaries. Expose semantic/temporal retrieval that returns candidate tab snapshots with provenance, then let the planner request a browser navigation to the selected historical URL.
- **owner gets:** The owner can recover something they personally saw but cannot name precisely, instead of manually hunting through Safari history and authenticated sites. It preserves the unique value of the browser node without turning the relay into a copy of their entire browsing history.
- effort: Medium-to-large: extension event capture, local encrypted storage/index, redaction, retention UI, retrieval endpoint, and tests for multiple profiles and stale URLs.  ·  risk: Indexing could retain sensitive content or expose old authenticated links. Default to explicit capture plus short retention, encrypt at rest, allow immediate deletion, store hashes/metadata where possible, and require an explicit candidate selection before navigation. If an index entry is stale, report it rather than retrying login or restoring form state.
- cost: No routine model API cost if embeddings and retrieval run locally; modest encrypted disk usage, configurable from tens to hundreds of MB.  ·  latency: No impact on normal browsing if capture is asynchronous; retrieval adds roughly 1–4 seconds locally, plus browser navigation time.
- security: Creates a new sensitive store, so it must be profile-scoped, encrypted, excluded from relay logs, and redacted before any model call. Access should be auditable and owner-deletable.
- depends on: Safari extension page lifecycle/snapshot events; A local encrypted index and redaction pipeline; A retrieval route consumable by mac-planner; Browser navigation bound to a verified selected result


## What it asked for

_Nothing._
