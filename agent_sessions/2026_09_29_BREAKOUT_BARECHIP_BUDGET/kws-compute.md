# On-device commands and choosing the main chip: kws-compute (2026-09-29)

Owner: research-kws-compute. Files: `kws-compute.md` and `compute-options.json`. Research was read-only. Prices come from DigiKey on 2026-09-29 unless a row says otherwise.
Tags: **[measured]** means the project's own hardware or a published measurement. **[vendor]** means a datasheet or vendor claim. **[est]** means my own calculation, with the inputs shown.

## TL;DR
- **Local commands after a button press are feasible**, covering app names, features and numbers like "50 minutes timer" or "set 7:30". The approach is a custom grammar-limited word model of about 40–60 words (DS-CNN-M/CRNN size, 0.2–0.5 MB int8). No general-purpose ASR is needed. It does **not** fit on the nRF9160: the app has 6.2 KB of RAM free and runs at 64 MHz. It fits well on an nRF5340 app core, and best on an **nRF54LM20B**, which has 512 KB RAM, 2 MB flash and the **Axon NPU**.
- **Battery reality check:** a local command costs about **8–40 mJ**. Sending the same audio over **BLE to the phone costs about the same (20–30 mJ)**. Over **LTE-M direct it costs about 2–5 J**, roughly 60–150× more. So local recognition is about latency, working offline, and saving cloud tokens and phone round-trips. It is **not** mainly a battery saving compared with BLE. The battery killers are LTE-M and the speaker.
- **Recommendation:** use the **nRF54LM20B** instead of the nRF5340. **The owner has decided on the nRF9151 as the baseline cellular SiP**, replacing the obsolete nRF9160-SICA-R7. With that pair, core chip cost falls by **$11.99 per unit at qty 1 and $7.58 at qty 100**. The firmware should still send cloud traffic over BLE first and use LTE-M only when there's no phone link (see §2).
- **The nRF9151 does not free any RAM:** it has the same 1 MB flash, 256 KB RAM and 64 MHz M33 as the nRF9160. So the §0 conclusion still holds: the recognizer belongs on the BLE SoC, not on the cellular SiP. Don't fit PSRAM. Drop MAX78000 (discontinued at DigiKey), ESP32-S3 (BLE TX at 0 dBm peaks at 176 mA) and Syntiant (it only pays off when always-on).

---

## 0. What the current firmware actually uses (nRF9160) [measured, repo]
| Item | Value | Source |
|---|---|---|
| App RAM region (NS, after TF-M) | 211,608 B | `firmware/nrf9160/build-bench/nrf9160/zephyr/zephyr.map` (`RAM 0x2000c568 len 0x33a98`) |
| App RAM used (latest build, Aug 13) | 205,244 B → **6.2 KB free** | same map, `_image_ram_end 0x2003e724`. `pendant-v2.md` reports 95.79%, 8.9 KB free |
| Flash used | 422 KB (`_flash_used 0x670ac`) of 1 MB | same map |
| Opus | libopus 1.6.1, 16 kHz, 16 kb/s, 20 ms frames, **28 KiB static pseudostack** | `src/audio_opus.h`, `audio_opus.c` |
| Main stack | 32 KiB (a SILK VLA overflow forced it up from 24 KiB) | memory note 2026-08-02 |
| Modem shmem | TX 8,320 + RX 8,192 + ctrl 1,256 B (outside the app region) | `build-opus/zephyr/.config` |
| System heap | 3 KB | `prj.conf` |
**Takeaway:** the nRF9160 app side has no room for a 35–80 KB KWS arena. Freeing that much would mean removing Opus or the stack. Its 64 MHz M33 would also run MFCC plus a command model at about 0.5–1× real time while Opus competes for the same core.

## 1. Compute numbers

### 1a. Feature extraction (MFCC / log-mel)
| Platform | Cost | Source |
|---|---|---|
| **nRF5340 app @128 MHz**, Edge Impulse MFCC, 1 s window | **93–94 ms per 1 s audio** (block mode). Rolling mode: 36–37 ms per 100 ms step | Jussinmäki MSc, U. Turku, Table 5.1 [measured] |
| STM32L476 (M4F @80 MHz), same model | 400 ms per 1 s audio (block) | same, Table 5.2 [measured] |
| M4F (MAX78000 host), 40 MFCC, 40 ms / 20 ms stride | **826 µJ per 1 s audio** | arXiv 2111.04988 §III-E [measured] |
| Hello-Edge DNN on M7 @216 MHz, MFCC + NN | ~12 ms per inference end to end; ~2 KB for audio I/O and MFCC buffers | arXiv 1711.07128 §4.5 [measured] |
→ On the nRF5340, MFCC for a 3 s command takes about 0.28 s of CPU, **about 7 mJ** at 24.6 mW (nRF5340 compute power measured in arXiv 2309.02393). On the nRF54LM20B it should be about 2–3 mJ, because the CPU runs at about 20 vs 61 µA/MHz (`pendant-v2.md` §1.2) [est].

### 1b. Recognizer options
| Option | Params / flash | RAM | Compute | Fits nRF9160 app? | Fits nRF5340 app? | Fits nRF54LM20B? |
|---|---|---|---|---|---|---|
| **(a) DS-CNN-S single keyword** (MLPerf Tiny KWS ref) | 38.6K params, **52.5 KB** tflite | ~20–30 KB arena. EI measured whole-app KWS at **35–81 KB RAM, 125–133 KB flash** on nRF5340 | 5.4 MOps per 1 s window. **66–100 ms on M4 @120 MHz** (Plumerai 71.7 ms / TFLM 100.7 ms). Axon NPU: **4.5 ms @3.0 mA = 40.5 µJ** | No (6 KB free) | Yes. EI measured 2–3 ms classify for a small model plus 94 ms MFCC | Yes, NN on Axon |
| **(b1) Custom grammar-limited command model** (my pick): DS-CNN-M/CRNN word/CTC over ~40–60 words (apps, verbs, 0–59 via ones/teens/tens, hours/minutes/seconds, am/pm, o'clock, cancel), with a grammar decoder and a confidence gate | 189–500 KB int8 (Hello-Edge DS-CNN M/L: 189.2 KB / 497.6 KB, 94.9% / 95.4% on 12-class) | 40–120 KB arena + 8 KB features. Audio streams, so no 96 KB clip buffer | ~20 MOps per 1 s audio → **~0.25–0.35 s CPU per 1 s audio on M33 @128 MHz** [est, scaled from 1a/1b] → 3 s command ≈ 0.8–1.0 s CPU, **~20–26 mJ**. Axon: ~15× faster → ~60 ms, **<1 mJ** | No | **Yes**: 512 KB RAM, but 1 MB flash is tight with firmware (~450 KB) plus the model | **Best**: 2 MB flash, NPU |
| (b2) Picovoice Rhino speech-to-intent | `libpv_rhino.a` 388 KB (Cortex-M4 archive). Contexts: clock 14 KB, alarm 11 KB, video_player 26 KB | demo `MEMORY_BUFFER_SIZE` **50 KB** | Real-time on M4 [vendor] | No | Technically yes, but **no M33/nRF MCU build is published** (only `stm32f411`). Needs a per-chipset UUID licence. Paid plans reportedly from about $6k (third-party listing) | Same licensing block |
| (b3) Sensory THF / TrulyNatural micro | not published (vendor says ≤1,000-word vocabularies; v4 "as little as 1 MB") | n/p | n/p | No | Unclear, commercial only | Unclear |
| (b4) Espressif MultiNet7 (ESP-SR), 200–300 phrases | model in flash | **18 KB internal + 2,920 KB PSRAM** | **11 ms per 32 ms frame** on ESP32-S3 @240 MHz (~34% of one core) | No | No (ESP-only) | No |
| (b5) Vosk small en-us | **40 MB** model | **~300 MB** runtime | n/a | No | No | No |
| (b6) Moonshine-tiny / Whisper-tiny | **27.1M / 37.8M params** → 27–38 MB int8 weights | Tens of MB activations/KV. Whisper-tiny runtime quoted ~273 MB | GFLOPs per utterance (Moonshine is 5× less than Whisper-tiny for 10 s) → about 50× over flash and minutes of M33 time | No | No | No (needs a phone or an Apollo510-class chip with MBs of RAM, and even then not tiny) |

MLPerf Tiny KWS reference: DS-CNN, 38.6K params, 49×10 MFCC input, 12 classes, 90% target (reference 91.6–92.2%) (arXiv 2106.07597).

### 1c. RAM and flash budget after the change (nRF5340 app core or nRF54LM20B) [est]
| Consumer | RAM | Flash |
|---|---|---|
| Existing app minus LTE/TLS/WS (ported) | ~110–140 KB | ~350–420 KB |
| BLE host + GATT (Zephyr) | ~30–50 KB | ~120–180 KB |
| Opus encoder (existing static scratch) + 32 KB stack | ~60 KB | in the above |
| Mic DMA and ring (PDM, 16 kHz, 2×20 ms plus a 1 s ring) | ~35 KB | – |
| BLE TX queue (Opus 16 kb/s × 1 s) | ~4 KB | – |
| **Command recognizer (b1)** arena + features | 50–130 KB | 0.2–0.5 MB |
| **Total** | **~290–420 KB of 512** | **~0.7–1.1 MB**: over 1 MB on the nRF5340, fine on the nRF54LM20B's 2 MB |
The nRF5340 has one more constraint: only the first 256 KB of its RAM is single-cycle (`pendant-v2.md` §1.2). The NN arena and the codec scratch have to be pinned there.

## 2. Energy per 2–3 s command
| Path | Parts | Energy per command |
|---|---|---|
| **Local, nRF54LM20B + Axon** | Mic 3 s (~3–7 mJ) + MFCC ~2–3 mJ + NN <1 mJ + haptic tick | **~8–12 mJ** [est] |
| **Local, nRF5340 CPU** | Mic 3–7 mJ + MFCC ~7 mJ + NN ~20–26 mJ | **~30–40 mJ** [est] |
| **BLE → phone → cloud** (nRF5340) | Mic 3–7 mJ + Opus encode ~10–15% of 128 MHz for 3 s ≈ 10 mJ + BLE link 0.3–0.6 mA × 3 V × 3–8 s ≈ 3–14 mJ (TX 3.4 / RX 2.7 mA) | **~20–30 mJ** on the device. The phone does the rest [est] |
| **LTE-M direct → cloud** (nRF91) | Nordic measured **108.9–142 mC** for a 40-byte UDP send, including the RRC tail (12.3 s). On top of that: TLS setup 2.4 s typical / 9.9 s worst [measured here], 3 s uplink, and 3–5 s waiting for the reply at 105–140 mA | **~0.5–1.25 C ≈ 0.14–0.35 mAh ≈ 1.9–4.6 J** [est from measured parts] |
| Spoken reply via MAX98357A (any cloud path) | ~50–100 mW average speech for 3–4 s | **~0.15–0.4 J**. This dominates BLE-path replies [est] |

### Daily budget (330 mAh, ~300 mAh usable) [est]
Idle floor: nRF5340 System ON idle 1.3 µA, or 2.4 µA with RAM retained [vendor]. Add a BLE connection kept alive at a long interval (~10–20 µA), BMI270 any-motion, PMIC Iq, and NAND deep power-down. With cellular fitted, add nRF9151 PSM at 2.7 µA. **Total ≈ 20–40 µA → 0.5–1.0 mAh/day.**
| Usage (per day) | mAh/day | Battery life |
|---|---|---|
| 50 commands, all local, haptic confirm | 0.8–1.3 | **~8–12 months** in theory (self-discharge will dominate) |
| 30 local + 20 cloud via BLE with spoken reply | 1.3–2.3 | **~4–7 months** |
| 50 cloud via BLE, spoken reply | 1.5–2.7 | ~3.5–6.5 months |
| 20 cloud via LTE-M direct + 30 local | 4–9 | **~5–10 weeks** |
| 50 cloud via LTE-M direct, spoken reply | 9–20 | **~2–5 weeks** |
Conclusion: "weeks" is met on any path. "Months or never charge" needs the phone (BLE) to carry cloud traffic, with LTE-M kept as a fallback when the phone is away.

### Solar on the ~34 mm face (~9 cm² total, ~5–6 cm² usable) [est]
| Light | Cell type | Harvest | vs floor (0.5–1.0 mAh/day) |
|---|---|---|---|
| Indoor 500 lux, 8 h | a-Si indoor cell (~4.3 µW/cm² @200 lux from AM-1454's 46.5 µW / 10.9 cm², scaled linearly) | ~64 µW → ~0.5 mWh → **~0.11 mAh/day** after ~80% MPPT | covers **~10–20%** of the idle floor |
| Outdoor sun, 30 min, pendant tilted (cos factor ~0.3–0.5) | c-Si (KXOB25-05X3F: 30.7 mW per 1.84 cm²) | ~30–45 mW → **~4–6 mAh/day** | covers the whole local-command day several times over |
→ "Never charge" works only for users who spend about 30 min a day outdoors with a c-Si cell, and mostly with local or BLE commands. Indoors, solar stretches the battery by about 10–20%. It doesn't replace charging.

## 3. Brain options, best value first
Prices are DigiKey qty 1 / qty 100 on 2026-09-29 unless noted.
| # | Part | Core / ML | RAM / NVM | Radio | Sleep | $ @1 / @100 | Stock | Verdict |
|---|---|---|---|---|---|---|---|---|
| 1 | **nRF54LM20B** (QGAA QFN52) | M33 128 MHz + RISC-V + **Axon NPU** (3–8 GOPS, 15× the CPU; KWS 40.5 µJ) | **512 KB / 2 MB** | BLE 6.0, 802.15.4 | <1 µA | **$5.94 / $4.49** | **0**, 16 wk. DK **$45, 643 in stock** (NPU enabled on all DKs) | **Best value.** Same NCS/Zephyr family as the current firmware |
| 2 | nRF54LM20A (QGAA) | same, no NPU | 512 KB / 2 MB | BLE 6.0 | <1 µA | $5.37 / $4.05 | 0, 16 wk | Fallback for #1. Only $0.44 cheaper, so take the B |
| 3 | nRF54L15 (QFAA) | M33 128 MHz, no NPU | 256 KB (188 KB after FLPR reserve) / 1.5 MB | BLE 5.4 | 0.7 µA | $4.38 / $3.29 | 306 in stock | KWS fits, command model plus Opus is tight. Cheapest part in stock |
| 4 | nRF5340 (QKAA) *(current plan)* | App M33 128 MHz, DSP, no NPU; separate net core | 512 KB + 64 KB / 1 MB + 256 KB | BLE 5.4 + LE Audio | 0.9–2.4 µA | $9.74 / $7.40 | 0 (2,994 due 10-30) | Works but costs more, uses ~3× the CPU energy, and has half the flash |
| 5 | Apollo510B (AP510BFA-CBR) | M55 250 MHz Helium | **3.75 MB / 4 MB** | BLE 5.4 | vendor claims class-leading | $21.10 / $15.23 | 2,213 | Could host MultiNet-class models. Would mean a toolchain rewrite; eval board $250.53 |
| 6 | Apollo4 Blue Lite (AMA4B2KL-KXR) | M4F 192 MHz | 1.375 MB / 2 MB | BLE | vendor ~µA | $10.64 / $7.51 | 62 | Older M4F, no NPU; dominated by #1 |
| 7 | Alif Balletto B1 | M55 160 MHz + **Ethos-U55 (128 MAC/cycle, up to 46 GOPS)** | 2 MB / 1.8 MB | BLE 5.3 | n/p | **chip price not published**. SK-B1 $51.28 (DigiKey) / $49.99 (Mouser), out of stock, next batch 2026-10-22 | – | Strongest NPU with BLE, but no chip price and immature Zephyr support. Watch it |
| 8 | ESP32-S3 (MINI-1-N4R2 module) | 2× LX7 240 MHz + PSRAM | 512 KB + 2 MB PSRAM | Wi-Fi + BLE 5 | 7 µA deep sleep | $5.21 / $4.05 | 157 | MultiNet7 runs offline, but **51–72 mA active and 176 mA BLE TX @0 dBm** → ~0.5 J per command. Bench reference only |
| 9 | STM32U585 | M33 160 MHz | 784 KB / 2 MB | **none** | µA | $10.89 / $7.21 | 1,953 | No radio and no NPU → dominated |
| 10 | STM32N657 | M55 800 MHz + Neural-ART NPU | 4.2 MB / no flash | none | high | $26.75 / $18.61 | 334 | Overkill and power-hungry |
| 11 | MAX78000 / MAX78002 | M4F + CNN accelerator (KWS 3.5 ms / 251 µJ) | 512 KB flash | none | – | **n/a: discontinued at DigiKey, 0 stock** (FTHR board too) | 0 | Drop |
| – | Syntiant NDP120 | always-on NDP | – | – | – | – | – | Its advantage is always-on µW listening. With a button, the NPU in #1 does the same job for about $0 extra. Drop (the owner already removed it) |
| – | nRF54H20 | M33 320 MHz + RISC-V | 1 MB / 2 MB | BLE | – | **n/a**: DigiKey "no longer available", DK "coming soon" | – | Not orderable |

### Does the nRF9160 earn its place?
| Part | $ @1 / @100 | Notes |
|---|---|---|
| nRF9160-SICA-B1A-R7 (previous) | $31.56 / $22.59 (research-components) | The old -SICA-R7 is obsolete. Nordic recommends the nRF9151 for new designs |
| **nRF9151-LACA-R (baseline, owner decision)** | **$23.37 / $17.92** cut tape. **11,739 in stock**, 16 wk. (The -R7 reel is out of stock, 100 due 2026-10-05) | Same **1 MB / 256 KB / M33 64 MHz** as the nRF9160, so **no RAM gain**. The ~6 KB-free problem carries over. **11×12×1 mm LGA vs 10×16×1.04 mm**: about 20% less area (132 vs 160 mm²), 4 mm shorter but 1 mm wider, which is easier to fit inside a 34 mm round puck. It is a different LGA-113 footprint, so the layout must be redone (not drop-in). Adds **Power Class 5 (20 dBm)**, which cuts TX peak current on a small battery, plus DECT NR+ and NB-NTN. PSM 2.7 µA (vs 9160's 1.4 µA with modem+MCU off, per `pendant-v2.md` §1.2). Reuses the same NCS modem library. **DK $102.43** (107 in stock, no qty breaks listed) |
| nRF9161-LACA-R7 | $32.93 / $23.96 @300 | Adds DECT NR+. Not needed |
- Cost and energy: each LTE-M cloud command uses about 0.14–0.35 mAh, **60–150× a BLE command**. The part plus antenna, SIM and plan cost about $18–31 plus a monthly fee.
- Its value is phone-free operation (walks, runs, a dead phone) and GPS. **The owner kept cellular as core, using the nRF9151.** For battery life, the firmware should send to cloud over BLE first and use LTE only when there's no phone link. Set the modem to Power Class 5 (20 dBm) when the signal allows, to limit TX peaks on the 330 mAh cell.

### PSRAM (APS6404L, 8 MB QSPI)
Adafruit #4677 (generic 64 Mbit, sanded) costs **$1.75**. The genuine APS6404L-3SQR-SN is at Mouser only, not DigiKey, and the page timed out, so its price is unverified. **Not needed.** The command model fits in on-chip RAM. Offline notes should be Opus-encoded straight to the W25N02KV NAND: 256 MB at 2 KB/s is about 35 h of audio. PSRAM only earns a place in an ESP32-S3/MultiNet design, and it would need a power switch for standby. Leave it off the BOM.

## 4. Recommendation
**Architecture:** button → PDM mic → MFCC on the M33 → grammar-limited command model on the **Axon NPU (nRF54LM20B)**.
- **If confidence ≥ threshold:** run locally (timer, alarm, notes to NAND, music transport, call-by-contact via the phone) and confirm with the LRA plus an earcon.
- **Otherwise:** send the buffered Opus audio to the cloud, **over BLE to the phone first** and over **nRF9151 LTE-M (core) only if there's no phone**.
- No always-on listening. Stream the audio into the recognizer while the button is held, so the result is ready within about 100 ms of release.
- Train with Edge Impulse or Nordic Edge AI Lab (both support the nRF54LM20 DK and Axon). Deploy with TFLM plus the Axon compiler. Avoid Rhino and Sensory because of licensing, not size.
- **EVT gate:** at least 95% intent+slot accuracy on about 200 recorded club utterances, in quiet and noisy conditions. Numbers are the risk, so confirm "fifty" vs "fifteen" with haptics and support "undo".

**Keep / swap:**
| Current | Proposed | Why |
|---|---|---|
| nRF5340 | **nRF54LM20B** | NPU, 2 MB flash, ~3× CPU efficiency, cheaper. Same NCS. Risk: 0 stock with a 16-wk lead → order DKs now and chips early. The fallback is nRF54LM20A, or the nRF5340 on the same schematic block |
| nRF9160 | **nRF9151 (core, owner decision)** | The nRF9160-SICA-R7 is obsolete. The nRF9151 is Nordic's successor: $8.19 cheaper at qty 1, 20% smaller, PC5 20 dBm. It has the same RAM, so no ML goes on it |
| (proposed) PSRAM, NDP120, ESP32 | none | Not needed or not efficient |
| nPM1304, W25N02KV, BMI270, PDM mics, MAX98357A, DRV2605L | keep | Unaffected |

**Per-device BOM delta (compute and cellular chips only):**
| Config | @1 | @100 | Δ vs current (nRF9160 + nRF5340 = $41.30 / $29.99) |
|---|---|---|---|
| nRF54LM20B + nRF9151 | $29.31 | $22.41 | **−$11.99 / −$7.58** |
| nRF54LM20B only (hypothetical BLE-only build, not the owner's baseline) | $5.94 | $4.49 | −$35.36 / −$25.50 |
Dev and testing: 3× NRF54LM20-DK ($135). **1× nRF9151-DK ($102.43, core)**, used to port the LTE-M firmware from the nRF9160 DK. Optional: 1× ESP32-S3-DevKitC-1-N8R8 ($15, currently out of stock) as a MultiNet accuracy reference.

## Log
- 2026-09-29: first draft. Coordinator update: the owner chose the nRF9151 as the baseline cellular SiP (nRF9160-SICA-R7 is obsolete). Re-priced NRF9151-LACA-R ($23.37 / $17.92, 11,739 in stock) and the NRF9151-DK ($102.43). Both marked core in the JSON. Added footprint, RAM and power notes.

## Sources
- MLPerf Tiny paper (DS-CNN 38.6K params, 52.5 KB): https://arxiv.org/pdf/2106.07597
- Plumerai MLPerf Tiny 1.0 KWS latencies (M4 @120 MHz): https://blog.plumerai.com/2022/11/mlperf-tiny-1.0/
- Hello Edge (DS-CNN S/M/L, M7 12 ms): https://arxiv.org/pdf/1711.07128
- MAX78000 KWS 3.5 ms / 251 µJ, M4F 905 ms / 11.2 mJ, MFCC 826 µJ: https://arxiv.org/pdf/2111.04988
- nRF5340 EI KWS measurements (MFCC 93–94 ms, RAM 35–81 KB): https://www.utupub.fi/bitstream/handle/10024/182678/Lauri_Jussinmaki_masters_thesis.pdf
- nRF5340 compute power 24.64 mW: https://arxiv.org/pdf/2309.02393
- Axon NPU: https://devzone.nordicsemi.com/nordic/nordic-blog/b/blog/posts/meet-the-axon-npu ; 3–8 GOPS: https://devzone.nordicsemi.com/f/nordic-q-a/127431/nrf54lm20b-axon-npu-performance-specs ; KWS 4.5 ms / 3.0 mA / 40.5 µJ: https://novelbits.io/nordic-axon-voice-workout-tracker/ ; 128 MHz, 15× CPU: https://www.cnx-software.com/2026/01/07/nordic-semi-nrf54lm20b-wireless-soc-integrates-128-mhz-axon-npu-for-edge-ai-workloads/
- Rhino MCU (stm32f411 only, 50 KB buffer, context sizes): https://github.com/Picovoice/rhino (demo/mcu, resources/contexts/cortexm) ; pricing listing: https://checkthat.ai/brands/picovoice/pricing
- Sensory on Cortex-M/Ethos: https://sensory.com/news/sensory-speech-technologies-on-arm-ip-cortex-m-ethos-u-micronpu/
- ESP-SR benchmarks (MultiNet7 18 KB + 2,920 KB PSRAM, 11 ms/frame): https://docs.espressif.com/projects/esp-sr/en/latest/esp32s3/benchmark/README.html ; ESP32-S3 datasheet v2.2 §5.6: https://documentation.espressif.com/esp32-s3_datasheet_en.pdf
- Vosk models: https://alphacephei.com/vosk/models ; Moonshine (27.1M params, 5× less than Whisper-tiny): https://arxiv.org/abs/2410.15608
- Nordic LTE-M power example (139.9 / 142 / 108.9 mC, RRC 111.48 mC): https://nrfconnectdocs.nordicsemi.com/ncs/2.1.2/nrf/app_power_opt.html
- DigiKey product pages: see `url` in compute-options.json. nRF5340, nRF9160 and solar prices are from research-components.md (same day).
