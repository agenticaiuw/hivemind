# Harness derivation — relay-realtime — round 96

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If I point at a private page and say what I want, coordinate the Mac and browser to inspect it, reconcile findings, and prepare a safe draft action without sending it."
- **useful because:** This turns a vague spoken request into a reliable, evidence-backed preparation across multiple surfaces, while keeping irreversible steps gated for the owner.
- **path:** pendant → relay → mac-bridge → browser
- **model tier:** Realtime for interpreting the request; planner and browser/Mac agents for inspection and drafting; cheaper models for extraction and summarization.
- **latency:** Quick acknowledgment, then asynchronous preparation; results arrive as a reviewable bundle.
- **cost:** Moderate: multiple reads/extractions and reconciliation dominate; should reuse existing sessions and avoid re-sending context.
- **security:** Authenticated pages contain sensitive data; data should stay within the owner’s devices where possible, and drafts must not be sent without explicit approval.
- **missing:** Reliable browser command queue with typed results and session affinity; A durable cross-surface reconciliation mechanism for evidence-backed drafts; Event delivery back to the relay/pendant for completion

### "“What did you do for me while I was away?” followed by “Undo the browser change you made at 3:10,” or “Show me exactly what you sent.” The pendant should answer from a unified, voice-searchable action history across the relay, Mac, and authenticated browser, then perform the requested undo when the underlying operation supports it."
- **useful because:** Today receipts and job status are fragmented by surface and job ID. A worn owner cannot reliably remember whether a spoken request became a Mac action, a browser command, or only a queued plan. This gives them a trustworthy, natural-language audit trail and recovery path without requiring them to be at the Mac or know internal IDs. It is specifically cross-surface: the pendant supplies the conversational reference, the relay correlates it, Mac/browser supply evidence and reversals, and the always-awake relay can explain the result later.
- **path:** pendant → relay → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** Realtime model only resolves the owner's short spoken reference and summarizes already-collected records. A cheaper background model should normalize action names, redact sensitive fields, and build searchable embeddings/indexes; no model should invent a receipt. mac-planner/mac-vision and browser-extension remain executors and must return typed before/after evidence plus an undo operation where available.
- **latency:** Under 500 ms to acknowledge and identify likely matching records; under 2 s for a spoken history summary from the relay's local index. An undo may take seconds and should be announced as in progress, with completion or failure spoken when the receipt arrives.
- **cost:** Realtime cost is one short turn (roughly a few cents or less depending on audio tokens). Background indexing is negligible per event; storage and retention dominate. Do not resend full page contents or screenshots to the realtime model—store hashes, titles, domains, action summaries, and redacted diffs, fetching detailed evidence only when the owner asks.
- **security:** History may reveal private browser titles, file paths, messages, and dictated text. Encrypt records, minimize retention, redact secrets/form values, bind every record to the owner's device/session, and distinguish observed evidence from an executor's claim. Undo must target the exact receipt and be idempotent; if no safe inverse exists, say so rather than approximating. The owner policy allows reversible actions without a confirmation gate, but destructive or irreversible operations should be reported as non-undoable, not silently replayed.
- **missing:** A relay-owned durable provenance ledger joining utterance/session ID, delegated job, Mac receipt, browser command/result, timestamps, and spoken response; A stable cross-surface receipt schema with before/after evidence, inverse action, idempotency key, and explicit undoability; Voice-reference resolution (time, app, domain, and semantic description) over that ledger, with privacy-preserving redaction; Executor adapters in mac-planner/mac-vision and browser-extension that emit evidence and accept an exact inverse receipt; A relay endpoint and pendant intent for history query, receipt explanation, and undo-by-reference, plus dashboard inspection/export and retention controls

### "“Private mode for the next five minutes.” While it is active, the pendant should still execute my request across the Mac and logged-in browser, but retain no raw audio/transcript, avoid screenshots and page-body logging, speak only a minimal result, and then prove what was and was not retained when I say “end private mode.”"
- **useful because:** A wearable is used in public and can hear sensitive ideas, credentials, health details, or work content. Today privacy is an all-or-nothing trust decision: downstream agents may need broad access, but the owner has no per-conversation way to limit durable exposure while still getting useful execution. This creates an explicit, reversible privacy boundary spanning the voice front door, relay logs, Mac actions, browser sessions, and dashboard rather than merely muting the microphone.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime handles the short mode toggle and a terse spoken acknowledgement. Enforcement must be deterministic middleware, not model compliance. Mac/browser executors emit only typed outcomes and cryptographic deletion attestations during the mode; a slower background janitor verifies tombstones and removes temporary blobs after the retention window.
- **latency:** Mode activation and acknowledgement under 300 ms. Requests retain normal execution latency; do not wait for a model-generated privacy explanation. End-mode should return a concise retention report within 1 s, with cleanup continuing asynchronously if needed.
- **cost:** Small per-session metadata and deletion-verification cost; no extra inference beyond the normal request. The major cost is bounded encrypted temporary storage for short-lived screenshots/audio, which should be capped and deleted at session end.
- **security:** The mode must be fail-closed for logging: if a downstream surface cannot honor redaction, do not send sensitive payload there and tell the owner. Never claim deletion without storage-level verification. Preserve only a non-content audit marker (start/end, policy version, success/failure). Browser cookies, passwords, and Mac files remain in their existing stores; this mode controls new relay/agent copies, screenshots, OCR, transcripts, and receipts. The physical button should provide an offline emergency stop that suppresses uplink until the relay confirms the mode.
- **missing:** A signed privacy-policy token propagated from relay to Mac and browser commands, with enforcement outside model prompts; Per-request retention classes and a content-free receipt format for private-mode actions; Temporary encrypted stores with verified deletion for audio, screenshots, OCR, page extracts, and planner prompts; Mac/browser adapters that refuse body capture and redact parameters while honoring typed execution; Pendant firmware support for a local privacy/stop gesture and LED indication, including behavior during LTE loss; A dashboard retention report that exposes only policy outcomes, never the protected content


## Changes it proposed to its own stack

### `relay` — Add a deterministic, signed `privacy_intent` envelope to every relay-dispatched request. The envelope carries mode (normal/private), start and expiry, allowed evidence classes (typed outcome only vs. screenshot/page body/transcript), and a per-request ephemeral key. Relay middleware rejects any response or log write whose class is not allowed, routes private blobs only to a short-lived encrypted store, and returns a content-free deletion receipt after expiry. Propagate the envelope unchanged through mac_delegate/mac_run_actions and browser_run_actions so downstream code cannot silently fall back to normal logging.
- **owner gets:** The owner can use the pendant for sensitive work in public without choosing between exposing a permanent transcript and losing the ability to act. They receive a reliable answer about whether protected material was retained, rather than trusting every model or adapter to remember a privacy instruction.
- effort: Medium: shared envelope types, relay middleware, temporary blob store with deletion verification, and adapter changes on Mac and browser. Add integration tests that intentionally return screenshots/page text in private mode and verify they are rejected and absent from logs.  ·  risk: A buggy classifier or adapter could leak content before middleware sees it; therefore enforce at dispatch and response boundaries, disable private-mode fallbacks, and surface a loud failure. If cleanup verification fails, retain only encrypted data under a short emergency TTL and tell the owner. Recovery is a normal-mode restart after expiry; no protected content is spoken in the failure message.
- cost: Low ongoing API cost; modest encrypted temporary-storage and deletion-check overhead per private request. No extra model call is required.  ·  latency: Approximately tens of milliseconds for envelope validation and response filtering; asynchronous cleanup avoids delaying ordinary replies.
- security: Improves confidentiality by making retention policy machine-enforced and cryptographically scoped. It does not erase data already present in third-party apps or the owner's browser/Mac stores, which must be stated explicitly.
- depends on: A relay-owned request/response envelope shared by Mac and browser adapters; Temporary encrypted blob storage with verified expiry/deletion; Pendant-local privacy gesture and status indication; Typed response/evidence classes from Mac and browser executors


## What it asked for

_Nothing._
## Its own summary

Recorded a new owner-facing capability: a spoken, cross-surface Private Mode that executes useful Mac/browser work while suppressing raw audio, transcripts, screenshots, page bodies, and sensitive receipts, then provides a verified retention report. Also recorded the concrete relay change: signed privacy envelopes and deterministic response/log filtering propagated through Mac and browser adapters. This is not a model prompt or approval gate; it is enforcement between existing surfaces.

**Biggest unknown:** Whether every existing Mac/browser adapter and storage path can be made to honor typed evidence classes and verified deletion; that requires implementation and adversarial integration tests, not more discovery this round.

