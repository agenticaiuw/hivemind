# Changes the agents proposed

Written by `scripts/harness-ledger.mjs`. Status is owned by this file and
survives re-runs — refreshing adds new proposals, it never resets what you
have already marked done.

**59 open · 59 implemented · 73 other**

The `×` column counts how many times a proposal was made. Anything above 1
was arrived at independently more than once, which is the strongest signal
in here.

## Open

| id | layer | proposed by | × | change |
| --- | --- | --- | --- | --- |
| `chg-a813b918` | relay | mac-planner | 11 | Enable a bounded audio-retention sweeper and per-job deletion controls: default to short retention for generated briefings, delete expired R2 objects  |
| `chg-16bc5dee` | browser-harness | browser-extension | 10 | Add a durable browser job runner with two backends: the authenticated Safari bridge for owner-private pages and Cloudflare Browser Run for public page |
| `cap-bff5f829` | capability | browser-extension | 10 | Check my logged-in web accounts for anything urgent, summarize it, and draft (but do not send) any replies that need my attention. |
| `cap-8c36c70a` | capability | browser-extension | 10 | Every weekday morning, check my logged-in calendar, task board, and travel reservations, then tell me the three things I need to know and prepare a su |
| `cap-5bd640c5` | capability | mac-planner | 10 | Watch my chosen logged-in web pages once a day and tell me only what changed; prepare drafts for any follow-up forms, but stop before submitting. |
| `chg-a82e0b13` | memory | mac-planner | 10 | Replace per-surface hand-written fleetContext prompt sections with a compact, typed context service that returns only task-relevant facts, each with s |
| `cap-4f5af34d` | capability | mac-planner | 9 | Check my authenticated browser accounts for anything that needs my attention, then put findings in a review queue instead of changing anything. |
| `chg-18a9c60f` | memory | mac-planner | 9 | Replace hand-written per-surface fleetContext prompt sections with a single typed context service that stores compact facts, provenance, sensitivity,  |
| `chg-0096a2b3` | memory | mac-planner | 9 | Replace per-surface hand-written fleetContext prompt sections with a shared, typed context compiler: retrieve only task-relevant entities/relations, a |
| `chg-14accc01` | browser-harness | browser-extension | 6 | Add a reliable browser command queue with request IDs, idempotency keys, tab/session affinity, typed results (page metadata, extracted text, screensho |
| `cap-a624ca3e` | capability | browser-extension | 6 | Every morning, check my private calendar, travel reservations, and important account notifications in Safari, then give me a concise spoken briefing w |
| `cap-b875c138` | capability | browser-extension | 6 | Draft a form, email, or support request from information on this private webpage, fill it in, and show me exactly what will be submitted before I appr |
| `cap-a09b223f` | capability | browser-extension | 6 | Watch my authenticated order, appointment, and account pages for changes, and tell me only when a meaningful change happens—never pollute my daily bri |
| `chg-498a3489` | memory | mac-planner | 6 | Replace per-surface hand-written fleetContext prompt sections with a compact, typed context projection service: durable facts, current goals, and perm |
| `chg-e767dfc0` | browser-harness | browser-extension | 3 | Build a first-class authenticated page-watch service: each watch stores URL/tab context, extraction selectors or semantic regions, a normalized baseli |
| `chg-5284a6ce` | browser-harness | browser-extension | 3 | Build a durable authenticated page-watch service: named watch definitions store URL/tab/session binding, extraction selectors or an agentic extraction |
| `chg-e14fff33` | browser-harness | browser-extension | 3 | Add a provenance-aware browser workbench: every extraction and field mutation gets a tabId, URL, timestamp, DOM locator, source snippet hash, action p |
| `chg-fa84f9a7` | browser-harness | browser-extension | 3 | Build a durable authenticated page-watch layer: named browser sessions with tab/window reattachment, per-watch cadence and quiet hours, DOM-region ext |
| `cap-0c8c5dfe` | capability | browser-extension | 3 | Watch the authenticated pages I choose, detect meaningful changes, and leave me a concise, sourced briefing with suggested next steps—without sending  |
| `cap-391cae82` | capability | browser-extension | 3 | When I ask about something on a logged-in site, have several agents inspect it in parallel, reconcile their findings, and give me an evidence-backed a |
| `cap-7217b17c` | capability | browser-extension | 3 | Prepare a browser transaction for me: gather the relevant logged-in data, fill the form or draft the message, show me exactly what will change with be |
| `cap-0d11cf82` | capability | browser-extension | 3 | Every weekday morning, check my authenticated work portal for new high-priority items and tell me only what needs my attention. |
| `cap-df9ec55e` | capability | browser-extension | 3 | When I say 'handle this' about something I found in Safari, gather the needed details across my logged-in tabs, fill the reversible parts, and show me |
| `cap-302a8868` | capability | browser-extension | 3 | “Every morning, check my logged-in work dashboards and tell me only what changed or needs my attention; keep watching the important pages and alert me |
| `cap-4b41e08a` | capability | mac-planner | 3 | While I sleep, investigate my open threads across Calendar, Mail, and authenticated browser tabs, then leave a ready-to-review workbench on my Mac whe |
| `cap-26c609fc` | capability | mac-planner | 3 | “When I ask you to do something that takes time, keep working after I leave and tell me exactly what happened when it’s done.” |
| `cap-a267b7e8` | capability | mac-planner | 3 | “Just give it the goal; figure out whether the Mac, browser, pendant, or server should do each part, and use whichever can.” |
| `cap-ca6005c3` | capability | mac-planner | 3 | “While I sleep, prepare tomorrow’s brief and leave me a short audio queue I can listen to from the pendant.” |
| `cap-51c2dc88` | capability | mac-planner | 3 | “Get me ready for my next meeting.” |
| `cap-a4c0ec8d` | capability | mac-vision | 3 | Turn on mac-vision's accessibility-mode UI interaction loop to automate GUI tasks without taking over the screen or keyboard focus. |
| `cap-a1aa3bf5` | capability | mac-vision | 3 | Show me a history of recent actions taken by mac-vision in automation loops with human-readable explanations and option to undo. |
| `cap-e21eb7f4` | capability | relay-realtime | 3 | “Every morning, give me a 30-second audio digest of what changed: calendar, reminders, and top emails.” |
| `cap-72fc9997` | capability | relay-realtime | 3 | "Queue this up and tell me when it’s done" (for example: summarize a long document, compare options, draft an email, or research a topic). |
| `cap-e5132197` | capability | relay-realtime | 3 | “When I press the pendant button, capture a short voice note, tag it with time and place if available, and later summarize it into tasks.” |
| `chg-9a6740ed` | context | mac-planner | 3 | Add a compact, durable Mac execution context cache and handoff protocol. Each server plan gets a jobId, parentId, monotonic sequence, intent hash, ref |
| `chg-f5d3b820` | hardware | mac-planner | 3 | Replace the desk-bound nRF9160 DK prototype with a jewelry-sized cellular/BLE pendant built around an nRF9161-class modem/application module plus a lo |
| `chg-258cbe5e` | hardware | mac-planner | 3 | Build the wearable revision around the nRF9160 with an ultra-low-power 6-axis IMU on the unused I2C bus, a vibration/LRA haptic driver, and a real mic |
| `chg-d9ce5471` | hardware | mac-vision | 3 | Add a dedicated low-power vision coprocessor or embedded GPU to the pendant hardware for on-device image analysis to recognize Mac screen contents and |
| `chg-a3af4c67` | integration | browser-extension | 3 | Define a cross-node Evidence Capsule protocol for browser results: immutable capsule ID, source URL/domain, capture time, tab/session identifier (pseu |
| `chg-91f3c214` | integration | mac-vision | 3 | Integrate mac-vision with the Cloudflare Worker relay to allow partial offloading of UI state classification and action suggestion to a cloud tier. Th |
| `chg-622e7336` | integration | relay-realtime | 3 | Wire up a server-side browser path using Cloudflare Browser Run and a routing rule: web reads/extraction default to server_browser_actions; only fall  |
| `chg-a7a155b1` | integration | relay-realtime | 3 | Use the new server-side browser capability for public web tasks directly from the relay, reserving the Mac harness for authenticated sessions and loca |
| `chg-d2c2cc02` | mac-harness | mac-planner | 3 | Add an idempotent Workbench transaction primitive to the Mac planner: accept a job_id and manifest, write all outputs into a temporary directory, fsyn |
| `chg-9596a2ad` | memory | mac-planner | 3 | Replace fleetContext.js's hand-written per-surface prompt section with a shared event log plus typed projections. Every node writes small signed event |
| `chg-5cc0bd50` | memory | mac-planner | 3 | Replace per-surface hand-written fleetContext prompts with a shared, event-sourced personal memory broker. Every node writes typed facts, preferences, |
| `chg-2903dddb` | memory | relay-realtime | 3 | Unify memory across surfaces: replace hand-written prompt sections per surface with a shared, versioned memory API that returns small, purpose-built s |
| `chg-7613a731` | memory | relay-realtime | 3 | Introduce a unified, cross-node memory write API with schema (entities, events, preferences, tasks) and TTLs, plus a pruning policy. Replace hand-writ |
| `chg-67952158` | routines | relay-realtime | 3 | Add a real scheduler: a Durable Object-backed job queue with delayed execution and recurring rules (cron-like). The relay can enqueue jobs, and a work |
| `chg-9b4366c7` | routines | relay-realtime | 3 | Add a relay-owned durable work queue with retries and a receipt log, implemented as a Durable Object (or D1 + Durable Object alarms). The relay expose |
| `chg-ae7e4af5` | routines | relay-realtime | 3 | Introduce a lightweight scheduler using Durable Object alarms or Cloudflare Cron to trigger queued jobs (summarize notes, send digests, retry failed u |
| `chg-9ffe4cd1` | browser-harness | browser-extension | 1 | Add a browser-bridge self-healing lease protocol: each Safari heartbeat carries a device nonce, extension version, tab inventory, and last-applied com |
| `cap-951c7f45` | capability | browser-extension | 1 | “Check my logged-in accounts for inconsistent personal details, upcoming expirations, or duplicate subscriptions, and prepare a concise fix list witho |
| `cap-c67d4f1e` | capability | relay-realtime | 1 | “I asked you to handle that on my Mac—what’s the status?” |
| `chg-99e3117a` | context | relay-realtime | 1 | Introduce a typed, minimal context service for the relay: given an utterance and a desired outcome (status query, dictation, mac task), return only re |
| `skill-20934f8c` | firmware | browser-extension | 1 | offline_alert_inbox |
| `skill-25e4ff13` | firmware | mac-planner | 1 | offline_moment_bookmark |
| `skill-feb6116a` | firmware | relay-realtime | 1 | offline_voice_memo_store_and_forward |
| `chg-44e46c8d` | mac-harness | mac-planner | 1 | Add a focus-safe execution coordinator around the existing FULL_CONTROL Mac executor. Before each plan, capture the foreground app and a lightweight a |
| `chg-31bcbfca` | mac-harness | mac-planner | 1 | Add a startup and periodic no-op input reachability probe to the Mac agent health path. When Accessibility is reported trusted, post the documented ze |

## Implemented

| id | layer | proposed by | × | change |
| --- | --- | --- | --- | --- |
| `cap-d65785c8` | capability | browser-extension | 12 | “Read the relevant pages in my open browser tabs, compare the options, and give me a short brief with links and any deadlines.” |
| `cap-9764ec65` | capability | browser-extension | 12 | “Research this topic across the public web, check the sources, and send me a cited answer later.” |
| `cap-1e04349c` | capability | browser-extension | 12 | “Fill out this web form from the information I give you, stop before submission, and show me exactly what will be sent.” |
| `cap-c18a0fce` | capability | browser-extension | 12 | Watch this logged-in page or price/availability page and tell me only when the specified condition changes. |
| `cap-75ee1730` | capability | browser-extension | 12 | Fill out this online form using the details we discussed, stop before the final submit, and show me exactly what will be sent. |
| `cap-eb3ab088` | capability | browser-extension | 12 | “Check my authenticated work sites and inboxes for anything urgent, summarize it, and leave me a short audio briefing.” |
| `cap-28eaa582` | capability | browser-extension | 12 | “Fill out this web form from my notes, but stop before submitting and show me exactly what will be sent.” |
| `cap-ea762950` | capability | browser-extension | 12 | “Watch this authenticated page and tell me when the status, price, or availability changes.” |
| `cap-fb442a50` | capability | mac-planner | 12 | “Every morning, check my calendar, unread email, and today’s files, then give me a short spoken brief with the meetings that need preparation and a pr |
| `cap-2a60c5ba` | capability | mac-planner | 12 | “Research this topic and leave me a concise source-linked briefing on my Mac, with an audio version I can play later.” |
| `cap-c071fa0a` | capability | mac-planner | 12 | “Every morning, give me a concise briefing of today’s calendar, unread priority messages, weather, and the files I need for my first meeting; let me a |
| `cap-0fee609c` | capability | mac-planner | 12 | “Prepare me for my next meeting: find the agenda and related local documents, summarize the open decisions and prior action items, and put the three m |
| `cap-70db8ef3` | capability | mac-planner | 12 | “When I say ‘prepare my workday’, check my calendar and inbox, make a concise brief, and put it in a note on my Mac; don't send anything.” |
| `cap-0e0b8d35` | capability | mac-planner | 12 | “Clean up my Downloads: group files by type into folders and show me what will be moved before doing it.” |
| `cap-23af3e85` | capability | mac-planner | 12 | “Every weekday at 5 pm, summarize the notes I created today into three next actions and put them in my task app; never send messages.” |
| `cap-5dbbe6df` | capability | relay-realtime | 12 | “Summarize what I missed in my email today.” |
| `cap-0e994cfb` | capability | relay-realtime | 12 | “Read my upcoming schedule for the day.” |
| `cap-2d29628a` | capability | relay-realtime | 12 | “Save this idea for later.” |
| `cap-1634d96f` | capability | relay-realtime | 12 | “Plan my day. Pull my calendar, summarize critical tasks and travel time, and give me a 30-second briefing.” |
| `cap-f66f7f6e` | capability | relay-realtime | 12 | “Read my notifications and tell me only what’s important.” |
| `cap-b5796f52` | capability | relay-realtime | 12 | “Start a focus session for 25 minutes. Block distractions and let me know when time’s up.” |
| `cap-fb73a1d0` | capability | relay-realtime | 12 | “Remember this: my bike lock code is 4829.” |
| `cap-d9af189b` | capability | relay-realtime | 12 | “Summarize the key points from this page and read them to me later.” |
| `cap-37804d89` | capability | relay-realtime | 12 | "Remind me to do X at 6 pm" or "Every weekday at 9, remind me to stand up" |
| `chg-43804606` | dashboard-ux | browser-extension | 12 | Add a Browser Jobs view shared by web, menubar, and iOS: active/queued/completed jobs, per-site permission scope, source evidence, extracted result, p |
| `chg-56aa1998` | dashboard-ux | mac-planner | 12 | Add a unified Jobs and Approvals view shared by web, menubar, and iOS: each job shows purpose, sources accessed, files/apps touched, risk level, estim |
| `chg-12222176` | firmware | relay-realtime | 12 | Implement adaptive duplex behavior: when downlink audio is playing, reduce or pause uplink capture/encoding to avoid LTE contention; resume capture af |
| `chg-075869de` | integration | mac-planner | 12 | Make FULL_CONTROL_MODE execute through a capability-scoped confirmation broker instead of bypassing actionRisk. Classify every action (read, reversibl |
| `chg-81e5c92d` | integration | relay-realtime | 12 | Add a server-side browser harness (Cloudflare Browser Run) so the relay can perform read-only web tasks without requiring the Mac to be online, with s |
| `chg-5fc73ce3` | mac-harness | mac-planner | 12 | Add transactional desktop jobs: each plan has a preview, stable job/action IDs, preconditions (expected app/path/hash), checkpoints, result receipts,  |
| `chg-5415e046` | memory | browser-extension | 12 | Create a browser-job memory tier separate from conversational context: retain only normalized facts, source URLs, retrieval timestamps, consent scope, |
| `chg-a18cc4f0` | memory | browser-extension | 12 | Add a browser-site capability registry in the knowledge graph: per origin, allowed paths, login/session status (never credentials), extraction recipe, |
| `chg-96771ece` | memory | mac-planner | 12 | Unify fleetContext and the knowledge graph behind a scoped memory service that stores facts with provenance, sensitivity, confidence, expiry, and last |
| `chg-fa7c3587` | model-routing | mac-planner | 12 | Route deterministic Mac requests (open app/URL, list a directory, create a standard reminder, read a known file) through a typed intent parser and loc |
| `chg-cd89301b` | model-routing | mac-planner | 12 | Introduce a policy router that classifies requests into realtime dialogue, deterministic Mac/browser execution, cheap background summarization, or hig |
| `chg-ea640c81` | model-routing | relay-realtime | 12 | Introduce a clear tiering rule: realtime relay model only handles conversational intent capture, clarification, and short confirmations. Any task that |
| `chg-324de76f` | stack | relay-realtime | 12 | Align the stack spec and orchestrator tool registry for the realtime agent, and publish a single authoritative capability manifest (tools, endpoints,  |
| `cap-b15b17f9` | capability | browser-extension | 11 | Open this website, fill out the form with the information we discussed, and show me exactly what is ready before you submit it. |
| `cap-cb69fbe6` | capability | browser-extension | 11 | Watch this logged-in page and tell me when the status changes, but don't click anything or send anything. |
| `cap-e49fb28e` | capability | mac-planner | 11 | “Research this topic, compare the best options, and leave me a short audio recommendation—don’t buy anything.” |
| `cap-52dcc328` | capability | mac-planner | 11 | “Every Friday, tidy my Downloads into dated folders, show me a preview, and only then apply it.” |
| `chg-0aa257d0` | dashboard-ux | browser-extension | 11 | Add a unified Jobs inbox across web, menubar, and iOS showing running/blocked/completed browser and Mac jobs, compact evidence, sensitive-field redact |
| `chg-6360d815` | memory | mac-planner | 11 | Replace per-surface hand-written fleetContext sections with a compact, typed context projection: stable preferences and permissions, current tasks, an |
| `chg-c3788e7b` | interaction | browser-extension | 10 | Make browser work explicitly two-phase: 'inspect' returns a concise result with citations and a proposed action; 'apply' repeats the exact destination |
| `chg-aace6694` | mac-harness | mac-planner | 10 | Add typed, read-only observability endpoints for job execution: running apps, foreground app, accessibility state, browser tabs, and allowlisted direc |
| `chg-5b887962` | routines | relay-realtime | 10 | Add a Worker-side scheduler using Cron Triggers and Durable Object alarms to run routines even when the Mac is asleep, with a simple queue that delega |
| `cap-2eef696b` | capability | mac-planner | 9 | When I say 'clean up my desktop', group obvious screenshots and downloads into dated folders, but show me the proposed moves first. |
| `cap-2b03a27d` | capability | mac-planner | 9 | Clean up my Downloads: identify duplicate, temporary, and likely finished files, show me a proposed plan, then move only the approved items into an ar |
| `cap-64c3562b` | capability | relay-realtime | 9 | “When I get back to my desk, summarize what happened while I was away and queue anything urgent.” |
| `cap-d5ef6ea9` | capability | relay-realtime | 9 | “Remind me every weekday at 5 to shut down and summarize what I did today.” |
| `chg-05a523e6` | interaction | mac-planner | 9 | Make every Mac plan two-phase by default: first return a concise preview with affected app/files/URLs and expected side effects, then execute only the |
| `chg-f79dcdb8` | routines | relay-realtime | 9 | Add a first-class scheduler/queue for delayed and recurring work in the relay, backed by Durable Objects (alarms) or Worker Cron. Provide a routine st |
| `cap-8648b1a9` | capability | mac-planner | 6 | “Once a week, clean up my Downloads: group files by type and project, flag duplicates and stale installers, and show me a review list before anything  |
| `chg-5e11771e` | mac-harness | mac-planner | 6 | Add an execution journal with per-action risk labels, pre-state capture where feasible, idempotency keys, and a narrow confirmation gate for irreversi |
| `chg-f527c3bc` | model-routing | relay-realtime | 6 | Default web reading and extraction to a server-side browser (Cloudflare Browser Run) via server_browser_actions when the task is purely web and does n |
| `chg-c128259b` | memory | mac-planner | 5 | Replace the surface-specific fleetContext prompt fragments and ad-hoc job history with a shared event-sourced task/artifact ledger. Each event has tas |
| `chg-5fd30665` | browser-harness | relay-realtime | 4 | Give the relay a server-side browsing path using Cloudflare Browser Run for public web tasks, with a policy to prefer server_browser_actions over rout |
| `chg-1e29f657` | hardware | mac-planner | 4 | Replace the desk-oriented nRF9160 DK prototype with a jewellery-sized low-power BLE pendant built around an nRF5340-class dual-core SoC (1 MB RAM-clas |
| `chg-56aed4a5` | memory | mac-planner | 4 | Replace per-surface prompt-written fleetContext sections with an event-sourced shared memory ledger plus compact, queryable projections: durable facts |

## Rejected / duplicate

| id | layer | proposed by | × | change |
| --- | --- | --- | --- | --- |
| `chg-bc35ae04` | browser-harness | browser-extension | 12 | Add a first-class browser session API: list tabs with stable tab IDs, select a tab explicitly, bootstrap navigation only after confirmation, capture a |
| `chg-2fffc681` | browser-harness | browser-extension | 12 | Add a durable browser-task runner: bootstrap a tab via navigate, maintain task-scoped tab IDs, execute read/click/type/wait sequences with timeouts, c |
| `chg-086a6904` | browser-harness | browser-extension | 12 | Replace generic browser action results with a typed, policy-enforcing runner: classify commands as read-only or mutating; enforce origin/path allowlis |
| `cap-fc6643a7` | capability | browser-extension | 12 | “Every weekday morning, check my authenticated work portal for new high-priority items and tell me only what needs my attention.” |
| `cap-daaf6d3e` | capability | browser-extension | 12 | Research this topic across my logged-in websites, compare the results, and send me a concise audio brief later. |
| `cap-b4dfb9ea` | capability | mac-planner | 12 | “Clean up my Downloads every Friday: group files by project, rename obvious duplicates, and show me a review list before anything is deleted.” |
| `cap-026858ec` | capability | mac-planner | 12 | “Find the best flight options for next Thursday, compare total price and duration, and leave me a shortlist; do not book.” |
| `cap-7e779dac` | capability | relay-realtime | 12 | "Summarize this webpage" or "Check the price on this product" |
| `chg-71ae0f60` | mac-harness | mac-planner | 12 | Replace FULL_CONTROL_MODE's undifferentiated execution path with a typed action broker: structured read/open/search actions by default, and separate m |
| `chg-e0d96401` | mac-harness | mac-planner | 12 | Put a typed capability broker in front of the existing FULL_CONTROL computer loop. Accept structured argv/files/app/UI operations with per-capability  |
| `chg-5dced2e2` | memory | mac-planner | 12 | Replace hand-written per-surface fleetContext prompt sections with a shared, typed context service: store facts with source, confidence, sensitivity,  |
| `chg-a05b2515` | memory | mac-planner | 12 | Replace per-surface prompt hand-written fleetContext with a compact, typed context API: stable owner preferences and permissions, task-local facts, an |
| `chg-54408a62` | model-routing | browser-extension | 12 | Introduce a browser-specific low-cost pipeline: deterministic command planner for navigation/extraction, small model for selector repair and page summ |
| `chg-67e2a397` | model-routing | mac-planner | 12 | Introduce an asynchronous job router with cheap background models for extraction, summarization, monitoring, and retries; reserve realtime for short v |
| `chg-1bd50c67` | model-routing | relay-realtime | 12 | Introduce a clear tiering policy: relay-realtime handles only intent capture, brief clarification, and immediate safety checks; everything else become |
| `chg-7f6f0131` | model-routing | relay-realtime | 12 | Add explicit, cheap tiers: relay captures intent and hands off to mac_delegate or server_browser_actions. Introduce job creation, status, cancellation |
| `chg-b3826cae` | browser-harness | browser-extension | 11 | Add a typed browser-job protocol with origin allowlists, tab bootstrap via navigate, structured extract selectors, per-action risk labels, screenshot/ |
| `cap-bc260bea` | capability | browser-extension | 11 | Every weekday morning, check my logged-in work dashboard, calendar, and inbox, then give me a short audio briefing with only what needs my attention. |
| `cap-2fc364ed` | capability | mac-planner | 11 | “Give me a workday brief at 8:30, and let me play it from the pendant when I’m ready.” |
| `cap-d91c8266` | capability | mac-planner | 11 | “Before my next meeting, prepare me: open the agenda, summarize relevant email, and put a private briefing on the pendant.” |
| `chg-6a6fa4b6` | mac-harness | mac-planner | 11 | Add a typed action policy in front of FULL_CONTROL_MODE: classify every action as read-only, reversible local mutation, or high-impact mutation; requi |
| `chg-9206eec2` | memory | browser-extension | 11 | Store browser task definitions as versioned, user-owned recipes (origin, allowed paths, selectors, extracted fields, cadence, privacy/retention, and c |
| `chg-e5bfe9ad` | model-routing | mac-planner | 11 | Route all non-conversational work through an asynchronous job planner: realtime handles intent capture and confirmation only; a cheaper background mod |
| `cap-9a41624d` | capability | browser-extension | 10 | Watch this logged-in page for a meaningful change and tell me when it happens, with the before-and-after evidence. |
| `cap-dde88711` | capability | mac-planner | 10 | Every weekday at 8:30, prepare a concise workday brief: today's calendar, unread mail grouped by urgency, and the top three actions; save it as an aud |
| `cap-c5c14868` | capability | mac-planner | 10 | When I say 'triage my inbox', classify unread mail into urgent, reply soon, reference, and noise, draft replies for the first two categories, and show |
| `cap-60031093` | capability | mac-planner | 10 | Keep a daily 'closeout' routine: at 5:30 PM, summarize unfinished calendar items and the notes/files I touched today, then create a short checklist fo |
| `cap-2a78a3d7` | capability | relay-realtime | 10 | “Check the weather and read the highlights to me.” |
| `chg-30c6ee4e` | dashboard-ux | browser-extension | 10 | Add a Jobs inbox shared by web, menubar, and iOS: each job shows status, source links, last update, evidence snippets, sensitivity, proposed actions,  |
| `chg-b453effa` | dashboard-ux | mac-planner | 10 | Add a unified Jobs inbox shared by web, menubar, and iOS: queued/running/completed/failed jobs, source timestamps, concise result, audio-play button,  |
| `chg-e4ff3197` | memory | browser-extension | 10 | Replace raw browser-page insertion into context with expiring, source-backed facts: store only normalized facts plus source URL, observedAt, confidenc |
| `chg-e567ac6a` | model-routing | mac-planner | 10 | Add an asynchronous job router: realtime handles only immediate conversational acknowledgement and dispatch; a cheaper background model handles calend |
| `cap-2fb3dd01` | capability | mac-planner | 9 | Every weekday morning, give me a short audio brief of today's calendar, unread important mail, weather, and any browser jobs that finished overnight. |
| `cap-d90ef7f1` | capability | mac-planner | 9 | Before my next meeting, prepare a one-page brief from the calendar invite, recent related mail, and approved web sources, save it to my Mac, and tell  |
| `cap-817211fc` | capability | mac-planner | 9 | Every weekday morning, give me a short brief of today's calendar, unread important mail, and the one thing I should prepare for; let me hear it on the |
| `cap-511245d4` | capability | mac-planner | 9 | When I say 'research this' or schedule a topic, investigate the web, summarize the best sources, and leave a cited note and a short audio briefing for |
| `cap-a5a9a6a9` | capability | mac-planner | 9 | Turn my unread mail into a priority list and draft replies for the top three, but never send anything without showing me the drafts first. |
| `cap-6bbef5ec` | capability | relay-realtime | 9 | “Read me the top three things I should care about right now.” |
| `chg-a649e91c` | dashboard-ux | mac-planner | 9 | Ship a unified Jobs inbox across web, menubar, and iOS showing queued/running/completed/failed work, source account, evidence links, data sensitivity, |
| `chg-75156244` | mac-harness | mac-planner | 9 | Add a mandatory server-side confirmation broker around POST /execute: classify each action batch, require a short-lived token for external side effect |
| `chg-85f818f7` | mac-harness | mac-planner | 9 | Add a real policy gate around POST /execute even when FULL_CONTROL_MODE is enabled: classify actions into read-only, reversible, and consequential; re |
| `chg-38c86bb7` | model-routing | mac-planner | 9 | Split work into a cheap asynchronous planner/classifier, deterministic Mac/browser executors, and realtime only for live dialogue and ambiguous confir |
| `cap-c262d2f0` | capability | browser-extension | 6 | When I ask, find the exact information on a logged-in website—such as my latest bill, a delivery status, or an insurance claim—and read me the answer, |
| `cap-4ad2b2ea` | capability | mac-planner | 6 | “Every weekday morning, give me a short brief of my calendar and important unread mail, and open the first meeting's materials on my Mac.” |
| `cap-72735dd9` | capability | mac-planner | 6 | “After each meeting, prepare a follow-up workspace: open the meeting notes, create a draft summary file with attendees and action items, and show me t |
| `cap-019af748` | capability | relay-realtime | 6 | Give me a quick briefing for my day, and make it something I can listen to later. |
| `cap-0d0e5fa0` | capability | relay-realtime | 6 | Look up this topic on the web and summarize it for me. |
| `chg-6c8e6a4f` | dashboard-ux | browser-extension | 6 | Create a unified task timeline showing source site/origin, extracted facts, pending approval cards, exact submit payload, model used, and retention/de |
| `chg-70480c0c` | memory | browser-extension | 6 | Store browser tasks as short-lived provenance records: origin, timestamp, normalized facts, confidence, redaction class, approval state, and content h |
| `chg-ac0e31c4` | model-routing | browser-extension | 6 | Route public web research to web_search, authenticated read-only lookups to a cheap browser-extraction model, long multi-page workflows to background  |
| `chg-1d2a4e64` | model-routing | mac-planner | 6 | Introduce a job classifier before model invocation: deterministic Mac plans and bounded Calendar/Mail extraction use rules or a cheap batch model; doc |
| `chg-dc197347` | relay | relay-realtime | 6 | Add a lightweight intent-routing policy that uses relay_route_intent to label the request and target mac-planner or server browser explicitly, and emi |
| `chg-b9b626f3` | routines | relay-realtime | 6 | Add a real scheduling layer for delayed and recurring work in the relay: use Cloudflare Cron Triggers for recurring jobs and Durable Object alarms for |
| `chg-924f8ac4` | browser-harness | browser-extension | 5 | Replace the current fire-and-forget browser enqueue path with a durable command queue: persist commandId, target tab/device, requested action, idempot |
| `cap-31e2c2fa` | capability | browser-extension | 5 | Watch my logged-in websites (bank, bills, delivery, work portals) and tell me only when something important changes; read the details to me, but never |
| `cap-72fb3e64` | capability | mac-planner | 5 | While I’m busy, watch my authenticated dashboards and tell me only when something important changes—like a bill, travel disruption, account alert, or  |
| `cap-9bc15e6b` | capability | mac-planner | 5 | Take care of this on my Mac, but show me exactly what you’re about to change before anything irreversible happens. |
| `cap-e1ee3b1d` | capability | mac-planner | 5 | Before each meeting, prepare a two-minute brief from the invite, recent mail, and relevant files; afterward, draft the follow-up and put it in my draf |
| `cap-1e4c774f` | capability | mac-planner | 5 | While I sleep, monitor my authenticated browser sources and Mac work queue, then give me a concise morning brief on the pendant with links, changes, a |
| `cap-f381bceb` | capability | relay-realtime | 5 | “Summarize the top results from the web about X, and keep it out of my Mac.” |
| `cap-e2d21e8e` | capability | relay-realtime | 5 | “Check my inbox and tell me what needs attention, but don’t send anything.” |
| `cap-e157b2ab` | capability | relay-realtime | 5 | “Keep an eye on this website and let me know when anything important changes.” |
| `chg-106220f4` | dashboard-ux | mac-planner | 5 | Add a unified job inbox showing queued/running/paused/completed work across relay, Mac, and browser. Each job displays source, progress, exact effects |
| `chg-50677507` | integration | relay-realtime | 5 | Add a relay-owned job scheduler using Cloudflare Cron Triggers plus Durable Object alarms to run periodic tasks (web diffs, inbox checks, maintenance) |
| `chg-d04e26d1` | interaction | relay-realtime | 5 | Introduce a confirmation gate for high-risk actions: relay summarizes intent, shows/reads a payload (e.g., draft email, purchase order, form submissio |
| `chg-a6c055eb` | mac-harness | mac-planner | 5 | Add a typed, idempotent execution transaction API around the existing FULL_CONTROL_MODE bridge: plan_hash, action IDs, preconditions (foreground app/f |
| `chg-faf33254` | model-routing | mac-planner | 5 | Introduce a three-tier planner pipeline: deterministic intent/action compiler for simple desktop commands; cheap background model for multi-step plann |
| `chg-c31b8eba` | model-routing | relay-realtime | 5 | Adopt a strict routing policy: realtime relay only for intent capture, clarification, and immediate reversible actions; mac_delegate for multi-step ta |
| `chg-6f1a605b` | routines | relay-realtime | 5 | Add a scheduler layer using Worker Cron Triggers and Durable Object alarms for delayed and recurring jobs, with a job table in D1 and a relay job-stat |
| `cap-e9d24899` | capability | mac-planner | 4 | Handle this while I'm away, and have the result waiting for me when I get back. |
| `cap-bf4fc79f` | capability | relay-realtime | 4 | “Give me a quick overnight briefing.” |
| `chg-2429a245` | routines | relay-realtime | 4 | Add a scheduling layer using Cloudflare Cron Triggers (for daily/weekly routines) and Durable Object alarms (for per-user delayed tasks and retries).  |
| `skill-ba1d5d1a` | firmware | mac-vision | 1 | computer_vision.screenshot |

