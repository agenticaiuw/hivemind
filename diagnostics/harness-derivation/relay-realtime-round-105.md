# Harness derivation — relay-realtime — round 105

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Read the page I’m looking at to me on the pendant, let me ask questions or say “pause/skip back,” and when I return to my Mac leave that exact tab, scroll position, and reading state ready to continue."
- **useful because:** The owner is often away from the Mac but may have an important authenticated page open. This creates one continuous reading session across browser, relay, and wearable instead of forcing them to repeat context or lose their place. It is materially different from polling pages or producing a one-time summary: the pendant becomes a remote, conversational audiobook for the owner’s live browser context.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** Realtime model handles short spoken commands and grounded question answering over the current extracted page; a cheaper background model chunks and summarizes long page sections. The Mac planner/browser extension owns tab identity, scroll position, and resume state.
- **latency:** Acknowledge pause/skip commands in under 300 ms; begin playback or answer a page-grounded question within 2 seconds. Initial extraction may take up to 5 seconds for a large authenticated page.
- **cost:** About $0.01–$0.05 per active reading session for realtime turns, dominated by audio/model tokens; background chunking is inexpensive and should be cached per page revision.
- **security:** Authenticated page text leaves the Mac/browser and is sent to the relay/model, so the UI must show the active tab origin and provide an explicit stop/delete control. Never read password fields, hidden form values, or cross-origin frames. Resume state should be encrypted and expire automatically; questions and playback must stay bound to the tab/session that supplied the text.
- **missing:** A browser-extension command to capture the foreground tab as a readable, sanitized document with stable section IDs and scroll anchors; A low-latency audio queue supporting pause, resume, skip-back, and interruption from the pendant; A durable cross-surface reading-session record that synchronizes tab ID, revision hash, section position, and spoken history; A Mac-side resume action that re-focuses the original tab and restores its scroll position when the owner asks


## Changes it proposed to its own stack

### `integration` — Implement the granted schemas relay_route_intent and server_browser_actions as real, callable tools, backed by orchestrator routes with receipts and status. relay_route_intent should accept an intent label, utterance, and target, enqueue a job, and return a jobId plus a spoken acknowledgement. server_browser_actions should run a sandboxed browser session in the cloud for public pages, return extracted text/structured results, and record provenance. Both should integrate with relay_job_status and Mac/browser job queues where applicable.
- **owner gets:** From the pendant, the owner can ask for help and reliably get it routed, even when the Mac is asleep or the browser extension is offline. They hear a clear acknowledgement and can later ask what happened.
- effort: High. Requires orchestrator/backend work, job receipts, and a durable execution backend for browser actions.  ·  risk: Medium. Routing mistakes could send private tasks to the wrong place. Mitigate with explicit targets, strict input validation, and provenance logging.
- cost: Moderate API and compute cost; dominated by browser execution time and extraction complexity.  ·  latency: Adds some queueing for complex tasks; pendant response remains quick with spoken acknowledgement.
- security: High. Browser actions and intent routing touch sensitive data; require authentication, strict origin controls, and careful logging redaction.
- depends on: Durable job runner for routed intents and browser actions; Provenance/receipts support for actions and results

### `integration` — Add a first-class cross-surface ReadingSession protocol. The browser extension posts a sanitized, revisioned document manifest (tabId, origin, section IDs, text ranges, and scroll anchors) to the relay; the relay maintains a short-lived cursor and audio queue; pendant events (pause, resume, skipBack, question, stop) update that cursor; and the Mac harness consumes a signed resume command that re-focuses the originating tab only if its revision still matches. Emit receipts for every cursor transition and invalidate the session on tab close, origin change, or expiry.
- **owner gets:** The owner can start reading an authenticated page at the Mac, walk away, continue by voice on the pendant, and return to exactly the same place without exposing unrelated tabs or losing their place. It turns separate browser and audio plumbing into one dependable everyday interaction.
- effort: Medium-high: browser extension extraction and anchors, relay state/TTL and event handling, pendant audio queue integration, and a Mac resume adapter with revision checks.  ·  risk: A stale or incorrectly sanitized extraction could read the wrong content; mitigate with origin display, revision hashes, section citations, and hard invalidation on navigation. If the link drops, preserve only the last acknowledged cursor and replay idempotently; never auto-resume a changed page.
- cost: Small durable metadata cost and modest relay CPU; model/audio cost is usage-driven and can be reduced by caching page chunks by revision. No new hardware required.  ·  latency: Cursor controls can be local/relay-fast (<300 ms); first extraction and generated spoken chunks add roughly 1–5 seconds.
- security: Authenticated content is explicitly scoped to one tab and origin, with short TTL, encrypted-at-rest session state, and deletion on stop. Do not transmit password inputs, hidden fields, or arbitrary page DOM.
- depends on: A browser-extension capture/extraction adapter with stable section IDs and scroll anchors; A pendant audio queue with interruptible playback and control events; A relay endpoint that accepts typed ReadingSession events and returns signed, idempotent commands; A Mac adapter that validates revision and restores tab/scroll state


## What it asked for

_Nothing._
