# Harness derivation — mac-planner — round 39

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Save my place here.” Later: “Resume the thing I saved.”"
- **useful because:** The owner can leave a complicated browser/Mac task without reconstructing tabs, files, and intent from memory. The system preserves a bounded, reviewable task capsule and resumes from the latest safe point rather than pretending a long-running job is still valid.
- **path:** pendant (voice command and spoken confirmation) → relay (durable encrypted task capsule, expiry, and resume orchestration) → browser extension (capture authenticated tab IDs, URLs, selected page region, and a redacted semantic snapshot) → Mac (capture foreground app, open documents, relevant directory paths, and a resumable action checkpoint; later execute the next step) → dashboard (show capsules, freshness, captured evidence, and delete/rename controls)
- **model tier:** Realtime only for the short voice acknowledgement and disambiguation; a cheaper background model normalizes the intent and extracts a compact checkpoint. No model should infer secrets from a full page when typed browser/Mac metadata suffices.
- **latency:** Acknowledge in under 1 second; capture capsule in under 5 seconds. Resume should first present a 10-second spoken summary and wait for the owner's explicit resume phrase if the checkpoint is stale or would mutate anything.
- **cost:** Roughly $0.002–$0.02 per save/resume depending on summarization; storage and browser/Mac inspection dominate operational complexity, not inference.
- **security:** Authenticated URLs, document names, and page snippets can be sensitive. Default to metadata plus a short redacted excerpt, encrypt at rest, bind browser checkpoints to a session/tab fingerprint, expire capsules after 30 days, and let the owner delete them. Never replay a mutation merely because it was in the checkpoint; re-check page/app state and surface a before/after plan for consequential actions.
- **missing:** A shared task-capsule schema with provenance, sensitivity labels, TTL, and checkpoint status; Browser extension API to export a redacted semantic snapshot and reattach to a tab/session; Read-only Mac context capture for current app/document and open-window metadata (the newly granted inspector covers only part of this); Resume orchestration that can reconcile stale browser tabs/files and convert the checkpoint into a new Mac/browser plan; Pendant phrase handling for save/resume and a dashboard view for capsule review/deletion

### "“Fill this in with my saved details, but don’t show the private values to the AI or speak them aloud.”"
- **useful because:** The owner could use authenticated browser forms and Mac documents without transmitting passwords, payment details, addresses, or identity numbers into model context. Today the system can inspect and act across surfaces, but it lacks a privacy-preserving way to use sensitive values while keeping them confined to the device that holds them.
- **path:** browser extension (detect eligible form fields and perform local, typed-value insertion) → Mac (access an owner-approved local credential/contact/payment vault or selected file without exposing raw values) → relay (coordinate a field-level plan using opaque references and return only success/failure and validation metadata) → pendant (voice request, field summary, and spoken warning if a value would leave the device) → dashboard (show field categories, source device, destination origin, and an audit receipt without revealing values)
- **model tier:** Use a cheaper background model only to classify field labels and resolve non-sensitive intent. Keep raw values out of all model prompts; realtime is needed only for the owner's short voice interaction and clarification.
- **latency:** Under 2 seconds for field classification and roughly 3 seconds for local vault lookup/insertion. Pause for clarification when a field is ambiguous, a domain is untrusted, or the requested category is not pre-authorized.
- **cost:** Approximately $0.001–$0.01 per form, mostly local integration and browser-origin policy checks; model cost is minimal because values never enter inference.
- **security:** A malicious or misidentified form could receive sensitive data. Require exact-origin and field-category allowlists, local OS/vault authorization, one-time scoped grants, visible before/after field-category receipts, no clipboard use, and automatic cancellation on navigation or DOM change. Never fill passwords, payment authorization, or identity documents solely from a vague voice command. Raw values must remain local and be excluded from relay logs, analytics, and screenshots.
- **missing:** A local secret/contact-value broker with typed references and OS-level authorization; Browser-extension field classifier and exact-origin enforcement; A relay protocol for opaque value handles, scoped grants, expiry, and typed success/failure attestations; Mac integration with approved local vaults and files; Dashboard and pendant UX for category-level confirmation and audit without value disclosure


## Changes it proposed to its own stack

### `context` — Add a resumable-task capsule protocol shared by relay, browser extension, and Mac planner. Each capsule stores intent, captured surfaces, provenance (tab/session/app/file), a normalized semantic snapshot hash, next safe step, sensitivity class, TTL, and status (captured/stale/awaiting-owner/completed). On resume, perception re-reads each bound surface, compares hashes, and emits either a refreshed plan or an explicit stale-context report; it must never blindly replay old actions.
- **owner gets:** Saying “save my place” would work across a browser task and desktop work, so the owner can stop at a meeting or shutdown and continue later without losing the exact context or accidentally acting on an outdated page.
- effort: Medium-high: schema and relay persistence, browser snapshot/reattachment, Mac context adapter, stale comparison, dashboard and pendant intents.  ·  risk: Sensitive context could be retained too long, or a false match could resume the wrong tab/file. Mitigate with short default TTL, encrypted storage, surface fingerprints, redacted snapshots, explicit stale status, and immutable audit receipts. Recovery is deleting the capsule or starting a fresh plan.
- cost: Low per capsule storage; approximately $0.002–$0.02 for background normalization/resume planning. Browser and Mac inspection traffic is the main variable cost.  ·  latency: Save acknowledgement under 1 second with capture completing asynchronously; resume adds 1–5 seconds for fresh surface reads before planning.
- security: Introduces a new sensitive durable store, so per-capsule encryption, owner-scoped keys, deletion, TTL, and no raw page/document bodies by default are required.
- depends on: A shared typed context/provenance service (the repeated memory/context backlog items); Authenticated browser session/tab API; Read-only Mac foreground/document context adapter; Relay durable job/capsule storage and pendant intent routing

### `integration` — Introduce a device-local sensitive-value broker shared by the Mac and browser extension. Models and relay receive opaque, single-use field handles such as contact.phone or billing.postal_code; only the local broker resolves a handle after checking the exact browser origin, field semantics, destination, expiry, and owner authorization. Return typed attestations (filled, rejected, ambiguous) rather than values, and erase handles after use.
- **owner gets:** The owner can ask the system to fill routine forms across authenticated sites without handing private data to the AI service, without putting it on the clipboard, and without having to manually retype it every time.
- effort: High: OS/vault adapters, browser-origin and DOM-field enforcement, scoped authorization protocol, audit receipts, and recovery for partially filled forms.  ·  risk: Incorrect field classification could put data in the wrong field or a compromised local app could abuse the broker. Recovery requires immediate handle revocation, clearing the affected form, and an audit trail. Start with low-risk contact fields and test origins before enabling financial or identity categories.
- cost: Negligible per-use API cost; engineering and security review dominate. Local vault integration may require existing password-manager APIs or a small encrypted store.  ·  latency: Adds about 0.5–2 seconds for local authorization and field validation; avoids expensive model calls because values stay outside model context.
- security: Substantially reduces data exposure to relay/model logs, but creates a high-value local broker. It needs OS keychain protection, least-privilege app entitlements, origin pinning, short-lived handles, tamper-evident receipts, and explicit category policy.
- depends on: A local typed-value vault adapter; Browser extension access to form semantics and exact origin; Relay support for opaque handles and non-sensitive attestations; Owner-facing category/origin authorization UI


## What it asked for

### `t12-xerg` (tool) — mac_context_capture
- why: The new resumable-task capsule needs a bounded read-only snapshot of the owner's current desktop context (foreground app, document/window identity, selected text or URL when available) without scraping arbitrary files or using side-effect-capable actions. Existing mac_readonly_inspect does not expose the active document/window semantic identity.

```json
{
  "operation": "current_context",
  "app_scope": "optional application bundle identifier or name; empty means foreground app",
  "include_selection": "boolean, default false",
  "include_window_title": "boolean, default true",
  "redact": "boolean, default true"
}
```

