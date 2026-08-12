# Pendant hardware research handoff — exterior and exploded-component images

**Prepared:** 2026-08-11  
**Scope:** a truthful, dimension-aware reference for the two requested image-generation deliverables. This is a visual/mechanical concept handoff, **not** a released manufacturing drawing or an order confirmation.

## Bottom line for the image brief

Render a compact, round **BLE pendant**, not an ESP32/cellular-dev-board gadget:

- **Exterior:** a 34 mm diameter by 12.5 mm thick round pendant, with a small top bail. Use a matte warm-white or charcoal PA12/PC body and a thin decorative metal ring only away from the antenna; do not depict a sealed all-metal radio enclosure.
- **Exploded view:** 34 mm outer diameter / approximately 31 mm inner usable diameter. Stack front cap → speaker/acoustic cup and PCB components → 0.8 mm four-layer circular PCB → round 30 mm × 4.7 mm LiPo → rear cap / magnetic pogo contacts. Keep antenna corner visibly clear of battery, speaker magnet, and LRA.
- **Radio/compute:** **Nordic nRF5340**, with Bluetooth Low Energy, is the specified v2 SoC. **Do not show or label an ESP32.** The historic ESP32 was an AirPods bridge in the nRF9160 desk prototype; v2 explicitly removes it in favor of phone-relayed BLE. The nRF9151 cellular footprint is DNP (laid out, not populated) and should either be omitted from the beauty/exploded image or shown as a light-grey optional/dormant footprint only.

## Evidence status — do not turn a design spec into claimed purchases

The two active hardware documents explicitly say the v2 hardware is a “specification for build,” and the audio/mute/secure-element respin is “not yet ordered, not yet fabricated, nothing here has been built.” Therefore no part below is confirmed as personally purchased merely because it has an MPN.

| Status | What the repository actually supports | Treatment in the image |
|---|---|---|
| **Specified / exact MPN** | nRF5340, nPM1304, BMI270, W25N02KVZEIR-TR, MAX98357AETE+T, DRV2605LDGSR, VLV101040A, 2450AT18A100, and some respin parts have named MPNs. | Label exact MPN where noted below; call them “specified” or “selected,” never “purchased.” |
| **Exact historical/legacy hardware** | Icarus SoM / nRF9160, ESP32 bridge, 500 mAh rectangular LiPo, SK6812, and the 18 mm PUI speaker belong to v1 or are expressly superseded/non-fitting. | Exclude from v2 component image. |
| **Requirement only / unresolved** | 30 mm round LiPo, 4-pin magnetic pogo, acoustic membranes, cap/squeeze input, RGB LED, and production enclosure have no confirmed orderable part in v2. | Show functional geometry only and label **assumption** / “TBD”; never attach a made-up MPN. |
| **Respin alternative** | Local speaker/mute/secure element document refines some v2 items but says it is not ordered. | Use its component dimensions only where noted; label as a **representative specified respin part**, not a bought component. |

## Component inventory for the exploded breakdown

The “visual allocation” dimensions include only enough breathing room for a legible exploded rendering; they are not a CAD placement authorization.

| Exploded label | Status / role | Exact part / documented body size | Visual placement and clearance notes |
|---|---|---|---|
| BLE SoC | **Specified v2 exact MPN** | Nordic `NRF5340-QKAA-R`, aQFN94, **7 × 7 mm**. Production alternate `NRF5340-CLAA-R`, WLCSP95 **4.4 × 4.0 mm**. Nordic confirms dual-core BLE-capable nRF5340 and both packages in its [product specification](https://docs-be.nordicsemi.com/bundle/nRF5340_PS_v1.1/raw/resource/enus/nRF5340_PS_v1.1.pdf). | Render the 7 × 7 mm QFN on the top side of the Ø32 mm PCB for EVT readability. Its dimensions are silicon-body dimensions; show surrounding decoupling and keep copper/antenna routing implied, not a bare chip floating on battery. |
| BLE antenna | **Specified v2 exact MPN** | Johanson `2450AT18A100`, **3.20 × 1.60 × 1.30 mm**. | Put at an outside PCB corner with a **6.5 × 6.5 mm no-ground keep-out** and an exterior nonconductive RF window. Do not place it under a metal ring, battery, LRA, or speaker magnet. |
| PMIC / charger / fuel gauge | **Specified v2 exact MPN** | Nordic `NPM1304-QEAA-R`, QFN32 **5 × 5 mm**; smaller CSP **3.1 × 2.4 mm** exists. Nordic’s [current datasheet](https://docs.nordicsemi.com/r/bundle/ps_npm1304/page/keyfeatures_html5.html?contentId=3fBx6Gr2QfQJzJWoOh1Mfw) confirms charger, dynamic power path, two 200 mA bucks, and package sizes. | Place central/top-side adjacent to battery power entry. Render several 0402 passives and a compact charge/contact interface, but not a separate large charger board. |
| Motion IMU | **Specified v2 exact MPN** | Bosch `BMI270`, 14-pin LGA **2.5 × 3.0 × 0.83 mm**. Bosch lists the **2.5 × 3.0 × 0.8 mm** package on its [BMI270 product page](https://www.bosch-sensortec.com/en/products/motion-sensors/imus/bmi270/). | Top-side, near geometric center and away from speaker/LRA; do not render as a large breakout board. |
| Offline NAND flash | **Specified v2 exact MPN** | Winbond `W25N02KVZEIR-TR`, **8 × 6 mm** WSON, 2 Gbit / 256 MB. Winbond’s [2025 selection guide](https://www.winbond.com/export/sites/winbond/product-selection-guide/file/2025-Product-Selection-Guide-Winbond-Code-Storage-Flash-Memory.pdf?__locale=en) lists W25N02KVTBIR at 8 × 6 mm; validate the exact suffix/package drawing before PCB release. | A visibly rectangular IC on top PCB face. The current source has no live availability claim for this exact v2 BOM line, so label it as “specified storage,” not installed hardware. |
| PDM microphones ×2 | **Specified v2 exact MPN** | TDK InvenSense `MMICT5838-00-012`, each **3.50 × 2.65 × 0.98 mm**, bottom port. | One near front acoustic opening; one rear/body-facing opening, roughly opposite sides. Render acoustic mesh/membrane above each. Do not draw generic large “mic modules.” |
| Local audio amp | **Specified exact MPN; refined by respin** | ADI `MAX98357AETE+T`, TQFN-16 **3.0 × 3.0 × 0.75 mm**. ADI confirms this exact package and MPN family on its [MAX98357A product page](https://www.analog.com/en/products/max98357a.html). | Top PCB face near speaker pads but physically separated from radio corner. It is a low-profile IC; the speaker, not the amp, sets the audio stack height. |
| Micro speaker | **Respin representative exact MPN, not confirmed bought** | PUI `AS01308MR-2-R`, **Ø13.0 ± 0.1 × 2.8 ± 0.2 mm**, 8 Ω. The repo selects it as a respin candidate because the legacy 18 mm `AS01808MR-R` cannot fit; PUI’s product family page confirms the 13 mm class [here](https://puiaudio.com/product/speakers-and-receivers/as01308mr-r). | Face/side port into a sealed ~0.5–1 cm³ back-volume cup; show a 13 mm round driver centered above PCB/battery footprint. Port it to side/bottom, not chest-facing front. This consumes one battery-layer footprint but should not be stacked directly over the cell. |
| Haptic driver | **Specified v2 exact MPN** | TI `DRV2605LDGSR`, VSSOP-10 **3.0 × 3.0 mm**. TI’s [datasheet](https://www.ti.com/lit/ds/symlink/drv2605l.pdf) confirms the VSSOP body size and LRA/ERM support. | Tiny top-side IC near LRA pads. |
| LRA haptic actuator | **Specified v2 exact MPN but supply/live status explicitly unverified** | Vybronics `VLV101040A`, **10 × 10 × 4.0 mm**. | Put on rear-facing/battery-layer region, not the antenna corner. It is one of the elements that makes the nominal 12.5 mm stack tight; show it side-by-side with (not on top of) the speaker/battery wherever possible. The project says to evaluate an 8 × 3.2 mm coin LRA if this 4 mm height breaks stack-up — do not silently replace it in labels. |
| Battery | **v2 requirement, not an exact purchasable MPN** | Round protected single-cell LiPo, **Ø30 × 4.7 mm, ≈330 mAh, ≈6.6 g**, “Grepow / equivalent,” semi-custom. | Depict a flat gold/black round cell with insulated tabs, largest layer beneath PCB. This is the critical geometry. A 34 mm OD body with 1.2 mm wall leaves ≈31 mm inner diameter; commodity rectangular cells in the legacy BOM do not fit. Label **“round LiPo — semi-custom / TBD supplier”**. |
| RGB status light | **Requirement only, no MPN** | Discrete RGB LED, **1.6 × 0.8 mm target**, driven by nPM1304 LED drivers. | Show a tiny aperture/light pipe on the rim or front. Do **not** depict SK6812/NeoPixel: v2 explicitly rejects it for quiescent current. |
| User input | **Requirement only, no selected mechanism** | “Squeeze/cap-touch” is open; a snap dome is a possible non-electronic alternative. | Exterior can show an unmarked gentle squeeze zone or a single flush tactile region; exploded view labels **“squeeze sensor / snap dome — TBD.”** Do not show legacy Omron button unless deliberately presenting v1. |
| Charging interface | **Requirement only, no selected MPN** | 4-pin magnetic pogo, gold contacts, rear face; v2 resolves the architecture to magnetic charging rather than USB-C. | Four small rear contact discs/arc; show a shallow contact carrier, label **“magnetic pogo charging — MPN TBD.”** |
| Optional cellular | **Specified DNP footprint only** | Nordic `NRF9151-LACA-R`, **12.1 × 11.1 × 1.2 mm**. | Omit from default exploded visual. If callout is needed, render a translucent grey unpopulated PCB footprint outside the installed parts stack: “Optional Tier 2 cellular, DNP; not a conversation radio.” |

## Enclosure and stacked-layout synthesis

### Proposed portrayal dimensions

| Envelope / feature | Dimension | Basis |
|---|---:|---|
| Outer body | **Ø34 mm × 12.5 mm** nominal | Active v2 target. 36 mm / 14 mm are hard limits. |
| PCB | **Ø32 mm × 0.8 mm**, 4 layers | v2 BOM target. |
| Usable internal diameter | **≈31 mm** | 34 mm outside diameter minus two 1.2 mm walls. |
| Battery | **Ø30 × 4.7 mm** | v2 semi-custom round-cell specification; leaves only ~0.5 mm radial clearance before wiring/adhesive, so this needs mechanical validation. |
| Speaker | **Ø13 × 2.8 mm** | Representative respin selection, shares lateral layer with battery rather than stacking full area. |
| LRA | **10 × 10 × 4.0 mm** | Exact v2 candidate; its 4 mm depth is the riskiest stack-height component. |
| Shell faces | **1.0 mm front + 1.0 mm rear** nominal | Existing v2 stack-up. |
| PCB components | **≤1.5 mm allocated height** | Existing v2 stack-up; the listed QFN/IMU/amp fit within it, but connectors/acoustic structures do not disappear. |

### Visual layer order (front / wearer-facing orientation may be mirrored by ID)

1. **Front cap, 1.0 mm nominal:** one microphone acoustic port, tiny RGB light-pipe, speaker port kept off the chest-facing face where possible; decorative metal ring must stop short of BLE antenna/RF window.
2. **Audio/acoustic layer:** 13 mm speaker seated in a sealed molded/gasketed cup with a side/bottom exit. Do not make it a bare disk open to the whole enclosure.
3. **Ø32 mm four-layer PCB, 0.8 mm:** nRF5340, nPM1304, flash, BMI270, amp, DRV2605L, two PDM mics at separated ports, antenna at a protected edge corner. PCB is between user-interface/acoustic features and battery.
4. **Energy/haptic layer:** Ø30 × 4.7 mm LiPo occupies central lower plane. The 10 × 10 × 4 mm LRA and 13 mm speaker must share lateral area / recessed pockets rather than be naively stacked across the whole battery. Keep the antenna corner clear.
5. **Rear cap, 1.0 mm nominal:** rear mic port with recessed standoff and four magnetic-pogo contacts. Include a bail/chain attachment at “up,” orienting the outward antenna corner.

### Honest thickness conclusion

The source’s own 12.5 mm arithmetic is: **1.0 front cap + 0.8 PCB + 1.5 component allocation + 4.7 battery + 1.0 rear cap + 1.0 adhesive/tolerance = 10.0 mm**, with speaker/LRA intended to share the battery layer’s lateral footprint. It closes only because components are co-planar in pockets, and the document says it has “no room spare.”

For an image, retain **12.5 mm** as the intended nominal envelope but annotate the exploded visual **“tight conceptual stack; mechanical/DFM validation required.”** If speaker or LRA cannot share the battery plane, use the source’s stated **14 mm** fallback rather than faking a 10 mm thick object.

## Exterior-image art direction

- Product scale: round personal pendant, not a smartwatch or AirPods case; add a simple bail and fine chain for scale.
- Material: prototype-friendly matte PA12/PC shell, gently radiused 34 mm circular body, nonconductive RF-window sector at upper/outward antenna corner, subtle PVD-like decorative ring elsewhere. Avoid a continuous metal shell.
- Interactions: one tiny diffused status aperture, small side/bottom speaker perforation bank, one discreet front mic hole and one rear mic/charge surface. No screen is specified.
- Geometry: front face clean; back face has four flush gold magnetic charge contacts, a rear mic mesh, regulatory/serial area only if visually useful.
- Exclude: ESP32 module, large USB-C jack, external cellular antenna, nRF9160 DK, rectangular 500 mAh hobby LiPo, 18 mm legacy speaker, SK6812 ring, and a prominent clicky legacy button.

## Exploded-image prompt-ready component caption set

Use these exact labels in the image, shortening only for legibility:

1. “Front PA12/PC cap — 34 mm outer Ø — mic mesh + RGB light pipe”
2. “13 mm micro speaker — representative PUI AS01308MR-2-R — 2.8 mm H”
3. “Ø32 mm, 0.8 mm, 4-layer PCB”
4. “nRF5340 BLE dual-core SoC — 7 × 7 mm QFN (specified)”
5. “nPM1304 PMIC / charger / fuel gauge — 5 × 5 mm (specified)”
6. “BMI270 motion IMU — 2.5 × 3.0 × 0.83 mm (specified)”
7. “W25N02KV 256 MB NAND flash — 8 × 6 mm (specified)”
8. “2× PDM microphones — 3.5 × 2.65 mm (specified)”
9. “MAX98357A I²S speaker amp — 3 × 3 mm (specified)”
10. “DRV2605L haptic driver — 3 × 3 mm + VLV101040A LRA — 10 × 10 × 4 mm”
11. “2450AT18A100 BLE antenna — 3.2 × 1.6 mm — keep-out corner”
12. “Round 1S LiPo — Ø30 × 4.7 mm, ~330 mAh — semi-custom / TBD supplier”
13. “Rear cap — magnetic pogo charging contacts — MPN TBD”
14. Optional ghosted callout only: “nRF9151 cellular — DNP backup delivery path; not fitted”

## Repository evidence consulted

- `docs/hardware/pendant-v2.md` §§1–4, especially BOM rows 1–18 and mechanical target/stack-up: selected v2 architecture, dimensions, exclusions, and open items.
- `docs/hardware/respin-speaker-mute-secure-element.md` §§1 and 5: compact speaker, local-audio, secure-element/mute status, and acoustic packaging constraints.
- `docs/Component_Datasheets.html` and `hardware/design/Design_Package_v1.md`: historic v1 parts cross-checked specifically to prevent them from being presented as the new pendant.
- Primary manufacturer sources linked inline for current package/dimension verification; distributor stock/pricing intentionally not repeated as current facts.

