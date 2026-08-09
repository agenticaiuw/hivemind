# Harness derivation — faculty-perception — round 133

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac permissions** — At 2026-08-08T01:04:17Z, AI Pendant Agent has Accessibility and Screen Recording trusted, inputReachability verified, and all required permissions ready; vision upload consent remains false.
  - evidence: GET /ops/snapshot and GET /observe both returned trusted:true, screenRecording:true, inputReachability.status=verified, permissions.ready=true, visionUploadConsented=false.
- **live cross-surface presence** — At 2026-08-08T01:04Z, home-macbook-bridge and Safari browser extension are online; no nRF9160 pendant appears in the live device table, and the only other registered device is offline cloudflare-contract-test.
  - evidence: discover:devices plus GET /ops/snapshot browser.online=true and relay payload macBridgeOnline=true; prior granted live pendant observability states no pendant has ever registered.
- **current browser context** — Safari extension is online with 9 tabs; active reported tab is platform.openai.com Billing overview, tabId 1148327. This is sensitive account context and should not be echoed or persisted casually.
  - evidence: GET /ops/snapshot and GET /browser/status returned tabUrl=https://platform.openai.com, tabTitle=Billing overview - OpenAI API, tabCount=9, online=true.

## Capabilities it proposed

### "If my pendant is unavailable, keep the conversation alive on my Mac and browser, then resume it on the pendant when it returns—without losing what was said or pretending I heard anything."
- **useful because:** The pendant is currently absent while the Mac bridge and Safari extension are live. Today a dropped wearable silently splits the conversation. This makes the system useful now at the desk and preserves a truthful handoff for later: Mac/browser delivery is distinct from pendant playback.
- **path:** relay-realtime → relay → mac-planner → browser-extension → unified → faculty-perception → faculty-action
- **model tier:** Use realtime only for the active voice turn; use a cheap background model to summarize and reconcile queued handoffs.
- **latency:** Detect device absence within 2 seconds; show or speak a Mac fallback within 3 seconds; reconcile on pendant reconnect within 10 seconds.
- **cost:** Low: one short background summarization per interrupted turn (roughly $0.001–$0.01 depending on model); browser and relay state dominate engineering, not inference.
- **security:** Mac/browser output may expose the same private answer in a visible or audible channel; require the existing browser/session trust and let the owner choose 'Mac fallback allowed'. Persist only encrypted, bounded turn summaries, never raw microphone audio by default. Never label Mac delivery as pendant-heard.
- **missing:** A relay-owned handoff record with per-surface delivery states and an idempotency key; A Mac/browser fallback renderer that can show a pending answer without claiming playback; A pendant reconnect consumer that sends the handoff key and a real device playback event (the accepted audio_delivery_ack_queue is needed for the final heard state)

### "While I was away, tell me only the external things that actually changed—new mail, calendar moves, browser-account changes, or Mac files—and show why you believe each one, not a guessed summary."
- **useful because:** Current continuity is mostly job/run history and cannot establish external-world change. A perception-first diff would compare authenticated browser pages and Mac app records at two observations, preserve source/time/hash evidence, and separate 'changed' from 'not checked' and 'could not access'. That is far more useful than a generic catch-up digest.
- **path:** relay → mac-planner → browser-extension → mac-vision → mac-terminal → faculty-perception → unified → relay-realtime
- **model tier:** Background/scheduled cheap model for candidate extraction and deduplication; realtime only to answer the owner's spoken query over the prepared evidence.
- **latency:** Scheduled observation under 30 seconds per watched source; spoken report under 2 seconds after the owner asks; no polling faster than the owner's configured cadence.
- **cost:** Moderate: browser reads and Mac app queries dominate; use hashes and structured fields so unchanged sources cost almost no model tokens. One concise report is roughly $0.005–$0.03.
- **security:** This touches highly sensitive authenticated pages, mail, calendars, and files. Default to metadata/diffs, redact secrets and message bodies, require per-source watch consent, encrypt local snapshots, and never upload raw page content to the relay unless explicitly requested. Changes must carry source URL/app, observedAt, content hash, and an access/error status.
- **missing:** A durable observation baseline/diff store with per-source consent and expiry; A scheduler that can invoke browser and AppleScript read-only probes and record inaccessible sources honestly; A unified typed change schema consumed by the wearable and Mac report

### "Remember exactly what I am looking at when I say 'save this', and later bring me back to that browser tab or screen region with the original evidence and my spoken note."
- **useful because:** A voice note alone loses the visual referent. With screen recording now verified and Safari extension online, the system can bind a spoken note to a content-addressed page/region, reopen the right tab, and tell the owner if the page changed or the evidence expired. This creates durable spatial memory across the wearable, browser, Mac, and relay.
- **path:** relay-realtime → browser-extension → mac-vision → mac-planner → faculty-perception → faculty-action → unified
- **model tier:** Realtime extracts the short utterance and intent; a cheap background model labels the region and summarizes only when needed. No expensive model for unchanged recalls.
- **latency:** Capture confirmation under 1.5 seconds; return-to-context under 5 seconds; changed-page comparison under 2 seconds from cached hashes.
- **cost:** Low-to-moderate: mostly local screenshot/DOM capture and storage; occasional small vision call ($0.005–$0.04) only for region labeling or ambiguous references.
- **security:** Screens may contain passwords and financial data. Redact sensitive regions before relay storage, keep full evidence local, require explicit 'save' (never passive capture), show source/time/expiry on recall, and refuse to act on stale or revoked evidence.
- **missing:** A single voice-triggered capture transaction joining audio turn, active tab/screenshot, region locator, and durable capsule; A Mac route that reopens/focuses the tab and visibly indicates stale or changed evidence; A pendant-friendly recall summary and expiry/revocation behavior across relay reconnects

### "Before anything leaves my Mac or browser, tell me exactly what private data would cross into the relay or model, and let me approve, redact, or keep it local with one spoken command."
- **useful because:** The owner currently has trust and automation, but no end-to-end view of what a browser read, screenshot, audio turn, or Mac action exports. This gives them a usable privacy boundary across the wearable, Mac, browser, and relay rather than forcing them to trust hidden prompts and tool plumbing.
- **path:** relay-realtime → relay → mac-planner → mac-vision → browser-extension → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** A local deterministic classifier handles known secrets and destinations; a cheap background model labels ambiguous content. Realtime only speaks the short consent summary.
- **latency:** Under 500 ms for known-secret detection; under 2 seconds for a spoken redaction/approval preview; action waits for explicit confirmation only when policy requires it.
- **cost:** Low to moderate: local classification is nearly free; ambiguous snippets may cost $0.001–$0.01. The dominant cost is engineering a single enforcement point, not inference.
- **security:** The inspector itself must never upload the data it is inspecting. Keep raw content local, send only destination, categories, byte counts, and redacted previews; make deny the default for unknown destinations; log consent decisions without storing secrets.
- **missing:** A preflight interceptor shared by Mac actions, browser reads, relay tool calls, audio uploads, and evidence capture; A typed redaction manifest with destination, sensitivity class, byte range, and expiry; A pendant/Mac consent protocol that binds approval to one immutable request hash and expires it after one action

### "Forget this everywhere: remove the recording, transcript, browser evidence, relay copy, Mac receipt, and spoken summary, then give me a signed report of what was deleted and what could not be reached."
- **useful because:** Today revocation is fragmented: a local evidence tombstone is not proof that relay audio, announcements, pipeline traces, browser spool entries, or Mac receipts are gone. The owner needs a single privacy action with honest per-store results, especially when a device or relay is offline.
- **path:** relay-realtime → relay → mac-planner → mac-terminal → browser-extension → unified → faculty-perception → faculty-action
- **model tier:** Cheap background orchestration and deterministic deletion; realtime only confirms the bounded deletion report. No model should inspect or summarize content during deletion.
- **latency:** Start immediately; report local deletion in under 2 seconds and remote acknowledgements or explicit timeouts within 10 seconds. Never claim completion while a store is unreachable.
- **cost:** Low API cost; mostly authenticated deletes and receipt storage. A retry after relay recovery is the dominant operational cost.
- **security:** Deletion authorization must be stronger than ordinary tool use, bound to a user-visible object set and request hash. Keep only minimal tombstone IDs and deletion receipts; never retain deleted content as a backup. Remote stores need authenticated, idempotent erasure and timeout states.
- **missing:** A cross-store deletion coordinator with an inventory of every copy and explicit unreachable/retention-blocked outcomes; Authenticated idempotent delete routes on relay, Mac pipeline/audio/jobs/announcements, browser spool, and evidence stores; A durable privacy receipt plus retry-on-reconnect queue that contains identifiers but no content

### "I lost my pendant—lock that device immediately, revoke its relay access, preserve my Mac and browser sessions, and tell me exactly what remains exposed and how to recover it."
- **useful because:** A wearable is a bearer of private conversations and may be physically lost. Current device presence, pairing, relay credentials, browser sessions, and Mac trust are separate; the owner cannot perform a precise lost-device response or distinguish a stale registry row from a live compromise.
- **path:** relay → relay-realtime → mac-planner → browser-extension → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Deterministic security workflow; realtime only narrates the short result. Use a cheap background model only to explain unfamiliar active sessions, never to decide revocation.
- **latency:** Revoke and disable pending delivery within 2 seconds; enumerate Mac/browser/relay exposure within 5 seconds; recovery pairing can take minutes but must be resumable.
- **cost:** Very low model cost; one authenticated relay mutation plus local session inventory. Recovery support is the engineering cost.
- **security:** Require a second factor or physical Mac confirmation, not a voice-only revocation phrase. Do not reveal credential material. Invalidate WebSocket sessions and queued audio, preserve an audit receipt, and ensure revoking the pendant cannot revoke the trusted Mac bridge or browser extension.
- **missing:** A device lifecycle state machine with lost/blocked/recovered states and immediate WebSocket/session termination; Credential rotation and queued-audio cancellation routes that are device-scoped, not admin-wide; A recovery ceremony that pairs a replacement pendant and rebinds only approved memories and routines


## What it asked for

_Nothing._
## Its own summary

Fresh reality: the Mac agent is now fully observable and actionable with Accessibility, Screen Recording, verified input reachability, and permissions.ready=true. Safari's browser extension is online with 9 tabs; relay and Mac bridge are online. There is still no registered nRF9160 pendant, so nothing may be described as pendant-heard. I recorded these facts and proposed three owner-facing capabilities: truthful Mac/browser fallback handoff while the pendant is absent; evidence-backed external-change detection while away; and voice-bound visual memory that can reopen a saved browser context and detect staleness.

**Biggest unknown:** The continuity tool granted in the prompt does not resolve in the live resolver (nearest routes are /ops/snapshot and /pipeline); direct probes work. I still need a real unified handoff/evidence transaction contract: per-turn IDs, per-surface delivery states, consent/redaction policy, and a device-originated playback event when a pendant eventually registers. No more TCC permission work is needed.

