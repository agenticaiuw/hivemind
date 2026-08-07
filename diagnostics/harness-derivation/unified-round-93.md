# Harness derivation — unified — round 93

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Check my Gmail (and other private accounts) even when the browser is unavailable, and tell me exactly what you could access; if something needs action, queue it for my review.”"
- **useful because:** The owner repeatedly asks to read Gmail/GitHub/calendar, but the authenticated browser is currently offline with 9 pending commands. This gives a truthful, useful result instead of a generic failure: use an already-authorized native Mac app when possible, fall back to the private browser when it returns, and have the pendant announce queued/completed status without sending or submitting anything.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use deterministic health/routing and AppleScript/native readers first; use a cheaper background model to normalize and prioritize retrieved items; reserve realtime for the owner's spoken request and concise final answer.
- **latency:** A spoken acknowledgement in under 1 second; native Mail/Calendar reads in 3–10 seconds; browser fallback may wait until the extension heartbeat returns. Never imply success before a typed receipt arrives.
- **cost:** Usually <$0.01 per check when native structured reads suffice; roughly $0.02–$0.08 when browser extraction and summarization are needed. Dominant costs are model summarization and audio generation, not routing.
- **security:** Read-only by default. Private account content stays on the Mac/relay path and only a minimized summary plus provenance reaches the pendant. Drafts may be prepared but never sent; sending, deleting, purchases, or form submission require explicit confirmation. Do not expose secrets from captured memory.
- **missing:** A capability-specific fallback policy that maps Gmail/calendar/GitHub intents to authorized native apps or browser tabs; A durable review queue that survives browser/Mac outages and records per-source partial success; A typed result schema distinguishing unavailable, read, stale, and action-required items; A browser heartbeat/reconnect trigger that drains pending commands only after session affinity is re-established

### "“Give me a safe spoken summary of my private screens, but keep sensitive details on the Mac; if I ask for one specific detail, make me deliberately unlock it on the pendant.”"
- **useful because:** Today a private-page answer can move from browser to Mac, relay, and wearable without a single user-visible data boundary. The owner should be able to use hands-free summaries in public while keeping message bodies, financial values, codes, and personal names off the pendant and out of audio unless intentionally unlocked.
- **path:** browser-extension → mac-planner → relay → pendant → dashboard
- **model tier:** Use deterministic on-device/Mac classification and redaction first; use a cheaper background model only for semantic sensitivity classification and summary generation. Realtime handles the short spoken summary and the deliberate unlock exchange, not bulk private-page processing.
- **latency:** Normal redacted summary within 3 seconds. A detail unlock should require a physical long-press plus a spoken confirmation and complete within 2 seconds; otherwise keep the detail local and say it was withheld.
- **cost:** Usually <$0.01 for deterministic redaction and a short summary; <$0.05 when semantic classification is needed. Cost is dominated by summarization, not transport.
- **security:** Raw page content remains on the Mac/browser session; relay receives only the minimum redacted payload and an opaque provenance handle. Sensitive categories need configurable policy and conservative defaults. Unlocks expire after one utterance or 30 seconds, are never persisted, and must not bypass existing confirmation for sending, buying, deleting, or submitting.
- **missing:** A shared sensitivity taxonomy and field-level redaction engine spanning browser DOM, native app output, and generated speech; A relay protocol that carries opaque provenance handles rather than raw private content; A pendant firmware secure-attention gesture and volatile one-detail unlock state; Dashboard controls to preview and audit exactly what crossed each surface; End-to-end tests proving redaction before relay upload and before audio rendering


## Changes it proposed to its own stack

### `integration` — Implement a source-health router and typed partial-result envelope for private-account reads. For each request, inspect /ops/status and /browser/status, choose authorized native Mac automation or browser session, attach source/session freshness and capability (read/draft/send), persist one idempotent review item per source, and emit pipeline events plus a pendant-safe acknowledgement. On reconnect, drain browser commands only with the original session/tab affinity; reconcile duplicates by request ID and never claim a source was read when it was unavailable.
- **owner gets:** “Read Gmail” will stop ending in an opaque failure. The owner will hear “Mail was checked, GitHub is waiting for Chrome to reconnect,” then receive the missing result later—without duplicate actions or false confidence.
- effort: Medium: shared result schema and router, native readers for Mail/Calendar/Notes, browser reconnect/drain worker, review-queue persistence, and receipt tests for offline/online races.  ·  risk: A native app may show a different mailbox or stale cache; label freshness and account identity, and require confirmation for mutations. Reconnect races could duplicate reads or drafts; idempotency keys and session affinity make retries safe. If the router is uncertain, return unavailable rather than guessing.
- cost: Negligible relay storage/compute; background summarization may cost <$0.05 per multi-source check. No new secret is needed beyond existing app/browser sessions.  ·  latency: Immediate acknowledgement; native reads typically seconds. Browser-dependent items become asynchronous and may complete when the extension reconnects.
- security: Improves least privilege by recording read versus mutate capability per source and minimizing payloads sent to relay/pendant. Existing bearer/session protections remain mandatory.
- depends on: A durable typed review-queue/result envelope (not currently exposed as one unified API); Native Mail/Calendar/GitHub read adapters using already-granted AppleScript or app APIs; Browser extension heartbeat and reconnect drain with request IDs; A policy compiler that keeps drafts separate from send/submit actions

### `integration` — Add a mandatory cross-surface data-firewall stage between every Mac/browser result and relay/audio output. It should classify fields, replace sensitive values with typed placeholders plus opaque local provenance handles, enforce per-surface allowlists, and refuse transmission if classification is uncertain. The Mac dashboard can resolve a handle locally after a physical pendant unlock; the relay and pendant never receive the underlying value. Log hashes and policy decisions, not private content.
- **owner gets:** The owner can ask for private-account help while wearing the pendant in public without accidentally hearing or transmitting message bodies, account numbers, access codes, or names. They get useful summaries by default and a deliberate, auditable path to one detail when truly needed.
- effort: Medium-high: define a shared result envelope, implement DOM/native structured-field classification, integrate it before /pipeline/audio and research speech, add volatile handle resolution on Mac, and build adversarial leakage tests for summaries, error messages, and TTS.  ·  risk: Over-redaction could make answers frustrating; show the category withheld and offer local Mac display. Under-classification is the critical failure, so fail closed, use conservative patterns plus semantic checks, and never allow the model to override the firewall. Lost handles simply expire and require rereading locally.
- cost: Small storage and CPU overhead; likely <$0.02 extra per private summary for classification, with no new external service required. No raw private data should be added to relay storage.  ·  latency: Adds roughly 100–500 ms for structured classification and policy checks; semantic fallback may add 1–2 seconds. Audio should not start until the firewall returns a pass.
- security: Substantially reduces accidental disclosure across browser → Mac → relay → pendant and creates an inspectable data-flow boundary. It does not replace account/session security or action confirmation.
- depends on: A shared sensitivity taxonomy and policy compiler; Opaque, expiring provenance handles resolved only on the Mac; A pendant secure-attention gesture and volatile unlock state; Integration hooks before relay result upload and TTS rendering


## What it asked for

_Nothing._
## Its own summary

Fresh inspection found no new orchestrator grants. The Mac bridge is online, but the browser extension is offline with 9 pending commands; /ops/status confirms Accessibility and Screen Recording remain unavailable while native automation grants are present. The active pipeline already renders 24 kHz mono PCM successfully, but the pendant prototype still captures at 15,625 Hz and spends about 87% of one core on simultaneous Opus encode/decode. I recorded a new cross-surface capability and integration change: health-aware private-account reads that truthfully combine native Mac readers, reconnecting browser sessions, durable partial results, pendant acknowledgements, and review-only follow-up. A proposed hardware change was correctly recognized as already covered by the existing audio backlog and not duplicated.

**Biggest unknown:** The implementation contracts still missing are the unified typed partial-result/review queue and the source-specific native readers (Mail/Calendar/GitHub). I also still need authoritative 24 kHz acceptance thresholds, production pendant constraints, and the owner's phone-companion/privacy boundary; those context requests are already pending and should not be re-requested. Operationally, the next observable blocker is restoring the browser extension heartbeat so the 9 queued commands can be classified or safely drained.

