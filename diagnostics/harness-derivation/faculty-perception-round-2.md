# Harness derivation — faculty-perception — round 2

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac agent and relay health** — Mac local agent v0.5.0 is live on /health; ops status reports relay reachable/configured, mac bridge online, browser extension offline, computer-use loop disabled, vision upload consent false, and Mac readiness false because Accessibility and Screen Recording permissions are missing (automation grants are present).
  - evidence: GET /ops/status returned 200 with these fields; GET /health returned service/version.
- **Current pendant audio pipeline** — Live pipeline telemetry exists and recent cloud-relay response rendered successfully as 24 kHz mono PCM: 164650 bytes, 3430 ms, no clipping; input telemetry in a recent job was 15625 Hz mono PCM and 937500 bytes, uploaded live LTE. Pipeline also contains held offline alerts/bookmarks from nrf9160.
  - evidence: GET /pipeline returned runs/events including TTS metadata and nrf9160 offline-store events.
- **Pendant hardware constraints** — Pendant is prototype nRF9160 DK: 211,608 B app RAM, 1 MB flash, one full-duplex I2S peripheral shared by mic/speaker, mic capture 15,625 Hz, Opus uplink 16 kHz/16 kbps, decode playback 24 kHz/60 ms frames resampled to 31,250 Hz I2S. Decode+encode consume about 87% of one core. LTE-M contention previously dropped 388 uplink packets (~7.8 s).
  - evidence: get_hardware_spec(pendant/audio/io/network) returned these values.
- **Storage and power** — microSD is a failure buffer only (write audio when upload fails), with FATFS/exFAT; no battery gauge is wired, so pendant charge cannot be read. ESP32 bridge receives I2S at 31,250 Hz, resamples to 44.1 kHz, and SBC-only A2DP source; large buffers can starve Bluetooth.
  - evidence: get_hardware_spec(storage/power/bridge) returned these constraints.
- **Active project** — Active project is AI Pendant Simulator at /Users/evanliu/agentic-gadget/software/ai-pendant-simulator, workspace ~/AI-Pendant-Workspace; goals are reliable voice interaction, LLM-first Mac planning, smarter multi-tier context memory. Open thread last work references saving order-page status.
  - evidence: GET /projects/active returned project, goals, and openThreads.
- **Timezone discrepancy** — Owner memory says timezone America/Chicago, while live machine-context reports Mac timezone America/New_York. Time-sensitive scheduling must not silently choose one; reconcile or state source.
  - evidence: Owner discover remembered timezone America/Chicago; GET /machine-context returned timezone America/New_York.
- **Briefing/account access** — Latest workday briefing says calendar and mail were not read because they need an Automation grant, and says nothing was sent. Yet ops status reports Calendar and Mail automation grants from cache. There is an access-state inconsistency requiring verification before claiming calendar/mail access.
  - evidence: GET /briefing/latest returned Not read calendar/mail; GET /ops/status listed Calendar/Mail granted from grant cache.
- **Briefing duplication** — Research briefings list contains many duplicate unplayed schedule briefings generated within minutes, each ~39.8s with identical headline/audio paths. This suggests deduplication or playback-state issue.
  - evidence: GET /research/briefings returned repeated identical 'Today's schedule — Friday, August 7' entries from 08:37–08:50, all played=false.

## What it asked for

_Nothing._
## Its own summary

Established live environment: Mac agent v0.5.0 and Cloudflare relay are reachable; relay/mac bridge online, browser extension offline, computer-use disabled, and Mac readiness false because Accessibility and Screen Recording are missing. Recent pendant pipeline telemetry confirms successful 24 kHz mono TTS (3.43 s, no clipping) and 15.625 kHz mono PCM uplink over LTE. Hardware constraints are recorded: nRF9160 prototype, one shared full-duplex I2S, ~87% CPU audio load, LTE contention packet loss, SD failure-buffer-only policy, and no battery gauge. Also recorded active project, timezone discrepancy (owner Chicago vs machine New York), calendar/mail permission inconsistency, and duplicate unplayed schedule briefings. Findings were sent to judgement/action/realtime peers.

**Biggest unknown:** Direct live pendant/firmware observability remains unavailable: I cannot establish whether the physical nRF9160 and ESP32 are currently connected, their current link/audio health, UART diagnostics, or whether the 24 kHz path is operating end-to-end right now. The pending pendant diagnostics capability and any authorized diagnostic route would resolve this.

