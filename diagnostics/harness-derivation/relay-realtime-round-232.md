# Harness derivation — relay-realtime — round 232

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Keep an eye on my microphone and audio link quality during a conversation, and warn me if I’m likely to sound bad."
- **useful because:** The owner gets immediate feedback before a whole interaction is wasted due to clipping, packet loss, or bridge issues.
- **path:** pendant → bridge → relay
- **model tier:** Realtime model only for the spoken feedback; measurement should be on-device and in the bridge where the audio actually flows.
- **latency:** Continuous low-latency monitoring with brief spoken warnings (under a second) when thresholds are exceeded.
- **cost:** Very low. Mostly counters and rolling averages; only tiny summaries cross the network.
- **security:** Do not transmit raw audio. Only send metrics like packet loss, underruns, and clipping rate.
- **missing:** Expose live audio health counters from pendant and ESP32 bridge to the relay; Threshold configuration and adaptive guidance logic; A small on-device diagnostic request path to run targeted tests

### "If I say “remember this preference,” store it and use it later, but keep memory small and relevant to the task."
- **useful because:** This makes the assistant feel personal without becoming a context blob. Preferences persist and show up only when they help.
- **path:** relay → mac-bridge → memory
- **model tier:** Realtime to capture the preference in the moment; cheaper context projection to decide what to include later.
- **latency:** Under a second to acknowledge and store; no added latency during normal turns.
- **cost:** Low. Small preference facts with strict TTLs and token budgets.
- **security:** Preferences can reveal sensitive habits; store only what’s necessary, with clear scope and optional expiration.
- **missing:** Wire the existing memory projection into the live prompt assembly so preferences are injected correctly; A voice command grammar for preference capture and confirmation

### "“When this happens, do the thing I just described.” For example: when a new high-priority message appears in my authenticated browser, create a Mac reminder with its due date, and tell me on the pendant; let me pause or disable the rule by voice."
- **useful because:** It turns a one-shot voice request into a dependable cross-surface assistant: the browser session observes a private page, the relay evaluates the rule, the Mac performs the local action, and the pendant reports the result. Today each piece can be used manually, but no owner-defined event-to-action chain crosses them.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-terminal
- **model tier:** Use a cheap deterministic matcher for known page fields and a background model only to extract structured fields from changed content. Use the realtime model only for creating or editing the rule conversationally and for short spoken alerts.
- **latency:** Rule creation should feel conversational (under 5 seconds). After an observed change, alert within 30 seconds and perform the Mac action within 60 seconds; missed checks must be reported as unknown rather than silently treated as no change.
- **cost:** Near-zero for DOM diffs and rule evaluation; about $0.005–$0.03 per ambiguous extraction. Browser polling and Mac wake/transport are the dominant operational costs.
- **security:** Rules can act on authenticated private content, so store selectors and extracted values encrypted and scope each rule to one origin/session. Show the exact action and target during creation. Keep the owner's maximum-access policy, but provide voice “pause rule” and an immutable execution log. Never send page bodies to the relay when a local extractor can produce the needed fields.
- **missing:** A durable rule object that composes browser-watch diffs into typed Mac actions; A browser-extension trigger that can wake the relay on a real change rather than only being checked manually; A relay evaluator with deduplication, retry, and explicit unknown/error states; A Mac action executor that accepts extracted fields and reports a receipt; Rule lifecycle commands: list, pause, resume, edit, and delete by voice

### "“Put what we just discussed on my Mac.” The pendant should turn the current voice answer, links, decisions, and any relevant browser findings into a small visual workspace, open it on the Mac, and keep the pendant and screen synchronized when I say “next,” “highlight that,” or “send this.”"
- **useful because:** A wearable is excellent for capture but poor for inspecting lists, links, and details. This gives the owner a seamless voice-to-screen handoff instead of making them repeat the request at the keyboard, and it works across the relay, memory, browser session, and Mac.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** The realtime model extracts the requested handoff and a cheap background formatter builds deterministic HTML/Markdown. Use the Mac planner only for opening the workspace and browser extension only when authenticated source links need to be embedded.
- **latency:** Speak acknowledgement immediately; open a usable workspace within 3 seconds. Incremental additions should appear within 2 seconds.
- **cost:** Usually below $0.01: formatting and local persistence dominate, with no model call needed when the transcript and links are already structured.
- **security:** The workspace may contain private conversation and authenticated URLs. Keep it on the local Mac, use a random unguessable session URL, expire it after a short period, and never publish it to a public cloud page. Let the owner say “erase that workspace.”
- **missing:** A relay-owned handoff artifact with transcript, links, citations, and stable item IDs; A local Mac renderer that can open and update that artifact without exposing it publicly; Bidirectional pendant-to-screen focus events for next/highlight/send; A browser adapter that can attach authenticated findings without copying full page bodies to the relay

### "“Make me a private take-home packet from this.” The system should gather the selected voice conversation, relevant local files, and authenticated browser pages into a cited, expiring bundle on my Mac, then speak a short inventory and let me ask for one item at a time."
- **useful because:** The owner can currently ask separate agents to read or act, but cannot reliably leave a coherent, auditable artifact for later work. This turns an ephemeral wearable conversation into a useful deliverable without sending the owner's whole workspace to a third party.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension
- **model tier:** Use deterministic collection and hashing first; use a slower model only to summarize and label the collected material. The realtime tier should only resolve “this,” “that page,” and speak the final inventory.
- **latency:** Acknowledge under 1 second; begin collection immediately and provide a first item within 10 seconds. Large bundles may take several minutes, with progress delivered asynchronously.
- **cost:** $0.02–$0.20 depending on document volume and summarization; local file enumeration and browser extraction dominate data movement, not relay speech.
- **security:** Default to local-only output, include source paths/URLs and timestamps, redact credentials and cookies, and expire the bundle automatically. Never silently include unrelated files; speak the inclusion list before collection when scope is ambiguous.
- **missing:** A scope resolver that maps spoken references to concrete files, browser tabs, and transcript spans; A local bundle writer with manifest, hashes, citations, and expiry; A browser extraction adapter that exports readable content without session secrets; A relay job that can stream item-level progress and answer inventory questions after the voice turn


## What it asked for

_Nothing._
