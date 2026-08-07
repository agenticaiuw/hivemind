# Harness derivation — mac-planner — round 94

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **granted Mac read surfaces** — mac_read_sources and mac_readonly_inspect are granted only as schemas and return an implementation-missing error when called; they cannot currently provide Calendar/Mail or machine-state truth.
  - evidence: Parallel calls this round to both tools returned: 'This tool was granted a schema but has no implementation yet.'

## Capabilities it proposed

### "Pause what you’re doing on my Mac and continue it later—even if I close the laptop; when I say resume, tell me what changed and pick up without repeating work."
- **useful because:** Today an asynchronous Mac job can report a receipt, but there is no durable, cross-surface pause/resume contract that captures the desktop/browser state, detects stale context, and prevents duplicate mutations. This lets the pendant act as a reliable control surface for interrupted work rather than merely starting or checking jobs.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** Use the realtime model only to interpret the short pause/resume utterance and speak the result; use a cheaper background model to serialize the task capsule, compare state on resume, and summarize diffs. No model should infer success without a Mac receipt.
- **latency:** A pause acknowledgement under 2 seconds; capsule write under 5 seconds. Resume should return a stale-state check and spoken summary within 10 seconds, then execute only the remaining bounded actions.
- **cost:** Usually 1 short realtime turn plus 1–2 cheap background comparisons; roughly $0.01–$0.05 per pause/resume depending on browser extraction and context size. The dominant cost is re-reading changed private pages, not the capsule itself.
- **security:** Capsules must contain references and hashes by default, not page bodies or email contents; encrypt at rest, apply per-item TTL, and redact secrets. Resuming a high-impact or irreversible action must preserve the owner’s existing maximum-access policy but still emit an explicit before/after receipt. If browser extension is offline, do not claim a resume; queue it and report pending.
- **missing:** A durable task-capsule schema with step IDs, idempotency keys, precondition snapshots, expiry, and remaining actions; Mac read-only inspection implementation (the granted mac_readonly_inspect schema currently has no implementation) for foreground app, running apps, browser tabs, and directory state; Relay persistence and a resume endpoint that reconciles Mac job receipts with the capsule; Browser bridge support for reattaching the original tab/session and returning typed state diffs; A dashboard view for paused, stale, blocked, and completed capsules

### "Save this moment for me: keep the page I’m on, the relevant draft or selection, and why I cared, then let me reopen the same private workspace from the pendant later; erase it automatically after I’m done."
- **useful because:** The owner can start jobs and create notes, but cannot make a bounded, expiring bookmark of the exact cross-surface moment they are in. This would preserve the working set—not just a URL—across a logged-in browser tab, the Mac’s current document/draft, and a spoken intent, while avoiding a permanent personal-data archive.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** Realtime handles only the short capture/restore utterance. A cheaper background model extracts a one-sentence intent and ranks relevant fields; deterministic adapters collect URLs, tab IDs, app/document identifiers, selection hashes, and draft metadata. Never send full page or document bodies to the model unless explicitly requested.
- **latency:** Acknowledge capture in under 2 seconds and finish the local/browser snapshot within 8 seconds. Restore should show a compact preview within 5 seconds, then open only after the owner says restore/open.
- **cost:** About $0.005–$0.03 per capture/restore for a small intent extraction and optional diff summary; storage and browser IPC dominate, not inference.
- **security:** This may contain private URLs, drafts, clipboard selections, and account context. Store an encrypted capsule with field-level redaction, device-bound keys, explicit per-capsule TTL, and a visible list of captured fields. Do not capture passwords, tokens, full clipboard contents, or page bodies by default. Restoration must not submit, send, or mutate anything; if the original tab/session is gone, report that precisely and offer only the safe artifacts.
- **missing:** A new expiring workspace-capsule primitive, distinct from a job: field manifest, encrypted payload, provenance, TTL, and one-time restore semantics; A foreground/document/selection adapter on Mac that works without relying on arbitrary shell and reports unavailable fields honestly; Browser bridge support for exporting and reattaching a specific private tab’s safe state (URL, tab ID, semantic anchors, and redacted draft metadata); Pendant-side capture and restore affordances (button/voice confirmation and a short spoken capsule name); A dashboard showing exactly which fields were captured, remaining TTL, and a destructive erase control

### "Before you use my private Mac or logged-in browser, tell me exactly what information would leave the device, let me remove any fields by voice, and then do the task with the redacted version."
- **useful because:** The owner has maximum-access automation but no usable, per-request data-egress preview. This gives them a practical privacy control that is narrower than blocking automation: they can inspect and edit the context packet before the relay/model/browser receives it, including fields the system would otherwise silently infer from tabs, mail, calendar, or documents.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** A deterministic local classifier builds the candidate field manifest; a cheap background model labels fields and explains them. Realtime is used only for the owner’s brief spoken edits and confirmation of the final manifest. Sensitive values remain local unless included in the final approved packet.
- **latency:** Generate the manifest in 2–5 seconds for a normal task, speak a 10-second summary, and apply voice redactions immediately. The actual task starts only after the edited manifest is available; no extra model turn is needed for unchanged fields.
- **cost:** Approximately $0.002–$0.02 per request; most work is local field extraction and serialization. Cost rises only when the owner asks for a natural-language explanation of many fields.
- **security:** The preview itself is sensitive and must be rendered locally when possible; store only a hash and policy decision, not the unredacted manifest. Default to URLs/titles/selected snippets rather than bodies, mask credentials and tokens unconditionally, and record exactly which fields were permitted. This is an informational control, not a promise that a third-party page cannot observe its own browser interaction.
- **missing:** A context-egress manifest protocol with field IDs, source, sensitivity, byte count, destination, TTL, and redaction state; Local extraction hooks for Mac documents, Calendar/Mail reads, and authenticated browser tabs; A relay ingress that accepts only the approved manifest and rejects undeclared fields; Pendant UI/voice grammar for 'remove the email body', 'allow this tab title', and 'show me the rest'; Dashboard audit view linking approved fields to job and browser receipts


## What it asked for

_Nothing._
## Its own summary

This round established a concrete implementation gap: the newly granted mac_read_sources and mac_readonly_inspect tools are schema-only and both fail with an implementation-missing error. I recorded that finding. I proposed a cross-surface pause/resume task capsule (pendant → relay → Mac/browser) that preserves step IDs, preconditions, receipts, and state diffs so interrupted work can resume without duplicate actions; it was recorded as connective work but flagged as close to an existing backlog item. I still need the host implementations of the two read-only tools, especially typed permission/partial-result envelopes; accessibility and Screen Recording remain unavailable, so UI snapshots must stay explicitly unavailable until the owner grants TCC permissions.

**Biggest unknown:** Whether the orchestrator will implement the granted read-only Mac tools this round; until then I cannot truthfully inspect Calendar/Mail, foreground apps, browser tabs, or directory state, and any resume workflow must rely on existing job/browser receipts only.

