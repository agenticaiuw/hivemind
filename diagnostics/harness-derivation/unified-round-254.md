# Harness derivation — unified — round 254

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Tell me what’s on the page I’m looking at, but do not send the page’s private contents to the relay.”"
- **useful because:** A logged-in browser tab contains the owner’s sessions and sensitive data that the pendant model should not routinely receive. A local Mac summarizer can answer useful questions while keeping page text, tokens, and form values on the Mac.
- **path:** pendant → relay → mac-bridge → browser
- **model tier:** background/local Mac model for page extraction and summarization; realtime only for the short spoken answer
- **latency:** Snapshot and answer within 4 seconds; fail closed if the browser bridge or local redaction step is unavailable.
- **cost:** ~$0.001–$0.02 per request depending on whether a local model suffices; browser snapshot and local processing dominate.
- **security:** The relay receives only an intent, a redacted structured summary, and a response—not DOM text, screenshots, cookies, URLs with secrets, or form values. Require a visible local indicator and refuse pages marked sensitive or payment/authentication. Keep a per-request receipt proving the redaction boundary.
- **missing:** A browser-side local summarizer/redactor that runs before any relay upload; A sensitivity classifier for auth, payment, health, and private-message pages; A receipt binding the spoken answer to the exact tab snapshot without retaining its contents

### "“Find the thing you created for me about this topic—whether it became a file, note, reminder, email draft, or browser change—and show me the exact result before you make another one.”"
- **useful because:** The system can act across apps, but owners cannot reliably locate the artifact an earlier run produced. This prevents duplicate notes/files/messages and makes cross-surface work feel continuous rather than disappearing into job logs.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background model for semantic indexing and artifact matching; realtime only to clarify an ambiguous match
- **latency:** Return ranked candidates and receipts within 3 seconds locally; never mutate while searching.
- **cost:** ~$0.002–$0.02 per query; local metadata indexing dominates, with model cost only for ambiguous semantic matches.
- **security:** Search only artifacts created or modified by this system and only sources explicitly bound to the request. Show paths/app names and hashes, not private contents by default. Require confirmation before opening, editing, sending, or deduplicating a candidate.
- **missing:** A cross-surface artifact index linking action receipts to resulting files, Notes/Reminders records, drafts, and browser command IDs; Post-action fingerprints (path, record ID, URL pattern, content hash) captured consistently by Mac and browser executors; A deduplication view that distinguishes the same artifact from two legitimately different outputs

### "“Keep anything from banking, health, messages, and passwords on this Mac; you may send only redacted summaries from ordinary pages to the relay.”"
- **useful because:** A single global privacy latch is too coarse for daily use. The owner needs a persistent, inspectable data-boundary policy that lets useful browser assistance continue while sensitive sources never cross the Mac boundary.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic policy engine for allow/deny/redact decisions; background model only to classify an unfamiliar site, never to override policy
- **latency:** Enforce before every browser snapshot/upload with under 50 ms added locally; a new-site classification may wait for owner confirmation rather than blocking unpredictably.
- **cost:** Near-zero per request after policy evaluation; occasional ~$0.001–$0.01 classification for an unrecognized origin.
- **security:** Default deny for credentials, payment, health, private messages, and hidden form values. Policies are signed/versioned, visible on the dashboard, and changes require explicit owner confirmation. Relay receives only fields allowed by the policy, plus a receipt saying what was withheld.
- **missing:** A policy store keyed by origin/app/data class with deny, redact, local-only, and allow outcomes; A mandatory pre-upload enforcement hook in browser and pipeline paths; A test/receipt endpoint proving the payload sent to relay matched the policy decision

### "“Keep researching this overnight, survive the Mac/browser going offline, and tell me only when there is a finished, source-linked result or a real blocker.”"
- **useful because:** Long work currently depends on a live Mac/browser path and can be left processing or silently expire when the machine sleeps. The owner needs a durable handoff: relay-held job, resumable browser checkpoints, deadline, and a concise pendant notification instead of repeated polling.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background model for research and summarization; realtime only for acceptance, blocker explanation, and the final spoken digest
- **latency:** Accept and stage in under 2 seconds; checkpoint every 1–5 minutes; notify on completion, deadline, or blocker without interrupting active speech.
- **cost:** ~$0.05–$0.50 per overnight research job depending on browsing/model calls; browser sessions and repeated failed attempts dominate.
- **security:** Bind the job to explicit domains/tabs and a deadline. Never auto-send or purchase. Persist only source URLs, quoted evidence limits, and checkpoint hashes; require physical approval for any external action. Expire browser credentials and discard stale checkpoints.
- **missing:** A real relay job lease and requeue sweep for crashed Mac workers; A durable browser checkpoint format with idempotent continuation and source bindings; A scheduler/notification path that can deliver completion through the existing inbox without interrupting speech

### "“For the next ten minutes, let you act only in this one tab, only on this site, and let me revoke that access from the pendant immediately.”"
- **useful because:** Today browser commands are bearer-authorized at the agent level, while the owner’s intent is usually narrower than ‘anything my browser can reach.’ A short-lived, tab-bound capability would make logged-in automation safe enough for real use and give the owner a physical revocation path.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic policy and capability-token checks; realtime model only interprets the owner’s spoken scope
- **latency:** Scope issuance and revocation under 500 ms; every browser command must be rejected if its tab, origin, nonce, or expiry no longer matches.
- **cost:** Negligible API cost; engineering effort is in extension enforcement, relay propagation, and audit receipts.
- **security:** Use an opaque nonce bound to extension ID, tab ID, origin, command class, expiry, and monotonic revocation counter. Never treat a URL string alone as identity. Deny navigation outside the bound origin by default, and record rejected attempts without page contents.
- **missing:** A capability-token store and verifier shared by relay and browser extension; Extension enforcement before execution rather than only in the planner; A pendant revocation event that propagates while offline and invalidates the token on reconnect; A receipt showing the exact scope, expiry, and revocation state


## What it asked for

_Nothing._
## Its own summary

Discovered the live surfaces: Safari on MacIntel and the Mac bridge are online; the cloudflare contract-test device is offline. I recorded three new owner-facing capabilities: a local-first browser data firewall, a cross-surface artifact finder tied to receipts, and durable overnight research with checkpointed browser work and relay recovery. The extracted-fact erase idea was correctly rejected as an existing duplicate rather than rephrased.

**Biggest unknown:** The remaining blockers are implementation gaps, not missing owner requirements: a pre-upload browser/pipeline policy hook and proof receipt; artifact fingerprints linking executor results to files/Notes/browser changes; and relay job leases/requeue plus durable browser checkpoints for overnight work. I still need an inventory of the workbench handoff routes and their exact schemas before claiming the overnight path can be wired.

