# Harness derivation — mac-terminal — round 222

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live USB diagnostic reachability** — The granted mac_usb_serial_diagnostics schema still does not resolve in the live inventory, despite both chips being physically connected; nearest capability is get_mac_status. Bench serial truth remains accessible only indirectly through existing shell capture scripts.
  - evidence: Called mac_usb_serial_diagnostics with the four enumerated device paths; resolver returned unresolved, inventory 223 routes/99 actions, best score action:get_mac_status 0.226.

## Capabilities it proposed

### "Make sure the thing I asked my Mac to do actually finishes, even if the command hangs or the local agent restarts."
- **useful because:** Today a 120-second shell action can hang without being killed, cancellation cannot interrupt it, retries do not exist, and a restart leaves jobs marked processing forever. This would turn a spoken request into a durable outcome rather than a hopeful dispatch, with the pendant truthfully reporting stale/failed state.
- **path:** pendant → relay → mac-planner → mac-vision → dashboard
- **model tier:** background for watchdog classification and retry planning; realtime only for the owner's spoken status question
- **latency:** Dispatch remains immediate; watchdog checks every 2-5 seconds, declares a dead worker within 15 seconds, and retries only after inspecting the durable ledger.
- **cost:** Low: mostly relay polling and local receipts; one cheap model call only for choosing a recovery branch after a failure. Dominant cost is any repeated Mac action, not reasoning.
- **security:** A retry can duplicate an irreversible command. The system must classify the action's replay safety, preserve the original command and outputs, and refuse automatic replay of non-idempotent actions while still reporting them on the pendant. No command contents or environment should leave the Mac.
- **missing:** Process-group cancellation that actually kills the child and descendants; Boot-time reconciliation of processing jobs and closing/associating ledgers; Idempotency/replay-safety enforcement wired into /execute; A relay watchdog that can push stale/failed state to the pendant

### "Put me back exactly where I was working when I say 'resume my work'—restore the right Mac windows, project, and authenticated browser page together."
- **useful because:** A browser tab alone or a Mac project alone is not the owner's context. A wearable-triggered resume should restore the cross-device working set, verify that the browser session is still the same authenticated page, and explain any part it cannot safely restore instead of opening the wrong document.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** background model builds a compact context capsule and maps it to restore actions; realtime only handles the short spoken command and confirmation of ambiguity
- **latency:** Capture in under 3 seconds when the owner marks a pause; restore in under 10 seconds, with each surface reporting readiness independently.
- **cost:** One small model call per save/restore plus local route calls; browser snapshots and Mac window inspection dominate latency, not tokens.
- **security:** Never persist page contents, cookies, or secrets. Store app/window identifiers, project path, tab URL/title, and a short owner-approved label. Restoration must detect expired sessions and avoid submitting forms or mutating pages.
- **missing:** A Mac snapshot/restore action for window geometry, focused app, and project workspace; A browser session snapshot with stable tab identity and authenticated-session health; A compact encrypted context-capsule store addressable by the pendant's existing moment marker payload; Cross-surface restore transaction with per-step receipts and rollback for window changes

### "Only interrupt me when something truly needs me: watch my authenticated browser sessions and Mac work, collapse duplicates, and tell me on the pendant what changed and what I should do."
- **useful because:** The owner currently has separate browser watches, Mac jobs, and briefing sources with no shared urgency model. This would turn a constant stream of tabs and agent completions into a single, sparse interruption channel that works while the Mac is open and queues a truthful alert for the pendant when it is not.
- **path:** browser-extension → mac-planner → mac-vision → relay → pendant → dashboard
- **model tier:** Cheap background model continuously deduplicates and ranks changes; realtime model only verbalizes a selected urgent alert or answers 'why did you interrupt me?'
- **latency:** Browser/Mac change detection within 30 seconds; urgent pendant alert within 5 seconds of classification; daily digest generation can be minutes.
- **cost:** Low-to-moderate polling and embedding/classification cost; token spend is bounded by sending only diffs and source metadata, never whole pages.
- **security:** Keep page text and private Mac content on-device; relay receives hashes, urgency, source host/app, and a short redacted summary. Per-site allowlists and a local pause switch are essential. Never take action from an alert without an explicit owner command.
- **missing:** A unified event envelope for browser page watches, Mac job completion/failure, and active-work changes; Cross-source deduplication and urgency policy with owner-tunable quiet hours; A privacy-preserving local summarizer/redactor before relay delivery; A durable alert inbox that can target the pendant's offline queue and acknowledge exactly once

### "Turn the authenticated page I am viewing into a private offline briefing I can listen to from the pendant later, with every claim tied back to its source and a way to ask follow-up questions without reopening the page."
- **useful because:** Today the browser can inspect a logged-in page and the Mac can generate research speech, but there is no end-to-end handoff from a private session into a durable, source-grounded wearable briefing. This lets the owner leave the desk without losing the page's useful content or silently trusting an untraceable summary.
- **path:** browser-extension → mac-planner → relay → pendant → dashboard
- **model tier:** Background model extracts and compresses only the requested page into cited claims and an audio script; realtime model handles a later spoken follow-up using the stored evidence capsule, not the whole page.
- **latency:** Capture and source indexing under 15 seconds for a normal page; audio becomes available within 30 seconds; pendant playback must start from its local queue without waiting for the browser.
- **cost:** Moderate per briefing, dominated by speech synthesis and page extraction; follow-ups are cheap because they reuse the compact evidence capsule.
- **security:** Page text, credentials, and cookies stay on the Mac/browser. The relay receives encrypted claim capsules and audio, with host/URL provenance and expiry. Never retain an entire private page by default; refuse follow-up answers when the stored evidence is insufficient rather than inventing them.
- **missing:** A browser-to-Mac private-content handoff that transfers selected structured claims without exposing session credentials; An evidence-capsule format with claim-level URL, title, selection/time, expiry, and confidence; Offline pendant audio/text queue with resumable playback and acknowledgement; A follow-up router that grounds answers in the capsule and can request a fresh browser read when online

### "Handle this multi-step web task for me, pause only when the site asks for a decision or authentication, and resume from the exact step after I answer on the pendant."
- **useful because:** Current browser actions are short command batches and Mac delegation is not a durable, resumable transaction. A long task can stop at an expired session, a confirmation page, or a changed layout and leave the owner unsure what happened. This would make authenticated browser work genuinely delegable while preserving the owner's control over decisions.
- **path:** pendant → relay → browser-extension → mac-planner → mac-vision → dashboard
- **model tier:** Background planner maintains the workflow state and uses a cheaper verifier after each step; realtime is reserved for the pendant's brief decision prompt and answer.
- **latency:** Each safe step executes immediately; a paused decision is queued instantly and can resume within 3 seconds of the owner's answer.
- **cost:** Moderate: browser interaction calls dominate, while state validation is cheap. Failed or changed pages should cost one re-plan, not a full restart.
- **security:** Never guess through payment, deletion, sending, or external publication steps. Persist a redacted action graph and page fingerprints, not credentials or full page bodies. Bind the answer to a specific step, site, and workflow nonce so a stale pendant response cannot authorize a different action.
- **missing:** Durable browser workflow state machine with checkpoint and resume tokens; Page fingerprint/diff verifier that detects layout or semantic changes before continuing; A pendant decision protocol carrying workflow nonce, options, expiry, and exactly-once answer; Browser action receipts joined to Mac job and relay workflow IDs; Recovery policy for expired authenticated sessions and changed pages


## Changes it proposed to its own stack

### `integration` — Add a first-class dual-chip bench session: launch the existing nRF9160/ESP32 autocapture scripts, parse timestamped UART lines into a bounded event stream, correlate USB disconnects and frame counters, and expose a single session receipt linked to the Mac job. When the pendant button is pressed, include the nearest serial events and bridge health in the action status shown on the dashboard.
- **owner gets:** The owner can test the actual wearable and audio bridge today, but currently has to run two scripts and manually compare unrelated logs. This would reveal 'button pressed but no audio', dropped frames, and which chip went stale in one glance before claiming the wearable works.
- effort: Medium: host-side parser plus dashboard session view; no firmware protocol change required if existing diagnostic frames are stable.  ·  risk: UART formats may change and a parser could mislabel silence as health. Preserve raw logs, show parser confidence, and never overwrite evidence. USB remains bench-only and must not be represented as LTE continuity.
- cost: Negligible API cost; local disk bounded to rotated logs, roughly tens of MB per session.  ·  latency: Near-real-time, 100-500 ms event updates; startup cost is the serial process launch.
- security: Local-only by default; redact payload bytes and transmit only counters/timestamps unless the owner explicitly exports raw logs.
- depends on: A real serial reader/parser capability or a narrowly scoped implementation over run_shell; Stable diagnostic framing in both chip firmwares; A dashboard route for correlated bench sessions


## What it asked for

_Nothing._
## Its own summary

This round produced four non-duplicate directions: a durable cross-node Mac job watchdog/recovery path (the highest-value reliability feature), exact cross-surface work-context restore, a sparse urgency/interruption channel, and a dual-chip USB bench-session correlator. I also verified that the supposedly granted USB serial diagnostic tool still does not resolve; the physical chips are present but serial truth remains inaccessible except through shell capture scripts. The most actionable missing capability is therefore a bounded serial reader/parser plus correlated dashboard receipt, not another proposal for wearable LTE behavior.

**Biggest unknown:** I still cannot read either USB UART through a resolved tool, so I do not know the live nRF9160/ESP32 framing, counters, or whether the current firmware emits health frames. Someone must implement the serial diagnostic capability or run the existing dual-chip capture scripts and inspect their logs.

