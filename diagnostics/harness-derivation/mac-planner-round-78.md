# Harness derivation — mac-planner — round 78

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-state** — Mac agent is online/full-control but not ready: Accessibility trusted=false and Screen Recording granted=false; browser extension offline with 5 pending commands and stale browser sessions.
  - evidence: GET /ops/status and GET /browser/status at 2026-08-07T11:49Z

## Capabilities it proposed

### "When my browser reconnects, tell me what was waiting and resume only the task I choose."
- **useful because:** Today the bridge can be offline while five commands wait and sessions point at stale tabs. This turns reconnection into a safe, understandable handoff: the pendant gets a short digest, stale work is not silently consumed, and the owner can choose one task to continue.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Cheap background model classifies queued commands and drafts a digest; realtime is used only if the owner discusses the choices by voice. No model is needed for tab identity or freshness checks.
- **latency:** Heartbeat detection within one polling interval (about 1-5 s); digest under 2 s. Resume begins only after a fresh tab/session witness and the owner's spoken selection.
- **cost:** Near-zero when idle; roughly $0.001-$0.01 per reconnect depending on queue size and summarization. Dominant cost is model summarization of command labels/results, not transport.
- **security:** Queued commands can contain private URLs, form data, or mutations. Keep raw payloads on the Mac/relay, show redacted labels and target domains on the pendant, expire commands after a TTL, and never replay a mutation solely because the extension came online. Require explicit owner selection for each non-read step; preserve the owner's maximum-access policy once selected.
- **missing:** A reconnect/quarantine state machine that distinguishes fresh pending commands from stale ones; Per-command intent labels, target tab fingerprint, TTL, and resume cursor persisted with receipts; A pendant notification/choice protocol and dashboard view for quarantined work; Browser heartbeat must report a stable tab/session fingerprint before replay

### "Bookmark this workspace, and restore it when I come back."
- **useful because:** The owner can leave a complicated desktop task and later return to the same working set instead of reconstructing it from memory. The bookmark would capture the active Mac apps, relevant files, browser tabs, and the last verified task step; restoration would detect drift and report it rather than blindly replaying old actions. This is a durable handoff between the worn pendant, the always-awake relay, the Mac, and authenticated browser sessions—not just opening a few apps.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** A cheap background model names and compresses the workspace capsule and identifies likely task-related items; deterministic code handles app/tab/file identity and restoration. Realtime is only used for the short spoken bookmark/restore interaction.
- **latency:** Bookmark confirmation in under 3 seconds. Restore should show a concise pendant status within 5 seconds and progressively open the verified workspace over 10-20 seconds, without blocking unrelated Mac use.
- **cost:** About $0.001-$0.02 per bookmark/restore, dominated by optional capsule summarization; deterministic snapshots and relay storage are negligible.
- **security:** Workspace state may reveal private URLs, filenames, and app contents. Store encrypted, redacted metadata by default; retain raw content only when explicitly requested. Never save passwords, form fields, or browser page bodies implicitly. Restoration must validate current tab/session identity and mark missing or changed resources instead of overwriting them. Opening files and tabs is reversible enough for the owner's maximum-access policy; destructive mutations are never part of restoration.
- **missing:** A first-class workspace-capsule schema containing app identities, file bookmarks, browser session/tab fingerprints, and the last verified job cursor; A relay-backed encrypted capsule store with retention and explicit delete; A Mac snapshot adapter that can obtain current apps/windows/files without relying on stale job logs; A restore planner that compares the capsule with current state and emits idempotent open/close actions; Pendant commands and dashboard controls for naming, listing, expiring, and restoring capsules


## Changes it proposed to its own stack

### `mac-harness` — Implement the already-granted mac_readonly_inspect contract as a real local-agent state-witness endpoint/tool. Support running_apps, foreground_app, browser_tabs, accessibility_enabled, ui_snapshot (only when Screen Recording is granted), and bounded list_directory. Return timestamped, redacted, typed snapshots with a monotonic witnessId and explicit unavailable reasons; never infer current state from stale browser sessions or the jobs log. Add a pre/post witness attachment to every mac_run_actions receipt so the relay can reconcile whether a step actually changed the desktop.
- **owner gets:** When the owner says 'continue that' or asks what is on screen, the pendant can tell the truth about the Mac and resume without stealing focus or replaying a stale browser command. Failed/offline browser work becomes an actionable 'extension offline / 5 commands pending' report instead of a misleading success.
- effort: Medium: local read-only inspectors plus receipt schema and tests; ui_snapshot needs the owner to enable Accessibility and Screen Recording, while the other inspectors can work with existing automation grants.  ·  risk: Snapshots may expose app names, URLs, window titles, or file names; default to redaction and bounded allowlisted paths, and attach only hashes/summaries to relay memory. If an inspector fails, mark witness unavailable and do not block ordinary actions. Recovery is retrying the witness and preserving the action receipt.
- cost: Negligible API cost; local CPU only. Small storage increase for bounded witness summaries (roughly <10 KB per action).  ·  latency: ~50-300 ms for app/foreground/browser inspection; ui_snapshot may add 0.5-2 s. Do not invoke vision unless explicitly needed.
- security: Read-only local access; browser URLs and UI text are sensitive, so redact by default and require explicit scope for raw snapshots. No new arbitrary shell capability.
- depends on: Implement the granted mac_readonly_inspect tool (currently schema exists but returns 'no implementation yet'); Keep browser session IDs and extension heartbeat as freshness checks; Optional: owner enables Accessibility and Screen Recording for UI snapshots


## What it asked for

_Nothing._
