# Harness derivation — unified — round 95

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-extension** — Chrome/browser bridge is still offline with no tab context and 9 pending commands; browser actions currently fail or time out. Mac bridge is online. The pipeline has successfully rendered 24 kHz mono PCM (75,734 bytes, no clipping) and relay accepted it, so remaining audio uncertainty is transport/pendant acceptance rather than Mac TTS.
  - evidence: GET /browser/status at 2026-08-07T13:39Z; GET /pipeline returned completed 24,000 Hz mono PCM event; GET /jobs showed browser_navigate failures due to extension offline/timeout.

## Capabilities it proposed

### "“Continue the browser task I started earlier, but only if the page and form are still the same; if anything changed while Chrome was offline, show me the differences on the pendant and let me approve the new plan.”"
- **useful because:** Today a dropped extension leaves pending commands with no safe, owner-friendly recovery. This makes a multi-node task resumable: the relay retains intent, the Mac reattaches the authenticated browser session, the browser supplies fresh evidence, and the pendant reports or requests a compact confirmation instead of silently replaying stale actions.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** background for revalidation/diffing; realtime only for the short spoken explanation and confirmation
- **latency:** Reconnect status within 5 seconds; fresh-page comparison within 20 seconds; no irreversible action until explicit owner confirmation
- **cost:** Usually <$0.01 per resume; dominated by one background reasoning pass over changed fields, with browser/Mac I/O dominating wall time
- **security:** Private authenticated page data remains on the Mac/relay path and must be minimized in diffs. Never replay a send/purchase/delete after reconnect without confirmation. Bind the resume to the original tab/session and expire it after a short TTL.
- **missing:** extension reconnect handshake and stale-command quarantine; typed before/after browser diff result with freshness and confidence; pendant-visible confirmation flow for changed plans; durable task intent/checkpoint record across relay and Mac

### "“When everything reconnects, tell me what happened while I was offline, what was delivered late, what failed, and what still needs me—one short spoken digest with links to the evidence.”"
- **useful because:** Today the pendant, relay, Mac jobs, and browser each retain fragments of an outage, but the owner must reconstruct the story manually. A causal recovery digest would turn those fragments into one trustworthy answer: distinguish delivered, failed, duplicated, and still-pending work, then identify only the decisions the owner must make.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** background model for reconciliation and causal summarization; realtime only to announce the finished digest or answer a follow-up
- **latency:** Generate within 30 seconds of the last surface reconnect; spoken digest under 45 seconds; links/evidence available immediately in the dashboard
- **cost:** Typically <$0.02 per incident, dominated by one background reconciliation pass over receipts and event logs; storage and routing are negligible
- **security:** The digest may mention private browser/account activity. Keep raw page content on the Mac/browser boundary, send only redacted event facts and evidence references to the relay, and require confirmation before retrying any action. Detect and label uncertain or missing telemetry instead of inventing continuity.
- **missing:** A shared outage/connection episode identifier across pendant, relay, Mac, and browser; Event normalization that correlates pipeline events, job receipts, browser command results, late pendant alerts, and reconnect times; Deduplication and causal classification (delivered, failed, superseded, unknown); A durable owner-facing recovery digest with evidence links and a pendant playback queue


## Changes it proposed to its own stack

### `integration` — Add a cross-surface approval-freshness envelope. When the relay or pendant asks the owner to approve a browser/Mac action, include the original intent hash, tab/session id, evidence timestamp, semantic page fingerprint, and a short expiry. The browser result endpoint and Mac executor must reject the approval if the tab, fingerprint, or expiry no longer matches, returning a re-plan request rather than executing. Record the rejected/stale approval in the job receipt.
- **owner gets:** A spoken “yes” will apply only to the exact page and change the owner saw, even if Chrome reconnects, a tab navigates, or a queued job runs later. This prevents the most dangerous failure mode: a correct approval being replayed against a different account page or transaction.
- effort: Medium: shared envelope schema, validation in relay/browser bridge/Mac executor, migration of receipt records, and deterministic tests for reconnect/navigation races.  ·  risk: Existing queued approvals may be rejected and require the owner to approve again; recovery is an explicit re-plan with a fresh preview. Clock skew is handled with server-issued monotonic expiry, not pendant wall-clock time.
- cost: Negligible API cost; a few hundred bytes per action receipt and one inexpensive hash/fingerprint comparison.  ·  latency: Adds under 100 ms locally; revalidation adds normal browser round-trip only when state changed.
- security: Improves replay and confused-deputy resistance. Do not include page secrets in the envelope—only hashes, IDs, timestamps, and redacted evidence references.
- depends on: browser command queue must expose stable tab/session affinity and typed results; Mac job receipts must preserve the evidence reference and approval state; owner-facing pendant confirmation path must distinguish approve, reject, and stale/re-plan

### `model-routing` — Introduce an evidence-threshold response contract for cross-surface work. Before answering completion/status questions, the relay aggregates typed receipts from the Mac, browser, and pendant; the response planner must classify each claim as confirmed, inferred, or unknown and refuse a single definitive success statement when a required surface has no receipt. It should ask one targeted recovery question or offer a safe retry plan, while preserving the underlying evidence links.
- **owner gets:** The owner gets honest answers after flaky connectivity instead of a confident-sounding “done” when the browser never responded or the pendant only received a late partial result. They hear exactly what is known and the one next decision that matters.
- effort: Medium: define claim/evidence types, enforce them in relay response assembly, add missing-receipt and contradictory-receipt tests, and expose concise spoken wording plus detailed dashboard evidence.  ·  risk: Some answers become “unknown” more often during rollout, which may feel less convenient; fallback is a short explanation and a reversible re-check, never an invented success. Existing jobs remain readable because the contract is additive.
- cost: Small background reasoning cost only when claims span multiple surfaces; compact evidence IDs reduce repeated context and API spend.  ·  latency: Adds roughly 0.5–2 seconds for receipt aggregation; skips expensive model calls for simple confirmed statuses.
- security: Reduces accidental disclosure by passing typed/redacted claims rather than raw private page contents. Evidence links remain access-controlled to the owner.
- depends on: typed action receipts from Mac and browser; pendant delivery/acknowledgement events with stable IDs; relay job and pipeline event correlation; a response schema that carries confidence and evidence references


## What it asked for

_Nothing._
## Its own summary

Fresh discovery confirms the Mac bridge is online, but the browser extension remains offline with 9 pending commands and no tab context; browser actions are therefore unsafe/unavailable. I recorded this finding and proposed (1) reconnect-safe browser task resumption with fresh evidence and pendant approval, and (2) a cross-surface approval-freshness envelope that rejects replayed approvals after tab/session/page changes. The 24 kHz Mac TTS path is producing clean 24 kHz mono PCM and the relay accepts it.

**Biggest unknown:** I still need the owner to reconnect/enable the browser bridge (and decide whether the 9 stale commands should be discarded or revalidated). For the audio goal, the remaining missing evidence is end-to-end pendant playback/transport acceptance, not Mac rendering. Accessibility/Screen Recording remain owner-controlled TCC grants and are not required for the safer AppleScript/browser-bridge paths.

