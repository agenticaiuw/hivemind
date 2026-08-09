# Harness derivation — mac-planner — round 289

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-device-status** — The Mac bridge is online, Safari has one online tab, while the nRF9160 pendant and iOS probe devices are offline; USB bench work is therefore the immediate actionable pendant path, not LTE assumptions.
  - evidence: discover(category='devices') returned home-macbook-bridge online, Safari on MacIntel online, nrf9160-pendant offline, and iOS probes offline.

## Capabilities it proposed

### "When I press the pendant's bookmark during a meeting, turn that moment into a durable follow-up tied to what was on my Mac, and put the right next action in tomorrow's brief."
- **useful because:** A bookmark today is only a timestamp. Correlating it with the active document, browser tab, calendar event, and nearby notes makes the pendant a one-press capture tool that produces an actionable follow-up instead of another orphaned memory.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background model for correlation and draft generation; realtime only for the spoken acknowledgement.
- **latency:** Acknowledge locally immediately; capture Mac/browser context within 10 seconds; include the follow-up in the next brief.
- **cost:** About $0.01-$0.05 per bookmark depending on context size; Mac/browser reads and durable event storage dominate, not the short acknowledgement.
- **security:** Active tab title, document path, calendar metadata, and note snippets leave the Mac only after redaction. Never capture page bodies or secrets by default. Draft follow-ups but require confirmation before sending mail or creating external tickets.
- **missing:** A relay consumer that joins offline_moment_bookmark events to a time-windowed Mac/browser context snapshot; A privacy/redaction policy for context fields and a durable bookmark-to-follow-up relation; A next-brief query that ranks unresolved bookmark follow-ups

### "Run a complete pendant bench check from my Mac, prove the audio and radio path meet their numeric targets, and leave me a small report plus a playable result without making me read UART logs."
- **useful because:** The pendant is physically connected over USB today but unregistered on LTE. This turns that otherwise awkward bench state into a useful, repeatable health check: it can distinguish firmware/audio regressions from network failures and give the owner a human result.
- **path:** pendant → mac-bridge → relay → dashboard
- **model tier:** Cheap background model parses bounded diagnostic output and writes the report; no realtime model is needed.
- **latency:** Start within 5 seconds and finish in under 2 minutes; show progress locally and leave a receipt even if the serial link drops.
- **cost:** Under $0.02 per run; almost all cost is local execution and artifact storage.
- **security:** Only synthetic fixtures, counters, and firmware version leave the Mac; never upload microphone data. The command must be an explicit allowlisted diagnostic invocation, with output size and runtime bounds. A failed test must not flash or mutate firmware.
- **missing:** A first-class bounded USB-serial diagnostic executor that can invoke the shipped audio_path_diagnostic_fixture and return exit status, timestamps, and capped logs; A relay evaluator for alias rejection, codec CPU, mic_drops, and tx_starved acceptance thresholds; A receipt that links the serial run, generated report, and playable synthetic fixture

### "If I ask you to do a long Mac task and walk away, finish it safely, survive a dropped connection, and leave a concise completion or failure card on the pendant that tells me exactly what changed."
- **useful because:** The Mac can act while the owner is absent and the pendant can reach them later, but today those surfaces do not form one durable handoff. This makes unattended work trustworthy: no duplicate retries, an atomic desktop result, and a physical notification that survives link loss.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Background planner for decomposition and summarization; deterministic workbench and receipt code for execution. Realtime is unnecessary.
- **latency:** Queue immediately, execute in the background, and surface a completion card within 3 seconds of the final receipt; retries resume without restarting completed stages.
- **cost:** Usually under $0.05 per job; model planning and final summarization dominate, while transaction and receipt handling are local.
- **security:** The job must declare touched paths/apps and redact file contents from the pendant card. Destructive actions retain the owner's existing confirmation policy. Never claim success without a verified receipt; expire stale cards and provide a local cancel path.
- **missing:** A relay job coordinator that binds a server job_id to a mac_workbench_transaction and its receipt; A durable pendant inbox payload type for structured completion cards with success, failure, changed resources, and retry state; A resumable Mac executor that checkpoints between actions and reports idempotency keys; A spoken-card renderer that summarizes receipts without leaking file contents

### "Before you change anything in a logged-in website, read the page, tell me in one sentence what will happen, and let me approve or cancel from the pendant; after approval, execute it and report the result."
- **useful because:** It gives the owner a safe voice-controlled bridge into authenticated browser sessions without exposing credentials or requiring the owner to return to the Mac. Unlike a generic action policy, this is a concrete browser transaction with a preview, a short-lived approval, and a result.
- **path:** pendant → relay → browser → mac-bridge → dashboard
- **model tier:** Realtime model only for the short spoken preview and approval turn; deterministic browser inspection, action staging, and result verification do the rest.
- **latency:** Page inspection and preview in 3 seconds; approval token valid for 60 seconds; execute and verify within 10 seconds.
- **cost:** Roughly $0.01-$0.04 per transaction; page extraction and the realtime approval turn dominate.
- **security:** Never speak or send passwords, tokens, or full page bodies. Bind approval to the exact tab, URL, action arguments, and a content hash; cancel if the page changes. Keep destructive-site actions (send, purchase, delete) explicitly confirmable and log only redacted receipts.
- **missing:** A browser-specific preview endpoint that converts a proposed click/type/submit into a deterministic effect summary; A short-lived approval binding to tab identity, URL, and page hash; Post-action verification and a compact pendant result card; A browser harness policy separating read/navigation from submit/delete/purchase

### "Mark this meeting, project, or conversation as temporary and have every node automatically forget its derived context at the deadline—Mac notes, browser captures, relay memory, queued audio, and pendant cards—with a proof that nothing retained it."
- **useful because:** Today privacy controls mostly stop capture; they do not give the owner a reliable, cross-surface expiration promise. This would let the owner use the system for sensitive work without having to remember which agent, cache, draft, or queued card might still contain it.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic retention ledger and deletion workers; a cheaper background model may classify derived artifacts, but deletion and proof must not depend on model judgement.
- **latency:** Apply the temporary scope immediately; deletion at the deadline within 1 minute; show a compact deletion receipt on the pendant or dashboard.
- **cost:** Low ongoing cost; the dominant expense is encrypted metadata and periodic deletion verification, not inference.
- **security:** Deletion must cover raw audio, transcripts, embeddings, browser snapshots, Mac drafts, logs, and backups where technically possible. Use per-scope encryption keys and destroy the key first, then scrub reachable copies. Report exceptions honestly instead of claiming erasure. The owner must explicitly choose the deadline and whether external sites are in scope.
- **missing:** A cross-node retention ledger assigning every artifact and derivative to an expiring scope; Per-scope encryption/key destruction for relay storage and queued audio; Mac and browser sweepers that honor expiration without deleting unrelated owner files; A verifiable erasure receipt with exceptions and last-seen copies

### "Before I act on an important document or send a response, check the relevant local files, calendar, and authenticated browser page for contradictions or stale facts, then tell me exactly what needs verification."
- **useful because:** The owner can currently read each surface separately, but the dangerous failure is cross-surface inconsistency: an old local draft, a changed web record, and a calendar commitment can all look plausible in isolation. A provenance-aware contradiction check prevents confident action on stale context.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background model extracts claims and compares them; realtime is used only to speak the short warning when the owner is about to act.
- **latency:** Return a bounded check in 5 seconds for a selected document/page; never block ordinary reading, but surface a warning before a send or submit action.
- **cost:** About $0.02-$0.10 per check depending on document and page size; claim extraction is the main cost.
- **security:** Transmit only selected excerpts and structured claims, not whole documents. Preserve source URLs, timestamps, and hashes. Treat private browser content as sensitive and never include secrets in the spoken warning. The system must distinguish contradiction, missing evidence, and mere uncertainty.
- **missing:** A claim/provenance graph spanning Mac files, calendar, and authenticated browser state; A bounded pre-action hook for send/submit operations that can pause only when the owner has opted into this check; A deterministic freshness and conflict report with source citations and page/document hashes

### "Undo the last thing you did for me across the Mac and browser, even if it involved several steps, and show me what could not be reversed before doing anything else."
- **useful because:** Today an action may touch a file, browser form, shortcut, and generated draft, while undo support is fragmented and often unavailable. A cross-surface undo plan would make delegation materially safer: the owner can recover from a mistaken multi-step operation without reconstructing it manually.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic action ledger and compensating operations; a background model can explain the recovery plan, but it must not invent reversals.
- **latency:** Identify the latest completed transaction in 2 seconds; present the recovery plan immediately; execute reversible steps within 10 seconds after confirmation.
- **cost:** Low model cost, roughly $0.01-$0.03 per undo; the engineering cost is maintaining compensating operations and durable receipts.
- **security:** Undo must never silently delete or overwrite. Show an exact touched-resource list and irreversibility exceptions. Bind undo to the original job and resource versions, refuse if a human changed the resource since execution, and retain an audit receipt.
- **missing:** A unified cross-surface action ledger with resource versions and causal transaction IDs; Compensating operations for browser mutations, files, shortcuts, and generated artifacts; Conflict detection when the owner or another app changed a touched resource after the original action; A pendant-friendly undo preview and confirmation protocol


## What it asked for

### `t23-46jv` (tool) — browser_effect_preview
- why: The owner needs a browser-specific, read-only preview before approving a logged-in-site mutation from the pendant. Existing browser inspection reads pages, but it cannot deterministically describe the effect of a proposed click/type/submit or bind that preview to the exact tab state.

```json
{
  "type": "object",
  "properties": {
    "session_id": {
      "type": "string"
    },
    "action": {
      "type": "string",
      "enum": [
        "click",
        "type",
        "select",
        "submit",
        "navigate"
      ]
    },
    "target_ref": {
      "type": "string"
    },
    "text": {
      "type": "string"
    },
    "url": {
      "type": "string"
    },
    "redact": {
      "type": "boolean"
    },
    "ttl_seconds": {
      "type": "integer",
      "minimum": 10,
      "maximum": 300
    }
  },
  "required": [
    "session_id",
    "action"
  ]
}
```

