# research-components — working log (2026-09-29)

Owner: research-components subagent. Claimed files: `components.json`, `research-components.md` (this folder only). Read-only web research; no purchases, sign-ins, or form submissions. Token telemetry unavailable to this subagent.

## Context reused
- `docs/hardware/pendant-v2.md` BOM: BMI270 IMU, DRV2605L + VLV101040A LRA, W25N02KV NAND, nPM1304 PMIC, MAX98357A amp, T5838 PDM mic, round ~330 mAh LiPo (semi-custom), Johanson 2450AT18A100 BLE antenna.
- `docs/hardware/respin-speaker-mute-secure-element.md`: MAX98357AETE+T ($3.96/$2.47@100), PUI AS01308MR-2-R speaker ($4.46), CUS-12TB mute switch ($0.91/$0.65), ATECC608C ($0.77), SPH0641LU4H-1 PDM mic ($3.22/$2.01).
- Already purchased (July 2026, 2026_09_23 purchase-evidence.json): nRF9160 DK ($179.80), MAX98357A #3006, PDM mic #3492, DRV2605L #2305, vibration disc #1201, 500 mAh LiPo #1578, oval speaker #3923, LSM6DSOX #4438, HUZZAH32 (ESP32, now dropped), microSD breakout + card.

## Working log
- 2026-09-29: DigiKey detail/search pages fetch fine via WebFetch (search-by-keyword redirects to detail); Mouser timed out — using DigiKey for bare chips, Adafruit/SparkFun/Seeed/Waveshare for breakouts.
- nRF9160-SICA-R7 is **Obsolete** at DigiKey; replacement NRF9160-SICA-B1A-R7 $31.56 @1 / $22.59 @100 (T&R), 9,637 stock. nRF9160 DK $179.80, 221 stock.
- NRF52840-QIAA-R $7.28 @1, 40,927 stock.
- DigiKey bare radios: NRF5340-QKAA-R $9.74/@100 $7.397 (0 stock, 2,994 due 2026-10-30); NRF52840-QIAA-R $7.28/@100 $5.5056 (40,927 stock); NRF7002-QFAA-R $4.65/@100 $3.50 (250 stock).
- DigiKey kits: nRF5340-DK $48.95; nRF52840-DK $48.95 (1,043); nRF7002-EK $20.33 (45); nRF7002-DK $59.23 (245); Thingy:91 X $101.44 (0 stock, ETA 2026-09-28 past due). Guessed "1490-...-ND" detail URLs 404 → kit rows link DigiKey keyword search (redirects to exact match).
- Adafruit breakouts verified: PDM mic #3492 $4.95; SPH0645 #3421 $6.95 (100+ $5.56); DRV2605L #2305 $7.95; vibe disc #1201 $1.95 (100+ $1.56); 500 mAh LiPo #1578 $7.95 (protected, 29x36x4.75); oval speaker #3923 $1.95 OOS; LSM6DSOX #4438 $11.95 OOS; MAX17048 #5580 $5.95; USB-C Micro-Lipo #4410 $5.95; Qi RX #1901 $14.95 (40x29 coil, 5V 500 mA); fingerprint #4750 $19.95 OOS and OPTICAL (not capacitive); MPR121 #1982 $7.95; AT42QT1070 #1362 $7.50; PS1240 piezo #160 $1.50; ATECC608 #4314 $4.95 (100+ $3.96); VCNL4040 #4161 $5.95 (100+ $4.76).
- CEO update received mid-task: replace generic extras with owner-slide list (NDP120, VM3011, force sensor, VPU/bone-conduction, Gore/Saati vents, VCNL4040/APDS-9960, UWB DW3000/Murata 2BP, APS6404L PSRAM, IS31FL3194 + LEDs, 2-pole mute switch, privacy LED, ATECC608B, NT3H2111, TPS22916, tools: PPK2, NanoVNA-H4, TC2030, pogo jig). Each gets a lever note (speed/accuracy/cost/privacy). Camera/fingerprint stay test-only.
- Fingerprint (capacitive UART): Waveshare UART Fingerprint Sensor (C) $19.99 OOS; DFRobot SEN0348 $19.90 (sale). No bare-chip route for hobbyists — module is the PCB part.
- Camera: arducam.com, robotshop, leeselectronic all 403 to WebFetch; DigiKey no Arducam SPI hits. UCTronics (Arducam's store) Arducam Mini 2MP OV2640 SPI $25.99. Adafruit OV5640 breakouts $9.95–19.95 all OOS and need DVP/parallel (unusable on nRF9160).
- E-ink: Waveshare 2.9" module $21.99; Waveshare 2.9" capacitive-touch e-Paper (Pico) $24.99.
- DigiKey bare: W25Q128JVSIQ $4.21/@90 $3.647 (47,261); MX25R6435FZNIL0 $2.89/@100 $2.50 (0 stock); W25N02KVZEIR $22.94/@126 $19.42, **0 stock, no backorders** (was $18.40 in pendant-v2, ~$10 at LCSC per v2); BMI270 $4.23/@100 $3.1715 (53,253); DRV2605LDGSR $2.28/@100 $1.38; VLV101040A LRA $7.18/@100 $5.64 (v2 guessed ~$2); MAX98357AETE+T $4.08/@100 $2.56 (40,043); MAX17048G+T10 $4.61/@100 $2.92; BQ25180YBGR $3.01/@100 $1.854.
- DigiKey bare: USB4105-GF-A $0.80/@100 $0.5745 (120,440); BQ51050BRHLR $4.97/@100 $3.16 (0 stock, due 2026-11-30); Würth 760308103205 Qi RX coil $8.27/@100 $6.61; AT42QT1070-SSUR $1.25/@25 $1.21; SPH0641LU4H-1 $3.22; AS01308MR-2-R speaker $4.46 (@400 $2.29, 3,459); NPM1304-QEAA-R $2.95/@100 $1.81 (3,421); NPM1304-EK $46.38 (50); CMT-8540S-SMT-TR magnetic buzzer $4.13/@100 $2.44; ATECC608B-SSHDA-T $0.90/@100 $0.887 (236 stock).
- Owner correction #2: DROP NDP120 + VM3011 (no always-listening; button/gesture trigger). ADD solar harvesting (optional, pendant): cells AM-1454/AM-5412, KXOB, Powerfilm; MPPT PMICs BQ25570, AEM10941/AEM00941, LTC3105 — each breakout + bare with 500 lux / full-sun output.
- Solar: BQ25570RGRR $8.87/@100 ~$5.85 (8,458); BQ25570EVM-206 $140 (85); MIKROE-2814 Solar Energy Click (BQ25570) $32 at DigiKey (25) — cheaper breakout; LTC3105EDD#PBF $9.68/@100 $6.04 (223); LTC3105 demo board not found at DigiKey; e-peas AEM10941/AEM00941 not at DigiKey, Mouser times out; EVK10941 AU$129.89 at Glyn (≈US$85, not USD-verified). KXOB25-05X3F-TB 23x8x1.8 mm, 30.7 mW (1 sun), $3.23/@100 $2.16 (2,981). Panasonic AM-1454CA discontinued at DigiKey (46.5 µW @200 lux per listing, 41.6x26.3 mm); AM-5412CAR-DGK-T 50x33 mm, 87.6 mW outdoor, $13.13, OBSOLETE (81 left) — too big for 34 mm face; AM-1417CA (35x13.9 mm, 18.75 µW @200 lux) RFQ-only at distributors (Arrow timed out). PowerFilm LL200-3-37 114x37 mm $5.89/@100 $3.95 — too big for pendant, fine for study-tool. Adafruit bq25185 solar charger #6091 $6.95 OOS (near-MPPT only).
- Indoor-power estimates: amorphous a-Si ~ scale linearly with lux from the 200 lux datasheet point (x2.5 for 500 lux). Crystalline KXOB only rated at 1 sun; indoor figure is an estimate (~0.2–0.4% of 1-sun output at 500 lux fluorescent/LED).
- Extras/sensors: VCNL4040M3OE $1.90; APDS-9960 $1.27; Adafruit APDS9960 #3595 $7.50; JS202011SCQN DPDT slide $0.87/@100 $0.616 (100,248); NT3H2111 NXP $1.45; MIKROE-2462 NFC Tag 2 Click $14; TPS22916CNYFPR $0.55/@100 $0.30; TPS22916EVM $70.60; IS31FL3194-CLS2-TR DigiKey $0.82/@100 $0.46, LCSC $1.05/@100 $0.65; no IS31FL3194 breakout at DigiKey (Tindie only, unverified); APS6404L-3SQR-SN LCSC out of stock (search snippet "from $2.94"); Adafruit #4677 64 Mbit PSRAM (ESP-PSRAM64, APS6404-class) $1.75.
- UWB: DWM3000TR13 $23.62/@100 $19.84 (10,231); DWM3000EVB $29.50 (1,086); Murata Type2BP EVK LBUA0VG2BP-EVK-P $179.99 (39-wk lead); bare Type2BP module not listed at DigiKey.
- VPU: Syntiant (ex-Knowles) V2S200D $4.09/@500 $2.82 (8,726). No eval board at DigiKey.
- Force: Interlink FSR400 34-00004 $8.30/@100 $6.36; Adafruit round FSR #166 $3.95. Gore GAW acoustic vents: no distributor price found (DigiKey none, Mouser times out) — sample/quote via Gore.
- LEDs: Kingbright APHHS1005CGCK 0402 green $0.26/@100 $0.126; APTF1616SEEZGQBDC 1.6 mm RGB $1.11/@100 $0.58. (No addressable LEDs — pendant-v2 rejects SK6812-class quiescent current.)
- Tools: NRF-PPK2 $107.30 (1,318); Tag-Connect TC2030-CTX-NL $42.95 (tag-connect.com); NanoVNA-H4 $109.95 R&L (search snippet; clones ~$60).
- Antennas/SIM: Adafruit passive GPS uFL #2461 $3.95 (100+ $3.16); Adafruit active GPS #960 $21.50; Adafruit sticker cellular #1991 $2.95; Ignion NN02-224 $1.64; Johanson 1575AT43A0040001E GNSS chip $0.94/@100 $0.699. Hologram: SIM $3, $1/mo, $0.03/MB. 1NCE: $14 for 10 yr/500 MB; SIM chip (MFF2) $2.50 — 500 MB is ~70 h of 16 kbps Opus, too small for a voice product.
- Breakouts: SparkFun BMI270 SEN-22397 $18.50; Seeed XIAO nRF52840 $9.99 ($8.99 10+); Adafruit QSPI W25Q128 DIP #5634 $2.95.
- Batteries: Adafruit 350 mAh #2750 $6.95 (100+ $5.56), 400 mAh #3898 $6.95; Jauch LP402535 370 mAh w/ PCM $9.51/@100 $6.58 (DigiKey). BQ29700DSER protection IC $0.61/@100 $0.333.
- E-ink/stylus: Adafruit 2.9" grayscale FeatherWing #4777 $22.50 OOS; Waveshare 7.5" HAT $56.99; GDEY029T94 raw panel $6.46 at buy-lcd (0 stock); GDEY029T94-T01 touch panel price not listed. No hobbyist EMR digitizer module found at any distributor; Amazon blocked (500/503).
- Misc: Adafruit PN532 #364 $39.95 OOS; Waveshare fingerprint (D) $16.99 in stock; Adafruit pogo pins P75-B1 10-pk #2430 $4.95; NanoVNA-H4 $109.95 at R&L (verified) — NOTE only reaches 1.5 GHz, so it cannot tune the 2.4 GHz BLE/Wi-Fi antenna or LTE bands above 1.5 GHz. MagSafe magnet ring: Etsy 403 / Amazon 503 → no verified price.

## Output
`components.json` has 100 rows. Each row gives breakout vs bare, core/test-only/optional, estimate vs actual, qty100, units for testing and per-device qty. The generator script is in the session scratchpad (not in the repo).

### Totals (computed from components.json; actual price if verified, else estimate)
- **Pendant core bare-chip BOM: ~$91/device** at the @100 tier (qty-1 price where no 100 tier was shown). At qty 1 it is ~$116. Lines: nRF9160 22.59, nRF5340 7.40, nRF7002 3.50, W25N02KV 19.42, BMI270 3.17, nPM1304 1.81, 370 mAh cell 6.58, DRV2605L 1.38, LRA 5.64, 2x SPH0641 6.44, MAX98357A 2.56, speaker 4.46, AT42QT1070 1.21, LTE antenna 1.64, GNSS antenna 0.70, SIM chip 2.50. **Excludes** PCB, passives, crystals, BLE chip antenna, pogo contacts, button/encoder, enclosure, and the semi-custom round cell premium.
- **Breakout testing (units_for_testing x price):** core $1,586, test-only $639, optional $593, so **$2,818 for all breakouts** (includes $430 of tools). Plus $105 of bare parts bought for bench tests (LRAs, speakers, LEDs, switches, cells). Everything together: **$2,923**. Excludes the 1 nRF9160 DK + 7 breakouts already owned, and shipping/tax (~15% on the July orders).

### Flags
1. NRF9160-SICA-R7 is obsolete; use NRF9160-SICA-B1A-R7 (or nRF9151).
2. W25N02KV: 0 stock and no backorders at DigiKey. NRF5340-QKAA-R: 0 stock, 2,994 due 2026-10-30. BQ51050B: 0 stock until 2026-11-30. Thingy:91 X: 0 stock.
3. VLV101040A LRA is $5.64 @100, not the ~$2 in pendant-v2.
4. NanoVNA-H4 stops at 1.5 GHz and can't tune the BLE/Wi-Fi or upper LTE antennas.
5. 1NCE's 500 MB / 10 yr is ~70 h of voice. Budget per-MB data instead (Hologram $0.03/MB ≈ $0.21/h of voice).
6. Unverified prices (actual=null): magnet ring, EMR digitizer, VPU eval, Gore vents, APS6404L (LCSC OOS), IS31FL3194 breakout, e-peas EVK/IC, AM-1454CA (discontinued), AM-1417CA (RFQ).

## Sources
DigiKey product/search pages as linked per row; adafruit.com/product/{3006,3492,3421,2305,1201,1578,3923,4438,5580,4410,1901,4750,1982,1362,160,4314,4161,3595,4677,5634,5673,5840,4777,2750,3898,364,960,1991,2461,166,2430,6091}; sparkfun.com SEN-22397; seeedstudio XIAO nRF52840; waveshare.com (2.9in module, Pico-CapTouch 2.9, 7.5in HAT, fingerprint C/D); dfrobot.com product-2051; uctronics.com Arducam Mini 2MP; buy-lcd.com GDEY029T94; good-display.com/product/465; hologram.io/pricing; 1nce.com/en-us/1nce-connect; tag-connect.com TC2030-CTX-NL; randl.com NanoVNA-H4; glynstore.com/evk10941; lcsc.com C2678591, C5333729.

## Follow-up: "why not ~16 GB instead of 256 MB?" (Storage rows, 12 appended, required=optional; W25N02KV row kept)
### Checked today
- **SD NAND (LGA-8, SPI mode):**
  - CSNP1GCR01-BOW 128 MB: $7.84 / @100 $5.81 (3,647 stock).
  - CSNP32GCR01-BOW 4 GB: $40.65 / @30 $32.16 (696 stock).
  - CSNP64GCR01-AOW 8 GB: $69.21, OOS.
  - XTSD04G/08G: LCSC shows not available.
  - No 16 GB (128 Gbit) SD NAND found in stock anywhere.
  - Adafruit XTSD breakouts: 512 MB $9.50, 2 GB $10.95 (100+ $8.76), 4 GB $12.50. All OOS.
  - XTX datasheet (DC characteristics): active 30 mA max, standby 0.2 mA max with the clock stopped, VDD 2.7–3.6 V, 250 ms power-up setup time.
- **eMMC:**
  - Foresee FEMDRW008G 8 GB BGA-153: $54.50 / @30 $42.17.
  - Micron MTFC4G at DigiKey: Not Available.
  - Can't be driven: eMMC has no SPI mode and the nRF parts have no MMC host.
- **microSD:**
  - Hirose DM3AT-SF-PEJM5 socket: $3.55 (83,826 stock).
  - Adafruit breakout #254: $7.50.
  - Kingston SDCIT2/8GB industrial card: $74.79 (@100 $63.45), OOS.
  - Adafruit 8 GB card #1294: $23.50, OOS.
  - Owned DFRobot 64 GB card: now obsolete.
- **SPI NAND:**
  - GD5F1GQ5UEYIGR 1 Gb: $9.05 / @100 $7.77 (5,252 stock).
  - W25N01GVZEIG 1 Gb: $15.51.
  - GD 2 Gb/4 Gb: OOS, reel-only pricing.
### Interfaces
- The nRF9151 and nRF5340 have SPIM (nRF9151 8 MHz; nRF5340 SPIM4 up to 32 MHz) and QSPI (NOR command set). There is no SDIO/MMC host.
- SD NAND and microSD work in SD-SPI mode (Zephyr sdhc-spi + FATFS). The SD spec caps SPI at 25 MHz, which realistically gives 0.5–2 MB/s.
- SPI NAND runs on SPIM/QSPI but needs our own FTL (no upstream Zephyr driver — verify).
- eMMC: not drivable.
### Capacity sanity (16 kbps Opus = 7.2 MB/h)
| Size | Hours of audio |
| ---: | ---: |
| 128 MB | 17.8 h |
| 256 MB | 35.6 h |
| 512 MB | 71 h |
| 4 GB | 569 h |
| 16 GB | 2,276 h |

pendant-v2's offline-capture state draws ~3.6 mA. A 330 mAh cell therefore records at most ~92 h (~660 MB) per charge. Anything beyond ~1 GB only helps if the device goes weeks without syncing.
