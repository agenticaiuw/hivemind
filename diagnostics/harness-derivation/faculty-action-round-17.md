# Harness derivation — faculty-action — round 17

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent** — Mac Local Agent v0.5.0 is live on localhost:8000; bearer auth configured, full-control and LLM planner enabled, but readiness is false because Accessibility and Screen Recording are not granted. Automation grants are cached for System Events, Finder, Reminders, Calendar, Mail, Notes, Messages, Safari, Chrome, etc.
  - evidence: GET /ops/status returned status 200 with fullControlMode:true, llmPlannerEnabled:true, accessibility.trusted:false, screenRecording.granted:false, ready:false; GET /capabilities listed 120 authenticated routes.
- **browser-bridge** — Chrome browser bridge is currently offline and has no active tab, with 2 pending commands; last seen 2026-08-07T09:21:08.821Z. Browser automation cannot be relied on until heartbeat/extension returns online.
  - evidence: GET /browser/status and GET /ops/status both report online:false, tabId:null, tabCount:null, pendingCommands:2.
- **relay** — Cloud relay is configured and reachable; pairing is required, speech-to-text configured, mac bridge online, durable audio and persistent state enabled. Relay reports macOS say TTS at 24 kHz PCM with tts-1 alloy fallback.
  - evidence: GET /ops/status relay.payload returned reachable:true, pairingRequired:true, macBridgeOnline:true, capabilities including durableAudio:true, models textToSpeech macOS say (24 kHz PCM).
- **host** — Owner Mac is MacBook-Air-6.local, Darwin arm64 macOS 26.5.2, timezone America/New_York, with 123 applications and many automation CLIs. This timezone is observed machine context, not separately owner-authoritative.
  - evidence: GET /machine-context returned hostname, platform darwin, timezone America/New_York, macOS version and app/CLI inventory.
- **pendant-hardware** — Pendant is prototype Nordic nRF9160 DK, 64MHz Cortex-M33, 211,608B app RAM, 1MB flash, one button/LED, one full-duplex I2S peripheral; mic capture is 15,625Hz, Opus uplink 16kHz/16kbps, playback decode 24kHz/60ms resampled to 31,250Hz I2S.
  - evidence: get_hardware_spec pendant/audio/io returned board, memory, controls, and audio path.
- **offline-storage** — Pendant microSD is a failure buffer only: audio is written to SD only when chunk upload cannot be uploaded; FATFS with exFAT enabled.
  - evidence: get_hardware_spec storage returned owner's standing rule and filesystem configuration.
- **action-capabilities** — Production tools available: get_mac_status for read-only live state; mac_run_actions for 1–3 reversible concrete Mac actions; browser_run_actions for browser work but requires bridge online; mac_delegate for complex/ambiguous workflows; relay_job_status for prior Mac jobs. No action was executed during reconnaissance.
  - evidence: describe() on all five tools returned their scope and constraints; browser status is offline and Mac readiness false.
- **owner-policy** — Owner memory says browser may read/click without asking; confirm before sending mail, deleting files, or buying; reminders/notes may be created without asking; replies should be one short spoken sentence. Current owner goal says derive next agent changes from harness ledger and ship 24kHz superwideband audio path end-to-end on pendant.
  - evidence: discover(owner) returned remembered policy and Now section.
- **timezone-conflict** — Timezone conflict remains unresolved: live machine-context reports America/New_York, while owner memory says America/Chicago. Do not choose silently for scheduling or spoken time answers.
  - evidence: GET /machine-context returned timezone America/New_York; discover(owner) remembered timezone America/Chicago.
- **scheduled-work** — Five routines are enabled, including morning brief, daily LPWAN research brief, evening wrap-up, daily calendar/mail/files brief, and Friday Downloads tidy preview; most recent statuses are completed except daily calendar/mail/files brief has not run.
  - evidence: discover(owner) returned scheduled routines with enabled:true and lastStatus fields.

## What it asked for

### `t19-p6h0` (tool) — propose_capability_or_change
- why: Owner explicitly requires recording a new capability/change this round; this tool is not exposed in the current tool list, but prior rounds indicated it may be granted dynamically. Need a recorder that persists proposal to backlog without implementing it.

```json
{
  "type": "object",
  "properties": {
    "kind": {
      "type": "string",
      "enum": [
        "capability",
        "change"
      ]
    },
    "title": {
      "type": "string"
    },
    "description": {
      "type": "string"
    },
    "why_now": {
      "type": "string"
    },
    "owner_value": {
      "type": "string"
    },
    "dependencies": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  },
  "required": [
    "kind",
    "title",
    "description",
    "why_now",
    "owner_value",
    "dependencies"
  ]
}
```

## Its own summary

Recon complete. Mac agent is live and authenticated, with full-control planner configured, but not ready: Accessibility and Screen Recording are both denied. Browser bridge is offline with no active tab and 2 pending commands, so browser work is blocked. Relay is reachable and paired infrastructure is configured; 24 kHz TTS is evidenced in pipeline telemetry. Owner policy is known (browser read/click allowed; confirm sends/deletes/purchases; reminders/notes allowed; concise spoken replies) and owner goal is end-to-end 24 kHz audio plus harness-led changes. I recorded the hardware/audio constraints, host inventory, routines, and the NY-vs-Chicago timezone conflict. Still needed for useful action: the already-requested Mac build/device inspection capability and firmware-read permission; Accessibility/Screen Recording grant; browser extension enablement/heartbeat; authoritative owner timezone and action-priority/approval policy; and the outstanding implementation/proposal tools. No side effects were performed.

**Biggest unknown:** Whether the orchestrator will actually grant the pending firmware/build/device inspection, proposal, and permission requests; until Accessibility/Screen Recording and browser connectivity are fixed, I cannot safely perform GUI or browser actions. Also timezone remains contradictory (live machine America/New_York vs remembered owner America/Chicago).

