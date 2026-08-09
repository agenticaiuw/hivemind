# Harness derivation — mac-planner — round 228

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I press the pendant's bookmark button, save exactly what I was doing on the Mac so I can later ask, "What was I in the middle of?""
- **useful because:** Interruptions currently destroy context. A physical bookmark plus a Mac/browser snapshot would create a reliable, time-stamped breadcrumb without requiring speech or a carefully worded command, and the relay could answer later with the active app, page, calendar proximity, and the unfinished artifact.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for capsule assembly and deduplication; realtime only for the later one-sentence spoken answer
- **latency:** LED acknowledgement immediately; Mac/browser snapshot under 3 seconds; later answer under 1 second from stored capsule
- **cost:** About $0.01-$0.04 per bookmark when summarization is needed; most bookmarks use a cheap structured record and no model call
- **security:** Capture only foreground app, active URL/title, selected calendar event, and workspace paths; redact page bodies and passwords by default. The owner should configure retention (for example 14 days) and whether browser titles may leave the Mac. No destructive action occurs.
- **missing:** A relay endpoint that atomically accepts a pendant bookmark plus a Mac/browser evidence capsule; A structured context-capsule schema and a later retrieval route; existing /capture is not documented as this joined record; A USB-connected pendant event forwarder while LTE registration is absent

### "Turn your answer into a real draft in my AI-Pendant-Workspace, open it in VS Code, and tell me exactly which files were created."
- **useful because:** The owner should not have to copy spoken output into an editor. The relay can compose while the Mac performs the local write, and an atomic transaction plus receipt makes the result trustworthy across retries: either the complete draft exists or it does not, with paths and hashes spoken back.
- **path:** relay → mac-bridge → mac-planner → dashboard → pendant
- **model tier:** background model for drafting and metadata extraction; realtime only for accepting the short command and confirming completion
- **latency:** A small draft in 5-15 seconds; transaction commit and VS Code open in under 2 seconds after generation; immediate failure receipt if the workspace is unavailable
- **cost:** Roughly $0.02-$0.15 depending on draft length; Mac actions and hashing dominate wall time, not API cost
- **security:** Write only beneath the owner-configured workspace root; never overwrite an existing path without an explicit versioned filename. Preview file names and hashes before opening. Do not send unrelated workspace contents to the relay; allow the owner to request local-only drafting.
- **missing:** A server-side plan format that carries generated file manifests and expected SHA-256 values into the Mac transaction tool; A stable spoken receipt route that links the pendant response to the workbench job ID; A workspace policy setting for overwrite/versioning and local-only content

### "Save this page as a cited local note, including the exact title, URL, access time, and the claims you extracted; if the page changes later, show me what changed."
- **useful because:** A browser answer disappears into chat and cannot be audited. This creates a local, dated evidence record while the authenticated browser can see the page and the Mac can store it. Later comparison turns a one-off lookup into a durable change detector, useful for documentation, purchases, and monitored web pages.
- **path:** browser → relay → mac-bridge → mac-planner → dashboard → pendant
- **model tier:** background model for claim extraction and diff summarization; no realtime model after the initial command
- **latency:** Capture and local note in 5 seconds for a normal page; future checks in the background, with a one-sentence pendant alert only when cited claims materially change
- **cost:** About $0.01-$0.08 per capture/check depending on page length; browser transfer and local hashing dominate, and unchanged pages can avoid model calls
- **security:** Keep authenticated page bodies on the Mac unless the owner explicitly enables relay analysis; redact account identifiers and hidden form values. Store only the requested URL by default, respect robots/access rules, and require confirmation before visiting a new domain or triggering a download.
- **missing:** A browser command for bounded page capture with stable content hashing and explicit redaction; A local cited-note writer that stores source metadata and claim hashes without overwriting prior versions; A scheduled diff route that can re-check a previously authorized URL and deliver only material changes

### "Fill out this form using my private notes, but do not send any of the note contents to the relay; show me a field-by-field preview on the pendant and submit only after I say yes."
- **useful because:** The browser can reach authenticated forms and the Mac can hold local notes, but today there is no safe way to combine them without exporting sensitive values into the server conversation. This would make voice-controlled form completion practical for applications, travel, and reimbursements while keeping secrets local and making the final submission explicit.
- **path:** pendant → relay → mac-bridge → browser → mac-planner → dashboard
- **model tier:** Realtime model only for intent and field mapping; local Mac rules or a small background model should select note values and redact them before any relay response
- **latency:** Field discovery and local mapping in 3-8 seconds; preview on pendant within 2 seconds after mapping; submit immediately after spoken confirmation
- **cost:** $0.01-$0.05 per form for intent mapping; page interaction and local extraction dominate, with no sensitive field contents sent to the model
- **security:** Values remain on the Mac. Return only field labels, masked previews, and validation status to relay/pendant. Never submit without a fresh confirmation tied to the exact URL, field hashes, and masked values. Block password, payment, and identity fields unless separately enabled.
- **missing:** A browser-side local extraction/fill command that accepts field selectors and values without returning page contents; A Mac-local secret broker for selecting values from approved notes and masking them in receipts; A pendant confirmation payload that binds approval to a specific form snapshot and destination

### "Erase everything this website or conversation taught you about me, everywhere you can reach, and give me a proof that each copy is gone."
- **useful because:** Today deletion is fragmented: browser state, Mac notes, relay memory, captures, and pendant queues have different owners and no shared erasure receipt. A single spoken revocation would let the owner withdraw a sensitive interaction instead of trusting that one surface was cleared while another retained it.
- **path:** pendant → relay → mac-bridge → browser → mac-planner → dashboard
- **model tier:** Realtime model only to resolve which interaction/site the owner means; deterministic background deletion and receipt generation should perform the actual work
- **latency:** Acknowledge locally in under 1 second; clear reachable copies in under 10 seconds; report unresolved/offline surfaces immediately and retry them later
- **cost:** Under $0.01 per request; deletion, indexing, and signed receipts dominate rather than model inference
- **security:** Require a narrowly bound target (site, conversation, date range, or capture ID), never interpret 'everything' silently. Delete browser session data, relay memory/captures, local files, and pending pendant records only within that scope. Keep a minimal tombstone and cryptographic deletion receipt without retaining content. The owner must confirm irreversible deletion.
- **missing:** A cross-surface data lineage index linking relay events to Mac files, browser sessions, and pendant queue records; Idempotent deletion endpoints on relay, Mac, and browser with a common tombstone ID; A signed, user-readable erasure receipt and retry state for offline pendant or disconnected Mac surfaces

### "Queue this command on the pendant and carry it out on my Mac when the link comes back, but only if it is still safe and relevant; expire it tomorrow if not."
- **useful because:** The owner can speak while walking away from connectivity and currently loses the intent. A durable, expiring command envelope would let the pendant capture intent offline, let the relay validate it later, and let the Mac execute it only against a fresh observed state rather than blindly replaying stale actions.
- **path:** pendant → relay → mac-bridge → mac-planner → dashboard
- **model tier:** Realtime model for the initial intent normalization; background model for later relevance checking; deterministic Mac preflight and execution for the final action list
- **latency:** Offline acknowledgement immediately; relay validation on reconnect under 5 seconds; Mac execution after fresh state check under 5 seconds, otherwise a pendant alert explaining why it was held
- **cost:** $0.01-$0.08 per queued intent depending on later interpretation; storage and state checks dominate
- **security:** Persist only an explicit, bounded action plan, target scope, expiry, and required conditions—not raw ambient audio. Never replay destructive actions unattended; require a new confirmation for sending, deleting, purchasing, or external publication. Cancel locally with the privacy latch or button and show expiry/blocked states on the single LED.
- **missing:** A pendant-to-relay durable intent envelope distinct from audio/inbox records; A relay relevance/expiry evaluator that can invalidate stale plans when calendar, browser, or Mac state changes; An execution lease on the Mac that binds the plan to a fresh mac_action_preflight result and produces an idempotent receipt


## What it asked for

_Nothing._
## Its own summary

This round produced three non-identical cross-node capabilities: (1) a physical pendant bookmark that later reconstructs interrupted Mac/browser work, (2) atomic voice-to-workspace drafting with VS Code opening and file/hash receipts, and (3) authenticated-page evidence capture into versioned cited local notes with future material-change alerts. I also gave mac-vision the current planning, preflight, verification, and TCC constraints.

**Biggest unknown:** The missing server contracts are still the limiting factor: there is no confirmed joined pendant-bookmark/context-capsule route, no browser bounded-capture+content-hash command, and no explicit plan-to-workbench file-manifest handoff. I also still lack owner-granted macOS Accessibility/Screen Recording, though the proposed workflows can degrade to AppleScript/browser metadata until that is granted.

