# Harness derivation — faculty-action — round 91

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say 'check Gmail, GitHub, or my calendar' from the pendant, capture it even if my Mac or browser is offline, then resume automatically when they reconnect and give me a sourced spoken result; never send, edit, or delete anything without my confirmation."
- **useful because:** The owner's recent attempts to read these accounts failed outright. This turns a transient disconnected bridge into a trustworthy asynchronous handoff: the pendant can accept the request now, the relay preserves it, and the authenticated browser on the Mac completes it later without moving credentials to the relay.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-action
- **model tier:** Use the realtime tier only to acknowledge and clarify the short spoken request; use a cheaper background model for queued account reads, evidence reconciliation, and concise briefing generation.
- **latency:** Acknowledge in under 1 second offline; resume within 30 seconds of Mac/browser heartbeat; deliver a 1–3 sentence spoken result within 2 minutes of reconnection, with explicit queued/running/completed status.
- **cost:** Roughly $0.01–$0.05 per queued check depending on page count and extraction; dominant costs are authenticated page extraction and speech synthesis, not the short acknowledgement.
- **security:** Keep cookies and page contents on the browser/Mac; relay stores only an encrypted intent, bounded account targets, and status. Redact secrets from receipts and logs. Reads are allowed by owner policy, but any send/edit/delete/purchase must become a separate confirmation checkpoint on the pendant and Mac. Expire unstarted intents and provide cancellation.
- **missing:** A durable offline intent spool with idempotency keys, TTL, and reconnect replay; A device-visible queued/running/completed/failure state and cancellation action; A resumable authenticated-read workflow that can reattach to the intended browser session and return citations; A compact spoken-result/audio delivery path from completed background jobs to the pendant

### "When I say “get this ready for me,” let the pendant capture the request, have the Mac and my open browser determine the relevant document, messages, calendar constraints, and files, then assemble a private ready-to-review packet on the Mac and announce exactly what is missing—without sending, submitting, or changing anything."
- **useful because:** Today the mind can inspect or act on individual surfaces, but it cannot turn an underspecified real-world request into one coherent, evidence-linked preparation packet spanning the owner's open browser, Mac files, and calendar. This would make the system useful at the moment of intent rather than requiring the owner to name every app and step.
- **path:** pendant → relay-realtime → faculty-perception → faculty-judgement → faculty-action → mac-planner → mac-vision → browser-extension
- **model tier:** Use the realtime model only to capture the short request and ask one clarification if genuinely necessary. Use a cheaper background model to gather, normalize, and assemble the packet; reserve the expensive tier for resolving conflicts or ambiguity.
- **latency:** Acknowledge immediately; produce an initial packet in 1–3 minutes and continue gathering for up to 10 minutes, with a spoken progress update if the owner leaves the conversation.
- **cost:** Approximately $0.03–$0.15 per preparation, dominated by multi-page authenticated extraction, local file inspection, and optional audio rendering; most orchestration should use the background tier.
- **security:** Keep private page contents and files on the Mac where possible. Every packet item needs source, timestamp, and access scope. Do not cross account boundaries or infer recipients. The output is draft-only: sending, submitting, deleting, purchasing, or editing requires a separate explicit approval. Expire packets and provide deletion.
- **missing:** A cross-surface preparation workspace that can merge browser evidence, local files, and calendar facts into one provenance-linked packet; A goal-to-artifact contract distinguishing gather, draft, and mutate operations; Conflict and ambiguity reporting that stops at missing information instead of guessing; A Mac-side review surface with per-item source links, freshness, and a clear final approval boundary


## Changes it proposed to its own stack

### `integration` — Add a durable cross-surface Intent Handoff protocol between pendant/relay and Mac/browser jobs. On voice capture, create an intent envelope {idempotencyKey, normalized goal, allowed read scopes, confirmation policy, createdAt, expiry}; persist only encrypted metadata in relay. When /browser/status reports the bridge online, claim the envelope exactly once, create or resume a /jobs task bound to the browser session, and stream state transitions queued→claimed→extracting→waiting-for-confirmation→completed/failed. Attach source URL/tab/timestamp/snippet hashes to the receipt, synthesize a short audio result, and let the pendant cancel or replay by intent ID. Do not auto-resubmit after ambiguous failures.
- **owner gets:** Their spoken 'read Gmail/GitHub/calendar' requests currently disappear as failures when the browser is offline. They would instead get an immediate queued acknowledgement and a reliable, cited answer later, without granting the relay access to account cookies or allowing accidental outbound actions.
- effort: Medium: relay envelope store and state machine, Mac bridge reconnect claimant, browser-session binding, receipt/audio callback, and pendant status/cancel UI; integration tests for duplicate delivery, expiry, reconnect, and confirmation boundaries.  ·  risk: A stale intent could run against changed page state or the wrong tab. Mitigate with session/account binding, short TTL, read-only scope, evidence snapshots, explicit re-authorization after long offline periods, and idempotency. Recover by canceling the intent and exposing the full receipt; never infer success from a lost callback.
- cost: Small durable-storage and queue cost; approximately $0.01–$0.05 per completed read plus speech synthesis, with background-tier model usage. No credential replication to relay.  ·  latency: Sub-second local acknowledgement; completion depends on bridge reconnection, then typically 30–120 seconds for three account reads.
- security: Improves containment by keeping cookies/page bodies on Mac/browser. Encrypt intent metadata, minimize retention, redact logs, bind jobs to account/session IDs, and require pendant confirmation for any mutation.
- depends on: Owner must keep the Mac bridge and relevant browser extension online/authorized when work should resume.; Use existing job receipts and browser command idempotency rather than inventing a second action ledger.; Existing offline_intent_spool request remains unfulfilled; implement this as the relay/Mac integration rather than re-requesting the unavailable skill.

### `integration` — Add a cross-surface temporal snapshot protocol. At the instant a spoken goal is accepted, the relay issues a snapshot nonce; the Mac agent records a manifest of relevant local files/apps, the browser bridge records tab URLs and bounded extraction hashes, and the perception layer records the pendant request plus timestamps. Judgement and action may reference only that nonce. The Mac review surface renders a replayable evidence bundle showing what was observed, what changed during preparation, and which facts are now stale; any mutation must revalidate the affected item immediately before execution.
- **owner gets:** The owner would be able to trust a preparation or recommendation even when pages, messages, or files change while the system works. They could see exactly what the mind saw, catch stale or mis-scoped evidence, and approve a result without wondering whether the action is based on an earlier tab state.
- effort: Medium-to-high: define a signed manifest format, capture bounded cross-surface evidence without copying secrets to the relay, persist bundles on the Mac, add freshness/revalidation checks to execution, and build a human-readable replay view.  ·  risk: Snapshots can contain sensitive content and may be mistaken for current truth. Encrypt and retain them briefly, store content locally with hashes in relay metadata, label every item with capture time and freshness, and force revalidation before any write. If capture is incomplete, the system must return an incomplete bundle rather than silently continue.
- cost: Small relay metadata cost; local disk usage scales with bounded evidence bundles. Background extraction is cheaper than repeatedly invoking the realtime tier; replay adds negligible API cost.  ·  latency: Adds roughly 1–5 seconds to initial capture and a few seconds for pre-action revalidation; avoids expensive rework and unsafe retries.
- security: Improves auditability but creates a sensitive local artifact. Encrypt at rest, redact secrets from manifests, enforce per-session access, short retention, and owner deletion. Never place raw authenticated page contents in model prompts unless required.
- depends on: A shared typed evidence/manifest schema across perception, browser bridge, Mac agent, and action receipts.; A Mac-side review/replay surface and local encrypted evidence store.; Execution must accept and verify a snapshot nonce and perform last-mile revalidation before writes.


## What it asked for

_Nothing._
## Its own summary

Discovered and verified the current execution blocker: Mac bridge is online, browser bridge is offline with 9 pending commands, and recent browser jobs time out. Proposed and recorded a novel cross-surface offline intent handoff capability plus the integration change needed to connect existing jobs, browser sessions, receipts, and audio delivery. Reported the remaining owner, implementation, hardware, and policy requirements.

**Biggest unknown:** Whether the owner will enable the Browser Bridge and when a physical pendant will reconnect; without those, the queued handoff cannot be validated end to end.

