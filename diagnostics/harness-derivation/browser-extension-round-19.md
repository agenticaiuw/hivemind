# Harness derivation — browser-extension — round 19

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser bridge availability** — GET /browser/status currently returns online:false, devices:[], pendingCommands:1; the granted browser command enqueue tool is still an unimplemented stub, so I cannot inspect or act in Safari this round.
  - evidence: Live GET /browser/status response and browser_command_enqueue error: tool granted schema but no implementation.

## Capabilities it proposed

### "Find upcoming renewals, deadlines, and commitments across my logged-in services, explain which ones matter, and prepare the changes or cancellation forms without submitting anything."
- **useful because:** Important obligations are scattered across insurer, utilities, subscriptions, travel, school, and vendor portals. The owner gets one prioritized list with source evidence and ready-to-review next steps instead of missing a renewal or manually checking every account.
- **path:** browser → relay → dashboard
- **model tier:** Background/scheduled work should use a cheaper slower model for extraction and deduplication; use realtime only when the owner asks follow-up questions or reviews a prepared action.
- **latency:** A scheduled scan can take several minutes and retry unavailable sites; the spoken result should be under 30 seconds, with dashboard evidence loaded on demand.
- **cost:** Roughly $0.05-$0.30 per scan depending on number of portals; browser session time and model calls dominate, while unchanged pages should be fingerprinted without model inference.
- **security:** This touches financial, health, and identity-linked portals. Keep raw values in Safari/local encrypted storage, send only deadline/vendor/status evidence, never expose credentials, and stop before any cancellation, payment, or submission.
- **missing:** Durable authenticated page-watch/job runner with per-site schedules; Cross-site entity/deadline normalization and deduplication; Local redaction/privacy boundary for browser results; Review queue that holds prepared but unsubmitted mutations


## Changes it proposed to its own stack

### `browser-harness` — Add an in-extension privacy boundary before browser results leave Safari: classify DOM regions and form fields (credentials, payment, health, private messages, identifiers), redact or hash them by default, and return only the minimum quoted spans/structured fields requested by the job. Preserve a local encrypted evidence map keyed by commandId so the user can later expand a redacted field explicitly. Apply the same policy to screenshots via local OCR/region masking, with per-site rules and an audit receipt.
- **owner gets:** The assistant can work across logged-in sites without routinely shipping passwords, card numbers, message bodies, or unrelated personal data into model context. The owner still gets precise answers and can deliberately reveal one needed field when necessary.
- effort: Medium-high: extension-side DOM classification and screenshot masking, encrypted local evidence store, policy metadata in command results, and planner support for redacted values.  ·  risk: Over-redaction could make a task fail or produce misleading omissions; return explicit redaction markers and a retry request for a narrowly scoped field. Crashes recover by replaying the command against the local evidence map.
- cost: Small per-command CPU/storage overhead; lower model token and privacy exposure costs. No meaningful API increase; screenshot OCR may add local CPU use.  ·  latency: Adds roughly 50-300 ms for DOM filtering and more for screenshots; preferable to sending full pages and paying model latency.
- security: Major improvement: secrets remain in Safari unless explicitly released. Encryption key must stay in the extension/keychain, and audit logs must avoid raw values.
- depends on: chg-16bc5dee durable browser job runner; A functioning Safari extension result path


## What it asked for

_Nothing._
