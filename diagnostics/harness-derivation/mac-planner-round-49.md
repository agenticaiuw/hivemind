# Harness derivation — mac-planner — round 49

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac_readonly_inspect availability** — The tool is listed as granted, but every operation currently returns 'schema but has no implementation yet'; the Mac bridge still cannot provide running-app, foreground, accessibility, UI, tab, or directory state through this interface.
  - evidence: Four parallel calls to mac_readonly_inspect (running_apps, foreground_app, accessibility_enabled, browser_tabs) all returned the same implementation error in Round 49.

## Capabilities it proposed

### "When I ask for my inbox, GitHub, or calendar, give me what is available now and finish the rest automatically when the browser comes back."
- **useful because:** Today a browser outage turns a simple request into repeated failures. This makes the Mac’s bounded Calendar/Mail access useful immediately, preserves the authenticated-browser portion for later, and gives one final spoken/note receipt instead of making the owner retry.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background/cheap model for merging and retry classification; realtime only for the initial one-sentence status and final alert.
- **latency:** Initial partial result within 3 seconds; browser retry with exponential backoff for 30 minutes, then one failure receipt. No polling more often than every 60 seconds.
- **cost:** About $0.001–$0.01 per request depending on summarization; most cost is only the final merge, not each retry. Calendar/Mail reads are local bounded calls; browser work is session-bound.
- **security:** Only pre-authorized account scopes and snippets leave the Mac. Never expose message bodies by default. Do not send mail, modify GitHub, or click destructive controls; queue only read operations. Surface browser device/session and exactly which sources were unavailable.
- **missing:** A durable cross-surface job that stores a partial result and resumes when browser status changes; Browser online-event or safe periodic retry webhook, rather than blind repeated commands; A merge schema with per-source freshness, citations, and deduplication; An owner-visible receipt in the pendant/dashboard for partial, resumed, and expired states

### "Continue the thing I was doing yesterday, from where I left off, and show me the next action before you do it."
- **useful because:** Today an interrupted request dissolves into scattered tabs, drafts, files, pending jobs, and spoken context. The owner has to reconstruct the task manually. A durable handoff would let them resume a real workflow across days and devices without repeating the whole explanation or risking a duplicate action.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Cheap background model maintains and compresses the workflow record; realtime is used only to answer the resume request and present the next action.
- **latency:** Resume summary in under 3 seconds from a local cached checkpoint; state reconciliation in under 10 seconds. Never auto-execute the next action until the owner explicitly says continue.
- **cost:** Roughly $0.002–$0.02 per resume, dominated by one compact reconciliation pass; durable checkpoints and hashes are local/relay storage.
- **security:** The record may contain sensitive URLs, drafts, filenames, and account identities. Store encrypted checkpoints with per-surface capability scopes, redact content by default, and retain only task-relevant excerpts. Before resuming, show the source state, age, and intended mutation; require confirmation for sending, deleting, purchasing, or publishing. Prevent duplicate execution with idempotency keys and receipts.
- **missing:** A durable workflow-checkpoint protocol shared by relay, Mac, and browser, with step IDs, dependencies, state hashes, and expiry; Mac and browser adapters that can report task-relevant state and reconcile it without scraping unrelated content; A resume planner that distinguishes completed, stale, failed, and unsafe-to-repeat steps; A dashboard/pendant presentation for a compact checkpoint and explicit next-step confirmation


## Changes it proposed to its own stack

### `mac-harness` — Implement the already-granted mac_readonly_inspect contract (running apps, foreground app, accessibility state, UI snapshot, browser tabs, approved directory listings) in the Mac bridge, returning typed JSON with timestamp and explicit unsupported/error states. Add a non-invasive preflight snapshot to every planned job receipt.
- **owner gets:** The assistant can stop guessing whether Safari, VS Code, or accessibility is available, and can explain why an action failed without taking over the screen. It also makes browser-offline fallback honest instead of reporting generic failure.
- effort: 1–2 days: bridge handlers plus tests against empty/offline/browser-permission cases; small receipt schema extension.  ·  risk: UI APIs can return stale or privacy-sensitive data. Keep snapshots opt-in per job, redact window titles/paths by default, cap output, and fall back to explicit unknown. Recovery is simply retrying without the snapshot.
- cost: Negligible API cost and local CPU; no cloud data required unless the caller asks to include the snapshot.  ·  latency: ~100–300 ms for app/accessibility state; UI snapshot may add up to 1 s and should be requested only for UI jobs.
- security: Read-only but potentially sensitive. Approved paths only, no keystroke capture, no arbitrary screenshots, redact account names and document text by default.
- depends on: An implementation behind the granted mac_readonly_inspect tool; Receipt fields for preflight timestamp and source freshness


## What it asked for

_Nothing._
## Its own summary

Round 49 found a concrete live gap and proposed two changes. Browser status is still offline with 3 pending commands, so I proposed a cross-surface partial-brief/resume flow: bounded Mac Calendar/Mail results now, browser-dependent Gmail/GitHub work queued and merged later with freshness/citations. I also proposed implementing the granted read-only Mac inspection tool and attaching a redacted preflight snapshot to job receipts. The granted mac_readonly_inspect interface is currently only a schema: all four tested operations reported no implementation.

**Biggest unknown:** Whether the Mac bridge has any internal read-only inspection endpoint that can back this tool; until implemented, I cannot verify app state, accessibility permission, tabs, or directories before planning actions.

