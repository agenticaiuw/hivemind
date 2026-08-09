# Harness derivation — mac-terminal — round 160

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser reliability** — The live Mac agent and Safari extension are online, but the retained job history shows browser_read_page has repeated failures: one idempotency key ran 9 times with 6 failures and several other read keys ran 7 times with 7 failures. The current tab is Google and browser status reports 9 tabs, so retries must preserve tab provenance.
  - evidence: GET /ops/snapshot; GET /browser/status; GET /journal

## Capabilities it proposed

### "“I changed something by accident—tell me exactly what the pendant just caused, and put it back if it is safely reversible.”"
- **useful because:** This turns the existing action/undo machinery into a trustworthy everyday recovery path: the owner can use the pendant after an unintended browser navigation, volume change, file move, or app action without reconstructing which job ran. It must distinguish 'reversible and restored' from 'irreversible, here is the evidence' rather than pretending.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime for the short spoken lookup; no expensive planning unless the receipt is ambiguous. Use deterministic receipt/undo metadata first, then a cheap text model only to phrase the result.
- **latency:** Under 2 seconds for the last-job receipt; under 5 seconds for a deterministic undo. If undo is unavailable, speak the reason immediately and offer no fake recovery.
- **cost:** Usually near-zero model cost: GET /jobs/:jobId and receipt metadata plus POST /jobs/:jobId/undo. A fallback explanation is a few hundred text tokens; the dominant cost is not inference but the existing Mac action.
- **security:** The relay must bind the request to the owner's active pendant session and never infer that an irreversible action was undone. Undo requires the exact job/action receipt and should report the pre/post evidence. Sensitive browser URLs/page text should be summarized or redacted before speech.
- **missing:** A pendant intent route that names the most recent completed action and asks for deterministic undo (not a new physical gesture); A relay-to-Mac resolver that joins job receipts to the spoken turn and returns a compact, redacted evidence capsule; A single response contract for undo success, not-reversible, already-undone, and missing-after-retention

### "“Watch this authenticated browser page for a real change, and tell me only when the change is worth my attention.”"
- **useful because:** The owner can delegate a long-running, session-bound observation from the pendant instead of repeatedly reopening a portal. The browser extension holds the authenticated session, the Mac can read the page, and the relay can stay awake while the Mac sleeps or reconnects. The key value is semantic change detection with evidence, not another generic notification.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Background/cheap model for periodic extraction and diff classification; realtime only when the owner asks for status or receives an alert. Never send full page contents to the relay unless needed; compare locally where possible.
- **latency:** Setup confirmation under 5 seconds. Poll cadence configurable from 1 minute to 1 hour. Alert within one poll after a meaningful change; reconnect and resume within 30 seconds.
- **cost:** Low: browser polling and local hashing dominate; use a small model only on changed text or structured fields, typically hundreds of tokens per change. No realtime spend while idle.
- **security:** The authenticated page remains in Safari/browser storage. Persist only a redacted selector, content hash, and extracted fields; do not upload cookies or whole page snapshots. The owner must explicitly name the page and stop the watch; alerts should avoid speaking secrets aloud in public.
- **missing:** A first-class watch definition with selector/field extraction, semantic threshold, cadence, and expiration; Durable relay delivery and deduplication for alerts when the Mac or browser extension briefly disconnects; A browser-side diff/evidence capsule that proves which fields changed without retaining the entire page

### "“While I was away, tell me which things you tried, which actually changed anything, and what still needs my attention.”"
- **useful because:** The owner gets a concise, trustworthy handoff after a burst of unattended work: completed reads, real mutations, failures, and unresolved work separated by evidence. This is more useful than a raw job list because it joins Mac jobs, browser receipts, relay delivery, and the pendant's last-known action beacon into one spoken answer.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use deterministic aggregation of jobs, receipts, journal, routing, and beacon state first; a cheap text model compresses only the resulting facts. Realtime is unnecessary unless the owner asks live.
- **latency:** On-demand answer in under 3 seconds from local stores; relay reconciliation may take up to 10 seconds. Never block the answer on a stale or offline node—label the missing evidence.
- **cost:** Near-zero when aggregating locally; a short summarization call only when there are many heterogeneous events. Storage is bounded by existing 120-job and receipt retention.
- **security:** Speak only redacted action labels and domains, not page contents, command strings, or secrets. Mark actions as 'attempted' versus 'confirmed' when the browser or relay lacks evidence; never infer success from dispatch alone.
- **missing:** A cross-node event join keyed by turn/job/action IDs, including pending offline beacon entries and relay delivery receipts; A deterministic classifier for attempted, confirmed, failed, superseded, and unknown outcomes; A compact spoken-summary route that can be invoked from the pendant without loading the full job history into the realtime model

### "“Read the private page I’m looking at, but only speak it when you can prove the answer is going to my ears—not the room—and otherwise show me a silent confirmation.”"
- **useful because:** The owner can use the pendant for genuinely private authenticated browser work without accidentally broadcasting account balances, messages, or work data. The browser supplies the page, the Mac supplies local audio-route state, the relay coordinates the turn, and the pendant confirms the actual playback path. Today the system can read pages and speak replies, but cannot establish this end-to-end privacy invariant.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime only for the active request and a short confirmation phrase. Deterministic checks handle browser provenance, Mac output route, and pendant playback acknowledgements; no model should decide whether a device is private.
- **latency:** Silent privacy check under 1 second; answer begins within 3 seconds after confirmation. If the route changes mid-answer, pause within one audio frame and mark the response incomplete.
- **cost:** Negligible model overhead. The cost is implementation across the audio bridge, Mac audio inspection, relay session state, and browser evidence capsule; normal page-reading inference remains the dominant API cost.
- **security:** Never send page text to the relay before the local privacy check unless the owner explicitly permits cloud processing. Require a cryptographic session nonce shared by pendant, Mac, and relay; bind the browser evidence capsule to that nonce. Treat speakers, AirPlay, screen recording, unknown Bluetooth outputs, stale heartbeats, and missing acknowledgements as unsafe. Persist only the decision and content hash, not private page text.
- **missing:** A hardware-backed or paired pendant playback acknowledgement that proves which audio route is active; A Mac audio-route attestation that distinguishes private headphones from speakers/AirPlay and reports changes during playback; A relay protocol binding browser evidence, privacy decision, audio stream, and turn nonce end to end; A silent pendant confirmation UX for approve/private, unsafe/silent, and interrupted states


## Changes it proposed to its own stack

### `browser-harness` — Add an evidence-preserving browser read fallback ladder. When browser_read_page fails for a tab, capture the failure class and tab provenance, then retry once with (1) the tab's current document locator, (2) a fresh tab/session heartbeat and same-tab read, and (3) a bounded visible-text extraction. Store each attempt as one receipt chain with the successful/failed evidence capsule, rather than issuing seven identical reads. Stop after the ladder and return the reason plus the last known URL/title.
- **owner gets:** Authenticated pages stop failing mysteriously. A request like “read the page” either succeeds from the live tab or tells the owner exactly why it cannot, instead of silently burning repeated attempts and potentially drifting to a different tab.
- effort: Medium: classify existing extension errors, add same-tab heartbeat/retry state, and link attempt receipts/evidence capsules. No new model required.  ·  risk: A retry could act on a changed page. This is read-only, but the URL/title and content hash must be checked between attempts; if provenance changes, stop and report it. Recovery is simply rerunning the read after the owner confirms the tab.
- cost: Reduces model and extension calls during the current observed failure pattern (browser_read_page had 9 runs and 6 failures, with several repeated failure keys). Adds at most two cheap extension calls on a genuine failure.  ·  latency: Successful reads unchanged. Failed reads take up to two extra bounded attempts, with a hard cap around 8 seconds.
- security: No cookies or page content leave the browser beyond the existing read route. Evidence capsules should retain hashes and redacted excerpts, not duplicate full authenticated page text.
- depends on: browser extension must return a stable error code and tab/document provenance; receipt/evidence capsule linkage must support multiple attempts under one logical request


## What it asked for

_Nothing._
## Its own summary

Recorded a new end-to-end private-browser-answer capability: the pendant should speak authenticated page content only after proving the audio is reaching the owner's intended private route, with silent confirmation and immediate interruption if the route changes. This requires paired pendant playback acknowledgement, Mac audio-route attestation, relay nonce binding, and browser-evidence linkage.

**Biggest unknown:** Whether the existing audio bridge can expose enough playback-route and acknowledgement information to establish that privacy invariant without new hardware.

