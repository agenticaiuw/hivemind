# Harness derivation — mac-terminal — round 212

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **USB serial observability** — The granted mac_usb_serial_diagnostics schema is still unresolved at runtime; no serial/USB inventory capability exists, so I cannot read the physically connected nRF9160 or ESP32 ports through a dedicated tool this round.
  - evidence: Called mac_usb_serial_diagnostics for all four documented ports with 1 s bounded reads; resolver returned unresolved, best match action:get_mac_status score 0.226.

## Capabilities it proposed

### "Pause that task; I’m leaving. When I’m back, resume it exactly where it stopped and tell me what remains."
- **useful because:** Today a Mac job, browser session, and pendant conversation have separate lifetimes. This would let the owner safely interrupt a multi-step task without losing the authenticated page, already-completed steps, or the reason it stopped, then continue later from the first unverified step rather than repeating side effects.
- **path:** pendant → mac-planner → browser-harness → relay → dashboard
- **model tier:** Background model for checkpoint classification and resume planning; realtime model only for the brief voice acknowledgement. No expensive turn is needed to poll progress.
- **latency:** Acknowledge the pause in under 1 second; checkpoint the active step within 2 seconds; resume within 5 seconds of a later voice command, excluding browser/network latency.
- **cost:** About $0.01–$0.05 per pause/resume depending on the number of steps; most cost is one compact checkpoint summary, not continuous conversation.
- **security:** The checkpoint may name authenticated tabs, local paths, or partially completed mutations. Keep page contents and secrets on the Mac/browser, store only hashes, step keys, and redacted state in relay memory, and require explicit owner intent to resume mutations. Never claim a step completed unless its receipt and post-state both exist.
- **missing:** A durable semantic checkpoint record that joins jobId, ledger stepKey, browser commandId, and conversation turnId; A resume executor that revalidates post-state before replaying a step and marks ambiguous steps as needing owner input; A Mac process-group handle so pause can stop a long-running shell rather than merely setting a cooperative abort flag

### "Before you tell me it’s done, prove it: check the Mac, the browser page, and the original request, then tell me exactly what changed and what you could not verify."
- **useful because:** A successful API call is not the same as the owner’s goal: a browser save can land in the wrong account, a shell command can exit early, and a page can change after a click. This gives one trustworthy answer assembled from independent evidence instead of a confident execution receipt.
- **path:** pendant → mac-planner → browser-harness → relay → dashboard
- **model tier:** Use a cheap background verification model to compare structured pre/post facts; reserve realtime for the spoken result and only escalate ambiguous contradictions to the expensive tier.
- **latency:** Return a short preliminary acknowledgement immediately, then complete independent checks in 3–10 seconds; if a page or process is still settling, report pending rather than wait indefinitely.
- **cost:** Roughly $0.02–$0.10 per verified task. The dominant cost is fetching a second structured browser snapshot and compacting filesystem/process state, not generation.
- **security:** Evidence can contain private page titles, file names, and account identifiers. Keep raw evidence local, send only redacted hashes/fields to relay, and expose the exact source and timestamp on the dashboard. A mismatch must be reported as unverified, never silently repaired by repeating a mutation.
- **missing:** A typed verification plan that maps each user goal to independent Mac and browser postconditions; A read-only Mac snapshot of command exit code, process state, and relevant file hashes; A compact evidence bundle and contradiction state that the pendant can summarize without uploading page contents

### "If you get stuck, don’t just say failed—tell me the one thing only I can do, wait for my answer on the pendant, and continue without starting over."
- **useful because:** Real work commonly stops at an owner-only boundary: a 2FA prompt, a permission dialog, a choice between two similar records, or a missing attachment. Today that boundary collapses into a failed job. This turns it into a compact handoff: the Mac/browser preserves its state, the relay carries one precise question, and the pendant collects the answer while the owner is away from the keyboard.
- **path:** pendant → relay → mac-planner → browser-harness → mac-vision → dashboard
- **model tier:** Cheap background model classifies the blocker and drafts a single-question handoff; realtime handles only the owner’s spoken answer. Use the expensive tier only when the answer is genuinely ambiguous.
- **latency:** Detect and announce a blocker within 2 seconds; ask one question under 15 words; resume within 5 seconds after the answer reaches the Mac/browser.
- **cost:** About $0.01–$0.06 per blocker, dominated by one compact state summary and (for browser challenges) a fresh structured snapshot.
- **security:** Do not read or relay OTP values, passwords, or page contents by default. Show the owner which app/tab is waiting, keep secrets local to the browser, bind the answer to a nonce and job step, expire it quickly, and reject late answers after the page has changed.
- **missing:** A blocker taxonomy with owner-answer schemas (approve, choose, provide-local-file, retry-after-login) instead of free-text prompts; A parked-step protocol that keeps the browser session and Mac job alive without replaying the completed mutation; A pendant-to-relay answer channel carrying a nonce, turnId, and expiry, with visible stale-question feedback

### "Keep me reachable without interrupting me: watch my Mac, authenticated browser sessions, and relay events, then interrupt the pendant only when something is urgent enough to displace what I’m doing—and tell me why it crossed that threshold."
- **useful because:** The owner currently has fragmented notifications and no dependable notion of attention cost. This would make the pendant a selective interrupt channel rather than another noisy inbox: it can distinguish a deadline change, a failed automation, and a routine update while considering the owner’s active app and current conversation.
- **path:** pendant → relay → mac-planner → browser-harness → dashboard
- **model tier:** A cheap background classifier handles event deduplication and urgency scoring; realtime is used only to phrase an interruption that actually passes the threshold.
- **latency:** Ingest ordinary events within 10 seconds; surface a genuinely urgent event within 2 seconds; suppress duplicates and batch low-priority changes into a later digest.
- **cost:** Approximately $0.01–$0.04 per event burst, dominated by compact event classification. Most routine events should be handled without a model call using cached rules and hashes.
- **security:** This necessarily correlates foreground-app state, authenticated browser metadata, relay jobs, and possibly calendar/mail-derived urgency. Keep raw content on its originating surface, transmit only redacted event summaries and confidence, provide a physical mute state on the pendant, and show an audit trail of every interruption and suppression decision.
- **missing:** A cross-surface event envelope with source, owner-visible summary, sensitivity, urgency evidence, expiry, and deduplication key; A user-adjustable attention policy that learns from dismissals without silently changing emergency thresholds; A relay-side event fusion and quiet-hours scheduler that can reach the pendant even when the Mac or browser changes state; A Mac foreground/lock/activity signal and browser event stream with stable privacy-preserving identifiers

### "I just did that successfully—turn what you observed into a routine I can name, inspect, and run next time, without recording secrets or brittle screen coordinates."
- **useful because:** The owner repeatedly performs the same multi-surface work but cannot currently promote a successful Mac/browser session into a trustworthy reusable routine. This would convert observed intent and verified outcomes into an editable recipe, preserving semantic targets while omitting passwords, tokens, and accidental clicks.
- **path:** mac-planner → browser-harness → relay → dashboard → pendant
- **model tier:** Use a background model to infer reusable steps from receipts and browser provenance; use realtime only when the owner names or corrects the generated routine.
- **latency:** Offer a draft within 10 seconds after a verified task; routine execution should start within 2 seconds and pause on the first uncertain target.
- **cost:** About $0.05–$0.20 per routine draft, mostly for compressing and generalizing the action trace; subsequent runs can be mostly deterministic and cheap.
- **security:** Action traces may expose private URLs, names, and local paths. Strip credentials and sensitive values before persistence, represent targets by approved semantic locators rather than screenshots, retain the source evidence and creation date, and require the owner to inspect the draft before it becomes callable.
- **missing:** A trace-to-routine compiler that generalizes targets while retaining explicit input parameters; Secret and personal-data redaction over shell, browser, and file receipts before routine persistence; A routine versioning and test-run format with expected postconditions and automatic drift detection; An owner-facing routine editor that can rename, disable, and repair one failed step from the pendant or dashboard

### "If I change something manually while you’re working, notice the conflict and protect my newer intent instead of overwriting it or blindly continuing."
- **useful because:** A Mac agent and browser automation can race the owner: a form, file, tab, or setting may change after a plan was made. Today the system has no owner-intent conflict model, so a successful later action can destroy a manual correction. This capability makes automation coexist with the owner rather than competing with them.
- **path:** mac-planner → mac-vision → browser-harness → relay → pendant → dashboard
- **model tier:** Use deterministic hashes and structured postconditions first; use a cheap model only to explain a conflict and suggest a safe continuation. Realtime is needed only for a brief pendant question.
- **latency:** Detect a conflicting change before the next mutating step, typically under 500 ms after a snapshot; ask the owner within 2 seconds and never wait indefinitely while holding a stale action.
- **cost:** Under $0.01 for most checks because hashes and structured fields dominate; $0.02–$0.06 for ambiguous conflict explanations.
- **security:** Before/after snapshots may contain private document or page data. Keep raw snapshots local, retain minimal hashes and field-level diffs, bind each continuation to the current session and step nonce, and expire unresolved conflicts rather than replaying stale mutations.
- **missing:** A cross-surface precondition and intent-version protocol for files, UI fields, browser pages, and settings; Owner-change attribution that distinguishes a manual edit from the agent’s own action; A conflict state machine with safe choices such as keep-owner-change, merge, re-read, or abandon; Pendant and dashboard rendering of a compact diff without exposing private page contents


## What it asked for

_Nothing._
