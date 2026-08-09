# Harness derivation — mac-planner — round 247

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-live-readiness** — At 2026-08-09T00:02Z the Mac bridge, relay, browser extension, Accessibility, Screen Recording, and automation permissions were all live and ready; Safari had four durable browser sessions, including YouTube and Google News. The pendant itself remains unregistered over LTE, so Mac-attached testing is the current path.
  - evidence: mac_readonly_inspect running_apps resolved to GET /observe (HTTP 200): accessibility trusted/eventsPost true, screenRecording true, browser sessions 4; GET /ops/snapshot and GET /browser/status both returned online=true and relay reachable.

## Capabilities it proposed

### "When I say “take over from here” while wearing the pendant, use what is on my Mac right now to finish the task: inspect the foreground app or browser tab, make the smallest useful edits or clicks, and tell me exactly what changed."
- **useful because:** This is the system's highest-value job: the pendant supplies intent while the Mac supplies eyes, authenticated browser sessions, and hands. Today those surfaces are separately callable; this makes an interrupted thought become a completed desktop outcome without the owner narrating every UI step.
- **path:** pendant → relay → mac-vision → browser-extension → mac-planner
- **model tier:** Use realtime only to understand the short spoken handoff and give the result; use the local vision/computer-use loop for UI work, with a cheaper text model to turn receipts into a one-sentence spoken report.
- **latency:** Acknowledge in under 1 second; inspect and act within 5–20 seconds, bounded to 25 steps. If the current app or target is ambiguous, stop and ask one focused question rather than guessing.
- **cost:** One realtime turn plus zero to a few local vision calls; roughly $0.01–$0.08 depending on screenshots and step count. The expensive part is repeated screenshots, not the relay acknowledgement.
- **security:** The relay should receive intent and redacted action receipts, not page passwords or full screenshots by default. The Mac loop may use authenticated sessions and FULL_CONTROL_MODE, so every run needs an explicit owner policy class for unattended actions, a before/after receipt, and a local undo/stop phrase. Sending mail, deleting files, purchases, and submissions must remain confirmation-required even though the current executor lacks a live gate.
- **missing:** A single handoff job that binds one pendant utterance to one foreground-app/browser-session context and one durable receipt; A policy-aware stop/confirm seam in the Mac executor (owner must configure it; do not assume FULL_CONTROL_MODE is consent); A compact result event from mac-vision containing target, actions, changed resources, and failure reason

### "After you do something on my Mac or in the browser, verify that it really took effect and fix it once if it did not — for example, confirm a saved document contains the new text or that a web form shows the submitted state — then tell me success, partial success, or failure."
- **useful because:** The dangerous gap today is not ability to click; it is false success. A pendant user cannot inspect a distant screen while walking. Independent verification turns brittle computer control into a trustworthy agent and catches stale tabs, dropped keystrokes, navigation races, and extension failures before the owner relies on the result.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** Use a cheap deterministic verifier first (DOM/state query, file hash, app-readable state, or screenshot diff); invoke the realtime model only for the spoken request and ambiguous repair choice. Use vision only when no structured state exists.
- **latency:** Initial action plus verification under 10 seconds for ordinary work. Allow one bounded repair attempt and a 30-second ceiling; report the first failure immediately if verification cannot be performed.
- **cost:** Usually <$0.01 using structured checks; $0.02–$0.06 when a screenshot and one local vision comparison are needed. No model call is needed for hash/DOM/state assertions.
- **security:** Verification must never silently broaden the action (e.g., resubmit a purchase). Store hashes, selectors, and redacted before/after facts rather than page bodies. A repair that changes external state needs the same owner policy class as the original action and must produce a linked receipt.
- **missing:** A declarative postcondition schema for files, apps, and browser DOM/state; A Mac executor hook that runs the postcondition after each action group and returns changed-resource evidence; A linked repair job with an attempt limit and receipt relationship across relay, Mac, and browser

### "When I leave my Mac mid-task or the connection drops, preserve where I was and what remains to do, then give me a short spoken resume card on the pendant when I reconnect; when I return, restore the exact browser tab and files without repeating completed work."
- **useful because:** The Mac and pendant are useful at different times: the Mac has the authenticated work and the pendant travels. This makes walking away safe instead of forcing the owner to remember tabs, unsaved edits, and half-finished agent jobs. It also prevents retries from duplicating an external action.
- **path:** mac-planner → browser-extension → relay → pendant → mac-vision
- **model tier:** Use deterministic workbench/job receipts and browser metadata for the capsule; use a small background text model to compress it into a one-sentence card. Reserve realtime for the owner's request to resume or change the plan.
- **latency:** Checkpoint on disconnect or explicit leave within 2 seconds; reconnect card should arrive within 5 seconds. Restore should be a bounded, explicit action and never auto-submit external forms.
- **cost:** Near-zero model cost for checkpointing; <$0.01 for summarization. Storage is a few KB per capsule plus optional redacted screenshot thumbnails.
- **security:** Never persist passwords, page bodies, clipboard secrets, or microphone audio. Encrypt capsule contents at rest and expire them. Restoration must validate the tab URL, file hashes, and job id before acting; if any drift is detected, speak “changed since checkpoint” rather than replaying clicks. Owner policy must decide which apps may be checkpointed.
- **missing:** A first-class capsule format linking Mac job receipts, browser session/tab identity, open files, and unfinished postconditions; A disconnect/idle trigger and relay delivery path that writes the capsule to the existing pendant inbox without duplicating offline alerts; An idempotent restore planner that uses hashes and browser/session identity rather than replaying raw coordinates

### "For anything consequential—send, publish, buy, or delete—show me the exact final target and summary on the Mac, read the summary aloud through the pendant, and let one deliberate press of the pendant authorize only that specific action; if the target changes, make me approve again."
- **useful because:** The owner gets maximum automation without having to babysit ordinary work, while consequential actions require physical presence and a clear last-look. This is stronger than a Mac popup: the approval cannot be accidentally triggered by a stale browser tab, background job, or remote prompt, and it works while the owner is away from the keyboard.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** Use deterministic target canonicalization and action hashing for the approval record. Use realtime only to explain the summary conversationally; use no model at all to decide whether a button press matches the pending hash.
- **latency:** Prepare the exact preview in under 2 seconds, speak it in under 3 seconds, and accept a single press for 30 seconds. Any changed target, expired preview, disconnect, or retry invalidates it immediately.
- **cost:** Usually under $0.01: one short realtime utterance plus deterministic hashing and a tiny signed event. No screenshot or model call is needed after the preview is prepared.
- **security:** The Mac must canonicalize recipient, URL, amount, file paths, and payload hash locally; secrets and full page contents must never enter the relay approval event. A press authorizes exactly one immutable hash, never a class of actions. Replay protection, expiry, device pairing, and a visible spoken cancellation are mandatory. The current FULL_CONTROL_MODE has no live approval gate, so this must be implemented below the execution dispatch rather than as a prompt convention.
- **missing:** A paired pendant-presence challenge path from the physical button to the Mac action broker, with nonce, expiry, and replay protection; A canonical preview/hash format for browser submissions, mail, purchases, deletions, and file mutations; An execution seam that refuses a consequential action unless its exact hash has a fresh pendant authorization, plus an append-only receipt tying preview, press, and result


## What it asked for

_Nothing._
## Its own summary

Round 247 produced three new cross-node capabilities: (1) a spoken pendant handoff that uses current Mac/browser context to complete a task, (2) declarative postconditions with one bounded repair so actions are verified rather than merely reported successful, and (3) durable Mac-to-pendant resume capsules that survive disconnects and prevent duplicate retries. Live inspection also established that the Mac bridge, relay, browser extension, Accessibility, Screen Recording, and automation permissions are currently ready; Safari has four durable sessions. I also recorded that the pendant is still LTE-unregistered, so USB/Mac-attached testing is the real path today.

**Biggest unknown:** Whether relay already has a durable capsule-to-pendant delivery route and whether browser sessions expose enough stable DOM/state identifiers for postcondition verification. I asked relay-realtime for route-level confirmation. Still needed: a policy-aware action/repair seam (owner-configured, not assumed from FULL_CONTROL_MODE), a declarative postcondition contract, and an idempotent capsule/restore format linking job receipts, browser identity, file hashes, and the existing pendant inbox.

