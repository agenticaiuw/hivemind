# Harness derivation — faculty-perception — round 132

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac and browser observability** — At 2026-08-08T01:01Z, /ops/snapshot reports Mac agent ready with Accessibility and Screen Recording granted, relay reachable and Mac bridge online, while no pendant appears in the snapshot. Safari extension is online with 9 tabs; active tab is platform.openai.com Billing overview, and capabilities is empty. /browser/status agrees and reports zero pending commands/spooled items.
  - evidence: GET /ops/snapshot and GET /browser/status both returned HTTP 200 with matching browser device, permissions.ready=true, accessibility.trusted=true, screenRecording.granted=true; GET /health reports agent healthy.

## Capabilities it proposed

### "“Before you answer, tell me whether the evidence is fresh and whether you can actually reach the device that would deliver it.”"
- **useful because:** This is the single most useful perception capability: it prevents the system from treating a healthy Mac bridge, a live Safari tab, or relay-accepted work as proof that a pendant received or played anything. It returns a compact verdict with per-source age, contradictions, and an explicit unknown when the pendant is absent, rather than a falsely confident completion sentence.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** background for snapshot assembly; realtime only to phrase the final two-sentence verdict
- **latency:** Under 500 ms when cached; up to 2 s for parallel relay/Mac/browser reads. Never wait for an absent pendant.
- **cost:** Negligible API cost for assembly; at most a short realtime generation when spoken. Dominant cost is none if the structured verdict is rendered directly.
- **security:** Do not expose page titles, URLs, or account state unless the owner asks; active-tab metadata must be privacy-classified and redacted. Treat all completion and delivery claims as untrusted until device-originated playback evidence exists. No mutation or confirmation is needed.
- **missing:** A single authenticated cross-surface read that includes relay device registry, Mac snapshot, browser lease, pipeline/job state, and permission trust with source timestamps; A defined vocabulary separating socket-write, Mac-executed, device-received, and device-played; The nRF9160 is not currently registered, so the pendant branch can only report unknown until hardware connects

### "“When you read something from the web for me, show me the exact source and whether it came from my logged-in Safari or a public relay fetch.”"
- **useful because:** The owner can currently hear an answer whose browser origin is unknowable: relay reads have no ID, hash, or persistence, while private Safari evidence and public Cloudflare reads are different trust boundaries. This capability makes every factual web answer auditable and prevents a public fallback from being mistaken for the owner's authenticated page.
- **path:** relay-realtime → browser-extension → mac-planner → dashboard
- **model tier:** background for hashing and provenance assembly; realtime only for the spoken answer
- **latency:** Add no more than 150 ms to a read; provenance should be generated in the same request, not reconstructed later.
- **cost:** Near-zero model cost; SHA-256 and a bounded redacted capsule are local computation. Storage is bounded by the existing Mac evidence-capsule and browser-provenance caps.
- **security:** Never persist raw credentials, payment fields, or private page bodies outside the existing redaction policy. Public relay results remain explicitly untrusted. A source URL may itself reveal sensitive context, so speak only origin/host by default and require confirmation to reveal full URLs.
- **missing:** Relay read_web_page must return a stable request ID and content hash and report transport/source metadata; The Mac must mint or receive an evidence capsule for relay-service reads, not only in-process relay-module calls; Mount the existing browserProvenance routes so grounded claims can be joined to capsule IDs

### "“Did the payment actually go through, or did one part of the system only think it did?”"
- **useful because:** For consequential tasks, the owner needs a contradiction report rather than a completion word: compare the browser's visible confirmation, the Mac action receipt, the relay job state, and (when available) device delivery evidence, then say exactly which claim conflicts or remains unverified. Today these sources can independently say success while no layer reconciles them.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** background deterministic reconciliation; realtime only when the owner asks aloud
- **latency:** Under 2 seconds using parallel reads; return a structured result even if one surface is offline.
- **cost:** Near-zero model cost for reconciliation; a short realtime phrasing call only on demand. Storage is a bounded receipt index keyed by action/artifact ID.
- **security:** Do not infer financial success from page text alone; mark confirmations as untrusted until the owner-visible source and action receipt agree. Redact account numbers and payment details. Never retry or mutate from this capability.
- **missing:** A common artifact/action correlation ID propagated through browser result, Mac ledger, relay job, and device delivery events; A typed evidence vocabulary for page confirmation versus action execution versus device playback; A read-only reconciler that preserves disagreement instead of choosing the most recent source

### "“Is that fact still true, or is it only the last thing you heard?”"
- **useful because:** The owner needs truth that expires by source, not a timeless memory. A relay job, browser tab, permission state, and device heartbeat each have different freshness limits; today an old successful observation can be repeated as if current. This capability returns the claim, observation time, source-specific expiry, and what would need rechecking.
- **path:** faculty-perception → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** background deterministic freshness evaluation; realtime only to answer a spoken follow-up
- **latency:** Under 200 ms when reading stored observations; re-check only the requested source and return within 2 seconds.
- **cost:** Negligible model/API cost; bounded local metadata indexed by claim and source, with no raw content retention.
- **security:** Store claim hashes and source metadata, not sensitive page text or account values. Never convert an expired claim into a negative claim; say unknown and identify the missing observation. Rechecking a source must remain read-only unless separately authorized.
- **missing:** A source-specific freshness policy for browser, relay, Mac, permissions, and pendant observations; Stable claim IDs/content hashes so a changed page or changed device state cannot overwrite the earlier observation silently; A reader that annotates every spoken factual claim with fresh, stale, or unknown status


## Changes it proposed to its own stack

### `browser-harness` — Add a signed, privacy-minimal browser capability attestation to every extension heartbeat and normalize it in /ops/snapshot. The extension currently reports online, nine tabs, and capabilities:[]; make that field an explicit versioned set (read active tab, inspect DOM, screenshot, click, type, submit), with a nonce, extension build, tab inventory count, and expiry. The Mac agent should reject or downgrade plans whose required capability is absent, and perception should record the exact attestation age rather than infer ability from online=true.
- **owner gets:** The owner stops hearing “I can do that” when Safari is alive but cannot perform the requested operation. It also makes a live browser session understandable: online means connected, not capable, and a capability change becomes a visible fact instead of a silent failure.
- effort: Medium: extension heartbeat schema and signature, Mac normalization/gating, dashboard display, and tests for stale/empty attestations. No new model is required.  ·  risk: An old extension may send no capabilities and appear unusable; recover by treating unknown as read-only and prompting for an extension update, never by assuming full control. A compromised extension could lie, so bind the attestation to the existing device/session nonce and expire it quickly.
- cost: Negligible API cost; a few hundred bytes per heartbeat and a small bounded state record.  ·  latency: No meaningful request latency; one local lookup before browser planning.
- security: Improves least privilege by making capabilities explicit. Do not include URLs, page text, cookies, or form values in the attestation; signatures cover only device/session/build/capability names and expiry.
- depends on: A stable browser extension device nonce; current live nonce is empty, so generate and persist one in the extension; A shared verification key or authenticated bridge channel for heartbeat signatures; A planner contract that declares required browser capabilities before dispatch

### `browser-harness` — Create a local-only sensitivity firewall at the browser-to-relay boundary. On each extension heartbeat and active-tab transition, classify the page origin and visible field roles; when the tab is payment, identity, health, private-message, or credential-sensitive, the Mac planner may use authenticated Safari extraction but must refuse to send page content through the public relay/browser reader. If classification is unknown or stale, default to metadata-only and surface the reason.
- **owner gets:** The owner gets a guarantee that a live logged-in page—such as the currently active billing page—will not silently fall back to a public cloud fetch or leak its contents when the private browser bridge is unavailable.
- effort: Medium: local classifier and policy gate, signed tab-state transitions, planner integration, and a visible reason when a request is downgraded or blocked.  ·  risk: False positives could make harmless pages inconvenient; recover with an explicit one-turn confirmation that permits a redacted excerpt, never unrestricted forwarding. If the extension disappears, fail closed rather than guessing from the URL.
- cost: Small local CPU/storage cost; no additional model call for known domains/field roles. A classifier call may cost a few cents only for unknown pages.  ·  latency: Usually under 50 ms from cached classification; unknown pages may add 300–800 ms for local inspection.
- security: Strongly reduces accidental exfiltration. The classifier must not upload DOM or form values; policy decisions and minimized labels are the only relay-visible data.
- depends on: The extension must expose active-tab transitions and field-role labels without values; The Mac planner must enforce a routing policy before invoking read_web_page or relay research; A user-visible override and audit record must distinguish allowed, redacted, and blocked reads


## What it asked for

_Nothing._
## Its own summary

Established fresh live state: the Mac agent is healthy and fully permissioned (Accessibility and Screen Recording granted), relay is reachable, Safari bridge is online with 9 tabs, and there are zero pending/spooled browser commands. The active Safari tab is platform.openai.com Billing overview, while the extension advertises capabilities:[]; online therefore does not mean able to act. No pendant is present in the live state. I recorded this finding and submitted three non-duplicate proposals: an evidence-freshness/device-reachability verdict (the most useful), auditable provenance for public relay versus private Safari web reads, and signed explicit browser capability attestations. I also informed faculty-judgement.

**Biggest unknown:** The granted read_continuity_snapshot tool still does not resolve in the running inventory; I used direct authenticated /ops/snapshot, /browser/status, /health, and the established /pipeline routes instead. To close the remaining perception gap, the system still needs a real pendant connection/registration and device-originated delivery evidence; for browser provenance it needs the relay-to-Mac capsule transport and a non-empty signed capability attestation.

