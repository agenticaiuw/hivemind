# Harness derivation — faculty-judgement — round 138

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Show me what you’re about to send or change, and let me approve it with one press on my pendant.”"
- **useful because:** The owner gets a genuinely trustworthy approval boundary: a browser form, message, purchase, or file operation can be prepared while they stay hands-free, but execution requires a physical press on the worn device. The preview and the press are cryptographically bound, single-use, and expire if the page or values change.
- **path:** browser-extension → mac-planner → relay-realtime → relay-realtime
- **model tier:** Realtime for the short spoken preview and approval handshake; background/local models for extracting the proposed diff and checking it has not changed.
- **latency:** Preview in under 3 seconds; after a button press, execute within 2 seconds and speak a one-sentence receipt.
- **cost:** Usually <$0.01 per approval; dominant cost is model extraction only for ambiguous pages, not the button handshake.
- **security:** The relay must never treat voice alone as approval for configured sensitive classes. Bind approval to a hash of target, account, tab, before/after values, and action; reject stale or replayed presses. No secret page contents need leave the Mac except the minimal preview. Purchases, sending messages, deletion, and external publication remain explicitly confirmable.
- **missing:** Pendant serial button-event transport and signed nonce acknowledgements; A physical-consent policy and one-shot nonce store in relay; Observation-backed browser/Mac diff receipts before arming execution

### "“When did I decide this, and what evidence led me there?”"
- **useful because:** The owner can recover the reasoning behind a decision instead of hunting through email, notes, browser tabs, and spoken conversations. The system returns a short dated chain of source excerpts, distinguishes remembered facts from inference, and offers to open the exact source on the Mac.
- **path:** relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Background/cheap model builds and indexes the evidence graph; realtime is used only to answer the spoken question and explain uncertainty.
- **latency:** Answer in 5 seconds for indexed sources; up to 20 seconds when authenticated tabs or local files must be searched.
- **cost:** <$0.02 for an indexed query; authenticated-page or broad local search dominates cost and should be opt-in.
- **security:** Keep private mail, files, and browser content on the Mac where possible; send only ranked snippets and provenance hashes to relay. Never expose sensitive facts merely because they are semantically related. Show source scope and confidence, and require confirmation before opening or sharing a source.
- **missing:** A cross-surface evidence index covering voice captures, local notes, Mac logs, and authenticated browser snapshots; Claim-versus-source lineage with contradiction handling and retention controls; A spoken disambiguation flow when several decisions match

### "“I got interrupted—give me the one-minute context I need to continue, and put me back where I was.”"
- **useful because:** After a call, notification, or commute interruption, the owner gets a spoken recovery card: what they were trying to do, the last confirmed step, unresolved choice, and the exact browser tabs/files to reopen. It works from the pendant without requiring them to remember a project name, and avoids the usual false claim that an action completed.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Cheap background summarization maintains a rolling, privacy-filtered context window; realtime only compresses it into the one-minute spoken response. Mac/browser perform the optional restore.
- **latency:** Speak the first useful sentence within 2 seconds; restore tabs/files and report verified state within 8 seconds.
- **cost:** <$0.01 when the rolling summary exists; occasional local summarization is the dominant cost.
- **security:** The rolling context must be encrypted and TTL-limited, with a physical privacy latch that stops capture. Do not repeat secrets or private page contents aloud in public. Restore is reversible and observation-backed; if Accessibility is unavailable, report that reopening—not UI manipulation—was performed.
- **missing:** A rolling cross-surface activity/context stream with explicit privacy zones and TTL; A continuation summarizer that records last confirmed state versus intent; Pendant button/event transport and a safe restore packet consumer

### "“Warn me before my personal information leaves my devices, wherever I’m about to send it.”"
- **useful because:** The owner gets a last-second, understandable warning when an email, browser form, upload, message, or clipboard action contains sensitive material such as credentials, private documents, financial details, or secrets. It can identify accidental cross-account or wrong-recipient leaks before submission, without requiring the owner to remember every privacy rule.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → pendant
- **model tier:** A local classifier handles routine secret and destination matching; a cheaper background model learns the owner's sensitivity labels; realtime is used only for ambiguous, urgent warnings.
- **latency:** Inline browser and clipboard checks under 150 ms; spoken or haptic warning within 1 second for ambiguous high-risk actions.
- **cost:** Near-zero API cost for local pattern and destination checks; <$0.01 for an ambiguous classification, with local inference dominating engineering complexity.
- **security:** Sensitive content must remain on-device by default and never be sent to the relay merely to classify it. Maintain an explicit per-destination policy, show the exact category and destination, allow one-time override only through deliberate pendant confirmation, and never store the secret itself in telemetry.
- **missing:** System-wide Mac egress interception covering Mail, Messages, clipboard, uploads, and shell tools; Browser pre-submit and file-upload hooks with destination identity; A local sensitivity taxonomy and owner-editable allow/deny policy; Pendant haptic/LED warning and one-shot override transport

### "“Watch me do this once, then offer to handle the boring parts next time without taking over.”"
- **useful because:** The owner can teach the system a personal workflow by demonstration—such as filing a recurring report or preparing a weekly download—without writing automation. The system extracts stable steps, identifies the steps that vary, runs future instances in preview mode, and asks only about the uncertain or consequential parts.
- **path:** mac-vision → browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** A background model synthesizes the demonstrated workflow and clusters later runs; realtime is reserved for asking a short clarification when a variable step is encountered.
- **latency:** Record actions without perceptible delay; produce a proposed routine within 30 seconds; future routine previews in under 5 seconds.
- **cost:** <$0.05 per workflow synthesis and <$0.01 per routine run; screenshots and page-state comparison dominate processing.
- **security:** Capture only an explicitly armed demonstration, redact credentials and secret fields locally, and require review before saving a routine. Routines run in a sandbox/preview first; destructive, external, or financial steps always stop for approval. The owner can revoke a routine and erase its recordings.
- **missing:** An explicit teach-mode recorder spanning Mac and authenticated browser actions; A routine compiler that separates stable actions from variables and irreversible checkpoints; Per-routine versioning, test runs, and rollback; A pendant button to arm/disarm teaching without relying on GUI permissions


## Changes it proposed to its own stack

### `integration` — Make every Mac/browser action receipt carry an epistemic outcome: observed_success, reported_success_unverified, blocked_unreachable, or failed. The executor must attach the observation method and timestamp, and the spoken agent must never collapse unverified UI success into completion. When Accessibility/Screen Recording is false or a browser tab is on a failed page, automatically downgrade and offer a verification or retry packet.
- **owner gets:** The owner stops being told that something happened when the UI was unreachable and nothing changed. They get an honest next step instead of silently trusting a false completion receipt.
- effort: Medium: typed receipt schema, observation adapters for AppleScript/browser bridge, and routing policy changes; no hardware needed for the first version.  ·  risk: Some successful actions will be reported as unverified more often, which feels conservative. Recovery is a read-back probe or explicit retry; preserve the original job and receipt for audit.
- cost: Negligible API cost; one extra local read-back per high-impact action. No new hardware cost.  ·  latency: Adds 0.5–3 seconds for observation on actions that claim completion.
- security: Improves safety by preventing false claims; stores hashes and metadata rather than page secrets.
- depends on: Current Mac/browser observation probes and the existing receipt/undo records; A policy mapping UI reachability to verification strength

### `mac-harness` — Add a local egress-inspection layer that classifies outbound text, attachments, clipboard pastes, browser form submissions, and uploads before dispatch. It should return only a sensitivity class, destination identity, and redacted reason to the relay, while holding the original content on the Mac. Integrate a hard pause for high-risk destinations and a pendant-confirmed one-time override.
- **owner gets:** The owner avoids the most damaging everyday mistakes—sending a private document to the wrong person, pasting a credential into a web form, or uploading a work file to a personal account—without surrendering their private data to the cloud.
- effort: High: requires Mail/Messages/browser hooks, local classification, destination normalization, and a shared policy/override protocol.  ·  risk: False positives could interrupt harmless work. Recover with per-destination allowlists, category-specific thresholds, and an explicit temporary override; never silently drop content.
- cost: Low recurring API cost if classification is local; moderate engineering and storage cost for policy/version audit records.  ·  latency: Target under 150 ms for common pattern checks and under 1 second for model-assisted ambiguity.
- security: Strongly positive if raw content never leaves the Mac; the policy engine itself becomes security-critical and needs signed updates and tamper-evident logs.
- depends on: System-wide Mac and browser interception points; Local redaction/classification model; Pendant warning and override event transport; Destination identity normalization


## What it asked for

### `s11-q7yk` (skill) — physical_consent_latch
- does: When the relay sends a signed, short-lived approval challenge over the USB/serial link, the pendant flashes a distinct LED pattern, accepts exactly one deliberate button press, returns a signed nonce response, and locally rejects stale, repeated, or malformed challenges. It must not transmit microphone audio or reveal the action payload.
- must be on-device because: The owner needs a physical, offline-surviving confirmation boundary that cannot be satisfied by replaying a voice transcript or a server retry. The button and LED are only available on the pendant.
- trigger: Server push over serial, followed by the owner pressing the physical button; cancel on timeout or a second press.
- storage: No durable payload storage; retain only a 32-byte rolling nonce/hash and monotonic expiry in pendant flash or retained RAM, plus a tiny event record (<256 B).
- RAM budget: ~2 KB code/state and buffers, comfortably below the 211,608 B application RAM budget; use fixed-size buffers and never store page contents.

