# Harness derivation — browser-extension — round 115

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser bridge health round 115** — Safari extension is currently offline; only home-chrome is registered in live status, with 11 pending browser commands. browser sessions contain stale tabs from earlier probes but cannot establish liveness.
  - evidence: GET /browser/status returned online:false, devices=[home-chrome offline], pendingCommands:11; GET /browser/sessions returned old default/probe sessions.

## Capabilities it proposed

### "What am I looking at right now? Give me the important parts of this private page, and remember which tab each fact came from."
- **useful because:** The pendant can answer about the authenticated Safari tab the owner is already viewing without making them read or share the screen. It combines browser-only access with realtime voice and leaves an auditable, cited result for follow-up.
- **path:** pendant → browser-extension → relay-realtime → mac-planner → dashboard
- **model tier:** Realtime model for the short spoken answer; cheaper background model for page extraction, normalization, citation packaging, and optional follow-up indexing.
- **latency:** About 2–5 seconds for a concise answer after the owner asks; extraction may continue in the background for a longer brief.
- **cost:** Low per invocation: one realtime turn plus a small extraction call; browser bridge and Mac storage dominate neither API cost nor latency.
- **security:** Page text and URLs behind existing logins leave Safari and transit the authenticated relay path. Return only the active tab's selected/visible content, redact obvious secrets and tokens, and retain source URL/title/DOM snippet hashes rather than raw page text by default. Never click, type, or submit for this read-only request.
- **missing:** A functioning browser command enqueue implementation (all currently granted enqueue wrappers are stubs); A live Safari heartbeat/tab identity and active-tab command; A compact evidence record linking each spoken claim to tabId, URL, timestamp, and source snippet hash; A planner route that turns the browser evidence into a realtime pendant response

### "Save this private page for me—even if the Mac or relay goes offline—and let me ask the pendant about the saved snapshot later, with the answer tied to the exact time and page version I saved."
- **useful because:** The owner can preserve fleeting authenticated context such as a disappearing dashboard, booking page, or message thread without keeping Safari open. Later questions remain grounded in what was actually visible at capture time rather than silently rereading a changed page.
- **path:** browser-extension → pendant → mac-planner → relay-realtime → dashboard
- **model tier:** A cheap background model creates a compact digest and searchable fact index after capture; realtime is used only when the owner asks a later question. Raw snapshot retention and indexing should not consume the expensive conversational tier.
- **latency:** A capture acknowledgement should arrive within 1 second; digest/indexing can complete asynchronously in under a minute. A later spoken answer should target 2–5 seconds when the snapshot is local or cached.
- **cost:** One modest extraction/indexing call per saved page, plus bounded encrypted storage; later questions use small retrieved excerpts rather than resending the entire page.
- **security:** Snapshots may contain highly sensitive logged-in data. Encrypt locally in the extension or Mac keychain before relay upload, retain URL/title/time/version metadata separately, apply a user-selected retention period, and never sync cookies, passwords, or form secrets. Reading a saved snapshot is read-only; sharing or using it to fill a live form must be a separate explicit action.
- **missing:** An extension-side capture command that serializes the visible/selected DOM into a bounded, encrypted snapshot while preserving page version metadata; An offline-capable encrypted snapshot store with retention and deletion controls, including pendant-accessible metadata when the Mac is asleep; A sync protocol that resumes partial uploads after reconnect and deduplicates snapshots by content hash; A retrieval route that distinguishes saved historical snapshots from live authenticated tabs and returns citations to the saved version; A pendant interaction that can address a saved snapshot by recency, page title, or spoken bookmark


## What it asked for

_Nothing._
